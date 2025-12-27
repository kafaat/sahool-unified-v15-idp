/**
 * k6 Load Testing Helpers
 * SAHOOL Platform - Utility Functions
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { config, yemenLocations, cropTypes, operationTypes } from './config.js';

// Custom metrics
export const authSuccessRate = new Rate('auth_success_rate');
export const fieldCreationTrend = new Trend('field_creation_duration');
export const satelliteAnalysisTrend = new Trend('satellite_analysis_duration');
export const weatherForecastTrend = new Trend('weather_forecast_duration');
export const apiErrors = new Counter('api_errors');
export const quotaExceeded = new Counter('quota_exceeded_errors');

/**
 * Authentication Helper
 * Creates a mock JWT token for load testing
 * In production, this would call the actual auth service
 */
export function authenticate(email = null, password = null) {
  const userEmail = email || config.testUser.email;
  const userPassword = password || config.testUser.password;

  // Mock authentication - create a test token
  // In real scenario, this would call: POST /auth/login
  const payload = JSON.stringify({
    email: userEmail,
    password: userPassword,
  });

  // For load testing, we simulate the auth token
  // Replace this with actual auth endpoint when available
  const mockToken = generateMockToken(userEmail);

  return {
    success: true,
    token: mockToken,
    userId: `user_${randomString(8)}`,
    tenantId: config.tenantId,
  };
}

/**
 * Generate mock JWT token for testing
 * In production, replace with actual JWT from auth service
 */
function generateMockToken(email) {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify({
    sub: `user_${randomString(8)}`,
    email: email,
    tenant_id: config.tenantId,
    roles: ['farmer'],
    permissions: ['field:read', 'field:write'],
    exp: Math.floor(Date.now() / 1000) + 3600,
    iat: Math.floor(Date.now() / 1000),
  }));
  const signature = randomString(32);

  return `${header}.${payload}.${signature}`;
}

/**
 * HTTP Request wrapper with authentication
 */
