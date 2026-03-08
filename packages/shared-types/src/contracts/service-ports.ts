/**
 * SAHOOL Unified Service Ports Registry
 * مصدر الحقيقة الوحيد لمنافذ الخدمات
 *
 * Single source of truth for all microservice ports.
 * Used by: Web, Admin, Mobile, api-client, Kong Gateway, Helm charts.
 *
 * @module @sahool/shared-types/contracts
 * @version 16.0.0
 */

// ---------------------------------------------------------------------------
// Service Port Constants - ثوابت المنافذ
// ---------------------------------------------------------------------------

/** Core application services - الخدمات الأساسية */
export const SERVICE_PORTS = {
  // ── Core Services ────────────────────────────────────────────────────
  /** Field management (consolidated) - إدارة الحقول */
  FIELD_MANAGEMENT: 3000,
  /** User authentication & management - المصادقة وإدارة المستخدمين */
  USER_SERVICE: 3025,
  /** Marketplace service - خدمة السوق */
  MARKETPLACE: 3010,
  /** Research trials - التجارب البحثية */
  RESEARCH_CORE: 3015,
  /** Disaster risk assessment - تقييم مخاطر الكوارث */
  DISASTER_ASSESSMENT: 3020,

  // ── Intelligence Layer ───────────────────────────────────────────────
  /** Satellite imagery & NDVI - صور الأقمار الصناعية */
  VEGETATION_ANALYSIS: 8090,
  /** Field indicators computation - حساب المؤشرات */
  INDICATORS: 8091,
  /** Weather data & forecasts - بيانات الطقس */
  WEATHER: 8092,
  /** Advisory & fertilizer recommendations - الاستشارات والتسميد */
  ADVISORY: 8093,
  /** Smart irrigation scheduling - الري الذكي */
  IRRIGATION_SMART: 8094,
  /** Crop health AI / disease detection - صحة المحاصيل */
  CROP_INTELLIGENCE: 8095,
  /** NDVI processing - معالجة NDVI */
  NDVI_PROCESSOR: 8118,
  /** Virtual sensor computation (ET0, ETC) - أجهزة الاستشعار الافتراضية */
  VIRTUAL_SENSORS: 8119,
  /** Field analytics - تحليلات الحقل */
  FIELD_INTELLIGENCE: 8120,
  /** Farmer skills assessment - تقييم مهارات المزارع */
  SKILLS_SERVICE: 8121,
  /** LAI estimation - تقدير مساحة الأوراق */
  LAI_ESTIMATION: 3022,
  /** Crop growth simulation - محاكاة نمو المحاصيل */
  CROP_GROWTH_MODEL: 3023,

  // ── Decision Layer ───────────────────────────────────────────────────
  /** Yield prediction (NestJS) - التنبؤ بالإنتاجية */
  YIELD_PREDICTION: 8152,
  /** Yield engine (legacy) - محرك الإنتاجية */
  YIELD_ENGINE: 8098,

  // ── Business Layer ───────────────────────────────────────────────────
  /** Task management - إدارة المهام */
  TASK_SERVICE: 8103,
  /** Equipment tracking - تتبع المعدات */
  EQUIPMENT: 8101,
  /** Notification service - خدمة الإشعارات */
  NOTIFICATIONS: 8110,
  /** Alert management - إدارة التنبيهات */
  ALERT_SERVICE: 8113,
  /** Audit logging - سجل التدقيق */
  AUDIT_SERVICE: 8114,
  /** Billing & invoicing - الفوترة */
  BILLING_CORE: 8089,
  /** Provider configuration - تكوين المزودين */
  PROVIDER_CONFIG: 8104,
  /** Inventory management - إدارة المخزون */
  INVENTORY: 8116,

  // ── Communication ────────────────────────────────────────────────────
  /** WebSocket gateway - بوابة WebSocket */
  WS_GATEWAY: 8081,
  /** Real-time messaging - الرسائل الفورية */
  CHAT_SERVICE: 8115,
  /** Field-level chat - دردشة الحقل */
  FIELD_CHAT: 8099,
  /** Community features (deprecated → chat-service) */
  COMMUNITY_CHAT: 8097,

  // ── IoT & Sensors ───────────────────────────────────────────────────
  /** IoT device management - إدارة أجهزة إنترنت الأشياء */
  IOT_SERVICE: 8117,
  /** IoT protocol gateway - بوابة بروتوكولات IoT */
  IOT_GATEWAY: 8106,
  /** IoT sensor hub - مركز الاستشعار */
  IOT_SENSOR_HUB: 8251,

  // ── AI & Agents ──────────────────────────────────────────────────────
  /** AI copilot (multi-LLM, RAG) - المساعد الذكي */
  COPILOT_API: 8088,
  /** AI advisory service - خدمة الاستشارات الذكية */
  AI_ADVISOR: 8112,
  /** AI agents core module - وحدة الوكلاء الذكية */
  AI_AGENTS_CORE: 8161,
  /** AI agents service - خدمة الوكلاء */
  AI_AGENTS_SERVICE: 8130,
  /** AI chat assistant - مساعد الدردشة الذكي */
  AI_CHAT_ASSISTANT: 8260,
  /** Agent registry - سجل الوكلاء */
  AGENT_REGISTRY: 8160,
  /** LLM orchestration - تنسيق نماذج اللغة */
  LLM_ORCHESTRATOR: 8164,
  /** Knowledge graph - الرسم البياني المعرفي */
  KNOWLEDGE_GRAPH: 8140,
  /** Code fix agent - وكيل إصلاح الكود */
  CODE_FIX_AGENT: 8162,
  /** Code review service - خدمة مراجعة الكود */
  CODE_REVIEW_SERVICE: 8102,

  // ── Vision & Terrain ─────────────────────────────────────────────────
  /** YOLO26 computer vision - الرؤية الحاسوبية */
  YOLO_VISION: 8150,
  /** Ground-level vision - رؤية مستوى الأرض */
  GROUND_VISION: 8182,
  /** Terrain analysis - تحليل التضاريس */
  TERRAIN_CORE: 8185,
  /** Hydrology analysis - تحليل المياه */
  HYDROLOGY: 8165,
  /** Field leveling optimization - تحسين تسوية الحقول */
  LEVELING_OPTIMIZER: 8170,
  /** Edge device management - إدارة الأجهزة الطرفية */
  EDGE_ORCHESTRATOR: 8180,
  /** vLLM DeepSeek inference server - خادم استدلال vLLM ديب سيك */
  VLLM_DEEPSEEK: 8270,

  // ── Agriculture Domain ───────────────────────────────────────────────
  /** Soil analysis - تحليل التربة */
  SOIL_ANALYSIS: 8134,
  /** Pest detection AI - كشف الآفات */
  PEST_DETECTION: 8125,
  /** Drone integration - تكامل الطائرات بدون طيار */
  DRONE_SERVICE: 8126,
  /** Cooperative management - إدارة التعاونيات */
  COOPERATIVE: 8127,
  /** GlobalGAP compliance - الامتثال لمعايير جلوبال جاب */
  GLOBALGAP: 8128,
  /** Product traceability - التتبع */
  TRACEABILITY: 8123,
  /** Farmer CRM - إدارة علاقات المزارعين */
  CRM_SERVICE: 8131,
  /** Astronomical / Islamic calendar - التقويم الفلكي */
  ASTRONOMICAL_CALENDAR: 8111,

  // ── Specialized ──────────────────────────────────────────────────────
  /** Logistics management - إدارة اللوجستيات */
  LOGISTICS: 8167,
  /** Supply chain management - إدارة سلسلة التوريد */
  SUPPLY_CHAIN: 8230,
  /** Low-code workflow automation - أتمتة بدون كود */
  LOWCODE_ENGINE: 8132,
  /** WeChat integration - تكامل وي شات */
  WECHAT: 8133,
  /** WhatsApp bot - بوت واتساب */
  WHATSAPP_BOT: 8240,
  /** USSD gateway - بوابة USSD */
  USSD_GATEWAY: 8183,
  /** Fertigation engine - محرك التسميد بالري */
  FERTIGATION_ENGINE: 8252,
  /** Irrigation cycle optimization - تحسين دورات الري */
  IRRIGATION_CYCLE_ENGINE: 8250,
  /** Digital twin simulation - المحاكاة الرقمية */
  DIGITAL_TWIN: 8253,
  /** MCP server - خادم MCP (changed from 8200 to avoid Vault conflict) */
  MCP_SERVER: 8201,

  // ── Applications ─────────────────────────────────────────────────────
  /** Admin portal - لوحة الإدارة */
  ADMIN: 3001,
  /** Web dashboard - لوحة القيادة */
  WEB: 3002,

  // ── Infrastructure ───────────────────────────────────────────────────
  /** Kong API Gateway - بوابة API */
  KONG_GATEWAY: 8000,
  /** Kong Admin API */
  KONG_ADMIN: 8001,
  /** NATS message queue - قائمة الرسائل */
  NATS: 4222,
  /** NATS monitoring */
  NATS_MONITOR: 8222,
  /** PostgreSQL database - قاعدة البيانات */
  POSTGRES: 5432,
  /** PgBouncer connection pool */
  PGBOUNCER: 6432,
  /** Redis cache - ذاكرة التخزين المؤقت */
  REDIS: 6379,
} as const;

