"""Access control applied to every update before any handler runs."""

import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.core.config import get_settings
from app.integrations.telegram.runtime import with_service

logger = logging.getLogger(__name__)
_DENY_AUDIT_EVERY = 600.0  # seconds; avoid DB spam from unknown users
_last_denied: dict[int, float] = {}
DENIED_TEXT = "Sizga bu botdan foydalanishga ruxsat berilmagan."


class AccessMiddleware(BaseMiddleware):
    """Private chats only, and only Telegram IDs in TELEGRAM_ALLOWED_USER_IDS.

    Account linking (/start CODE) is checked later by the service; everything
    else additionally requires a linked, active panel user.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        chat = (
            event.chat
            if isinstance(event, Message)
            else (
                event.message.chat if isinstance(event, CallbackQuery) and event.message else None
            )
        )
        if user is None or (chat is not None and chat.type != "private"):
            return None  # ignore groups/channels silently
        if user.id not in get_settings().telegram_allowed_user_ids:
            now = time.monotonic()
            last = _last_denied.get(user.id)
            # Note: compare against None, not 0 — monotonic() can be small after boot.
            if last is None or now - last > _DENY_AUDIT_EVERY:
                _last_denied[user.id] = now
                logger.warning("telegram_access_denied", extra={"telegram_user_id": user.id})
                await with_service(lambda s: s.record_denied(user.id, "not in allowlist"))
            if isinstance(event, Message):
                await event.answer(DENIED_TEXT)
            elif isinstance(event, CallbackQuery):
                await event.answer(DENIED_TEXT, show_alert=True)
            return None
        return await handler(event, data)
