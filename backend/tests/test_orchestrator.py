import json

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.dependencies import CSRF_COOKIE_NAME
from backend.app.models import Workflow, WorkflowPhase, WorkspaceUsage
from backend.app.ollama import get_ollama_adapter


PASSWORD = "correct horse battery staple"


class SequentialModel:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def chat(self, prompt: str, system: str | None = None) -> dict[str, str]:
        self.prompts.append(prompt)
        return {"model": "local-test", "response": f"phase-{len(self.prompts)}"}


class FailsOnceModel:
    def __init__(self) -> None:
        self.calls = 0

    def chat(self, prompt: str, system: str | None = None) -> dict[str, str]:
        self.calls += 1
        if self.calls == 1:
            raise HTTPException(status_code=503, detail="Local AI service is unavailable")
        return {"model": "local-test", "response": f"phase-{self.calls}"}


class FailsDeveloperOnceModel:
    def __init__(self) -> None:
        self.prompts: list[str] = []
        self.failed_developer = False

    def chat(self, prompt: str, system: str | None = None) -> dict[str, str]:
        self.prompts.append(prompt)
        if "Produce a proposed implementation" in prompt and not self.failed_developer:
            self.failed_developer = True
            raise HTTPException(status_code=503, detail="Local AI service is unavailable")
        return {"model": "local-test", "response": f"phase-{len(self.prompts)}"}


def csrf(client: TestClient) -> dict[str, str]:
    return {"X-CSRF-Token": client.cookies[CSRF_COOKIE_NAME]}


def create_user_workspace_workflow(client: TestClient) -> tuple[str, dict]:
    registered = client.post(
        "/auth/register",
        json={"email": "orchestrator@example.com", "password": PASSWORD},
    )
    assert registered.status_code == 201
    headers = csrf(client)
    workspace = client.post(
        "/workspaces",
        json={"name": "Orchestrator workspace"},
        headers=headers,
    )
    assert workspace.status_code == 201
    workspace_id = workspace.json()["id"]
    workflow = client.post(
        f"/workspaces/{workspace_id}/workflows",
        json={"title": "Test task", "task": "Implement a small API"},
        headers=headers,
    )
    assert workflow.status_code == 201
    return workspace_id, workflow.json()


def test_workflow_executes_and_persists_planner_developer_qa_in_order(
    client,
    test_engine,
) -> None:
    model = SequentialModel()
    client.app.dependency_overrides[get_ollama_adapter] = lambda: model
    workspace_id, workflow = create_user_workspace_workflow(client)

    result = client.post(
        f"/workspaces/{workspace_id}/workflows/{workflow['id']}/run",
        headers=csrf(client),
    )

    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "completed"
    assert [phase["name"] for phase in body["phases"]] == ["planner", "developer", "qa"]
    assert [phase["status"] for phase in body["phases"]] == ["completed"] * 3
    assert [phase["output"] for phase in body["phases"]] == [
        "phase-1",
        "phase-2",
        "phase-3",
    ]
    assert "PLANNER OUTPUT:\nphase-1" in model.prompts[1]
    assert "DEVELOPER OUTPUT:\nphase-2" in model.prompts[2]
    assert all(phase["attempt_count"] == 1 for phase in body["phases"])
    with Session(test_engine) as db:
        rows = list(
            db.scalars(
                select(WorkflowPhase)
                .where(WorkflowPhase.workflow_id == workflow["id"])
                .order_by(WorkflowPhase.sequence)
            )
        )
        usage = db.scalar(
            select(WorkspaceUsage).where(
                WorkspaceUsage.workspace_id == workspace_id,
                WorkspaceUsage.metric == "ai_requests",
            )
        )
        assert [row.output for row in rows] == ["phase-1", "phase-2", "phase-3"]
        assert usage is not None and usage.units == 3
        persisted = db.get(Workflow, workflow["id"])
        assert persisted is not None and persisted.status == "completed"


def test_workflow_tenant_isolation_and_csrf(client) -> None:
    workspace_id, workflow = create_user_workspace_workflow(client)
    outsider = TestClient(client.app)
    with outsider:
        response = outsider.post(
            "/auth/register",
            json={"email": "other@example.com", "password": PASSWORD},
        )
        assert response.status_code == 201
        assert outsider.get(
            f"/workspaces/{workspace_id}/workflows/{workflow['id']}"
        ).status_code == 404
        assert outsider.post(
            f"/workspaces/{workspace_id}/workflows/{workflow['id']}/run",
            headers=csrf(outsider),
        ).status_code == 404

    no_csrf = client.post(f"/workspaces/{workspace_id}/workflows", json={
        "title": "Unauthorized",
        "task": "Should not be created",
    })
    assert no_csrf.status_code == 403


