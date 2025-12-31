/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * SAHOOL IDP - Agent-Based Load Testing Simulation
 * محاكاة اختبار الحمل القائمة على الوكلاء لمنصة سهول
 * ═══════════════════════════════════════════════════════════════════════════════
 *
 * This script simulates 10 virtual agents (users) performing concurrent operations:
 * - Agent login/authentication
 * - Profile retrieval
 * - Field operations (CRUD)
 * - Session management
 *
 * The simulation helps identify:
 * - Connection pool exhaustion
 * - Session loss between instances
 * - Race conditions in database
 * - High latency issues
 *
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import http from 'k6/http';
import { check, group, sleep, fail } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';

// ═══════════════════════════════════════════════════════════════════════════════
// CUSTOM METRICS - مقاييس مخصصة
// ═══════════════════════════════════════════════════════════════════════════════

// Success rates
const loginSuccessRate = new Rate('login_success_rate');
const profileSuccessRate = new Rate('profile_success_rate');
const fieldOpsSuccessRate = new Rate('field_operations_success_rate');
const sessionPersistenceRate = new Rate('session_persistence_rate');

// Response time trends
const loginDuration = new Trend('login_duration_ms');
const profileDuration = new Trend('profile_duration_ms');
const fieldListDuration = new Trend('field_list_duration_ms');
const fieldCreateDuration = new Trend('field_create_duration_ms');

// Error counters
const connectionPoolErrors = new Counter('connection_pool_errors');
const sessionLossErrors = new Counter('session_loss_errors');
const raceConditionErrors = new Counter('race_condition_errors');
const timeoutErrors = new Counter('timeout_errors');

// Active agents gauge
const activeAgents = new Gauge('active_agents');

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION - الإعدادات
// ═══════════════════════════════════════════════════════════════════════════════

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const AGENT_COUNT = parseInt(__ENV.AGENT_COUNT) || 10;
const SIMULATION_DURATION = __ENV.SIMULATION_DURATION || '3m';
const ENVIRONMENT = __ENV.ENVIRONMENT || 'simulation';

// Test configuration with agent-based staging
export const options = {
    // Simulate 10 agents ramping up and performing operations
    stages: [
        { duration: '30s', target: AGENT_COUNT },     // Ramp up to 10 agents
        { duration: '1m', target: AGENT_COUNT },      // Stay at 10 agents for 1 minute
        { duration: '30s', target: AGENT_COUNT * 2 }, // Increase to 20 agents (stress)
        { duration: '30s', target: AGENT_COUNT },     // Back to 10 agents
        { duration: '10s', target: 0 },               // Ramp down
    ],

    // Performance thresholds
    thresholds: {
        // General HTTP metrics
        'http_req_duration': ['p(95)<500', 'p(99)<1000'],
        'http_req_failed': ['rate<0.05'], // Allow 5% error rate for simulation

        // Custom metrics thresholds
        'login_success_rate': ['rate>0.95'],           // 95% login success
        'profile_success_rate': ['rate>0.95'],         // 95% profile fetch success
        'session_persistence_rate': ['rate>0.90'],     // 90% session persistence
        'field_operations_success_rate': ['rate>0.90'], // 90% field ops success

        // Response time thresholds
        'login_duration_ms': ['p(95)<800'],
        'profile_duration_ms': ['p(95)<300'],
        'field_list_duration_ms': ['p(95)<500'],

        // Error thresholds
        'connection_pool_errors': ['count<10'],
        'session_loss_errors': ['count<5'],
        'race_condition_errors': ['count<5'],
    },

    // Tags for filtering
    tags: {
        test_type: 'agent_simulation',
        environment: ENVIRONMENT,
        agent_count: AGENT_COUNT.toString(),
    },

    // Summary output
    summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
};

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS - دوال مساعدة
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Generate unique agent identifier
 */
function getAgentId() {
    return `agent_${__VU}`;
}

/**
 * Generate agent email
 */
function getAgentEmail() {
    return `agent_${__VU}@sahool-test.io`;
}

/**
 * Random string generator
 */
function randomString(length = 8) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

/**
 * Parse error from response
 */
function parseError(response) {
    try {
        const body = JSON.parse(response.body);
        return body.error || body.message || `HTTP ${response.status}`;
    } catch (e) {
        return `HTTP ${response.status}: ${response.body}`;
    }
}

/**
 * Check for specific error types
 */
