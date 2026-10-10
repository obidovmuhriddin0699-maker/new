"""aiogram layer tests with real aiogram types; Telegram API calls are mocked."""

import pytest
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from sqlalchemy import select

import app.integrations.telegram.middleware as mw
from app.integrations.telegram import handlers
from app.integrations.telegram.bot import COMMANDS, build_dispatcher, main
from app.integrations.telegram.middleware import AccessMiddleware
from app.models import Approval, AuditLog, Content
from app.models.enums import ContentStatus
from app.services.telegram import TelegramService
from tests.conftest import TG_OWNER, TG_STRANGER, make_ready, mock_factory


class Sent:
    def __init__(self) -> None:
        self.messages: list[tuple[str, InlineKeyboardMarkup | None]] = []
        self.alerts: list[str] = []
        self.edits: list[object] = []

    @property
    def texts(self) -> list[str]:
        return [t for t, _ in self.messages]

    def last_markup(self) -> InlineKeyboardMarkup:
        markup = [m for _, m in self.messages if m is not None][-1]
        return markup


@pytest.fixture
def sent(monkeypatch) -> Sent:
    box = Sent()

    async def answer(self, text, reply_markup=None, **kw):
        box.messages.append((text, reply_markup))

    async def cb_answer(self, text=None, show_alert=None, **kw):
        if text:
            box.alerts.append(text)

    async def edit_markup(self, reply_markup=None, **kw):
        box.edits.append(reply_markup)

    monkeypatch.setattr(Message, "answer", answer)
    monkeypatch.setattr(CallbackQuery, "answer", cb_answer)
    monkeypatch.setattr(Message, "edit_reply_markup", edit_markup)
    return box


def msg(text: str, user_id: int = TG_OWNER, chat_type: str = "private") -> Message:
    return Message.model_validate(
        {
            "message_id": 1,
            "date": 0,
            "text": text,
            "chat": {"id": user_id, "type": chat_type},
            "from": {"id": user_id, "is_bot": False, "first_name": "Test"},
        }
    )


def callback(data: str, user_id: int = TG_OWNER) -> CallbackQuery:
    return CallbackQuery.model_validate(
        {
            "id": "cb1",
            "chat_instance": "ci",
            "data": data,
            "from": {"id": user_id, "is_bot": False, "first_name": "Test"},
            "message": {
                "message_id": 2,
                "date": 0,
                "text": "preview",
                "chat": {"id": user_id, "type": "private"},
            },
        }
    )


def cmd(command: str, args: str | None = None) -> CommandObject:
    return CommandObject(prefix="/", command=command, args=args)


def fsm(user_id: int = TG_OWNER) -> FSMContext:
    return FSMContext(
        storage=MemoryStorage(), key=StorageKey(bot_id=1, chat_id=user_id, user_id=user_id)
    )


def first_callback(markup: InlineKeyboardMarkup) -> str:
    return markup.inline_keyboard[0][0].callback_data  # type: ignore[return-value]


# ------------------------------------------------------------------ middleware
async def test_middleware_blocks_strangers_and_groups(sent, tg_settings, db, monkeypatch):
    monkeypatch.setattr(mw, "_last_denied", {})
    called = []

    async def handler(event, data):
        called.append(event)

    m = AccessMiddleware()
    await m(handler, msg("/status", user_id=TG_STRANGER), {})
    assert called == [] and sent.texts == [mw.DENIED_TEXT]
    assert db.scalars(select(AuditLog).where(AuditLog.action == "TELEGRAM_ACCESS_DENIED")).one()
    await m(handler, msg("/status", user_id=TG_STRANGER), {})  # throttled audit
    assert len(db.scalars(select(AuditLog)).all()) == 1
    await m(handler, msg("/status", chat_type="group"), {})
    assert called == []
    await m(handler, msg("/status"), {})
    assert len(called) == 1
    await m(handler, callback("mx:x", user_id=TG_STRANGER), {})
    assert sent.alerts == [mw.DENIED_TEXT]


# ------------------------------------------------------------------ commands
async def test_start_links_account(sent, db, human, user, tg_settings):
    code, _ = TelegramService(db).create_link_code(human)
    await handlers.cmd_start(msg(f"/start {code}"), cmd("start", code))
    assert "Hisob bog‘landi" in sent.texts[-1]
    db.refresh(user)
    assert user.telegram_user_id == TG_OWNER
    await handlers.cmd_start(msg("/start BAD"), cmd("start", "BAD-CODE"))
    assert "noto‘g‘ri" in sent.texts[-1]


