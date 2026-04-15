#!/usr/bin/env pwsh
# ═══════════════════════════════════════════════════════════════════════════════
# HOTFIX-002: Fix NATS Authentication
# ═══════════════════════════════════════════════════════════════════════════════
#
# Resolves NATS "Authorization Violation" due to credential mismatch.
# ⚠️  Development only. Production uses nats-secure.conf with mTLS.
#
# Usage:
#   .\scripts\apply-hotfix-002.ps1              # Apply hotfix
#   .\scripts\apply-hotfix-002.ps1 -FullReset   # Full reset (removes volumes)
# ═══════════════════════════════════════════════════════════════════════════════

param([switch]$FullReset)

Write-Host "Applying HOTFIX-002..." -ForegroundColor Cyan

if ($FullReset) {
    docker compose -f docker-compose-core.yml down
    docker volume rm sahool-nats-data 2>$null
}

docker compose -f docker-compose-core.yml up -d nats
Start-Sleep -Seconds 5

$natsContainer = docker compose -f docker-compose-core.yml ps -q nats
$test = docker run --rm --network "container:$natsContainer" natsio/nats-box nats --server nats://127.0.0.1:4222 --user sahool_app --password $env:NATS_PASSWORD pub test "hotfix-ok" 2>&1
if ($test -match "Published") {
    Write-Host "✅ HOTFIX-002 applied successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Authentication test failed" -ForegroundColor Red
}
