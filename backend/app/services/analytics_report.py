"""Weekly analyst report: facts from stored insights → rule-based text → optional AI phrasing.

* ``build_facts`` only reads ``analytics_snapshots`` / ``content_performance`` (values Meta
  returned) and ``contents``. Missing values stay missing and are listed in ``data_gaps``.
* The rule-based summary is always produced; the AI Analyst may replace its wording, but
  any number not present in the facts makes its answer invalid (``app/agents/analyst.py``)
  and the rule-based text is kept, with the reason recorded.
* Reports never change content, approve, schedule or publish anything.
"""

import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.analyst import AnalyticsAnalyst
from app.agents.permissions import AgentTool
from app.agents.structured import run_sync
from app.core.actors import Actor, AgentActor, HumanActor, SystemActor
from app.core.config import get_settings
from app.core.errors import AppError, NotFoundError, PermissionDeniedError
from app.core.transaction import atomic
from app.models import (
    AnalyticsReport,
    AnalyticsSnapshot,
    Content,
    ContentPerformance,
    InstagramAccount,
)
from app.models.enums import ActorType, AuditAction, ContentStatus
from app.providers.ai.base import AIProviderError
from app.providers.ai.factory import create_ai_provider
from app.repositories import BrandProfileRepository
from app.services.audit import AuditLogService
from app.services.guards import require_human_writer

logger = logging.getLogger(__name__)

ANALYST_ACTOR = SystemActor("analytics_report")
ANALYST_AGENT = AgentActor(name="analytics_analyst", tools=frozenset({AgentTool.READ_ANALYTICS}))
ACCOUNT_METRICS = ("reach", "views", "accounts_engaged", "total_interactions")
METRIC_LABELS = {
    "reach": "qamrov (reach)",
    "views": "ko‘rishlar (views)",
    "accounts_engaged": "faol akkauntlar",
    "total_interactions": "interaksiyalar",
}
ENGAGEMENT_DEFINITION = "total_interactions / reach (only when Meta returned both)"
TYPE_LABELS = {"POST": "Post", "CAROUSEL": "Carousel", "REELS": "Reels", "STORY": "Story"}


def previous_week(today: date) -> tuple[date, date]:
    """Last complete Monday–Sunday week before ``today``."""
    monday = today - timedelta(days=today.weekday())
    return monday - timedelta(days=7), monday - timedelta(days=1)


def _pct(rate: float | None) -> float | None:
    return round(rate * 100, 2) if rate is not None else None


@dataclass(slots=True)
class ReportText:
    summary: str
    highlights: list[dict[str, Any]]
    recommendations: list[str]