async def test_start_without_link_explains(sent, tg_settings, user):
    await handlers.cmd_start(msg("/start"), cmd("start"))
    assert "bog‘lanmagan" in sent.texts[-1]


async def test_status_analytics_settings_help(sent, linked_owner, db, human):
    make_ready(db, human)
    await handlers.cmd_status(msg("/status"))
    await handlers.cmd_analytics(msg("/analytics"))
    await handlers.cmd_settings(msg("/settings"))
    await handlers.cmd_help(msg("/help"))
    assert "Tasdiq kutmoqda: 1" in sent.texts[0]
    assert "Ma’lumot yo‘q" in sent.texts[1]
    assert "owner@example.com" in sent.texts[2]
    assert "/content" in sent.texts[3]


async def test_unlinked_user_gets_explanation(sent, tg_settings, user):
    await handlers.cmd_status(msg("/status"))
    assert "bog‘lanmagan" in sent.texts[-1]


async def test_content_lists_pending_with_buttons(sent, linked_owner, db, human):
    await handlers.cmd_content(msg("/content"), cmd("content"))
    assert sent.texts[-1] == "Tasdiq kutayotgan kontent yo‘q."
    content = make_ready(db, human)
    await handlers.cmd_content(msg("/content"), cmd("content"))
    text, markup = sent.messages[-1]
    assert f"#{content.id}" in text
    labels = [b.text for row in markup.inline_keyboard for b in row]
    assert labels[:3] == ["✅ TASDIQLASH", "✏️ TAHRIR", "❌ RAD ETISH"]
    assert markup.inline_keyboard[-1][0].url == f"https://panel.example/content/{content.id}"


async def test_full_button_flow_through_handlers(sent, linked_owner, db, human):
    content = make_ready(db, human)
    await handlers.cmd_review(msg(f"/approve {content.id}"), cmd("approve", str(content.id)))
    state = fsm()
    await handlers.on_button(callback(first_callback(sent.last_markup())), state)
    assert "tasdiqlaysizmi" in sent.texts[-1]
    assert sent.edits == [None]  # tapped message loses its (spent) buttons
    await handlers.on_button(callback(first_callback(sent.last_markup())), state)
    assert "tasdiqlandi" in sent.texts[-1]
    db.expire_all()
    assert db.get(Content, content.id).status == ContentStatus.APPROVED
    assert db.scalars(select(Approval)).one().channel.value == "TELEGRAM"


async def test_review_command_requires_id_and_never_decides(sent, linked_owner, db, human):
    await handlers.cmd_review(msg("/reject"), cmd("reject"))
    assert "Foydalanish" in sent.texts[-1]
    content = make_ready(db, human)
    await handlers.cmd_review(msg(f"/reject {content.id}"), cmd("reject", str(content.id)))
    db.expire_all()
    assert db.get(Content, content.id).status == ContentStatus.READY_FOR_REVIEW
    await handlers.cmd_review(msg("/approve 999"), cmd("approve", "999"))
    assert "topilmadi" in sent.texts[-1]


async def test_edit_flow_with_fsm(sent, linked_owner, db, human):
    content = make_ready(db, human)
    await handlers.cmd_review(msg(f"/approve {content.id}"), cmd("approve", str(content.id)))
    edit_cb = sent.last_markup().inline_keyboard[1][0].callback_data
    state = fsm()
    await handlers.on_button(callback(edit_cb), state)
    assert "nimani o‘zgartirish" in sent.texts[-1]
    assert await state.get_state() == handlers.EditComment.waiting.state
    await handlers.edit_comment(msg("Rasmni yorqinroq qiling"), state)
    assert "tahrir so‘raldi" in sent.texts[-1]
    assert await state.get_state() is None
    db.expire_all()
    assert db.get(Content, content.id).status == ContentStatus.EDIT_REQUESTED


async def test_generation_commands(sent, linked_owner, db, brand, monkeypatch):
    import app.services.ai_content as module

    monkeypatch.setattr(module, "create_ai_provider", mock_factory())
    await handlers.cmd_reels(msg("/reels Kichik xona"), cmd("reels", "Kichik xona"))
    assert "ko‘rib chiqishga yuborildi" in sent.texts[-1]
    content = db.scalars(select(Content)).one()
    assert content.status == ContentStatus.READY_FOR_REVIEW
    assert content.content_type.value == "REELS"
    await handlers.cmd_reels(msg("/reels"), cmd("reels"))
    assert "Mavzuni yozing" in sent.texts[-1]
    await handlers.cmd_plan(msg("/plan"))
    assert "Haftalik reja" in sent.texts[-1] and "optimal" in sent.texts[-1]