function categorizeError(response) {
    const body = response.body || '';
    const status = response.status;

    // Connection pool exhaustion
    if (body.includes('Connection is not available') ||
        body.includes('pool exhausted') ||
        body.includes('connection timeout') ||
        body.includes('too many connections')) {
        connectionPoolErrors.add(1);
        return 'connection_pool';
    }

    // Session loss
    if (status === 401 || body.includes('session expired') ||
        body.includes('invalid token') || body.includes('not authenticated')) {
        sessionLossErrors.add(1);
        return 'session_loss';
    }

    // Race condition / data integrity
    if (body.includes('duplicate key') ||
        body.includes('DataIntegrityViolation') ||
        body.includes('constraint violation') ||
        body.includes('already exists')) {
        raceConditionErrors.add(1);
        return 'race_condition';
    }

    // Timeout
    if (response.error && response.error.includes('timeout')) {
        timeoutErrors.add(1);
        return 'timeout';
    }

    return 'other';
}

// ═══════════════════════════════════════════════════════════════════════════════
// SETUP FUNCTION - يعمل مرة واحدة قبل الاختبار
// ═══════════════════════════════════════════════════════════════════════════════

export function setup() {
    console.log('═══════════════════════════════════════════════════════════════');
    console.log('  SAHOOL IDP - Agent Simulation Starting');
    console.log('  محاكاة الوكلاء لمنصة سهول');
    console.log('═══════════════════════════════════════════════════════════════');
    console.log(`  Environment: ${ENVIRONMENT}`);
    console.log(`  Base URL: ${BASE_URL}`);
    console.log(`  Agent Count: ${AGENT_COUNT}`);
    console.log(`  Duration: ${SIMULATION_DURATION}`);
    console.log('═══════════════════════════════════════════════════════════════');

    // Verify services are reachable
    const healthCheck = http.get(`${BASE_URL}/healthz`, { timeout: '10s' });
    const isHealthy = healthCheck.status === 200;

    console.log(`\n  Health Check: ${isHealthy ? 'PASSED' : 'FAILED'}`);

    if (!isHealthy) {
        console.log('  WARNING: Service may not be fully ready');
        console.log(`  Status: ${healthCheck.status}`);
    }

    console.log('\n  Starting agent simulation...\n');

    return {
        startTime: new Date().toISOString(),
        baseUrl: BASE_URL,
        healthCheck: isHealthy,
    };
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN TEST FUNCTION - الدالة الرئيسية للاختبار
// ═══════════════════════════════════════════════════════════════════════════════

export default function (data) {
    const agentId = getAgentId();
    const agentEmail = getAgentEmail();
    let token = null;
    let userId = null;
    let fieldId = null;

    // Track active agents
    activeAgents.add(1);

    // ═══════════════════════════════════════════════════════════════════════════
    // PHASE 1: Agent Authentication - مصادقة الوكيل
    // ═══════════════════════════════════════════════════════════════════════════

    group('Phase 1: Authentication', () => {
        const loginPayload = JSON.stringify({
            username: agentId,
            email: agentEmail,
            password: 'password123',
        });

        const loginStart = Date.now();
        const loginRes = http.post(`${BASE_URL}/api/auth/login`, loginPayload, {
            headers: {
                'Content-Type': 'application/json',
                'X-Agent-ID': agentId,
            },
            timeout: '30s',
        });
        const loginEnd = Date.now();

        // Record duration
        loginDuration.add(loginEnd - loginStart);

        // Check login success
        const loginSuccess = check(loginRes, {
            'login status is 200': (r) => r.status === 200,
            'login has token': (r) => {
                try {
                    const body = JSON.parse(r.body);
                    return body.token !== undefined || body.access_token !== undefined;
                } catch (e) {
                    return false;
                }
            },
            'login response time < 1s': (r) => r.timings.duration < 1000,
        });

        loginSuccessRate.add(loginSuccess);

        if (loginRes.status === 200) {
            try {
                const body = JSON.parse(loginRes.body);
                token = body.token || body.access_token;
                userId = body.userId || body.user_id || body.sub;
            } catch (e) {
                console.log(`[${agentId}] Failed to parse login response`);
            }
        } else {
            categorizeError(loginRes);
            console.log(`[${agentId}] Login failed: ${parseError(loginRes)}`);
        }

        sleep(0.5);
    });

    // If login failed, try mock token for testing infrastructure
    if (!token) {
        // Generate a mock token for testing load balancing and infrastructure
        token = `mock_token_${agentId}_${Date.now()}`;
        userId = `user_${agentId}`;
        console.log(`[${agentId}] Using mock token for infrastructure testing`);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // PHASE 2: Profile Retrieval - جلب الملف الشخصي
    // ═══════════════════════════════════════════════════════════════════════════

    group('Phase 2: Profile', () => {
        const profileStart = Date.now();
        const profileRes = http.get(`${BASE_URL}/api/profile`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'X-Agent-ID': agentId,
            },
            timeout: '30s',
        });
        const profileEnd = Date.now();

        profileDuration.add(profileEnd - profileStart);

        const profileSuccess = check(profileRes, {
            'profile status is 200 or 401': (r) => r.status === 200 || r.status === 401,
            'profile response time < 500ms': (r) => r.timings.duration < 500,
        });

        profileSuccessRate.add(profileRes.status === 200);

        // Check for session persistence
        if (profileRes.status === 401) {
            sessionLossErrors.add(1);
            console.log(`[${agentId}] Session lost on profile request`);
        }

        sleep(0.3);
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // PHASE 3: Session Persistence Test - اختبار استمرارية الجلسة
    // ═══════════════════════════════════════════════════════════════════════════

    group('Phase 3: Session Persistence', () => {
        // Make 3 consecutive requests to test session across instances
        let sessionPersisted = true;

        for (let i = 0; i < 3; i++) {
            const res = http.get(`${BASE_URL}/api/profile`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'X-Agent-ID': agentId,
                    'X-Request-Sequence': i.toString(),
                },
                timeout: '30s',
            });

            if (res.status === 401) {
                sessionPersisted = false;
                sessionLossErrors.add(1);
            }

            sleep(0.2);
        }

        sessionPersistenceRate.add(sessionPersisted);
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // PHASE 4: Field Operations - عمليات الحقول
    // ═══════════════════════════════════════════════════════════════════════════

    group('Phase 4: Field Operations', () => {
        // List fields
        const listStart = Date.now();
        const listRes = http.get(`${BASE_URL}/api/fields?tenant_id=tenant_simulation&limit=10`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'X-Agent-ID': agentId,
            },
            timeout: '30s',
        });
        fieldListDuration.add(Date.now() - listStart);

        check(listRes, {
            'list fields status OK': (r) => r.status === 200 || r.status === 401,
        });

        // Create field (test for race conditions)
        const fieldData = {
            tenant_id: 'tenant_simulation',
            name: `Agent ${agentId} Field ${randomString(4)}`,
            name_ar: `حقل الوكيل ${agentId}`,
            crop_type: 'wheat',
            area_hectares: Math.random() * 10 + 1,
            geometry: {
                type: 'Polygon',
                coordinates: [[
                    [44.19, 15.37],
                    [44.20, 15.37],
                    [44.20, 15.38],
                    [44.19, 15.38],
                    [44.19, 15.37],
                ]],
            },
        };

        const createStart = Date.now();
        const createRes = http.post(`${BASE_URL}/api/fields`, JSON.stringify(fieldData), {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-Agent-ID': agentId,
            },
            timeout: '30s',
        });
        fieldCreateDuration.add(Date.now() - createStart);

        const createSuccess = check(createRes, {
            'create field status is 201 or 200': (r) => r.status === 201 || r.status === 200,
            'create field response time < 1s': (r) => r.timings.duration < 1000,
        });

        fieldOpsSuccessRate.add(createRes.status === 201 || createRes.status === 200);

        if (createRes.status === 201 || createRes.status === 200) {
            try {
                const body = JSON.parse(createRes.body);
                fieldId = body.id || body.field_id;
            } catch (e) {
                // Ignore parse errors
            }
        } else {
            categorizeError(createRes);
        }

        sleep(0.5);
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // PHASE 5: Cleanup - التنظيف
    // ═══════════════════════════════════════════════════════════════════════════

    if (fieldId) {
        group('Phase 5: Cleanup', () => {
            const deleteRes = http.del(`${BASE_URL}/api/fields/${fieldId}`, null, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'X-Agent-ID': agentId,
                },
                timeout: '30s',
            });

            check(deleteRes, {
                'delete field successful': (r) => r.status === 200 || r.status === 204 || r.status === 404,
            });

            sleep(0.3);
        });
    }

    // Think time between iterations
    sleep(Math.random() * 2 + 1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// TEARDOWN FUNCTION - يعمل مرة واحدة بعد الاختبار
// ═══════════════════════════════════════════════════════════════════════════════

export function teardown(data) {
    const endTime = new Date().toISOString();

    console.log('\n═══════════════════════════════════════════════════════════════');
    console.log('  SAHOOL IDP - Agent Simulation Complete');
    console.log('  اكتملت محاكاة الوكلاء لمنصة سهول');
    console.log('═══════════════════════════════════════════════════════════════');
    console.log(`  Start Time: ${data.startTime}`);
    console.log(`  End Time: ${endTime}`);
    console.log('═══════════════════════════════════════════════════════════════');
    console.log('\n  Check the metrics above for:');
    console.log('  - connection_pool_errors: Should be < 10');
    console.log('  - session_loss_errors: Should be < 5');
    console.log('  - race_condition_errors: Should be < 5');
    console.log('  - login_success_rate: Should be > 95%');
    console.log('  - session_persistence_rate: Should be > 90%');
    console.log('═══════════════════════════════════════════════════════════════\n');
}

// ═══════════════════════════════════════════════════════════════════════════════
// HANDLER SUMMARY - ملخص المعالج
// ═══════════════════════════════════════════════════════════════════════════════

export function handleSummary(data) {
    const summary = {
        timestamp: new Date().toISOString(),
        environment: ENVIRONMENT,
        agent_count: AGENT_COUNT,
        metrics: {
            total_requests: data.metrics.http_reqs?.values?.count || 0,
            failed_requests: data.metrics.http_req_failed?.values?.rate || 0,
            avg_duration: data.metrics.http_req_duration?.values?.avg || 0,
            p95_duration: data.metrics.http_req_duration?.values['p(95)'] || 0,
            login_success: data.metrics.login_success_rate?.values?.rate || 0,
            session_persistence: data.metrics.session_persistence_rate?.values?.rate || 0,
        },
        errors: {
            connection_pool: data.metrics.connection_pool_errors?.values?.count || 0,
            session_loss: data.metrics.session_loss_errors?.values?.count || 0,
            race_condition: data.metrics.race_condition_errors?.values?.count || 0,
            timeout: data.metrics.timeout_errors?.values?.count || 0,
        },
    };

    return {
        '/results/agent-simulation-summary.json': JSON.stringify(summary, null, 2),
        'stdout': textSummary(data, { indent: '  ', enableColors: true }),
    };
}

// Text summary helper
function textSummary(data, opts) {
    const indent = opts.indent || '';

    let out = '\n' + indent + '═══════════════════════════════════════════════════════════════\n';
    out += indent + '  AGENT SIMULATION SUMMARY - ملخص محاكاة الوكلاء\n';
    out += indent + '═══════════════════════════════════════════════════════════════\n\n';

    // Key metrics
    out += indent + '  KEY METRICS:\n';
    out += indent + '  ───────────────────────────────────────────────────────────────\n';

    const metrics = [
        { name: 'Total Requests', value: data.metrics.http_reqs?.values?.count || 0 },
        { name: 'Failed Rate', value: ((data.metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2) + '%' },
        { name: 'Avg Duration', value: (data.metrics.http_req_duration?.values?.avg || 0).toFixed(2) + 'ms' },
        { name: 'P95 Duration', value: (data.metrics.http_req_duration?.values['p(95)'] || 0).toFixed(2) + 'ms' },
    ];

    for (const m of metrics) {
        out += indent + `    ${m.name}: ${m.value}\n`;
    }

    // Error summary
    out += '\n' + indent + '  ERROR ANALYSIS:\n';
    out += indent + '  ───────────────────────────────────────────────────────────────\n';
    out += indent + `    Connection Pool Errors: ${data.metrics.connection_pool_errors?.values?.count || 0}\n`;
    out += indent + `    Session Loss Errors: ${data.metrics.session_loss_errors?.values?.count || 0}\n`;
    out += indent + `    Race Condition Errors: ${data.metrics.race_condition_errors?.values?.count || 0}\n`;
    out += indent + `    Timeout Errors: ${data.metrics.timeout_errors?.values?.count || 0}\n`;

    out += '\n' + indent + '═══════════════════════════════════════════════════════════════\n';

    return out;
}
