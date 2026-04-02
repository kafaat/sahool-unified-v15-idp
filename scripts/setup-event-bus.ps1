#!/usr/bin/env pwsh
# ═══════════════════════════════════════════════════════════════════════════════
# Setup SAHOOL Event Bus - JetStream Streams
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host "Setting up SAHOOL Event Bus..." -ForegroundColor Cyan

nats context save sahool-local --server nats://localhost:4222 --user sahool_app --password $env:NATS_PASSWORD
nats context select sahool-local

$streams = @("SAHOOL_EVENTS", "SAHOOL_COMMANDS", "SAHOOL_REGISTRY", "SAHOOL_HEALTH", "SAHOOL_AUDIT")
foreach ($s in $streams) {
    $domain = ($s.Split('_')[1]).ToLower()
    nats stream add $s --subjects="SAHOOL.${domain}.>" --retention=limits -f 2>$null
}

Write-Host "✅ Event Bus ready" -ForegroundColor Green
