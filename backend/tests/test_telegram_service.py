from datetime import timedelta

import pytest
from sqlalchemy import select

from app.core.actors import HumanActor
from app.models import Approval, AuditLog, TelegramActionToken, TelegramLinkCode, User
from app.models.base import utcnow
from app.models.enums import ApprovalChannel, ContentStatus
from app.services import ContentService
from app.services.telegram import (
    CALLBACK_PREFIX,
    TelegramAccessError,
    TelegramService,
    TelegramTokenError,
)
from tests.conftest import TG_OTHER, TG_OWNER, TG_STRANGER, make_content, make_ready


def _cb(reply, label_start):
    for row in reply.buttons:
        for b in row:
            if b.text.startswith(label_start):
                return b.callback_data
    raise AssertionError(f"button {label_start!r} not found in {reply.buttons}")


def _review(db, tg, content):
    svc = TelegramService(db)
    buttons = svc.review_buttons(tg, content)
    db.commit()
    return buttons


# ------------------------------------------------------------------ linking
def test_link_code_flow(db, human, user, tg_settings):
    svc = TelegramService(db)
    code, expires = svc.create_link_code(human)
    assert len(code) == 9 and code[4] == "-"
    stored = db.scalars(select(TelegramLinkCode)).one()
    assert stored.code_hash != code and code not in stored.code_hash  # only the hash is stored
    linked = svc.link(TG_OWNER, code.lower().replace("-", ""))  # tolerant input
    assert linked.id == user.id and user.telegram_user_id == TG_OWNER
    with pytest.raises(TelegramAccessError, match="noto‘g‘ri"):
        svc.link(TG_OWNER, code)  # one-time
    actions = [a.action for a in db.scalars(select(AuditLog))]
    assert "TELEGRAM_LINK_CODE_CREATED" in actions and "TELEGRAM_ACCOUNT_LINKED" in actions


def test_link_requires_allowlist_and_valid_code(db, human, tg_settings):
    svc = TelegramService(db)
    code, _ = svc.create_link_code(human)
    with pytest.raises(TelegramAccessError) as exc:
        svc.link(TG_STRANGER, code)
    assert exc.value.code == "not_allowed"
    denied = db.scalars(select(AuditLog).where(AuditLog.action == "TELEGRAM_ACCESS_DENIED")).one()
    assert denied.details["telegram_user_id"] == TG_STRANGER
    with pytest.raises(TelegramAccessError):
        svc.link(TG_OWNER, "0000-0000")
    row = db.scalars(select(TelegramLinkCode)).one()
    row.expires_at = utcnow() - timedelta(seconds=1)
    db.commit()
    with pytest.raises(TelegramAccessError, match="muddati"):
        svc.link(TG_OWNER, code)


def test_new_code_invalidates_old(db, human, tg_settings):
    svc = TelegramService(db)
    old, _ = svc.create_link_code(human)
    new, _ = svc.create_link_code(human)
    with pytest.raises(TelegramAccessError):
        svc.link(TG_OWNER, old)
    svc.link(TG_OWNER, new)


def test_telegram_id_moves_between_users(db, human, user, tg_settings):
    other = User(email="second@example.com", password_hash="x", telegram_user_id=TG_OWNER)
    db.add(other)
    db.commit()
    svc = TelegramService(db)
    code, _ = svc.create_link_code(human)
    svc.link(TG_OWNER, code)
    db.refresh(other)
    assert other.telegram_user_id is None and user.telegram_user_id == TG_OWNER


def test_resolve_user_rules(db, user, tg_settings):
    svc = TelegramService(db)
    with pytest.raises(TelegramAccessError) as e1:
        svc.resolve_user(TG_STRANGER)
    assert e1.value.code == "not_allowed"
    with pytest.raises(TelegramAccessError) as e2:
        svc.resolve_user(TG_OWNER)
    assert e2.value.code == "not_linked"
    user.telegram_user_id = TG_OWNER
    user.is_active = False
    db.commit()
    with pytest.raises(TelegramAccessError) as e3:
        svc.resolve_user(TG_OWNER)
    assert e3.value.code == "inactive"


def test_unlink(db, human, linked_owner):
    TelegramService(db).unlink(human)
    assert linked_owner.telegram_user_id is None


# ------------------------------------------------------------------ tokens
def test_tokens_are_hashed_bound_and_one_time(db, human, linked_owner):
    content = make_ready(db, human)
    svc = TelegramService(db)
    token = svc.issue_token(TG_OWNER, "approve", content)
    db.commit()
    row = db.scalars(select(TelegramActionToken)).one()
    assert row.token_hash != token and len(token) >= 20
    with pytest.raises(TelegramTokenError):
        svc.consume_token(TG_OTHER, token, {"approve"})  # another Telegram user
    with pytest.raises(TelegramTokenError):
        svc.consume_token(TG_OWNER, token, {"reject"})  # wrong action
    svc.consume_token(TG_OWNER, token, {"approve"})
    with pytest.raises(TelegramTokenError, match="allaqachon"):
        svc.consume_token(TG_OWNER, token, {"approve"})


