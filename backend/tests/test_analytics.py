"""PHASE 9: insights sync, weekly analyst report, analytics API. Meta and AI are fakes."""

import json
import logging
from datetime import UTC, date, datetime, time, timedelta
from urllib.parse import parse_qs

import httpx
import pytest
import respx
from sqlalchemy import select

from app.agents.analyst import allowed_numbers, checked_schema, unknown_numbers
from app.core.config import get_settings
from app.core.errors import PermissionDeniedError
from app.models import AnalyticsReport, AnalyticsSnapshot, AuditLog, ContentPerformance
from app.models.base import utcnow
from app.models.enums import AuditAction, ContentStatus, ContentType
from app.services.analytics_report import AnalyticsReportService, previous_week
from app.services.analytics_sync import AnalyticsSyncService, engagement_rate
from tests.conftest import IG_PUBLISH_ID, PUBLISH_TOKEN, make_publishable, mock_factory

GRAPH = "https://graph.instagram.com/v26.0"


class FakeInsights:
    """Media / account insights with per-type metric support like Meta's (one bad metric
    fails the whole request with #100)."""

    def __init__(self) -> None:
        self.media: dict[str, dict] = {}  # media_id -> {"type": FEED|REELS|STORY, "metrics": {}}
        self.account = {"reach": 900, "views": 2400, "accounts_engaged": 120}
        self.followers = 1500
        self.requests: list[httpx.Request] = []
        self.fail_with: dict | None = None

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        q = {k: v[0] for k, v in parse_qs(request.url.query.decode()).items()}
        assert q.get("access_token") == PUBLISH_TOKEN
        if self.fail_with:
            return httpx.Response(400, json=self.fail_with)
        parts = request.url.path.strip("/").split("/")[1:]
        if parts == ["me"]:
            return httpx.Response(200, json={"followers_count": self.followers, "media_count": 12})
        if parts == [IG_PUBLISH_ID, "insights"]:
            assert q["period"] == "day" and q["metric_type"] == "total_value"
            assert int(q["until"]) > int(q["since"])
            return self._insights(q["metric"].split(","), self.account, total_value=True)
        media_id = parts[0]
        m = self.media[media_id]
        if parts[1:] == ["insights"]:
            return self._insights(
                q["metric"].split(","), m["metrics"], supported=m.get("supported")
            )
        return httpx.Response(
            200,
            json={
                "id": media_id,
                "media_product_type": m["type"],
                "media_type": "IMAGE",
                "permalink": f"https://www.instagram.com/p/{media_id}/",
                "like_count": m.get("like_count"),
                "comments_count": m.get("comments_count"),
            },
        )

    @staticmethod
    def _insights(requested, values, *, total_value=False, supported=None) -> httpx.Response:
        if supported is not None and any(r not in supported for r in requested):
            return httpx.Response(
                400,
                json={"error": {"message": "(#100) Incompatible metric", "code": 100}},
            )
        data = []
        for name in requested:
            if name not in values:
                continue
            entry = {"name": name, "period": "day" if total_value else "lifetime"}
            if total_value:
                entry["total_value"] = {"value": values[name]}
            else:
                entry["values"] = [{"value": values[name]}]
            data.append(entry)
        return httpx.Response(200, json={"data": data})


@pytest.fixture
def insights(monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s, "meta_graph_base_url", "https://graph.instagram.com")
    monkeypatch.setattr(s, "meta_graph_api_version", "v26.0")
    fake = FakeInsights()
    with respx.mock(assert_all_called=False) as router:
        router.route(host="graph.instagram.com").mock(side_effect=fake.handler)
        yield fake


@pytest.fixture
def insights_account(db, ig_account):
    """ig_account plus the insights scope."""
    from app.repositories import OAuthTokenRepository

    token = OAuthTokenRepository(db).get_active_for_account(ig_account.id)
    token.scopes = (
        "instagram_business_basic instagram_business_content_publish "
        "instagram_business_manage_insights"
    )
    db.commit()
    return ig_account


def published(db, human, media_id: str, *, days_ago: int = 2, **kw):
    content = make_publishable(db, human, **kw)
    content.status = ContentStatus.PUBLISHED
    content.ig_media_id = media_id
    content.published_at = utcnow() - timedelta(days=days_ago)
    db.commit()
    return content


