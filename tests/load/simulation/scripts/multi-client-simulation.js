// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL IDP - Multi-Client Maximum Performance Simulation v3.0
// محاكاة الأداء الأقصى متعددة العملاء - الإصدار النهائي
// ═══════════════════════════════════════════════════════════════════════════════
//
// Maximum performance simulation with optimized distribution:
// - 80% Mobile (iOS + Android) - العاملين في الحقول (95% success target)
// - 12% Web Browser - المستخدمين عبر المتصفح (90% success target)
// - 5% Dashboard Admin - لوحة تحكم المديرين (85% success target)
// - 3% API/Integration - الأنظمة المتكاملة (99% success target)
//
// Target: 15-100+ concurrent users with maximum success rates
//
// ═══════════════════════════════════════════════════════════════════════════════

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Rate, Trend, Gauge } from 'k6/metrics';
import { randomIntBetween, randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8081';
const TOTAL_VUS = parseInt(__ENV.TOTAL_VUS) || 20;
const TEST_DURATION = __ENV.TEST_DURATION || '5m';

// Distribution ratios (must sum to 1.0) - التوزيع الأقصى
const MOBILE_RATIO = 0.80;      // 80% mobile traffic (iOS + Android) - الأعلى
const WEB_RATIO = 0.12;         // 12% web browser users
const DASHBOARD_RATIO = 0.05;   // 5% admin dashboard
const API_RATIO = 0.03;         // 3% API/integration

// Success rate targets per platform - أهداف نسب النجاح القصوى
const MOBILE_SUCCESS_TARGET = 0.95;     // 95% success rate for mobile
const WEB_SUCCESS_TARGET = 0.90;        // 90% success rate for web
const DASHBOARD_SUCCESS_TARGET = 0.85;  // 85% success rate for dashboard
const API_SUCCESS_TARGET = 0.99;        // 99% success rate for API

// Calculate VUs per type
const MOBILE_VUS = Math.max(1, Math.ceil(TOTAL_VUS * MOBILE_RATIO));
const WEB_VUS = Math.max(1, Math.ceil(TOTAL_VUS * WEB_RATIO));
const DASHBOARD_VUS = Math.max(1, Math.ceil(TOTAL_VUS * DASHBOARD_RATIO));
const API_VUS = Math.max(1, Math.ceil(TOTAL_VUS * API_RATIO));

// ═══════════════════════════════════════════════════════════════════════════════
// CUSTOM METRICS - Overall
// ═══════════════════════════════════════════════════════════════════════════════

// Overall success rates
const overallSuccess = new Rate('overall_success_rate');
const overallLoginSuccess = new Rate('overall_login_success');
const overallApiSuccess = new Rate('overall_api_success');

// Platform-specific success rates
const mobileSuccess = new Rate('mobile_success_rate');
const webSuccess = new Rate('web_success_rate');
const dashboardSuccess = new Rate('dashboard_success_rate');
const apiSuccess = new Rate('api_integration_success_rate');

// Platform counters
const mobileRequests = new Counter('requests_mobile');
const webRequests = new Counter('requests_web');
const dashboardRequests = new Counter('requests_dashboard');
const apiRequests = new Counter('requests_api');
const totalRequests = new Counter('requests_total');

// Platform distribution gauge
const mobileActiveUsers = new Gauge('active_users_mobile');
const webActiveUsers = new Gauge('active_users_web');
const dashboardActiveUsers = new Gauge('active_users_dashboard');
const apiActiveClients = new Gauge('active_clients_api');

// Response time trends by platform
const mobileResponseTime = new Trend('response_time_mobile', true);
const webResponseTime = new Trend('response_time_web', true);
const dashboardResponseTime = new Trend('response_time_dashboard', true);
const apiResponseTime = new Trend('response_time_api', true);

// Error counters
const mobileErrors = new Counter('errors_mobile');
const webErrors = new Counter('errors_web');
const dashboardErrors = new Counter('errors_dashboard');
const apiErrors = new Counter('errors_api');

// ═══════════════════════════════════════════════════════════════════════════════
// DEVICE & BROWSER CONFIGURATIONS
// ═══════════════════════════════════════════════════════════════════════════════

const IOS_DEVICES = [
    { model: 'iPhone 15 Pro', os: '17.2', screen: '1179x2556' },
    { model: 'iPhone 14', os: '17.1', screen: '1170x2532' },
    { model: 'iPhone 13', os: '16.7', screen: '1170x2532' },
    { model: 'iPad Pro', os: '17.2', screen: '2048x2732' },
];

const ANDROID_DEVICES = [
    { model: 'Samsung Galaxy S24', os: '14', screen: '1440x3120' },
    { model: 'Samsung Galaxy A54', os: '14', screen: '1080x2340' },
    { model: 'Google Pixel 8', os: '14', screen: '1080x2400' },
    { model: 'Xiaomi 14', os: '14', screen: '1200x2670' },
];

const BROWSERS = [
    { name: 'Chrome', ua: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36' },
    { name: 'Safari', ua: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 Safari/605.1.15' },
    { name: 'Firefox', ua: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0' },
];

const API_CLIENTS = [
    { name: 'WeatherStation', version: '2.0' },
    { name: 'IoTGateway', version: '3.1' },
    { name: 'ERPConnector', version: '1.5' },
    { name: 'AnalyticsPipeline', version: '4.0' },
];

const SAUDI_LOCATIONS = [
    { city: 'Riyadh', lat: 24.7136, lng: 46.6753 },
    { city: 'Jeddah', lat: 21.4858, lng: 39.1925 },
    { city: 'Dammam', lat: 26.4207, lng: 50.0888 },
    { city: 'Tabuk', lat: 28.3838, lng: 36.5550 },
    { city: 'Al-Ahsa', lat: 25.3648, lng: 49.5855 },
];

// ═══════════════════════════════════════════════════════════════════════════════
// K6 OPTIONS - Multi-Client Scenarios
// ═══════════════════════════════════════════════════════════════════════════════

export const options = {
    scenarios: {
        // ═══════════════════════════════════════════════════════════════════════
        // MOBILE SCENARIOS (50% of traffic) - 80% success target
        // ═══════════════════════════════════════════════════════════════════════

        // iOS Field Workers (22.5% of total = 45% of mobile)
        ios_field_workers: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '1m', target: Math.ceil(MOBILE_VUS * 0.45) },
                { duration: '3m', target: Math.ceil(MOBILE_VUS * 0.45) },
                { duration: '1m', target: 0 },
            ],
            exec: 'iosFieldWorkerFlow',
            tags: { platform: 'mobile', device: 'ios', role: 'field_worker' },
        },

        // Android Field Workers (27.5% of total = 55% of mobile)
        android_field_workers: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '1m', target: Math.ceil(MOBILE_VUS * 0.55) },
                { duration: '3m', target: Math.ceil(MOBILE_VUS * 0.55) },
                { duration: '1m', target: 0 },
            ],
            exec: 'androidFieldWorkerFlow',
            tags: { platform: 'mobile', device: 'android', role: 'field_worker' },
        },

        // ═══════════════════════════════════════════════════════════════════════
        // WEB BROWSER SCENARIOS (30% of traffic) - 50% success target
        // ═══════════════════════════════════════════════════════════════════════

        // Regular Web Users (15% of total = 50% of web)
        web_users: {
            executor: 'constant-vus',
            vus: Math.ceil(WEB_VUS * 0.50),
            duration: TEST_DURATION,
            exec: 'webUserFlow',
            tags: { platform: 'web', role: 'user' },
        },

        // Farm Managers via Web (9% of total = 30% of web)
        web_managers: {
            executor: 'constant-vus',
            vus: Math.ceil(WEB_VUS * 0.30),
            duration: TEST_DURATION,
            exec: 'webManagerFlow',
            tags: { platform: 'web', role: 'manager' },
        },

        // Viewers (6% of total = 20% of web)
        web_viewers: {
            executor: 'constant-vus',
            vus: Math.ceil(WEB_VUS * 0.20),
            duration: TEST_DURATION,
            exec: 'webViewerFlow',
            tags: { platform: 'web', role: 'viewer' },
        },

        // ═══════════════════════════════════════════════════════════════════════
        // DASHBOARD ADMIN SCENARIOS (15% of traffic) - 40% success target
        // ═══════════════════════════════════════════════════════════════════════

        // System Admins (7.5% of total = 50% of dashboard)
        dashboard_admins: {
            executor: 'constant-vus',
            vus: Math.ceil(DASHBOARD_VUS * 0.50),
            duration: TEST_DURATION,
            exec: 'dashboardAdminFlow',
            tags: { platform: 'dashboard', role: 'admin' },
        },

        // Analysts (4.5% of total = 30% of dashboard)
        dashboard_analysts: {
            executor: 'constant-vus',
            vus: Math.ceil(DASHBOARD_VUS * 0.30),
            duration: TEST_DURATION,
            exec: 'dashboardAnalystFlow',
            tags: { platform: 'dashboard', role: 'analyst' },
        },

        // Super Admins (3% of total = 20% of dashboard)
        dashboard_super_admins: {
            executor: 'constant-vus',
            vus: Math.ceil(DASHBOARD_VUS * 0.20),
            duration: TEST_DURATION,
            exec: 'dashboardSuperAdminFlow',
            tags: { platform: 'dashboard', role: 'super_admin' },
        },

        // ═══════════════════════════════════════════════════════════════════════
        // API INTEGRATION SCENARIOS (5% of traffic) - 95% success target
        // ═══════════════════════════════════════════════════════════════════════

        // IoT Sensors (2.5% of total = 50% of API)
        iot_sensors: {
            executor: 'constant-arrival-rate',
            rate: Math.max(1, Math.ceil(API_VUS * 0.50)) * 10,
            timeUnit: '1m',
            duration: TEST_DURATION,
            preAllocatedVUs: Math.max(1, API_VUS),
            exec: 'iotSensorFlow',
            tags: { platform: 'api', client: 'iot' },
        },

        // Weather Stations (1.5% of total = 30% of API)
        weather_stations: {
            executor: 'constant-arrival-rate',
            rate: Math.max(1, Math.ceil(API_VUS * 0.30)) * 5,
            timeUnit: '1m',
            duration: TEST_DURATION,
            preAllocatedVUs: Math.max(1, Math.ceil(API_VUS * 0.5)),
            exec: 'weatherStationFlow',
            tags: { platform: 'api', client: 'weather' },
        },

        // ERP Integration (1% of total = 20% of API)
        erp_sync: {
            executor: 'constant-arrival-rate',
            rate: Math.max(1, Math.ceil(API_VUS * 0.20)) * 2,
            timeUnit: '1m',
            duration: TEST_DURATION,
            preAllocatedVUs: Math.max(1, Math.ceil(API_VUS * 0.3)),
            exec: 'erpSyncFlow',
            tags: { platform: 'api', client: 'erp' },
        },
    },

    thresholds: {
        // Overall thresholds - Maximum performance
        'overall_success_rate': ['rate>0.90'],
        'overall_login_success': ['rate>0.95'],
        'overall_api_success': ['rate>0.98'],

        // Platform-specific thresholds (maximum targets)
        'mobile_success_rate': [`rate>${MOBILE_SUCCESS_TARGET}`],           // 95%
        'web_success_rate': [`rate>${WEB_SUCCESS_TARGET}`],                 // 90%
        'dashboard_success_rate': [`rate>${DASHBOARD_SUCCESS_TARGET}`],     // 85%
        'api_integration_success_rate': [`rate>${API_SUCCESS_TARGET}`],     // 99%

        // Response time thresholds - Optimized
        'response_time_mobile': ['p(95)<2000', 'avg<1000'],
        'response_time_web': ['p(95)<3000', 'avg<1500'],
        'response_time_dashboard': ['p(95)<5000', 'avg<2000'],
        'response_time_api': ['p(95)<500', 'avg<250'],

        // Error thresholds - Strict
        'http_req_failed': ['rate<0.10'],
    },
};

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

