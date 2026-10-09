#!/bin/sh
# Backup service (runs in the postgres:16-alpine image, on the internal data network).
#
#   backup.sh daemon   every day at BACKUP_TIME (UTC, HH:MM; default 02:30)
#   backup.sh once     one backup now (used by scripts/deploy.sh before migrations)
#
# Writes to /backups (a host directory — copy it off the server!):
#   db-<UTC timestamp>.dump      pg_dump custom format (restore: scripts/restore.sh)
#   media-<UTC timestamp>.tar.gz uploaded post media
#   *.sha256                     checksums
# Keeps BACKUP_RETENTION_DAYS (default 14). Records the result in system_settings
# ("ops.last_backup") so the ops monitor can alert when backups stop, and optionally pings
# BACKUP_HEARTBEAT_URL (e.g. healthchecks.io) on success.
set -eu
# Dumps hold password hashes and (encrypted) OAuth tokens: owner-only files.
umask 077

: "${PGHOST:=postgres}" "${PGUSER:?}" "${PGPASSWORD:?}" "${PGDATABASE:?}"
export PGHOST PGUSER PGPASSWORD PGDATABASE
OUT=/backups
chmod 700 "$OUT" 2>/dev/null || true
RETENTION="${BACKUP_RETENTION_DAYS:-14}"
AT="${BACKUP_TIME:-02:30}"

log() { echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"logger\":\"backup\",\"message\":\"$1\"}"; }

record() {  # $1 = JSON object (no single quotes inside)
  psql -q -v ON_ERROR_STOP=1 -c "INSERT INTO system_settings (key, value, description)
    VALUES ('ops.last_backup', '{\"value\": $1}', 'Last backup run (backup service)')
    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now()" >/dev/null
}

run_backup() {
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  db="$OUT/db-$stamp.dump"
  media="$OUT/media-$stamp.tar.gz"
  log "backup started ($stamp)"
  if ! pg_dump -Fc -f "$db.partial" "$PGDATABASE"; then
    rm -f "$db.partial"
    record "{\"ok\": false, \"at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"error\": \"pg_dump failed\"}" || true
    log "pg_dump FAILED"
    return 1
  fi
  mv "$db.partial" "$db"
  tar -czf "$media.partial" -C /media . && mv "$media.partial" "$media"
  (cd "$OUT" && sha256sum "$(basename "$db")" "$(basename "$media")" > "backup-$stamp.sha256")
  find "$OUT" -maxdepth 1 \( -name 'db-*.dump' -o -name 'media-*.tar.gz' -o -name 'backup-*.sha256' \) \
    -mtime "+$RETENTION" -delete
  db_bytes=$(wc -c < "$db" | tr -d ' ')
  media_bytes=$(wc -c < "$media" | tr -d ' ')
  record "{\"ok\": true, \"at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"db_file\": \"$(basename "$db")\", \"db_bytes\": $db_bytes, \"media_bytes\": $media_bytes}"
  if [ -n "${BACKUP_HEARTBEAT_URL:-}" ]; then
    wget -q -T 10 -O /dev/null "$BACKUP_HEARTBEAT_URL" || log "heartbeat ping failed"
  fi
  log "backup finished: $(basename "$db") ($db_bytes bytes), media $media_bytes bytes"
}

seconds_until() {  # next HH:MM UTC
  now=$(date -u +%s)
  target=$(date -u -d "$(date -u +%Y-%m-%d) $1:00" +%s 2>/dev/null || date -u -D '%Y-%m-%d %H:%M:%S' -d "$(date -u +%Y-%m-%d) $1:00" +%s)
  [ "$target" -le "$now" ] && target=$((target + 86400))
  echo $((target - now))
}

case "${1:-daemon}" in
  once) run_backup ;;
  daemon)
    log "backup daemon: daily at $AT UTC, keeping $RETENTION days"
    while true; do
      sleep "$(seconds_until "$AT")"
      run_backup || log "backup run failed; will retry tomorrow"
    done
    ;;
  *) echo "usage: backup.sh [daemon|once]" >&2; exit 2 ;;
esac
