import json

import httpx
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.dependencies import CSRF_COOKIE_NAME
from backend.app.models import WorkspaceUsage
from backend.app.ollama import OllamaAdapter, get_ollama_adapter


PASSWORD = "correct horse battery staple"


class StubOllama:
    def __init__(self) -> None:
        self.call_count = 0

    def chat(self, prompt: str, system: str | None = None) -> dict[str, str]:
        self.call_count += 1
        return {"model": "stub-model", "response": f"reply:{prompt}"}


class BrokenOllama:
    def chat(self, prompt: str, system: str | None = None) -> dict[str, str]:
        raise HTTPException(status_code=503, detail="Local AI service is unavailable")


def csrf(client: TestClient) -> dict[str, str]:
    return {"X-CSRF-Token": client.cookies[CSRF_COOKIE_NAME]}


def register_and_create_workspace(client: TestClient) -> str:
    registration = client.post(
        "/auth/register",
        json={"email": "ai-owner@example.com", "password": PASSWORD},
    )
    assert registration.status_code == 201
    workspace = client.post(
        "/workspaces",
        json={"name": "AI workspace"},
        headers=csrf(client),
    )
    assert workspace.status_code == 201
    return workspace.json()["id"]


def test_ai_chat_calls_adapter_and_records_workspace_usage(client, test_engine) -> None:
    client.app.dependency_overrides[get_ollama_adapter] = lambda: StubOllama()
    workspace_id = register_and_create_workspace(client)

    response = client.post(
        f"/workspaces/{workspace_id}/ai/chat",
        json={"prompt": "hello", "system": "be concise"},
        headers=csrf(client),
    )

    assert response.status_code == 200
    assert response.json() == {"model": "stub-model", "response": "reply:hello"}
    with Session(test_engine) as db:
        usage = db.scalar(
            select(WorkspaceUsage).where(
                WorkspaceUsage.workspace_id == workspace_id,
                WorkspaceUsage.metric == "ai_requests",
            )
        )
        assert usage is not None
        assert usage.units == 1


def test_ai_chat_tenant_and_csrf_checks_happen_before_model_call(client) -> None:
    stub = StubOllama()
    client.app.dependency_overrides[get_ollama_adapter] = lambda: stub
    workspace_id = register_and_create_workspace(client)
    outsider = TestClient(client.app)

    with outsider:
        outsider.post(
            "/auth/register",
            json={"email": "outsider@example.com", "password": PASSWORD},
        )
        denied = outsider.post(
            f"/workspaces/{workspace_id}/ai/chat",
            json={"prompt": "hello"},
            headers=csrf(outsider),
        )

    no_csrf = client.post(f"/workspaces/{workspace_id}/ai/chat", json={"prompt": "hello"})
    assert denied.status_code == 404
    assert no_csrf.status_code == 403


def test_ai_chat_enforces_configured_plan_quota(client, monkeypatch) -> None:
    monkeypatch.setenv(
        "BILLING_PLANS_JSON",
        json.dumps(
            [
                {
                    "id": "one-call",
                    "name": "One call",
                    "price_minor": 100,
                    "currency": "USD",
                    "limits": {"ai_requests": 1},
                }
            ]
        ),
    )
    stub = StubOllama()
    client.app.dependency_overrides[get_ollama_adapter] = lambda: stub
    workspace_id = register_and_create_workspace(client)
    checkout = client.post(
        f"/workspaces/{workspace_id}/billing/checkout",
        json={"plan_id": "one-call"},
        headers=csrf(client),
    )
    assert checkout.status_code == 200

    accepted = client.post(
        f"/workspaces/{workspace_id}/ai/chat",
        json={"prompt": "first"},
        headers=csrf(client),
    )
    rejected = client.post(
        f"/workspaces/{workspace_id}/ai/chat",
        json={"prompt": "second"},
        headers=csrf(client),
    )

    assert accepted.status_code == 200
    assert rejected.status_code == 429
    assert stub.call_count == 1


def test_upstream_failure_does_not_commit_usage(client, test_engine) -> None:
    client.app.dependency_overrides[get_ollama_adapter] = lambda: BrokenOllama()
    workspace_id = register_and_create_workspace(client)

    response = client.post(
        f"/workspaces/{workspace_id}/ai/chat",
        json={"prompt": "hello"},
        headers=csrf(client),
    )

    assert response.status_code == 503
    with Session(test_engine) as db:
        usage = db.scalar(
            select(WorkspaceUsage).where(
                WorkspaceUsage.workspace_id == workspace_id,
                WorkspaceUsage.metric == "ai_requests",
            )
        )
        assert usage is None


def test_ollama_adapter_sends_server_selected_model_and_bounds_output(monkeypatch) -> None:
    calls = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict:
            return {"message": {"content": "hello"}}

    class FakeClient:
        def __init__(self, timeout: float) -> None:
            calls["timeout"] = timeout

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            pass

        def post(self, url: str, json: dict) -> FakeResponse:
            calls["url"] = url
            calls["body"] = json
            return FakeResponse()

    monkeypatch.setattr("backend.app.ollama.httpx.Client", FakeClient)
    adapter = OllamaAdapter(base_url="http://127.0.0.1:11434/", model="local-model")

    assert adapter.chat("prompt", "system") == {
        "model": "local-model",
        "response": "hello",
    }
    assert calls["url"] == "http://127.0.0.1:11434/api/chat"
    assert calls["body"]["model"] == "local-model"
    assert calls["body"]["stream"] is False
    assert calls["body"]["options"]["num_predict"] == 2048
    assert calls["body"]["messages"] == [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "prompt"},
    ]


def test_ollama_adapter_translates_connection_failure(monkeypatch) -> None:
    class FakeClient:
        def __init__(self, timeout: float) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            pass

        def post(self, url: str, json: dict):
            request = httpx.Request("POST", url)
            raise httpx.ConnectError("connection refused", request=request)

    monkeypatch.setattr("backend.app.ollama.httpx.Client", FakeClient)

    try:
        OllamaAdapter().chat("prompt")
    except HTTPException as exc:
        assert exc.status_code == 503
    else:
        raise AssertionError("Expected Ollama connection failure to produce HTTP 503")