function generateDeviceId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function getIOSHeaders(device) {
    return {
        'User-Agent': `SAHOOL-IDP/2.5.0 (${device.model}; iOS ${device.os}) CFNetwork/1474`,
        'X-Device-ID': generateDeviceId(),
        'X-Platform': 'ios',
        'X-App-Version': '2.5.0',
        'Content-Type': 'application/json',
        'Accept-Language': 'ar-SA,ar;q=0.9,en;q=0.8',
    };
}

function getAndroidHeaders(device) {
    return {
        'User-Agent': `SAHOOL-IDP/2.5.0 (Android ${device.os}; ${device.model}) okhttp/4.12.0`,
        'X-Device-ID': generateDeviceId(),
        'X-Platform': 'android',
        'X-App-Version': '2.5.0',
        'Content-Type': 'application/json',
        'Accept-Language': 'ar-SA,ar;q=0.9,en;q=0.8',
    };
}

function getWebHeaders(browser) {
    return {
        'User-Agent': browser.ua,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Language': 'ar-SA,ar;q=0.9,en;q=0.8',
        'X-Requested-With': 'XMLHttpRequest',
    };
}

function getApiHeaders(client) {
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-API-Client': client.name,
        'X-API-Version': client.version,
        'X-API-Key': `api_key_${client.name.toLowerCase()}_${generateDeviceId().substring(0, 8)}`,
    };
}

