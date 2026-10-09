# Security (PHASE 10)

Principle: **AI = assistant, USER = final authority.** Nothing reaches Instagram without a
human approval of the exact version, and every decision is recorded in an audit log that
the database itself keeps append-only.

## 1. Threat model (what we defend against)

| Threat | Main controls |
|---|---|
| AI publishes, approves or schedules by itself | Agents never hold `PUBLISH_TO_INSTAGRAM`, `APPROVE_CONTENT` or `CREATE_SCHEDULE` (hard deny). The approve, publish and schedule endpoints require a human session (`actor=human`) with the OWNER or ADMIN role. Only the backend `publish_service` can move content to PUBLISHING, and it first re-checks the approval hash. |
| Edited content published under an old approval | Approval is bound to (content, version, SHA-256 hash), and the hash is re-verified just before publishing |
| Duplicate posts | Per-version idempotency key, exclusive schedule claim, container reuse, lost-response reconciliation (`docs/PUBLISHING.md`) |
| Password guessing / credential stuffing | 30 login attempts / 5 min per IP; 10 failures / 15 min per (e-mail, IP) lock that pair (even the right password is refused); Argon2 hashing; identical answers for unknown e-mails; every success, failure and block audited |
| Stolen session token | httpOnly + SameSite=Strict cookie (never readable by JS); 30-minute expiry; **server-side revocation**: logout puts the token's `jti` on a denylist; "log out everywhere" and password change invalidate every earlier token (millisecond cut-off) |
| CSRF | Same-origin check (`Origin` / `Sec-Fetch-Site`) on every state-changing panel request; SameSite=Strict |
| XSS / clickjacking | React escaping; CSP (`default-src 'self'`, `object-src 'none'`, `frame-ancestors 'none'`); `X-Frame-Options: DENY`; the API sends `default-src 'none'` |
| Token / secret leakage | OAuth tokens Fernet-encrypted at rest; secrets never sent to the browser; a log filter masks `access_token`/`client_secret` in every process; audit details are redacted; a repo secret-scan test |
| Abuse / cost blow-up (AI, Meta quota) | Per-user limits on AI generation, publishing, uploads, insights sync, reports, OAuth and Telegram link codes; per-IP limits on Meta callbacks and the whole API |
| Malicious upload | Type checked from the file's bytes (JPEG/MP4/MOV only), size limits, random 192-bit names, served with `nosniff` |
| Oversized request bodies | Declared body size above 1 MB (JSON) or the media limit (uploads) is refused with 413 before routing |
| Fake Meta callbacks | `signed_request` HMAC-SHA256 with the app secret, compared in constant time |
| OAuth login CSRF / account takeover | One-time, user-bound, hashed `state` that expires after 10 minutes |
| Telegram impersonation | Allowlist plus account linking by one-time code (5 wrong codes / 15 min per Telegram id); one-time, user-bound callback tokens |
| Tampering with history | `audit_logs` UPDATE and DELETE are rejected by a database trigger (PostgreSQL and SQLite) |
| Host-header attacks | `ALLOWED_HOSTS` (TrustedHost) in production |
| Spoofed client IP | `X-Forwarded-For` is honoured only from `TRUSTED_PROXIES`, and the right-most untrusted hop is used. The panel forwards it only with `TRUST_PROXY_HEADERS=true` |
| Known-vulnerable dependencies | `pip-audit` and `npm audit` are part of the release checklist (below) |

## 2. Rate limits (`app/core/ratelimit.py`)

| Name | Limit | Key |
|---|---|---|
| login-ip | 30 / 5 min | client IP |
| login-fail | 10 failures / 15 min | e-mail + IP (reset on success) |
| api-ip | 600 / min | client IP (all `/api/v1`, not `/health`) |
| ai | 60 / hour | user |
| publish | 30 / hour | user |
| upload | 60 / hour | user |
| analytics-sync | 6 / hour | user |
| report | 10 / hour | user |
| oauth-start | 10 / 10 min | user |
| meta-callback | 60 / min | IP |
| telegram-code | 10 / hour | user |
| telegram-link | 5 wrong codes / 15 min | Telegram id |

* Responses: `429 rate_limited` with a `Retry-After` header and an Uzbek message.
* Storage: Redis (shared by every process). If Redis is down, the limiter falls back to
  per-process memory for 30 s: it never fails open.
* Production refuses to start with rate limiting disabled or memory-only.
* Keys are SHA-256 hashed, so no e-mail or IP is stored in Redis.

## 3. Sessions

