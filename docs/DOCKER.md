# Docker production images (PHASE 11)

Two compose files:

| File | Purpose |
|---|---|
| `docker-compose.yml` | Local development: source bind mounts, hot reload, dev servers, ports on 127.0.0.1 |
| `docker-compose.prod.yml` | Production: immutable images, least privilege, internal network, only the panel exposed |

TLS, a domain and the reverse proxy in front of the panel are PHASE 12.

## 1. Images

| Image | Dockerfile | Base | Contents | Size |
|---|---|---|---|---|
| `muxriddin-backend:prod` | `docker/backend.prod.Dockerfile` | `python:3.12-slim` pinned by digest | `/opt/venv` from `backend/requirements.lock`, `app/`, `alembic/` | ~420 MB |
| `muxriddin-frontend:prod` | `docker/frontend.prod.Dockerfile` | `node:22-alpine` pinned by digest | Next.js `standalone` server + static files | ~350 MB |

One backend image serves the API, the Celery worker, beat, the Telegram bot and the
migrate job; only the command differs.

**Reproducible builds.** `backend/requirements.lock` pins all 66 runtime packages with
SHA-256 hashes. pip installs it with `--require-hashes`, so a tampered package fails the
build. The frontend uses `npm ci` with `package-lock.json`.

**Hardening built into the images:**

* Non-root user `app` (uid/gid 10001). Application code is root-owned, so the app cannot
  modify itself.
* Multi-stage builds: no compiler, no tests, no pip cache and no `.env` in the final image
  (`.dockerignore` excludes `.env*`, `data/`, `.venv`, `node_modules`, `.git`).
* **No package managers at runtime:**
  - backend: pip and `ensurepip` are removed from both the venv and the system Python;
  - frontend: npm, npx, corepack and yarn are removed.
* The backend refuses to start unless the production configuration is valid. It checks
  the JWT secret, the Fernet key, PostgreSQL, CORS, Redis-backed rate limiting, HTTPS
  redirect and media URLs, and that no mock providers are configured.
* `uvicorn --workers $WEB_CONCURRENCY --no-proxy-headers --no-server-header`. The app
  resolves client IPs itself from `TRUSTED_PROXIES`.
* Image `HEALTHCHECK`s:
  - backend: `/health` (database and Redis);
  - frontend: `/login`.

**Test stage.** `--target test` adds pytest and the test suite on top of the exact
production dependencies. Run it in CI:

```bash
docker build -f docker/backend.prod.Dockerfile --target test -t muxriddin-backend:test .
docker run --rm muxriddin-backend:test     # 545 passed, 8 skipped (git/Redis/Postgres-only tests skip)
```

## 2. Production stack (`docker-compose.prod.yml`)

```
            127.0.0.1:3000 (reverse proxy / TLS in PHASE 12)
                      │
                ┌─────▼─────┐   edge network (has internet: Meta, Telegram, Ollama)
                │ frontend  │──────────────┐
                └───────────┘              │
       ┌──────────┬──────────┬─────────────▼┐
       │ backend  │  worker  │ telegram-bot │   (beat and migrate: data network only)
       └────┬─────┴────┬─────┴──────┬───────┘
            │  data network (internal: no internet, not published)
       ┌────▼─────┐ ┌──▼────┐
       │ postgres │ │ redis │
       └──────────┘ └───────┘
```

| Service | Role | Notes |
|---|---|---|
| `postgres` | PostgreSQL 16 | Volume `postgres_data`; superuser = owner role, used only by `migrate` |
| `redis` | Rate limits + Celery broker | Password required, AOF persistence, `noeviction` (never silently drops limiter keys or tasks) |
| `migrate` | One-shot | Runs `alembic upgrade head`, then `python -m app.cli db-app-role` as the owner. Every app service waits for it to succeed |
| `backend` | API | Not published; reachable only from the panel |
| `worker` | Celery worker | Healthcheck: `celery inspect ping` |
| `beat` | Scheduler | Exactly one instance (publishing every minute, reconciliation, token refresh, insights, weekly report) |
| `frontend` | Panel | The only published port: `${PANEL_BIND:-127.0.0.1}:${PANEL_PORT:-3000}` |
| `telegram-bot` | Profile `telegram` | Long polling |
| `ollama` | Profile `ollama` | Optional containerised LLM; pin its tag in production |

**Least-privilege database role.** The app connects as `APP_DB_USER`, which can:

* read and write rows;
* only SELECT and INSERT on `audit_logs`;
* only read `alembic_version`.

