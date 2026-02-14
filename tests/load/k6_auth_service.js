/**
 * SAHOOL Platform - User Service (Auth) Load Test
 * اختبار الحمل لخدمة المستخدمين والمصادقة
 *
 * Service: user-service (port 3025)
 * Purpose: Load test authentication endpoints including login, token refresh, and validation
 *
 * Run with:
 *   k6 run tests/load/k6_auth_service.js
 *   k6 run --env BASE_URL=http://user-service:3025 tests/load/k6_auth_service.js
 *
 * Environment variables:
 *   - BASE_URL: User service URL (default: http://localhost:3025)
 *   - TEST_EMAIL: Test user email (default: loadtest@sahool.io)
 *   - TEST_PASSWORD: Test user password (default: LoadTest123!)
 *   - TENANT_ID: Tenant ID for multi-tenant testing (default: tenant_loadtest)
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// =============================================================================
// Configuration
// =============================================================================

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3025';
const TEST_EMAIL = __ENV.TEST_EMAIL || 'loadtest@sahool.io';
const TEST_PASSWORD = __ENV.TEST_PASSWORD || 'LoadTest123!';
const TENANT_ID = __ENV.TENANT_ID || 'tenant_loadtest';

// =============================================================================
// Custom Metrics
// =============================================================================

// Latency trends
const healthLatency = new Trend('auth_health_latency', true);
const loginLatency = new Trend('auth_login_latency', true);
const tokenRefreshLatency = new Trend('auth_token_refresh_latency', true);
const tokenValidateLatency = new Trend('auth_token_validate_latency', true);
const profileLatency = new Trend('auth_profile_latency', true);
const logoutLatency = new Trend('auth_logout_latency', true);

// Success rates
const loginSuccessRate = new Rate('auth_login_success');
const refreshSuccessRate = new Rate('auth_refresh_success');
const healthSuccessRate = new Rate('auth_health_success');
const overallAuthSuccess = new Rate('auth_overall_success');

// Counters
const totalLogins = new Counter('auth_total_logins');
const failedLogins = new Counter('auth_failed_logins');
const totalRefreshes = new Counter('auth_total_refreshes');
const rateLimitHits = new Counter('auth_rate_limit_hits');
const invalidCredentialAttempts = new Counter('auth_invalid_credential_attempts');

// =============================================================================
// Test Options
// =============================================================================

export const options = {
  stages: [
    { duration: '1m', target: 10 },   // Ramp up to 10 VUs
    { duration: '2m', target: 50 },   // Ramp up to 50 VUs
    { duration: '3m', target: 100 },  // Ramp up to 100 VUs
    { duration: '3m', target: 100 },  // Hold at 100 VUs
    { duration: '1m', target: 30 },   // Ramp down to 30 VUs
    { duration: '1m', target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    // Health endpoint thresholds
    auth_health_latency: ['p(95)<200', 'p(99)<500'],
    auth_health_success: ['rate>0.99'],

    // Auth endpoint thresholds
    auth_login_latency: ['p(95)<1000', 'p(99)<2000'],
    auth_token_refresh_latency: ['p(95)<1000', 'p(99)<2000'],
    auth_token_validate_latency: ['p(95)<500', 'p(99)<1000'],
    auth_profile_latency: ['p(95)<500', 'p(99)<1000'],

    // Success rates
    auth_login_success: ['rate>0.90'],
    auth_refresh_success: ['rate>0.95'],
    auth_overall_success: ['rate>0.95'],

    // General HTTP thresholds
    http_req_failed: ['rate<0.05'],
    checks: ['rate>0.90'],
  },
  tags: {
    test_type: 'load',
    service: 'user-service',
    environment: __ENV.ENVIRONMENT || 'local',
  },
};

// =============================================================================
// Helper Functions
// =============================================================================

function getHeaders(token) {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Tenant-ID': TENANT_ID,
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

function randomElement(array) {
  return array[Math.floor(Math.random() * array.length)];
}

function randomFloat(min, max) {
  return parseFloat((Math.random() * (max - min) + min).toFixed(2));
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomString(length) {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * Generate a mock JWT token for testing.
 * In production, this comes from the actual auth endpoint.
 */
