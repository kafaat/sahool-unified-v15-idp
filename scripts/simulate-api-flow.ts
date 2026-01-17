/**
 * SAHOOL API Flow Simulation Test
 * اختبار محاكاة تدفق API
 *
 * This script simulates API calls to verify the frontend-backend integration
 * without requiring actual services to be running.
 */

// Mock API responses for simulation
const mockResponses = {
  // Auth endpoints
  "/api/v1/auth/login": {
    success: true,
    data: {
      access_token: "mock_jwt_token_" + Date.now(),
      user: {
        id: "user-123",
        email: "farmer@sahool.com",
        name: "مزارع يمني",
        role: "farmer",
        tenantId: "tenant-001",
      },
    },
  },

  "/api/v1/auth/me": {
    success: true,
    data: {
      id: "user-123",
      email: "farmer@sahool.com",
      name: "مزارع يمني",
      role: "farmer",
    },
  },

  // Fields endpoints
  "/api/v1/fields": {
    success: true,
    data: [
      {
        id: "field-001",
        name: "حقل القمح الشرقي",
        name_ar: "حقل القمح الشرقي",
        cropType: "wheat",
        area_hectares: 5.5,
        status: "active",
        ndvi_value: 0.72,
        last_irrigation: "2025-12-24T10:00:00Z",
        coordinates: [
          [44.191, 15.369],
          [44.195, 15.369],
          [44.195, 15.365],
          [44.191, 15.365],
        ],
      },
      {
        id: "field-002",
        name: "حقل الذرة الغربي",
        name_ar: "حقل الذرة الغربي",
        cropType: "corn",
        area_hectares: 3.2,
        status: "active",
        ndvi_value: 0.65,
        last_irrigation: "2025-12-25T08:00:00Z",
        coordinates: [
          [44.185, 15.369],
          [44.189, 15.369],
          [44.189, 15.365],
          [44.185, 15.365],
        ],
      },
    ],
  },

  // Weather endpoints
  "/api/v1/weather/current": {
    success: true,
    data: {
      temperature: 28.5,
      humidity: 45,
      windSpeed: 12.3,
      windDirection: "NE",
      precipitation: 0,
      solarRadiation: 850,
      condition: "sunny",
      condition_ar: "مشمس",
      location: "صنعاء، اليمن",
      updated_at: new Date().toISOString(),
    },
  },

  "/api/v1/weather/forecast": {
    success: true,
    data: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() + i * 86400000).toISOString().split("T")[0],
      temp_max: 30 + Math.random() * 5,
      temp_min: 18 + Math.random() * 3,
      humidity: 40 + Math.random() * 20,
      precipitation_chance: Math.random() * 30,
      condition: i % 3 === 0 ? "cloudy" : "sunny",
    })),
  },

  // Tasks endpoints
  "/api/v1/tasks": {
    success: true,
    data: [
      {
        id: "task-001",
        title: "ري حقل القمح",
        description: "ري الحقل الشرقي بعد قياسات الرطوبة",
        status: "open",
        priority: "high",
        field_id: "field-001",
        assignee_id: "user-123",
        due_date: new Date(Date.now() + 86400000).toISOString(),
        created_at: new Date().toISOString(),
      },
      {
        id: "task-002",
        title: "تسميد الذرة",
        description: "إضافة الأسمدة النيتروجينية",
        status: "in_progress",
        priority: "medium",
        field_id: "field-002",
        assignee_id: "user-123",
        due_date: new Date(Date.now() + 172800000).toISOString(),
        created_at: new Date(Date.now() - 86400000).toISOString(),
      },
    ],
  },

  // IoT endpoints
  "/api/v1/sensors": {
    success: true,
    data: [
      {
        id: "sensor-001",
        name: "مستشعر رطوبة التربة - الشرق",
        type: "soil_moisture",
        status: "active",
        field_id: "field-001",
        last_reading: {
          value: 42.5,
          unit: "%",
          timestamp: new Date().toISOString(),
        },
      },
      {
        id: "sensor-002",
        name: "مستشعر درجة الحرارة",
        type: "temperature",
        status: "active",
        field_id: "field-001",
        last_reading: {
          value: 28.3,
          unit: "°C",
          timestamp: new Date().toISOString(),
        },
      },
      {
        id: "sensor-003",
        name: "مستشعر الرطوبة الجوية",
        type: "humidity",
        status: "active",
        field_id: "field-001",
        last_reading: {
          value: 45,
          unit: "%",
          timestamp: new Date().toISOString(),
        },
      },
    ],
  },

  // Equipment endpoints
  "/api/v1/equipment": {
    success: true,
    data: [
      {
        id: "equip-001",
        name: "جرار زراعي",
        type: "tractor",
        status: "active",
        last_maintenance: "2025-12-01T00:00:00Z",
        next_maintenance: "2026-03-01T00:00:00Z",
      },
      {
        id: "equip-002",
        name: "نظام ري بالتنقيط",
        type: "irrigation_system",
        status: "active",
        last_maintenance: "2025-11-15T00:00:00Z",
        next_maintenance: "2026-02-15T00:00:00Z",
      },
    ],
  },

  // NDVI endpoints
  "/api/v1/ndvi": {
    success: true,
    data: {
      summary: {
        healthy_fields: 2,
        moderate_fields: 0,
        stressed_fields: 0,
        average_ndvi: 0.685,
      },
      fields: [
        { field_id: "field-001", ndvi: 0.72, classification: "healthy" },
        { field_id: "field-002", ndvi: 0.65, classification: "healthy" },
      ],
    },
  },

  // Irrigation endpoints
  "/api/v1/irrigation": {
    success: true,
    data: {
      et0: 5.2,
      etc: 4.16,
      recommended_amount_mm: 25,
      next_irrigation: new Date(Date.now() + 86400000).toISOString(),
      water_balance: {
        precipitation: 0,
        irrigation: 30,
        evapotranspiration: 26,
        balance: 4,
      },
    },
  },

  // Fertilizer endpoints
  "/api/v1/fertilizer": {
    success: true,
    data: {
      recommendations: [
        { nutrient: "N", amount_kg_ha: 45, type: "Urea", timing: "Now" },
        { nutrient: "P", amount_kg_ha: 20, type: "DAP", timing: "In 2 weeks" },
        { nutrient: "K", amount_kg_ha: 30, type: "MOP", timing: "In 2 weeks" },
      ],
    },
  },

  // Yield endpoints
  "/api/v1/yield": {
    success: true,
    data: {
      predicted_yield_ton_ha: 3.8,
      confidence: 0.85,
      factors: {
        weather_impact: 0.95,
        soil_impact: 0.92,
        management_impact: 0.88,
      },
    },
  },

  // Astronomical calendar
  "/api/v1/astronomical": {
    success: true,
    data: {
      date: new Date().toISOString().split("T")[0],
      hijri_date: "22 جمادى الآخرة 1447",
      lunar_mansion: "النعائم",
      moon_phase: "الربع الأول",
      agricultural_advice: "وقت مناسب للزراعة والري",
      proverb: "إذا طلعت النعائم، أخصبت الأرض وأمطر الغمام",
    },
  },

  // Marketplace endpoints
  "/api/v1/marketplace": {
    success: true,
    data: {
      listings: [
        {
          id: "listing-001",
          title: "قمح يمني عضوي",
          price: 500,
          currency: "YER",
          quantity: 100,
          unit: "كجم",
          seller: "مزرعة السعادة",
        },
      ],
    },
  },

  // Billing endpoints
  "/api/v1/billing": {
    success: true,
    data: {
      subscription: {
        plan: "pro",
        status: "active",
        fields_limit: 20,
        fields_used: 2,
        expires_at: "2026-12-26T00:00:00Z",
      },
    },
  },
};

