"""PHASE 12: operations monitor (OPS_ALERT -> Telegram). No real Redis, Meta or disk needed."""

from datetime import timedelta
from types import SimpleNamespace

import pytest
from sqlalchemy import select, update

from app.core.actors import SystemActor
from app.core.config import get_settings
from app.core.transaction import atomic
from app.models import AuditLog, ContentSchedule, OAuthToken
from app.models.base import utcnow
from app.models.enums import AuditAction, ScheduleStatus
from app.repositories import SystemSettingRepository
from app.services import ScheduleService
from app.services import ops as ops_module
from app.services.audit import AuditLogService
from app.services.ops import BACKUP_KEY, STATE_KEY, OpsMonitor
from tests.conftest import make_approved


@pytest.fixture(autouse=True)
def _healthy_host(monkeypatch):
    """Redis up and plenty of disk, whatever the machine running the tests looks like."""
    monkeypatch.setattr(ops_module, "check_redis", lambda: (True, None))
    plenty = SimpleNamespace(total=100, used=10, free=90)
    monkeypatch.setattr(ops_module.shutil, "disk_usage", lambda _p: plenty)


def keys(db) -> set[str]:
    return {p.key for p in OpsMonitor(db).problems()}


def alerts(db) -> list[AuditLog]:
    return list(
        db.scalars(
            select(AuditLog)
            .where(AuditLog.action == AuditAction.OPS_ALERT.value)
            .order_by(AuditLog.id)
        )
    )


def scheduled(db, human, *, at, status=ScheduleStatus.PENDING, **fields) -> ContentSchedule:
    content = make_approved(db, human)
    row = ScheduleService(db).schedule(
        content.id, human, scheduled_at=utcnow() + timedelta(hours=1)
    )
    db.execute(
        update(ContentSchedule)
        .where(ContentSchedule.id == row.schedule.id)
        .values(scheduled_at=at, status=status, **fields)
    )
    db.commit()
    return row.schedule


def test_healthy_system_has_no_problems_and_no_alert(db):
    assert OpsMonitor(db).run() == []
    assert alerts(db) == []


def test_redis_down_is_critical(db, monkeypatch):
    monkeypatch.setattr(ops_module, "check_redis", lambda: (False, "Connection refused"))
    [p] = OpsMonitor(db).problems()
    assert (p.key, p.severity) == ("redis", "critical")


def test_alert_only_on_change_then_daily_reminder_then_resolved(db, monkeypatch):
    down = {"v": True}
    monkeypatch.setattr(ops_module, "check_redis", lambda: (not down["v"], "x"))
    OpsMonitor(db).run()
    OpsMonitor(db).run()  # same problem -> no duplicate
    assert len(alerts(db)) == 1
    assert alerts(db)[0].status == "FAILED"

    # 25 h later the problem is still there -> one reminder
    state = SystemSettingRepository(db).get_value(STATE_KEY)
    with atomic(db):
        SystemSettingRepository(db).set_value(
            STATE_KEY, {**state, "at": (utcnow() - timedelta(hours=25)).isoformat()}
        )
    OpsMonitor(db).run()
    assert len(alerts(db)) == 2

    down["v"] = False
    OpsMonitor(db).run()
    last = alerts(db)[-1]
    assert len(alerts(db)) == 3
    assert last.status == "SUCCESS"
    assert last.details["problems"] == [] and last.details["resolved"] == ["redis"]
    OpsMonitor(db).run()  # healthy and already reported -> silent
    assert len(alerts(db)) == 3


def test_failed_stuck_and_overdue_schedules(db, human, monkeypatch):
    now = utcnow()
    scheduled(db, human, at=now - timedelta(hours=1), status=ScheduleStatus.FAILED)
    scheduled(
        db,
        human,
        at=now - timedelta(hours=1),
        status=ScheduleStatus.PROCESSING,
        processing_started_at=now - timedelta(minutes=45),
    )
    scheduled(db, human, at=now - timedelta(minutes=20))
    monkeypatch.setenv("META_DRY_RUN", "false")
    get_settings.cache_clear()
    assert {"publish:failed", "publish:stuck", "publish:overdue"} <= keys(db)


def test_overdue_is_ignored_in_dry_run_and_fresh_rows_are_fine(db, human):
    now = utcnow()
    scheduled(db, human, at=now - timedelta(minutes=20))  # dry run: nothing is published
    scheduled(
        db,
        human,
        at=now,
        status=ScheduleStatus.PROCESSING,
        processing_started_at=now - timedelta(minutes=5),
    )
    assert keys(db) == set()