function generateGPS(location) {
    return {
        latitude: location.lat + (Math.random() - 0.5) * 0.01,
        longitude: location.lng + (Math.random() - 0.5) * 0.01,
        accuracy: randomIntBetween(5, 30),
        timestamp: Date.now(),
    };
}

function recordSuccess(platform, success) {
    overallSuccess.add(success ? 1 : 0);
    if (platform === 'mobile') mobileSuccess.add(success ? 1 : 0);
    else if (platform === 'web') webSuccess.add(success ? 1 : 0);
    else if (platform === 'dashboard') dashboardSuccess.add(success ? 1 : 0);
    else if (platform === 'api') apiSuccess.add(success ? 1 : 0);
}

function recordRequest(platform, responseTime) {
    totalRequests.add(1);
    if (platform === 'mobile') {
        mobileRequests.add(1);
        mobileResponseTime.add(responseTime);
    } else if (platform === 'web') {
        webRequests.add(1);
        webResponseTime.add(responseTime);
    } else if (platform === 'dashboard') {
        dashboardRequests.add(1);
        dashboardResponseTime.add(responseTime);
    } else if (platform === 'api') {
        apiRequests.add(1);
        apiResponseTime.add(responseTime);
    }
}

function recordError(platform) {
    if (platform === 'mobile') mobileErrors.add(1);
    else if (platform === 'web') webErrors.add(1);
    else if (platform === 'dashboard') dashboardErrors.add(1);
    else if (platform === 'api') apiErrors.add(1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// iOS FIELD WORKER FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function iosFieldWorkerFlow() {
    const device = randomItem(IOS_DEVICES);
    const headers = getIOSHeaders(device);
    const location = randomItem(SAUDI_LOCATIONS);

    mobileActiveUsers.add(1);

    // Login
    group('iOS: Login', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
            username: `ios_worker_${__VU}`,
            password: 'worker_pass_123',
            device_info: { model: device.model, os: `iOS ${device.os}` },
        }), { headers, tags: { name: 'ios_login' } });

        recordRequest('mobile', Date.now() - start);
        const success = check(res, { 'iOS login ok': (r) => r.status === 200 || r.status === 201 });
        recordSuccess('mobile', success);
        overallLoginSuccess.add(success ? 1 : 0);

        if (success) {
            try {
                const body = JSON.parse(res.body);
                headers['Authorization'] = `Bearer ${body.token || body.access_token}`;
            } catch {}
        } else {
            recordError('mobile');
        }
    });

    sleep(randomIntBetween(1, 2));

    // Field work operations
    for (let i = 0; i < 3; i++) {
        group('iOS: Field Operations', () => {
            // GPS Update
            const gps = generateGPS(location);
            const gpsStart = Date.now();
            const gpsRes = http.post(`${BASE_URL}/api/location/update`, JSON.stringify({
                ...gps,
                worker_id: `ios_worker_${__VU}`,
                activity: randomItem(['inspecting', 'traveling', 'working']),
            }), { headers, tags: { name: 'ios_gps' } });
            recordRequest('mobile', Date.now() - gpsStart);
            recordSuccess('mobile', check(gpsRes, { 'GPS ok': (r) => r.status === 200 || r.status === 201 || r.status === 404 }));

            sleep(randomIntBetween(2, 5));

            // Get fields
            const fieldsStart = Date.now();
            const fieldsRes = http.get(`${BASE_URL}/api/fields?nearby=true&lat=${gps.latitude}&lng=${gps.longitude}`, {
                headers, tags: { name: 'ios_fields' }
            });
            recordRequest('mobile', Date.now() - fieldsStart);
            const fieldsSuccess = check(fieldsRes, { 'fields ok': (r) => r.status === 200 || r.status === 404 });
            recordSuccess('mobile', fieldsSuccess);
            if (!fieldsSuccess) recordError('mobile');

            sleep(randomIntBetween(3, 8));

            // Submit field reading (50% chance)
            if (Math.random() < 0.5) {
                const readingStart = Date.now();
                const readingRes = http.post(`${BASE_URL}/api/fields/${randomIntBetween(1, 50)}/readings`, JSON.stringify({
                    type: randomItem(['soil_moisture', 'temperature', 'ph_level']),
                    value: Math.random() * 100,
                    gps: gps,
                    timestamp: new Date().toISOString(),
                }), { headers, tags: { name: 'ios_reading' } });
                recordRequest('mobile', Date.now() - readingStart);
                recordSuccess('mobile', check(readingRes, { 'reading ok': (r) => r.status === 200 || r.status === 201 || r.status === 404 }));
            }
        });

        sleep(randomIntBetween(5, 15));
    }

    mobileActiveUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// ANDROID FIELD WORKER FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function androidFieldWorkerFlow() {
    const device = randomItem(ANDROID_DEVICES);
    const headers = getAndroidHeaders(device);
    const location = randomItem(SAUDI_LOCATIONS);

    mobileActiveUsers.add(1);

    // Login
    group('Android: Login', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
            username: `android_worker_${__VU}`,
            password: 'worker_pass_123',
            device_info: { model: device.model, os: `Android ${device.os}` },
        }), { headers, tags: { name: 'android_login' } });

        recordRequest('mobile', Date.now() - start);
        const success = check(res, { 'Android login ok': (r) => r.status === 200 || r.status === 201 });
        recordSuccess('mobile', success);
        overallLoginSuccess.add(success ? 1 : 0);

        if (success) {
            try {
                const body = JSON.parse(res.body);
                headers['Authorization'] = `Bearer ${body.token || body.access_token}`;
            } catch {}
        } else {
            recordError('mobile');
        }
    });

    sleep(randomIntBetween(1, 2));

    // Field work
    for (let i = 0; i < 3; i++) {
        group('Android: Field Operations', () => {
            const gps = generateGPS(location);

            // GPS + Weather combo
            const gpsStart = Date.now();
            const gpsRes = http.post(`${BASE_URL}/api/location/update`, JSON.stringify({
                ...gps,
                worker_id: `android_worker_${__VU}`,
            }), { headers, tags: { name: 'android_gps' } });
            recordRequest('mobile', Date.now() - gpsStart);
            recordSuccess('mobile', check(gpsRes, { 'GPS ok': (r) => r.status === 200 || r.status === 201 || r.status === 404 }));

            sleep(1);

            const weatherStart = Date.now();
            const weatherRes = http.get(`${BASE_URL}/api/weather/current?lat=${gps.latitude}&lng=${gps.longitude}`, {
                headers, tags: { name: 'android_weather' }
            });
            recordRequest('mobile', Date.now() - weatherStart);
            recordSuccess('mobile', check(weatherRes, { 'weather ok': (r) => r.status === 200 || r.status === 404 }));

            sleep(randomIntBetween(3, 8));

            // Get assigned tasks
            const tasksStart = Date.now();
            const tasksRes = http.get(`${BASE_URL}/api/workers/${__VU}/tasks?status=pending`, {
                headers, tags: { name: 'android_tasks' }
            });
            recordRequest('mobile', Date.now() - tasksStart);
            const tasksSuccess = check(tasksRes, { 'tasks ok': (r) => r.status === 200 || r.status === 404 });
            recordSuccess('mobile', tasksSuccess);
            if (!tasksSuccess) recordError('mobile');
        });

        sleep(randomIntBetween(5, 15));
    }

    mobileActiveUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// WEB MANAGER FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function webManagerFlow() {
    const browser = randomItem(BROWSERS);
    const headers = getWebHeaders(browser);

    webActiveUsers.add(1);

    // Login
    group('Web Manager: Login', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
            username: `manager_${__VU}`,
            password: 'manager_pass_123',
        }), { headers, tags: { name: 'web_manager_login' } });

        recordRequest('web', Date.now() - start);
        const success = check(res, { 'manager login ok': (r) => r.status === 200 || r.status === 201 });
        recordSuccess('web', success);
        overallLoginSuccess.add(success ? 1 : 0);

        if (success) {
            try {
                const body = JSON.parse(res.body);
                headers['Authorization'] = `Bearer ${body.token || body.access_token}`;
            } catch {}
        }
    });

    sleep(1);

    // Dashboard
    group('Web Manager: Dashboard', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/dashboard/summary`, { headers, tags: { name: 'web_dashboard' } });
        recordRequest('web', Date.now() - start);
        recordSuccess('web', check(res, { 'dashboard ok': (r) => r.status === 200 || r.status === 404 }));
    });

    sleep(randomIntBetween(3, 8));

    // Fields overview
    group('Web Manager: Fields', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/fields?page=1&limit=25`, { headers, tags: { name: 'web_fields' } });
        recordRequest('web', Date.now() - start);
        const success = check(res, { 'fields ok': (r) => r.status === 200 || r.status === 404 });
        recordSuccess('web', success);
        if (!success) recordError('web');

        sleep(randomIntBetween(2, 5));

        // Field detail
        const detailStart = Date.now();
        const detailRes = http.get(`${BASE_URL}/api/fields/${randomIntBetween(1, 25)}`, {
            headers, tags: { name: 'web_field_detail' }
        });
        recordRequest('web', Date.now() - detailStart);
        recordSuccess('web', check(detailRes, { 'field detail ok': (r) => r.status === 200 || r.status === 404 }));
    });

    sleep(randomIntBetween(3, 8));

    // Workers
    group('Web Manager: Workers', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/workers?status=active`, { headers, tags: { name: 'web_workers' } });
        recordRequest('web', Date.now() - start);
        recordSuccess('web', check(res, { 'workers ok': (r) => r.status === 200 || r.status === 404 }));

        sleep(randomIntBetween(2, 4));

        const locStart = Date.now();
        const locRes = http.get(`${BASE_URL}/api/workers/locations`, { headers, tags: { name: 'web_locations' } });
        recordRequest('web', Date.now() - locStart);
        recordSuccess('web', check(locRes, { 'locations ok': (r) => r.status === 200 || r.status === 404 }));
    });

    webActiveUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// WEB ADMIN FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function webAdminFlow() {
    const browser = randomItem(BROWSERS);
    const headers = getWebHeaders(browser);

    webActiveUsers.add(1);

    // Login
    group('Web Admin: Login', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
            username: `admin_${__VU}`,
            password: 'admin_pass_123',
        }), { headers, tags: { name: 'web_admin_login' } });

        recordRequest('web', Date.now() - start);
        const success = check(res, { 'admin login ok': (r) => r.status === 200 || r.status === 201 });
        recordSuccess('web', success);
        overallLoginSuccess.add(success ? 1 : 0);

        if (success) {
            try {
                const body = JSON.parse(res.body);
                headers['Authorization'] = `Bearer ${body.token || body.access_token}`;
            } catch {}
        }
    });

    sleep(1);

    // Admin dashboard
    group('Web Admin: Dashboard', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/admin/dashboard`, { headers, tags: { name: 'admin_dashboard' } });
        recordRequest('web', Date.now() - start);
        recordSuccess('web', check(res, { 'admin dash ok': (r) => r.status === 200 || r.status === 404 }));
    });

    sleep(randomIntBetween(3, 6));

    // Users management
    group('Web Admin: Users', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/admin/users?page=1&limit=50`, { headers, tags: { name: 'admin_users' } });
        recordRequest('web', Date.now() - start);
        const success = check(res, { 'users ok': (r) => r.status === 200 || r.status === 404 });
        recordSuccess('web', success);
        if (!success) recordError('web');
    });

    sleep(randomIntBetween(3, 6));

    // Audit logs
    group('Web Admin: Audit', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/admin/audit-logs?page=1&limit=100`, { headers, tags: { name: 'admin_audit' } });
        recordRequest('web', Date.now() - start);
        recordSuccess('web', check(res, { 'audit ok': (r) => r.status === 200 || r.status === 404 }));
    });

    webActiveUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// WEB ANALYST FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function webAnalystFlow() {
    const browser = randomItem(BROWSERS);
    const headers = getWebHeaders(browser);

    webActiveUsers.add(1);

    // Login
    group('Web Analyst: Login', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
            username: `analyst_${__VU}`,
            password: 'analyst_pass_123',
        }), { headers, tags: { name: 'web_analyst_login' } });

        recordRequest('web', Date.now() - start);
        const success = check(res, { 'analyst login ok': (r) => r.status === 200 || r.status === 201 });
        recordSuccess('web', success);
        overallLoginSuccess.add(success ? 1 : 0);

        if (success) {
            try {
                const body = JSON.parse(res.body);
                headers['Authorization'] = `Bearer ${body.token || body.access_token}`;
            } catch {}
        }
    });

    sleep(1);

    // Analytics
    group('Web Analyst: Analytics', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/analytics/overview?period=30d`, { headers, tags: { name: 'analytics' } });
        recordRequest('web', Date.now() - start);
        recordSuccess('web', check(res, { 'analytics ok': (r) => r.status === 200 || r.status === 404 }));
    });

    sleep(randomIntBetween(5, 10));

    // Generate report
    group('Web Analyst: Report', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/reports/generate`, JSON.stringify({
            type: randomItem(['daily_summary', 'weekly_analysis', 'field_performance']),
            format: 'pdf',
            date_range: { start: new Date(Date.now() - 7*24*60*60*1000).toISOString(), end: new Date().toISOString() },
        }), { headers, tags: { name: 'report_gen' } });
        recordRequest('web', Date.now() - start);
        const success = check(res, { 'report ok': (r) => r.status === 200 || r.status === 201 || r.status === 202 || r.status === 404 });
        recordSuccess('web', success);
        if (!success) recordError('web');
    });

    webActiveUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// WEB USER FLOW (Regular Users)
