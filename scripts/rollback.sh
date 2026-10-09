#!/usr/bin/env bash
# Switch back to the previous release's images (or a given tag from .deploy/releases).
#
#   ./scripts/rollback.sh          previous release
#   ./scripts/rollback.sh <tag>    a specific release
#
# Images only: database migrations are NOT reverted. If the release you are leaving ran a
# migration, restore the backup that deploy.sh took right before it (scripts/restore.sh).
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env.production}"; export ENV_FILE
C=(docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE")
[ -f .deploy/releases ] || { echo "no .deploy/releases — nothing to roll back to"; exit 1; }
TAG="${1:-$(tail -2 .deploy/releases | head -1 | cut -d' ' -f1)}"
CURRENT="$(tail -1 .deploy/releases | cut -d' ' -f1)"
[ "$TAG" != "$CURRENT" ] || [ -n "${1:-}" ] || { echo "only one release recorded"; exit 1; }
for image in muxriddin-backend muxriddin-frontend; do
  docker image inspect "$image:$TAG" >/dev/null || { echo "image $image:$TAG not found"; exit 1; }
  docker tag "$image:$TAG" "$image:prod"
done
IMAGE_TAG=prod "${C[@]}" up -d --remove-orphans
echo "$TAG $(date -u +%Y-%m-%dT%H:%M:%SZ) rollback" >> .deploy/releases
echo "Rolled back to $TAG. Run ./scripts/prod-smoke.sh to verify."
