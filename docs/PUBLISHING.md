# Instagram Publishing (PHASE 8)

```
USER → APPROVE (v N) → USER "publish" / schedule → SYSTEM publish_service → META API → INSTAGRAM
```

AI can create and edit drafts. It can never approve, schedule or publish. The only code
that calls Meta's `media_publish` is `app/services/publish.py`, and it runs as the
`publish_service` system actor.

## 1. Sources (checked October 2026)

| Topic | Source |
|---|---|
| Container → status → `media_publish` flow, carousel (≤ 10 children), Reels, Stories, public URL requirement | https://developers.facebook.com/documentation/instagram-platform/content-publishing |
| `status_code` values (`IN_PROGRESS`, `FINISHED`, `PUBLISHED`, `ERROR`, `EXPIRED` = not published within 24 h) | same page, "Troubleshooting" |
| `content_publishing_limit` (`quota_usage`, `config.quota_total`, `quota_duration`) | same page |
| Story `media_type=STORIES`; `media_product_type` distinguishes stories | https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media |

`developers.facebook.com` was not reachable from the build environment. The facts were
taken from search results quoting those pages. Where the sources disagreed, the code
avoids hard-coding the answer:

* **Daily quota:** Meta's pages say 100 in one place and 50 in another. The live
  `config.quota_total` is used. `META_PUBLISH_LIMIT_FALLBACK` (default 50) applies only
  if Meta omits it.
* **Stories on Creator accounts:** not clearly documented. They are not blocked: the
  panel shows a warning, and Meta's own error is shown if it refuses.
* **Image format:** JPEG is the format Meta documents reliably. The preflight blocks
  non-JPEG images, and uploads accept JPEG only.

## 2. What is published

The **approved version's snapshot** (`content_versions` row), not the working copy. The
approval is bound to that version's SHA-256 hash, which is re-verified just before
publishing.

| Type | Containers |
|---|---|
| POST | `image_url`, `caption` |
| CAROUSEL | one `is_carousel_item=true` container per media item (`media_type=VIDEO` for videos), then `media_type=CAROUSEL` + `children` + `caption` |
| REELS | `media_type=REELS`, `video_url`, `caption`, `share_to_feed=true` |
| STORY | `media_type=STORIES` + `image_url` or `video_url` (no caption) |

**Caption** = hook (unless the caption already opens with it) + caption + CTA +
hashtags, separated by blank lines (`app/core/caption.py`). The 2,200-character quality
limit is computed on exactly this text.

`GET /api/v1/contents/{id}/publish-preview` shows these parameters without calling
Meta. Tokens are never included.

## 3. Flow and safety checks

1. **Request.** An OWNER/ADMIN either clicks *Instagram’ga nashr qilish* (`POST
   /contents/{id}/publish` with `expected_version`) or schedules a time. The service
   requires a valid human approval of that exact version, else 409 `approval_required`.
   Audit: `CONTENT_PUBLISH_REQUESTED` with `approval_id`, `approved_by_user_id` and
   `requested_by_user_id`.
2. **Schedule row.** One per (content, version) via `idempotency_key =
   publish:content:{id}:v{version}`. A retry reuses it.
3. **Claim.** `PENDING → PROCESSING` with a conditional UPDATE. Only one worker wins;
   duplicate Celery deliveries are no-ops.
4. **Preflight.** The same checklist the panel shows (`ReviewService.readiness`):
   status, approval, quality, format, media count and type, HTTPS URLs, JPEG, account,
   live token, the `instagram_business_content_publish` scope, and the publisher. Any
   blocker fails here, **before anything is sent to Meta**.
5. **Quota.** `content_publishing_limit` is checked. If exhausted, the schedule is
   deferred by 1 hour (`CONTENT_PUBLISH_DEFERRED`) and nothing is created.
6. **`start_publishing`.** `→ PUBLISHING`. This step re-verifies the approval.
7. **Containers.** The container id is **committed before publishing**
   (`INSTAGRAM_CONTAINER_CREATED`).
8. **Wait.** `status_code` is polled until `FINISHED` (`META_CONTAINER_POLL_INTERVAL_SECONDS`,
   max `META_CONTAINER_MAX_WAIT_SECONDS`). Video processing can take minutes.
