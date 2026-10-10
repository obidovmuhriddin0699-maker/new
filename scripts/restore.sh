#!/usr/bin/env bash
# Restore a backup made by the backup service (docs/DEPLOYMENT.md §7).
#
#   ./scripts/restore.sh backups/db-20261009T023000Z.dump [backups/media-20261009T023000Z.tar.gz] [--yes]
#
# Stops the app, restores the database (and media if given), re-applies migrations and the
# least-privilege role grants, then starts everything again. The current state is backed up
# first, so a restore can itself be undone.
#
# The database restore is one transaction: the public schema is dropped and recreated (so
# tables added by newer migrations do not survive) and the dump is loaded; any error rolls
# all of it back. If anything fails once the app is stopped, the app is started again.
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env.production}"; export ENV_FILE
C=(docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE")
DB_DUMP="${1:?usage: restore.sh <db-*.dump> [media-*.tar.gz] [--yes]}"
MEDIA_TAR=""; YES=no
for arg in "${@:2}"; do
  case "$arg" in --yes) YES=yes ;; *) MEDIA_TAR="$arg" ;; esac
done
val() { { grep -E "^$1=" "$ENV_FILE" || true; } | tail -1 | cut -d= -f2- | sed 's/[[:space:]]*#.*$//'; }
# Optional services (COMPOSE_PROFILES=telegram) are stopped and started with the rest.
COMPOSE_PROFILES="$(val COMPOSE_PROFILES)"; export COMPOSE_PROFILES
OWNER="$(val POSTGRES_USER)"; OWNER="${OWNER:-muxriddin_owner}"
DB="$(val POSTGRES_DB)"; DB="${DB:-muxriddin}"

[ -f "$DB_DUMP" ] || { echo "not found: $DB_DUMP"; exit 1; }
[ -z "$MEDIA_TAR" ] || [ -f "$MEDIA_TAR" ] || { echo "not found: $MEDIA_TAR"; exit 1; }

# Verify checksums when the backup's .sha256 file is next to it.
stamp="$(basename "$DB_DUMP" | sed -E 's/^db-(.*)\.dump$/\1/')"
sums="$(dirname "$DB_DUMP")/backup-$stamp.sha256"
if [ -f "$sums" ]; then
  (cd "$(dirname "$DB_DUMP")" && grep -E "$(basename "$DB_DUMP")${MEDIA_TAR:+|$(basename "$MEDIA_TAR")}" "backup-$stamp.sha256" | sha256sum -c -) \
    || { echo "checksum mismatch — refusing to restore"; exit 1; }
fi

if [ "$YES" != yes ]; then
  echo "This REPLACES the database${MEDIA_TAR:+ and media} with: $DB_DUMP ${MEDIA_TAR}"
  read -r -p "Type 'restore' to continue: " answer
  [ "$answer" = restore ] || { echo "aborted"; exit 1; }
fi

echo "== safety backup of the current state"
"${C[@]}" run --rm --no-deps backup sh /backup.sh once

stopped=no
on_exit() {
  status=$?
  if [ "$status" -ne 0 ] && [ "$stopped" = yes ]; then
    echo "!! restore FAILED (exit $status, see the error above) — starting the app again" >&2
    "${C[@]}" up -d || echo "!! could not start the app: run '${C[*]} up -d' by hand" >&2
  fi
}
trap on_exit EXIT

echo "== stopping the app"
stopped=yes
"${C[@]}" stop caddy frontend backend worker beat telegram-bot backup >/dev/null 2>&1 || true

echo "== restoring the database"
# The dump is converted to SQL first (a broken dump fails here, before anything is touched),
# then schema reset + restore run in a single transaction as the owner. --no-owner: objects
# belong to the owner; the app role's grants are re-applied by the migrate step below.
# shellcheck disable=SC2016 # expanded by the container's shell
"${C[@]}" exec -T postgres sh -c '
  set -eu
  sql="/tmp/restore-$$.sql"
  trap "rm -f \"$sql\"" EXIT
  pg_restore --no-owner -f "$sql"
  PGOPTIONS="-c client_min_messages=warning" psql -q -U "$1" -d "$2" -v ON_ERROR_STOP=1 --single-transaction \
    -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" -f "$sql" >/dev/null
' restore "$OWNER" "$DB" < "$DB_DUMP"

if [ -n "$MEDIA_TAR" ]; then
  echo "== restoring media"
  volume="$("${C[@]}" config --format json | python3 -c 'import json,sys; print(json.load(sys.stdin)["volumes"]["media_data"]["name"])' 2>/dev/null || echo muxriddin-prod_media_data)"
  docker run --rm -v "$volume:/media" -v "$(cd "$(dirname "$MEDIA_TAR")" && pwd)/$(basename "$MEDIA_TAR"):/restore.tar.gz:ro" \
    postgres:16-alpine sh -c 'find /media -mindepth 1 -delete && tar -xzf /restore.tar.gz -C /media'
fi

echo "== migrations + role grants"
"${C[@]}" run --rm migrate

echo "== starting"
"${C[@]}" up -d
stopped=no
echo "Restore finished. Run ./scripts/prod-smoke.sh to verify."
