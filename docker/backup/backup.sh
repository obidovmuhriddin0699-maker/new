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

utc_now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# Every step is checked explicitly: run_backup is called as `run_backup || ...`, where
# `set -e` is ignored inside the function, so a failed command would otherwise go unnoticed.
# A failure removes this run's files, records {"ok": false}, skips the heartbeat, returns 1.
fail() {  # $1 = step name
  # shellcheck disable=SC2086 # $created: this run's own files (paths without spaces)
  rm -f "$db.partial" "$media.partial" "$sums.partial" $created
  record "{\"ok\": false, \"at\": \"$(utc_now)\", \"error\": \"$1 failed\"}" || log "could not record the failure"
  log "backup FAILED: $1 failed"
  return 1
}

run_backup() {
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  db="$OUT/db-$stamp.dump"
  media="$OUT/media-$stamp.tar.gz"
  sums="$OUT/backup-$stamp.sha256"
  created=""
  log "backup started ($stamp)"
  if [ -e "$db" ] || [ -e "$media" ]; then
    log "backup $stamp already exists"
    return 1
  fi
  pg_dump -Fc -f "$db.partial" "$PGDATABASE" || { fail pg_dump; return 1; }
  mv "$db.partial" "$db" || { fail "move db dump"; return 1; }
  created="$db"
  tar -czf "$media.partial" -C /media . || { fail "media tar"; return 1; }
  mv "$media.partial" "$media" || { fail "move media archive"; return 1; }
  created="$created $media"
  (cd "$OUT" && sha256sum "$(basename "$db")" "$(basename "$media")" > "$(basename "$sums").partial") \
    || { fail sha256sum; return 1; }
  mv "$sums.partial" "$sums" || { fail "move checksums"; return 1; }
  created="$created $sums"
  db_bytes=$(wc -c < "$db" | tr -d ' ') || { fail "db size"; return 1; }
  media_bytes=$(wc -c < "$media" | tr -d ' ') || { fail "media size"; return 1; }
  case "$db_bytes$media_bytes" in
    ''|*[!0-9]*) fail "size check"; return 1 ;;
  esac
  [ "$db_bytes" -gt 0 ] && [ "$media_bytes" -gt 0 ] || { fail "size check"; return 1; }
  if ! record "{\"ok\": true, \"at\": \"$(utc_now)\", \"db_file\": \"$(basename "$db")\", \"db_bytes\": $db_bytes, \"media_bytes\": $media_bytes}"; then
    # The files are fine, but the ops monitor cannot see this run: no heartbeat either.
    log "backup written but could not be recorded in the database"
    return 1
  fi
  # Retention only after a successful run, so failures never eat into the old backups.
  find "$OUT" -maxdepth 1 \( -name 'db-*.dump' -o -name 'media-*.tar.gz' -o -name 'backup-*.sha256' \) \
    -mtime "+$RETENTION" -delete || log "retention cleanup failed"
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
