from sqlalchemy import inspect as sa_inspect

import app.models as models
from app.models import Base, InstagramAccount, OAuthToken, User

ENTITIES = [
    "User",
    "InstagramAccount",
    "OAuthToken",
    "Content",
    "ContentAsset",
    "ContentSchedule",
    "Approval",
    "AnalyticsSnapshot",
    "ContentPerformance",
    "BrandProfile",
    "AIJob",
    "AuditLog",
    "SystemSetting",
    "OAuthState",
    "DataDeletionRequest",
    "AnalyticsReport",
    "RevokedToken",
]


def test_all_entities_importable():
    for name in ENTITIES:
        assert hasattr(models, name), name
    # 13 core entities + content_versions + 2 Telegram tables (PHASE 5)
    # + oauth_states and data_deletion_requests (PHASE 7) + analytics_reports (PHASE 9)
    # + revoked_tokens (PHASE 10)
    assert len(Base.metadata.tables) == 20


def test_no_instagram_password_column():
    for model in (User, InstagramAccount, OAuthToken):
        cols = {c.key for c in sa_inspect(model).columns}
        assert not any("instagram_password" in c or c == "ig_password" for c in cols)
    ig_cols = {c.key for c in sa_inspect(InstagramAccount).columns}
    assert not any("password" in c for c in ig_cols)


def test_oauth_token_has_only_ciphertext():
    cols = {c.key for c in sa_inspect(OAuthToken).columns}
    assert "token_ciphertext" in cols
    assert "access_token" not in cols and "token" not in cols


def test_oauth_token_repr_hides_ciphertext():
    t = OAuthToken(id=1, instagram_account_id=2, token_ciphertext="SECRET-CIPHERTEXT")
    assert "SECRET" not in repr(t)


def test_soft_delete_on_key_entities():
    for name in ("User", "InstagramAccount", "Content", "ContentAsset", "BrandProfile"):
        assert "deleted_at" in {c.key for c in sa_inspect(getattr(models, name)).columns}


def test_schedule_idempotency_key_unique():
    col = models.ContentSchedule.__table__.c.idempotency_key
    assert col.unique