function generateMockToken() {
  const header = __ENV.MOCK_TOKEN_HEADER || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9';
  const payload = JSON.stringify({
    sub: `user_${randomString(8)}`,
    email: TEST_EMAIL,
    tid: TENANT_ID,
    roles: ['farmer'],
    permissions: ['field:read', 'field:write'],
    exp: Math.floor(Date.now() / 1000) + 3600,
    iat: Math.floor(Date.now() / 1000),
  });
  // Base64url encode the payload (simplified for k6)
  const encodedPayload = encodeURIComponent(payload);
  const signature = randomString(32);
  return `${header}.${encodedPayload}.${signature}`;
}

// =============================================================================
// Test Data
// =============================================================================

const TEST_USERS = [
  { email: 'farmer1@sahool.io', role: 'farmer' },
  { email: 'farmer2@sahool.io', role: 'farmer' },
  { email: 'manager1@sahool.io', role: 'farm_manager' },
  { email: 'admin1@sahool.io', role: 'admin' },
  { email: 'agronomist1@sahool.io', role: 'agronomist' },
];

const INVALID_EMAILS = [
  'nonexistent@sahool.io',
  'invalid@test.com',
  `random_${randomString(6)}@sahool.io`,
];

const INVALID_PASSWORDS = [
  'wrongpassword',
  '123456',
  'short',
  '',
];

// =============================================================================
// Setup
// =============================================================================

