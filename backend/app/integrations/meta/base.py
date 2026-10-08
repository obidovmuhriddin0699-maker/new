"""Meta / Instagram integration interface (PHASE 1: interface + mock only).

No real HTTP client exists yet. The real implementation (PHASE 7/8) will be
written against the official Meta documentation, using Instagram Login by
default. Endpoint paths, API version and scope names come from configuration.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum


class MetaCapability(StrEnum):
    IMAGE_POST = "IMAGE_POST"
    CAROUSEL = "CAROUSEL"
    REELS = "REELS"
    STORY = "STORY"
    INSIGHTS = "INSIGHTS"


@dataclass(slots=True)
class MetaAccountInfo:
    ig_user_id: str
    username: str
    account_type: str


class MetaInstagramClient(ABC):
    """Read-only surface for PHASE 1. Publishing methods are added in PHASE 8,
    behind the approval-gated publish service — never exposed to agents."""

    @abstractmethod
    async def get_account_info(self) -> MetaAccountInfo: ...

    @abstractmethod
    def supported_capabilities(self) -> frozenset[MetaCapability]: ...
