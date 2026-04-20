"""
Shared service registry constants for all container tests.
سجل الخدمات المشترك لجميع اختبارات الحاويات

Centralises the authoritative port → service-name mapping so that
test_build.py, test_container_smoke.py, and any future container test
modules import from one place instead of maintaining separate copies.

When adding, renaming, or removing a service:
  1. Update PYTHON_SERVICES or NODE_SERVICES below.
  2. All container tests automatically pick up the change.

Source of truth: governance/services.yaml
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Python / FastAPI services  (service-name → canonical container port)
# ---------------------------------------------------------------------------

PYTHON_SERVICES: dict[str, int] = {
    "advisory-service": 8093,
    "agent-registry": 8160,
    "ai-advisor": 8112,
    "ai-agents-core": 8161,
    "ai-agents-service": 8130,
    "ai-chat-assistant": 8260,
    "alert-service": 8113,
    "astronomical-calendar": 8111,
    "audit-service": 8114,
    "billing-core": 8089,
    "code-fix-agent": 8162,
    "code-review-service": 8102,
    "community-service": 8133,
    "cooperative-service": 8127,
    "copilot-api": 8088,
    "crm-service": 8131,
    "crop-intelligence-service": 8095,
    "digital-twin-engine": 8253,
    "drone-service": 8126,
    "edge-orchestrator-service": 8180,
    "equipment-service": 8101,
    "fertigation-engine": 8252,
    "field-intelligence": 8120,
    "globalgap-compliance": 8128,
    "ground-vision-service": 8182,
    "hydrology-service": 8165,
    "indicators-service": 8091,
    "inventory-service": 8116,
    "iot-gateway": 8106,
    "iot-sensor-hub": 8251,
    "irrigation-cycle-engine": 8250,
    "irrigation-smart": 8094,
    "knowledge-graph": 8140,
    "leveling-optimizer-service": 8170,
    "llm-orchestrator-service": 8164,
    "logistics-service": 8167,
    "lowcode-engine": 8132,
    "mcp-server": 8201,
    "ndvi-processor": 8118,
    "notification-service": 8110,
    "pest-detection-service": 8125,
    "provider-config": 8104,
    "skills-service": 8121,
    "soil-analysis-service": 8134,
    "supply-chain-service": 8230,
    "task-service": 8103,
    "terrain-core-service": 8185,
    "traceability-service": 8123,
    "ussd-gateway": 8183,
    "vegetation-analysis-service": 8090,
    "virtual-sensors": 8119,
    "weather-service": 8092,
    "whatsapp-bot-service": 8240,
    "ws-gateway": 8081,
    "yolo26-vision-service": 8150,
}

# ---------------------------------------------------------------------------
# Node.js / NestJS services  (service-name → canonical container port)
# ---------------------------------------------------------------------------

NODE_SERVICES: dict[str, int] = {
    "chat-service": 8115,
    "crop-growth-model": 3023,
    "disaster-assessment": 3020,
    "field-management-service": 3000,
    "iot-service": 8117,
    "lai-estimation": 3022,
    "marketplace-service": 3010,
    "partner-auth-service": 3030,
    "research-core": 3015,
    "user-service": 3025,
    "yield-prediction": 3021,
    "yield-prediction-service": 8152,
}

# ---------------------------------------------------------------------------
# Portless workers / init containers – have Dockerfiles but no HTTP port
# ---------------------------------------------------------------------------

PORTLESS_SERVICES: set[str] = {"agro-rules", "code-review-agent", "demo-data"}

# ---------------------------------------------------------------------------
# Deprecated / archived services – kept for reference, not started by default
# ---------------------------------------------------------------------------

DEPRECATED_SERVICES: dict[str, int] = {
    "wechat-service": 8135,  # replaced by community-service (2026-03-13)
}

# ---------------------------------------------------------------------------
# Infrastructure / supporting services (image-based, not built from src)
# ---------------------------------------------------------------------------

INFRA_SERVICES: set[str] = {
    "postgres",
    "pgbouncer",
    "redis",
    "nats",
    "kong",
    "vault",
    "qdrant",
    "milvus",
    "minio",
    "mqtt",
    "ollama",
    "mlflow",
    "etcd",
    "etcd-perms-init",
    "nats-prometheus-exporter",
}

# ---------------------------------------------------------------------------
# Derived convenience collections
# ---------------------------------------------------------------------------

#: All services that are built from source and have an HTTP endpoint.
ALL_HTTP_SERVICES: dict[str, int] = {**PYTHON_SERVICES, **NODE_SERVICES}

#: All services that are built from source (HTTP + portless workers).
ALL_BUILT_SERVICES: dict[str, int | None] = {
    **PYTHON_SERVICES,
    **NODE_SERVICES,
    **dict.fromkeys(PORTLESS_SERVICES),
}
