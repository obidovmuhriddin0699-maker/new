from app.core.config import get_settings
from app.integrations.meta.base import MetaCapability
from app.integrations.meta.mock import MockMetaInstagramClient


async def test_mock_client_never_hits_network():
    client = MockMetaInstagramClient()
    info = await client.get_account_info()
    assert info.ig_user_id.startswith("mock-")
    assert MetaCapability.REELS in client.supported_capabilities()


def test_meta_defaults_are_safe():
    s = get_settings()
    assert s.meta_dry_run is True
    assert s.meta_login_mode == "instagram"
    # No Meta secrets are part of PHASE 1 configuration.
    assert not any(name.startswith("meta_app_secret") for name in type(s).model_fields)
