param(
    [switch]$ForceRegen,
    [switch]$NoCelery
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Ensure dev certs exist (or regenerate if requested)
$certPath = Join-Path $PSScriptRoot "..\app\cert.cer"
$keyPath  = Join-Path $PSScriptRoot "..\app\key.pem"

if ($ForceRegen -or !(Test-Path $certPath) -or !(Test-Path $keyPath)) {
    Write-Host "Generating self-signed development certificate..." -ForegroundColor Cyan
    & (Join-Path $PSScriptRoot 'generate-dev-cert.ps1')
}

# Compose file
$compose = Join-Path $PSScriptRoot "..\docker-compose-dev-WIN_SQLite.yml"

# Start dependencies
Write-Host "Starting Redis..." -ForegroundColor Cyan
docker compose -f $compose up -d redis

# Start app (SSL via runserver_plus using cert.cer/key.pem inside /app)
Write-Host "Starting app (HTTPS on 8000)..." -ForegroundColor Cyan
docker compose -f $compose up -d app

if (-not $NoCelery) {
    Write-Host "Starting celery worker..." -ForegroundColor Cyan
    docker compose -f $compose up -d celery_worker
}

# Show status
Write-Host "\nServices status:" -ForegroundColor Yellow
docker compose -f $compose ps

Write-Host "\nOpen: https://localhost:8000" -ForegroundColor Green
