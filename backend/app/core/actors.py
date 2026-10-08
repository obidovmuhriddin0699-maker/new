"""Who is performing an operation.

Every service method that changes state receives an ``Actor``. Approval-type
operations accept only ``HumanActor``, and the approval service additionally
re-verifies the referenced user in the database, so constructing a
``HumanActor`` in code is not enough to forge an approval.
"""

from dataclasses import dataclass, field

from app.agents.permissions import AgentTool
from app.models.enums import ActorType, ApprovalChannel


@dataclass(frozen=True, slots=True)
class HumanActor:
    """An authenticated human. Built only from a verified session (JWT / Telegram)."""

    user_id: int
    channel: ApprovalChannel = ApprovalChannel.WEB
    request_id: str | None = None

    @property
    def actor_type(self) -> ActorType:
        return ActorType.HUMAN

    @property
    def display_name(self) -> str:
        return f"user:{self.user_id}"


@dataclass(frozen=True, slots=True)
class AgentActor:
    """An AI agent. Never carries a user id and never has publish/approve tools."""

    name: str
    tools: frozenset[AgentTool] = field(default_factory=frozenset)

    @property
    def actor_type(self) -> ActorType:
        return ActorType.AGENT

    @property
    def display_name(self) -> str:
        return f"agent:{self.name}"


@dataclass(frozen=True, slots=True)
class SystemActor:
    """Internal backend job (scheduler, publish worker). Not an AI agent."""

    name: str

    @property
    def actor_type(self) -> ActorType:
        return ActorType.SYSTEM

    @property
    def display_name(self) -> str:
        return f"system:{self.name}"


Actor = HumanActor | AgentActor | SystemActor

# The only system component that may move content into PUBLISHING (PHASE 8).
PUBLISH_SERVICE_NAME = "publish_service"