async def test_generation_failure_is_reported(sent, linked_owner, db, brand, monkeypatch):
    import app.services.ai_content as module
    from app.providers.ai.base import AIProviderUnavailableError

    monkeypatch.setattr(
        module,
        "create_ai_provider",
        mock_factory(AIProviderUnavailableError("Ollama is not reachable.")),
    )
    await handlers.cmd_story(msg("/story Uslublar"), cmd("story", "Uslublar"))
    assert "muvaffaqiyatsiz" in sent.texts[-1] and "Hech narsa saqlanmadi" in sent.texts[-1]
    assert db.scalars(select(Content)).all() == []


async def test_viewer_cannot_generate(sent, tg_settings, db, viewer, brand):
    from app.models import User

    db.get(User, viewer.user_id).telegram_user_id = TG_OWNER
    db.commit()
    await handlers.cmd_reels(msg("/reels Kichik xona"), cmd("reels", "Kichik xona"))
    assert "ruxsatingiz yo‘q" in sent.texts[-1]


# ------------------------------------------------------------------ bot / notifier
async def test_notifier_sends_and_advances(linked_owner, db, human):
    from unittest.mock import AsyncMock

    from app.integrations.telegram.notifier import notify_once

    bot = AsyncMock()
    TelegramService(db).init_notify_cursor()
    content = make_ready(db, human)
    assert await notify_once(bot) == 1
    tg, text = bot.send_message.call_args.args[:2]
    assert tg == TG_OWNER and f"#{content.id}" in text
    assert await notify_once(bot) == 0  # cursor advanced
    assert db.scalars(select(AuditLog).where(AuditLog.action == "TELEGRAM_NOTIFICATION_SENT")).one()


async def test_notifier_survives_send_errors(linked_owner, db, human):
    from unittest.mock import AsyncMock

    from app.integrations.telegram.notifier import notify_once

    bot = AsyncMock()
    bot.send_message.side_effect = RuntimeError("blocked by user")
    TelegramService(db).init_notify_cursor()
    make_ready(db, human)
    assert await notify_once(bot) == 0
    assert await notify_once(bot) == 0  # does not resend forever


async def test_bot_refuses_unsafe_configuration(monkeypatch, tg_settings):
    from pydantic import SecretStr

    monkeypatch.setattr(tg_settings, "telegram_enabled", False)
    assert await main() == 2
    monkeypatch.setattr(tg_settings, "telegram_enabled", True)
    monkeypatch.setattr(tg_settings, "telegram_bot_token", SecretStr("123:abc"))
    monkeypatch.setattr(tg_settings, "telegram_allowed_user_ids", [])
    assert await main() == 2


def test_dispatcher_and_commands():
    dp = build_dispatcher()
    assert dp.message.outer_middleware and dp.callback_query.outer_middleware
    names = {c for c, _ in COMMANDS}
    assert {
        "content",
        "plan",
        "reels",
        "story",
        "status",
        "approve",
        "reject",
        "analytics",
        "settings",
    } <= names


async def test_bot_startup_errors_are_clean(monkeypatch, tg_settings, capsys):
    from aiogram import Bot
    from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError
    from aiogram.methods import GetMe
    from pydantic import SecretStr

    monkeypatch.setattr(tg_settings, "telegram_enabled", True)
    monkeypatch.setattr(tg_settings, "telegram_bot_token", SecretStr("123:SECRETVALUE"))
    closed = []

    async def close(self):
        closed.append(True)

    monkeypatch.setattr("aiogram.client.session.aiohttp.AiohttpSession.close", close)
    for error, code, text in [
        (TelegramUnauthorizedError(method=GetMe(), message="Unauthorized"), 2, "invalid"),
        (TelegramNetworkError(method=GetMe(), message="dns"), 1, "Cannot reach"),
    ]:

        async def get_me(self, _error=error):
            raise _error

        monkeypatch.setattr(Bot, "get_me", get_me)
        assert await main() == code
        err = capsys.readouterr().err
        assert text in err and "SECRETVALUE" not in err
    assert len(closed) == 2  # HTTP session always closed
