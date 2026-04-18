"""
SAHOOL Unified Service Ports Registry (Python mirror)
=====================================================

Python mirror of::

    packages/shared-types/src/contracts/service-ports.ts

The TypeScript file is the SINGLE SOURCE OF TRUTH for all microservice
ports. This module is seed scaffolding that re-declares the
``SERVICE_PORTS`` record as a frozen dataclass so Python services can
import ports without hard-coding them.

DO NOT edit by hand — regenerate via ``scripts/sync-contracts-to-python.ts``
(not yet implemented). When adding a new service, update the TS file
first, then regenerate this file.

This module is a seed only and is not wired into any service yet.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ServicePorts:
    """Frozen dataclass mirroring the TS ``SERVICE_PORTS`` record."""

    # ── Core Services ────────────────────────────────────────────────────
    FIELD_MANAGEMENT: int = 3000
    USER_SERVICE: int = 3025
    PARTNER_AUTH: int = 3030
    MARKETPLACE: int = 3010
    RESEARCH_CORE: int = 3015
    DISASTER_ASSESSMENT: int = 3020

    # ── Intelligence Layer ───────────────────────────────────────────────
    VEGETATION_ANALYSIS: int = 8090
    INDICATORS: int = 8091
    WEATHER: int = 8092
    ADVISORY: int = 8093
    IRRIGATION_SMART: int = 8094
    CROP_INTELLIGENCE: int = 8095
    NDVI_PROCESSOR: int = 8118  # deprecated: use VEGETATION_ANALYSIS
    VIRTUAL_SENSORS: int = 8119
    FIELD_INTELLIGENCE: int = 8120
    SKILLS_SERVICE: int = 8121
    LAI_ESTIMATION: int = 3022
    CROP_GROWTH_MODEL: int = 3023

    # ── Decision Layer ───────────────────────────────────────────────────
    YIELD_PREDICTION: int = 8152
    YIELD_ENGINE: int = 8098
    YIELD_PREDICTION_LEGACY: int = 3021  # deprecated

    # ── Business Layer ───────────────────────────────────────────────────
    TASK_SERVICE: int = 8103
    EQUIPMENT: int = 8101
    NOTIFICATIONS: int = 8110
    ALERT_SERVICE: int = 8113
    AUDIT_SERVICE: int = 8114
    BILLING_CORE: int = 8089
    PROVIDER_CONFIG: int = 8104
    INVENTORY: int = 8116

    # ── Communication ────────────────────────────────────────────────────
    WS_GATEWAY: int = 8081
    CHAT_SERVICE: int = 8115
    FIELD_CHAT: int = 8099
    COMMUNITY_CHAT: int = 8097  # deprecated: use CHAT_SERVICE

    # ── IoT & Sensors ───────────────────────────────────────────────────
    IOT_SERVICE: int = 8117
    IOT_GATEWAY: int = 8106
    IOT_SENSOR_HUB: int = 8251

    # ── AI & Agents ──────────────────────────────────────────────────────
    COPILOT_API: int = 8088
    AI_ADVISOR: int = 8112
    AI_AGENTS_CORE: int = 8161
    AI_AGENTS_SERVICE: int = 8130
    AI_CHAT_ASSISTANT: int = 8260
    AGENT_REGISTRY: int = 8160
    LLM_ORCHESTRATOR: int = 8164
    KNOWLEDGE_GRAPH: int = 8140
    CODE_FIX_AGENT: int = 8162
    CODE_REVIEW_SERVICE: int = 8102

    # ── Vision & Terrain ─────────────────────────────────────────────────
    YOLO_VISION: int = 8150
    GROUND_VISION: int = 8182
    TERRAIN_CORE: int = 8185
    HYDROLOGY: int = 8165
    LEVELING_OPTIMIZER: int = 8170
    EDGE_ORCHESTRATOR: int = 8180
    VLLM_DEEPSEEK: int = 8270

    # ── Agriculture Domain ───────────────────────────────────────────────
    SOIL_ANALYSIS: int = 8134
    PEST_DETECTION: int = 8125
    DRONE_SERVICE: int = 8126
    COOPERATIVE: int = 8127
    GLOBALGAP: int = 8128
    TRACEABILITY: int = 8123
    CRM_SERVICE: int = 8131
    ASTRONOMICAL_CALENDAR: int = 8111

    # ── Specialized ──────────────────────────────────────────────────────
    LOGISTICS: int = 8167
    SUPPLY_CHAIN: int = 8230
    LOWCODE_ENGINE: int = 8132
    COMMUNITY: int = 8133
    WECHAT: int = 8135  # deprecated
    WHATSAPP_BOT: int = 8240
    USSD_GATEWAY: int = 8183
    FERTIGATION_ENGINE: int = 8252
    IRRIGATION_CYCLE_ENGINE: int = 8250
    DIGITAL_TWIN: int = 8253
    MCP_SERVER: int = 8201
    CARBON_SERVICE: int = 8195

    # ── Applications ─────────────────────────────────────────────────────
    ADMIN: int = 3001
    WEB: int = 3002

    # ── Infrastructure ───────────────────────────────────────────────────
    KONG_GATEWAY: int = 8000
    KONG_ADMIN: int = 8001
    NATS: int = 4222
    NATS_MONITOR: int = 8222
    POSTGRES: int = 5432
    PGBOUNCER: int = 6432
    REDIS: int = 6379


#: Module-level singleton for convenient imports, e.g.
#: ``from shared.contracts_py import SERVICE_PORTS``.
SERVICE_PORTS: ServicePorts = ServicePorts()
