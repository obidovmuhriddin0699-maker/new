#!/usr/bin/env bash
# Smoke test for the production stack (docker-compose.prod.yml). Read-only: it does not
# create users or content. Optional login checks use SMOKE_EMAIL / SMOKE_PASSWORD.
# The panel is reached as https://$DOMAIN through Caddy; requests are pinned to
# SMOKE_HOST (default 127.0.0.1, i.e. run it on the server) so DNS is not needed.
#
#   ENV_FILE=.env.production ./scripts/prod-smoke.sh
#   SMOKE_EMAIL=you@example.com SMOKE_PASSWORD='...' ./scripts/prod-smoke.sh
set -uo pipefail

ENV_FILE="${ENV_FILE:-.env.production}"
export ENV_FILE
C=(docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE")
val() { grep -E "^$1=" "$ENV_FILE" | tail -1 | cut -d= -f2- | sed 's/[[:space:]]*#.*$//'; }
DOMAIN="$(val DOMAIN)"; TLS="$(val CADDY_TLS)"; HOST_IP="${SMOKE_HOST:-127.0.0.1}"
PANEL="https://${DOMAIN}"
CURL=(curl -s --max-time 15 --noproxy "${DOMAIN}" --resolve "${DOMAIN}:443:${HOST_IP}" --resolve "${DOMAIN}:80:${HOST_IP}")
# "tls internal" = Caddy's own CA (testing); a real certificate must verify normally.
[ "$TLS" = internal ] && CURL+=(-k)
fails=0
ok()   { printf '  \033[32mOK\033[0m   %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; fails=$((fails + 1)); }
check() { if eval "$2" >/dev/null 2>&1; then ok "$1"; else bad "$1"; fi; }

echo "== services"
state="$("${C[@]}" ps -a --format '{{.Service}} {{.State}} {{.Health}} {{.ExitCode}}')"
for s in backend worker frontend postgres redis; do
  check "$s healthy" "grep -q '^$s running healthy' <<<\"\$state\""
done
for s in beat caddy backup; do
  check "$s running" "grep -q '^$s running' <<<\"\$state\""
done
check "migrate finished (exit 0)" "grep -q '^migrate exited .* 0$' <<<\"\$state\""

echo "== exposure"
# `compose port` prints ":0" (or nothing) for a port that is not published.
unpublished() { local p; p="$("${C[@]}" port "$1" "$2" 2>/dev/null)"; [ -z "$p" ] || [ "$p" = ":0" ]; }
check "backend is not published on the host" "unpublished backend 8000"
check "postgres is not published" "unpublished postgres 5432"
check "redis is not published" "unpublished redis 6379"
check "panel (frontend) is only reachable through Caddy" "unpublished frontend 3000"
check "caddy publishes 443" "! unpublished caddy 443"
check "data network has no internet (postgres)" \
  "! ${C[*]} exec -T postgres wget -q -T 3 -O /dev/null http://1.1.1.1"

echo "== https (Caddy)"
redirect="$("${CURL[@]}" -o /dev/null -w '%{http_code} %{redirect_url}' "http://${DOMAIN}/login")"
check "http:// redirects to https://" "grep -Eq '^30[18] https://${DOMAIN}/login' <<<\"\$redirect\""
if [ "$TLS" = internal ]; then
  echo "  --   certificate check skipped (CADDY_TLS=internal)"
else
  check "certificate is valid for ${DOMAIN}" \
    "curl -s -o /dev/null --max-time 15 --noproxy ${DOMAIN} --resolve ${DOMAIN}:443:${HOST_IP} https://${DOMAIN}/login"
fi
check "TLS 1.0/1.1 refused" "! ${CURL[*]} -o /dev/null --tls-max 1.1 $PANEL/login"

echo "== panel"
headers="$("${CURL[@]}" -D - -o /dev/null "$PANEL/login")"
check "panel /login 200" "grep -q ' 200' <<<\"\$headers\""
check "CSP header" "grep -qi '^content-security-policy:.*frame-ancestors' <<<\"\$headers\""
check "HSTS header" "grep -qi '^strict-transport-security:' <<<\"\$headers\""
check "X-Frame-Options DENY" "grep -qi '^x-frame-options: DENY' <<<\"\$headers\""
check "no X-Powered-By / Server header" "! grep -Eqi '^(x-powered-by|server):' <<<\"\$headers\""
check "robots.txt disallows indexing" "${CURL[*]} $PANEL/robots.txt | grep 'Disallow: /'"
check "privacy policy is public" "${CURL[*]} $PANEL/privacy | grep 'Privacy Policy'"
check "terms are public" "${CURL[*]} $PANEL/terms | grep 'Terms of Service'"
health="$("${CURL[@]}" "$PANEL/api/backend/health")"
check "API health via panel: database ok" "grep -q '\"database\":{\"ok\":true' <<<\"\$health\""
check "API health via panel: redis ok" "grep -q '\"redis\":{\"ok\":true' <<<\"\$health\""

echo "== containers"
check "backend runs as uid 10001" "[ \"\$(${C[*]} exec -T backend id -u)\" = 10001 ]"
check "frontend runs as uid 10001" "[ \"\$(${C[*]} exec -T frontend id -u)\" = 10001 ]"
check "backend root filesystem is read-only" "! ${C[*]} exec -T backend sh -c 'touch /app/x'"
check "no pip in the backend image" "! ${C[*]} exec -T backend sh -c 'command -v pip || python -m pip --version || python -m ensurepip --help'"
check "APP_ENV=production" "${C[*]} exec -T backend printenv APP_ENV | grep -qx production"

check "caddy root filesystem is read-only" "! ${C[*]} exec -T caddy touch /etc/x"

echo "== backups"
BDIR="$(val BACKUP_DIR)"; BDIR="${BDIR:-./backups}"
check "backup directory exists" "[ -d \"$BDIR\" ]"
last_backup="$(${C[*]} exec -T postgres psql -U "$(val POSTGRES_USER)" -d "$(val POSTGRES_DB)" -Atc \
  "SELECT value->'value'->>'ok' FROM system_settings WHERE key='ops.last_backup'" 2>/dev/null)"
if [ -z "$last_backup" ]; then
  echo "  --   no backup recorded yet (first one runs at BACKUP_TIME; or: ${C[*]} exec backup sh /backup.sh once)"
else
  check "last backup succeeded" "[ \"$last_backup\" = true ]"
fi

echo "== data layer"
APP_USER="$(val APP_DB_USER)"; APP_PW="$(val APP_DB_PASSWORD)"; DB="$(val POSTGRES_DB)"; DB="${DB:-muxriddin}"
check "app DB role cannot delete audit history" \
  "(${C[*]} exec -T -e PGPASSWORD=\"$APP_PW\" postgres psql -h 127.0.0.1 -U \"$APP_USER\" -d \"$DB\" -c 'DELETE FROM audit_logs' 2>&1 || true) | grep 'permission denied'"
check "app DB role cannot change the schema" \
  "(${C[*]} exec -T -e PGPASSWORD=\"$APP_PW\" postgres psql -h 127.0.0.1 -U \"$APP_USER\" -d \"$DB\" -c 'CREATE TABLE pwned(id int)' 2>&1 || true) | grep 'permission denied'"
check "redis requires a password" "(${C[*]} exec -T redis sh -c 'REDISCLI_AUTH= redis-cli ping' 2>&1 || true) | grep NOAUTH"

# {"email": SMOKE_EMAIL, "password": SMOKE_PASSWORD} as JSON (python3, else jq, else printf).
login_body() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json, os; print(json.dumps({"email": os.environ["SMOKE_EMAIL"], "password": os.environ["SMOKE_PASSWORD"]}))'
  elif command -v jq >/dev/null 2>&1; then
    jq -cn --arg email "$SMOKE_EMAIL" --arg password "$SMOKE_PASSWORD" '{email: $email, password: $password}'
  else
    json_str() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/\t/\\t/g'; }
    printf '{"email":"%s","password":"%s"}' "$(json_str "$SMOKE_EMAIL")" "$(json_str "$SMOKE_PASSWORD")"
  fi
}

if [ -n "${SMOKE_EMAIL:-}" ] && [ -n "${SMOKE_PASSWORD:-}" ]; then
  export SMOKE_EMAIL SMOKE_PASSWORD
  echo "== session"
  jar="$(mktemp)"; copy="$(mktemp)"
  # A forged X-Forwarded-For must not reach the audit log: Caddy overwrites it.
  # The body is sent on stdin (not in the process list) and built with a JSON encoder, so
  # quotes or backslashes in the password cannot break it.
  login_body | "${CURL[@]}" -c "$jar" -X POST "$PANEL/api/auth/login" -H "Origin: $PANEL" \
    -H 'Content-Type: application/json' -H 'X-Forwarded-For: 203.0.113.66' --data-binary @- >/dev/null
  check "login through the panel" "${CURL[*]} -b $jar $PANEL/api/backend/auth/me | grep '\"email\"'"
  login_ip="$("${CURL[@]}" -b "$jar" "$PANEL/api/backend/audit-logs?action=AUTH_LOGIN_SUCCEEDED&limit=1" \
    | grep -o '"ip":"[^"]*"' | head -1 | cut -d'"' -f4)"
  echo "       audited client IP: ${login_ip:-?}"
  check "audit log has the real client IP (not the proxy, not a forged header)" \
    "[ -n \"$login_ip\" ] && [ \"$login_ip\" != 203.0.113.66 ] && [ \"$login_ip\" != 172.30.0.10 ]"
  check "ops monitor reachable (owner/admin)" "${CURL[*]} -b $jar $PANEL/api/backend/system/ops-status | grep '\"ok\"'"
  cp "$jar" "$copy"
  "${CURL[@]}" -b "$jar" -X POST "$PANEL/api/auth/logout" -H "Origin: $PANEL" >/dev/null
  check "logout revokes the token server-side" \
    "[ \"\$(${CURL[*]} -o /dev/null -w '%{http_code}' -b $copy $PANEL/api/backend/auth/me)\" = 401 ]"
  check "rate-limit counters live in Redis" "${C[*]} exec -T redis redis-cli --scan --pattern 'rl:*' | grep rl:"
  rm -f "$jar" "$copy"
else
  echo "== session (skipped: set SMOKE_EMAIL and SMOKE_PASSWORD to test login/logout)"
fi

echo
if [ "$fails" -eq 0 ]; then echo "All checks passed."; else echo "$fails check(s) failed."; fi
exit "$fails"