# ================================================================== sync
def test_sync_stores_only_returned_values(db, human, insights_account, insights):
    c = published(db, human, "m1")
    insights.media["m1"] = {
        "type": "FEED",
        "metrics": {"reach": 400, "views": 900, "likes": 30, "saved": 12, "total_interactions": 48},
    }
    [result] = AnalyticsSyncService(db).sync_all()
    assert result.status == "ok" and result.media_synced == 1 and result.account_windows == 3

    perf = db.scalar(select(ContentPerformance).where(ContentPerformance.content_id == c.id))
    assert perf.metrics == {
        "reach": 400,
        "views": 900,
        "likes": 30,
        "saved": 12,
        "total_interactions": 48,
    }
    assert perf.engagement_rate == pytest.approx(0.12)
    snap = db.scalars(select(AnalyticsSnapshot).where(AnalyticsSnapshot.scope == "media")).one()
    assert sorted(snap.unavailable) == ["comments", "shares"]  # requested, not returned
    assert "impressions" not in str(insights.requests) and "plays" not in str(insights.requests)

    week = db.scalars(select(AnalyticsSnapshot).where(AnalyticsSnapshot.period == "week")).one()
    assert week.metrics == {"reach": 900, "views": 2400, "accounts_engaged": 120}
    assert week.unavailable == ["total_interactions"]
    assert week.window_end == datetime.combine(utcnow().date(), time.min, tzinfo=UTC)
    assert week.window_end - week.window_start == timedelta(days=7)
    day = db.scalars(select(AnalyticsSnapshot).where(AnalyticsSnapshot.period == "day")).one()
    assert day.metrics["followers_count"] == 1500


def test_sync_is_idempotent_for_account_windows(db, human, insights_account, insights):
    AnalyticsSyncService(db).sync_all()
    AnalyticsSyncService(db).sync_all()
    rows = db.scalars(select(AnalyticsSnapshot).where(AnalyticsSnapshot.scope == "account")).all()
    assert len(rows) == 3  # day, week, days_28 — once per window end


def test_incompatible_metric_falls_back_to_one_by_one(db, human, insights_account, insights):
    published(db, human, "s1", content_type=ContentType.STORY)
    insights.media["s1"] = {
        "type": "STORY",
        "metrics": {"reach": 50, "views": 80},
        "supported": {"reach", "views"},  # shares / total_interactions refused for this media
    }
    AnalyticsSyncService(db).sync_all()
    snap = db.scalars(select(AnalyticsSnapshot).where(AnalyticsSnapshot.scope == "media")).one()
    assert snap.metrics == {"reach": 50, "views": 80}
    assert sorted(snap.unavailable) == ["shares", "total_interactions"]


def test_media_fields_fill_likes_when_insights_lack_them(db, human, insights_account, insights):
    c = published(db, human, "m2")
    insights.media["m2"] = {
        "type": "FEED",
        "metrics": {"reach": 10},
        "like_count": 4,
        "comments_count": 1,
    }
    AnalyticsSyncService(db).sync_all()
    perf = db.scalar(select(ContentPerformance).where(ContentPerformance.content_id == c.id))
    assert perf.metrics == {"reach": 10, "likes": 4, "comments": 1}
    assert perf.engagement_rate is None  # no total_interactions from Meta → no ratio


def test_old_media_is_not_synced(db, human, insights_account, insights):
    published(db, human, "old", days_ago=60)
    [result] = AnalyticsSyncService(db).sync_all()
    assert result.media_synced == 0


def test_missing_insights_scope_skips(db, human, ig_account, insights):
    [result] = AnalyticsSyncService(db).sync_all()
    assert result.status == "skipped" and "manage_insights" in result.reason
    assert insights.requests == []
    assert (
        db.scalars(
            select(AuditLog).where(AuditLog.action == AuditAction.ANALYTICS_SYNC_FAILED.value)
        )
        .one()
        .status
        == "SKIPPED"
    )


def test_meta_error_is_recorded(db, human, insights_account, insights):
    insights.fail_with = {
        "error": {"message": "Invalid token", "type": "OAuthException", "code": 190}
    }
    [result] = AnalyticsSyncService(db).sync_all()
    assert result.status == "failed" and "qayta ulang" in result.reason


def test_token_never_logged(db, human, insights_account, insights, caplog):
    caplog.set_level(logging.DEBUG)
    published(db, human, "m3")
    insights.media["m3"] = {"type": "FEED", "metrics": {"reach": 1}}
    AnalyticsSyncService(db).sync_all()
    assert PUBLISH_TOKEN not in caplog.text


def test_engagement_rate_needs_both_values():
    assert engagement_rate({"reach": 200, "total_interactions": 10}) == 0.05
    assert engagement_rate({"reach": 0, "total_interactions": 10}) is None
    assert engagement_rate({"reach": 200}) is None


