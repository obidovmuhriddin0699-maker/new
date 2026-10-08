import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import CurrentUser, CsrfSession
from backend.app.models import TelegramAccount
from backend.app.schemas import TelegramLinkCodeResponse, TelegramLinkStatusResponse
from backend.app.telegram import create_link_code, revoke_telegram_link


router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/link-code", response_model=TelegramLinkCodeResponse)
def generate_link_code(
    auth_session: CsrfSession,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> TelegramLinkCodeResponse:
    result = create_link_code(
        db,
        user.id,
        os.getenv("TELEGRAM_BOT_USERNAME", "").lstrip("@") or None,
    )
    return TelegramLinkCodeResponse(**result)


@router.get("/link", response_model=TelegramLinkStatusResponse)
def get_link_status(
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> TelegramLinkStatusResponse:
    account = db.scalar(
        select(TelegramAccount).where(TelegramAccount.user_id == user.id)
    )
    return TelegramLinkStatusResponse(
        linked=account is not None,
        workspace_id=account.workspace_id if account else None,
    )


@router.delete("/link", status_code=status.HTTP_204_NO_CONTENT)
def unlink_account(
    auth_session: CsrfSession,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> None:
    revoke_telegram_link(db, user.id)