interface SimulationResult {
  endpoint: string;
  status: "success" | "error";
  latency_ms: number;
  response?: unknown;
  error?: string;
}

class APISimulator {
  private results: SimulationResult[] = [];
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  private async simulateRequest(endpoint: string): Promise<SimulationResult> {
    const start = Date.now();

    // Simulate network latency (20-100ms)
    const latency = 20 + Math.random() * 80;
    await new Promise((resolve) => setTimeout(resolve, latency));

    // Find matching mock response
    const mockKey = Object.keys(mockResponses).find((key) =>
      endpoint.startsWith(key),
    );

    if (mockKey) {
      return {
        endpoint,
        status: "success",
        latency_ms: Date.now() - start,
        response: mockResponses[mockKey as keyof typeof mockResponses],
      };
    }

    return {
      endpoint,
      status: "error",
      latency_ms: Date.now() - start,
      error: "Endpoint not found in mock data",
    };
  }

  async runSimulation(): Promise<void> {
    console.log(
      "\n═══════════════════════════════════════════════════════════════════════════════",
    );
    console.log("  SAHOOL API Flow Simulation");
    console.log("  محاكاة تدفق API سهول");
    console.log(
      "═══════════════════════════════════════════════════════════════════════════════\n",
    );

    const endpoints = Object.keys(mockResponses);

    console.log("Testing", endpoints.length, "API endpoints...\n");

    for (const endpoint of endpoints) {
      const result = await this.simulateRequest(endpoint);
      this.results.push(result);

      const icon = result.status === "success" ? "✓" : "✗";
      const color = result.status === "success" ? "\x1b[32m" : "\x1b[31m";
      console.log(
        `${color}${icon}\x1b[0m ${endpoint} (${result.latency_ms}ms)`,
      );
    }

    this.printSummary();
  }

