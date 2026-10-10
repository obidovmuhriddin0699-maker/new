<#
.SYNOPSIS
  One-time local development setup (Windows PowerShell 5.1+ / PowerShell 7+).

.DESCRIPTION
  - creates backend\.venv and installs backend dependencies
  - creates .env from .env.example and generates local secrets (JWT + Fernet)
  - runs Alembic migrations (SQLite by default, or DATABASE_URL from .env)
  - installs frontend dependencies

  Usage (from the repository root):
    powershell -ExecutionPolicy Bypass -File .\scripts\dev-setup.ps1
#>
[CmdletBinding()]
param(
    [string]$Python = "python",
    [switch]$SkipFrontend
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

# PowerShell 5.1 has no $IsWindows variable; it only runs on Windows.
$OnWindows = ($PSVersionTable.PSEdition -eq "Desktop") -or $IsWindows
$VenvPython = if ($OnWindows) { "backend\.venv\Scripts\python.exe" } else { "backend/.venv/bin/python" }

Step "Checking tools"
& $Python --version
if ($LASTEXITCODE -ne 0) { throw "Python not found. Install Python 3.12 and re-run." }
if (-not $SkipFrontend) {
    node --version
    if ($LASTEXITCODE -ne 0) { throw "Node.js not found. Install Node.js 22 LTS and re-run." }
}

Step "Creating virtual environment"
if (-not (Test-Path $VenvPython)) {
    & $Python -m venv backend/.venv
    if ($LASTEXITCODE -ne 0) { throw "venv creation failed" }
}
& $VenvPython -m pip install --upgrade pip --quiet
& $VenvPython -m pip install -e "backend[dev]" --quiet
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }

Step "Preparing .env"
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "    created .env from .env.example"
}
$envText = Get-Content ".env" -Raw
if ($envText -match "(?m)^JWT_SECRET_KEY=\s*$") {
    $jwt = & $VenvPython -c "import secrets; print(secrets.token_urlsafe(48))"
    $envText = $envText -replace "(?m)^JWT_SECRET_KEY=\s*$", "JWT_SECRET_KEY=$jwt"
    Write-Host "    generated JWT_SECRET_KEY"
}
if ($envText -match "(?m)^TOKEN_ENCRYPTION_KEYS=\s*$") {
    $fernet = & $VenvPython -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    $envText = $envText -replace "(?m)^TOKEN_ENCRYPTION_KEYS=\s*$", "TOKEN_ENCRYPTION_KEYS=$fernet"
    Write-Host "    generated TOKEN_ENCRYPTION_KEYS"
}
# UTF-8 without BOM (PowerShell 5.1's -Encoding UTF8 writes a BOM)
[System.IO.File]::WriteAllText((Join-Path $Root ".env"), $envText, (New-Object System.Text.UTF8Encoding $false))

Step "Running database migrations"
Push-Location backend
try {
    & "..\$VenvPython".Replace("\", [IO.Path]::DirectorySeparatorChar) -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw "alembic upgrade failed" }
} finally {
    Pop-Location
}

if (-not $SkipFrontend) {
    Step "Installing frontend dependencies"
    Push-Location frontend
    try {
        if (-not (Test-Path ".env.local")) { Copy-Item ".env.example" ".env.local" }
        npm install --no-audit --no-fund
        if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
    } finally {
        Pop-Location
    }
}

Step "Done"
Write-Host @"

Next steps:
  1) Create the admin user:
       cd backend
       .\.venv\Scripts\python.exe -m app.cli create-admin --email you@example.com
  2) Start the backend:
       .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
  3) In another terminal, start the frontend:
       cd frontend
       npm run dev
  4) Open http://localhost:3000 and http://localhost:8000/docs
"@
