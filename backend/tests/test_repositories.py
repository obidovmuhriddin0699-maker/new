from datetime import timedelta

import pytest

from app.models import (
    AIJob,
    AnalyticsSnapshot,
    BrandProfile,
    ContentPerformance,
    InstagramAccount,
    OAuthToken,
    User,
)
from app.models.base import utcnow
from app.models.enums import AIJobStatus, ContentStatus, ContentType
from app.repositories import (
    AIJobRepository,
    AnalyticsSnapshotRepository,
    AuditLogRepository,
    BrandProfileRepository,
    ContentPerformanceRepository,
    ContentRepository,
    InstagramAccountRepository,
    OAuthTokenRepository,
    SystemSettingRepository,
    UserRepository,
)
from tests.conftest import make_content


def test_user_repository(db):
    repo = UserRepository(db)
    assert not repo.exists_any()
    user = repo.add(User(email="x@example.com", password_hash="h", telegram_user_id=42))
    db.commit()
    assert repo.get(user.id) is user
    assert repo.get_by_email("X@Example.com") is user
    assert repo.get_by_telegram_id(42) is user
    assert repo.get_active(user.id) is user
    user.is_active = False
    assert repo.get_active(user.id) is None
    assert repo.exists_any()


def test_soft_delete_hides_rows(db):
    repo = UserRepository(db)
    user = repo.add(User(email="gone@example.com", password_hash="h"))
    repo.soft_delete(user)
    db.commit()
    assert repo.get(user.id) is None
    assert repo.get(user.id, include_deleted=True) is user
    assert repo.count() == 0
    assert repo.count(include_deleted=True) == 1
    assert repo.get_by_email("gone@example.com") is None


def test_soft_delete_rejected_for_non_soft_models(db):
    job = AIJobRepository(db).add(AIJob(agent="a", input={}))
    with pytest.raises(TypeError):
        AIJobRepository(db).soft_delete(job)


def test_instagram_and_token_repositories(db, user):
    accounts = InstagramAccountRepository(db)
    account = accounts.add(InstagramAccount(user_id=user.id, ig_user_id="ig-1", username="m"))
    tokens = OAuthTokenRepository(db)
    old = tokens.add(OAuthToken(instagram_account_id=account.id, token_ciphertext="c1"))
    new = tokens.add(OAuthToken(instagram_account_id=account.id, token_ciphertext="c2"))
    old.revoked_at = utcnow()
    db.commit()
    assert accounts.get_by_ig_user_id("ig-1") is account
    assert list(accounts.list_for_user(user.id)) == [account]
    assert tokens.get_active_for_account(account.id) is new
    assert list(tokens.list_active_for_account(account.id)) == [new]


def test_content_repository_search(db, human):
    a = make_content(db, human, content_type=ContentType.REELS)
    make_content(db, human, content_type=ContentType.POST)
    repo = ContentRepository(db)
    rows, total = repo.search(content_type=ContentType.REELS)
    assert total == 1 and rows[0].id == a.id
    rows, total = repo.search(status=ContentStatus.DRAFT, limit=1)
    assert total == 2 and len(rows) == 1
    assert repo.get_for_update(a.id) is a


def test_brand_profile_repository(db):
    repo = BrandProfileRepository(db)
    repo.add(BrandProfile(name="A", is_default=False))
    b = repo.add(BrandProfile(name="B", is_default=True))
    db.commit()
    assert repo.get_by_name("A").name == "A"
    assert repo.get_default() is b


def test_ai_job_repository(db):
    repo = AIJobRepository(db)
    repo.add(AIJob(agent="planner", input={"q": 1}, status=AIJobStatus.QUEUED))
    repo.add(AIJob(agent="planner", input={}, status=AIJobStatus.FAILED))
    db.commit()
    assert len(repo.list_by_status(AIJobStatus.QUEUED)) == 1


def test_analytics_and_performance_repositories(db, user, human):
    account = InstagramAccountRepository(db).add(
        InstagramAccount(user_id=user.id, ig_user_id="ig-2")
    )
    content = make_content(db, human)
    snaps = AnalyticsSnapshotRepository(db)
    now = utcnow()
    snaps.add(
        AnalyticsSnapshot(
            instagram_account_id=account.id,
            scope="account",
            captured_at=now - timedelta(days=10),
            metrics={"reach": 1},
        )
    )
    snaps.add(
        AnalyticsSnapshot(
            instagram_account_id=account.id,
            scope="media",
            content_id=content.id,
            captured_at=now,
            metrics={"likes": 3},
        )
    )
    perf = ContentPerformanceRepository(db)
    perf.add(ContentPerformance(content_id=content.id, metrics={"likes": 3}))
    db.commit()
    assert len(snaps.list_for_account(account.id)) == 2
    assert len(snaps.list_for_account(account.id, since=now - timedelta(days=1))) == 1
    assert len(snaps.list_for_account(account.id, scope="account")) == 1
    assert perf.get_for_content(content.id).metrics == {"likes": 3}


def test_system_setting_repository(db):
    repo = SystemSettingRepository(db)
    assert repo.get_value("missing", default="d") == "d"
    repo.set_value("k", {"a": 1}, "desc")
    repo.set_value("k", [1, 2])
    db.commit()
    assert repo.get_value("k") == [1, 2]
    assert repo.get("k").description == "desc"


def test_audit_repository_is_append_only():
    for forbidden in ("update", "delete", "soft_delete_all"):
        assert not hasattr(AuditLogRepository, forbidden)


def test_utc_datetimes_are_timezone_aware(db, human):
    content = make_content(db, human)
    db.expire_all()
    reloaded = ContentRepository(db).get(content.id)
    assert reloaded.created_at.tzinfo is not None
    assert reloaded.created_at <= utcnow()