export type ServicePortKey = keyof typeof SERVICE_PORTS;
export type ServicePort = (typeof SERVICE_PORTS)[ServicePortKey];

// ---------------------------------------------------------------------------
// Service Metadata - بيانات وصفية للخدمات
// ---------------------------------------------------------------------------

export interface ServiceInfo {
  /** Internal service key */
  key: ServicePortKey;
  /** Service port */
  port: number;
  /** Service display name (EN) */
  name: string;
  /** Service display name (AR) */
  nameAr: string;
  /** Kong route prefix */
  kongRoute: string;
  /** Runtime type */
  type: "python" | "nodejs" | "infrastructure";
  /** Event architecture layer */
  layer: "core" | "acquisition" | "intelligence" | "decision" | "business";
  /** Is deprecated */
  deprecated?: boolean;
  /** Replacement service key (if deprecated) */
  replacedBy?: ServicePortKey;
}

/**
 * Complete service registry with metadata.
 * Used for service discovery, health checks, and documentation.
 */
export const SERVICE_REGISTRY: Record<string, ServiceInfo> = {
  "field-management": {
    key: "FIELD_MANAGEMENT",
    port: SERVICE_PORTS.FIELD_MANAGEMENT,
    name: "Field Management",
    nameAr: "إدارة الحقول",
    kongRoute: "/api/v1/fields",
    type: "nodejs",
    layer: "core",
  },
  "user-service": {
    key: "USER_SERVICE",
    port: SERVICE_PORTS.USER_SERVICE,
    name: "User Service",
    nameAr: "خدمة المستخدمين",
    kongRoute: "/api/v1/auth",
    type: "nodejs",
    layer: "core",
  },
  "weather-service": {
    key: "WEATHER",
    port: SERVICE_PORTS.WEATHER,
    name: "Weather Service",
    nameAr: "خدمة الطقس",
    kongRoute: "/api/v1/weather",
    type: "python",
    layer: "acquisition",
  },
  "vegetation-analysis": {
    key: "VEGETATION_ANALYSIS",
    port: SERVICE_PORTS.VEGETATION_ANALYSIS,
    name: "Vegetation Analysis",
    nameAr: "تحليل الغطاء النباتي",
    kongRoute: "/api/v1/satellite",
    type: "python",
    layer: "intelligence",
  },
  "crop-intelligence": {
    key: "CROP_INTELLIGENCE",
    port: SERVICE_PORTS.CROP_INTELLIGENCE,
    name: "Crop Intelligence",
    nameAr: "ذكاء المحاصيل",
    kongRoute: "/api/v1/crop-health",
    type: "python",
    layer: "intelligence",
  },
  "advisory-service": {
    key: "ADVISORY",
    port: SERVICE_PORTS.ADVISORY,
    name: "Advisory Service",
    nameAr: "خدمة الاستشارات",
    kongRoute: "/api/v1/advisory",
    type: "python",
    layer: "decision",
  },
  "irrigation-smart": {
    key: "IRRIGATION_SMART",
    port: SERVICE_PORTS.IRRIGATION_SMART,
    name: "Smart Irrigation",
    nameAr: "الري الذكي",
    kongRoute: "/api/v1/irrigation",
    type: "python",
    layer: "decision",
  },
  "task-service": {
    key: "TASK_SERVICE",
    port: SERVICE_PORTS.TASK_SERVICE,
    name: "Task Service",
    nameAr: "خدمة المهام",
    kongRoute: "/api/v1/tasks",
    type: "python",
    layer: "business",
  },
  "equipment-service": {
    key: "EQUIPMENT",
    port: SERVICE_PORTS.EQUIPMENT,
    name: "Equipment Service",
    nameAr: "خدمة المعدات",
    kongRoute: "/api/v1/equipment",
    type: "python",
    layer: "business",
  },
  "notification-service": {
    key: "NOTIFICATIONS",
    port: SERVICE_PORTS.NOTIFICATIONS,
    name: "Notification Service",
    nameAr: "خدمة الإشعارات",
    kongRoute: "/api/v1/notifications",
    type: "python",
    layer: "business",
  },
  "alert-service": {
    key: "ALERT_SERVICE",
    port: SERVICE_PORTS.ALERT_SERVICE,
    name: "Alert Service",
    nameAr: "خدمة التنبيهات",
    kongRoute: "/api/v1/alerts",
    type: "python",
    layer: "business",
  },
  "billing-core": {
    key: "BILLING_CORE",
    port: SERVICE_PORTS.BILLING_CORE,
    name: "Billing Core",
    nameAr: "الفوترة",
    kongRoute: "/api/v1/billing",
    type: "python",
    layer: "business",
  },
  "marketplace-service": {
    key: "MARKETPLACE",
    port: SERVICE_PORTS.MARKETPLACE,
    name: "Marketplace",
    nameAr: "السوق",
    kongRoute: "/api/v1/marketplace",
    type: "nodejs",
    layer: "business",
  },
  "chat-service": {
    key: "CHAT_SERVICE",
    port: SERVICE_PORTS.CHAT_SERVICE,
    name: "Chat Service",
    nameAr: "خدمة الدردشة",
    kongRoute: "/api/v1/chat",
    type: "nodejs",
    layer: "business",
  },
  "iot-service": {
    key: "IOT_SERVICE",
    port: SERVICE_PORTS.IOT_SERVICE,
    name: "IoT Service",
    nameAr: "خدمة إنترنت الأشياء",
    kongRoute: "/api/v1/iot",
    type: "nodejs",
    layer: "acquisition",
  },
  "copilot-api": {
    key: "COPILOT_API",
    port: SERVICE_PORTS.COPILOT_API,
    name: "Copilot API",
    nameAr: "المساعد الذكي",
    kongRoute: "/api/v1/copilot",
    type: "python",
    layer: "intelligence",
  },
  "yolo-vision": {
    key: "YOLO_VISION",
    port: SERVICE_PORTS.YOLO_VISION,
    name: "YOLO Vision Service",
    nameAr: "خدمة الرؤية الحاسوبية",
    kongRoute: "/api/v1/vision",
    type: "python",
    layer: "intelligence",
  },
  "terrain-core": {
    key: "TERRAIN_CORE",
    port: SERVICE_PORTS.TERRAIN_CORE,
    name: "Terrain Core",
    nameAr: "تحليل التضاريس",
    kongRoute: "/api/v1/terrain",
    type: "python",
    layer: "intelligence",
  },
  "crm-service": {
    key: "CRM_SERVICE",
    port: SERVICE_PORTS.CRM_SERVICE,
    name: "CRM Service",
    nameAr: "إدارة علاقات المزارعين",
    kongRoute: "/api/v1/crm",
    type: "python",
    layer: "business",
  },
  "community-chat": {
    key: "COMMUNITY_CHAT",
    port: SERVICE_PORTS.COMMUNITY_CHAT,
    name: "Community Chat",
    nameAr: "دردشة المجتمع",
    kongRoute: "/api/v1/community",
    type: "nodejs",
    layer: "business",
    deprecated: true,
    replacedBy: "CHAT_SERVICE",
  },
  "vllm-deepseek": {
    key: "VLLM_DEEPSEEK",
    port: SERVICE_PORTS.VLLM_DEEPSEEK,
    name: "vLLM DeepSeek Inference Server",
    nameAr: "خادم استدلال vLLM ديب سيك",
    kongRoute: "/api/v1/llm",
    type: "python",
    layer: "intelligence",
  },
};

