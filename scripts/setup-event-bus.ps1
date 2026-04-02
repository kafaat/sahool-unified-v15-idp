#!/usr/bin/env pwsh
# ═══════════════════════════════════════════════════════════════════════════════
# Setup SAHOOL Event Bus - JetStream Streams
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host "Setting up SAHOOL Event Bus..." -ForegroundColor Cyan

nats context save sahool-local --server nats://localhost:4222 --user sahool_app --password $env:NATS_PASSWORD
nats context select sahool-local

# Create streams with per-stream retention and settings matching sahool-streams.yaml
# Subject prefix is lowercase to match NATS ACLs in config/nats/nats.conf
nats stream add SAHOOL_EVENTS    --subjects="sahool.events.>"   --retention=limits    --max-age=30d  --storage=file   -f 2>$null
nats stream add SAHOOL_COMMANDS  --subjects="sahool.commands.>"  --retention=workqueue --max-age=7d   --storage=file   -f 2>$null
nats stream add SAHOOL_REGISTRY  --subjects="sahool.registry.>"  --retention=limits    --max-age=1h   --storage=memory -f 2>$null
nats stream add SAHOOL_HEALTH    --subjects="sahool.health.>,sahool.metrics.>" --retention=limits --max-age=24h --storage=memory -f 2>$null
nats stream add SAHOOL_AUDIT     --subjects="sahool.audit.>"    --retention=limits    --max-age=7y   --storage=file   --deny-delete -f 2>$null

Write-Host "✅ Event Bus ready" -ForegroundColor Green
