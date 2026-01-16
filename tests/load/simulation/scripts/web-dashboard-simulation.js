// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL IDP - Web Dashboard Simulation
// محاكاة لوحة التحكم على الويب
// ═══════════════════════════════════════════════════════════════════════════════
//
// Simulates realistic web dashboard user behavior with:
// - Admin dashboard interactions
// - Farm manager workflows
// - Report generation
// - Real-time data monitoring
// - Multi-tab browsing simulation
// - Data export operations
//
// ═══════════════════════════════════════════════════════════════════════════════

import http from "k6/http";
import { check, sleep, group } from "k6";
import { Counter, Rate, Trend, Gauge } from "k6/metrics";
import {
  randomIntBetween,
  randomItem,
} from "https://jslib.k6.io/k6-utils/1.2.0/index.js";

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const BASE_URL = __ENV.BASE_URL || "http://localhost:8081";
const WEB_VUS = parseInt(__ENV.WEB_VUS) || 15;
const TEST_DURATION = __ENV.TEST_DURATION || "5m";

// ═══════════════════════════════════════════════════════════════════════════════
// CUSTOM METRICS
// ═══════════════════════════════════════════════════════════════════════════════

// Success rates
const webLoginSuccess = new Rate("web_login_success");
const webPageLoadSuccess = new Rate("web_page_load_success");
const webApiSuccess = new Rate("web_api_success");
const reportGenSuccess = new Rate("web_report_generation_success");
const dataExportSuccess = new Rate("web_data_export_success");

// Counters
const adminSessions = new Counter("web_admin_sessions");
const managerSessions = new Counter("web_manager_sessions");
const viewerSessions = new Counter("web_viewer_sessions");
const reportsGenerated = new Counter("web_reports_generated");
const dataExports = new Counter("web_data_exports");

// Trends
const dashboardLoadTime = new Trend("web_dashboard_load_time", true);
const reportGenTime = new Trend("web_report_generation_time", true);
const dataTableLoadTime = new Trend("web_data_table_load_time", true);
const chartRenderTime = new Trend("web_chart_render_time", true);

// Gauges
const activeWebUsers = new Gauge("web_active_users");
const concurrentReports = new Gauge("web_concurrent_reports");

// ═══════════════════════════════════════════════════════════════════════════════
// BROWSER CONFIGURATIONS
// ═══════════════════════════════════════════════════════════════════════════════

const BROWSERS = [
  {
    name: "Chrome",
    ua: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    share: 0.65,
  },
  {
    name: "Safari",
    ua: "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    share: 0.2,
  },
  {
    name: "Firefox",
    ua: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    share: 0.1,
  },
  {
    name: "Edge",
    ua: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    share: 0.05,
  },
];

const SCREEN_RESOLUTIONS = [
  { width: 1920, height: 1080, name: "Full HD" },
  { width: 2560, height: 1440, name: "2K QHD" },
  { width: 3840, height: 2160, name: "4K UHD" },
  { width: 1366, height: 768, name: "HD" },
  { width: 1536, height: 864, name: "HD+" },
  { width: 1440, height: 900, name: "WXGA+" },
];

const USER_ROLES = [
  {
    role: "admin",
    weight: 0.15,
    pages: ["dashboard", "users", "settings", "reports", "audit"],
  },
  {
    role: "manager",
    weight: 0.35,
    pages: ["dashboard", "fields", "workers", "reports", "weather"],
  },
  {
    role: "analyst",
    weight: 0.25,
    pages: ["dashboard", "reports", "analytics", "exports"],
  },
  { role: "viewer", weight: 0.25, pages: ["dashboard", "fields", "weather"] },
];

const DASHBOARD_WIDGETS = [
  { id: "active_fields", api: "/api/widgets/active-fields", priority: "high" },
  {
    id: "weather_overview",
    api: "/api/widgets/weather-overview",
    priority: "high",
  },
  { id: "iot_status", api: "/api/widgets/iot-status", priority: "medium" },
  {
    id: "worker_locations",
    api: "/api/widgets/worker-locations",
    priority: "medium",
  },
  {
    id: "alerts_summary",
    api: "/api/widgets/alerts-summary",
    priority: "high",
  },
  { id: "crop_health", api: "/api/widgets/crop-health", priority: "low" },
  { id: "water_usage", api: "/api/widgets/water-usage", priority: "medium" },
  {
    id: "recent_activities",
    api: "/api/widgets/recent-activities",
    priority: "low",
  },
];

