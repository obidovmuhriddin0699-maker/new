#!/usr/bin/env bash
# Deploy or update the production stack on this server (docs/DEPLOYMENT.md §5).
#
#   ./scripts/deploy.sh            build the current checkout, back up, migrate, start, smoke-test
#   SKIP_BUILD=1 ./scripts/deploy.sh   restart with the already-built images
#
# Every release is tagged with the git commit (muxriddin-*:<sha>) and recorded in
# .deploy/releases, so scripts/rollback.sh can switch back to the previous images.
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env.production}"; export ENV_FILE
C=(docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE")
val() { grep -E "^$1=" "$ENV_FILE" | tail -1 | cut -d= -f2- | sed 's/[[:space:]]*#.*$//'; }

echo "== preflight"
[ -f "$ENV_FILE" ] || { echo "missing $ENV_FILE (cp .env.production.example $ENV_FILE)"; exit 1; }
if grep -qE '^[A-Z_]+=.*change-me' "$ENV_FILE"; then
  echo "$ENV_FILE still contains change-me values:"; grep -nE '^[A-Z_]+=.*change-me' "$ENV_FILE" | cut -d= -f1; exit 1
fi
for key in DOMAIN CADDY_TLS POSTGRES_PASSWORD APP_DB_PASSWORD REDIS_PASSWORD JWT_SECRET_KEY TOKEN_ENCRYPTION_KEYS; do
  [ -n "$(val "$key")" ] || { echo "$key is empty in $ENV_FILE"; exit 1; }
done
"${C[@]}" config -q
backup_dir="$(val BACKUP_DIR)"; backup_dir="${backup_dir:-./backups}"; mkdir -p .deploy "$backup_dir"
backup_uid="$(val BACKUP_UID)"; backup_uid="${backup_uid:-1000}"
if [ "$(stat -c %u "$backup_dir")" != "$backup_uid" ]; then
  echo "$backup_dir is owned by uid $(stat -c %u "$backup_dir"), but BACKUP_UID=$backup_uid:"
  echo "  set BACKUP_UID/BACKUP_GID to \`id -u\`/\`id -g\` in $ENV_FILE, or: sudo chown $backup_uid $backup_dir"; exit 1
fi

TAG="$(git rev-parse --short=12 HEAD 2>/dev/null || date -u +%Y%m%d%H%M%S)"
if [ -z "${SKIP_BUILD:-}" ]; then
  echo "== build $TAG"
  IMAGE_TAG="$TAG" "${C[@]}" build backend frontend
else
  TAG=prod
  if [ -s .deploy/releases ]; then TAG="$(tail -1 .deploy/releases | cut -d' ' -f1)"; fi
fi

if [ -n "$("${C[@]}" ps -q postgres 2>/dev/null)" ]; then
  echo "== backup before migrating"
  "${C[@]}" run --rm --no-deps backup sh /backup.sh once
fi

echo "== release $TAG"
for image in muxriddin-backend muxriddin-frontend; do
  [ "$TAG" = prod ] || docker tag "$image:$TAG" "$image:prod"
done
IMAGE_TAG=prod "${C[@]}" up -d --remove-orphans
grep -q "^$TAG " .deploy/releases 2>/dev/null || echo "$TAG $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> .deploy/releases

echo "== waiting for health"
for _ in $(seq 1 60); do
  state="$("${C[@]}" ps --format '{{.Service}} {{.Health}}')"
  if grep -q '^backend healthy' <<<"$state" && grep -q '^frontend healthy' <<<"$state"; then break; fi
  sleep 5
done

echo "== smoke test"
./scripts/prod-smoke.sh && echo "Deployed $TAG." || { echo "Smoke test failed — consider ./scripts/rollback.sh"; exit 1; }