9. **`media_publish`** → media id → permalink → `PUBLISHED`.
   Audit: `CONTENT_PUBLISH_SUCCEEDED`, with media id, permalink, approver and requester.
   Telegram: "✅ nashr qilindi".

## 4. Never a duplicate post

| Situation | What happens |
|---|---|
| Same version requested again | 409 `already_published` / `publish_in_progress` |
| Two workers / duplicate task | only the claim winner works; the other returns `skipped` |
| Retry after a failure | the stored container is reused if still `FINISHED`. Meta publishes a container at most once |
| `media_publish` sent, **no answer** (timeout, dropped connection, 5xx) | `outcome_unknown=true`; content stays `PUBLISHING`; the user cannot re-publish. The container `status_code` decides: `PUBLISHED` → success (the media id is found via recent media with the same caption); `EXPIRED`/`ERROR` → definitely not published → `FAILED`; `FINISHED` → after `PUBLISH_RECONCILE_AFTER_MINUTES` the **same** container is published |
| Connection refused before sending | nothing was sent; automatic retry |
| Worker crash | the `publish.reconcile` beat task (every 5 min) resumes stale `PROCESSING` schedules |

## 5. Errors and retries

Meta errors are classified (`app/integrations/meta/errors.py`) and shown in Uzbek, with
Meta's text appended:

* **Retried automatically** (up to `PUBLISH_MAX_ATTEMPTS`): network, transient (Meta
  codes 1, 2), rate limit (4, 17, 32, 613, subcode 2207042 = daily publishing limit).
* **Final; a human fixes and retries:**
  - expired token (190): reconnect the account;
  - missing permission (10, 200–299);
  - media rejected (subcodes 2207xxx, container `ERROR`). In this case the container
    is discarded and the next try creates a new one.

`FAILED → PUBLISHING` needs the approval to still be valid. Editing the content creates
a new version and requires a new approval.

## 6. Dry run

`META_DRY_RUN=true` (the default):

* `POST /publish` returns `status=dry_run` with the full preview. Audit:
  `CONTENT_PUBLISH_DRY_RUN`. No Meta call is made and nothing changes.
* The scheduler leaves due schedules untouched and logs that it skipped them.
* The readiness check shows a `dry_run` warning.

## 7. Media hosting

Meta downloads media from a **public HTTPS URL** at publish time. Two options:

1. **Upload** in the panel (content page → Media). The backend checks the magic bytes:
   JPEG images up to `MEDIA_MAX_IMAGE_MB`, MP4/MOV videos up to `MEDIA_MAX_VIDEO_MB`.
   The file is stored under `MEDIA_ROOT` with a random 192-bit name and served without
   a session at `{MEDIA_PUBLIC_BASE_URL or PANEL_PUBLIC_URL}/media/<name>`
   (Next.js → backend). Locally, that base must be an HTTPS tunnel (README §11).
2. **Attach an HTTPS URL** you already host (CDN / S3). Only `https://` is accepted.

Each media change creates a new content version, so the content must be approved again.
In production with `META_DRY_RUN=false`, startup is refused unless the media base URL is
HTTPS.

## 8. Not supported / never faked

The `/instagram/capabilities` endpoint and the panel list them: music, story stickers
(link, poll, question), filters/effects, Instagram drafts, and replacing media after
publishing. Each is shown as *Not supported by current Meta API*.

## 9. Operations

| Task | How |
|---|---|
| Due schedules | Celery beat `publish.process_due` every 60 s (or `python -m app.cli publish-due`) |
| Stuck / unknown outcomes | beat `publish.reconcile` every 5 min (or `python -m app.cli reconcile-publishing`) |
| Quota | Instagram page → *Nashr limitini tekshirish* (`GET /instagram/accounts/{id}/publishing-limit`) |

## 10. Tests

* `tests/test_publishing.py` (32 tests) uses a stateful fake Meta (`tests/meta_publish_fake.py`)
  behind `respx`. It covers duplicates, lost responses, expired containers, quota,
  retries, the approval gate, permissions and token redaction.
* `tests/test_media_upload.py` covers byte validation, size limits, public serving,
  path traversal and the log-redaction filter.
* E2E `e2e/publishing.spec.ts` covers upload → approve → preview → publish → permalink
  against `tests/fake_meta.py`. Nothing in any test contacts Instagram.