export function authenticatedRequest(method, url, body = null, token = null, params = {}) {
  const headers = {
    'Content-Type': 'application/json',
    'X-Tenant-Id': config.tenantId,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const requestParams = {
    headers: headers,
    timeout: config.timeout,
    ...params,
  };

  let response;
  switch (method.toUpperCase()) {
    case 'GET':
      response = http.get(url, requestParams);
      break;
    case 'POST':
      response = http.post(url, body ? JSON.stringify(body) : null, requestParams);
      break;
    case 'PUT':
      response = http.put(url, body ? JSON.stringify(body) : null, requestParams);
      break;
    case 'DELETE':
      response = http.del(url, null, requestParams);
      break;
    default:
      throw new Error(`Unsupported HTTP method: ${method}`);
  }

  // Track errors
  if (response.status >= 400) {
    apiErrors.add(1);

    if (response.status === 429) {
      quotaExceeded.add(1);
    }
  }

  return response;
}

/**
 * Validate response helper
 */
export function validateResponse(response, expectedStatus = 200, checkName = 'response') {
  const checks = {};
  checks[`${checkName}: status is ${expectedStatus}`] = response.status === expectedStatus;

  if (response.status === expectedStatus && response.body) {
    try {
      const body = JSON.parse(response.body);
      checks[`${checkName}: has valid JSON body`] = true;
      return { success: check(response, checks), data: body };
    } catch (e) {
      checks[`${checkName}: has valid JSON body`] = false;
      return { success: check(response, checks), data: null };
    }
  }

  return { success: check(response, checks), data: null };
}

/**
 * Random field generator
 */
export function generateRandomField(tenantId = null) {
  const tenant = tenantId || config.tenantId;
  const location = randomElement(yemenLocations);
  const crop = randomElement(cropTypes);

  // Generate random polygon around the location
  const coordinates = generateRandomPolygon(location.lat, location.lon);

  return {
    tenant_id: tenant,
    name: `Test Field ${randomString(6)}`,
    name_ar: `حقل اختبار ${randomString(6)}`,
    crop_type: crop,
    area_hectares: randomFloat(1.0, 20.0),
    geometry: {
      type: 'Polygon',
      coordinates: [coordinates],
    },
    soil_type: randomElement(['loamy', 'sandy', 'clay', 'silty']),
    irrigation_type: randomElement(['drip', 'sprinkler', 'flood', 'furrow']),
    planting_date: randomPastDate(90), // within last 90 days
    metadata: {
      test: true,
      loadtest_id: `loadtest_${Date.now()}`,
    },
  };
}

/**
 * Generate random polygon coordinates
 */
function generateRandomPolygon(centerLat, centerLon, points = 4, radius = 0.01) {
  const coordinates = [];
  const angleStep = (2 * Math.PI) / points;

  for (let i = 0; i <= points; i++) {
    const angle = i * angleStep;
    const r = radius * (0.8 + Math.random() * 0.4); // vary radius
    const lat = centerLat + r * Math.cos(angle);
    const lon = centerLon + r * Math.sin(angle);
    coordinates.push([lon, lat]); // GeoJSON format: [lon, lat]
  }

  return coordinates;
}

/**
 * Generate random operation
 */
export function generateRandomOperation(fieldId, tenantId = null) {
  const tenant = tenantId || config.tenantId;
  const operationType = randomElement(operationTypes);

  return {
    tenant_id: tenant,
    field_id: fieldId,
    operation_type: operationType,
    scheduled_date: randomFutureDate(7), // next 7 days
    notes: `Load test operation: ${operationType}`,
    notes_ar: `عملية اختبار الحمل: ${operationType}`,
    metadata: {
      test: true,
      loadtest_id: `loadtest_${Date.now()}`,
    },
  };
}

/**
 * Generate random task
 */
export function generateRandomTask(fieldId, tenantId = null) {
  const tenant = tenantId || config.tenantId;
  const taskType = randomElement(operationTypes);

  return {
    tenant_id: tenant,
    title: `Load Test Task: ${taskType}`,
    title_ar: `مهمة اختبار الحمل: ${taskType}`,
    description: `Automated load testing task`,
    task_type: taskType,
    priority: randomElement(['low', 'medium', 'high', 'urgent']),
    field_id: fieldId,
    assigned_to: `user_${randomString(8)}`,
    due_date: randomFutureDate(7),
    scheduled_time: `${randomInt(6, 18)}:00`,
    estimated_duration_minutes: randomInt(30, 180),
  };
}

/**
 * Generate random equipment
 */
export function generateRandomEquipment(fieldId = null, tenantId = null) {
  const tenant = tenantId || config.tenantId;
  const equipmentType = randomElement(equipmentTypes);

  return {
    tenant_id: tenant,
    name: `Test ${equipmentType} ${randomString(4)}`,
    name_ar: `${equipmentType} اختبار ${randomString(4)}`,
    equipment_type: equipmentType,
    brand: randomElement(['John Deere', 'Case IH', 'New Holland', 'Kubota']),
    model: `Model-${randomString(6)}`,
    serial_number: `SN-${randomString(10)}`,
    year: randomInt(2018, 2025),
    field_id: fieldId,
    status: 'operational',
  };
}

/**
 * Random string generator
 */
export function randomString(length = 8) {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * Random integer between min and max (inclusive)
 */
export function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Random float between min and max
 */
export function randomFloat(min, max, decimals = 2) {
  const value = Math.random() * (max - min) + min;
  return parseFloat(value.toFixed(decimals));
}

/**
 * Random element from array
 */
export function randomElement(array) {
  return array[Math.floor(Math.random() * array.length)];
}

/**
 * Random past date (ISO string)
 */
export function randomPastDate(daysAgo = 30) {
  const now = new Date();
  const past = new Date(now.getTime() - randomInt(0, daysAgo) * 24 * 60 * 60 * 1000);
  return past.toISOString().split('T')[0];
}

/**
 * Random future date (ISO string)
 */
export function randomFutureDate(daysAhead = 30) {
  const now = new Date();
  const future = new Date(now.getTime() + randomInt(1, daysAhead) * 24 * 60 * 60 * 1000);
  return future.toISOString();
}

/**
 * Think time - random sleep between requests
 */
export function thinkTime(min = 1, max = 3) {
  sleep(randomFloat(min, max, 1));
}

/**
 * Verify JSON response structure
 */
export function verifyJsonStructure(data, requiredFields) {
  const checks = {};

  for (const field of requiredFields) {
    const fieldPath = field.split('.');
    let value = data;

    for (const part of fieldPath) {
      if (value && typeof value === 'object') {
        value = value[part];
      } else {
        value = undefined;
        break;
      }
    }

    checks[`field ${field} exists`] = value !== undefined;
  }

  return check(data, checks);
}

/**
 * Log test iteration info
 */
export function logIteration(iteration, message) {
  if (iteration % 10 === 0) {
    console.log(`[Iteration ${iteration}] ${message}`);
  }
}

/**
 * Calculate success rate from checks
 */
export function calculateSuccessRate(successCount, totalCount) {
  return totalCount > 0 ? (successCount / totalCount) * 100 : 0;
}

/**
 * Batch request helper - send multiple requests in parallel
 */
export function batchRequests(requests) {
  return http.batch(requests);
}

/**
 * Create weather analysis request
 */
export function createWeatherAnalysisRequest(locationId = null) {
  const location = locationId || randomElement(yemenLocations).id;

  return {
    location_id: location,
    days: randomInt(3, 7),
  };
}

/**
 * Create satellite analysis request
 */
export function createSatelliteAnalysisRequest(fieldId, lat = null, lon = null) {
  const location = randomElement(yemenLocations);

  return {
    field_id: fieldId,
    latitude: lat || location.lat,
    longitude: lon || location.lon,
    satellite: randomElement(['sentinel-2', 'landsat-8', 'landsat-9']),
    start_date: randomPastDate(30),
    end_date: new Date().toISOString().split('T')[0],
    cloud_cover_max: randomFloat(10, 30),
  };
}

/**
 * Create irrigation calculation request
 */
export function createIrrigationRequest(fieldId) {
  return {
    field_id: fieldId,
    crop: randomElement(cropTypes),
    growth_stage: randomElement(['initial', 'development', 'mid_season', 'late_season']),
    area_hectares: randomFloat(1.0, 20.0),
    soil_type: randomElement(['loamy', 'sandy', 'clay', 'silty']),
    irrigation_method: randomElement(['drip', 'sprinkler', 'flood', 'furrow']),
    current_soil_moisture: randomFloat(30, 70),
    last_irrigation_date: randomPastDate(7),
  };
}

/**
 * Validate field response structure
 */
export function validateFieldResponse(field) {
  return verifyJsonStructure(field, [
    'id',
    'tenant_id',
    'name',
    'crop_type',
    'area_hectares',
    'created_at',
  ]);
}

/**
 * Validate operation response structure
 */
export function validateOperationResponse(operation) {
  return verifyJsonStructure(operation, [
    'id',
    'tenant_id',
    'field_id',
    'operation_type',
    'scheduled_date',
  ]);
}

/**
 * Error handler
 */
export function handleError(response, context = '') {
  if (response.status >= 400) {
    console.error(`[ERROR ${response.status}] ${context}: ${response.body}`);
    return false;
  }
  return true;
}

/**
 * Setup function - runs once per VU
 */
export function setupVU() {
  console.log(`VU ${__VU} starting...`);
  const auth = authenticate();
  return {
    token: auth.token,
    userId: auth.userId,
    tenantId: auth.tenantId,
  };
}

/**
 * Teardown function - runs once per VU
 */
export function teardownVU(data) {
  console.log(`VU ${__VU} completed. Processed requests.`);
}