def test_expired_token(db, human, linked_owner):
    content = make_ready(db, human)
    svc = TelegramService(db)
    token = svc.issue_token(TG_OWNER, "approve", content, ttl=timedelta(seconds=-1))
    with pytest.raises(TelegramTokenError, match="muddati"):
        svc.consume_token(TG_OWNER, token, {"approve"})


def test_callback_data_fits_telegram_limit(db, human, linked_owner):
    content = make_ready(db, human)
    for row in _review(db, TG_OWNER, content):
        for b in row:
            if b.callback_data:
                assert len(b.callback_data.encode()) <= 64


# ------------------------------------------------------------------ decisions
def test_two_step_approve_via_telegram(db, human, user, linked_owner):
    content = make_ready(db, human)
    buttons = _review(db, TG_OWNER, content)
    first = TelegramService(db).handle_callback(TG_OWNER, buttons[0][0].callback_data)
    assert "v1" in first.text and "nashr qilmaydi" in first.text
    assert db.scalars(select(Approval)).all() == []  # first tap does not approve
    done = TelegramService(db).handle_callback(TG_OWNER, _cb(first, "Ha"))
    assert "tasdiqlandi" in done.text and "PHASE 8" in done.text
    approval = db.scalars(select(Approval)).one()
    assert approval.channel == ApprovalChannel.TELEGRAM
    assert approval.decided_by_user_id == user.id and approval.content_version == 1
    db.refresh(content)
    assert content.status == ContentStatus.APPROVED
    replay = TelegramService(db).handle_callback(TG_OWNER, _cb(first, "Ha"))
    assert "allaqachon" in replay.text


def test_reject_and_cancel(db, human, linked_owner):
    content = make_ready(db, human)
    buttons = _review(db, TG_OWNER, content)
    prompt = TelegramService(db).handle_callback(TG_OWNER, buttons[1][1].callback_data)
    cancel = TelegramService(db).handle_callback(TG_OWNER, _cb(prompt, "Bekor"))
    assert cancel.text == "Bekor qilindi." and cancel.buttons  # fresh review buttons
    prompt = TelegramService(db).handle_callback(TG_OWNER, _cb(cancel, "❌"))
    done = TelegramService(db).handle_callback(TG_OWNER, _cb(prompt, "Ha"))
    assert "rad etildi" in done.text
    db.refresh(content)
    assert content.status == ContentStatus.REJECTED


def test_edit_request_with_comment(db, human, linked_owner):
    content = make_ready(db, human)
    buttons = _review(db, TG_OWNER, content)
    ask = TelegramService(db).handle_callback(TG_OWNER, buttons[1][0].callback_data)
    assert ask.await_comment_token
    done = TelegramService(db).submit_edit_comment(
        TG_OWNER, ask.await_comment_token, "CTA ni qisqartiring"
    )
    assert "tahrir so‘raldi" in done.text
    db.refresh(content)
    assert content.status == ContentStatus.EDIT_REQUESTED
    approval = db.scalars(select(Approval)).one()
    assert approval.comment == "CTA ni qisqartiring"
    assert approval.channel == ApprovalChannel.TELEGRAM


def test_button_for_old_version_cannot_act_on_new_version(db, human, linked_owner):
    content = make_ready(db, human)
    buttons = _review(db, TG_OWNER, content)
    ContentService(db).update(content.id, human, expected_version=1, changes={"caption": "v2"})
    reply = TelegramService(db).handle_callback(TG_OWNER, buttons[0][0].callback_data)
    assert "v1 uchun edi" in reply.text and "v2" in reply.text
    assert reply.buttons  # fresh buttons for v2
    assert db.scalars(select(Approval)).all() == []


def test_confirm_issued_for_v1_cannot_approve_v2(db, human, linked_owner):
    content = make_ready(db, human)
    buttons = _review(db, TG_OWNER, content)
    prompt = TelegramService(db).handle_callback(TG_OWNER, buttons[0][0].callback_data)
    ContentService(db).update(content.id, human, expected_version=1, changes={"caption": "v2"})
    reply = TelegramService(db).handle_callback(TG_OWNER, _cb(prompt, "Ha"))
    assert "v1 uchun edi" in reply.text
    assert db.scalars(select(Approval)).all() == []