| Action | Effect |
|---|---|
| Login | JWT with `jti` and a millisecond `iat_ms`, 30 min, stored in an httpOnly cookie by the Next.js server |
| Logout | `POST /api/auth/logout` → backend `/auth/logout` puts the `jti` on the denylist (until expiry) → cookie cleared. A copied cookie stops working |
| Log out everywhere | Settings → *Barcha qurilmalardan chiqish* (`/auth/logout-all`): every token issued before now is rejected |
| Password change | Settings form (`/auth/change-password`). Rules: at least 12 characters, not containing the e-mail name, not trivial, different from the old one. Afterwards every session is signed out |
| Deactivated user | Their tokens are refused on the next request |

## 4. Headers

* **Panel** (`next.config.ts`, production builds):
  - CSP: `default-src 'self'`, scripts and styles `'self' 'unsafe-inline'` (Next.js inline
    bootstrap), images and video from `https:`;
  - HSTS;
  - `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy: no-referrer`;
  - `Permissions-Policy`, `Cross-Origin-Opener-Policy`.
* **API** (`app/main.py`):
  - CSP `default-src 'none'`, `Cache-Control: no-store`, CORP `same-origin`
    (`cross-origin` for `/media/` so Meta can fetch files);
  - HSTS in production;
  - the request ID is echoed back only if it matches `[A-Za-z0-9._-]{1,64}`.

## 5. Accepted risks (documented, reviewed in PHASE 10)

| Item | Why accepted | Revisit |
|---|---|---|
| CSP allows `'unsafe-inline'` scripts | Next.js App Router injects inline bootstrap scripts. Nonce-based CSP forces dynamic rendering of every page. All other sources are locked to `'self'` | When moving to nonce-based CSP |
| `braces` / `micromatch` advisories (via `eslint-config-next`) | Dev-only lint tooling with trusted inputs; `braces` has no patched release. Production dependency tree: `npm audit --omit=dev` = 0 | When a fix is released |
| Next.js' bundled PostCSS | Pinned to the patched 8.5.29 via `overrides` in `package.json` (no Next 16 major upgrade needed) | On the next Next.js upgrade |
| Public `/media/<name>` | Meta's servers must download media without a session. Names are random 192-bit, files are inert and type-checked | — |
| JWT in a cookie, not a server session store | Revocation is covered by the `jti` denylist and the per-user cut-off | — |
| A DB superuser can drop the audit trigger | **Closed for the app (PHASE 11):** the production stack runs the app as a least-privilege role that owns nothing (it cannot drop the trigger, alter tables or UPDATE/DELETE `audit_logs`). Only the owner credentials, used by the one-shot migrate service, can | — |

## 6. Operations

* **Rotate the token encryption key:**
  1. Put the new key first in `TOKEN_ENCRYPTION_KEYS` and keep the old key after it.
  2. Restart, then run `python -m app.cli rotate-token-keys`.
  3. Remove the old key and restart again.
* **Rotate `JWT_SECRET_KEY`:** every session ends immediately. Use it if the secret may
  have leaked.
* **Rotate Meta / Telegram secrets:** do it in their dashboards, update `.env`, restart.
  Reconnect Instagram if the app secret changed.
* **Suspected account compromise:**
  1. Settings → change the password (this signs out everywhere).
  2. Review the audit logs page for `AUTH_*`, `CONTENT_APPROVED` and
     `CONTENT_PUBLISH_*` events.
* **Release checklist:**
  - `pip-audit` (backend venv) → no known vulnerabilities;
  - `npm audit --omit=dev` (frontend) → 0;
  - the full test suites;
  - `pytest tests/test_repo_hygiene.py` (secret scan, `.gitignore`).

## 7. Tests

* `tests/test_security_hardening.py` (21 tests):
  - limiter (memory and real Redis, outage fallback);
  - lockout, `Retry-After`, audit without passwords, user enumeration, spoofed XFF, the
    trusted-proxy algorithm;
  - logout and logout-all revocation, password change, deactivation;
  - endpoint and global limits, headers/HSTS, request-ID sanitising, body-size limit,
    trusted hosts;
  - audit append-only, key rotation.
* `tests/test_repo_hygiene.py`: `.env` ignored, no source folder hidden by `.gitignore`,
  no secrets in tracked files.
* E2E `e2e/auth.spec.ts`: a replayed cookie after logout gets 401; the panel sends its
  security headers.
* Earlier phases: approval security, OAuth state/HMAC, publish gate, token redaction,
  upload validation.