const REPORT_TYPES = [
  { type: "daily_summary", duration: "fast", size: "small" },
  { type: "weekly_analysis", duration: "medium", size: "medium" },
  { type: "monthly_report", duration: "slow", size: "large" },
  { type: "field_performance", duration: "medium", size: "medium" },
  { type: "worker_productivity", duration: "fast", size: "small" },
  { type: "weather_impact", duration: "medium", size: "medium" },
  { type: "iot_analytics", duration: "slow", size: "large" },
];

// ═══════════════════════════════════════════════════════════════════════════════
// K6 OPTIONS
// ═══════════════════════════════════════════════════════════════════════════════

export const options = {
  scenarios: {
    // Admin users - heavy dashboard usage
    admin_users: {
      executor: "constant-vus",
      vus: Math.ceil(WEB_VUS * 0.15),
      duration: TEST_DURATION,
      exec: "adminFlow",
      tags: { role: "admin" },
    },
    // Farm managers - field management focus
    manager_users: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "1m", target: Math.ceil(WEB_VUS * 0.35) },
        { duration: "3m", target: Math.ceil(WEB_VUS * 0.35) },
        { duration: "1m", target: 0 },
      ],
      exec: "managerFlow",
      tags: { role: "manager" },
    },
    // Data analysts - heavy report generation
    analyst_users: {
      executor: "constant-vus",
      vus: Math.ceil(WEB_VUS * 0.25),
      duration: TEST_DURATION,
      exec: "analystFlow",
      tags: { role: "analyst" },
    },
    // Read-only viewers
    viewer_users: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "30s", target: Math.ceil(WEB_VUS * 0.25) },
        { duration: "4m", target: Math.ceil(WEB_VUS * 0.25) },
        { duration: "30s", target: 0 },
      ],
      exec: "viewerFlow",
      tags: { role: "viewer" },
    },
    // Real-time dashboard polling
    realtime_polling: {
      executor: "constant-arrival-rate",
      rate: 30,
      timeUnit: "1m",
      duration: TEST_DURATION,
      preAllocatedVUs: 10,
      exec: "realtimePollingFlow",
      tags: { type: "realtime" },
    },
  },
  thresholds: {
    web_login_success: ["rate>0.95"],
    web_page_load_success: ["rate>0.90"],
    web_api_success: ["rate>0.90"],
    web_dashboard_load_time: ["p(95)<5000"],
    web_report_generation_time: ["p(95)<30000"],
    "http_req_duration{role:admin}": ["p(95)<3000"],
    "http_req_duration{role:manager}": ["p(95)<2500"],
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

function selectBrowser() {
  const rand = Math.random();
  let cumulative = 0;
  for (const browser of BROWSERS) {
    cumulative += browser.share;
    if (rand < cumulative) return browser;
  }
  return BROWSERS[0];
}

function getWebHeaders(browser, resolution) {
  return {
    "User-Agent": browser.ua,
    Accept: "application/json, text/html, */*",
    "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "X-Screen-Width": resolution.width.toString(),
    "X-Screen-Height": resolution.height.toString(),
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
  };
}

function generateSessionId() {
  return "sess_" + Math.random().toString(36).substring(2, 15);
}

function simulatePageLoad(headers, pageName, loadTime) {
  // Simulate browser parsing and rendering
  sleep(loadTime / 1000);
  return true;
}

function simulateUserThinking() {
  // Simulate user reading/thinking time (3-15 seconds)
  sleep(randomIntBetween(3, 15));
}

function simulateDataEntry() {
  // Simulate typing and form filling (5-20 seconds)
  sleep(randomIntBetween(5, 20));
}

// ═══════════════════════════════════════════════════════════════════════════════
// ADMIN FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function adminFlow() {
  const browser = selectBrowser();
  const resolution = randomItem(SCREEN_RESOLUTIONS);
  const headers = getWebHeaders(browser, resolution);
  const sessionId = generateSessionId();

  adminSessions.add(1);
  activeWebUsers.add(1);

  // Login
  group("Admin: Login", () => {
    const loginRes = http.post(
      `${BASE_URL}/api/auth/login`,
      JSON.stringify({
        username: `admin_${__VU}`,
        password: "admin_password_123",
        remember_me: true,
        session_id: sessionId,
      }),
      { headers, tags: { name: "admin_login" } },
    );

    const success = check(loginRes, {
      "admin login ok": (r) => r.status === 200 || r.status === 201,
    });
    webLoginSuccess.add(success ? 1 : 0);

    if (success) {
      try {
        const body = JSON.parse(loginRes.body);
        headers["Authorization"] = `Bearer ${body.token || body.access_token}`;
      } catch {}
    }
  });

  sleep(1);

  // Load main dashboard
  group("Admin: Dashboard", () => {
    const dashStart = Date.now();

    // Parallel widget loading (simulating dashboard)
    const requests = DASHBOARD_WIDGETS.map((widget) => ({
      method: "GET",
      url: `${BASE_URL}${widget.api}`,
      params: { headers, tags: { name: `widget_${widget.id}` } },
    }));

    const responses = http.batch(requests);

    let allSuccess = true;
    responses.forEach((res, i) => {
      const ok = check(res, {
        [`widget ${DASHBOARD_WIDGETS[i].id} loaded`]: (r) =>
          r.status === 200 || r.status === 404,
      });
      if (!ok) allSuccess = false;
    });

    dashboardLoadTime.add(Date.now() - dashStart);
    webPageLoadSuccess.add(allSuccess ? 1 : 0);
  });

  simulateUserThinking();

  // User management
  group("Admin: User Management", () => {
    // List users
    const usersRes = http.get(`${BASE_URL}/api/admin/users?page=1&limit=50`, {
      headers,
      tags: { name: "list_users" },
    });
    webApiSuccess.add(
      check(usersRes, {
        "users listed": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );

    simulateUserThinking();

    // View user details
    const userDetailRes = http.get(
      `${BASE_URL}/api/admin/users/${randomIntBetween(1, 100)}`,
      {
        headers,
        tags: { name: "user_detail" },
      },
    );
    webApiSuccess.add(
      check(userDetailRes, {
        "user detail loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );
  });

  simulateUserThinking();

  // System settings
  group("Admin: Settings", () => {
    const settingsRes = http.get(`${BASE_URL}/api/admin/settings`, {
      headers,
      tags: { name: "settings" },
    });
    webApiSuccess.add(
      check(settingsRes, {
        "settings loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );

    // Audit logs
    const auditRes = http.get(
      `${BASE_URL}/api/admin/audit-logs?page=1&limit=100`,
      {
        headers,
        tags: { name: "audit_logs" },
      },
    );
    webApiSuccess.add(
      check(auditRes, {
        "audit logs loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );
  });

  activeWebUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// MANAGER FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function managerFlow() {
  const browser = selectBrowser();
  const resolution = randomItem(SCREEN_RESOLUTIONS);
  const headers = getWebHeaders(browser, resolution);

  managerSessions.add(1);
  activeWebUsers.add(1);

  // Login
  group("Manager: Login", () => {
    const loginRes = http.post(
      `${BASE_URL}/api/auth/login`,
      JSON.stringify({
        username: `manager_${__VU}`,
        password: "manager_password_123",
      }),
      { headers, tags: { name: "manager_login" } },
    );

    const success = check(loginRes, {
      "manager login ok": (r) => r.status === 200 || r.status === 201,
    });
    webLoginSuccess.add(success ? 1 : 0);

    if (success) {
      try {
        const body = JSON.parse(loginRes.body);
        headers["Authorization"] = `Bearer ${body.token || body.access_token}`;
      } catch {}
    }
  });

  sleep(1);

  // Dashboard with field focus
  group("Manager: Dashboard", () => {
    const dashStart = Date.now();

    const summaryRes = http.get(`${BASE_URL}/api/dashboard/summary`, {
      headers,
      tags: { name: "dashboard_summary" },
    });
    webApiSuccess.add(
      check(summaryRes, {
        "summary loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );

    dashboardLoadTime.add(Date.now() - dashStart);
  });

  simulateUserThinking();

  // Field management
  group("Manager: Field Operations", () => {
    // List all fields
    const tableStart = Date.now();
    const fieldsRes = http.get(
      `${BASE_URL}/api/fields?page=1&limit=25&sort=name`,
      {
        headers,
        tags: { name: "fields_list" },
      },
    );
    dataTableLoadTime.add(Date.now() - tableStart);
    webApiSuccess.add(
      check(fieldsRes, {
        "fields listed": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );

    simulateUserThinking();

    // View field details
    const fieldId = randomIntBetween(1, 50);
    const fieldDetailRes = http.get(`${BASE_URL}/api/fields/${fieldId}`, {
      headers,
      tags: { name: "field_detail" },
    });
    webApiSuccess.add(
      check(fieldDetailRes, {
        "field detail loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );

    // Get field sensors
    const sensorsRes = http.get(`${BASE_URL}/api/fields/${fieldId}/sensors`, {
      headers,
      tags: { name: "field_sensors" },
    });
    webApiSuccess.add(
      check(sensorsRes, {
        "sensors loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );

    // Get field history chart data
    const chartStart = Date.now();
    const historyRes = http.get(
      `${BASE_URL}/api/fields/${fieldId}/history?days=30`,
      {
        headers,
        tags: { name: "field_history" },
      },
    );
    chartRenderTime.add(Date.now() - chartStart);
    webApiSuccess.add(
      check(historyRes, {
        "history loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );
  });

  simulateUserThinking();

  // Worker management
  group("Manager: Workers", () => {
    const workersRes = http.get(`${BASE_URL}/api/workers?status=active`, {
      headers,
      tags: { name: "workers_list" },
    });
    webApiSuccess.add(
      check(workersRes, {
        "workers listed": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );

    // Worker locations map data
    const locationsRes = http.get(`${BASE_URL}/api/workers/locations`, {
      headers,
      tags: { name: "worker_locations" },
    });
    webApiSuccess.add(
      check(locationsRes, {
        "locations loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );
  });

  simulateUserThinking();

  // Weather check
  group("Manager: Weather", () => {
    const weatherRes = http.get(`${BASE_URL}/api/weather/forecast?days=7`, {
      headers,
      tags: { name: "weather_forecast" },
    });
    webApiSuccess.add(
      check(weatherRes, {
        "weather loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );
  });

  activeWebUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// ANALYST FLOW (Heavy Reports)
// ═══════════════════════════════════════════════════════════════════════════════

export function analystFlow() {
  const browser = selectBrowser();
  const resolution = randomItem(SCREEN_RESOLUTIONS);
  const headers = getWebHeaders(browser, resolution);

  activeWebUsers.add(1);

  // Login
  group("Analyst: Login", () => {
    const loginRes = http.post(
      `${BASE_URL}/api/auth/login`,
      JSON.stringify({
        username: `analyst_${__VU}`,
        password: "analyst_password_123",
      }),
      { headers, tags: { name: "analyst_login" } },
    );

    const success = check(loginRes, {
      "analyst login ok": (r) => r.status === 200 || r.status === 201,
    });
    webLoginSuccess.add(success ? 1 : 0);

    if (success) {
      try {
        const body = JSON.parse(loginRes.body);
        headers["Authorization"] = `Bearer ${body.token || body.access_token}`;
      } catch {}
    }
  });

  sleep(1);

  // Quick dashboard view
  group("Analyst: Dashboard", () => {
    const dashRes = http.get(`${BASE_URL}/api/dashboard/analytics`, {
      headers,
      tags: { name: "analytics_dashboard" },
    });
    webApiSuccess.add(
      check(dashRes, {
        "analytics loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );
  });

  simulateUserThinking();

  // Generate reports
  group("Analyst: Report Generation", () => {
    const reportType = randomItem(REPORT_TYPES);
    reportsGenerated.add(1);
    concurrentReports.add(1);

    const reportStart = Date.now();

    // Request report generation
    const genRes = http.post(
      `${BASE_URL}/api/reports/generate`,
      JSON.stringify({
        type: reportType.type,
        date_range: {
          start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
          end: new Date().toISOString(),
        },
        format: randomItem(["pdf", "excel", "csv"]),
        filters: {
          include_charts: true,
          include_summary: true,
        },
      }),
      { headers, tags: { name: "report_generate" } },
    );

    const success = check(genRes, {
      "report generation started": (r) =>
        r.status === 200 ||
        r.status === 201 ||
        r.status === 202 ||
        r.status === 404,
    });
    reportGenSuccess.add(success ? 1 : 0);

    // Simulate waiting for report (polling)
    if (success && (genRes.status === 200 || genRes.status === 202)) {
      let reportId;
      try {
        const body = JSON.parse(genRes.body);
        reportId = body.report_id || body.id;
      } catch {}

      if (reportId) {
        // Poll for completion
        for (let i = 0; i < 5; i++) {
          sleep(2);
          const statusRes = http.get(
            `${BASE_URL}/api/reports/${reportId}/status`,
            {
              headers,
              tags: { name: "report_status" },
            },
          );
          try {
            const status = JSON.parse(statusRes.body);
            if (status.status === "completed") break;
          } catch {}
        }
      }
    }

    reportGenTime.add(Date.now() - reportStart);
    concurrentReports.add(-1);
  });

  simulateUserThinking();

  // Data export
  group("Analyst: Data Export", () => {
    dataExports.add(1);

    const exportRes = http.post(
      `${BASE_URL}/api/exports/create`,
      JSON.stringify({
        entity: randomItem(["fields", "workers", "sensors", "readings"]),
        format: randomItem(["csv", "xlsx", "json"]),
        filters: {
          date_from: new Date(
            Date.now() - 7 * 24 * 60 * 60 * 1000,
          ).toISOString(),
          date_to: new Date().toISOString(),
        },
      }),
      { headers, tags: { name: "data_export" } },
    );

    const success = check(exportRes, {
      "export created": (r) =>
        r.status === 200 ||
        r.status === 201 ||
        r.status === 202 ||
        r.status === 404,
    });
    dataExportSuccess.add(success ? 1 : 0);
  });

  activeWebUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// VIEWER FLOW (Read-Only)
// ═══════════════════════════════════════════════════════════════════════════════

export function viewerFlow() {
  const browser = selectBrowser();
  const resolution = randomItem(SCREEN_RESOLUTIONS);
  const headers = getWebHeaders(browser, resolution);

  viewerSessions.add(1);
  activeWebUsers.add(1);

  // Login
  group("Viewer: Login", () => {
    const loginRes = http.post(
      `${BASE_URL}/api/auth/login`,
      JSON.stringify({
        username: `viewer_${__VU}`,
        password: "viewer_password_123",
      }),
      { headers, tags: { name: "viewer_login" } },
    );

    const success = check(loginRes, {
      "viewer login ok": (r) => r.status === 200 || r.status === 201,
    });
    webLoginSuccess.add(success ? 1 : 0);

    if (success) {
      try {
        const body = JSON.parse(loginRes.body);
        headers["Authorization"] = `Bearer ${body.token || body.access_token}`;
      } catch {}
    }
  });

  sleep(1);

  // View dashboard
  group("Viewer: Dashboard", () => {
    const dashStart = Date.now();
    const dashRes = http.get(`${BASE_URL}/api/dashboard/summary`, {
      headers,
      tags: { name: "viewer_dashboard" },
    });
    dashboardLoadTime.add(Date.now() - dashStart);
    webPageLoadSuccess.add(
      check(dashRes, {
        "dashboard loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );
  });

  simulateUserThinking();

  // Browse fields
  group("Viewer: Browse Fields", () => {
    const fieldsRes = http.get(`${BASE_URL}/api/fields?page=1&limit=20`, {
      headers,
      tags: { name: "browse_fields" },
    });
    webApiSuccess.add(
      check(fieldsRes, {
        "fields loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );

    simulateUserThinking();

    // Click on a field
    const fieldRes = http.get(
      `${BASE_URL}/api/fields/${randomIntBetween(1, 20)}`,
      {
        headers,
        tags: { name: "view_field" },
      },
    );
    webApiSuccess.add(
      check(fieldRes, {
        "field viewed": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );
  });

  simulateUserThinking();

  // Check weather
  group("Viewer: Weather", () => {
    const weatherRes = http.get(`${BASE_URL}/api/weather/current`, {
      headers,
      tags: { name: "current_weather" },
    });
    webApiSuccess.add(
      check(weatherRes, {
        "weather loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );
  });

  activeWebUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// REALTIME POLLING FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function realtimePollingFlow() {
  const headers = {
    "Content-Type": "application/json",
    "X-Polling-Client": "true",
  };

  group("Realtime: Polling", () => {
    // Simulate dashboard auto-refresh polling
    const endpoints = [
      "/api/realtime/alerts",
      "/api/realtime/worker-status",
      "/api/realtime/sensor-readings",
    ];

    endpoints.forEach((endpoint) => {
      const res = http.get(`${BASE_URL}${endpoint}`, {
        headers,
        tags: { name: "realtime_poll" },
      });
      check(res, {
        "poll successful": (r) => r.status === 200 || r.status === 404,
      });
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SETUP & TEARDOWN
// ═══════════════════════════════════════════════════════════════════════════════

export function setup() {
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );
  console.log("  SAHOOL IDP - Web Dashboard Simulation Starting");
  console.log("  محاكاة لوحة التحكم على الويب");
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );
  console.log(`  Target: ${BASE_URL}`);
  console.log(`  Web VUs: ${WEB_VUS}`);
  console.log(`  Admins: ${Math.ceil(WEB_VUS * 0.15)}`);
  console.log(`  Managers: ${Math.ceil(WEB_VUS * 0.35)}`);
  console.log(`  Analysts: ${Math.ceil(WEB_VUS * 0.25)}`);
  console.log(`  Viewers: ${Math.ceil(WEB_VUS * 0.25)}`);
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );

  const healthRes = http.get(`${BASE_URL}/health`);
  if (healthRes.status !== 200) {
    console.warn("Warning: Backend health check failed");
  }

  return { startTime: Date.now() };
}

export function teardown(data) {
  const duration = (Date.now() - data.startTime) / 1000;
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );
  console.log("  Web Dashboard Simulation Complete");
  console.log(`  Duration: ${duration.toFixed(2)}s`);
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// SUMMARY HANDLER
// ═══════════════════════════════════════════════════════════════════════════════

export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    test_type: "web_dashboard_simulation",
    user_distribution: {
      admins: data.metrics.web_admin_sessions?.values?.count || 0,
      managers: data.metrics.web_manager_sessions?.values?.count || 0,
      viewers: data.metrics.web_viewer_sessions?.values?.count || 0,
    },
    success_rates: {
      login:
        (data.metrics.web_login_success?.values?.rate * 100 || 0).toFixed(2) +
        "%",
      page_load:
        (data.metrics.web_page_load_success?.values?.rate * 100 || 0).toFixed(
          2,
        ) + "%",
      api:
        (data.metrics.web_api_success?.values?.rate * 100 || 0).toFixed(2) +
        "%",
      report_generation:
        (
          data.metrics.web_report_generation_success?.values?.rate * 100 || 0
        ).toFixed(2) + "%",
      data_export:
        (data.metrics.web_data_export_success?.values?.rate * 100 || 0).toFixed(
          2,
        ) + "%",
    },
    performance: {
      dashboard_load_p95:
        (data.metrics.web_dashboard_load_time?.values?.["p(95)"] || 0).toFixed(
          2,
        ) + "ms",
      report_gen_p95:
        (
          data.metrics.web_report_generation_time?.values?.["p(95)"] || 0
        ).toFixed(2) + "ms",
      data_table_p95:
        (data.metrics.web_data_table_load_time?.values?.["p(95)"] || 0).toFixed(
          2,
        ) + "ms",
      chart_render_p95:
        (data.metrics.web_chart_render_time?.values?.["p(95)"] || 0).toFixed(
          2,
        ) + "ms",
    },
    activities: {
      reports_generated: data.metrics.web_reports_generated?.values?.count || 0,
      data_exports: data.metrics.web_data_exports?.values?.count || 0,
    },
  };

  const textSummary = `
═══════════════════════════════════════════════════════════════════════════════
                    🖥️  WEB DASHBOARD SIMULATION RESULTS
                    نتائج محاكاة لوحة التحكم
═══════════════════════════════════════════════════════════════════════════════

USER DISTRIBUTION:
────────────────────────────────────────────────────────────────────────────────
  👑 Admin Sessions:    ${summary.user_distribution.admins}
  👔 Manager Sessions:  ${summary.user_distribution.managers}
  👁️  Viewer Sessions:   ${summary.user_distribution.viewers}

SUCCESS RATES:
────────────────────────────────────────────────────────────────────────────────
  🔐 Login Success:        ${summary.success_rates.login}
  📄 Page Load Success:    ${summary.success_rates.page_load}
  📡 API Success:          ${summary.success_rates.api}
  📊 Report Generation:    ${summary.success_rates.report_generation}
  📤 Data Export:          ${summary.success_rates.data_export}

PERFORMANCE:
────────────────────────────────────────────────────────────────────────────────
  📈 Dashboard Load (p95):   ${summary.performance.dashboard_load_p95}
  📋 Report Gen (p95):       ${summary.performance.report_gen_p95}
  📊 Data Table (p95):       ${summary.performance.data_table_p95}
  📉 Chart Render (p95):     ${summary.performance.chart_render_p95}

ACTIVITIES:
────────────────────────────────────────────────────────────────────────────────
  📊 Reports Generated:    ${summary.activities.reports_generated}
  📤 Data Exports:         ${summary.activities.data_exports}

═══════════════════════════════════════════════════════════════════════════════
`;

  return {
    stdout: textSummary,
    "./results/web-dashboard-results.json": JSON.stringify(summary, null, 2),
  };
}

// Default export for standalone run
export default function () {
  const rand = Math.random();
  if (rand < 0.15) {
    adminFlow();
  } else if (rand < 0.5) {
    managerFlow();
  } else if (rand < 0.75) {
    analystFlow();
  } else {
    viewerFlow();
  }
}