def test_viewer_cannot_approve_and_denial_is_audited(db, human, viewer, tg_settings):
    viewer_user = db.get(User, viewer.user_id)
    viewer_user.telegram_user_id = TG_OTHER
    db.commit()
    content = make_ready(db, human)
    buttons = _review(db, TG_OTHER, content)
    prompt = TelegramService(db).handle_callback(TG_OTHER, buttons[0][0].callback_data)
    reply = TelegramService(db).handle_callback(TG_OTHER, _cb(prompt, "Ha"))
    assert "OWNER yoki ADMIN" in reply.text
    assert db.scalars(select(Approval)).all() == []
    denied = db.scalars(select(AuditLog).where(AuditLog.action == "APPROVAL_DENIED")).one()
    assert denied.actor_user_id == viewer_user.id


def test_forged_and_foreign_callbacks(db, human, linked_owner):
    content = make_ready(db, human)
    buttons = _review(db, TG_OWNER, content)
    svc = TelegramService(db)
    assert "yaroqsiz" in svc.handle_callback(TG_OWNER, CALLBACK_PREFIX + "forged-token").text
    assert "Noma’lum" in svc.handle_callback(TG_OWNER, "approve:1").text
    # A button issued to TG_OWNER pressed by another (unlinked) account:
    with pytest.raises(TelegramAccessError):
        svc.handle_callback(TG_OTHER, buttons[0][0].callback_data)
    with pytest.raises(TelegramAccessError):
        svc.handle_callback(TG_STRANGER, buttons[0][0].callback_data)


def test_deleted_content(db, human, linked_owner):
    content = make_ready(db, human)
    buttons = _review(db, TG_OWNER, content)
    ContentService(db).soft_delete(content.id, human)
    assert (
        "topilmadi"
        in TelegramService(db).handle_callback(TG_OWNER, buttons[0][0].callback_data).text
    )


# ------------------------------------------------------------------ views
def test_preview_escapes_html_and_is_bounded(db, human):
    content = make_content(
        db,
        human,
        caption="<script>alert(1)</script> " + "x" * 5000,
        topic="<b>bold</b>",
        hashtags=["#a"],
    )
    text = TelegramService(db).preview(content)
    assert "<script>" not in text and "&lt;script&gt;" in text
    assert "&lt;b&gt;bold&lt;/b&gt;" in text
    assert len(text) <= 4096


def test_status_and_analytics_text(db, human, linked_owner):
    make_ready(db, human)
    svc = TelegramService(db)
    assert "Tasdiq kutmoqda: 1" in svc.status_text()
    assert "Ma’lumot yo‘q" in svc.analytics_text()
    assert "owner@example.com" in svc.settings_text(TG_OWNER)


# ------------------------------------------------------------------ notifications
def test_notifications_start_from_now_and_target_approvers(db, human, user, viewer, linked_owner):
    make_ready(db, human)  # history before the bot started: must not be sent
    viewer_user = db.get(User, viewer.user_id)
    viewer_user.telegram_user_id = TG_OTHER  # viewer: linked but cannot approve
    db.commit()
    svc = TelegramService(db)
    messages, last = svc.collect_review_notifications()
    assert messages == []
    svc.advance_cursor(last)

    content = make_ready(db, human)
    messages, last = TelegramService(db).collect_review_notifications()
    assert [tg for tg, _ in messages] == [TG_OWNER]
    reply = messages[0][1]
    assert f"#{content.id}" in reply.text and "TASDIQ KUTMOQDA" in reply.text
    TelegramService(db).advance_cursor(last)
    # The notification's buttons work for its recipient:
    prompt = TelegramService(db).handle_callback(TG_OWNER, reply.buttons[0][0].callback_data)
    assert "tasdiqlaysizmi" in prompt.text
    again, _ = TelegramService(db).collect_review_notifications()
    assert again == []


def test_notifications_skip_non_allowlisted_and_stale(
    db, human, user, linked_owner, tg_settings, monkeypatch
):
    svc = TelegramService(db)
    svc.advance_cursor(svc.init_notify_cursor())
    content = make_ready(db, human)
    ContentService(db).update(content.id, human, expected_version=1, changes={"caption": "x"})
    ApprovalService = __import__("app.services", fromlist=["ApprovalService"]).ApprovalService
    ApprovalService(db).approve(content.id, human, expected_version=2)
    messages, _ = TelegramService(db).collect_review_notifications()
    assert messages == []  # no longer waiting for review
    monkeypatch.setattr(tg_settings, "telegram_allowed_user_ids", [TG_OTHER])
    make_ready(db, human)
    messages, _ = TelegramService(db).collect_review_notifications()
    assert messages == []  # owner removed from the allowlist


def test_link_code_requires_human(db, tg_settings):
    from app.core.actors import AgentActor
    from app.core.errors import PermissionDeniedError

    with pytest.raises(PermissionDeniedError):
        TelegramService(db).create_link_code(AgentActor(name="x"))
    with pytest.raises(PermissionDeniedError):
        TelegramService(db).create_link_code(HumanActor(user_id=4242))
