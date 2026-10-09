# Meta OAuth: Instagram API with Instagram Login (PHASE 7)

The system connects an Instagram **professional** account (Business or Creator) only
through Meta's official OAuth flow. It never asks for, receives or stores an Instagram
login or password. There is no scraping, no browser automation and no private API.

PHASE 7 only **connects** the account and manages its token. Publishing comes in
PHASE 8 and still goes through USER → APPROVE → SYSTEM → META API.

## 1. Sources (checked October 2026)

| Topic | Official source |
|---|---|
| Business Login flow (authorize URL, code exchange, `#_`, `data[]` response) | https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login/business-login |
| Short → long-lived token (`ig_exchange_token`, 60 days) | https://developers.facebook.com/docs/instagram-platform/reference/access_token/ |
| Token refresh (`ig_refresh_token`, ≥ 24 h old, not expired) | https://developers.facebook.com/docs/instagram-platform/reference/refresh_access_token/ |
| `GET /me` fields (`user_id`, `username`, `account_type`, …) | https://developers.facebook.com/documentation/instagram-platform/reference/me.md |
| Getting started, access levels | https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login/get-started |
| Insights permission | https://developers.facebook.com/documentation/instagram-platform/insights |

`developers.facebook.com` was not reachable from the build environment. The facts
above come from search results quoting those pages and two community write-ups
(gist.github.com/PrenSJ2/0213e60e834e66b7e09f7f93999163fc and
gist.github.com/jameschapman2c/65eff9f54a2d350b17a6ce5127b9fe42). **Check them
against the live docs before you go to production.** Every endpoint URL and the Graph
API version can be changed in `.env` without a code change.

## 2. Flow

```
Panel (/instagram)            Backend                         Meta (instagram.com / graph.instagram.com)
 │ "Instagram'ni ulash"        │                               │
 │ POST oauth/start ─────────► │ OWNER/ADMIN human? configured?     │
 │                             │ Fernet key present?           │
 │                             │ state = random 256-bit        │
 │                             │ store sha256(state), user, TTL│
 │ ◄──── authorize_url ─────── │ audit INSTAGRAM_OAUTH_STARTED │
 │ window.location → instagram.com/oauth/authorize?client_id&redirect_uri&response_type=code&scope&state
 │                                   (official consent screen; the user logs in on Instagram, not here)
 │ ◄──────────────── 302 /instagram/callback?code=…&state=…#_ ─┤
 │ POST oauth/callback {state, code} ►                          │
 │                             │ consume state (one-time, same user, not expired; burned even on mismatch)
 │                             │ POST api.instagram.com/oauth/access_token ─► short-lived token + permissions
 │                             │ GET graph.instagram.com/access_token (ig_exchange_token) ─► long-lived, 60 days
 │                             │ GET graph.instagram.com/vXX/me?fields=user_id,username,account_type,…
 │                             │ required scopes granted? (else refused, nothing stored)
 │                             │ link account + store token ENCRYPTED (Fernet), old tokens revoked
 │ ◄──── account + warnings ── │ audit INSTAGRAM_ACCOUNT_LINKED / OAUTH_TOKEN_STORED
```

### Why the callback page has no session check in middleware

The session cookie is `SameSite=Strict`, so the browser does **not** send it on the
cross-site redirect from instagram.com. `middleware.ts` therefore lets
`/instagram/callback` through. The page then calls the backend through the same-origin
proxy, and that request does carry the cookie. If the user is not logged in, they are
sent to `/login?next=…` and the flow continues after login (the state is not consumed by
an unauthenticated request). The code is removed from the address bar
(`history.replaceState`), and `Referrer-Policy: no-referrer` keeps it out of `Referer` headers.

## 3. Security properties

| Threat | Defence |
|---|---|
| Login CSRF / forced account linking | `state` is random, single-use, bound to the user who started, expires after `META_OAUTH_STATE_TTL_MINUTES`; only its SHA-256 is stored |
| Stolen callback URL | The state is burned on first use. A wrong user's attempt also burns it, so the owner must start again |
| Token theft from DB | Tokens are stored only as Fernet ciphertext (`oauth_tokens.token_ciphertext`); key from `TOKEN_ENCRYPTION_KEYS` |
| Token in logs | httpx/httpcore loggers capped at WARNING (they log full URLs incl. `access_token`); Meta error messages truncated; audit details redacted |
| Token/secret in browser | Never returned by any endpoint; `/instagram/status` returns only expiry, scopes and warnings |
| Fake Meta callbacks | `signed_request` verified with HMAC-SHA256 + app secret + `compare_digest`, algorithm checked |
| AI connecting/publishing | `start` and `complete` require a human OWNER/ADMIN session; agents are refused |
| Code burned without storage | `start` refuses if `TOKEN_ENCRYPTION_KEYS` is missing, before the user consents |

