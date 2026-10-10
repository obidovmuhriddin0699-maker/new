"""Server-side authorization checks shared by services."""

from sqlalchemy.orm import Session

from app.agents.permissions import AgentTool, is_allowed
from app.core.actors import PUBLISH_SERVICE_NAME, Actor, AgentActor, HumanActor, SystemActor
from app.core.errors import ApprovalForbiddenError, PermissionDeniedError
from app.models import User
from app.models.enums import UserRole
from app.repositories import UserRepository

WRITER_ROLES = frozenset({UserRole.OWNER, UserRole.ADMIN})
APPROVER_ROLES = frozenset({UserRole.OWNER, UserRole.ADMIN})


def require_active_human(session: Session, actor: Actor) -> User:
    if not isinstance(actor, HumanActor):
        raise PermissionDeniedError("This operation requires a human user")
    user = UserRepository(session).get_active(actor.user_id)
    if user is None:
        raise PermissionDeniedError("User not found or inactive")
    return user


def require_human_writer(session: Session, actor: Actor) -> User:
    user = require_active_human(session, actor)
    if user.role not in WRITER_ROLES:
        raise PermissionDeniedError("Your role cannot modify content")
    return user


def require_human_approver(session: Session, actor: Actor) -> User:
    """Approval decisions: only a verified, active human with an approver role."""
    if not isinstance(actor, HumanActor):
        raise ApprovalForbiddenError("Only a human user can approve, reject or request edits")
    user = UserRepository(session).get_active(actor.user_id)
    if user is None:
        raise ApprovalForbiddenError("Approving user not found or inactive")
    if user.role not in APPROVER_ROLES:
        raise ApprovalForbiddenError("Your role cannot make approval decisions")
    return user


def require_writer(session: Session, actor: Actor, agent_tool: AgentTool) -> None:
    """Human writer, or an agent that holds ``agent_tool``. System actors are not writers."""
    if isinstance(actor, AgentActor):
        if not is_allowed(actor.tools, agent_tool.value):
            raise PermissionDeniedError(f"Agent '{actor.name}' lacks {agent_tool.value}")
        return
    require_human_writer(session, actor)


def require_publish_service(actor: Actor) -> SystemActor:
    """Only the backend publish service may drive publishing states (never an agent)."""
    if not isinstance(actor, SystemActor) or actor.name != PUBLISH_SERVICE_NAME:
        raise PermissionDeniedError("Only the publish service can perform this operation")
    return actor
