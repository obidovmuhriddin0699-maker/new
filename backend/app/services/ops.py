"""Operations monitor: problems an owner must act on, alerted via Telegram.

Runs every 5 minutes (Celery beat ``ops.check``). An ``OPS_ALERT`` audit event — which the
Telegram notifier forwards to linked approvers — is recorded only when the set of problems
changes (new problem or all resolved), plus a daily reminder while something stays broken.
"""

import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.actors import SystemActor
from app.core.config import get_settings
from app.core.redis import check_redis
from app.core.transaction import atomic
from app.models import AuditLog, ContentSchedule
from app.models.base import utcnow
from app.models.enums import AuditAction, ScheduleStatus
from app.repositories import SystemSettingRepository

OPS_ACTOR = SystemActor("ops_monitor")
STATE_KEY = "ops.alert_state"
BACKUP_KEY = "ops.last_backup"
REMIND_EVERY = timedelta(hours=24)

Severity = Literal["critical", "warning"]


@dataclass(frozen=True, slots=True)
class Problem:
    key: str
    severity: Severity
    message: str


def _parse(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


class OpsMonitor:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()

    # ------------------------------------------------------------------ checks
    def problems(self) -> list[Problem]:
        out: list[Problem] = []
        out += self._redis()
        out += self._instagram()
        out += self._publishing()
        out += self._backups()
        out += self._analytics()
        out += self._disk()
        return out

    def _redis(self) -> list[Problem]:
        ok, error = check_redis()
        return (
            []
            if ok
            else [
                Problem(
                    "redis",
                    "critical",
                    f"Redis ishlamayapti ({error}): navbat va limitlar to‘xtagan.",
                )
            ]
        )

    def _instagram(self) -> list[Problem]:
        from app.services.instagram_oauth import InstagramOAuthService

        out = []
        for s in InstagramOAuthService(self.session).statuses():
            name = f"@{s.account.username or s.account.ig_user_id}"
            if s.needs_reconnect:
                out.append(
                    Problem(
                        f"instagram:{s.account.id}:reconnect",
                        "critical",
                        f"{name}: Instagram’ni qayta ulash kerak (token yo‘q/muddati o‘tgan "
                        "yoki ruxsat yetishmaydi). Nashr ishlamaydi.",
                    )
                )
            elif s.token_expires_at and s.token_expires_at - utcnow() < timedelta(days=5):
                out.append(
                    Problem(
                        f"instagram:{s.account.id}:expiring",
                        "warning",
                        f"{name}: token {s.token_expires_at:%Y-%m-%d} da tugaydi va avtomatik "
                        "yangilanmadi — worker/beat ishlayotganini tekshiring.",
                    )
                )
        return out

    def _publishing(self) -> list[Problem]:
        now = utcnow()
        out = []
        failed = self.session.scalar(
            select(func.count())
            .select_from(ContentSchedule)
            .where(
                ContentSchedule.status == ScheduleStatus.FAILED,
                ContentSchedule.updated_at >= now - timedelta(hours=24),
            )
        )
        if failed:
            out.append(
                Problem(
                    "publish:failed",
                    "warning",
                    f"Oxirgi 24 soatda {failed} ta nashr muvaffaqiyatsiz — panelda ko‘ring.",
                )
            )
        stuck = self.session.scalar(
            select(func.count())
            .select_from(ContentSchedule)
            .where(
                ContentSchedule.status == ScheduleStatus.PROCESSING,
                ContentSchedule.processing_started_at < now - timedelta(minutes=30),
            )
        )
        if stuck:
            out.append(
                Problem(
                    "publish:stuck",
                    "critical",
                    f"{stuck} ta nashr 30 daqiqadan beri tugamagan (Meta javobi noma’lum yoki "
                    "worker to‘xtagan).",
                )
            )
        overdue = self.session.scalar(
            select(func.count())
            .select_from(ContentSchedule)
            .where(
                ContentSchedule.status == ScheduleStatus.PENDING,
                ContentSchedule.scheduled_at < now - timedelta(minutes=15),
            )
        )
        if overdue and not self.settings.meta_dry_run:
            out.append(
                Problem(
                    "publish:overdue",
                    "critical",
                    f"{overdue} ta rejalashtirilgan nashr vaqti o‘tib ketgan — Celery worker "
                    "yoki beat ishlamayapti.",
                )
            )
        return out

    def _backups(self) -> list[Problem]:
        if self.settings.app_env != "production" or not self.settings.backup_monitoring:
            return []
        last = SystemSettingRepository(self.session).get_value(BACKUP_KEY)
        if not isinstance(last, dict):
            return [Problem("backup:missing", "warning", "Hali birorta zaxira nusxa olinmagan.")]
        at = _parse(last.get("at"))
        if not last.get("ok"):
            return [
                Problem(
                    "backup:failed",
                    "critical",
                    f"Oxirgi zaxira nusxa muvaffaqiyatsiz: {last.get('error', 'noma’lum xato')}.",
                )
            ]
        if at is None or utcnow() - at > timedelta(hours=26):
            return [
                Problem(
                    "backup:stale",
                    "critical",
                    f"Oxirgi zaxira nusxa {at:%Y-%m-%d %H:%M} UTC da — 26 soatdan eski."
                    if at
                    else "Zaxira nusxa vaqti noma’lum.",
                )
            ]
        return []

    def _analytics(self) -> list[Problem]:
        last = self.session.scalars(
            select(AuditLog)
            .where(
                AuditLog.action.in_(
                    [AuditAction.ANALYTICS_SYNCED.value, AuditAction.ANALYTICS_SYNC_FAILED.value]
                ),
                AuditLog.timestamp >= utcnow() - timedelta(hours=24),
            )
            .order_by(AuditLog.id.desc())
            .limit(1)
        ).first()
        if last is not None and last.action == AuditAction.ANALYTICS_SYNC_FAILED.value:
            return [
                Problem(
                    "analytics:sync",
                    "warning",
                    f"Statistika sinxronlanmadi: {(last.error or '')[:200]}",
                )
            ]
        return []

    def _disk(self) -> list[Problem]:
        try:
            usage = shutil.disk_usage(self.settings.media_root)
        except OSError:
            return []
        free = usage.free / usage.total if usage.total else 1
        if free < 0.10:
            return [
                Problem(
                    "disk",
                    "critical" if free < 0.05 else "warning",
                    f"Media diskida joy kam: {free * 100:.0f}% bo‘sh.",
                )
            ]
        return []

    # ------------------------------------------------------------------ alerting
    def run(self) -> list[Problem]:
        problems = self.problems()
        repo = SystemSettingRepository(self.session)
        state = repo.get_value(STATE_KEY) or {}
        previous = set(state.get("keys", []))
        current = {p.key for p in problems}
        last_alert = _parse(state.get("at"))
        changed = current != previous
        remind = bool(current) and (last_alert is None or utcnow() - last_alert > REMIND_EVERY)
        if changed or remind:
            with atomic(self.session):
                self.audit_alert(problems, resolved=sorted(previous - current))
                repo.set_value(
                    STATE_KEY,
                    {"keys": sorted(current), "at": utcnow().isoformat()},
                    "Last ops alert (ops monitor)",
                )
        return problems

    def audit_alert(self, problems: list[Problem], *, resolved: list[str]) -> None:
        from app.services.audit import AuditLogService

        AuditLogService(self.session).record(
            AuditAction.OPS_ALERT,
            OPS_ACTOR,
            status="FAILED" if problems else "SUCCESS",
            details={"problems": [asdict(p) for p in problems], "resolved": resolved},
        )
