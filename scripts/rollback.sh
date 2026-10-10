#!/usr/bin/env bash
# Switch back to the previous release's images (or a given tag from .deploy/releases).
#
#   ./scripts/rollback.sh          the most recent release that differs from the current one
#   ./scripts/rollback.sh <tag>    a specific release
#
# Images only: database migrations are NOT reverted. If the release you are leaving ran a
# migration, restore the backup that deploy.sh took right before it (scripts/restore.sh).
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env.production}"; export ENV_FILE
C=(docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE")
val() { { grep -E "^$1=" "$ENV_FILE" || true; } | tail -1 | cut -d= -f2- | sed 's/[[:space:]]*#.*$//'; }
COMPOSE_PROFILES="$(val COMPOSE_PROFILES)"; export COMPOSE_PROFILES
[ -s .deploy/releases ] || { echo "no .deploy/releases — nothing to roll back to"; exit 1; }
# The last line is the running release (deploy.sh and this script append one per switch).
CURRENT="$(tail -1 .deploy/releases | cut -d' ' -f1)"
PREVIOUS="$(awk -v cur="$CURRENT" '$1 != cur { tag = $1 } END { print tag }' .deploy/releases)"
TAG="${1:-$PREVIOUS}"
[ -n "$TAG" ] || { echo "no release other than $CURRENT recorded — nothing to roll back to"; exit 1; }
echo "== rolling back: $CURRENT -> $TAG"
for image in muxriddin-backend muxriddin-frontend; do
  docker image inspect "$image:$TAG" >/dev/null || { echo "image $image:$TAG not found"; exit 1; }
  docker tag "$image:$TAG" "$image:prod"
done
IMAGE_TAG=prod "${C[@]}" up -d --remove-orphans
echo "$TAG $(date -u +%Y-%m-%dT%H:%M:%SZ) rollback" >> .deploy/releases
echo "Rolled back to $TAG. Run ./scripts/prod-smoke.sh to verify."
