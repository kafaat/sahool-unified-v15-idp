/**
 * SAHOOL Mock API Server
 * خادم محاكاة لجميع خدمات الـ Kernel المسترجعة
 */

const http = require("http");

// Mock Data
const mockData = {
  // Fields (field-core)
  fields: [
    {
      id: "field_001",
      name: "حقل الطماطم - صنعاء",
      tenantId: "tenant_1",
      cropType: "طماطم",
      status: "active",
      areaHectares: 5.2,
      ndviValue: 0.72,
      healthScore: 85,
      boundary: {
        type: "Polygon",
        coordinates: [
          [
            [44.19, 15.37],
            [44.195, 15.37],
            [44.195, 15.375],
            [44.19, 15.375],
            [44.19, 15.37],
          ],
        ],
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: "field_002",
      name: "حقل البن - إب",
      tenantId: "tenant_1",
      cropType: "بن",
      status: "active",
      areaHectares: 8.5,
      ndviValue: 0.45,
      healthScore: 65,
      boundary: {
        type: "Polygon",
        coordinates: [
          [
            [44.16, 13.96],
            [44.17, 13.96],
            [44.17, 13.97],
            [44.16, 13.97],
            [44.16, 13.96],
          ],
        ],
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: "field_003",
      name: "حقل القات - تعز",
      tenantId: "tenant_1",
      cropType: "قات",
      status: "active",
      areaHectares: 3.8,
      ndviValue: 0.28,
      healthScore: 40,
      boundary: {
        type: "Polygon",
        coordinates: [
          [
            [44.02, 13.58],
            [44.03, 13.58],
            [44.03, 13.59],
            [44.02, 13.59],
            [44.02, 13.58],
          ],
        ],
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: "field_004",
      name: "حقل الموز - الحديدة",
      tenantId: "tenant_1",
      cropType: "موز",
      status: "active",
      areaHectares: 12.0,
      ndviValue: 0.68,
      healthScore: 80,
      boundary: {
        type: "Polygon",
        coordinates: [
          [
            [42.95, 14.8],
            [42.97, 14.8],
            [42.97, 14.82],
            [42.95, 14.82],
            [42.95, 14.8],
          ],
        ],
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ],

  // Tasks (task-service)
  tasks: [
    {
      id: "task_001",
      title: "ري الطماطم - الصباح",
      description: "ري الحقل الشمالي لمدة 30 دقيقة",
      fieldId: "field_001",
      fieldName: "حقل الطماطم",
      status: "pending",
      priority: "high",
      taskType: "irrigation",
      dueDate: new Date().toISOString(),
      assigneeName: "أحمد محمد",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: "task_002",
      title: "رش مبيدات وقائية",
      description: "رش مبيد فطري للوقاية من البياض الدقيقي",
      fieldId: "field_001",
      fieldName: "حقل الطماطم",
      status: "in_progress",
      priority: "medium",
      taskType: "pesticide",
      dueDate: new Date(Date.now() + 86400000).toISOString(),
      assigneeName: "محمد علي",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: "task_003",
      title: "فحص مرض صدأ البن",
      description: "فحص ميداني للكشف عن علامات مرض صدأ الأوراق",
      fieldId: "field_002",
      fieldName: "حقل البن",
      status: "pending",
      priority: "high",
      taskType: "inspection",
      dueDate: new Date().toISOString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: "task_004",
      title: "حصاد الموز الناضج",
      description: "جمع العناقيد الناضجة من الصف 1-5",
      fieldId: "field_004",
      fieldName: "حقل الموز",
      status: "completed",
      priority: "medium",
      taskType: "harvest",
      completedAt: new Date().toISOString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ],

  // NDVI Summary (ndvi-engine)
  ndviSummary: {
    tenantId: "tenant_1",
    totalFields: 4,
    averageNdvi: 0.53,
    averageHealth: 0.68,
    totalAreaHectares: 29.5,
    distribution: {
      healthy: 2,
      moderate: 1,
      stressed: 0,
      critical: 1,
    },
    timestamp: new Date().toISOString(),
  },

  // Weather (weather-core)
  weather: {
    location: { lat: 15.37, lng: 44.19, name: "صنعاء" },
    current: {
      temperature: 28,
      humidity: 45,
      windSpeed: 12,
      windDirection: 180,
      pressure: 1013,
      cloudCover: 20,
      uvIndex: 8,
      description: "مشمس جزئياً",
      icon: "02d",
    },
    timestamp: new Date().toISOString(),
  },

  // Alerts
  alerts: [
    {
      id: "alert_001",
      title: "انخفاض NDVI مكتشف",
      type: "ndvi_low",
      severity: "warning",
      category: "ndvi",
      status: "active",
      fieldId: "field_003",
      fieldName: "حقل القات",
      message: "الحقل يظهر تراجع في صحة النبات",
      createdAt: new Date().toISOString(),
    },
    {
      id: "alert_002",
      title: "موجة حارة متوقعة",
      type: "heat_wave",
      severity: "info",
      category: "weather",
      status: "active",
      message: "متوقع ارتفاع درجات الحرارة غداً",
      createdAt: new Date(Date.now() - 3600000).toISOString(),
    },
  ],

  // Equipment (equipment-service)
  equipment: [
    {
      id: "equip_001",
      name: "جرار زراعي",
      type: "tractor",
      status: "available",
      tenantId: "tenant_1",
      lastMaintenanceDate: new Date(Date.now() - 86400000 * 30).toISOString(),
    },
    {
      id: "equip_002",
      name: "نظام ري بالتنقيط",
      type: "irrigation_system",
      status: "in_use",
      tenantId: "tenant_1",
    },
  ],

  // Sensors (iot-gateway)
  sensors: [
    {
      id: "sensor_001",
      fieldId: "field_001",
      name: "مستشعر رطوبة التربة",
      type: "soil_moisture",
      status: "online",
      batteryLevel: 85,
      lastReading: {
        sensorId: "sensor_001",
        value: 45,
        unit: "%",
        timestamp: new Date().toISOString(),
      },
    },
    {
      id: "sensor_002",
      fieldId: "field_001",
      name: "مستشعر درجة الحرارة",
      type: "temperature",
      status: "online",
      batteryLevel: 92,
      lastReading: {
        sensorId: "sensor_002",
        value: 28.5,
        unit: "°C",
        timestamp: new Date().toISOString(),
      },
    },
  ],
};

// Route handlers
const routes = {
  // Fields API
  "GET /api/v1/fields": () => ({ success: true, data: mockData.fields }),
  "GET /api/v1/fields/:id": (params) => {
    const field = mockData.fields.find((f) => f.id === params.id);
    return field
      ? { success: true, data: field }
      : { success: false, error: "Field not found" };
  },

  // Tasks API
  "GET /api/v1/tasks": () => ({ success: true, data: mockData.tasks }),
  "POST /api/v1/tasks/:id/complete": (params) => {
    const task = mockData.tasks.find((t) => t.id === params.id);
    if (task) {
      task.status = "completed";
      task.completedAt = new Date().toISOString();
    }
    return { success: true, data: task };
  },

  // NDVI API
  "GET /api/v1/ndvi/summary/:tenantId": () => ({
    success: true,
    data: mockData.ndviSummary,
  }),
  "GET /api/v1/ndvi/:fieldId": (params) => {
    const field = mockData.fields.find((f) => f.id === params.fieldId);
    return {
      success: true,
      data: {
        fieldId: params.fieldId,
        fieldName: field?.name || "Unknown",
        current: {
          value: field?.ndviValue || 0.5,
          category: { name: "Moderate", nameAr: "متوسط", color: "#f59e0b" },
          date: new Date().toISOString(),
        },
        statistics: {
          average: field?.ndviValue || 0.5,
          min: 0.3,
          max: 0.8,
          trend: 0.02,
          trendDirection: "stable",
        },
        history: [],
        lastUpdated: new Date().toISOString(),
      },
    };
  },

  // Weather API
  "GET /api/v1/weather/current": () => ({
    success: true,
    data: mockData.weather,
  }),
  "GET /api/v1/weather/forecast": () => ({
    success: true,
    data: {
      location: { lat: 15.37, lng: 44.19 },
      daily: [
        {
          date: new Date().toISOString(),
          tempMax: 32,
          tempMin: 18,
          humidity: 40,
          precipitation: 0,
          precipitationProbability: 5,
          windSpeed: 10,
          description: "مشمس",
          icon: "01d",
        },
        {
          date: new Date(Date.now() + 86400000).toISOString(),
          tempMax: 34,
          tempMin: 20,
          humidity: 35,
          precipitation: 0,
          precipitationProbability: 10,
          windSpeed: 12,
          description: "مشمس جزئياً",
          icon: "02d",
        },
        {
          date: new Date(Date.now() + 86400000 * 2).toISOString(),
          tempMax: 30,
          tempMin: 19,
          humidity: 50,
          precipitation: 2,
          precipitationProbability: 40,
          windSpeed: 8,
          description: "غائم جزئياً",
          icon: "03d",
        },
      ],
    },
  }),

  // Alerts API
  "GET /api/v1/alerts": () => ({ success: true, data: mockData.alerts }),
  "POST /api/v1/alerts/:id/acknowledge": (params) => {
    const alert = mockData.alerts.find((a) => a.id === params.id);
    if (alert) alert.status = "acknowledged";
    return { success: true };
  },

  // Equipment API
  "GET /api/v1/equipment": () => ({ success: true, data: mockData.equipment }),

  // Sensors API
  "GET /api/v1/sensors/:fieldId": (params) => ({
    success: true,
    data: mockData.sensors.filter((s) => s.fieldId === params.fieldId),
  }),

  // Agro Advisor API
  "POST /api/v1/advisor/analyze": (params, body) => ({
    success: true,
    data: {
      recommendations: [
        {
          type: "irrigation",
          priority: "high",
          message: "يُنصح بالري خلال الـ 24 ساعة القادمة",
          messageAr: "يُنصح بالري خلال الـ 24 ساعة القادمة",
        },
        {
          type: "fertilizer",
          priority: "medium",
          message: "أضف سماد NPK بمعدل 50 كجم/هكتار",
          messageAr: "أضف سماد NPK بمعدل 50 كجم/هكتار",
        },
      ],
    },
  }),

  // Health check
  "GET /healthz": () => ({
    status: "ok",
    services: [
      "field-core",
      "task-service",
      "ndvi-engine",
      "weather-core",
      "agro-advisor",
      "iot-gateway",
    ],
  }),

  // Service Registry & Comparison API
  "GET /api/v1/services": () => ({
    success: true,
    data: {
      services: [
        {
          type: "satellite",
          name: "Satellite Service",
          nameAr: "خدمة الأقمار الصناعية",
          legacy: { port: 8107, status: "deprecated" },
          modern: { port: 8090, status: "active" },
        },
        {
          type: "weather",
          name: "Weather Service",
          nameAr: "خدمة الطقس",
          legacy: { port: 8108, status: "deprecated" },
          modern: { port: 8092, status: "active" },
        },
        {
          type: "fertilizer",
          name: "Fertilizer Advisor",
          nameAr: "مستشار التسميد",
          legacy: { port: 8105, status: "deprecated" },
          modern: { port: 8093, status: "active" },
        },
        {
          type: "crop-health",
          name: "Crop Health AI",
          nameAr: "صحة المحاصيل",
          legacy: { port: 8100, status: "deprecated" },
          modern: { port: 8095, status: "active" },
        },
        {
          type: "community",
          name: "Community Chat",
          nameAr: "الدردشة المجتمعية",
          legacy: { port: 8099, status: "deprecated" },
          modern: { port: 8097, status: "active" },
        },
        {
          type: "notifications",
          name: "Notification Service",
          nameAr: "خدمة الإشعارات",
          legacy: { port: 8089, status: "deprecated" },
          modern: { port: 8110, status: "active" },
        },
      ],
    },
  }),

  "GET /api/v1/services/health": async () => {
    // In a real implementation, this would check actual service health
    return {
      success: true,
      data: {
        satellite: {
          modern: { healthy: true, latency: 45 },
          legacy: { healthy: false, latency: -1 },
        },
        weather: {
          modern: { healthy: true, latency: 32 },
          legacy: { healthy: false, latency: -1 },
        },
        fertilizer: {
          modern: { healthy: true, latency: 28 },
          legacy: { healthy: false, latency: -1 },
        },
        "crop-health": {
          modern: { healthy: true, latency: 120 },
          legacy: { healthy: false, latency: -1 },
        },
        community: {
          modern: { healthy: true, latency: 55 },
          legacy: { healthy: false, latency: -1 },
        },
        notifications: {
          modern: { healthy: true, latency: 38 },
          legacy: { healthy: false, latency: -1 },
        },
        mock: { healthy: true, latency: 5 },
      },
    };
  },
};

// CORS Configuration - Development only
const ALLOWED_ORIGINS = [
  "http://localhost:3000",
  "http://localhost:3001",
  "http://localhost:5173",
  "http://127.0.0.1:3000",
  "http://127.0.0.1:3001",
];

// Create server
const server = http.createServer((req, res) => {
  // CORS headers - Restrict to allowed origins
  const origin = req.headers.origin;
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader("Access-Control-Allow-Origin", origin);
  } else if (!origin) {
    // Allow requests without origin (curl, mobile apps, etc.)
    res.setHeader("Access-Control-Allow-Origin", "http://localhost:3000");
  }
  // Note: If origin is not allowed, we don't set the header (browser will block)

  res.setHeader(
    "Access-Control-Allow-Methods",
    "GET, POST, PUT, DELETE, OPTIONS",
  );
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.setHeader("Access-Control-Allow-Credentials", "true");

  if (req.method === "OPTIONS") {
    res.writeHead(200);
    res.end();
    return;
  }

  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname;
  const method = req.method;

  console.log(`[${new Date().toISOString()}] ${method} ${path}`);

  // Find matching route
  let handler = null;
  let params = {};

  for (const [routeKey, routeHandler] of Object.entries(routes)) {
    const [routeMethod, routePath] = routeKey.split(" ");
    if (routeMethod !== method) continue;

    // Convert route pattern to regex
    const pattern = routePath.replace(/:(\w+)/g, "([^/]+)");
    const regex = new RegExp(`^${pattern}$`);
    const match = path.match(regex);

    if (match) {
      handler = routeHandler;
      // Extract params
      const paramNames = (routePath.match(/:(\w+)/g) || []).map((p) =>
        p.slice(1),
      );
      paramNames.forEach((name, i) => {
        params[name] = match[i + 1];
      });
      break;
    }
  }

  if (handler) {
    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", () => {
      try {
        const parsedBody = body ? JSON.parse(body) : {};
        const result = handler(params, parsedBody);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(result));
      } catch (error) {
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ success: false, error: error.message }));
      }
    });
  } else {
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ success: false, error: "Route not found" }));
  }
});

const PORT = process.env.PORT || 8000;
server.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════════════╗
║          SAHOOL Mock API Server                                  ║
║          خادم محاكاة لخدمات الـ Kernel المسترجعة                  ║
╠══════════════════════════════════════════════════════════════════╣
║  Port: ${PORT}                                                        ║
║  URL:  http://localhost:${PORT}                                       ║
╠══════════════════════════════════════════════════════════════════╣
║  Services Simulated:                                             ║
║    ✓ field-core      - إدارة الحقول                              ║
║    ✓ task-service    - إدارة المهام                              ║
║    ✓ ndvi-engine     - تحليل NDVI                                ║
║    ✓ weather-core    - بيانات الطقس                              ║
║    ✓ agro-advisor    - التوصيات الزراعية                         ║
║    ✓ iot-gateway     - المستشعرات                                ║
║    ✓ equipment-service - المعدات                                 ║
╚══════════════════════════════════════════════════════════════════╝
  `);
});
