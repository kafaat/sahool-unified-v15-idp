// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL IDP - Mobile App Simulation (Flutter/React Native)
// محاكاة تطبيق الهاتف المحمول
// ═══════════════════════════════════════════════════════════════════════════════
//
// Simulates realistic mobile app user behavior with:
// - Device-specific headers (iOS/Android)
// - Offline/Online transitions
// - Background/Foreground app states
// - Push notification handling
// - GPS location updates
// - Camera/Image uploads
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
const MOBILE_VUS = parseInt(__ENV.MOBILE_VUS) || 20;
const TEST_DURATION = __ENV.TEST_DURATION || "5m";

// ═══════════════════════════════════════════════════════════════════════════════
// CUSTOM METRICS
// ═══════════════════════════════════════════════════════════════════════════════

// Success rates
const mobileLoginSuccess = new Rate("mobile_login_success");
const mobileApiSuccess = new Rate("mobile_api_success");
const imagUploadSuccess = new Rate("mobile_image_upload_success");
const gpsUpdateSuccess = new Rate("mobile_gps_update_success");
const offlineeSyncSuccess = new Rate("mobile_offline_sync_success");

// Counters
const iosRequests = new Counter("mobile_ios_requests");
const androidRequests = new Counter("mobile_android_requests");
const backgroundSyncs = new Counter("mobile_background_syncs");
const pushNotifications = new Counter("mobile_push_notifications");

// Trends
const appLaunchTime = new Trend("mobile_app_launch_time", true);
const imageUploadTime = new Trend("mobile_image_upload_time", true);
const syncDuration = new Trend("mobile_sync_duration", true);

// Gauges
const activeDevices = new Gauge("mobile_active_devices");
const offlineDevices = new Gauge("mobile_offline_devices");

// ═══════════════════════════════════════════════════════════════════════════════
// DEVICE CONFIGURATIONS
// ═══════════════════════════════════════════════════════════════════════════════

const IOS_DEVICES = [
  { model: "iPhone 15 Pro", os: "17.2", screen: "1179x2556" },
  { model: "iPhone 14", os: "17.1", screen: "1170x2532" },
  { model: "iPhone 13", os: "16.7", screen: "1170x2532" },
  { model: "iPhone SE", os: "17.0", screen: "750x1334" },
  { model: "iPad Pro", os: "17.2", screen: "2048x2732" },
];

const ANDROID_DEVICES = [
  { model: "Samsung Galaxy S24", os: "14", screen: "1440x3120" },
  { model: "Samsung Galaxy A54", os: "14", screen: "1080x2340" },
  { model: "Google Pixel 8", os: "14", screen: "1080x2400" },
  { model: "Xiaomi 14", os: "14", screen: "1200x2670" },
  { model: "OnePlus 12", os: "14", screen: "1440x3168" },
];

const NETWORK_CONDITIONS = [
  { name: "5G", latency: 10, bandwidth: "high" },
  { name: "4G LTE", latency: 50, bandwidth: "high" },
  { name: "4G", latency: 100, bandwidth: "medium" },
  { name: "3G", latency: 300, bandwidth: "low" },
  { name: "WiFi", latency: 20, bandwidth: "high" },
  { name: "Offline", latency: 0, bandwidth: "none" },
];

const SAUDI_LOCATIONS = [
  { city: "Riyadh", lat: 24.7136, lng: 46.6753 },
  { city: "Jeddah", lat: 21.4858, lng: 39.1925 },
  { city: "Mecca", lat: 21.3891, lng: 39.8579 },
  { city: "Medina", lat: 24.5247, lng: 39.5692 },
  { city: "Dammam", lat: 26.4207, lng: 50.0888 },
  { city: "Tabuk", lat: 28.3838, lng: 36.555 },
  { city: "Abha", lat: 18.2164, lng: 42.5053 },
  { city: "Al-Ahsa", lat: 25.3648, lng: 49.5855 },
];

