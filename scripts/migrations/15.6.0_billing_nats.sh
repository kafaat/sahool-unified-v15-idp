#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Migration: 15.6.0 - Billing NATS Integration
# ترحيل: إضافة تكامل NATS مع خدمة الفوترة
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "Running migration 15.6.0: Billing NATS Integration"

# Create NATS stream for billing events
if docker ps | grep -q sahool-nats; then
    echo "Creating BILLING stream in NATS JetStream..."
    docker exec sahool-nats nats stream add BILLING \
        --subjects "sahool.billing.*,sahool.payment.*,sahool.subscription.*" \
        --retention limits \
        --max-age 30d \
        --storage file \
        --replicas 1 \
        --discard old \
        2>/dev/null || echo "Stream already exists or NATS CLI not available"
fi

# Verify billing-core has NATS_URL
if grep -q "NATS_URL" docker-compose.yml; then
    echo "NATS_URL configuration found in billing_core"
else
    echo "WARNING: NATS_URL not found in billing_core configuration"
fi

echo "Migration 15.6.0 completed"