def test_workflow_failure_persists_and_explicit_retry_resumes_failed_phase(
    client,
    test_engine,
) -> None:
    model = FailsOnceModel()
    client.app.dependency_overrides[get_ollama_adapter] = lambda: model
    workspace_id, workflow = create_user_workspace_workflow(client)
    run_url = f"/workspaces/{workspace_id}/workflows/{workflow['id']}/run"

    failed = client.post(run_url, headers=csrf(client))
    assert failed.status_code == 503
    state = client.get(f"/workspaces/{workspace_id}/workflows/{workflow['id']}")
    assert state.json()["status"] == "failed"
    assert state.json()["phases"][0]["status"] == "failed"
    assert state.json()["phases"][0]["attempt_count"] == 1
    with Session(test_engine) as db:
        assert db.scalar(
            select(WorkspaceUsage).where(
                WorkspaceUsage.workspace_id == workspace_id,
                WorkspaceUsage.metric == "ai_requests",
            )
        ) is None

    retried = client.post(run_url, headers=csrf(client))
    assert retried.status_code == 200
    assert retried.json()["status"] == "completed"
    assert retried.json()["phases"][0]["attempt_count"] == 2
    with Session(test_engine) as db:
        usage = db.scalar(
            select(WorkspaceUsage).where(
                WorkspaceUsage.workspace_id == workspace_id,
                WorkspaceUsage.metric == "ai_requests",
            )
        )
        assert usage is not None and usage.units == 3


def test_retry_preserves_completed_phases_and_never_exceeds_attempt_bound(client) -> None:
    model = FailsDeveloperOnceModel()
    client.app.dependency_overrides[get_ollama_adapter] = lambda: model
    workspace_id, workflow = create_user_workspace_workflow(client)
    run_url = f"/workspaces/{workspace_id}/workflows/{workflow['id']}/run"

    assert client.post(run_url, headers=csrf(client)).status_code == 503
    first_state = client.get(f"/workspaces/{workspace_id}/workflows/{workflow['id']}").json()
    assert [phase["status"] for phase in first_state["phases"]] == [
        "completed",
        "failed",
        "pending",
    ]
    assert first_state["phases"][1]["attempt_count"] == 1

    resumed = client.post(run_url, headers=csrf(client))
    assert resumed.status_code == 200
    assert resumed.json()["status"] == "completed"
    assert len(model.prompts) == 4
    assert model.prompts[1] == model.prompts[2]
    assert resumed.json()["phases"][0]["attempt_count"] == 1
    assert resumed.json()["phases"][1]["attempt_count"] == 2
    assert client.post(run_url, headers=csrf(client)).status_code == 409


def test_workflow_respects_billing_quota_without_calling_model(client, monkeypatch) -> None:
    monkeypatch.setenv(
        "BILLING_PLANS_JSON",
        json.dumps(
            [
                {
                    "id": "two-phases",
                    "name": "Two phases",
                    "price_minor": 100,
                    "currency": "USD",
                    "limits": {"ai_requests": 2},
                }
            ]
        ),
    )
    model = SequentialModel()
    client.app.dependency_overrides[get_ollama_adapter] = lambda: model
    workspace_id, workflow = create_user_workspace_workflow(client)
    checkout = client.post(
        f"/workspaces/{workspace_id}/billing/checkout",
        json={"plan_id": "two-phases"},
        headers=csrf(client),
    )
    assert checkout.status_code == 200

    response = client.post(
        f"/workspaces/{workspace_id}/workflows/{workflow['id']}/run",
        headers=csrf(client),
    )

    assert response.status_code == 429
    assert len(model.prompts) == 2
    state = client.get(f"/workspaces/{workspace_id}/workflows/{workflow['id']}").json()
    assert state["status"] == "failed"
    assert [phase["status"] for phase in state["phases"]] == [
        "completed",
        "completed",
        "failed",
    ]
    assert state["phases"][2]["attempt_count"] == 0
