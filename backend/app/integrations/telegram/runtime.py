"""Glue between async aiogram handlers and the synchronous service layer."""

import asyncio
from collections.abc import Callable
from typing import TypeVar

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.database import get_sessionmaker
from app.services.telegram import Button, TelegramService

T = TypeVar("T")


def _run(fn: Callable[[TelegramService], T]) -> T:
    with get_sessionmaker()() as session:
        return fn(TelegramService(session))


async def with_service(fn: Callable[[TelegramService], T]) -> T:
    """Run blocking DB work in a worker thread with its own session."""
    return await asyncio.to_thread(_run, fn)


def keyboard(rows: list[list[Button]]) -> InlineKeyboardMarkup | None:
    if not rows:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=b.text, url=b.url)
                if b.url
                else InlineKeyboardButton(text=b.text, callback_data=b.callback_data)
                for b in row
            ]
            for row in rows
        ]
    )
