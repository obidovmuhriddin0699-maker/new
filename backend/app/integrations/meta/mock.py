"""In-memory mock used by tests and local development. Never talks to Meta."""

from app.integrations.meta.base import MetaAccountInfo, MetaCapability, MetaInstagramClient


class MockMetaInstagramClient(MetaInstagramClient):
    def __init__(self, username: str = "muxriddin.design.mock") -> None:
        self._info = MetaAccountInfo(
            ig_user_id="mock-ig-user-0001", username=username, account_type="BUSINESS"
        )

    async def get_account_info(self) -> MetaAccountInfo:
        return self._info

    def supported_capabilities(self) -> frozenset[MetaCapability]:
        return frozenset(MetaCapability)