# ================================================================== analyst guard
def test_number_guard():
    facts = {
        "account": {"reach": 900},
        "content": [{"content_id": 7, "engagement_rate_percent": 5.25}],
    }
    allowed = allowed_numbers(facts)
    assert unknown_numbers("Reach 900, engagement 5.25%", allowed) == []
    assert unknown_numbers("engagement 5,25% bo‘ldi", allowed) == []
    assert unknown_numbers("Reach 950 ga oshdi", allowed) == ["950"]
    schema = checked_schema(facts)
    ok = schema.model_validate(
        {
            "summary": "Reach 900.",
            "highlights": [{"content_id": 7, "reason": "5.25% engagement"}],
            "recommendations": ["Haftasiga 3 ta Reels"],
        }
    )
    assert ok.highlights[0].content_id == 7
    with pytest.raises(ValueError):
        schema.model_validate({"summary": "Reach 2x ga, 47% o‘sdi", "recommendations": ["x"]})
    with pytest.raises(ValueError):
        schema.model_validate(
            {
                "summary": "ok",
                "highlights": [{"content_id": 99, "reason": "x"}],
                "recommendations": ["x"],
            }
        )


# ================================================================== reports
def _seed_week(db, human, ig_account, start: date):
    end_dt = datetime.combine(start + timedelta(days=7), time.min, tzinfo=UTC)
    db.add_all(
        [
            AnalyticsSnapshot(
                instagram_account_id=ig_account.id,
                scope="account",
                period="week",
                captured_at=utcnow(),
                window_start=end_dt - timedelta(days=7),
                window_end=end_dt,
                metrics={"reach": 900, "views": 2400},
                unavailable=["total_interactions"],
            ),
            AnalyticsSnapshot(
                instagram_account_id=ig_account.id,
                scope="account",
                period="week",
                captured_at=utcnow(),
                window_start=end_dt - timedelta(days=14),
                window_end=end_dt - timedelta(days=7),
                metrics={"reach": 700},
            ),
        ]
    )
    a = published(db, human, "w1", topic="Yorug‘lik")
    b = published(db, human, "w2", topic="Ranglar")
    for c, rate, reach in ((a, 0.08, 500), (b, 0.03, 300)):
        c.published_at = datetime.combine(start + timedelta(days=2), time(10), tzinfo=UTC)
        db.add(ContentPerformance(content_id=c.id, metrics={"reach": reach}, engagement_rate=rate))
    db.commit()
    return a, b


def test_rule_based_report_uses_facts_only(db, human, ig_account, monkeypatch):
    monkeypatch.setattr(get_settings(), "analytics_report_use_ai", False)
    start, _ = previous_week(utcnow().date())
    a, _b = _seed_week(db, human, ig_account, start)
    report = AnalyticsReportService(db).create_weekly(human)
    assert report.status == "READY" and report.source == "rules"
    assert (
        "2 ta kontent" in report.summary
        and "qamrov (reach): 900 (oldingi hafta: 700)" in report.summary
    )
    assert report.facts["best_content_id"] == a.id
    assert report.highlights[0]["content_id"] == a.id and "8.0%" in report.summary
    assert "total_interactions" in report.summary  # unavailable metric is named, not invented
    assert unknown_numbers(report.summary, allowed_numbers(report.facts)) == []


def test_ai_report_accepted_when_numbers_match(db, human, ig_account, brand, monkeypatch):
    start, _ = previous_week(utcnow().date())
    a, _ = _seed_week(db, human, ig_account, start)
    answer = json.dumps(
        {
            "summary": "Akkaunt qamrovi 900 ga yetdi.",
            "highlights": [{"content_id": a.id, "reason": "Eng yuqori engagement: 8.0%"}],
            "recommendations": ["Yorug‘lik mavzusida 2 ta karusel tayyorlang."],
        },
        ensure_ascii=False,
    )
    factory = mock_factory(answer)
    report = AnalyticsReportService(db, provider_factory=factory).create_weekly(human)
    assert report.source == "ai" and report.summary == "Akkaunt qamrovi 900 ga yetdi."
    assert report.provider == "mock"
    prompt = factory.created[0].calls[0]["prompt"]
    assert "TASK: weekly_analytics_report" in prompt and '"reach": 900' in prompt


