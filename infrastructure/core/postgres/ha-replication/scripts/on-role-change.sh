#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Patroni Role Change Callback
# سكريبت استدعاء عند تغيير دور العقدة
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Handles PostgreSQL role changes (primary/replica promotion/demotion)
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

ACTION="$1"  # 'on_start', 'on_stop', 'on_restart', 'on_role_change'
ROLE="$2"    # 'master' or 'replica'
CLUSTER="$3" # Cluster name

# Logging
LOG_FILE="/var/log/postgresql/patroni-callbacks.log"
mkdir -p "$(dirname "${LOG_FILE}")"

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] [${ACTION}] [${ROLE}] $*" >> "${LOG_FILE}"
}

log "Role change detected: ${ACTION} -> ${ROLE} in cluster ${CLUSTER}"

# Notification function
send_notification() {
    local message="$1"
    local severity="${2:-info}"

    # Send to monitoring system (Prometheus Pushgateway)
    if command -v curl >/dev/null 2>&1 && [ -n "${PUSHGATEWAY_URL:-}" ]; then
        cat <<EOF | curl --data-binary @- "${PUSHGATEWAY_URL}/metrics/job/patroni/instance/$(hostname)" >/dev/null 2>&1 || true
# TYPE patroni_role_change gauge
patroni_role_change{action="${ACTION}",role="${ROLE}",cluster="${CLUSTER}"} 1
EOF
    fi

    # Send Slack notification for critical events
    if [ "${SLACK_WEBHOOK_URL:-}" ] && [ "$severity" = "critical" ]; then
        curl -X POST "${SLACK_WEBHOOK_URL}" \
            -H 'Content-Type: application/json' \
            -d @- >/dev/null 2>&1 <<EOF || true
{
    "attachments": [{
        "color": "warning",
        "title": "🔄 PostgreSQL Role Change",
        "text": "${message}",
        "fields": [
            {"title": "Action", "value": "${ACTION}", "short": true},
            {"title": "New Role", "value": "${ROLE}", "short": true},
            {"title": "Cluster", "value": "${CLUSTER}", "short": true},
            {"title": "Node", "value": "$(hostname)", "short": true}
        ],
        "footer": "SAHOOL Platform - PostgreSQL HA",
        "ts": $(date +%s)
    }]
}
EOF
    fi
}

# Handle role-specific actions
case "$ROLE" in
    master)
        log "This node is now the PRIMARY (master)"
        send_notification "Node $(hostname) promoted to PRIMARY in cluster ${CLUSTER}" "critical"

        # Ensure proper permissions
        chmod 700 /var/lib/postgresql/data || true

        # Update application connection strings (if using config service)
        if [ -n "${CONFIG_SERVICE_URL:-}" ]; then
            curl -X POST "${CONFIG_SERVICE_URL}/postgres/primary" \
                -d "host=$(hostname)" >/dev/null 2>&1 || true
        fi
        ;;

    replica)
        log "This node is now a REPLICA (standby)"
        send_notification "Node $(hostname) is now REPLICA in cluster ${CLUSTER}" "info"
        ;;

    *)
        log "Unknown role: ${ROLE}"
        ;;
esac

log "Role change handling completed successfully"
exit 0
