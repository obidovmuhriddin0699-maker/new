"""Background loop: notify approvers about content waiting for review.

It reads new CONTENT_SUBMITTED_FOR_REVIEW events from the append-only audit
log (cursor stored in system_settings), so the content services never depend
on Telegram. On first start the cursor begins at "now" (no history flood).
"""

import asyncio
import logging

from aiogram import Bot

from app.core.config import get_settings
from app.integrations.telegram.runtime import keyboard, with_service
from app.models.enums import AuditAction
from app.services.audit import AuditLogService
from app.services.telegram import TelegramService

logger = logging.getLogger(__name__)


def _collect(s: TelegramService):  # type: ignore[no-untyped-def]
    return s.collect_review_notifications()


async def notify_once(bot: Bot) -> int:
    messages, last_id = await with_service(_collect)
    sent = 0
    for telegram_id, reply in messages:
        try:
            await bot.send_message(telegram_id, reply.text, reply_markup=keyboard(reply.buttons))
            sent += 1
        except Exception as exc:  # noqa: BLE001 - user blocked the bot, network, etc.
            logger.warning("telegram_notify_failed", extra={"error_type": type(exc).__name__})

    def finish(s: TelegramService) -> None:
        s.advance_cursor(last_id)
        if sent:
            from app.core.actors import SystemActor
            from app.core.transaction import atomic

            with atomic(s.session):
                AuditLogService(s.session).record(
                    AuditAction.TELEGRAM_NOTIFICATION_SENT,
                    SystemActor("telegram_bot"),
                    details={"messages": sent, "cursor": last_id},
                )

    await with_service(finish)
    return sent


async def notifier_loop(bot: Bot) -> None:
    interval = max(5, get_settings().telegram_notify_interval_seconds)
    while True:
        try:
            await notify_once(bot)
        except Exception:  # noqa: BLE001 - keep the loop alive; details in the log
            logger.exception("telegram_notifier_error")
        await asyncio.sleep(interval)
