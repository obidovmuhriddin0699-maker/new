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
returns the service health status. The SQLite database URL defaults to
`sqlite:///./app.db` and can be overridden with the `DATABASE_URL` environment
variable.

Run the backend tests from the repository root with:

```powershell
python -m pytest backend/tests
```

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