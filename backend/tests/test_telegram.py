import json
import time

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.dependencies import CSRF_COOKIE_NAME
from backend.app.models import TelegramAccount, TelegramLinkChallenge, WorkspaceUsage
from backend.app.telegram import (
    TELEGRAM_SYSTEM_PROMPT,
    _is_prompt_echo,
    consume_link_code,
    create_link_code,
    hash_link_code,
    process_telegram_message,
)
from fastapi import HTTPException


PASSWORD = "correct horse battery staple"


class FakeSender:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send_message(self, chat_id: int | str, text: str) -> None:
        self.messages.append(text)


class FakeOllama:
    def __init__(self, response: str | None = None) -> None:
        self.calls = 0
        self.system_prompts: list[str | None] = []
        self.temperatures: list[float | None] = []
        self.response = response

    def chat(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
    ) -> dict[str, str]:
        self.calls += 1
        self.system_prompts.append(system)
        self.temperatures.append(temperature)
        return {
            "model": "fake-local",
            "response": self.response or f"reply-{self.calls}",
        }


class FailingOllama:
    def chat(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
    ) -> dict[str, str]:
        raise HTTPException(status_code=503, detail="Private upstream error")


def csrf(client: TestClient) -> dict[str, str]:
    return {"X-CSRF-Token": client.cookies[CSRF_COOKIE_NAME]}


def register_and_workspace(client: TestClient, email: str) -> str:
    response = client.post(
        "/auth/register",
        json={"email": email, "password": PASSWORD},
    )
    assert response.status_code == 201
    workspace = client.post(
        "/workspaces",
        json={"name": "Telegram workspace"},
        headers=csrf(client),
    )
    assert workspace.status_code == 201
    return workspace.json()["id"]


def generate_code(client: TestClient) -> str:
    response = client.post("/telegram/link-code", headers=csrf(client))
    assert response.status_code == 200
    assert response.json()["expires_at"] > int(time.time())
    return response.json()["code"]


def telegram_message(telegram_user_id: int, text: str) -> dict:
    return {
        "from": {"id": telegram_user_id},
        "chat": {"id": telegram_user_id, "type": "private"},
        "text": text,
    }


def test_link_code_is_one_time_and_status_can_be_revoked(client) -> None:
    register_and_workspace(client, "link-owner@example.com")
    code = generate_code(client)
    sender = FakeSender()
    with client.app.state.session_factory() as db:
        process_telegram_message(db, telegram_message(345001, f"/link {code}"), FakeOllama(), sender)
    assert "muvaffaqiyatli" in sender.messages[-1]

    link = client.get("/telegram/link")
    assert link.status_code == 200
    assert link.json() == {"linked": True, "workspace_id": None}

    replay = client.post("/telegram/link-code", headers=csrf(client))
    assert replay.status_code == 200
    sender = FakeSender()
    with client.app.state.session_factory() as db:
        process_telegram_message(db, telegram_message(345002, f"/link {code}"), FakeOllama(), sender)
    assert "yaroqsiz" in sender.messages[-1]

    unlinked = client.delete("/telegram/link", headers=csrf(client))
    assert unlinked.status_code == 204
    assert client.get("/telegram/link").json() == {"linked": False, "workspace_id": None}


def test_link_challenge_expires_and_cannot_be_redeemed_by_another_user(
    client,
    test_engine,
    monkeypatch,
) -> None:
    register_and_workspace(client, "first@example.com")
    code = generate_code(client)
    now = int(time.time())
    monkeypatch.setattr("backend.app.telegram.time.time", lambda: now + 601)
    with Session(test_engine) as db:
        assert not consume_link_code(db, code, "345010")
        assert db.scalar(select(TelegramAccount)) is None
    monkeypatch.undo()

    second = TestClient(client.app)
    with second:
        register_and_workspace(second, "second@example.com")
        second_code = generate_code(second)
        with Session(test_engine) as db:
            challenge = db.scalar(
                select(TelegramLinkChallenge).where(
                    TelegramLinkChallenge.code_hash == hash_link_code(second_code)
                )
            )
            assert challenge is not None
            challenge.expires_at = int(time.time()) - 1
            db.commit()
            assert not consume_link_code(db, second_code, "345011")


def test_link_identity_cannot_be_reassigned_to_a_different_user(client, test_engine) -> None:
    register_and_workspace(client, "identity-owner@example.com")
    first_code = generate_code(client)
    with Session(test_engine) as db:
        assert consume_link_code(db, first_code, "345020")

    second = TestClient(client.app)
    with second:
        register_and_workspace(second, "identity-other@example.com")
        second_code = generate_code(second)
        with Session(test_engine) as db:
            assert not consume_link_code(db, second_code, "345020")
            assert db.scalar(
                select(TelegramAccount).where(
                    TelegramAccount.telegram_user_id == "345020"
                )
            ).user_id != second.get("/auth/me").json()["id"]