## 4. Token lifecycle

* Long-lived token: 60 days (`expires_at` stored).
* Celery beat task `instagram.refresh_tokens` runs every 6 hours and refreshes tokens
  that expire within `META_TOKEN_REFRESH_WINDOW_DAYS` (default 15). Meta only refreshes
  tokens that are at least 24 hours old and not yet expired.
* Manual: panel → Instagram → "Tokenni yangilash", or `python -m app.cli refresh-instagram-tokens`.
* A refreshed token replaces the old one (old row revoked). Audit: `OAUTH_TOKEN_REFRESHED` / `OAUTH_TOKEN_REFRESH_FAILED`.
* An expired token cannot be refreshed. The account shows **"Qayta ulash kerak"** and the user connects again.

## 5. Endpoints

| Method | Path (`/api/v1`) | Who |
|---|---|---|
| GET | `/instagram/status` | logged-in user |
| POST | `/instagram/oauth/start` | human OWNER/ADMIN |
| POST | `/instagram/oauth/callback` | human OWNER/ADMIN (the callback page) |
| POST | `/instagram/accounts/{id}/refresh-token` | human OWNER/ADMIN |
| DELETE | `/instagram/accounts/{id}` | human OWNER/ADMIN (tokens revoked locally, account soft-deleted) |
| POST | `/instagram/meta/deauthorize` | Meta (form `signed_request`) |
| POST | `/instagram/meta/data-deletion` | Meta (form `signed_request`) → `{url, confirmation_code}` |
| GET | `/instagram/meta/data-deletion/{code}` | public status |

Public URLs to enter in the Meta App Dashboard (served by Next.js, forwarded to the backend):

* Deauthorize callback URL: `https://<panel>/api/meta/deauthorize`
* Data deletion request URL: `https://<panel>/api/meta/data-deletion`
* Status URL returned to Meta: `https://<panel>/api/meta/data-deletion-status?code=…`

Deauthorize revokes the account's tokens. Data deletion deletes tokens and analytics
snapshots, scrubs the username and picture, soft-deletes the account and records a
`data_deletion_requests` row (status `completed`). Content and approvals made by your
own team are your data and are kept.

## 6. Error mapping

Meta errors are classified (`app/integrations/meta/errors.py`) into user-friendly Uzbek
messages with stable codes. Meta's raw message is kept, truncated, only in `details`:

| Meta | Code | HTTP |
|---|---|---|
| 190 with an expiry subcode | `meta_token_expired` | 502 |
| other OAuth errors | `meta_oauth` | 502 |
| 4, 17, 32, 613, 8000x | `meta_rate_limit` | 429 |
| 10, 200–299 | `meta_permission_denied` | 403 |
| 1, 2 | `meta_transient` | 502 |
| 100 | `meta_invalid_request` | 502 |
| network/timeout | `meta_network` | 503 |
| not configured | `meta_not_configured` | 503 |

## 7. Testing without Meta

* Unit/API tests (`tests/test_instagram_oauth.py`) mock every Meta call with `respx`.
* E2E (`e2e/instagram.spec.ts`) runs `tests/fake_meta.py` on `127.0.0.1:8200`. It mimics
  the documented shapes (`data[]`, `#_`, `ig_exchange_token`, `ig_refresh_token`,
  `/vXX/me`), and because `127.0.0.1` and `localhost` are different sites, the
  E2E test exercises the real cross-site redirect and the SameSite=Strict cookie behaviour.
* Nothing in tests contacts instagram.com or graph.instagram.com.

## 8. Not supported / known limits

* Meta's pages only clearly document Story publishing for Business accounts. Creator accounts get a warning (on connect and before publishing a Story) but are not blocked: Meta's own answer is shown.
* Personal (non-professional) Instagram accounts cannot use this API. Convert the account to Business/Creator in the Instagram app.
* Facebook Login mode (`META_LOGIN_MODE=facebook`, Page-linked accounts) is not implemented. Instagram Login is the default and only implemented mode.
