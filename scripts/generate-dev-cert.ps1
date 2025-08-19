Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Generate self-signed cert and key into ./app using an ephemeral container with OpenSSL
# This avoids requiring OpenSSL on the host and is reproducible across machines.

$AppDir = (Resolve-Path (Join-Path $PSScriptRoot "..\app")).Path
Write-Host "Generating development TLS certificate in: $AppDir" -ForegroundColor Cyan

# Ensure target directory exists
if (!(Test-Path $AppDir)) { throw "App directory not found: $AppDir" }

 # Create a minimal OpenSSL config to ensure SAN is present across OpenSSL/LibreSSL variants
$sanPath = Join-Path $AppDir "san.cnf"
$sanConfig = @"
[ req ]
default_bits       = 2048
distinguished_name = dn
x509_extensions    = v3_req
prompt             = no

[ dn ]
CN = localhost

[ v3_req ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = localhost
IP.1  = 127.0.0.1
"@
Set-Content -LiteralPath $sanPath -Value $sanConfig -NoNewline

# Use Alpine to install openssl and generate a cert with SAN for localhost and 127.0.0.1
$mount = "${AppDir}:/work"
$shellCmd = "apk add --no-cache openssl && openssl req -x509 -nodes -newkey rsa:2048 -days 825 -keyout key.pem -out cert.cer -config san.cnf -extensions v3_req"
$dockerArgs = @("run","--rm","-v",$mount,"-w","/work","alpine:3","sh","-lc",$shellCmd)

Write-Host ("docker " + ($dockerArgs -join ' ')) -ForegroundColor DarkGray
& docker @dockerArgs
if ($LASTEXITCODE -ne 0) { throw "OpenSSL container failed with exit code $LASTEXITCODE" }

# Verify files
$certPath = Join-Path $AppDir "cert.cer"
$keyPath = Join-Path $AppDir "key.pem"
if (!(Test-Path $certPath) -or !(Test-Path $keyPath)) { throw "Certificate/key files were not created." }

# Cleanup temp files
Remove-Item -LiteralPath $sanPath -Force -ErrorAction SilentlyContinue

Write-Host "Created: $certPath" -ForegroundColor Green
Write-Host "Created: $keyPath" -ForegroundColor Green
