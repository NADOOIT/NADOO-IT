param(
    [switch]$Quick
)

$script = Join-Path $PSScriptRoot 'scripts\test-docker.ps1'

if ($Quick) {
    & $script -Quick
} else {
    & $script
}

exit $LASTEXITCODE
