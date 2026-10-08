# new

## Backend foundation

The initial backend is a FastAPI application with a SQLite connection managed by
SQLAlchemy.

From the repository root, install the dependencies and start the API:

```powershell
python -m pip install -r requirements-dev.txt
python -m uvicorn backend.app.main:app --reload
```

The API is available at `http://127.0.0.1:8000/`; `http://127.0.0.1:8000/health`
returns the liveness status and `/ready` checks the database connection. The
SQLite database URL defaults to `sqlite:///./app.db` for local development and
can be overridden with `DATABASE_URL`.

Run the backend tests from the repository root with:

```powershell
python -m pytest backend/tests
```

Run the web panel in another terminal:

```powershell
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. The panel defaults to the backend at
`http://127.0.0.1:8000`; override it with Vite's `VITE_API_BASE_URL` environment
variable before starting the dev server. Cookie-authenticated API requests use
credentials and automatically send the readable CSRF cookie in
`X-CSRF-Token`. The backend allows the local Vite origins by default; set
`CORS_ORIGINS` to a comma-separated explicit origin list for other frontends.

## SaaS core

Register with `POST /auth/register`, log in with `POST /auth/login`, get the
current user and memberships from `GET /auth/me`, and end the current session
with `POST /auth/logout`. Registration creates a user; create one or more
workspaces with `POST /workspaces`. Owners can add existing registered users
and assign roles using `POST /workspaces/{workspace_id}/members`; owners and
admins can change eligible membership roles using
`PATCH /workspaces/{workspace_id}/members/{user_id}`. Only owners can assign
the admin role or change an admin's role; owners cannot be changed through
this endpoint. Use
`POST /workspaces/{workspace_id}/select` to select a workspace for the current
session.

Authenticated state-changing requests must send the `csrf_token` cookie value
in the `X-CSRF-Token` header. The `session` cookie is HttpOnly; both cookies use
SameSite=Lax. For local HTTP development cookies are not Secure by default; set
`COOKIE_SECURE=true` when serving over HTTPS. Sessions expire after seven days.

## Billing

Each new workspace starts with a 30-day trial. `GET
/workspaces/{workspace_id}/billing` returns the trial/subscription state;
`GET /workspaces/{workspace_id}/billing/plans` returns the configured plan
catalog. Prices and quotas are not hard-coded: configure `BILLING_PLANS_JSON`
as a JSON array of objects with `id`, `name`, `price_minor`, `currency` (3
uppercase letters), and optional `limits` (metric-to-nonnegative-integer map).
An empty or unset catalog is valid, but no plan checkout is available until a
catalog is configured.

Only workspace owners/admins can call
`POST /workspaces/{workspace_id}/billing/checkout`; it uses the test-only
adapter (default `PAYMENT_MODE=test`) and simulates activation without contacting
a payment provider or charging money. All workspace members can record
tenant-scoped usage with `POST /workspaces/{workspace_id}/billing/usage/{metric}`;
configured plan limits are enforced in rolling fixed 30-day buckets. Expired
trials cannot record metered usage. Existing workspaces created before Billing
receive their trial when first accessed through a billing endpoint. The
current schema follows the existing `create_all` approach, not a migration
framework.

## Local AI

`POST /workspaces/{workspace_id}/ai/chat` sends a prompt to the locally running
Ollama `/api/chat` endpoint and records one `ai_requests` unit against that
workspace. Requests require workspace membership and the CSRF header. The
workspace's trial/subscription and configured `ai_requests` plan quota are
enforced before the model is called. Configure `OLLAMA_BASE_URL` (defaults to
`http://127.0.0.1:11434`) and `OLLAMA_MODEL` (defaults to `qwen2.5-coder:3b`).
The model is selected by the server, not by callers; prompt and system input
lengths are bounded. If Ollama is unavailable, the API returns HTTP 503 and
rolls back the usage reservation. No remote AI provider is configured.

## Orchestrator v1

Create a workspace-scoped workflow with
`POST /workspaces/{workspace_id}/workflows` using `{"title":"...","task":"..."}`.
List and inspect workflows at the same path and
`GET /workspaces/{workspace_id}/workflows/{workflow_id}`. Manually start or
resume a workflow with
`POST /workspaces/{workspace_id}/workflows/{workflow_id}/run`. Creation and run
require the usual `X-CSRF-Token`; every endpoint verifies workspace membership.

Each workflow stores its Planner, Developer, and QA phase state/output and runs
them in that order using the configured local Ollama model. A failed phase can
be manually retried once (two attempts maximum per phase); completed phases
remain saved and are not re-run. Each successful model call consumes one
`ai_requests` unit. Failed calls do not consume quota. The Developer phase only
produces proposed text and QA only reviews it: this version does not run
commands, execute generated code, or write project files. Task and prior phase
text are treated as untrusted input; outputs are bounded and persisted in the
workspace database.

## Web panel