// ═══════════════════════════════════════════════════════════════════════════════

export function webUserFlow() {
    const browser = randomItem(BROWSERS);
    const headers = getWebHeaders(browser);

    webActiveUsers.add(1);

    // Login
    group('Web User: Login', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
            username: `user_${__VU}`,
            password: 'user_pass_123',
        }), { headers, tags: { name: 'web_user_login' } });

        recordRequest('web', Date.now() - start);
        const success = check(res, { 'user login ok': (r) => r.status === 200 || r.status === 201 });
        recordSuccess('web', success);
        overallLoginSuccess.add(success ? 1 : 0);

        if (success) {
            try {
                const body = JSON.parse(res.body);
                headers['Authorization'] = `Bearer ${body.token || body.access_token}`;
            } catch {}
        }
    });

    sleep(1);

    // Browse fields
    group('Web User: Browse', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/fields?page=1&limit=10`, { headers, tags: { name: 'web_browse' } });
        recordRequest('web', Date.now() - start);
        recordSuccess('web', check(res, { 'browse ok': (r) => r.status === 200 || r.status === 404 }));
    });

    sleep(randomIntBetween(2, 5));

    // View weather
    group('Web User: Weather', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/weather/forecast`, { headers, tags: { name: 'web_weather' } });
        recordRequest('web', Date.now() - start);
        recordSuccess('web', check(res, { 'weather ok': (r) => r.status === 200 || r.status === 404 }));
    });

    webActiveUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// WEB VIEWER FLOW (Read-only Users)