export function setup() {
  console.log('='.repeat(70));
  console.log('SAHOOL - User Service (Auth) Load Test');
  console.log('اختبار الحمل لخدمة المصادقة');
  console.log('='.repeat(70));
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Test Email: ${TEST_EMAIL}`);
  console.log(`Tenant ID: ${TENANT_ID}`);
  console.log('='.repeat(70));

  // Verify service is reachable
  const healthResp = http.get(`${BASE_URL}/healthz`);
  if (healthResp.status !== 200) {
    console.warn(`WARNING: Health check returned status ${healthResp.status}`);
  } else {
    console.log('Service health check passed.');
  }

  return { startTime: Date.now() };
}

// =============================================================================
// Test Scenarios
// =============================================================================

export default function () {
  let accessToken = null;
  let refreshToken = null;

  // -------------------------------------------------------------------------
  // Group 1: Health and Readiness Checks
  // -------------------------------------------------------------------------
  group('Health Checks', function () {
    const healthResp = http.get(`${BASE_URL}/healthz`, { headers: getHeaders() });
    healthLatency.add(healthResp.timings.duration);

    const healthOk = check(healthResp, {
      'healthz returns 200': (r) => r.status === 200,
      'healthz has status field': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.status !== undefined;
        } catch {
          return false;
        }
      },
    });
    healthSuccessRate.add(healthOk ? 1 : 0);

    const readyResp = http.get(`${BASE_URL}/readyz`, { headers: getHeaders() });
    healthLatency.add(readyResp.timings.duration);

    check(readyResp, {
      'readyz returns 200': (r) => r.status === 200,
    });

    sleep(0.3);
  });

  // -------------------------------------------------------------------------
  // Group 2: Login (Valid Credentials)
  // -------------------------------------------------------------------------
  group('Login', function () {
    const user = randomElement(TEST_USERS);

    const loginPayload = JSON.stringify({
      email: user.email,
      password: TEST_PASSWORD,
      tenant_id: TENANT_ID,
    });

    const loginResp = http.post(
      `${BASE_URL}/api/v1/auth/login`,
      loginPayload,
      { headers: getHeaders(), timeout: '15s' }
    );

    loginLatency.add(loginResp.timings.duration);
    totalLogins.add(1);

    check(loginResp, {
      'login responds': (r) => r.status === 200 || r.status === 401 || r.status === 400 || r.status === 422,
      'login not server error': (r) => r.status < 500,
      'login within threshold': (r) => r.timings.duration < 3000,
    });

    if (loginResp.status === 429) {
      rateLimitHits.add(1);
    }

    if (loginResp.status === 200) {
      loginSuccessRate.add(1);
      overallAuthSuccess.add(1);

      // Extract tokens
      try {
        const body = JSON.parse(loginResp.body);
        accessToken = body.access_token || body.token;
        refreshToken = body.refresh_token;

        check(loginResp, {
          'login response has access token': () => accessToken !== null && accessToken !== undefined,
          'login response has refresh token': () => refreshToken !== null && refreshToken !== undefined,
        });
      } catch {
        // Use mock token if parsing fails
        accessToken = generateMockToken();
      }
    } else {
      loginSuccessRate.add(0);
      overallAuthSuccess.add(0);
      failedLogins.add(1);
      // Generate a mock token for subsequent tests
      accessToken = generateMockToken();
    }

    sleep(randomFloat(0.3, 0.8));
  });

  // -------------------------------------------------------------------------
  // Group 3: Token Refresh
  // -------------------------------------------------------------------------
  group('Token Refresh', function () {
    const refreshPayload = JSON.stringify({
      refresh_token: refreshToken || generateMockToken(),
      tenant_id: TENANT_ID,
    });

    const refreshResp = http.post(
      `${BASE_URL}/api/v1/auth/token/refresh`,
      refreshPayload,
      { headers: getHeaders(), timeout: '10s' }
    );

    tokenRefreshLatency.add(refreshResp.timings.duration);
    totalRefreshes.add(1);

    check(refreshResp, {
      'token refresh responds': (r) => r.status === 200 || r.status === 401 || r.status === 400 || r.status === 422,
      'token refresh not server error': (r) => r.status < 500,
      'token refresh within threshold': (r) => r.timings.duration < 2000,
    });

    if (refreshResp.status === 429) {
      rateLimitHits.add(1);
    }

    if (refreshResp.status === 200) {
      refreshSuccessRate.add(1);
      overallAuthSuccess.add(1);

      // Update access token
      try {
        const body = JSON.parse(refreshResp.body);
        if (body.access_token || body.token) {
          accessToken = body.access_token || body.token;
        }
        if (body.refresh_token) {
          refreshToken = body.refresh_token;
        }
      } catch {
        // Ignore parse errors
      }
    } else {
      refreshSuccessRate.add(0);
      overallAuthSuccess.add(0);
    }

    sleep(randomFloat(0.3, 0.8));
  });

  // -------------------------------------------------------------------------
  // Group 4: Token Validation (30% of iterations)
  // -------------------------------------------------------------------------
  if (Math.random() < 0.3 && accessToken) {
    group('Token Validation', function () {
      const validateResp = http.get(
        `${BASE_URL}/api/v1/auth/validate`,
        { headers: getHeaders(accessToken), timeout: '10s' }
      );

      tokenValidateLatency.add(validateResp.timings.duration);

      check(validateResp, {
        'token validation responds': (r) => r.status === 200 || r.status === 401,
        'token validation not server error': (r) => r.status < 500,
      });

      overallAuthSuccess.add(validateResp.status < 500 ? 1 : 0);

      sleep(0.3);
    });
  }

  // -------------------------------------------------------------------------
  // Group 5: Get User Profile (25% of iterations)
  // -------------------------------------------------------------------------
  if (Math.random() < 0.25 && accessToken) {
    group('User Profile', function () {
      const profileResp = http.get(
        `${BASE_URL}/api/v1/auth/profile`,
        { headers: getHeaders(accessToken), timeout: '10s' }
      );

      profileLatency.add(profileResp.timings.duration);

      const profileOk = check(profileResp, {
        'profile request responds': (r) => r.status === 200 || r.status === 401 || r.status === 404,
        'profile request not server error': (r) => r.status < 500,
      });

      overallAuthSuccess.add(profileOk ? 1 : 0);

      if (profileResp.status === 200) {
        check(profileResp, {
          'profile has user data': (r) => {
            try {
              const body = JSON.parse(r.body);
              return body.email !== undefined || body.id !== undefined || body.user_id !== undefined;
            } catch {
              return false;
            }
          },
        });
      }

      sleep(0.3);
    });
  }

  // -------------------------------------------------------------------------
  // Group 6: Invalid Login Attempts (10% of iterations - tests security)
  // -------------------------------------------------------------------------
  if (Math.random() < 0.1) {
    group('Invalid Login Attempts', function () {
      // Test with invalid credentials
      const invalidEmail = randomElement(INVALID_EMAILS);
      const invalidPassword = randomElement(INVALID_PASSWORDS);
      invalidCredentialAttempts.add(1);

      const invalidLoginPayload = JSON.stringify({
        email: invalidEmail,
        password: invalidPassword,
        tenant_id: TENANT_ID,
      });

      const invalidResp = http.post(
        `${BASE_URL}/api/v1/auth/login`,
        invalidLoginPayload,
        { headers: getHeaders(), timeout: '10s' }
      );

      loginLatency.add(invalidResp.timings.duration);

      check(invalidResp, {
        'invalid login rejected': (r) => r.status === 401 || r.status === 400 || r.status === 422 || r.status === 429,
        'invalid login not 200': (r) => r.status !== 200,
        'invalid login not server error': (r) => r.status < 500,
      });

      if (invalidResp.status === 429) {
        rateLimitHits.add(1);
      }

      // Verify brute-force protection is not bypassed
      overallAuthSuccess.add(invalidResp.status < 500 ? 1 : 0);

      sleep(randomFloat(1.0, 2.0)); // Longer sleep after invalid attempts
    });
  }

  // -------------------------------------------------------------------------
  // Group 7: Logout (5% of iterations)
  // -------------------------------------------------------------------------
  if (Math.random() < 0.05 && accessToken) {
    group('Logout', function () {
      const logoutResp = http.post(
        `${BASE_URL}/api/v1/auth/logout`,
        JSON.stringify({ refresh_token: refreshToken }),
        { headers: getHeaders(accessToken), timeout: '10s' }
      );

      logoutLatency.add(logoutResp.timings.duration);

      check(logoutResp, {
        'logout responds': (r) => r.status === 200 || r.status === 204 || r.status === 401,
        'logout not server error': (r) => r.status < 500,
      });

      overallAuthSuccess.add(logoutResp.status < 500 ? 1 : 0);

      // Clear tokens after logout
      accessToken = null;
      refreshToken = null;

      sleep(0.5);
    });
  }

  // -------------------------------------------------------------------------
  // Group 8: Concurrent Session Simulation (10% of iterations)
  // -------------------------------------------------------------------------
  if (Math.random() < 0.1) {
    group('Concurrent Session Burst', function () {
      // Simulate multiple login attempts from different users
      const sessionCount = randomInt(2, 4);

      for (let i = 0; i < sessionCount; i++) {
        const user = randomElement(TEST_USERS);
        const payload = JSON.stringify({
          email: user.email,
          password: TEST_PASSWORD,
          tenant_id: TENANT_ID,
        });

        const resp = http.post(
          `${BASE_URL}/api/v1/auth/login`,
          payload,
          { headers: getHeaders(), timeout: '15s' }
        );

        loginLatency.add(resp.timings.duration);
        totalLogins.add(1);

        check(resp, {
          'concurrent login responds': (r) => r.status < 500,
        });

        if (resp.status >= 500) {
          failedLogins.add(1);
        }

        sleep(0.2);
      }
    });
  }

  // Random sleep between iterations
  sleep(randomFloat(0.5, 2.0));
}

// =============================================================================
// Teardown
// =============================================================================

export function teardown(data) {
  const durationSec = ((Date.now() - data.startTime) / 1000).toFixed(2);
  console.log('='.repeat(70));
  console.log('User Service (Auth) Load Test Complete');
  console.log('اختبار الحمل لخدمة المصادقة مكتمل');
  console.log(`Duration: ${durationSec} seconds`);
  console.log('='.repeat(70));
}

// =============================================================================
// Handle Summary - JSON Output
// =============================================================================

export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    test_type: 'auth_service_load_test',
    service: 'user-service',
    base_url: BASE_URL,
    health: {
      latency_p95: (data.metrics.auth_health_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      success_rate: ((data.metrics.auth_health_success?.values?.rate || 0) * 100).toFixed(2) + '%',
    },
    login: {
      latency_p95: (data.metrics.auth_login_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      latency_avg: (data.metrics.auth_login_latency?.values?.avg || 0).toFixed(2) + 'ms',
      success_rate: ((data.metrics.auth_login_success?.values?.rate || 0) * 100).toFixed(2) + '%',
      total: data.metrics.auth_total_logins?.values?.count || 0,
      failed: data.metrics.auth_failed_logins?.values?.count || 0,
    },
    token_refresh: {
      latency_p95: (data.metrics.auth_token_refresh_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      success_rate: ((data.metrics.auth_refresh_success?.values?.rate || 0) * 100).toFixed(2) + '%',
      total: data.metrics.auth_total_refreshes?.values?.count || 0,
    },
    token_validation: {
      latency_p95: (data.metrics.auth_token_validate_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
    },
    profile: {
      latency_p95: (data.metrics.auth_profile_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
    },
    security: {
      invalid_attempts: data.metrics.auth_invalid_credential_attempts?.values?.count || 0,
      rate_limit_hits: data.metrics.auth_rate_limit_hits?.values?.count || 0,
    },
    overall: {
      auth_success_rate: ((data.metrics.auth_overall_success?.values?.rate || 0) * 100).toFixed(2) + '%',
    },
    http: {
      requests: data.metrics.http_reqs?.values?.count || 0,
      failed_rate: ((data.metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2) + '%',
      duration_p95: (data.metrics.http_req_duration?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
    },
  };

  const textSummary = `
${'='.repeat(70)}
           User Service (Auth) Load Test Results
           نتائج اختبار الحمل لخدمة المصادقة
${'='.repeat(70)}

HEALTH CHECKS:
${'─'.repeat(70)}
  Latency (p95):             ${summary.health.latency_p95}
  Success Rate:              ${summary.health.success_rate}

LOGIN:
${'─'.repeat(70)}
  Latency (p95):             ${summary.login.latency_p95}
  Latency (avg):             ${summary.login.latency_avg}
  Success Rate:              ${summary.login.success_rate}
  Total Logins:              ${summary.login.total}
  Failed Logins:             ${summary.login.failed}

TOKEN REFRESH:
${'─'.repeat(70)}
  Latency (p95):             ${summary.token_refresh.latency_p95}
  Success Rate:              ${summary.token_refresh.success_rate}
  Total Refreshes:           ${summary.token_refresh.total}

TOKEN VALIDATION:
${'─'.repeat(70)}
  Latency (p95):             ${summary.token_validation.latency_p95}

USER PROFILE:
${'─'.repeat(70)}
  Latency (p95):             ${summary.profile.latency_p95}

SECURITY:
${'─'.repeat(70)}
  Invalid Login Attempts:    ${summary.security.invalid_attempts}
  Rate Limit Hits:           ${summary.security.rate_limit_hits}

OVERALL AUTH SUCCESS:        ${summary.overall.auth_success_rate}

HTTP OVERVIEW:
${'─'.repeat(70)}
  Total Requests:            ${summary.http.requests}
  Failed Rate:               ${summary.http.failed_rate}
  Duration (p95):            ${summary.http.duration_p95}

${'='.repeat(70)}
`;

  return {
    stdout: textSummary,
    './results/k6_auth_service_results.json': JSON.stringify(summary, null, 2),
  };
}
