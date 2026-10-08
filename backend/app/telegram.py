import hashlib
import logging
import os
import secrets
import time
import uuid
from collections.abc import Callable
from difflib import SequenceMatcher
from typing import Any, Protocol

import httpx
from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.billing import ensure_billing_account, enforce_and_record_usage
from backend.app.models import Membership, TelegramAccount, TelegramLinkChallenge, Workspace
from backend.app.ollama import OllamaAdapter


LINK_CODE_LIFETIME_SECONDS = 10 * 60
MAX_TELEGRAM_MESSAGE_CHARS = 4_000
TELEGRAM_API_TIMEOUT_SECONDS = 35
PROMPT_ECHO_MIN_CHARS = 160
PROMPT_ECHO_RESPONSE_MIN_CHARS = 96
PROMPT_ECHO_SIMILARITY_THRESHOLD = 0.72
TELEGRAM_SYSTEM_PROMPT = (
    "You are a helpful assistant. ALWAYS write the final answer in natural, "
    "grammatically correct Uzbek using Latin script. Keep it simple, clear, "
    "and concise (no more than three short sentences). Answer the actual question "
    "directly. Do not introduce yourself, mix languages, or repeat the user's "
    "text. If the message is unclear, ask one short clarifying question instead "
    "of guessing. Correct clear factual errors politely; never invent facts.\n\n"
    "Follow these examples:\n"
    "User: O‘zbekiston qachon mustaqil bo‘lgan?\n"
    "Assistant: O‘zbekiston mustaqilligi 1991-yil 31-avgustda e’lon qilingan. "
    "1-sentabr — Mustaqillik kuni.\n"
    "User: O‘zbekiston 20-iyun 1991-yilda mustaqil bo‘lgan.\n"
    "Assistant: Kichik tuzatish: O‘zbekiston mustaqilligi 1991-yil 31-avgustda "
    "e’lon qilingan. 20-iyun 1990-yilda esa davlat suvereniteti to‘g‘risidagi "
    "deklaratsiya qabul qilingan.\n"
    "User: [tushunarsiz, buzilgan jumla]\n"
    "Assistant: Xabaringizni to‘liq tushunmadim. Iltimos, savolingizni "
    "boshqacha qilib yozing."
)
logger = logging.getLogger(__name__)


def hash_link_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def create_link_code(db: Session, user_id: str, bot_username: str | None) -> dict[str, Any]:
    now = int(time.time())
    db.execute(
        delete(TelegramLinkChallenge).where(
            TelegramLinkChallenge.user_id == user_id,
        )
    )
    db.execute(
        delete(TelegramLinkChallenge).where(
            TelegramLinkChallenge.expires_at <= now,
        )
    )
    code = secrets.token_urlsafe(24)
    challenge = TelegramLinkChallenge(
        id=str(uuid.uuid4()),
        code_hash=hash_link_code(code),
        user_id=user_id,
        expires_at=now + LINK_CODE_LIFETIME_SECONDS,
    )
    db.add(challenge)
    db.commit()
    return {"code": code, "expires_at": challenge.expires_at, "bot_username": bot_username}


def consume_link_code(db: Session, code: str, telegram_user_id: str) -> bool:
    now = int(time.time())
    challenge = db.scalar(
        select(TelegramLinkChallenge)
        .where(TelegramLinkChallenge.code_hash == hash_link_code(code))
        .with_for_update()
    )
    if (
        challenge is None
        or challenge.consumed_at is not None
        or challenge.expires_at <= now
    ):
        return False

    telegram_account = db.scalar(
        select(TelegramAccount).where(
            TelegramAccount.telegram_user_id == telegram_user_id
        )
    )
    if telegram_account is not None and telegram_account.user_id != challenge.user_id:
        return False
    user_account = db.scalar(
        select(TelegramAccount).where(TelegramAccount.user_id == challenge.user_id)
    )
    if user_account is not None and user_account.telegram_user_id != telegram_user_id:
        return False

    if telegram_account is None:
        telegram_account = TelegramAccount(
            id=str(uuid.uuid4()),
            telegram_user_id=telegram_user_id,
            user_id=challenge.user_id,
        )
        db.add(telegram_account)
    challenge.consumed_at = now
    db.commit()
    return True


def revoke_telegram_link(db: Session, user_id: str) -> bool:
    result = db.execute(
        delete(TelegramAccount).where(TelegramAccount.user_id == user_id)
    )
    db.execute(
        delete(TelegramLinkChallenge).where(
            TelegramLinkChallenge.user_id == user_id,
            TelegramLinkChallenge.consumed_at.is_(None),
        )
    )
    db.commit()
    return bool(result.rowcount)


