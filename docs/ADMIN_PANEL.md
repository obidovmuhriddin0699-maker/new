# Admin panel (PHASE 4)

Next.js 15 (App Router) + TypeScript + Tailwind CSS 4. Mobile-first: works in
Android/iPhone browsers (drawer navigation, no horizontal scrolling).

## 1. Architecture: backend-for-frontend (BFF)

```
Browser ──(same origin, httpOnly cookie)──► Next.js  /api/auth/login|logout
                                                    /api/backend/<path>  ──(Bearer JWT, server-side)──► FastAPI /api/v1/<path>
```

* The JWT is stored only in an **httpOnly, SameSite=Strict** cookie (`mx_session`),
  `Secure` on HTTPS (`SESSION_COOKIE_SECURE=auto|true|false`). Browser JavaScript
  cannot read it; it never appears in localStorage.
* `/api/backend/*` attaches the token server-side and forwards to `BACKEND_URL`.
  * State-changing requests must be **same-origin** (Origin / Sec-Fetch-Site check) → CSRF protection.
  * Path segments are whitelisted (`[A-Za-z0-9_.-]`, no `..`); body ≤ 1 MB.
  * `auth/login` is blocked on the proxy so the token can never be returned to the browser.
  * A 401 from the backend clears the cookie (expired session → login page).
* `middleware.ts` redirects requests without a session cookie to `/login?next=…`
  (local paths only — no open redirect). Real authorization always happens in the backend.
* Only the frontend port needs to be reachable from a phone; the backend can stay on localhost.

## 2. Pages

| Route | Purpose |
|---|---|
| `/login` | Panel login (never asks for the Instagram password) |
| `/overview` | Total / pending approval / scheduled / published / failed / drafts, reach & engagement (real analytics only, otherwise "Ma’lumot yo‘q"), upcoming, AI + system status |
| `/content` | Content queue with status tabs, type filter, pagination |
| `/content/new` | Manual draft |
| `/content/[id]` | **Approval UI**: preview (media / caption / hashtags / slides / scenes / frames), info (platform, scheduled time, version), actions, quality check, history |
| `/ai` | AI Studio: post, carousel, reels, story, ideas, content plan, strategy, hashtags (polls jobs in Celery mode) |
| `/calendar` | Day / week / month views; item panel with Preview, Edit, Regenerate, Approve, Schedule, Delete |
| `/media` | Asset library (metadata; `not_configured` notice) |
| `/instagram` | Connection status — connect button arrives in PHASE 7 |
| `/analytics` | Real metrics only — PHASE 9 |
| `/telegram` | Planned bot commands — PHASE 5 |
| `/ai-settings` | Provider/model status, job mode, media providers, agent permissions (read-only; settings live in `.env`) |
| `/brand` | Edit the brand profile used for generation and quality checks |
| `/logs` | Audit log with filters (OWNER/ADMIN only) |
| `/settings` | Account, role, logout, system health |

## 3. Approval UI rules

Actions shown per status (the backend enforces the same rules):

| Status | Actions |
|---|---|
| DRAFT, EDIT_REQUESTED | Edit, Submit for review, Regenerate, Delete |
| READY_FOR_REVIEW | **Approve**, Request edit, Reject, Edit, Regenerate, Delete |
| APPROVED | Schedule, Request edit, Edit (warns: new version → re-approval), Delete |
| SCHEDULED | Cancel schedule, Request edit, Edit, Delete |
| FAILED | Edit, Regenerate, Delete |
| REJECTED | Delete |
| GENERATING, PUBLISHING, PUBLISHED | none |

* Every decision sends `expected_version` — approving content that changed after
  it was opened is refused with a clear message.
* The approve confirmation states the exact version and that **it does not publish**.
* "Approve & publish" is shown disabled ("PHASE 8"): there is no publish endpoint.
* Scheduling works (human-only, approved version only) but nothing is published until PHASE 8.

## 4. New backend endpoints

`GET /dashboard/summary`, `GET /calendar?start&end` (≤ 62 days),
`GET /audit-logs` (OWNER/ADMIN), `GET|POST /brand-profiles`, `GET|PATCH /brand-profiles/{id}`,
`GET /assets`, `POST|DELETE /contents/{id}/schedule`, `DELETE /contents/{id}`,
`POST /ai/regenerate`. `Content` gained `planned_date` (calendar planning, not versioned)
and `scheduled_at` in responses.

## 5. Tests

* Backend: `tests/test_panel_api.py` (+ updated OpenAPI tests).
* Frontend: `npm run lint`, `npm run typecheck`, `npm run build`.
* E2E (`frontend/e2e`, Playwright, desktop + Pixel 7): login/logout, httpOnly cookie,
  open-redirect and CSRF protection, approve/edit/reject/stale-version flows, AI Studio
  generation, regenerate, calendar, every page renders without errors or horizontal scroll.
  The E2E stack is isolated (backend :8100 with a fresh SQLite DB + mock AI, frontend :3100).