The React/Vite panel includes email/password login and registration, first
workspace onboarding, workspace switching/creation, trial and configured plan
limits/usage, local AI chat, and workflow creation/run/results. It displays
backend validation, quota, and service errors. Billing plan checkout is
explicitly labeled as a test simulation; no real payment is made. The browser
cannot choose the model or bypass backend authorization.

## Telegram bot (local polling MVP)

Create a bot with Telegram's official `@BotFather`, then save its token in a
local `.env` file at the repository root (this file is git-ignored):

```dotenv
TELEGRAM_BOT_TOKEN=<store privately in local .env>
TELEGRAM_BOT_USERNAME=Agentbot01bot
```

Replace the token placeholder locally in a text editor; do not type the token
into a shell command.

Start polling from the repository root in the same terminal:

```powershell
python -m backend.telegram_bot
```

The bot loads `.env` on startup without overriding variables already set in
the process environment. Never paste the token into chat, source code, issue
comments, or a committed file. Keep the bot process private and run only one
polling instance. Polling needs outbound HTTPS access to Telegram (no webhook
or public hosting is required). The bot uses the same `DATABASE_URL`,
`OLLAMA_BASE_URL`, `OLLAMA_MODEL`, and `BILLING_PLANS_JSON` environment
configuration as the backend.

In the web panel, open **Telegram bot**, generate the one-time code, and send
`/link CODE` to the bot in a private chat. Codes expire after 10 minutes, are
stored hashed, and can be used once. The linked user chooses a workspace with
`/workspaces` and `/use WORKSPACE_ID`; membership is rechecked for every AI
message, and AI requests consume that workspace's `ai_requests` quota. Unlink
from the web panel to revoke access immediately. Telegram usernames are never
used as identity proof; groups, oversized messages, unlinked accounts, and
workspace access outside the linked user's memberships are rejected. AI
failures do not consume quota. This MVP has no conversation history, webhook,
real payment integration, command execution, or file writing.
Telegram AI replies are instructed to use concise, grammatically correct Uzbek
in Latin script. If the model repeats a long user message instead of answering,
the bot asks the user to clarify rather than echoing the text.

## Railway production preparation

The repository includes a Dockerfile and Railway health-check configuration.
The container serves both the built React panel and FastAPI API from one HTTPS
origin. `railway.json` uses `/ready`, which returns success only when the
database connection is available; `/health` is a liveness-only check.

Configure a Railway PostgreSQL service and provide its `DATABASE_URL` reference
to the app service. Legacy `postgres://` and `postgresql://` URLs are normalized
to the psycopg 3 SQLAlchemy driver. Do not use SQLite on Railway: its container
filesystem is ephemeral unless explicitly mounted to persistent storage, and
the app is configured to require PostgreSQL in production.

Production startup validates `APP_ENV`/Railway environment, secure cookies,
PostgreSQL, CORS, and an external Ollama URL, then runs `alembic upgrade head`
before starting Uvicorn on Railway's `PORT`. Local development continues to
create missing tables with SQLAlchemy `create_all`; production skips that
development shortcut and uses versioned Alembic migrations. Back up the
database before applying future migrations. The initial migration is intended
for a new database; an existing database created with `create_all` must be
backed up and baselined deliberately before using this deployment path.

Required production settings:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | Railway PostgreSQL connection URL; use a Railway variable reference, not a copied credential. |
| `OLLAMA_BASE_URL` | Reachable HTTP(S) endpoint for an Ollama service hosted separately; localhost is rejected in production. |
| `OLLAMA_MODEL` | Model installed on that Ollama service (default remains `qwen2.5-coder:3b`). |
| `COOKIE_SECURE` | Set to `true`; secure session and CSRF cookies are enabled by default in production. |
| `CORS_ORIGINS` | Optional comma-separated HTTPS origins only if the frontend is hosted separately. Same-origin Docker deployment needs no CORS allowlist. |
| `BILLING_PLANS_JSON` | Optional plan catalogue; prices/quotas must be explicitly configured. |

Cookies use `SameSite=Lax`; if hosting the panel separately, use a frontend
origin on the same site as the API. Arbitrary cross-site frontend origins are
not supported by the current cookie configuration.

Do not expose Ollama without appropriate network controls and authentication.
Use Railway private networking when the model service is hosted there, or a
secured HTTPS endpoint; never point the production app at `127.0.0.1`.
`PAYMENT_MODE=test` remains a simulation and is not a real billing provider.
Telegram polling is not started by the API container; if enabled later, deploy
it as a separate single-instance worker using the same PostgreSQL and Ollama
services and inject its rotated `TELEGRAM_BOT_TOKEN` through Railway secrets.

For local development, create `.env` from `.env.example` and fill secrets only
in the local ignored file. Never put real credentials in README, source,
screenshots, or Git history. A Telegram token that has appeared in any history
must be revoked through BotFather and replaced.