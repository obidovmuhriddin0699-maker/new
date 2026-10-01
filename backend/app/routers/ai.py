from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.billing import ensure_billing_account, enforce_and_record_usage
from backend.app.database import get_db
from backend.app.dependencies import CurrentUser, CsrfSession, require_membership
from backend.app.ollama import OllamaAdapter, get_ollama_adapter
from backend.app.schemas import AIChatRequest, AIChatResponse


router = APIRouter(prefix="/workspaces/{workspace_id}/ai", tags=["ai"])


@router.post("/chat", response_model=AIChatResponse)
def chat(
    workspace_id: str,
    payload: AIChatRequest,
    auth_session: CsrfSession,
    user: CurrentUser,
    db: Session = Depends(get_db),
    ollama: OllamaAdapter = Depends(get_ollama_adapter),
) -> AIChatResponse:
    require_membership(workspace_id, user, db)
    billing = ensure_billing_account(db, workspace_id)
    enforce_and_record_usage(
        db,
        billing,
        workspace_id,
        "ai_requests",
        1,
    )
    result = ollama.chat(payload.prompt, payload.system)
    db.commit()
    return AIChatResponse(**result)
