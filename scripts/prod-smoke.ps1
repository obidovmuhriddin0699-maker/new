# Smoke test for the production stack (docker-compose.prod.yml) - Windows PowerShell 5.1+ / PowerShell 7.
# Read-only: it does not create users or content. Optional login checks use -Email / -Password.
# The panel is reached as https://DOMAIN through Caddy with curl.exe (built into Windows 10/11);
# requests are pinned to -HostIp (default 127.0.0.1) with --resolve, so no DNS/hosts edit is needed.
#
#   .\scripts\prod-smoke.ps1
#   .\scripts\prod-smoke.ps1 -EnvFile .env.production -Email you@example.com -Password '...'
param(
    [string]$EnvFile = ".env.production",
    [string]$Email = "",
    [string]$Password = "",
    [string]$HostIp = "127.0.0.1"
)
$ErrorActionPreference = "Continue"
$env:ENV_FILE = $EnvFile
$compose = @("compose", "-f", "docker-compose.prod.yml", "--env-file", $EnvFile)

function Get-EnvValue([string]$Name) {
    $line = Get-Content $EnvFile | Where-Object { $_ -match "^$Name=" } | Select-Object -Last 1
    if (-not $line) { return "" }
    return (($line -split "=", 2)[1] -replace "\s+#.*$", "").Trim()
}
function Invoke-Compose([string[]]$Arguments) { & docker @compose @Arguments 2>&1 | Out-String }

$domain = Get-EnvValue "DOMAIN"; $tls = Get-EnvValue "CADDY_TLS"
$panel = "https://$domain"
$onWindows = $env:OS -eq "Windows_NT"
$curlExe = if ($onWindows) { "curl.exe" } else { "curl" }
$nullDev = if ($onWindows) { "NUL" } else { "/dev/null" }
$curlBase = @("-s", "--max-time", "15", "--noproxy", $domain, "--resolve", "${domain}:443:$HostIp", "--resolve", "${domain}:80:$HostIp")
# "tls internal" = Caddy's own CA (testing); a real certificate must verify normally.
if ($tls -eq "internal") { $curlBase += "-k" }
function Invoke-Curl([string[]]$Arguments) { (& $curlExe @curlBase @Arguments 2>$null) -join "`n" }
$script:fails = 0
function Check([string]$Name, [scriptblock]$Test) {
    $ok = $false
    try { $ok = [bool](& $Test) } catch { $ok = $false }
    if ($ok) { Write-Host "  OK   $Name" -ForegroundColor Green }
    else { Write-Host "  FAIL $Name" -ForegroundColor Red; $script:fails++ }
}

Write-Host "== services"
$state = Invoke-Compose @("ps", "-a", "--format", "{{.Service}} {{.State}} {{.Health}} {{.ExitCode}}")
foreach ($s in "backend", "worker", "frontend", "postgres", "redis") {
    Check "$s healthy" { $state -match "(?m)^$s running healthy" }
}
foreach ($s in "beat", "caddy", "backup") {
    Check "$s running" { $state -match "(?m)^$s running" }
}
Check "migrate finished (exit 0)" { $state -match "(?m)^migrate exited .* 0\s*$" }

Write-Host "== exposure"
foreach ($pair in @(@("backend", "8000"), @("postgres", "5432"), @("redis", "6379"))) {
    $published = (Invoke-Compose @("port", $pair[0], $pair[1])).Trim()
    Check "$($pair[0]) is not published on the host" { -not $published -or $published -eq ":0" -or $published -match "no port" }
}
$frontPort = (Invoke-Compose @("port", "frontend", "3000")).Trim()
Check "panel (frontend) is only reachable through Caddy" { -not $frontPort -or $frontPort -eq ":0" -or $frontPort -match "no port" }
Check "caddy publishes 443" { (Invoke-Compose @("port", "caddy", "443")).Trim() -match ":443$" }
Check "data network has no internet (postgres)" {
    & docker @compose exec -T postgres wget -q -T 3 -O /dev/null http://1.1.1.1 2>$null; $LASTEXITCODE -ne 0
}

Write-Host "== https (Caddy)"
$redirect = Invoke-Curl @("-o", $nullDev, "-w", "%{http_code} %{redirect_url}", "http://$domain/login")
Check "http:// redirects to https://" { $redirect -match "^30[18] https://$([regex]::Escape($domain))/login" }
if ($tls -eq "internal") {
    Write-Host "  --   certificate check skipped (CADDY_TLS=internal)"
} else {
    Check "certificate is valid for $domain" {
        & $curlExe -s -o $nullDev --max-time 15 --noproxy $domain --resolve "${domain}:443:$HostIp" "https://$domain/login" 2>$null; $LASTEXITCODE -eq 0
    }
}
Check "TLS 1.0/1.1 refused" { & $curlExe @curlBase -o $nullDev --tls-max 1.1 "$panel/login" 2>$null; $LASTEXITCODE -ne 0 }

Write-Host "== panel"
$headers = Invoke-Curl @("-D", "-", "-o", $nullDev, "$panel/login")
Check "panel /login 200" { $headers -match "^HTTP/\S+ 200" }
Check "CSP header" { $headers -match "(?im)^content-security-policy:.*frame-ancestors" }
Check "HSTS header" { $headers -match "(?im)^strict-transport-security:" }
Check "X-Frame-Options DENY" { $headers -match "(?im)^x-frame-options: DENY" }
Check "no X-Powered-By / Server header" { $headers -notmatch "(?im)^(x-powered-by|server):" }
Check "robots.txt disallows indexing" { (Invoke-Curl @("$panel/robots.txt")) -match "Disallow: /" }
Check "privacy policy is public" { (Invoke-Curl @("$panel/privacy")) -match "Privacy Policy" }
Check "terms are public" { (Invoke-Curl @("$panel/terms")) -match "Terms of Service" }
$health = Invoke-Curl @("$panel/api/backend/health") | ConvertFrom-Json
Check "API health via panel: database ok" { $health.components.database.ok }
Check "API health via panel: redis ok" { $health.components.redis.ok }

