# Smoke test for the production stack (docker-compose.prod.yml) — Windows PowerShell 5.1+ / PowerShell 7.
# Read-only: it does not create users or content. Optional login checks use -Email / -Password.
#
#   .\scripts\prod-smoke.ps1
#   .\scripts\prod-smoke.ps1 -EnvFile .env.production -Email you@example.com -Password '...'
param(
    [string]$EnvFile = ".env.production",
    [string]$Email = "",
    [string]$Password = ""
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

$port = Get-EnvValue "PANEL_PORT"; if (-not $port) { $port = "3000" }
$panel = "http://127.0.0.1:$port"
$script:fails = 0
function Check([string]$Name, [scriptblock]$Test) {
    $ok = $false
    try { $ok = [bool](& $Test) } catch { $ok = $false }
    if ($ok) { Write-Host "  OK   $Name" -ForegroundColor Green }
    else { Write-Host "  FAIL $Name" -ForegroundColor Red; $script:fails++ }
}
function Get-Panel([string]$Path, $Session = $null) {
    $params = @{ Uri = "$panel$Path"; UseBasicParsing = $true; ErrorAction = "Stop" }
    if ($Session) { $params.WebSession = $Session }
    try { return Invoke-WebRequest @params } catch { return $_.Exception.Response }
}

Write-Host "== services"
$state = Invoke-Compose @("ps", "-a", "--format", "{{.Service}} {{.State}} {{.Health}} {{.ExitCode}}")
foreach ($s in "backend", "worker", "frontend", "postgres", "redis") {
    Check "$s healthy" { $state -match "(?m)^$s running healthy" }
}
Check "beat running" { $state -match "(?m)^beat running" }
Check "migrate finished (exit 0)" { $state -match "(?m)^migrate exited .* 0\s*$" }

Write-Host "== exposure"
foreach ($pair in @(@("backend", "8000"), @("postgres", "5432"), @("redis", "6379"))) {
    $published = (Invoke-Compose @("port", $pair[0], $pair[1])).Trim()
    Check "$($pair[0]) is not published on the host" { -not $published -or $published -eq ":0" -or $published -match "no port" }
}
Check "data network has no internet (postgres)" {
    & docker @compose exec -T postgres wget -q -T 3 -O /dev/null http://1.1.1.1 2>$null; $LASTEXITCODE -ne 0
}

Write-Host "== panel"
$login = Get-Panel "/login"
Check "panel /login 200" { [int]$login.StatusCode -eq 200 }
Check "CSP header" { "$($login.Headers['Content-Security-Policy'])" -match "frame-ancestors" }
Check "HSTS header" { "$($login.Headers['Strict-Transport-Security'])" -match "max-age" }
Check "X-Frame-Options DENY" { "$($login.Headers['X-Frame-Options'])" -eq "DENY" }
Check "no X-Powered-By" { -not $login.Headers['X-Powered-By'] }
Check "robots.txt disallows indexing" { (Get-Panel "/robots.txt").Content -match "Disallow: /" }
$health = (Get-Panel "/api/backend/health").Content | ConvertFrom-Json
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
    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $body = @{ email = $Email; password = $Password } | ConvertTo-Json
    Invoke-WebRequest -Uri "$panel/api/auth/login" -Method Post -Body $body -ContentType "application/json" `
        -Headers @{ Origin = $panel } -WebSession $session -UseBasicParsing | Out-Null
    Check "login through the panel" { (Get-Panel "/api/backend/auth/me" $session).Content -match '"email"' }
    $copy = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    foreach ($c in $session.Cookies.GetCookies($panel)) { $copy.Cookies.Add($c) }
    Invoke-WebRequest -Uri "$panel/api/auth/logout" -Method Post -Headers @{ Origin = $panel } `
        -WebSession $session -UseBasicParsing | Out-Null
    Check "logout revokes the token server-side" { [int](Get-Panel "/api/backend/auth/me" $copy).StatusCode -eq 401 }
    Check "rate-limit counters live in Redis" { (Invoke-Compose @("exec", "-T", "redis", "redis-cli", "--scan", "--pattern", "rl:*")) -match "rl:" }
} else {
    Write-Host "== session (skipped: pass -Email and -Password to test login/logout)"
}

Write-Host ""
if ($script:fails -eq 0) { Write-Host "All checks passed." -ForegroundColor Green }
else { Write-Host "$($script:fails) check(s) failed." -ForegroundColor Red }
exit $script:fails
