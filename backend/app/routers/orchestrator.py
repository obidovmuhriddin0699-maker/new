from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import CurrentUser, CsrfSession, require_membership
from backend.app.models import Workflow, WorkflowPhase
from backend.app.ollama import OllamaAdapter, get_ollama_adapter
from backend.app.orchestrator import create_workflow, get_workflow, run_workflow
from backend.app.schemas import WorkflowCreate, WorkflowPhaseResponse, WorkflowResponse


router = APIRouter(prefix="/workspaces/{workspace_id}/workflows", tags=["orchestrator"])


def serialize_workflow(db: Session, workflow: Workflow) -> WorkflowResponse:
    phases = db.scalars(
        select(WorkflowPhase)
        .where(WorkflowPhase.workflow_id == workflow.id)
        .order_by(WorkflowPhase.sequence)
    )
    return WorkflowResponse(
        id=workflow.id,
        workspace_id=workflow.workspace_id,
        created_by_user_id=workflow.created_by_user_id,
        title=workflow.title,
        task=workflow.task,
        status=workflow.status,
        last_error=workflow.last_error,
        phases=[
            WorkflowPhaseResponse(
                name=phase.name,
                status=phase.status,
                attempt_count=phase.attempt_count,
                output=phase.output,
                model=phase.model,
            )
            for phase in phases
        ],
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
    )


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create(
    workspace_id: str,
    payload: WorkflowCreate,
    auth_session: CsrfSession,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> WorkflowResponse:
    require_membership(workspace_id, user, db)
    workflow = create_workflow(
        db,
        workspace_id,
        user.id,
        payload.title,
        payload.task,
    )
    return serialize_workflow(db, workflow)


@router.get("", response_model=list[WorkflowResponse])
def list_for_workspace(
    workspace_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[WorkflowResponse]:
    require_membership(workspace_id, user, db)
    workflows = db.scalars(
        select(Workflow)
        .where(Workflow.workspace_id == workspace_id)
        .order_by(Workflow.created_at.desc(), Workflow.id)
    )
    return [serialize_workflow(db, workflow) for workflow in workflows]


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get(
    workspace_id: str,
    workflow_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> WorkflowResponse:
    require_membership(workspace_id, user, db)
    workflow = get_workflow(db, workspace_id, workflow_id)
    return serialize_workflow(db, workflow)


@router.post("/{workflow_id}/run", response_model=WorkflowResponse)
def run(
    workspace_id: str,
    workflow_id: str,
    auth_session: CsrfSession,
    user: CurrentUser,
    db: Session = Depends(get_db),
    ollama: OllamaAdapter = Depends(get_ollama_adapter),
) -> WorkflowResponse:
    require_membership(workspace_id, user, db)
    workflow = run_workflow(db, workspace_id, workflow_id, ollama)
    return serialize_workflow(db, workflow)
