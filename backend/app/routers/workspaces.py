import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.billing import ensure_billing_account
from backend.app.database import get_db
from backend.app.dependencies import (
    CurrentUser,
    CsrfSession,
    require_membership,
    require_workspace_admin,
)
from backend.app.models import Membership, User, Workspace
from backend.app.schemas import (
    MemberCreate,
    MembershipResponse,
    MemberRoleUpdate,
    WorkspaceCreate,
    WorkspaceResponse,
)


router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(user: CurrentUser, db: Session = Depends(get_db)) -> list[WorkspaceResponse]:
    rows = db.execute(
        select(Workspace, Membership.role)
        .join(Membership, Membership.workspace_id == Workspace.id)
        .where(Membership.user_id == user.id)
        .order_by(Workspace.name)
    ).all()
    return [
        WorkspaceResponse(id=workspace.id, name=workspace.name, role=role)
        for workspace, role in rows
    ]


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreate,
    auth_session: CsrfSession,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    workspace = Workspace(id=str(uuid.uuid4()), name=payload.name)
    db.add(workspace)
    db.flush()
    db.add(
        Membership(
            id=str(uuid.uuid4()),
            workspace_id=workspace.id,
            user_id=user.id,
            role="owner",
        )
    )
    ensure_billing_account(db, workspace.id)
    auth_session.active_workspace_id = workspace.id
    db.commit()
    return WorkspaceResponse(id=workspace.id, name=workspace.name, role="owner")


@router.post("/{workspace_id}/select", response_model=WorkspaceResponse)
def select_workspace(
    workspace_id: str,
    auth_session: CsrfSession,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    membership = require_membership(workspace_id, user, db)
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    auth_session.active_workspace_id = workspace.id
    db.commit()
    return WorkspaceResponse(id=workspace.id, name=workspace.name, role=membership.role)


@router.get("/{workspace_id}/members", response_model=list[MembershipResponse])
def list_members(
    workspace_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[MembershipResponse]:
    require_membership(workspace_id, user, db)
    rows = db.execute(
        select(User, Membership.role)
        .join(Membership, Membership.user_id == User.id)
        .where(Membership.workspace_id == workspace_id)
        .order_by(User.email)
    ).all()
    return [
        MembershipResponse(user_id=member.id, email=member.email, role=role)
        for member, role in rows
    ]


@router.post(
    "/{workspace_id}/members",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    workspace_id: str,
    payload: MemberCreate,
    auth_session: CsrfSession,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> MembershipResponse:
    actor_membership = require_workspace_admin(workspace_id, user, db)
    if actor_membership.role == "admin" and payload.role != "member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can add admins")

    member = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    existing = db.scalar(
        select(Membership).where(
            Membership.workspace_id == workspace_id,
            Membership.user_id == member.id,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member")

    membership = Membership(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        user_id=member.id,
        role=payload.role,
    )
    db.add(membership)
    db.commit()
    return MembershipResponse(user_id=member.id, email=member.email, role=payload.role)


@router.patch(
    "/{workspace_id}/members/{member_user_id}",
    response_model=MembershipResponse,
)
def update_member_role(
    workspace_id: str,
    member_user_id: str,
    payload: MemberRoleUpdate,
    auth_session: CsrfSession,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> MembershipResponse:
    actor_membership = require_workspace_admin(workspace_id, user, db)
    membership = db.scalar(
        select(Membership).where(
            Membership.workspace_id == workspace_id,
            Membership.user_id == member_user_id,
        )
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if membership.role == "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role cannot be changed")
    if actor_membership.role == "admin" and membership.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins cannot manage admins")
    if actor_membership.role == "admin" and payload.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can add admins")

    member = db.get(User, member_user_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    membership.role = payload.role
    db.commit()
    return MembershipResponse(user_id=member.id, email=member.email, role=membership.role)