It owns nothing, so it cannot alter or create tables, drop the audit trigger, or
TRUNCATE. This closes the PHASE 10 risk "DB superuser can drop the audit trigger" for the
application's credentials. The role is created or updated idempotently on every deploy by
the migrate service.

**Container hardening (all app services):**

* `read_only: true`, with tmpfs for `/tmp` (and `/app/.next/cache` in the panel);
* `cap_drop: [ALL]` and `no-new-privileges`;
* `init: true`;
* memory limits;
* `restart: unless-stopped`;
* json-file log rotation (10 MB × 5).

## 3. Deploy (Linux VPS or Windows 11 with Docker Desktop)

**PowerShell:**

```powershell
Copy-Item .env.production.example .env.production
notepad .env.production                     # replace every change-me (generation commands are in the file)
$env:ENV_FILE = ".env.production"
docker compose -f docker-compose.prod.yml --env-file .env.production build
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
docker compose -f docker-compose.prod.yml --env-file .env.production run --rm backend python -m app.cli create-admin --email you@example.com
.\scripts\prod-smoke.ps1 -EnvFile .env.production -Email you@example.com -Password '...'
```

**bash:**

```bash
cp .env.production.example .env.production && nano .env.production
export ENV_FILE=.env.production
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.production run --rm backend python -m app.cli create-admin --email you@example.com
SMOKE_EMAIL=you@example.com SMOKE_PASSWORD='...' ./scripts/prod-smoke.sh
```

`create-admin` prompts for the password when `--password` is omitted (recommended), so it
does not end up in shell history.

**Updating:** `git pull`, then run `build` and `up -d` again. The migrate service applies
new migrations and refreshes the app role's privileges before the app restarts.

## 4. Smoke test (`scripts/prod-smoke.sh`, `scripts/prod-smoke.ps1`)

30 read-only checks. They never create users or content.

* **Services:**
  - backend, worker, frontend, postgres and redis are healthy;
  - beat is running;
  - migrate exited with 0.
* **Exposure:**
  - backend, Postgres and Redis are not published;
  - the data network has no internet.
* **Panel:**
  - `/login` returns 200;
  - CSP, HSTS and `X-Frame-Options` are set; there is no `X-Powered-By`;
  - `robots.txt` disallows indexing;
  - health through the panel reports the database and Redis as OK.
* **Containers:**
  - backend and frontend run as uid 10001;
  - the root filesystem is read-only;
  - there is no pip;
  - `APP_ENV=production`.
* **Data layer:**
  - the app role is refused `DELETE FROM audit_logs` and `CREATE TABLE`;
  - Redis requires a password.
* **Session** (with credentials):
  - login through the panel works;
  - logout revokes the token server-side (a replayed cookie gets 401);
  - rate-limit keys are stored in Redis.

The script exits non-zero when any check fails. Stopping the worker, for example, is
reported as `FAIL worker healthy`.

## 5. Maintenance

* **Base images** are pinned by digest (`PYTHON_IMAGE`, `NODE_IMAGE` build args). To take
  OS security updates:
  1. Run `docker pull python:3.12-slim node:22-alpine`.
  2. Read the new digests with `docker inspect --format '{{index .RepoDigests 0}}' <image>`.
  3. Update the two Dockerfiles, rebuild, and run the test stage and the smoke test.
* **Python dependencies:** edit `backend/pyproject.toml`, then regenerate the lock inside
  the same base image:

  ```bash
  docker run --rm -v "$PWD/backend:/w" -w /w python:3.12-slim sh -c \
    "pip install -q pip-tools && pip-compile -q --generate-hashes --strip-extras --allow-unsafe -o requirements.lock pyproject.toml"
  ```
* **Vulnerability scan** (Trivy):

  ```bash
  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.58.1 \
    image --scanners vuln --severity HIGH,CRITICAL muxriddin-backend:prod
  ```

  PHASE 11 result:

  | Image | Layer | HIGH/CRITICAL | Fixable |
  |---|---|---|---|
  | frontend | OS | 0 | — |
  | frontend | Node | 0 (npm removed) | — |
  | backend | Python | 0 | — |
  | backend | Debian OS | 44 | 0 (no upstream fix yet) |

  Rebuild on a new base digest when Debian ships fixes.
* **Backups:**
  - database:

    ```bash
    docker compose -f docker-compose.prod.yml --env-file .env.production exec -T postgres \
      pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB" > backup.dump
    ```

  - media: back up the `muxriddin-prod_media_data` volume;
  - keep `.env.production` (especially `TOKEN_ENCRYPTION_KEYS`) safely offline.
    Without it the stored Instagram tokens cannot be decrypted.

  Automated backups are PHASE 12.
