#!/usr/bin/env bash
# Restore a backup made by the backup service (docs/DEPLOYMENT.md §7).
#
#   ./scripts/restore.sh backups/db-20261009T023000Z.dump [backups/media-20261009T023000Z.tar.gz] [--yes]
#
# Stops the app, restores the database (and media if given), re-applies migrations and the
# least-privilege role grants, then starts everything again. The current state is backed up
# first, so a restore can itself be undone.
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env.production}"; export ENV_FILE
C=(docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE")
DB_DUMP="${1:?usage: restore.sh <db-*.dump> [media-*.tar.gz] [--yes]}"
MEDIA_TAR=""; YES=no
for arg in "${@:2}"; do
  case "$arg" in --yes) YES=yes ;; *) MEDIA_TAR="$arg" ;; esac
done
val() { grep -E "^$1=" "$ENV_FILE" | tail -1 | cut -d= -f2- | sed 's/[[:space:]]*#.*$//'; }
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

echo "== stopping the app"
"${C[@]}" stop caddy frontend backend worker beat telegram-bot backup >/dev/null 2>&1 || true

echo "== restoring the database"
"${C[@]}" exec -T postgres pg_restore -U "$OWNER" -d "$DB" --clean --if-exists --no-owner --single-transaction < "$DB_DUMP"

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
echo "Restore finished. Run ./scripts/prod-smoke.sh to verify."