class AnalyticsReportService:
    def __init__(self, session: Session, provider_factory=None) -> None:  # type: ignore[no-untyped-def]
        self.session = session
        self.settings = get_settings()
        self.audit = AuditLogService(session)
        self.provider_factory = provider_factory or (lambda: create_ai_provider())

    # ------------------------------------------------------------------ reads
    def latest(self) -> AnalyticsReport | None:
        return self.session.scalars(
            select(AnalyticsReport).order_by(AnalyticsReport.id.desc()).limit(1)
        ).first()

    def list(self, limit: int = 20) -> list[AnalyticsReport]:
        return list(
            self.session.scalars(
                select(AnalyticsReport).order_by(AnalyticsReport.id.desc()).limit(limit)
            ).all()
        )

    def get(self, report_id: int) -> AnalyticsReport:
        report = self.session.get(AnalyticsReport, report_id)
        if report is None:
            raise NotFoundError("Report not found")
        return report

    # ------------------------------------------------------------------ create
    def create_weekly(self, actor: Actor, week_start: date | None = None) -> AnalyticsReport:
        user_id = None
        if isinstance(actor, HumanActor):
            user_id = require_human_writer(self.session, actor).id
        elif not isinstance(actor, SystemActor):
            raise PermissionDeniedError("Only a human or the backend scheduler can create reports")
        if week_start is None:
            start, end = previous_week(datetime.now(UTC).date())
        else:
            if week_start.weekday() != 0:
                raise AppError("week_start must be a Monday", code="invalid_range")
            start, end = week_start, week_start + timedelta(days=6)

        account = self._account()
        facts = self.build_facts(start, end, account)
        text = self.rule_text(facts)
        source, provider, model, rejected = "rules", None, None, None
        status = "READY" if facts["has_data"] else "NO_DATA"
        if facts["has_data"] and self.settings.analytics_report_use_ai:
            brand = BrandProfileRepository(self.session).get_default()
            if brand is None:
                rejected = "Brend profili yo‘q — AI ishlatilmadi"
            else:
                try:
                    output, meta = self._run_ai(brand, facts)
                    text = ReportText(
                        output.summary,
                        [h.model_dump() for h in output.highlights],
                        list(output.recommendations),
                    )
                    source, provider, model = "ai", meta.provider, meta.model
                except AIProviderError as exc:
                    details = "; ".join(getattr(exc, "errors", [])[:3])
                    rejected = f"{exc.category}: {exc.message} {details}".strip()[:1000]
                    logger.info("analyst_ai_rejected", extra={"category": exc.category})

        with atomic(self.session):
            report = AnalyticsReport(
                instagram_account_id=account.id if account else None,
                period_start=start,
                period_end=end,
                status=status,
                facts=facts,
                summary=text.summary,
                highlights=text.highlights,
                recommendations=text.recommendations,
                source=source,
                provider=provider,
                model=model,
                ai_rejected_reason=rejected,
                created_by=ActorType.HUMAN if user_id else ActorType.SYSTEM,
                created_by_user_id=user_id,
            )
            self.session.add(report)
            self.session.flush()
            self.audit.record(
                AuditAction.ANALYTICS_REPORT_CREATED,
                actor,
                details={
                    "report_id": report.id,
                    "period": f"{start.isoformat()}..{end.isoformat()}",
                    "status": status,
                    "source": source,
                    "ai_rejected_reason": rejected,
                },
            )
        return report

    def _run_ai(self, brand, facts):  # type: ignore[no-untyped-def]
        async def go():  # type: ignore[no-untyped-def]
            provider = self.provider_factory()
            try:
                return await AnalyticsAnalyst(provider).weekly_report(
                    brand,
                    language=self.settings.analytics_report_language,
                    facts=_prompt_facts(facts),
                )
            finally:
                await provider.aclose()

        return run_sync(go())

    # ------------------------------------------------------------------ facts
    def build_facts(
        self, start: date, end: date, account: InstagramAccount | None = None
    ) -> dict[str, Any]:
        start_dt = datetime.combine(start, time.min, tzinfo=UTC)
        end_dt = datetime.combine(end + timedelta(days=1), time.min, tzinfo=UTC)
        gaps: list[str] = []

        week = self._account_window(account, "week", end_dt) if account else None
        prev = self._account_window(account, "week", start_dt) if account else None
        account_facts: dict[str, Any] = {}
        if week is None:
            gaps.append("Bu hafta uchun akkaunt statistikasi sinxronlanmagan")
        else:
            account_facts = {k: week.metrics[k] for k in ACCOUNT_METRICS if k in week.metrics}
            if week.unavailable:
                gaps.append(
                    "Meta qaytarmagan akkaunt ko‘rsatkichlari: " + ", ".join(week.unavailable)
                )
        previous = (
            {k: prev.metrics[k] for k in ACCOUNT_METRICS if k in prev.metrics} if prev else {}
        )
        followers_end = self._followers_at(account, end_dt) if account else None
        followers_start = self._followers_at(account, start_dt) if account else None

        published = self.session.scalars(
            select(Content).where(
                Content.status == ContentStatus.PUBLISHED,
                Content.published_at >= start_dt,
                Content.published_at < end_dt,
                Content.deleted_at.is_(None),
            )
        ).all()
        items: list[dict[str, Any]] = []
        for c in published:
            perf = self.session.scalar(
                select(ContentPerformance).where(ContentPerformance.content_id == c.id)
            )
            item: dict[str, Any] = {
                "content_id": c.id,
                "format": c.content_type.value,
                "topic": c.topic,
                "published_at": c.published_at.date().isoformat() if c.published_at else None,
                "metrics": dict(perf.metrics) if perf else {},
                "engagement_rate_percent": _pct(perf.engagement_rate) if perf else None,
            }
            if not perf:
                gaps.append(f"#{c.id} uchun insights hali yo‘q")
            items.append(item)
        items.sort(
            key=lambda i: (
                i["engagement_rate_percent"] is not None,
                i["engagement_rate_percent"] or 0,
                i["metrics"].get("reach") or 0,
            ),
            reverse=True,
        )
        best = items[0] if items and items[0]["engagement_rate_percent"] is not None else None

        by_format: dict[str, dict[str, Any]] = {}
        for i in items:
            row = by_format.setdefault(i["format"], {"published": 0, "rates": []})
            row["published"] += 1
            if i["engagement_rate_percent"] is not None:
                row["rates"].append(i["engagement_rate_percent"])
        formats = {
            fmt: {
                "published": row["published"],
                "avg_engagement_rate_percent": round(sum(row["rates"]) / len(row["rates"]), 2)
                if row["rates"]
                else None,
            }
            for fmt, row in by_format.items()
        }
        return {
            "period_start": start.isoformat(),
            "period_end": end.isoformat(),
            "account": account_facts,
            "previous_week_account": previous,
            "followers": {"start": followers_start, "end": followers_end},
            "published_count": len(published),
            "content": items[:10],
            "best_content_id": best["content_id"] if best else None,
            "formats": formats,
            "data_gaps": gaps,
            "engagement_rate_definition": ENGAGEMENT_DEFINITION,
            "has_data": bool(account_facts or any(i["metrics"] for i in items)),
        }

    def _account(self) -> InstagramAccount | None:
        return self.session.scalars(
            select(InstagramAccount)
            .where(InstagramAccount.deleted_at.is_(None))
            .order_by(InstagramAccount.id)
            .limit(1)
        ).first()

    def _account_window(
        self, account: InstagramAccount, period: str, window_end: datetime
    ) -> AnalyticsSnapshot | None:
        return self.session.scalars(
            select(AnalyticsSnapshot)
            .where(
                AnalyticsSnapshot.instagram_account_id == account.id,
                AnalyticsSnapshot.scope == "account",
                AnalyticsSnapshot.period == period,
                AnalyticsSnapshot.window_end == window_end,
            )
            .order_by(AnalyticsSnapshot.id.desc())
            .limit(1)
        ).first()

    def _followers_at(self, account: InstagramAccount, at: datetime) -> int | None:
        snaps = self.session.scalars(
            select(AnalyticsSnapshot)
            .where(
                AnalyticsSnapshot.instagram_account_id == account.id,
                AnalyticsSnapshot.scope == "account",
                AnalyticsSnapshot.period == "day",
                AnalyticsSnapshot.window_end <= at,
            )
            .order_by(AnalyticsSnapshot.window_end.desc())
            .limit(3)
        ).all()
        for s in snaps:
            value = (s.metrics or {}).get("followers_count")
            if isinstance(value, int):
                return value
        return None

    # ------------------------------------------------------------------ rule-based text
    @staticmethod
    def rule_text(facts: dict[str, Any]) -> ReportText:
        period = f"{facts['period_start']} – {facts['period_end']}"
        if not facts["has_data"]:
            return ReportText(
                f"{period}: statistik ma’lumot yo‘q. "
                + ("; ".join(facts["data_gaps"]) or "Insights hali sinxronlanmagan")
                + ". Tizim ko‘rsatkichlarni taxmin qilmaydi.",
                [],
                [
                    "Instagram akkaunt ulangan va instagram_business_manage_insights ruxsati "
                    "berilganini tekshiring, so‘ng statistikani sinxronlang."
                ],
            )
        lines = [f"{period}: {facts['published_count']} ta kontent nashr qilindi."]
        acc, prev = facts["account"], facts["previous_week_account"]
        for key in ACCOUNT_METRICS:
            if key in acc:
                tail = f" (oldingi hafta: {prev[key]})" if key in prev else ""
                lines.append(f"Akkaunt {METRIC_LABELS[key]}: {acc[key]}{tail}.")
        f = facts["followers"]
        if f["start"] is not None and f["end"] is not None:
            lines.append(f"Obunachilar: {f['start']} → {f['end']}.")
        highlights: list[dict[str, Any]] = []
        best = next(
            (i for i in facts["content"] if i["content_id"] == facts["best_content_id"]), None
        )
        if best:
            m = best["metrics"]
            parts = [f"engagement {best['engagement_rate_percent']}%"]
            parts += [f"{k} {m[k]}" for k in ("reach", "total_interactions", "saved") if k in m]
            reason = (
                f"Haftaning eng yaxshi natijasi: {TYPE_LABELS.get(best['format'], best['format'])} "
                f"«{best['topic'] or '#' + str(best['content_id'])}» — " + ", ".join(parts) + "."
            )
            lines.append(reason)
            highlights.append({"content_id": best["content_id"], "reason": reason})
        if facts["data_gaps"]:
            lines.append("Ma’lumot yo‘q: " + "; ".join(facts["data_gaps"]) + ".")

        recs: list[str] = []
        rated = {
            k: v["avg_engagement_rate_percent"]
            for k, v in facts["formats"].items()
            if v["avg_engagement_rate_percent"] is not None
        }
        if len(rated) >= 2:
            top = max(rated, key=lambda k: rated[k])
            recs.append(
                f"{TYPE_LABELS.get(top, top)} formati bu hafta o‘rtacha engagement bo‘yicha "
                "yaxshiroq natija berdi — keyingi haftada uni ko‘proq rejalashtiring."
            )
        if best:
            recs.append(
                f"«{best['topic'] or best['format']}» mavzusini davom ettiruvchi "
                "kontent tayyorlang."
            )
        if facts["published_count"] == 0:
            recs.append("Bu hafta nashr bo‘lmagan — keyingi hafta rejasini tuzing.")
        if not recs:
            recs.append("Bir necha hafta ma’lumot to‘planguncha turli formatlarni sinab ko‘ring.")
        return ReportText(" ".join(lines), highlights, recs)


def _prompt_facts(facts: dict[str, Any]) -> dict[str, Any]:
    """Compact copy for the prompt (the prompt builder truncates long context)."""
    slim = dict(facts)
    slim["content"] = [
        {k: v for k, v in i.items() if k != "published_at"} for i in facts["content"][:6]
    ]
    return slim