class MessageSender(Protocol):
    def send_message(self, chat_id: int | str, text: str) -> None: ...


def _send_long_message(sender: MessageSender, chat_id: int | str, text: str) -> None:
    for start in range(0, len(text), MAX_TELEGRAM_MESSAGE_CHARS):
        sender.send_message(chat_id, text[start : start + MAX_TELEGRAM_MESSAGE_CHARS])


def _is_prompt_echo(prompt: str, response: str) -> bool:
    if len(prompt) < PROMPT_ECHO_MIN_CHARS:
        return False
    normalized_prompt = "".join(char for char in prompt.casefold() if char.isalnum())
    normalized_response = "".join(char for char in response.casefold() if char.isalnum())
    return len(normalized_response) >= PROMPT_ECHO_RESPONSE_MIN_CHARS and (
        SequenceMatcher(
            None,
            normalized_prompt,
            normalized_response,
            autojunk=False,
        ).ratio()
        >= PROMPT_ECHO_SIMILARITY_THRESHOLD
    )


def process_telegram_message(
    db: Session,
    message: dict[str, Any],
    ollama: OllamaAdapter,
    sender: MessageSender,
) -> None:
    sender_id = message.get("from", {}).get("id")
    chat_id = message.get("chat", {}).get("id")
    chat_type = message.get("chat", {}).get("type")
    text = message.get("text")
    if (
        not isinstance(sender_id, int)
        or not isinstance(chat_id, int)
        or sender_id != chat_id
        or chat_type != "private"
        or not isinstance(text, str)
    ):
        return
    text = text.strip()
    if not text:
        return
    if len(text) > MAX_TELEGRAM_MESSAGE_CHARS:
        sender.send_message(chat_id, "Xabar juda uzun. 4000 belgigacha yuboring.")
        return

    command, _, argument = text.partition(" ")
    command = command.split("@", 1)[0].lower()
    telegram_user_id = str(sender_id)

    if command in {"/start", "/help"}:
        sender.send_message(
            chat_id,
            "Mahalliy AI bot. Avval veb panelda Telegram’ni bog‘lash kodi yarating, "
            "so‘ng /link KOD yuboring. Workspace tanlash: /workspaces va /use ID. "
            "Bog‘lanishni bekor qilish uchun veb paneldan unlink qiling.",
        )
        return

    if command == "/link":
        code = argument.strip()
        if not code or len(code) > 128:
            sender.send_message(chat_id, "Paneldagi bir martalik kod bilan /link KOD yuboring.")
        elif consume_link_code(db, code, telegram_user_id):
            sender.send_message(
                chat_id,
                "Hisob muvaffaqiyatli bog‘landi. Workspace’larni ko‘rish uchun /workspaces yuboring.",
            )
        else:
            sender.send_message(chat_id, "Kod yaroqsiz, muddati tugagan yoki boshqa hisobga bog‘langan.")
        return

    account = db.scalar(
        select(TelegramAccount).where(
            TelegramAccount.telegram_user_id == telegram_user_id
        )
    )
    if command == "/unlink":
        sender.send_message(chat_id, "Telegram bog‘lanishini veb paneldan bekor qiling.")
        return
    if account is None:
        sender.send_message(chat_id, "Avval veb panelda hisobni bog‘lang va /link KOD yuboring.")
        return

    if command in {"/workspaces", "/workspace"}:
        rows = db.execute(
            select(Workspace.id, Workspace.name, Membership.role)
            .join(Membership, Membership.workspace_id == Workspace.id)
            .where(Membership.user_id == account.user_id)
            .order_by(Workspace.name)
        ).all()
        if not rows:
            account.workspace_id = None
            db.commit()
            sender.send_message(chat_id, "Hisobingizda hozircha workspace mavjud emas.")
        else:
            lines = ["Workspace tanlash uchun /use ID yuboring:"]
            lines.extend(f"• {name} — {role} — {workspace_id}" for workspace_id, name, role in rows)
            _send_long_message(sender, chat_id, "\n".join(lines))
        return

    if command == "/use":
        workspace_id = argument.strip()
        membership = db.scalar(
            select(Membership).where(
                Membership.workspace_id == workspace_id,
                Membership.user_id == account.user_id,
            )
        )
        if membership is None:
            sender.send_message(chat_id, "Workspace topilmadi yoki unga a’zoligingiz yo‘q.")
            return
        account.workspace_id = workspace_id
        db.commit()
        sender.send_message(chat_id, "Workspace tanlandi. Endi xabar yuborishingiz mumkin.")
        return

    if text.startswith("/"):
        sender.send_message(chat_id, "Buyruq tushunarsiz. Yordam uchun /help yuboring.")
        return
    if not account.workspace_id:
        sender.send_message(chat_id, "Avval workspace tanlang: /workspaces")
        return

    membership = db.scalar(
        select(Membership).where(
            Membership.workspace_id == account.workspace_id,
            Membership.user_id == account.user_id,
        )
    )
    if membership is None:
        account.workspace_id = None
        db.commit()
        sender.send_message(
            chat_id,
            "Bu workspace’ga a’zoligingiz qolmagan. Yangisini tanlash uchun /workspaces yuboring.",
        )
        return

    billing = ensure_billing_account(db, account.workspace_id)
    try:
        enforce_and_record_usage(
            db,
            billing,
            account.workspace_id,
            "ai_requests",
            1,
        )
        db.flush()
        result = ollama.chat(text, system=TELEGRAM_SYSTEM_PROMPT, temperature=0.2)
        reply = result["response"]
        if _is_prompt_echo(text, reply):
            reply = (
                "Xabaringizni to‘liq tushunmadim. Iltimos, savolingizni "
                "qisqa va aniqroq qilib yozing."
            )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        logger.warning("Telegram AI request failed with HTTP status %d.", exc.status_code)
        if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            reply = "Workspace AI limiti tugadi. Tarif yoki foydalanish limitlarini panelda tekshiring."
        elif exc.status_code == 402:
            reply = "Workspace sinov muddati tugagan yoki billing faol emas."
        else:
            reply = "Mahalliy AI hozircha javob bera olmayapti. Keyinroq urinib ko‘ring."
    except Exception as exc:
        db.rollback()
        logger.error("Telegram AI request failed (%s).", type(exc).__name__)
        reply = "Mahalliy AI hozircha javob bera olmayapti. Keyinroq urinib ko‘ring."
    _send_long_message(sender, chat_id, reply)