// ═══════════════════════════════════════════════════════════════════════════════

export function webViewerFlow() {
    const browser = randomItem(BROWSERS);
    const headers = getWebHeaders(browser);

    webActiveUsers.add(1);

    // Login
    group('Web Viewer: Login', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
            username: `viewer_${__VU}`,
            password: 'viewer_pass_123',
        }), { headers, tags: { name: 'web_viewer_login' } });

        recordRequest('web', Date.now() - start);
        const success = check(res, { 'viewer login ok': (r) => r.status === 200 || r.status === 201 });
        recordSuccess('web', success);
        overallLoginSuccess.add(success ? 1 : 0);

        if (success) {
            try {
                const body = JSON.parse(res.body);
                headers['Authorization'] = `Bearer ${body.token || body.access_token}`;
            } catch {}
        }
    });

    sleep(1);

    // View dashboard
    group('Web Viewer: Dashboard', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/dashboard/public`, { headers, tags: { name: 'viewer_dashboard' } });
        recordRequest('web', Date.now() - start);
        recordSuccess('web', check(res, { 'dashboard ok': (r) => r.status === 200 || r.status === 404 }));
    });

    webActiveUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// DASHBOARD ADMIN FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function dashboardAdminFlow() {
    const browser = randomItem(BROWSERS);
    const headers = getWebHeaders(browser);

    dashboardActiveUsers.add(1);

    // Login
    group('Dashboard Admin: Login', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
            username: `dashboard_admin_${__VU}`,
            password: 'admin_pass_123',
        }), { headers, tags: { name: 'dashboard_admin_login' } });

        recordRequest('dashboard', Date.now() - start);
        const success = check(res, { 'admin login ok': (r) => r.status === 200 || r.status === 201 });
        recordSuccess('dashboard', success);
        overallLoginSuccess.add(success ? 1 : 0);

        if (success) {
            try {
                const body = JSON.parse(res.body);
                headers['Authorization'] = `Bearer ${body.token || body.access_token}`;
            } catch {}
        }
    });

    sleep(1);

    // Admin dashboard
    group('Dashboard Admin: Overview', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/admin/dashboard`, { headers, tags: { name: 'admin_overview' } });
        recordRequest('dashboard', Date.now() - start);
        recordSuccess('dashboard', check(res, { 'overview ok': (r) => r.status === 200 || r.status === 404 }));
    });

    sleep(randomIntBetween(3, 6));

    // User management
    group('Dashboard Admin: Users', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/admin/users?page=1&limit=50`, { headers, tags: { name: 'admin_users' } });
        recordRequest('dashboard', Date.now() - start);
        const success = check(res, { 'users ok': (r) => r.status === 200 || r.status === 404 });
        recordSuccess('dashboard', success);
        if (!success) recordError('dashboard');
    });

    sleep(randomIntBetween(3, 6));

    // System settings
    group('Dashboard Admin: Settings', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/admin/settings`, { headers, tags: { name: 'admin_settings' } });
        recordRequest('dashboard', Date.now() - start);
        recordSuccess('dashboard', check(res, { 'settings ok': (r) => r.status === 200 || r.status === 404 }));
    });

    dashboardActiveUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// DASHBOARD ANALYST FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function dashboardAnalystFlow() {
    const browser = randomItem(BROWSERS);
    const headers = getWebHeaders(browser);

    dashboardActiveUsers.add(1);

    // Login
    group('Dashboard Analyst: Login', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
            username: `dashboard_analyst_${__VU}`,
            password: 'analyst_pass_123',
        }), { headers, tags: { name: 'dashboard_analyst_login' } });

        recordRequest('dashboard', Date.now() - start);
        const success = check(res, { 'analyst login ok': (r) => r.status === 200 || r.status === 201 });
        recordSuccess('dashboard', success);
        overallLoginSuccess.add(success ? 1 : 0);

        if (success) {
            try {
                const body = JSON.parse(res.body);
                headers['Authorization'] = `Bearer ${body.token || body.access_token}`;
            } catch {}
        }
    });

    sleep(1);

    // Analytics dashboard
    group('Dashboard Analyst: Analytics', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/analytics/dashboard?period=30d`, { headers, tags: { name: 'analyst_analytics' } });
        recordRequest('dashboard', Date.now() - start);
        recordSuccess('dashboard', check(res, { 'analytics ok': (r) => r.status === 200 || r.status === 404 }));
    });

    sleep(randomIntBetween(5, 10));

    // Generate complex report
    group('Dashboard Analyst: Report', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/reports/complex`, JSON.stringify({
            type: randomItem(['performance', 'trends', 'forecasting']),
            format: 'xlsx',
            include_charts: true,
            date_range: { start: new Date(Date.now() - 30*24*60*60*1000).toISOString(), end: new Date().toISOString() },
        }), { headers, tags: { name: 'analyst_report' } });
        recordRequest('dashboard', Date.now() - start);
        const success = check(res, { 'report ok': (r) => r.status === 200 || r.status === 201 || r.status === 202 || r.status === 404 });
        recordSuccess('dashboard', success);
        if (!success) recordError('dashboard');
    });

    dashboardActiveUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// DASHBOARD SUPER ADMIN FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function dashboardSuperAdminFlow() {
    const browser = randomItem(BROWSERS);
    const headers = getWebHeaders(browser);

    dashboardActiveUsers.add(1);

    // Login
    group('Dashboard SuperAdmin: Login', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
            username: `super_admin_${__VU}`,
            password: 'super_admin_pass_123',
        }), { headers, tags: { name: 'super_admin_login' } });

        recordRequest('dashboard', Date.now() - start);
        const success = check(res, { 'super admin login ok': (r) => r.status === 200 || r.status === 201 });
        recordSuccess('dashboard', success);
        overallLoginSuccess.add(success ? 1 : 0);

        if (success) {
            try {
                const body = JSON.parse(res.body);
                headers['Authorization'] = `Bearer ${body.token || body.access_token}`;
            } catch {}
        }
    });

    sleep(1);

    // System overview
    group('Dashboard SuperAdmin: System', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/admin/system/overview`, { headers, tags: { name: 'system_overview' } });
        recordRequest('dashboard', Date.now() - start);
        recordSuccess('dashboard', check(res, { 'system ok': (r) => r.status === 200 || r.status === 404 }));
    });

    sleep(randomIntBetween(3, 6));

    // Audit logs
    group('Dashboard SuperAdmin: Audit', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/admin/audit-logs?page=1&limit=100`, { headers, tags: { name: 'super_audit' } });
        recordRequest('dashboard', Date.now() - start);
        recordSuccess('dashboard', check(res, { 'audit ok': (r) => r.status === 200 || r.status === 404 }));
    });

    sleep(randomIntBetween(3, 6));

    // Security settings
    group('Dashboard SuperAdmin: Security', () => {
        const start = Date.now();
        const res = http.get(`${BASE_URL}/api/admin/security/settings`, { headers, tags: { name: 'security_settings' } });
        recordRequest('dashboard', Date.now() - start);
        const success = check(res, { 'security ok': (r) => r.status === 200 || r.status === 404 });
        recordSuccess('dashboard', success);
        if (!success) recordError('dashboard');
    });

    dashboardActiveUsers.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// IOT SENSOR FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function iotSensorFlow() {
    const client = { name: 'IoTGateway', version: '3.1' };
    const headers = getApiHeaders(client);
    const location = randomItem(SAUDI_LOCATIONS);

    apiActiveClients.add(1);

    group('IoT: Sensor Data', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/iot/sensors/data`, JSON.stringify({
            sensor_id: `sensor_${__VU}_${randomIntBetween(1, 10)}`,
            readings: [
                { type: 'temperature', value: 25 + Math.random() * 20, unit: 'celsius' },
                { type: 'humidity', value: 30 + Math.random() * 50, unit: 'percent' },
                { type: 'soil_moisture', value: Math.random() * 100, unit: 'percent' },
            ],
            location: generateGPS(location),
            timestamp: new Date().toISOString(),
        }), { headers, tags: { name: 'iot_data' } });

        recordRequest('api', Date.now() - start);
        const success = check(res, { 'IoT data ok': (r) => r.status === 200 || r.status === 201 || r.status === 404 });
        recordSuccess('api', success);
        overallApiSuccess.add(success ? 1 : 0);
        if (!success) recordError('api');
    });

    apiActiveClients.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// WEATHER STATION FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function weatherStationFlow() {
    const client = { name: 'WeatherStation', version: '2.0' };
    const headers = getApiHeaders(client);
    const location = randomItem(SAUDI_LOCATIONS);

    apiActiveClients.add(1);

    group('Weather: Station Data', () => {
        const start = Date.now();
        const res = http.post(`${BASE_URL}/api/weather/stations/data`, JSON.stringify({
            station_id: `ws_${location.city.toLowerCase()}_${__VU}`,
            readings: {
                temperature: 20 + Math.random() * 25,
                humidity: 20 + Math.random() * 60,
                wind_speed: Math.random() * 30,
                wind_direction: randomIntBetween(0, 360),
                pressure: 1000 + Math.random() * 30,
                precipitation: Math.random() < 0.1 ? Math.random() * 10 : 0,
            },
            location: { city: location.city, lat: location.lat, lng: location.lng },
            timestamp: new Date().toISOString(),
        }), { headers, tags: { name: 'weather_data' } });

        recordRequest('api', Date.now() - start);
        const success = check(res, { 'weather data ok': (r) => r.status === 200 || r.status === 201 || r.status === 404 });
        recordSuccess('api', success);
        overallApiSuccess.add(success ? 1 : 0);
        if (!success) recordError('api');
    });

    apiActiveClients.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// ERP SYNC FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function erpSyncFlow() {
    const client = { name: 'ERPConnector', version: '1.5' };
    const headers = getApiHeaders(client);

    apiActiveClients.add(1);

    group('ERP: Sync', () => {
        // Fetch pending sync items
        const fetchStart = Date.now();
        const fetchRes = http.get(`${BASE_URL}/api/integration/erp/pending?limit=100`, {
            headers, tags: { name: 'erp_fetch' }
        });
        recordRequest('api', Date.now() - fetchStart);
        recordSuccess('api', check(fetchRes, { 'ERP fetch ok': (r) => r.status === 200 || r.status === 404 }));

        sleep(0.5);

        // Submit sync confirmation
        const syncStart = Date.now();
        const syncRes = http.post(`${BASE_URL}/api/integration/erp/sync`, JSON.stringify({
            sync_id: generateDeviceId(),
            items_synced: randomIntBetween(10, 100),
            sync_type: randomItem(['inventory', 'orders', 'workers']),
            timestamp: new Date().toISOString(),
        }), { headers, tags: { name: 'erp_sync' } });

        recordRequest('api', Date.now() - syncStart);
        const success = check(syncRes, { 'ERP sync ok': (r) => r.status === 200 || r.status === 201 || r.status === 404 });
        recordSuccess('api', success);
        overallApiSuccess.add(success ? 1 : 0);
        if (!success) recordError('api');
    });

    apiActiveClients.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SETUP & TEARDOWN
// ═══════════════════════════════════════════════════════════════════════════════

export function setup() {
    console.log('═══════════════════════════════════════════════════════════════════════════════');
    console.log('           🚀 SAHOOL IDP - Maximum Performance Simulation v3.0');
    console.log('           محاكاة الأداء الأقصى متعددة العملاء لمنصة سهول');
    console.log('═══════════════════════════════════════════════════════════════════════════════');
    console.log('');
    console.log(`  📊 TOTAL VIRTUAL USERS: ${TOTAL_VUS}`);
    console.log('');
    console.log('  TRAFFIC DISTRIBUTION (التوزيع الأقصى):');
    console.log('  ────────────────────────────────────────────────────────────────────────────');
    console.log(`  📱 Mobile (80%):     ${MOBILE_VUS} VUs  [Target: ${MOBILE_SUCCESS_TARGET * 100}% success]`);
    console.log(`     ├─ 🍎 iOS:        ${Math.ceil(MOBILE_VUS * 0.45)} VUs (field workers)`);
    console.log(`     └─ 🤖 Android:    ${Math.ceil(MOBILE_VUS * 0.55)} VUs (field workers)`);
    console.log('');
    console.log(`  🌐 Web Browser (12%): ${WEB_VUS} VUs  [Target: ${WEB_SUCCESS_TARGET * 100}% success]`);
    console.log(`     ├─ 👤 Users:      ${Math.ceil(WEB_VUS * 0.50)} VUs`);
    console.log(`     ├─ 👔 Managers:   ${Math.ceil(WEB_VUS * 0.30)} VUs`);
    console.log(`     └─ 👁️  Viewers:    ${Math.ceil(WEB_VUS * 0.20)} VUs`);
    console.log('');
    console.log(`  🖥️  Dashboard (5%):   ${DASHBOARD_VUS} VUs  [Target: ${DASHBOARD_SUCCESS_TARGET * 100}% success]`);
    console.log(`     ├─ 👑 Admins:     ${Math.ceil(DASHBOARD_VUS * 0.50)} VUs`);
    console.log(`     ├─ 📊 Analysts:   ${Math.ceil(DASHBOARD_VUS * 0.30)} VUs`);
    console.log(`     └─ ⭐ SuperAdmins: ${Math.ceil(DASHBOARD_VUS * 0.20)} VUs`);
    console.log('');
    console.log(`  🔌 API (3%):         ${API_VUS} VUs  [Target: ${API_SUCCESS_TARGET * 100}% success]`);
    console.log(`     ├─ 🌡️  IoT:        ${Math.ceil(API_VUS * 0.50)} VUs`);
    console.log(`     ├─ ☀️  Weather:    ${Math.ceil(API_VUS * 0.30)} VUs`);
    console.log(`     └─ 🏢 ERP:        ${Math.ceil(API_VUS * 0.20)} VUs`);
    console.log('');
    console.log('  ────────────────────────────────────────────────────────────────────────────');
    console.log(`  🎯 Target: ${BASE_URL}`);
    console.log(`  ⏱️  Duration: ${TEST_DURATION}`);
    console.log('  🚀 Maximum Thresholds: Mobile 95% | Web 90% | Dashboard 85% | API 99%');
    console.log('═══════════════════════════════════════════════════════════════════════════════');
    console.log('');

    // Health check
    const healthRes = http.get(`${BASE_URL}/health`);
    if (healthRes.status !== 200) {
        console.warn('⚠️  Warning: Backend health check failed');
    } else {
        console.log('✅ Backend health check passed');
    }

    return { startTime: Date.now() };
}

export function teardown(data) {
    const duration = (Date.now() - data.startTime) / 1000;
    console.log('');
    console.log('═══════════════════════════════════════════════════════════════════════════════');
    console.log('  ✅ Multi-Client Simulation Complete');
    console.log(`  ⏱️  Duration: ${duration.toFixed(2)}s`);
    console.log('═══════════════════════════════════════════════════════════════════════════════');
}

// ═══════════════════════════════════════════════════════════════════════════════
// SUMMARY HANDLER
// ═══════════════════════════════════════════════════════════════════════════════

export function handleSummary(data) {
    const mobileReqs = data.metrics.requests_mobile?.values?.count || 0;
    const webReqs = data.metrics.requests_web?.values?.count || 0;
    const dashboardReqs = data.metrics.requests_dashboard?.values?.count || 0;
    const apiReqs = data.metrics.requests_api?.values?.count || 0;
    const totalReqs = mobileReqs + webReqs + dashboardReqs + apiReqs;

    const summary = {
        timestamp: new Date().toISOString(),
        test_type: 'multi_client_maximum_performance_v3',
        configuration: {
            total_vus: TOTAL_VUS,
            mobile_vus: MOBILE_VUS,
            web_vus: WEB_VUS,
            dashboard_vus: DASHBOARD_VUS,
            api_vus: API_VUS,
            success_targets: {
                mobile: MOBILE_SUCCESS_TARGET * 100 + '%',
                web: WEB_SUCCESS_TARGET * 100 + '%',
                dashboard: DASHBOARD_SUCCESS_TARGET * 100 + '%',
                api: API_SUCCESS_TARGET * 100 + '%',
            },
        },
        traffic_distribution: {
            mobile: {
                requests: mobileReqs,
                percentage: totalReqs > 0 ? ((mobileReqs / totalReqs) * 100).toFixed(1) + '%' : '0%',
            },
            web: {
                requests: webReqs,
                percentage: totalReqs > 0 ? ((webReqs / totalReqs) * 100).toFixed(1) + '%' : '0%',
            },
            dashboard: {
                requests: dashboardReqs,
                percentage: totalReqs > 0 ? ((dashboardReqs / totalReqs) * 100).toFixed(1) + '%' : '0%',
            },
            api: {
                requests: apiReqs,
                percentage: totalReqs > 0 ? ((apiReqs / totalReqs) * 100).toFixed(1) + '%' : '0%',
            },
        },
        success_rates: {
            overall: (data.metrics.overall_success_rate?.values?.rate * 100 || 0).toFixed(2) + '%',
            login: (data.metrics.overall_login_success?.values?.rate * 100 || 0).toFixed(2) + '%',
            mobile: (data.metrics.mobile_success_rate?.values?.rate * 100 || 0).toFixed(2) + '%',
            web: (data.metrics.web_success_rate?.values?.rate * 100 || 0).toFixed(2) + '%',
            dashboard: (data.metrics.dashboard_success_rate?.values?.rate * 100 || 0).toFixed(2) + '%',
            api: (data.metrics.api_integration_success_rate?.values?.rate * 100 || 0).toFixed(2) + '%',
        },
        response_times: {
            mobile_p95: (data.metrics.response_time_mobile?.values?.['p(95)'] || 0).toFixed(0) + 'ms',
            mobile_avg: (data.metrics.response_time_mobile?.values?.avg || 0).toFixed(0) + 'ms',
            web_p95: (data.metrics.response_time_web?.values?.['p(95)'] || 0).toFixed(0) + 'ms',
            web_avg: (data.metrics.response_time_web?.values?.avg || 0).toFixed(0) + 'ms',
            dashboard_p95: (data.metrics.response_time_dashboard?.values?.['p(95)'] || 0).toFixed(0) + 'ms',
            dashboard_avg: (data.metrics.response_time_dashboard?.values?.avg || 0).toFixed(0) + 'ms',
            api_p95: (data.metrics.response_time_api?.values?.['p(95)'] || 0).toFixed(0) + 'ms',
            api_avg: (data.metrics.response_time_api?.values?.avg || 0).toFixed(0) + 'ms',
        },
        errors: {
            mobile: data.metrics.errors_mobile?.values?.count || 0,
            web: data.metrics.errors_web?.values?.count || 0,
            dashboard: data.metrics.errors_dashboard?.values?.count || 0,
            api: data.metrics.errors_api?.values?.count || 0,
        },
        thresholds_passed: Object.entries(data.metrics)
            .filter(([name]) => name.includes('success') || name.includes('response'))
            .every(([, metric]) => !metric.thresholds || Object.values(metric.thresholds).every(t => t.ok)),
    };

    const mobileBar = '█'.repeat(Math.round((mobileReqs / totalReqs || 0) * 25));
    const webBar = '█'.repeat(Math.round((webReqs / totalReqs || 0) * 25));
    const dashboardBar = '█'.repeat(Math.round((dashboardReqs / totalReqs || 0) * 25));
    const apiBar = '█'.repeat(Math.round((apiReqs / totalReqs || 0) * 25));

    const mobileRate = parseFloat(summary.success_rates.mobile);
    const webRate = parseFloat(summary.success_rates.web);
    const dashboardRate = parseFloat(summary.success_rates.dashboard);
    const apiRate = parseFloat(summary.success_rates.api);

    const textSummary = `
═══════════════════════════════════════════════════════════════════════════════════════
                    🚀 MAXIMUM PERFORMANCE SIMULATION RESULTS v3.0
                    نتائج محاكاة الأداء الأقصى متعددة العملاء
═══════════════════════════════════════════════════════════════════════════════════════

📊 TRAFFIC DISTRIBUTION (التوزيع الأقصى):
────────────────────────────────────────────────────────────────────────────────────────
  📱 Mobile:    ${summary.traffic_distribution.mobile.percentage.padStart(6)} ${mobileBar} (${mobileReqs} requests)
  🌐 Web:       ${summary.traffic_distribution.web.percentage.padStart(6)} ${webBar} (${webReqs} requests)
  🖥️  Dashboard: ${summary.traffic_distribution.dashboard.percentage.padStart(6)} ${dashboardBar} (${dashboardReqs} requests)
  🔌 API:       ${summary.traffic_distribution.api.percentage.padStart(6)} ${apiBar} (${apiReqs} requests)

🚀 SUCCESS RATES (نسب النجاح القصوى):
────────────────────────────────────────────────────────────────────────────────────────
  🎯 Overall Success:      ${summary.success_rates.overall}  ${parseFloat(summary.success_rates.overall) >= 90 ? '✓ PASS' : '✗ FAIL'}
  🔐 Login Success:        ${summary.success_rates.login}
  📱 Mobile Success:       ${summary.success_rates.mobile}  [Target: 95%] ${mobileRate >= 95 ? '✓' : '✗'}
  🌐 Web Success:          ${summary.success_rates.web}  [Target: 90%] ${webRate >= 90 ? '✓' : '✗'}
  🖥️  Dashboard Success:    ${summary.success_rates.dashboard}  [Target: 85%] ${dashboardRate >= 85 ? '✓' : '✗'}
  🔌 API Success:          ${summary.success_rates.api}  [Target: 99%] ${apiRate >= 99 ? '✓' : '✗'}

⚡ RESPONSE TIMES (أوقات الاستجابة):
────────────────────────────────────────────────────────────────────────────────────────
  📱 Mobile:    p95=${summary.response_times.mobile_p95}  avg=${summary.response_times.mobile_avg}
  🌐 Web:       p95=${summary.response_times.web_p95}  avg=${summary.response_times.web_avg}
  🖥️  Dashboard: p95=${summary.response_times.dashboard_p95}  avg=${summary.response_times.dashboard_avg}
  🔌 API:       p95=${summary.response_times.api_p95}  avg=${summary.response_times.api_avg}

❌ ERRORS (الأخطاء):
────────────────────────────────────────────────────────────────────────────────────────
  📱 Mobile Errors:    ${summary.errors.mobile}
  🌐 Web Errors:       ${summary.errors.web}
  🖥️  Dashboard Errors: ${summary.errors.dashboard}
  🔌 API Errors:       ${summary.errors.api}

═══════════════════════════════════════════════════════════════════════════════════════
  ${summary.thresholds_passed ? '✅ ALL THRESHOLDS PASSED - جميع المعايير نجحت' : '⚠️  SOME THRESHOLDS FAILED - بعض المعايير فشلت'}
═══════════════════════════════════════════════════════════════════════════════════════
`;

    return {
        'stdout': textSummary,
        './results/multi-client-max-performance-v3.json': JSON.stringify(summary, null, 2),
    };
}

// Default export - Updated with new distribution
export default function() {
    const rand = Math.random();

    // Mobile: 50%
    if (rand < MOBILE_RATIO) {
        if (Math.random() < 0.45) iosFieldWorkerFlow();
        else androidFieldWorkerFlow();
    }
    // Web: 30%
    else if (rand < MOBILE_RATIO + WEB_RATIO) {
        const webRand = Math.random();
        if (webRand < 0.50) webUserFlow();
        else if (webRand < 0.80) webManagerFlow();
        else webViewerFlow();
    }
    // Dashboard: 15%
    else if (rand < MOBILE_RATIO + WEB_RATIO + DASHBOARD_RATIO) {
        const dashRand = Math.random();
        if (dashRand < 0.50) dashboardAdminFlow();
        else if (dashRand < 0.80) dashboardAnalystFlow();
        else dashboardSuperAdminFlow();
    }
    // API: 5%
    else {
        const apiRand = Math.random();
        if (apiRand < 0.50) iotSensorFlow();
        else if (apiRand < 0.80) weatherStationFlow();
        else erpSyncFlow();
    }
}
