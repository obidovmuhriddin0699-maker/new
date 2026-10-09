"""Bot entry point (long polling).

    python -m app.integrations.telegram

Long polling works behind NAT (a Windows laptop) without a public URL.
A webhook deployment can be added in PHASE 12.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.integrations.telegram.handlers import router
from app.integrations.telegram.middleware import AccessMiddleware
from app.integrations.telegram.notifier import notifier_loop

COMMANDS = [
    ("content", "Tasdiq kutayotgan kontent / yangi post"),
    ("plan", "Haftalik kontent reja"),
    ("reels", "Reels ssenariysi"),
    ("story", "Story konsepti"),
    ("status", "Umumiy holat"),
    ("approve", "Kontentni tasdiqlash (ID)"),
    ("reject", "Kontentni rad etish (ID)"),
    ("analytics", "Analitika"),
    ("settings", "Sozlamalar"),
    ("help", "Yordam"),
]


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.outer_middleware(AccessMiddleware())
    dp.callback_query.outer_middleware(AccessMiddleware())
    dp.include_router(router)
    return dp


async def main() -> int:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_json)
    # aiogram can include request URLs (which contain the token) in debug logs.
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    token = settings.telegram_bot_token.get_secret_value()
    if not settings.telegram_enabled or not token:
        print(
            "Telegram bot is disabled. Set TELEGRAM_ENABLED=true and TELEGRAM_BOT_TOKEN.",
            file=sys.stderr,
        )
        return 2
    if not settings.telegram_allowed_user_ids:
        print("TELEGRAM_ALLOWED_USER_IDS is empty; refusing to start an open bot.", file=sys.stderr)
        return 2

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        try:
            me = await bot.get_me()
        except TelegramUnauthorizedError:
            print("TELEGRAM_BOT_TOKEN is invalid (Telegram rejected it).", file=sys.stderr)
            return 2
        except (TelegramNetworkError, OSError) as exc:
            print(
                f"Cannot reach the Telegram API ({type(exc).__name__}). Check the network.",
                file=sys.stderr,
            )
            return 1
        logging.getLogger(__name__).info("telegram_bot_started", extra={"bot": me.username})
        dp = build_dispatcher()
        await bot.set_my_commands([BotCommand(command=c, description=d) for c, d in COMMANDS])
        notifier = asyncio.create_task(notifier_loop(bot))
        try:
            await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
        finally:
            notifier.cancel()
        return 0
    finally:
        await bot.session.close()