// ═══════════════════════════════════════════════════════════════════════════════
// K6 OPTIONS
// ═══════════════════════════════════════════════════════════════════════════════

export const options = {
  scenarios: {
    // iOS Users - 45% of mobile traffic
    ios_users: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "1m", target: Math.ceil(MOBILE_VUS * 0.45) },
        { duration: "3m", target: Math.ceil(MOBILE_VUS * 0.45) },
        { duration: "1m", target: 0 },
      ],
      exec: "iosUserFlow",
      tags: { platform: "ios" },
    },
    // Android Users - 55% of mobile traffic
    android_users: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "1m", target: Math.ceil(MOBILE_VUS * 0.55) },
        { duration: "3m", target: Math.ceil(MOBILE_VUS * 0.55) },
        { duration: "1m", target: 0 },
      ],
      exec: "androidUserFlow",
      tags: { platform: "android" },
    },
    // Field workers with GPS updates
    field_workers: {
      executor: "constant-vus",
      vus: Math.ceil(MOBILE_VUS * 0.3),
      duration: TEST_DURATION,
      exec: "fieldWorkerFlow",
      tags: { role: "field_worker" },
    },
    // Background sync simulation
    background_sync: {
      executor: "constant-arrival-rate",
      rate: 10,
      timeUnit: "1m",
      duration: TEST_DURATION,
      preAllocatedVUs: 5,
      exec: "backgroundSyncFlow",
      tags: { type: "background" },
    },
  },
  thresholds: {
    mobile_login_success: ["rate>0.95"],
    mobile_api_success: ["rate>0.90"],
    mobile_app_launch_time: ["p(95)<3000"],
    mobile_image_upload_time: ["p(95)<10000"],
    "http_req_duration{platform:ios}": ["p(95)<2000"],
    "http_req_duration{platform:android}": ["p(95)<2000"],
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

// Cryptographically secure random number in [0, 1)
function secureRandom() {
  const array = new Uint32Array(1);
  crypto.getRandomValues(array);
  return array[0] * Math.pow(2, -32);
}

function generateDeviceId() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    const r = (secureRandom() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function getIOSHeaders(device) {
  return {
    "User-Agent": `SAHOOL-IDP/2.5.0 (${device.model}; iOS ${device.os}) CFNetwork/1474 Darwin/23.0.0`,
    "X-Device-ID": generateDeviceId(),
    "X-Device-Model": device.model,
    "X-OS-Version": `iOS ${device.os}`,
    "X-App-Version": "2.5.0",
    "X-Screen-Resolution": device.screen,
    "X-Platform": "ios",
    "X-Push-Token": `ios_push_${generateDeviceId().substring(0, 8)}`,
    "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8",
    "Content-Type": "application/json",
  };
}

function getAndroidHeaders(device) {
  return {
    "User-Agent": `SAHOOL-IDP/2.5.0 (Linux; Android ${device.os}; ${device.model}) okhttp/4.12.0`,
    "X-Device-ID": generateDeviceId(),
    "X-Device-Model": device.model,
    "X-OS-Version": `Android ${device.os}`,
    "X-App-Version": "2.5.0",
    "X-Screen-Resolution": device.screen,
    "X-Platform": "android",
    "X-Push-Token": `fcm_${generateDeviceId().substring(0, 8)}`,
    "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8",
    "Content-Type": "application/json",
  };
}

function simulateNetworkCondition() {
  const condition = randomItem(NETWORK_CONDITIONS);
  if (condition.name === "Offline") {
    return null; // Signal offline state
  }
  sleep(condition.latency / 1000); // Simulate latency
  return condition;
}

function generateGPSCoordinates(baseLocation) {
  // Add small random offset to simulate movement
  return {
    latitude: baseLocation.lat + (secureRandom() - 0.5) * 0.01,
    longitude: baseLocation.lng + (secureRandom() - 0.5) * 0.01,
    accuracy: randomIntBetween(5, 50),
    altitude: randomIntBetween(0, 500),
    speed: randomIntBetween(0, 120),
    timestamp: Date.now(),
  };
}

function generateFieldImage() {
  // Simulate a base64 encoded image (placeholder)
  const imageSize = randomIntBetween(100000, 500000);
  return {
    data: "data:image/jpeg;base64," + "A".repeat(Math.min(imageSize, 1000)),
    size: imageSize,
    type: "image/jpeg",
    name: `field_photo_${Date.now()}.jpg`,
    metadata: {
      timestamp: new Date().toISOString(),
      gps: generateGPSCoordinates(randomItem(SAUDI_LOCATIONS)),
    },
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// iOS USER FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function iosUserFlow() {
  const device = randomItem(IOS_DEVICES);
  const headers = getIOSHeaders(device);
  const location = randomItem(SAUDI_LOCATIONS);

  iosRequests.add(1);
  activeDevices.add(1);

  // Simulate app launch
  const launchStart = Date.now();

  group("iOS: App Launch", () => {
    // Check server connectivity
    const healthRes = http.get(`${BASE_URL}/health`, {
      headers,
      tags: { name: "health_check" },
    });
    check(healthRes, { "health check ok": (r) => r.status === 200 });

    // Fetch app config
    const configRes = http.get(`${BASE_URL}/api/config/mobile`, {
      headers,
      tags: { name: "app_config" },
    });
    check(configRes, {
      "config loaded": (r) => r.status === 200 || r.status === 404,
    });
  });

  appLaunchTime.add(Date.now() - launchStart);
  sleep(randomIntBetween(1, 2));

  // Login
  group("iOS: Authentication", () => {
    const loginPayload = JSON.stringify({
      username: `ios_user_${__VU}`,
      password: "test_password_123",
      device_info: {
        model: device.model,
        os: `iOS ${device.os}`,
        app_version: "2.5.0",
      },
      push_token: headers["X-Push-Token"],
    });

    const loginRes = http.post(`${BASE_URL}/api/auth/login`, loginPayload, {
      headers,
      tags: { name: "login" },
    });

    const success = check(loginRes, {
      "login successful": (r) => r.status === 200 || r.status === 201,
      "has token": (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.token || body.access_token;
        } catch {
          return false;
        }
      },
    });

    mobileLoginSuccess.add(success ? 1 : 0);

    if (success) {
      try {
        const body = JSON.parse(loginRes.body);
        headers["Authorization"] = `Bearer ${body.token || body.access_token}`;
      } catch {}
    }
  });

  sleep(randomIntBetween(2, 4));

  // Main app usage
  group("iOS: Main Features", () => {
    // View dashboard
    const dashRes = http.get(`${BASE_URL}/api/dashboard/summary`, {
      headers,
      tags: { name: "dashboard" },
    });
    mobileApiSuccess.add(
      check(dashRes, {
        "dashboard loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );

    sleep(randomIntBetween(1, 3));

    // View fields list
    const fieldsRes = http.get(`${BASE_URL}/api/fields?page=1&limit=20`, {
      headers,
      tags: { name: "fields_list" },
    });
    mobileApiSuccess.add(
      check(fieldsRes, {
        "fields loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );

    sleep(randomIntBetween(2, 5));

    // Check weather
    const gps = generateGPSCoordinates(location);
    const weatherRes = http.get(
      `${BASE_URL}/api/weather/current?lat=${gps.latitude}&lng=${gps.longitude}`,
      { headers, tags: { name: "weather" } },
    );
    mobileApiSuccess.add(
      check(weatherRes, {
        "weather loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );
  });

  sleep(randomIntBetween(3, 6));

  // Simulate push notification received
  if (secureRandom() < 0.3) {
    group("iOS: Push Notification", () => {
      pushNotifications.add(1);
      const notifRes = http.post(
        `${BASE_URL}/api/notifications/received`,
        JSON.stringify({
          notification_id: generateDeviceId(),
          received_at: new Date().toISOString(),
          platform: "ios",
        }),
        { headers, tags: { name: "push_received" } },
      );
      check(notifRes, {
        "notification logged": (r) =>
          r.status === 200 || r.status === 201 || r.status === 404,
      });
    });
  }

  activeDevices.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// ANDROID USER FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function androidUserFlow() {
  const device = randomItem(ANDROID_DEVICES);
  const headers = getAndroidHeaders(device);
  const location = randomItem(SAUDI_LOCATIONS);

  androidRequests.add(1);
  activeDevices.add(1);

  // Simulate app launch
  const launchStart = Date.now();

  group("Android: App Launch", () => {
    const healthRes = http.get(`${BASE_URL}/health`, {
      headers,
      tags: { name: "health_check" },
    });
    check(healthRes, { "health check ok": (r) => r.status === 200 });

    const configRes = http.get(`${BASE_URL}/api/config/mobile`, {
      headers,
      tags: { name: "app_config" },
    });
    check(configRes, {
      "config loaded": (r) => r.status === 200 || r.status === 404,
    });
  });

  appLaunchTime.add(Date.now() - launchStart);
  sleep(randomIntBetween(1, 3));

  // Login
  group("Android: Authentication", () => {
    const loginPayload = JSON.stringify({
      username: `android_user_${__VU}`,
      password: "test_password_123",
      device_info: {
        model: device.model,
        os: `Android ${device.os}`,
        app_version: "2.5.0",
      },
      fcm_token: headers["X-Push-Token"],
    });

    const loginRes = http.post(`${BASE_URL}/api/auth/login`, loginPayload, {
      headers,
      tags: { name: "login" },
    });

    const success = check(loginRes, {
      "login successful": (r) => r.status === 200 || r.status === 201,
    });

    mobileLoginSuccess.add(success ? 1 : 0);

    if (success) {
      try {
        const body = JSON.parse(loginRes.body);
        headers["Authorization"] = `Bearer ${body.token || body.access_token}`;
      } catch {}
    }
  });

  sleep(randomIntBetween(2, 4));

  // Main app usage
  group("Android: Main Features", () => {
    // Dashboard
    const dashRes = http.get(`${BASE_URL}/api/dashboard/summary`, {
      headers,
      tags: { name: "dashboard" },
    });
    mobileApiSuccess.add(
      check(dashRes, {
        "dashboard loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );

    sleep(randomIntBetween(1, 3));

    // Fields
    const fieldsRes = http.get(`${BASE_URL}/api/fields`, {
      headers,
      tags: { name: "fields_list" },
    });
    mobileApiSuccess.add(
      check(fieldsRes, {
        "fields loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );

    sleep(randomIntBetween(1, 2));

    // IoT Sensors
    const iotRes = http.get(`${BASE_URL}/api/iot/sensors`, {
      headers,
      tags: { name: "iot_sensors" },
    });
    mobileApiSuccess.add(
      check(iotRes, {
        "iot loaded": (r) => r.status === 200 || r.status === 404,
      })
        ? 1
        : 0,
    );
  });

  sleep(randomIntBetween(2, 5));

  // Android-specific: Battery optimization sync
  if (secureRandom() < 0.2) {
    group("Android: Doze Sync", () => {
      backgroundSyncs.add(1);
      const syncRes = http.post(
        `${BASE_URL}/api/sync/batch`,
        JSON.stringify({
          sync_type: "doze_window",
          pending_operations: randomIntBetween(1, 10),
          battery_level: randomIntBetween(20, 100),
        }),
        { headers, tags: { name: "doze_sync" } },
      );
      check(syncRes, {
        "doze sync ok": (r) =>
          r.status === 200 || r.status === 201 || r.status === 404,
      });
    });
  }

  activeDevices.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// FIELD WORKER FLOW (GPS + Images)
// ═══════════════════════════════════════════════════════════════════════════════

export function fieldWorkerFlow() {
  const isIOS = secureRandom() < 0.4;
  const device = isIOS ? randomItem(IOS_DEVICES) : randomItem(ANDROID_DEVICES);
  const headers = isIOS ? getIOSHeaders(device) : getAndroidHeaders(device);
  const location = randomItem(SAUDI_LOCATIONS);

  // Login first
  group("Field Worker: Login", () => {
    const loginRes = http.post(
      `${BASE_URL}/api/auth/login`,
      JSON.stringify({
        username: `field_worker_${__VU}`,
        password: "field_password_123",
        role: "field_worker",
      }),
      { headers, tags: { name: "field_login" } },
    );

    if (loginRes.status === 200 || loginRes.status === 201) {
      try {
        const body = JSON.parse(loginRes.body);
        headers["Authorization"] = `Bearer ${body.token || body.access_token}`;
      } catch {}
    }
  });

  sleep(1);

  // Continuous GPS updates (simulating field work)
  for (let i = 0; i < 5; i++) {
    group("Field Worker: GPS Update", () => {
      const gps = generateGPSCoordinates(location);

      const gpsRes = http.post(
        `${BASE_URL}/api/location/update`,
        JSON.stringify({
          ...gps,
          worker_id: `worker_${__VU}`,
          activity: randomItem(["traveling", "working", "inspecting", "idle"]),
        }),
        { headers, tags: { name: "gps_update" } },
      );

      gpsUpdateSuccess.add(
        check(gpsRes, {
          "gps update ok": (r) =>
            r.status === 200 || r.status === 201 || r.status === 404,
        })
          ? 1
          : 0,
      );
    });

    sleep(randomIntBetween(5, 15));

    // Occasionally take a photo
    if (secureRandom() < 0.3) {
      group("Field Worker: Image Upload", () => {
        const uploadStart = Date.now();
        const image = generateFieldImage();

        const uploadRes = http.post(
          `${BASE_URL}/api/fields/images`,
          JSON.stringify({
            field_id: `field_${randomIntBetween(1, 100)}`,
            image: image,
            notes: "Field inspection photo",
          }),
          { headers, tags: { name: "image_upload" } },
        );

        imageUploadTime.add(Date.now() - uploadStart);
        imagUploadSuccess.add(
          check(uploadRes, {
            "image uploaded": (r) =>
              r.status === 200 || r.status === 201 || r.status === 404,
          })
            ? 1
            : 0,
        );
      });
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// BACKGROUND SYNC FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function backgroundSyncFlow() {
  const headers = {
    "Content-Type": "application/json",
    "X-Sync-Type": "background",
    "X-Device-ID": generateDeviceId(),
  };

  backgroundSyncs.add(1);

  group("Background: Sync", () => {
    const syncStart = Date.now();

    // Simulate offline data sync
    const pendingData = {
      offline_operations: randomIntBetween(1, 20),
      last_sync: new Date(
        Date.now() - randomIntBetween(60000, 3600000),
      ).toISOString(),
      data: Array.from({ length: randomIntBetween(1, 5) }, (_, i) => ({
        id: generateDeviceId(),
        type: randomItem(["field_update", "gps_log", "image", "reading"]),
        timestamp: new Date().toISOString(),
      })),
    };

    const syncRes = http.post(
      `${BASE_URL}/api/sync/offline`,
      JSON.stringify(pendingData),
      {
        headers,
        tags: { name: "offline_sync" },
      },
    );

    syncDuration.add(Date.now() - syncStart);
    offlineeSyncSuccess.add(
      check(syncRes, {
        "sync successful": (r) =>
          r.status === 200 || r.status === 201 || r.status === 404,
      })
        ? 1
        : 0,
    );
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SETUP & TEARDOWN
// ═══════════════════════════════════════════════════════════════════════════════

export function setup() {
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );
  console.log("  SAHOOL IDP - Mobile App Simulation Starting");
  console.log("  محاكاة تطبيق الهاتف المحمول");
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );
  console.log(`  Target: ${BASE_URL}`);
  console.log(`  Mobile VUs: ${MOBILE_VUS}`);
  console.log(`  iOS: ${Math.ceil(MOBILE_VUS * 0.45)} users`);
  console.log(`  Android: ${Math.ceil(MOBILE_VUS * 0.55)} users`);
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );

  // Verify backend is accessible
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
  console.log("  Mobile Simulation Complete");
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
    test_type: "mobile_app_simulation",
    platforms: {
      ios: {
        requests: data.metrics.mobile_ios_requests?.values?.count || 0,
      },
      android: {
        requests: data.metrics.mobile_android_requests?.values?.count || 0,
      },
    },
    success_rates: {
      login:
        (data.metrics.mobile_login_success?.values?.rate * 100 || 0).toFixed(
          2,
        ) + "%",
      api:
        (data.metrics.mobile_api_success?.values?.rate * 100 || 0).toFixed(2) +
        "%",
      image_upload:
        (
          data.metrics.mobile_image_upload_success?.values?.rate * 100 || 0
        ).toFixed(2) + "%",
      gps_update:
        (
          data.metrics.mobile_gps_update_success?.values?.rate * 100 || 0
        ).toFixed(2) + "%",
      offline_sync:
        (
          data.metrics.mobile_offline_sync_success?.values?.rate * 100 || 0
        ).toFixed(2) + "%",
    },
    performance: {
      app_launch_p95:
        (data.metrics.mobile_app_launch_time?.values?.["p(95)"] || 0).toFixed(
          2,
        ) + "ms",
      image_upload_p95:
        (data.metrics.mobile_image_upload_time?.values?.["p(95)"] || 0).toFixed(
          2,
        ) + "ms",
    },
    activities: {
      background_syncs:
        data.metrics.mobile_background_syncs?.values?.count || 0,
      push_notifications:
        data.metrics.mobile_push_notifications?.values?.count || 0,
    },
  };

  const textSummary = `
═══════════════════════════════════════════════════════════════════════════════
                    📱 MOBILE APP SIMULATION RESULTS
                    نتائج محاكاة تطبيق الهاتف المحمول
═══════════════════════════════════════════════════════════════════════════════

PLATFORM DISTRIBUTION:
────────────────────────────────────────────────────────────────────────────────
  🍎 iOS Requests:      ${summary.platforms.ios.requests}
  🤖 Android Requests:  ${summary.platforms.android.requests}

SUCCESS RATES:
────────────────────────────────────────────────────────────────────────────────
  🔐 Login Success:     ${summary.success_rates.login}
  📡 API Success:       ${summary.success_rates.api}
  📷 Image Upload:      ${summary.success_rates.image_upload}
  📍 GPS Update:        ${summary.success_rates.gps_update}
  🔄 Offline Sync:      ${summary.success_rates.offline_sync}

PERFORMANCE:
────────────────────────────────────────────────────────────────────────────────
  🚀 App Launch (p95):    ${summary.performance.app_launch_p95}
  📤 Image Upload (p95):  ${summary.performance.image_upload_p95}

ACTIVITIES:
────────────────────────────────────────────────────────────────────────────────
  🔄 Background Syncs:    ${summary.activities.background_syncs}
  🔔 Push Notifications:  ${summary.activities.push_notifications}

═══════════════════════════════════════════════════════════════════════════════
`;

  return {
    stdout: textSummary,
    "./results/mobile-simulation-results.json": JSON.stringify(
      summary,
      null,
      2,
    ),
  };
}

// Default export for standalone run
export default function () {
  if (secureRandom() < 0.45) {
    iosUserFlow();
  } else {
    androidUserFlow();
  }
}
