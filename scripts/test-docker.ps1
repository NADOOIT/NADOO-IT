Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

param(
    [switch]$Quick
)

$composeFile = "docker-compose-test.yml"

if ($Quick) {
    Write-Host "Running quick test with inline install..." -ForegroundColor Cyan
    docker compose -f $composeFile run --rm test sh -lc "python -m pip install --upgrade pip && pip install -r /workspace/requirements-dev.txt && pytest -q"
} else {
    Write-Host "Running full test (build + install)..." -ForegroundColor Cyan
    docker compose -f $composeFile up --build --abort-on-container-exit --exit-code-from test
}

exit $LASTEXITCODE