// ---------------------------------------------------------------------------
// Backward-compatible aliases - أسماء مستعارة للتوافق
// ---------------------------------------------------------------------------

/**
 * Aliases for service ports used in legacy code.
 * Maps old names → canonical SERVICE_PORTS keys.
 *
 * @deprecated Use SERVICE_PORTS directly
 */
export const SERVICE_PORT_ALIASES = {
  /** @deprecated Admin uses 8080 for auth → use SERVICE_PORTS.USER_SERVICE (3025) via Kong */
  auth: SERVICE_PORTS.USER_SERVICE,
  fieldCore: SERVICE_PORTS.FIELD_MANAGEMENT,
  satellite: SERVICE_PORTS.VEGETATION_ANALYSIS,
  indicators: SERVICE_PORTS.INDICATORS,
  weather: SERVICE_PORTS.WEATHER,
  fertilizer: SERVICE_PORTS.ADVISORY,
  irrigation: SERVICE_PORTS.IRRIGATION_SMART,
  cropHealth: SERVICE_PORTS.CROP_INTELLIGENCE,
  virtualSensors: SERVICE_PORTS.VIRTUAL_SENSORS,
  communityChat: SERVICE_PORTS.COMMUNITY_CHAT,
  community: SERVICE_PORTS.COMMUNITY_CHAT,
  yieldEngine: SERVICE_PORTS.YIELD_ENGINE,
  equipment: SERVICE_PORTS.EQUIPMENT,
  task: SERVICE_PORTS.TASK_SERVICE,
  providerConfig: SERVICE_PORTS.PROVIDER_CONFIG,
  notifications: SERVICE_PORTS.NOTIFICATIONS,
  wsGateway: SERVICE_PORTS.WS_GATEWAY,
  marketplace: SERVICE_PORTS.MARKETPLACE,
  soilAnalysis: SERVICE_PORTS.SOIL_ANALYSIS,
  drone: SERVICE_PORTS.DRONE_SERVICE,
  cooperative: SERVICE_PORTS.COOPERATIVE,
  traceability: SERVICE_PORTS.TRACEABILITY,
  billing: SERVICE_PORTS.BILLING_CORE,
  alerts: SERVICE_PORTS.ALERT_SERVICE,
  inventory: SERVICE_PORTS.INVENTORY,
  copilot: SERVICE_PORTS.COPILOT_API,
  aiAdvisor: SERVICE_PORTS.AI_ADVISOR,
  aiAgents: SERVICE_PORTS.AI_AGENTS_CORE,
  knowledgeGraph: SERVICE_PORTS.KNOWLEDGE_GRAPH,
  yoloVision: SERVICE_PORTS.YOLO_VISION,
  terrainCore: SERVICE_PORTS.TERRAIN_CORE,
  hydrology: SERVICE_PORTS.HYDROLOGY,
  levelingOptimizer: SERVICE_PORTS.LEVELING_OPTIMIZER,
  edgeOrchestrator: SERVICE_PORTS.EDGE_ORCHESTRATOR,
  vllmDeepseek: SERVICE_PORTS.VLLM_DEEPSEEK,
} as const;

// ---------------------------------------------------------------------------
// Helper Functions - دوال مساعدة
// ---------------------------------------------------------------------------

/**
 * Get the full service URL for a given port and optional base host.
 * @param port - Service port from SERVICE_PORTS
 * @param host - Base host (default: "localhost")
 * @param protocol - Protocol (default: "http")
 */
export function getServiceUrl(
  port: number,
  host: string = "localhost",
  protocol: string = "http",
): string {
  return `${protocol}://${host}:${port}`;
}

/**
 * Get all service URLs for a given host.
 */
export function getAllServiceUrls(
  host: string = "localhost",
  protocol: string = "http",
): Record<ServicePortKey, string> {
  const urls = {} as Record<ServicePortKey, string>;
  for (const [key, port] of Object.entries(SERVICE_PORTS)) {
    urls[key as ServicePortKey] = `${protocol}://${host}:${port}`;
  }
  return urls;
}
