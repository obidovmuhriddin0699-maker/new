from pydantic import SecretStr

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
    # PHASE 7: the app secret exists but is a SecretStr and empty by default.
    assert s.meta_app_secret.get_secret_value() == ""
    shown = s.model_copy(update={"meta_app_secret": SecretStr("top-secret-value")})
    assert "top-secret-value" not in repr(shown)
