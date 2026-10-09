# syntax=docker/dockerfile:1
# Production image for the FastAPI backend, Celery worker/beat and Telegram bot.
#
#   docker build -f docker/backend.prod.Dockerfile -t muxriddin-backend:prod .
#   docker build -f docker/backend.prod.Dockerfile --target test -t muxriddin-backend:test .
#
# * Dependencies come from backend/requirements.lock (exact versions + SHA-256 hashes).
# * The base image is pinned by digest; bump it deliberately (docs/DOCKER.md §5).
# * Final image: no compiler, no pip cache, no tests, non-root user, read-only friendly.

ARG PYTHON_IMAGE=python:3.12-slim@sha256:05cda9777409a9c3ffddd94a4c476b79f0769a0b4857f0c7ed9226b6800b0d6f

# ------------------------------------------------------------------ dependencies
FROM ${PYTHON_IMAGE} AS deps
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
COPY backend/requirements.lock /tmp/requirements.lock
RUN pip install --require-hashes --no-deps -r /tmp/requirements.lock

# ------------------------------------------------------------------ tests (CI only)
FROM deps AS test
WORKDIR /app
RUN pip install "pytest>=8.3" "pytest-asyncio>=0.24" "respx>=0.22" "ruff>=0.8"
COPY backend/ ./
CMD ["python", "-m", "pytest", "-q"]

# ------------------------------------------------------------------ production
FROM ${PYTHON_IMAGE} AS production
LABEL org.opencontainers.image.title="muxriddin-backend" \
      org.opencontainers.image.description="MUXRIDDIN AI INSTAGRAM MANAGER backend (API, worker, beat, bot)"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/venv/bin:$PATH \
    APP_ENV=production \
    MEDIA_ROOT=/var/lib/muxriddin/media \
    WEB_CONCURRENCY=2

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --home-dir /app --shell /usr/sbin/nologin app \
    && mkdir -p /var/lib/muxriddin/media \
    && chown app:app /var/lib/muxriddin/media

COPY --from=deps /opt/venv /opt/venv
# No package installer at runtime: a compromised process cannot pip-install tools.
# (both the venv's and the base image's system pip, plus ensurepip which could reinstall it).
RUN rm -rf /opt/venv/bin/pip* /opt/venv/lib/python3.12/site-packages/pip \
           /opt/venv/lib/python3.12/site-packages/pip-*.dist-info \
           /usr/local/bin/pip* /usr/local/lib/python3.12/site-packages/pip \
           /usr/local/lib/python3.12/site-packages/pip-*.dist-info \
           /usr/local/lib/python3.12/ensurepip
WORKDIR /app
# Application code only (tests, caches and local data are excluded by .dockerignore and
# by copying explicit paths). Root-owned: the app user can read but not modify its code.
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./alembic.ini

USER app
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
    CMD ["python", "-c", "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"]

# --no-proxy-headers: the app resolves the client IP itself from TRUSTED_PROXIES
# (app/core/ratelimit.py); uvicorn must not rewrite the peer address first.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${WEB_CONCURRENCY} --no-proxy-headers --no-server-header"]