Write-Host "== containers"
Check "backend runs as uid 10001" { (Invoke-Compose @("exec", "-T", "backend", "id", "-u")).Trim() -eq "10001" }
Check "frontend runs as uid 10001" { (Invoke-Compose @("exec", "-T", "frontend", "id", "-u")).Trim() -eq "10001" }
Check "backend root filesystem is read-only" {
    & docker @compose exec -T backend sh -c "touch /app/x" 2>$null; $LASTEXITCODE -ne 0
}
Check "no pip in the backend image" {
    & docker @compose exec -T backend sh -c "command -v pip || python -m pip --version" 2>$null; $LASTEXITCODE -ne 0
}
Check "APP_ENV=production" { (Invoke-Compose @("exec", "-T", "backend", "printenv", "APP_ENV")).Trim() -eq "production" }

Check "caddy root filesystem is read-only" {
    & docker @compose exec -T caddy touch /etc/x 2>$null; $LASTEXITCODE -ne 0
}

Write-Host "== backups"
$backupDir = Get-EnvValue "BACKUP_DIR"; if (-not $backupDir) { $backupDir = "./backups" }
Check "backup directory exists" { Test-Path $backupDir -PathType Container }
$lastBackup = (Invoke-Compose @("exec", "-T", "postgres", "psql", "-U", (Get-EnvValue "POSTGRES_USER"),
    "-d", (Get-EnvValue "POSTGRES_DB"), "-Atc",
    "SELECT value->'value'->>'ok' FROM system_settings WHERE key='ops.last_backup'")).Trim()
if (-not $lastBackup) {
    Write-Host "  --   no backup recorded yet (first one runs at BACKUP_TIME; or: docker compose ... exec backup sh /backup.sh once)"
} else {
    Check "last backup succeeded" { $lastBackup -eq "true" }
}

Write-Host "== data layer"
$appUser = Get-EnvValue "APP_DB_USER"; $appPw = Get-EnvValue "APP_DB_PASSWORD"
$db = Get-EnvValue "POSTGRES_DB"; if (-not $db) { $db = "muxriddin" }
foreach ($sql in "DELETE FROM audit_logs", "CREATE TABLE pwned(id int)") {
    Check "app DB role refused: $sql" {
        (Invoke-Compose @("exec", "-T", "-e", "PGPASSWORD=$appPw", "postgres", "psql", "-h", "127.0.0.1",
            "-U", $appUser, "-d", $db, "-c", $sql)) -match "permission denied"
    }
}
Check "redis requires a password" { (Invoke-Compose @("exec", "-T", "redis", "sh", "-c", "REDISCLI_AUTH= redis-cli ping")) -match "NOAUTH" }

if ($Email -and $Password) {
    Write-Host "== session"
    $jar = (New-TemporaryFile).FullName; $copy = (New-TemporaryFile).FullName
    $bodyFile = (New-TemporaryFile).FullName
    # UTF-8 without BOM (Set-Content -Encoding utf8 adds a BOM in Windows PowerShell 5.1,
    # ascii would turn non-ASCII password characters into "?").
    $json = @{ email = $Email; password = $Password } | ConvertTo-Json -Compress
    [IO.File]::WriteAllText($bodyFile, $json, (New-Object Text.UTF8Encoding $false))
    # A forged X-Forwarded-For must not reach the audit log: Caddy overwrites it.
    Invoke-Curl @("-c", $jar, "-X", "POST", "$panel/api/auth/login", "-H", "Origin: $panel",
        "-H", "Content-Type: application/json", "-H", "X-Forwarded-For: 203.0.113.66", "--data-binary", "@$bodyFile") | Out-Null
    Remove-Item $bodyFile
    Check "login through the panel" { (Invoke-Curl @("-b", $jar, "$panel/api/backend/auth/me")) -match '"email"' }
    $audit = Invoke-Curl @("-b", $jar, "$panel/api/backend/audit-logs?action=AUTH_LOGIN_SUCCEEDED&limit=1") | ConvertFrom-Json
    $loginIp = "$($audit.items[0].details.ip)"
    Write-Host "       audited client IP: $loginIp"
    Check "audit log has the real client IP (not the proxy, not a forged header)" {
        $loginIp -and $loginIp -ne "203.0.113.66" -and $loginIp -ne "172.30.0.10"
    }
    Check "ops monitor reachable (owner/admin)" { (Invoke-Curl @("-b", $jar, "$panel/api/backend/system/ops-status")) -match '"ok"' }
    Copy-Item $jar $copy -Force
    Invoke-Curl @("-b", $jar, "-X", "POST", "$panel/api/auth/logout", "-H", "Origin: $panel") | Out-Null
    Check "logout revokes the token server-side" {
        (Invoke-Curl @("-o", $nullDev, "-w", "%{http_code}", "-b", $copy, "$panel/api/backend/auth/me")) -eq "401"
    }
    Remove-Item $jar, $copy -ErrorAction SilentlyContinue
    Check "rate-limit counters live in Redis" { (Invoke-Compose @("exec", "-T", "redis", "redis-cli", "--scan", "--pattern", "rl:*")) -match "rl:" }
} else {
    Write-Host "== session (skipped: pass -Email and -Password to test login/logout)"
}

Write-Host ""
if ($script:fails -eq 0) { Write-Host "All checks passed." -ForegroundColor Green }
else { Write-Host "$($script:fails) check(s) failed." -ForegroundColor Red }
exit $script:fails