class TelegramBotAPI:
    def __init__(
        self,
        token: str,
        timeout_seconds: float = TELEGRAM_API_TIMEOUT_SECONDS,
    ) -> None:
        self._token = token
        self.timeout_seconds = timeout_seconds

    def _request(self, method: str, payload: dict[str, Any]) -> Any:
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"https://api.telegram.org/bot{self._token}/{method}",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
            raise RuntimeError("Telegram API request failed") from exc
        if not isinstance(result, dict) or not result.get("ok"):
            raise RuntimeError("Telegram API returned an error")
        return result.get("result")

    def get_updates(self, offset: int | None) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {
            "timeout": 25,
            "allowed_updates": ["message"],
        }
        if offset is not None:
            payload["offset"] = offset
        result = self._request("getUpdates", payload)
        return result if isinstance(result, list) else []

    def send_message(self, chat_id: int | str, text: str) -> None:
        self._request("sendMessage", {"chat_id": chat_id, "text": text})

def run_polling(
    session_factory: Callable[[], Session],
    ollama: OllamaAdapter,
    bot: TelegramBotAPI,
) -> None:
    offset: int | None = None
    consecutive_poll_failures = 0
    while True:
        try:
            updates = bot.get_updates(offset)
        except RuntimeError:
            consecutive_poll_failures += 1
            if consecutive_poll_failures == 1 or consecutive_poll_failures % 10 == 0:
                logger.warning(
                    "Telegram polling request failed; retrying (failure count: %d).",
                    consecutive_poll_failures,
                )
            time.sleep(min(2 ** min(consecutive_poll_failures, 6), 60))
            continue
        consecutive_poll_failures = 0
        for update in updates:
            update_id = update.get("update_id")
            if isinstance(update_id, int):
                offset = update_id + 1
            message = update.get("message")
            if not isinstance(message, dict):
                continue
            try:
                with session_factory() as db:
                    process_telegram_message(db, message, ollama, bot)
            except Exception as exc:
                logger.error("Telegram update failed (%s).", type(exc).__name__)
                try:
                    chat_id = message.get("chat", {}).get("id")
                    if isinstance(chat_id, int):
                        bot.send_message(chat_id, "Xatolik yuz berdi. Keyinroq qayta urinib ko‘ring.")
                except RuntimeError:
                    pass