def test_instagram_reconnect_and_expiry(db, ig_account):
    assert keys(db) == set()
    db.execute(
        update(OAuthToken)
        .where(OAuthToken.instagram_account_id == ig_account.id)
        .values(expires_at=utcnow() + timedelta(days=2))
    )
    db.commit()
    assert keys(db) == {f"instagram:{ig_account.id}:expiring"}
    db.execute(
        update(OAuthToken)
        .where(OAuthToken.instagram_account_id == ig_account.id)
        .values(expires_at=utcnow() - timedelta(minutes=1))
    )
    db.commit()
    problems = OpsMonitor(db).problems()
    assert [(p.key, p.severity) for p in problems] == [
        (f"instagram:{ig_account.id}:reconnect", "critical")
    ]
    assert "@muxriddin.design" in problems[0].message


@pytest.fixture
def production(monkeypatch):
    """Only the backup check looks at APP_ENV; fake it instead of a full production config."""
    real = get_settings()
    monkeypatch.setattr(
        ops_module,
        "get_settings",
        lambda: SimpleNamespace(
            app_env="production",
            meta_dry_run=True,
            media_root=real.media_root,
            backup_monitoring=getattr(real, "backup_monitoring", True),
        ),
    )


def set_backup(db, value):
    with atomic(db):
        SystemSettingRepository(db).set_value(BACKUP_KEY, value)


def test_backups_are_not_checked_outside_production(db):
    assert keys(db) == set()


def test_backup_states_in_production(db, production):
    assert keys(db) == {"backup:missing"}
    set_backup(db, {"ok": False, "at": utcnow().isoformat(), "error": "pg_dump failed"})
    [p] = OpsMonitor(db).problems()
    assert (p.key, p.severity) == ("backup:failed", "critical")
    assert "pg_dump failed" in p.message
    set_backup(db, {"ok": True, "at": (utcnow() - timedelta(hours=30)).isoformat()})
    assert keys(db) == {"backup:stale"}
    # format written by docker/backup/backup.sh
    set_backup(db, {"ok": True, "at": utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")})
    assert keys(db) == set()


def test_backup_check_can_be_turned_off(db, monkeypatch):
    """Platforms with their own database backups (Railway) have no backup service."""
    monkeypatch.setenv("BACKUP_MONITORING", "false")
    get_settings.cache_clear()
    real = get_settings()
    monkeypatch.setattr(
        ops_module,
        "get_settings",
        lambda: SimpleNamespace(
            app_env="production",
            meta_dry_run=True,
            media_root=real.media_root,
            backup_monitoring=real.backup_monitoring,
        ),
    )
    assert keys(db) == set()


def test_latest_analytics_sync_failure_warns(db):
    service = AuditLogService(db)
    actor = SystemActor("analytics")
    with atomic(db):
        service.record(AuditAction.ANALYTICS_SYNC_FAILED, actor, status="FAILED", error="(#10) x")
    assert keys(db) == {"analytics:sync"}
    with atomic(db):
        service.record(AuditAction.ANALYTICS_SYNCED, actor)
    assert keys(db) == set()


def test_low_disk(db, monkeypatch):
    usage = SimpleNamespace(total=100, used=96, free=4)
    monkeypatch.setattr(ops_module.shutil, "disk_usage", lambda _p: usage)
    [p] = OpsMonitor(db).problems()
    assert (p.key, p.severity) == ("disk", "critical")
    usage.free = 8
    assert OpsMonitor(db).problems()[0].severity == "warning"


def test_ops_alert_reaches_telegram(db, linked_owner, monkeypatch):
    from app.services.telegram import TelegramService

    TelegramService(db).init_notify_cursor()
    monkeypatch.setattr(ops_module, "check_redis", lambda: (False, "refused"))
    OpsMonitor(db).run()
    monkeypatch.setattr(ops_module, "check_redis", lambda: (True, None))
    OpsMonitor(db).run()
    messages, _ = TelegramService(db).collect_review_notifications()
    texts = [m.text for _, m in messages]
    assert any("Tizim ogohlantirishi" in t and "🔴" in t and "Redis" in t for t in texts)
    assert any("Tizim holati tiklandi" in t for t in texts)
    assert all(not m.buttons for _, m in messages)


def test_ops_check_task_is_scheduled():
    from app.workers.celery_app import celery_app
    from app.workers.tasks.system import ops_check  # noqa: F401  (registers the task)

    assert "ops.check" in celery_app.tasks
    assert celery_app.conf.beat_schedule["ops-check"]["task"] == "ops.check"


def test_ops_status_api(client, auth_headers, db, viewer, monkeypatch):
    from app.core.security import create_access_token

    assert client.get("/api/v1/system/ops-status").status_code == 401
    body = client.get("/api/v1/system/ops-status", headers=auth_headers).json()
    assert body == {"ok": True, "problems": []}
    monkeypatch.setattr(ops_module, "check_redis", lambda: (False, "refused"))
    body = client.get("/api/v1/system/ops-status", headers=auth_headers).json()
    assert body["ok"] is False and body["problems"][0]["key"] == "redis"
    assert alerts(db) == []  # viewing never sends alerts
    token = create_access_token(str(viewer.user_id))
    denied = client.get("/api/v1/system/ops-status", headers={"Authorization": f"Bearer {token}"})
    assert denied.status_code == 403