def test_private_message_workspace_access_and_quota_are_enforced(
    client,
    test_engine,
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "BILLING_PLANS_JSON",
        json.dumps(
            [
                {
                    "id": "telegram-one",
                    "name": "Telegram one",
                    "price_minor": 100,
                    "currency": "USD",
                    "limits": {"ai_requests": 1},
                }
            ]
        ),
    )
    workspace_id = register_and_workspace(client, "bot-user@example.com")
    code = generate_code(client)
    with Session(test_engine) as db:
        assert consume_link_code(db, code, "345030")
    checkout = client.post(
        f"/workspaces/{workspace_id}/billing/checkout",
        json={"plan_id": "telegram-one"},
        headers=csrf(client),
    )
    assert checkout.status_code == 200
    ollama = FakeOllama()
    sender = FakeSender()
    with Session(test_engine) as db:
        process_telegram_message(db, telegram_message(345030, "/use not-a-workspace"), ollama, sender)
        assert "a’zoligingiz yo‘q" in sender.messages[-1]
        process_telegram_message(db, telegram_message(345030, "/use " + workspace_id), ollama, sender)
        assert "tanlandi" in sender.messages[-1]
        process_telegram_message(db, telegram_message(345030, "first request"), ollama, sender)
        assert sender.messages[-1] == "reply-1"
        assert len(ollama.system_prompts) == 1
        assert "grammatically correct Uzbek" in ollama.system_prompts[0]
        assert "1991-yil 31-avgustda" in ollama.system_prompts[0]
        assert ollama.temperatures == [0.2]
        process_telegram_message(db, telegram_message(345030, "over quota"), ollama, sender)
        assert "limiti tugadi" in sender.messages[-1]
        assert ollama.calls == 1

    with Session(test_engine) as db:
        usage = db.scalar(
            select(WorkspaceUsage).where(
                WorkspaceUsage.workspace_id == workspace_id,
                WorkspaceUsage.metric == "ai_requests",
            )
        )
        assert usage is not None and usage.units == 1


def test_prompt_echo_is_replaced_with_a_clear_clarification() -> None:
        garbled_message = (
            "O‘zbekiston Respublikasi mustaqilligi haqida ma’lumot kerak. "
            "Bu mavzuni batafsil, lekin sodda qilib tushuntirib bering."
        ) * 2
        assert _is_prompt_echo(
            garbled_message,
            garbled_message.replace("mustaqilligi", "mustaqillik").replace("deklaratsiya", "deklaratsiyasi"),
        )
        assert not _is_prompt_echo("Salom, yordam bering", "Salom! Albatta yordam beraman.")


def test_bot_does_not_return_a_long_echo_of_unclear_user_input(client, test_engine) -> None:
        workspace_id = register_and_workspace(client, "echo-guard@example.com")
        with Session(test_engine) as db:
            code = create_link_code(db, client.get("/auth/me").json()["id"], None)["code"]
            assert consume_link_code(db, code, "345031")
            account = db.scalar(
                select(TelegramAccount).where(TelegramAccount.telegram_user_id == "345031")
            )
            assert account is not None
            account.workspace_id = workspace_id
            db.commit()

        unclear_message = (
            "O‘zbekiston Respublikasi mustaqilligi haqida tushuntiring. "
            "Bu tarixiy mavzuni sodda qilib izohlang. "
        ) * 5
        sender = FakeSender()
        ollama = FakeOllama(response=unclear_message)
        with Session(test_engine) as db:
            process_telegram_message(
                db,
                telegram_message(345031, unclear_message),
                ollama,
                sender,
            )

        assert sender.messages == [
            "Xabaringizni to‘liq tushunmadim. Iltimos, savolingizni qisqa va aniqroq qilib yozing."
        ]


def test_bot_ignores_group_messages_and_rejects_oversized_text(test_engine) -> None:
    sender = FakeSender()
    ollama = FakeOllama()
    with Session(test_engine) as db:
        process_telegram_message(
            db,
            {
                "from": {"id": 345040},
                "chat": {"id": -100345040, "type": "group"},
                "text": "ignore me",
            },
            ollama,
            sender,
        )
        process_telegram_message(
            db,
            telegram_message(345040, "x" * 4_001),
            ollama,
            sender,
        )
    assert ollama.calls == 0
    assert len(sender.messages) == 1
    assert "juda uzun" in sender.messages[0]


def test_unlinked_users_are_never_forwarded_to_model(client) -> None:
    sender = FakeSender()
    ollama = FakeOllama()
    with client.app.state.session_factory() as db:
        process_telegram_message(
            db,
            telegram_message(345050, "private prompt"),
            ollama,
            sender,
        )
    assert ollama.calls == 0
    assert "bog‘lang" in sender.messages[0]


def test_link_code_api_requires_csrf_and_stores_only_hash(client, test_engine) -> None:
    register_and_workspace(client, "challenge-owner@example.com")
    denied = client.post("/telegram/link-code")
    assert denied.status_code == 403
    code = generate_code(client)
    with Session(test_engine) as db:
        challenge = db.scalar(select(TelegramLinkChallenge))
        assert challenge is not None
        assert challenge.code_hash == hash_link_code(code)
        assert challenge.code_hash != code


def test_ai_failure_does_not_consume_telegram_workspace_quota(
    client,
    test_engine,
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "BILLING_PLANS_JSON",
        json.dumps(
            [
                {
                    "id": "telegram-one",
                    "name": "Telegram one",
                    "price_minor": 100,
                    "currency": "USD",
                    "limits": {"ai_requests": 1},
                }
            ]
        ),
    )
    workspace_id = register_and_workspace(client, "bot-failure@example.com")
    with Session(test_engine) as db:
        code = create_link_code(db, client.get("/auth/me").json()["id"], None)["code"]
        assert consume_link_code(db, code, "345060")
        account = db.scalar(
            select(TelegramAccount).where(TelegramAccount.telegram_user_id == "345060")
        )
        assert account is not None
        account.workspace_id = workspace_id
        db.commit()

    sender = FakeSender()
    with Session(test_engine) as db:
        process_telegram_message(
            db,
            telegram_message(345060, "failed prompt"),
            FailingOllama(),
            sender,
        )
    assert "javob bera" in sender.messages[-1]
    with Session(test_engine) as db:
        assert db.scalar(
            select(WorkspaceUsage).where(
                WorkspaceUsage.workspace_id == workspace_id,
                WorkspaceUsage.metric == "ai_requests",
            )
        ) is None