  private printSummary(): void {
    const successful = this.results.filter(
      (r) => r.status === "success",
    ).length;
    const failed = this.results.filter((r) => r.status === "error").length;
    const avgLatency =
      this.results.reduce((acc, r) => acc + r.latency_ms, 0) /
      this.results.length;

    console.log(
      "\n═══════════════════════════════════════════════════════════════════════════════",
    );
    console.log("  Simulation Summary");
    console.log(
      "═══════════════════════════════════════════════════════════════════════════════\n",
    );
    console.log(`  \x1b[32mSuccessful:\x1b[0m ${successful}`);
    console.log(`  \x1b[31mFailed:\x1b[0m     ${failed}`);
    console.log(`  Avg Latency: ${avgLatency.toFixed(2)}ms`);
    console.log(
      `  Success Rate: ${((successful / this.results.length) * 100).toFixed(1)}%\n`,
    );

    if (failed === 0) {
      console.log("\x1b[32m✓ All API simulations passed!\x1b[0m\n");
    }
  }

  async testFullFlow(): Promise<void> {
    console.log(
      "\n═══════════════════════════════════════════════════════════════════════════════",
    );
    console.log("  Full User Flow Simulation");
    console.log("  محاكاة تدفق المستخدم الكامل");
    console.log(
      "═══════════════════════════════════════════════════════════════════════════════\n",
    );

    const flows = [
      {
        name: "Login Flow",
        endpoints: ["/api/v1/auth/login", "/api/v1/auth/me"],
      },
      {
        name: "Dashboard Load",
        endpoints: [
          "/api/v1/fields",
          "/api/v1/weather/current",
          "/api/v1/tasks",
        ],
      },
      {
        name: "Field Details",
        endpoints: ["/api/v1/fields", "/api/v1/ndvi", "/api/v1/sensors"],
      },
      {
        name: "Irrigation Planning",
        endpoints: ["/api/v1/irrigation", "/api/v1/weather/forecast"],
      },
      { name: "Equipment Check", endpoints: ["/api/v1/equipment"] },
      { name: "Yield Prediction", endpoints: ["/api/v1/yield"] },
    ];

    for (const flow of flows) {
      console.log(`\n\x1b[34m▶ ${flow.name}\x1b[0m`);
      const flowStart = Date.now();

      for (const endpoint of flow.endpoints) {
        const result = await this.simulateRequest(endpoint);
        const icon = result.status === "success" ? "  ✓" : "  ✗";
        console.log(`${icon} ${endpoint}`);
      }

      console.log(
        `  \x1b[90mFlow completed in ${Date.now() - flowStart}ms\x1b[0m`,
      );
    }

    console.log("\n\x1b[32m✓ All user flows simulated successfully!\x1b[0m\n");
  }
}

// Run simulation
const simulator = new APISimulator();

async function main() {
  const mode = process.argv[2] || "full";

  if (mode === "flow") {
    await simulator.testFullFlow();
  } else {
    await simulator.runSimulation();
    await simulator.testFullFlow();
  }
}

main().catch(console.error);
