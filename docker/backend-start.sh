#!/bin/sh
# Default command of the backend image. One image, several roles (APP_ROLE):
#
#   web       API server (default). RUN_MIGRATIONS=true applies migrations first;
#             BOOTSTRAP_ADMIN_EMAIL + BOOTSTRAP_ADMIN_PASSWORD create the first owner if
#             that user does not exist yet (remove both variables afterwards).
#   worker    Celery worker. CELERY_BEAT=true also runs the scheduler in the same
#             process (only ONE such instance may exist).
#   beat      Celery beat on its own.
#   telegram  Telegram bot (long polling).
#   migrate   apply migrations and exit (e.g. as a platform pre-deploy command).
#
# docker-compose.prod.yml sets explicit commands per service and does not use this
# script for the worker, beat or telegram roles; platforms that run one image with
# different variables per service (Railway, Render...) do.
#
# Platforms that mount volumes owned by root (Railway) need the container started as
# root (RAILWAY_RUN_UID=0): the script then hands the media directory to the app user
# and drops privileges, so the application itself never runs as root.
set -eu

if [ "$(id -u)" = "0" ]; then
  media="${MEDIA_ROOT:-/var/lib/muxriddin/media}"
  mkdir -p "$media"
  chown -R app:app "$media"
  exec setpriv --reuid=app --regid=app --init-groups --inh-caps=-all -- "$0" "$@"
fi

role="${APP_ROLE:-web}"
case "$role" in
  web)
    if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
      python -m app.cli migrate
    fi
    if [ -n "${BOOTSTRAP_ADMIN_EMAIL:-}" ] && [ -n "${BOOTSTRAP_ADMIN_PASSWORD:-}" ]; then
      # Fails harmlessly ("already exists") on every later start.
      python -m app.cli create-admin --email "$BOOTSTRAP_ADMIN_EMAIL" \
        --password "$BOOTSTRAP_ADMIN_PASSWORD" || true
    fi
    exec python -m app.serve
    ;;
  worker)
    set -- celery -A app.workers.celery_app worker -l info --concurrency="${CELERY_CONCURRENCY:-2}"
    if [ "${CELERY_BEAT:-false}" = "true" ]; then
      set -- "$@" -B --schedule /tmp/celerybeat-schedule
    fi
    exec "$@"
    ;;
  beat)
    exec celery -A app.workers.celery_app beat -l info --schedule /tmp/celerybeat-schedule
    ;;
  telegram)
    exec python -m app.integrations.telegram
    ;;
  migrate)
    exec python -m app.cli migrate
    ;;
  *)
    echo "unknown APP_ROLE: $role (web | worker | beat | telegram | migrate)" >&2
    exit 2
    ;;
esac
