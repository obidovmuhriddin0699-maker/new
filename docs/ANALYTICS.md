# Analytics and AI Analyst (PHASE 9)

```
Instagram (Meta insights) → sync → analytics_snapshots / content_performance
                                  → weekly facts → AI Analyst (phrasing only) → report
                                  → recommendations → AI Strategist (next content strategy)
```

**Rule:** every number shown comes from the Meta API, or is a documented ratio of two
Meta numbers. A metric Meta did not return is stored as *unavailable* and shown as "—".
It is never estimated, interpolated or filled in by AI.

## 1. Sources (checked October 2026)

| Topic | Source |
|---|---|
| Insights endpoints and permissions (`instagram_business_manage_insights`, graph.instagram.com) | https://developers.facebook.com/docs/instagram-platform/insights/ |
| `impressions`, `plays` and `video_views` retired in 2025, replaced by `views` | Meta changelog v22.0, as summarised by [Supermetrics](https://docs.supermetrics.com/docs/instagram-insights-updates) and [Emplifi](https://docs.emplifi.io/platform/latest/home/instagram-insights-metrics-deprecation-april-2025) |
| Per-type metric support; one incompatible metric fails the whole request (#100) | [Airbyte issue #14524](https://github.com/airbytehq/airbyte/issues/14524), [social-api.ai guide](https://social-api.ai/blog/instagram-graph-api-media-insights-shares-metric) |
| Account metrics with `metric_type=total_value`; without `since`/`until` only 24 h | [PostZen guide](https://www.postzen.dev/blog/instagram-insights-explained) |

`developers.facebook.com` was not reachable from the build environment, so these facts come
from secondary sources that quote Meta. The code is defensive where they may be wrong:

* metric lists are per media type;
* an incompatible-metric error triggers one-by-one requests;
* whatever is still refused is recorded as unavailable.

## 2. What is collected

| Scope | Endpoint | Metrics requested |
|---|---|---|
| Media (FEED, REELS) | `GET /{media-id}/insights` | reach, views, likes, comments, shares, saved, total_interactions |
| Media (STORY) | same | reach, views, shares, total_interactions |
| Media fields | `GET /{media-id}?fields=…` | media_product_type, permalink, like_count, comments_count (used only where insights lack likes/comments) |
| Account | `GET /{ig-user-id}/insights?period=day&metric_type=total_value&since&until` | reach, views, accounts_engaged, total_interactions |
| Profile | `GET /me?fields=followers_count,media_count` | followers_count (stored with the 1-day window) |

**Account windows.** Each window ends at the start of the current UTC day, so it covers
complete days only:

* `day` — 1 day;
* `week` — 7 days;
* `days_28` — 28 days.

Each window is stored once per window end, so repeated syncs do not duplicate rows.
`reach` is unique accounts, so it is **not** additive: the 7-day reach is requested from
Meta, never summed from daily values.

**Media.** Content published by this system within `ANALYTICS_MEDIA_DAYS` (default 30).
Every sync appends a lifetime snapshot (growth history) and updates `content_performance`
with the latest values.

**Engagement rate** = `total_interactions / reach`, calculated only when Meta returned
both values. This is *our* ratio, not an Instagram metric, and the panel says so.

## 3. Sync

* Celery beat `analytics.sync` runs every 6 hours. It can also be run from the panel
  (*Statistikani yangilash*, `POST /analytics/sync`) or with `python -m app.cli sync-insights`.
* Sync is read-only towards Instagram and works with `META_DRY_RUN=true`.
* Sync is skipped, with a clear reason, when there is no live token or the account lacks
  `instagram_business_manage_insights`.
* Audit records: `ANALYTICS_SYNCED` (counts and unavailable metrics) and
  `ANALYTICS_SYNC_FAILED` (`SKIPPED` / `FAILED`).
* Tokens are never logged; the httpx redaction filter covers every process.

## 4. Weekly AI Analyst report

* Celery beat `analytics.weekly_report` runs Monday 03:10 UTC (08:10 Tashkent) for the
  previous Monday–Sunday. It can also be created from the panel (*Hisobot yaratish*) or
  with `python -m app.cli weekly-report`.
* **Facts** (`AnalyticsReportService.build_facts`) are built only from stored data:
  - the account's 7-day window and the previous week's window;
  - followers at the start and end of the week;
  - content published that week with its metrics and engagement %;
  - the best content;
  - per-format averages;
  - `data_gaps`, which lists what is missing.
* **Rule-based text** is always produced from the facts.
* **AI phrasing** (`app/agents/analyst.py`) uses the default AI provider (Ollama
  `qwen2.5:3b` by default) and gets only the facts. A per-report schema rejects:
  - any number in the summary or highlights that is not in the facts;
  - in recommendations, any number other than small counts 1–10 that is not in the facts;
  - any `content_id` that is not in the facts.

  The structured-output repair loop asks the model to fix its answer. If it still fails,
  or the provider is down, the rule-based text is kept and `ai_rejected_reason` records why.
* If there are no data, the report status is `NO_DATA`, it says so, and the AI is not called.
* Audit: `ANALYTICS_REPORT_CREATED`. Telegram approvers receive the report.
* The analyst agent only has `READ_ANALYTICS`. Reports never change, approve, schedule or
  publish content.

## 5. Next content strategy

`AIContentService._performance_summary` gives the AI Strategist:

* the top stored content by engagement;
* the definition of engagement;
* the latest READY report's summary and recommendations.

Without data the Strategist is told that no performance data exists, as before.

## 6. API

| Method | Path (`/api/v1`) | Notes |
|---|---|---|
| GET | `/analytics/overview` | latest 1/7/28-day windows, followers, per-content metrics and unavailable lists, last sync status |
| GET | `/analytics/history?days=30` | daily (1-day window) values |
| POST | `/analytics/sync` | OWNER/ADMIN; returns a per-account result |
| GET | `/analytics/reports`, `/analytics/reports/{id}` | reports with facts |
| POST | `/analytics/reports` | OWNER/ADMIN; `{week_start?: Monday}`; 202 when `AI_JOBS_MODE=celery` |

## 7. Tests

* `tests/test_analytics.py` (20 tests) uses a fake insights server that mimics per-type
  support and the #100 failure. It covers:
  - the sync rules (only returned values, idempotent windows, one-by-one fallback, old
    media, missing scope, Meta errors, no token in logs);
  - the number guard, and AI accepted / rejected / unavailable;
  - NO_DATA, permissions, the Strategist feed, the API and Telegram.
* E2E `e2e/analytics.spec.ts` checks, against `tests/fake_meta.py`:
  - a real value is shown;
  - the metric Meta did not return is shown as "—";
  - the engagement % appears only when both values exist;
  - a report is created.
