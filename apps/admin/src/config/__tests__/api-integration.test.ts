/**
 * API Integration Tests
 * اختبارات تكامل API
 *
 * Verifies the API configuration works correctly for routing requests
 * to the right services. Tests environment detection, URL generation,
 * port mapping, path resolution, and cross-service consistency.
 *
 * @module config/__tests__/api-integration
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

// ---------------------------------------------------------------------------
// Mock @sahool/shared-types/contracts
// ---------------------------------------------------------------------------

vi.mock('@sahool/shared-types/contracts', () => ({
  SERVICE_PORTS: {
    FIELD_MANAGEMENT: 3000,
    USER_SERVICE: 3025,
    MARKETPLACE: 3010,
    RESEARCH_CORE: 3015,
    DISASTER_ASSESSMENT: 3020,
    VEGETATION_ANALYSIS: 8090,
    INDICATORS: 8091,
    WEATHER: 8092,
    ADVISORY: 8093,
    IRRIGATION_SMART: 8094,
    CROP_INTELLIGENCE: 8095,
    NDVI_PROCESSOR: 8118,
    VIRTUAL_SENSORS: 8119,
    FIELD_INTELLIGENCE: 8120,
    SKILLS_SERVICE: 8121,
    LAI_ESTIMATION: 3022,
    CROP_GROWTH_MODEL: 3023,
    YIELD_PREDICTION: 8152,
    TASK_SERVICE: 8103,
    EQUIPMENT: 8101,
    NOTIFICATIONS: 8110,
    ALERT_SERVICE: 8113,
    AUDIT_SERVICE: 8114,
    BILLING_CORE: 8089,
    PROVIDER_CONFIG: 8104,
    INVENTORY: 8116,
    WS_GATEWAY: 8081,
    CHAT_SERVICE: 8115,
    FIELD_CHAT: 8099,
    COMMUNITY_CHAT: 8097,
    IOT_SERVICE: 8117,
    IOT_GATEWAY: 8106,
    COPILOT_API: 8088,
    AI_ADVISOR: 8112,
    AI_AGENTS_CORE: 8161,
    KNOWLEDGE_GRAPH: 8140,
    YOLO_VISION: 8150,
    TERRAIN_CORE: 8185,
    HYDROLOGY: 8165,
    LEVELING_OPTIMIZER: 8170,
    EDGE_ORCHESTRATOR: 8180,
    SOIL_ANALYSIS: 8134,
    PEST_DETECTION: 8125,
    DRONE_SERVICE: 8126,
    COOPERATIVE: 8127,
    GLOBALGAP: 8128,
    TRACEABILITY: 8123,
    CRM_SERVICE: 8131,
    ASTRONOMICAL_CALENDAR: 8111,
    LOGISTICS: 8167,
    SUPPLY_CHAIN: 8230,
    LOWCODE_ENGINE: 8132,
  },
  HEALTH_ENDPOINTS: {
    LIVENESS: '/healthz',
    READINESS: '/readyz',
    HEALTH: '/health',
    METRICS: '/metrics',
  },
  AUTH_ENDPOINTS: {
    LOGIN: '/api/v1/auth/login',
    LOGOUT: '/api/v1/auth/logout',
    REFRESH: '/api/v1/auth/refresh',
    ME: '/api/v1/auth/me',
    REGISTER: '/api/v1/auth/register',
    ACTIVITY: '/api/v1/auth/activity',
  },
  FIELD_ENDPOINTS: {
    LIST: '/api/v1/fields',
    GET: '/api/v1/fields/{fieldId}',
    CREATE: '/api/v1/fields',
    UPDATE: '/api/v1/fields/{fieldId}',
    DELETE: '/api/v1/fields/{fieldId}',
    NEARBY: '/api/v1/fields/nearby',
    SYNC: '/api/v1/fields/sync',
    SYNC_BATCH: '/api/v1/fields/sync/batch',
    BOUNDARY: '/api/v1/field-core/fields/{fieldId}/boundary',
    BOUNDARY_UPDATE: '/api/v1/field-core/fields/{fieldId}/boundary',
    BOUNDARY_HISTORY: '/api/v1/field-core/fields/{fieldId}/boundary-history',
    BOUNDARY_ROLLBACK: '/api/v1/field-core/fields/{fieldId}/boundary-history/rollback',
  },
  CROP_HEALTH_ENDPOINTS: {
    ANALYZE: '/api/v1/crop-health/analyze',
    DIAGNOSE: '/api/v1/crop-health/diagnose',
    DIAGNOSES_LIST: '/api/v1/crop-health/diagnoses',
    DIAGNOSES_STATS: '/api/v1/crop-health/diagnoses/stats',
    DIAGNOSES_UPDATE: '/api/v1/crop-health/diagnoses/{diagnosisId}',
  },
  IRRIGATION_ENDPOINTS: {
    SCHEDULES_LIST: '/api/v1/irrigation/schedules',
    RECOMMENDATIONS: '/api/v1/irrigation/recommendations',
    HISTORY: '/api/v1/irrigation/history/{fieldId}',
  },
  ADVISORY_ENDPOINTS: {
    RECOMMENDATIONS: '/api/v1/advisory/recommendations',
    FERTILIZER_ADVISORY: '/api/v1/advisory/fertilizer',
    FERTILIZER_CALCULATE: '/api/v1/advisory/fertilizer/calculate',
  },
  TASK_ENDPOINTS: {
    LIST: '/api/v1/tasks',
    GET: '/api/v1/tasks/{taskId}',
    CREATE: '/api/v1/tasks',
    UPDATE: '/api/v1/tasks/{taskId}',
    DELETE: '/api/v1/tasks/{taskId}',
  },
  EQUIPMENT_ENDPOINTS: {
    LIST: '/api/v1/equipment',
    GET: '/api/v1/equipment/{equipmentId}',
    MAINTENANCE: '/api/v1/equipment/{equipmentId}/maintenance',
  },
  NOTIFICATION_ENDPOINTS: {
    LIST: '/api/v1/notifications',
    GET: '/api/v1/notifications/{notificationId}',
    MARK_READ: '/api/v1/notifications/{notificationId}/read',
    MARK_ALL_READ: '/api/v1/notifications/read-all',
  },
  IOT_ENDPOINTS: {
    DEVICES: '/api/v1/iot/devices',
    DEVICE_GET: '/api/v1/iot/devices/{deviceId}',
    READINGS_BY_FARM: '/api/v1/iot/readings/{farmId}',
  },
  INDICATOR_ENDPOINTS: {
    DASHBOARD: '/api/v1/indicators/dashboard',
    SUMMARY: '/api/v1/indicators/summary',
    TRENDS: '/api/v1/indicators/trends',
  },
  BILLING_ENDPOINTS: {
    INVOICES: '/api/v1/billing/invoices',
    INVOICE_GET: '/api/v1/billing/invoices/{invoiceId}',
    SUBSCRIPTIONS: '/api/v1/billing/subscriptions',
    USAGE: '/api/v1/billing/usage',
  },
  AUDIT_ENDPOINTS: {
    LOGS: '/api/v1/audit/logs',
    LOG_GET: '/api/v1/audit/logs/{logId}',
    STATS: '/api/v1/audit/stats',
  },
  SOIL_ENDPOINTS: {
    TESTS: '/api/v1/soil/tests',
    TEST_GET: '/api/v1/soil/tests/{testId}',
    RECOMMENDATIONS: '/api/v1/soil/recommendations',
  },
  DRONE_ENDPOINTS: {
    FLIGHTS: '/api/v1/drone/flights',
    FLIGHT_GET: '/api/v1/drone/flights/{flightId}',
    FLIGHT_PLAN: '/api/v1/drone/flights/plan',
    DEVICES: '/api/v1/drone/devices',
  },
  INVENTORY_ENDPOINTS: {
    LIST: '/api/v1/inventory',
    GET: '/api/v1/inventory/{itemId}',
    STOCK_LEVELS: '/api/v1/inventory/stock-levels',
  },
  TRACEABILITY_ENDPOINTS: {
    BATCHES: '/api/v1/traceability/batches',
    BATCH_GET: '/api/v1/traceability/batches/{batchId}',
    EVENTS: '/api/v1/traceability/events',
    QR_CODE: '/api/v1/traceability/batches/{batchId}/qr',
  },
  TERRAIN_ENDPOINTS: {
    DEM: '/api/v1/terrain/dem',
    SLOPE: '/api/v1/terrain/slope',
    ASPECT: '/api/v1/terrain/aspect',
  },
  CHAT_ENDPOINTS: {
    COMMUNITY_POSTS: '/api/v1/posts',
    COMMUNITY_POST_GET: '/api/v1/posts/{postId}',
    COMMUNITY_COMMENTS: '/api/v1/posts/{postId}/comments',
  },
  YIELD_ENDPOINTS: {
    PREDICTIONS: '/api/v1/yield/predictions',
    HISTORY: '/api/v1/yield/fields/{fieldId}/history',
  },
  buildUrl: (template: string, params: Record<string, string>) => {
    let url = template;
    for (const [key, val] of Object.entries(params)) {
      url = url.replace(`{${key}}`, encodeURIComponent(val));
    }
    return url;
  },
}));

// ---------------------------------------------------------------------------
// Import the module under test AFTER mocking
// ---------------------------------------------------------------------------

import {
  IS_PRODUCTION,
  IS_DEVELOPMENT,
  IS_TEST,
  API_BASE_URL,
  getServiceUrl,
  SERVICE_PORTS,
  SERVICE_URLS,
  API_PATHS,
  API_URLS,
} from '@/config/api';

// ═══════════════════════════════════════════════════════════════════════════
// 1. Environment Detection Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Environment Detection', () => {
  it('IS_PRODUCTION is false in test environment', () => {
    expect(IS_PRODUCTION).toBe(false);
  });

  it('IS_DEVELOPMENT is false in test environment', () => {
    expect(IS_DEVELOPMENT).toBe(false);
  });

  it('IS_TEST is true in test environment', () => {
    expect(IS_TEST).toBe(true);
  });

  it('API_BASE_URL defaults to http://localhost:8000', () => {
    expect(API_BASE_URL).toBe('http://localhost:8000');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 2. getServiceUrl Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('getServiceUrl', () => {
  it('returns direct port URL in default test/dev mode (no gateway env)', () => {
    // In test mode (not production, no API_GATEWAY_URL), it falls through
    // to `${API_BASE_HOST}:${port}`
    const url = getServiceUrl(3000);
    expect(url).toMatch(/:\d+$/);
    expect(url).toContain('3000');
  });

  it('returns correct URL for various ports', () => {
    const url8092 = getServiceUrl(8092);
    expect(url8092).toContain('8092');

    const url3025 = getServiceUrl(3025);
    expect(url3025).toContain('3025');
  });

  it('returns API_GATEWAY_URL when env var is set (Docker mode)', () => {
    // Temporarily set API_GATEWAY_URL
    const originalGateway = process.env.API_GATEWAY_URL;
    process.env.API_GATEWAY_URL = 'http://kong:8000';

    // getServiceUrl reads process.env at call time
    const url = getServiceUrl(3000);
    expect(url).toBe('http://kong:8000');

    // Restore
    if (originalGateway === undefined) {
      delete process.env.API_GATEWAY_URL;
    } else {
      process.env.API_GATEWAY_URL = originalGateway;
    }
  });

  it('produces a valid URL format', () => {
    const url = getServiceUrl(8090);
    expect(url).toMatch(/^https?:\/\/.+/);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 3. SERVICE_PORTS Validation
// ═══════════════════════════════════════════════════════════════════════════

describe('SERVICE_PORTS', () => {
  it('fieldManagement port maps to FIELD_MANAGEMENT = 3000', () => {
    expect(SERVICE_PORTS.fieldManagement).toBe(3000);
  });

  it('auth port maps to USER_SERVICE = 3025', () => {
    expect(SERVICE_PORTS.auth).toBe(3025);
  });

  it('weather port maps to WEATHER = 8092', () => {
    expect(SERVICE_PORTS.weather).toBe(8092);
  });

  it('satellite port maps to VEGETATION_ANALYSIS = 8090', () => {
    expect(SERVICE_PORTS.satellite).toBe(8090);
  });

  it('indicators port maps to INDICATORS = 8091', () => {
    expect(SERVICE_PORTS.indicators).toBe(8091);
  });

  it('irrigation port maps to IRRIGATION_SMART = 8094', () => {
    expect(SERVICE_PORTS.irrigation).toBe(8094);
  });

  it('task port maps to TASK_SERVICE = 8103', () => {
    expect(SERVICE_PORTS.task).toBe(8103);
  });

  it('equipment port maps to EQUIPMENT = 8101', () => {
    expect(SERVICE_PORTS.equipment).toBe(8101);
  });

  it('notifications port maps to NOTIFICATIONS = 8110', () => {
    expect(SERVICE_PORTS.notifications).toBe(8110);
  });

  it('yoloVision port maps to YOLO_VISION = 8150', () => {
    expect(SERVICE_PORTS.yoloVision).toBe(8150);
  });

  it('terrainCore port maps to TERRAIN_CORE = 8185', () => {
    expect(SERVICE_PORTS.terrainCore).toBe(8185);
  });

  it('soilAnalysis port maps to SOIL_ANALYSIS = 8134', () => {
    expect(SERVICE_PORTS.soilAnalysis).toBe(8134);
  });

  it('all ports are positive numbers', () => {
    for (const [key, port] of Object.entries(SERVICE_PORTS)) {
      expect(typeof port).toBe('number');
      expect(port).toBeGreaterThan(0);
    }
  });

  it('all ports are within valid TCP port range', () => {
    for (const [key, port] of Object.entries(SERVICE_PORTS)) {
      expect(port).toBeGreaterThanOrEqual(1);
      expect(port).toBeLessThanOrEqual(65535);
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 4. API_PATHS Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('API_PATHS', () => {
  describe('fields', () => {
    it('list returns /api/v1/fields', () => {
      expect(API_PATHS.fields.list).toBe('/api/v1/fields');
    });

    it('create returns /api/v1/fields', () => {
      expect(API_PATHS.fields.create).toBe('/api/v1/fields');
    });

    it('byId returns parameterized path', () => {
      const path = API_PATHS.fields.byId('field-123');
      expect(path).toBe('/api/v1/fields/field-123');
    });

    it('update returns parameterized path', () => {
      const path = API_PATHS.fields.update('field-456');
      expect(path).toBe('/api/v1/fields/field-456');
    });

    it('delete returns parameterized path', () => {
      const path = API_PATHS.fields.delete('field-789');
      expect(path).toBe('/api/v1/fields/field-789');
    });
  });

  describe('weather', () => {
    it('current returns /weather/current', () => {
      expect(API_PATHS.weather.current).toBe('/weather/current');
    });

    it('forecast returns /weather/forecast', () => {
      expect(API_PATHS.weather.forecast).toBe('/weather/forecast');
    });

    it('agricultural returns /weather/agricultural-report', () => {
      expect(API_PATHS.weather.agricultural).toBe('/weather/agricultural-report');
    });

    it('alerts returns parameterized path with locationId', () => {
      const path = API_PATHS.weather.alerts('loc-001');
      expect(path).toBe('/weather/alerts/loc-001');
    });
  });

  describe('satellite', () => {
    it('timeseries returns correct path with fieldId', () => {
      const path = API_PATHS.satellite.timeseries('field-abc');
      expect(path).toBe('/v1/timeseries/field-abc');
    });

    it('analyze returns /v1/analyze', () => {
      expect(API_PATHS.satellite.analyze).toBe('/v1/analyze');
    });

    it('indices returns correct path with fieldId', () => {
      const path = API_PATHS.satellite.indices('field-xyz');
      expect(path).toBe('/v1/indices/field-xyz');
    });

    it('satellites returns /v1/satellites', () => {
      expect(API_PATHS.satellite.satellites).toBe('/v1/satellites');
    });
  });

  describe('health', () => {
    it('live returns /healthz', () => {
      expect(API_PATHS.health.live).toBe('/healthz');
    });

    it('ready returns /readyz', () => {
      expect(API_PATHS.health.ready).toBe('/readyz');
    });
  });

  describe('auth', () => {
    it('login returns /api/v1/auth/login', () => {
      expect(API_PATHS.auth.login).toBe('/api/v1/auth/login');
    });

    it('logout returns /api/v1/auth/logout', () => {
      expect(API_PATHS.auth.logout).toBe('/api/v1/auth/logout');
    });

    it('me returns /api/v1/auth/me', () => {
      expect(API_PATHS.auth.me).toBe('/api/v1/auth/me');
    });
  });

  describe('tasks', () => {
    it('list returns /api/v1/tasks', () => {
      expect(API_PATHS.tasks.list).toBe('/api/v1/tasks');
    });

    it('byId returns parameterized path', () => {
      const path = API_PATHS.tasks.byId('task-001');
      expect(path).toBe('/api/v1/tasks/task-001');
    });
  });

  describe('equipment', () => {
    it('list returns /api/v1/equipment', () => {
      expect(API_PATHS.equipment.list).toBe('/api/v1/equipment');
    });

    it('maintenance returns parameterized path', () => {
      const path = API_PATHS.equipment.maintenance('eq-001');
      expect(path).toBe('/api/v1/equipment/eq-001/maintenance');
    });
  });

  describe('terrain', () => {
    it('analyze returns /api/v1/terrain/dem', () => {
      expect(API_PATHS.terrain.analyze).toBe('/api/v1/terrain/dem');
    });

    it('slope returns /api/v1/terrain/slope', () => {
      expect(API_PATHS.terrain.slope).toBe('/api/v1/terrain/slope');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 5. SERVICE_URLS Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('SERVICE_URLS', () => {
  it('all service URLs are defined and non-empty strings', () => {
    for (const [key, url] of Object.entries(SERVICE_URLS)) {
      expect(url).toBeDefined();
      expect(typeof url).toBe('string');
      expect((url as string).length).toBeGreaterThan(0);
    }
  });

  it('fieldManagement URL points to port 3000 in dev mode', () => {
    expect(SERVICE_URLS.fieldManagement).toContain('3000');
  });

  it('auth URL points to port 3025 in dev mode', () => {
    expect(SERVICE_URLS.auth).toContain('3025');
  });

  it('weather URL points to port 8092 in dev mode', () => {
    expect(SERVICE_URLS.weather).toContain('8092');
  });

  it('satellite URL points to port 8090 in dev mode', () => {
    expect(SERVICE_URLS.satellite).toContain('8090');
  });

  it('yoloVision URL points to port 8150 in dev mode', () => {
    expect(SERVICE_URLS.yoloVision).toContain('8150');
  });

  it('terrainCore URL points to port 8185 in dev mode', () => {
    expect(SERVICE_URLS.terrainCore).toContain('8185');
  });

  it('all URLs have valid URL format', () => {
    for (const [key, url] of Object.entries(SERVICE_URLS)) {
      expect(url).toMatch(/^https?:\/\/.+/);
    }
  });

  it('fieldCore and fieldManagement point to the same service', () => {
    expect(SERVICE_URLS.fieldCore).toBe(SERVICE_URLS.fieldManagement);
  });

  it('auth and users point to the same service', () => {
    expect(SERVICE_URLS.auth).toBe(SERVICE_URLS.users);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 6. API_URLS Integration Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('API_URLS integration', () => {
  it('weatherEndpoints.current resolves to full URL with /weather/current', () => {
    expect(API_URLS.weatherEndpoints.current).toContain('8092');
    expect(API_URLS.weatherEndpoints.current).toContain('/weather/current');
  });

  it('weatherEndpoints.forecast resolves to full URL with /weather/forecast', () => {
    expect(API_URLS.weatherEndpoints.forecast).toContain('/weather/forecast');
  });

  it('satelliteEndpoints.timeseries resolves correctly with fieldId', () => {
    const url = API_URLS.satelliteEndpoints.timeseries('field-100');
    expect(url).toContain('8090');
    expect(url).toContain('/v1/timeseries/field-100');
  });

  it('satelliteEndpoints.analyze resolves to full URL', () => {
    expect(API_URLS.satelliteEndpoints.analyze).toContain('8090');
    expect(API_URLS.satelliteEndpoints.analyze).toContain('/v1/analyze');
  });

  it('satelliteEndpoints.indices resolves correctly with fieldId', () => {
    const url = API_URLS.satelliteEndpoints.indices('field-200');
    expect(url).toContain('/v1/indices/field-200');
  });

  it('fields.list resolves to full URL with /api/v1/fields', () => {
    expect(API_URLS.fields.list).toContain('3000');
    expect(API_URLS.fields.list).toContain('/api/v1/fields');
  });

  it('fields.create resolves to full URL', () => {
    expect(API_URLS.fields.create).toContain('/api/v1/fields');
  });

  it('fields.byId resolves with field parameter', () => {
    const url = API_URLS.fields.byId('f-001');
    expect(url).toContain('3000');
    expect(url).toContain('/api/v1/fields/f-001');
  });

  it('auth.login resolves through API_BASE_URL (Kong gateway)', () => {
    expect(API_URLS.auth.login).toContain('/api/v1/auth/login');
  });

  it('auth.me resolves through API_BASE_URL', () => {
    expect(API_URLS.auth.me).toContain('/api/v1/auth/me');
  });

  it('dashboard.stats resolves to indicators service', () => {
    expect(API_URLS.dashboard.stats).toContain('8091');
    expect(API_URLS.dashboard.stats).toContain('/api/v1/indicators/dashboard');
  });

  it('health helper generates correct health URL for any service', () => {
    const healthUrl = API_URLS.health(SERVICE_URLS.weather);
    expect(healthUrl).toContain('8092');
    expect(healthUrl.endsWith('/healthz')).toBe(true);
  });

  it('visionEndpoints.detectPest resolves to yolo vision service', () => {
    expect(API_URLS.visionEndpoints.detectPest).toContain('8150');
    expect(API_URLS.visionEndpoints.detectPest).toContain('/api/v1/detect/pest');
  });

  it('terrainEndpoints.analyze resolves to terrain core service', () => {
    expect(API_URLS.terrainEndpoints.analyze).toContain('8185');
    expect(API_URLS.terrainEndpoints.analyze).toContain('/api/v1/terrain/dem');
  });

  it('notificationEndpoints.list resolves correctly', () => {
    expect(API_URLS.notificationEndpoints.list).toContain('8110');
    expect(API_URLS.notificationEndpoints.list).toContain('/api/v1/notifications');
  });

  it('taskEndpoints.list resolves correctly', () => {
    expect(API_URLS.taskEndpoints.list).toContain('8103');
    expect(API_URLS.taskEndpoints.list).toContain('/api/v1/tasks');
  });

  it('equipmentEndpoints.list resolves correctly', () => {
    expect(API_URLS.equipmentEndpoints.list).toContain('8101');
    expect(API_URLS.equipmentEndpoints.list).toContain('/api/v1/equipment');
  });

  it('billingEndpoints.invoices resolves correctly', () => {
    expect(API_URLS.billingEndpoints.invoices).toContain('8089');
    expect(API_URLS.billingEndpoints.invoices).toContain('/api/v1/billing/invoices');
  });

  it('traceabilityEndpoints.qrCode resolves with batchId parameter', () => {
    const url = API_URLS.traceabilityEndpoints.qrCode('batch-99');
    expect(url).toContain('8123');
    expect(url).toContain('/api/v1/traceability/batches/batch-99/qr');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 7. Cross-Service Consistency Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Cross-service consistency', () => {
  it('all SERVICE_PORTS values are unique (no port conflicts)', () => {
    const ports = Object.values(SERVICE_PORTS);
    const uniquePorts = new Set(ports);

    // fieldCore and fieldManagement share port 3000, auth and users share 3025,
    // fieldChat/communityChat may share ports with chat-related services, etc.
    // We check that deliberate aliases are the only duplicates.
    const portCounts = new Map<number, string[]>();
    for (const [key, port] of Object.entries(SERVICE_PORTS)) {
      const existing = portCounts.get(port as number) || [];
      existing.push(key);
      portCounts.set(port as number, existing);
    }

    // Verify known aliases share the same port intentionally
    const knownAliases: Record<number, string[]> = {
      3000: ['fieldCore', 'fieldManagement'],
      3025: ['auth', 'users'],
    };

    for (const [port, keys] of portCounts.entries()) {
      if (keys.length > 1) {
        const expectedAliases = knownAliases[port];
        expect(expectedAliases).toBeDefined();
        expect(keys.sort()).toEqual(expectedAliases!.sort());
      }
    }
  });

  it('all required core services have URLs defined', () => {
    const requiredServices = [
      'fieldManagement',
      'auth',
      'weather',
      'satellite',
      'indicators',
      'advisory',
      'irrigation',
      'notifications',
      'task',
      'equipment',
    ];

    for (const service of requiredServices) {
      expect(SERVICE_URLS).toHaveProperty(service);
      expect((SERVICE_URLS as Record<string, string>)[service]).toBeTruthy();
    }
  });

  it('all SERVICE_URLS keys have corresponding SERVICE_PORTS entries', () => {
    for (const key of Object.keys(SERVICE_URLS)) {
      expect(SERVICE_PORTS).toHaveProperty(key);
    }
  });

  it('SERVICE_URLS are built from SERVICE_PORTS correctly', () => {
    // Each SERVICE_URL should contain its corresponding port number
    for (const [key, port] of Object.entries(SERVICE_PORTS)) {
      const url = (SERVICE_URLS as Record<string, string>)[key];
      if (url) {
        expect(url).toContain(String(port));
      }
    }
  });

  it('API_PATHS has all major domain sections', () => {
    const expectedSections = [
      'health',
      'auth',
      'fields',
      'weather',
      'satellite',
      'indicators',
      'irrigation',
      'notifications',
      'tasks',
      'equipment',
      'advisory',
      'billing',
      'audit',
      'terrain',
      'vision',
    ];

    for (const section of expectedSections) {
      expect(API_PATHS).toHaveProperty(section);
    }
  });
});