def test_ai_report_with_invented_numbers_falls_back(db, human, ig_account, brand):
    start, _ = previous_week(utcnow().date())
    _seed_week(db, human, ig_account, start)
    bad = json.dumps({"summary": "Qamrov 35% ga o‘sdi!", "recommendations": ["x"]})
    report = AnalyticsReportService(db, provider_factory=mock_factory(bad, bad, bad)).create_weekly(
        human
    )
    assert report.source == "rules"
    assert "35" in report.ai_rejected_reason and "35%" not in report.summary


def test_ai_unavailable_falls_back(db, human, ig_account, brand):
    from app.providers.ai.base import AIProviderUnavailableError

    start, _ = previous_week(utcnow().date())
    _seed_week(db, human, ig_account, start)
    factory = mock_factory(AIProviderUnavailableError("Ollama ishlamayapti"))
    report = AnalyticsReportService(db, provider_factory=factory).create_weekly(human)
    assert report.source == "rules" and "provider_unavailable" in report.ai_rejected_reason


def test_no_data_report_is_honest_and_skips_ai(db, human, brand):
    factory = mock_factory()
    report = AnalyticsReportService(db, provider_factory=factory).create_weekly(human)
    assert report.status == "NO_DATA" and "taxmin qilmaydi" in report.summary
    assert factory.created == []


def test_report_permissions(db, human, viewer, agent):
    with pytest.raises(PermissionDeniedError):
        AnalyticsReportService(db).create_weekly(viewer)
    with pytest.raises(PermissionDeniedError):
        AnalyticsReportService(db).create_weekly(agent)


def test_previous_week_is_monday_to_sunday():
    assert previous_week(date(2026, 10, 9)) == (date(2026, 9, 28), date(2026, 10, 4))
    assert previous_week(date(2026, 10, 5)) == (date(2026, 9, 28), date(2026, 10, 4))


def test_strategist_receives_report_recommendations(db, human, ig_account, brand, monkeypatch):
    from app.services.ai_content import AIContentService

    monkeypatch.setattr(get_settings(), "analytics_report_use_ai", False)
    start, _ = previous_week(utcnow().date())
    _seed_week(db, human, ig_account, start)
    AnalyticsReportService(db).create_weekly(human)
    perf = AIContentService(db)._performance_summary()
    assert perf["latest_weekly_report"]["recommendations"]
    assert perf["top_content"][0]["engagement_rate"] == 0.08


# ================================================================== API + Telegram
@pytest.fixture
def api(client, auth_headers):
    client.headers.update(auth_headers)
    return client


def test_api_overview_sync_and_reports(api, db, human, insights_account, insights, monkeypatch):
    monkeypatch.setattr(get_settings(), "analytics_report_use_ai", False)
    published(db, human, "m9")
    insights.media["m9"] = {"type": "REELS", "metrics": {"reach": 70, "total_interactions": 7}}
    empty = api.get("/api/v1/analytics/overview").json()
    assert empty["windows"] == [] and empty["last_sync"] is None

    r = api.post("/api/v1/analytics/sync")
    assert r.status_code == 200 and r.json()[0]["status"] == "ok"
    o = api.get("/api/v1/analytics/overview").json()
    assert {w["period"] for w in o["windows"]} == {"day", "week", "days_28"}
    assert o["followers_count"] == 1500 and o["last_sync"]["status"] == "SUCCESS"
    item = o["content"][0]
    assert (
        item["metrics"] == {"reach": 70, "total_interactions": 7} and item["engagement_rate"] == 0.1
    )
    assert "likes" in item["unavailable"]
    assert len(api.get("/api/v1/analytics/history?days=7").json()) == 1

    rep = api.post("/api/v1/analytics/reports", json={})
    assert rep.status_code == 201, rep.text
    assert api.get("/api/v1/analytics/reports").json()[0]["id"] == rep.json()["id"]
    bad = api.post("/api/v1/analytics/reports", json={"week_start": "2026-10-07"})
    assert bad.status_code == 400  # not a Monday


def test_telegram_gets_report(db, human, linked_owner, ig_account, monkeypatch):
    from app.services.telegram import TelegramService

    monkeypatch.setattr(get_settings(), "analytics_report_use_ai", False)
    TelegramService(db).init_notify_cursor()
    start, _ = previous_week(utcnow().date())
    _seed_week(db, human, ig_account, start)
    AnalyticsReportService(db).create_weekly(human)
    messages, _ = TelegramService(db).collect_review_notifications()
    assert any("Haftalik hisobot" in m.text for _, m in messages)
    assert "Haftalik hisobot" in TelegramService(db).analytics_text()
    assert db.scalars(select(AnalyticsReport)).one().status == "READY"
