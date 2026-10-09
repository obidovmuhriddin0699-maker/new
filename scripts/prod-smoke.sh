#!/usr/bin/env bash
# Smoke test for the production stack (docker-compose.prod.yml). Read-only: it does not
# create users or content. Optional login checks use SMOKE_EMAIL / SMOKE_PASSWORD.
#
#   ENV_FILE=.env.production ./scripts/prod-smoke.sh
#   SMOKE_EMAIL=you@example.com SMOKE_PASSWORD='...' ./scripts/prod-smoke.sh
set -uo pipefail

ENV_FILE="${ENV_FILE:-.env.production}"
export ENV_FILE
C=(docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE")
val() { grep -E "^$1=" "$ENV_FILE" | tail -1 | cut -d= -f2- | sed 's/[[:space:]]*#.*$//'; }
PORT="$(val PANEL_PORT)"; PORT="${PORT:-3000}"
PANEL="http://127.0.0.1:${PORT}"
fails=0
ok()   { printf '  \033[32mOK\033[0m   %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; fails=$((fails + 1)); }
check() { if eval "$2" >/dev/null 2>&1; then ok "$1"; else bad "$1"; fi; }

echo "== services"
state="$("${C[@]}" ps -a --format '{{.Service}} {{.State}} {{.Health}} {{.ExitCode}}')"
for s in backend worker frontend postgres redis; do
  check "$s healthy" "grep -q '^$s running healthy' <<<\"\$state\""
done
check "beat running" "grep -q '^beat running' <<<\"\$state\""
check "migrate finished (exit 0)" "grep -q '^migrate exited .* 0$' <<<\"\$state\""

echo "== exposure"
# `compose port` prints ":0" (or nothing) for a port that is not published.
unpublished() { local p; p="$("${C[@]}" port "$1" "$2" 2>/dev/null)"; [ -z "$p" ] || [ "$p" = ":0" ]; }
check "backend is not published on the host" "unpublished backend 8000"
check "postgres is not published" "unpublished postgres 5432"
check "redis is not published" "unpublished redis 6379"
check "data network has no internet (postgres)" \
  "! ${C[*]} exec -T postgres wget -q -T 3 -O /dev/null http://1.1.1.1"

echo "== panel"
headers="$(curl -s -D - -o /dev/null "$PANEL/login")"
check "panel /login 200" "grep -q ' 200' <<<\"\$headers\""
check "CSP header" "grep -qi '^content-security-policy:.*frame-ancestors' <<<\"\$headers\""
check "HSTS header" "grep -qi '^strict-transport-security:' <<<\"\$headers\""
check "X-Frame-Options DENY" "grep -qi '^x-frame-options: DENY' <<<\"\$headers\""
check "no X-Powered-By" "! grep -qi '^x-powered-by' <<<\"\$headers\""
check "robots.txt disallows indexing" "curl -s $PANEL/robots.txt | grep -q 'Disallow: /'"
health="$(curl -s "$PANEL/api/backend/health")"
check "API health via panel: database ok" "grep -q '\"database\":{\"ok\":true' <<<\"\$health\""
check "API health via panel: redis ok" "grep -q '\"redis\":{\"ok\":true' <<<\"\$health\""

echo "== containers"
check "backend runs as uid 10001" "[ \"\$(${C[*]} exec -T backend id -u)\" = 10001 ]"
check "frontend runs as uid 10001" "[ \"\$(${C[*]} exec -T frontend id -u)\" = 10001 ]"
check "backend root filesystem is read-only" "! ${C[*]} exec -T backend sh -c 'touch /app/x'"
check "no pip in the backend image" "! ${C[*]} exec -T backend sh -c 'command -v pip || python -m pip --version || python -m ensurepip --help'"
check "APP_ENV=production" "${C[*]} exec -T backend printenv APP_ENV | grep -qx production"

echo "== data layer"
APP_USER="$(val APP_DB_USER)"; APP_PW="$(val APP_DB_PASSWORD)"; DB="$(val POSTGRES_DB)"; DB="${DB:-muxriddin}"
check "app DB role cannot delete audit history" \
  "(${C[*]} exec -T -e PGPASSWORD=\"$APP_PW\" postgres psql -h 127.0.0.1 -U \"$APP_USER\" -d \"$DB\" -c 'DELETE FROM audit_logs' 2>&1 || true) | grep -q 'permission denied'"
check "app DB role cannot change the schema" \
  "(${C[*]} exec -T -e PGPASSWORD=\"$APP_PW\" postgres psql -h 127.0.0.1 -U \"$APP_USER\" -d \"$DB\" -c 'CREATE TABLE pwned(id int)' 2>&1 || true) | grep -q 'permission denied'"
check "redis requires a password" "(${C[*]} exec -T redis sh -c 'REDISCLI_AUTH= redis-cli ping' 2>&1 || true) | grep -q NOAUTH"

if [ -n "${SMOKE_EMAIL:-}" ] && [ -n "${SMOKE_PASSWORD:-}" ]; then
  echo "== session"
  jar="$(mktemp)"; copy="$(mktemp)"
  curl -s -c "$jar" -X POST "$PANEL/api/auth/login" -H "Origin: $PANEL" -H 'Content-Type: application/json' \
    -d "{\"email\":\"$SMOKE_EMAIL\",\"password\":\"$SMOKE_PASSWORD\"}" >/dev/null
  check "login through the panel" "curl -s -b $jar $PANEL/api/backend/auth/me | grep -q '\"email\"'"
  cp "$jar" "$copy"
  curl -s -b "$jar" -X POST "$PANEL/api/auth/logout" -H "Origin: $PANEL" >/dev/null
  check "logout revokes the token server-side" \
    "[ \"\$(curl -s -o /dev/null -w '%{http_code}' -b $copy $PANEL/api/backend/auth/me)\" = 401 ]"
  check "rate-limit counters live in Redis" "${C[*]} exec -T redis redis-cli --scan --pattern 'rl:*' | grep -q rl:"
  rm -f "$jar" "$copy"
else
  echo "== session (skipped: set SMOKE_EMAIL and SMOKE_PASSWORD to test login/logout)"
fi

echo
if [ "$fails" -eq 0 ]; then echo "All checks passed."; else echo "$fails check(s) failed."; fi
exit "$fails"
