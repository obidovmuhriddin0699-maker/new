"""Telegram linking endpoints for the admin panel."""

from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.api.deps import DbSession, HumanActorDep
from app.core.config import get_settings
from app.schemas.errors import error_responses
from app.services.guards import require_active_human
from app.services.telegram import TelegramService

router = APIRouter(prefix="/telegram", tags=["telegram"])


class TelegramStatus(BaseModel):
    enabled: bool = Field(description="Bot configured (TELEGRAM_ENABLED + token)")
    bot_username: str | None
    linked: bool
    telegram_user_id: int | None
    allowed: bool = Field(description="Linked Telegram id is in TELEGRAM_ALLOWED_USER_IDS")
    commands: list[str]


class LinkCode(BaseModel):
    code: str
    expires_at: datetime
    deep_link: str | None
    instructions: str


COMMANDS = [
    "/start",
    "/content",
    "/plan",
    "/reels",
    "/story",
    "/status",
    "/approve",
    "/reject",
    "/analytics",
    "/settings",
]


@router.get(
    "/status",
    response_model=TelegramStatus,
    summary="Telegram bot and link status",
    responses=error_responses(401),
)
def telegram_status(db: DbSession, actor: HumanActorDep) -> TelegramStatus:
    user = require_active_human(db, actor)
    s = get_settings()
    return TelegramStatus(
        enabled=s.telegram_enabled and bool(s.telegram_bot_token.get_secret_value()),
        bot_username=s.telegram_bot_username or None,
        linked=user.telegram_user_id is not None,
        telegram_user_id=user.telegram_user_id,
        allowed=user.telegram_user_id in s.telegram_allowed_user_ids,
        commands=COMMANDS,
    )


@router.post(
    "/link-code",
    response_model=LinkCode,
    status_code=status.HTTP_201_CREATED,
    summary="Create a one-time code to link your Telegram account",
    description="The code is shown once, stored only as a hash and expires quickly. "
    "Your Telegram ID must also be listed in TELEGRAM_ALLOWED_USER_IDS.",
    responses=error_responses(401, 403),
)
def create_link_code(db: DbSession, actor: HumanActorDep) -> LinkCode:
    code, expires = TelegramService(db).create_link_code(actor)
    username = get_settings().telegram_bot_username
    compact = code.replace("-", "")
    return LinkCode(
        code=code,
        expires_at=expires,
        deep_link=f"https://t.me/{username}?start={compact}" if username else None,
        instructions=f"Botga yuboring: /start {code}",
    )


@router.delete(
    "/link",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlink your Telegram account",
    responses=error_responses(401),
)
def unlink(db: DbSession, actor: HumanActorDep) -> None:
    TelegramService(db).unlink(actor)
