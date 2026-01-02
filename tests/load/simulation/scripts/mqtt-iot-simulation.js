/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * SAHOOL IDP - MQTT/IoT Device Simulation
 * محاكاة أجهزة إنترنت الأشياء و MQTT لمنصة سهول
 * ═══════════════════════════════════════════════════════════════════════════════
 *
 * This script simulates IoT devices and sensors communicating via HTTP/REST API
 * (since k6 doesn't natively support MQTT, we simulate the HTTP gateway layer)
 *
 * Simulated Devices:
 * - Soil Moisture Sensors (40%)
 * - Weather Stations (25%)
 * - Irrigation Controllers (20%)
 * - GPS Trackers (15%)
 *
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Rate, Trend, Gauge } from 'k6/metrics';
import { randomIntBetween, randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8081';
const IOT_GATEWAY_URL = __ENV.IOT_GATEWAY_URL || `${BASE_URL}/api/iot`;
const TOTAL_DEVICES = parseInt(__ENV.TOTAL_DEVICES) || 50;
const TEST_DURATION = __ENV.TEST_DURATION || '5m';
const MQTT_TOPIC_PREFIX = __ENV.MQTT_TOPIC_PREFIX || 'sahool/iot';

// Device distribution
const SOIL_SENSOR_RATIO = 0.40;      // 40% soil moisture sensors
const WEATHER_STATION_RATIO = 0.25;  // 25% weather stations
const IRRIGATION_RATIO = 0.20;       // 20% irrigation controllers
const GPS_TRACKER_RATIO = 0.15;      // 15% GPS trackers

// ═══════════════════════════════════════════════════════════════════════════════
// CUSTOM METRICS
// ═══════════════════════════════════════════════════════════════════════════════

// Success rates
const iotPublishSuccess = new Rate('iot_publish_success_rate');
const iotSubscribeSuccess = new Rate('iot_subscribe_success_rate');
const deviceAuthSuccess = new Rate('device_auth_success_rate');
const telemetrySuccess = new Rate('telemetry_success_rate');

// Device-specific metrics
const soilSensorSuccess = new Rate('soil_sensor_success');
const weatherStationSuccess = new Rate('weather_station_success');
const irrigationSuccess = new Rate('irrigation_success');
const gpsTrackerSuccess = new Rate('gps_tracker_success');

// Counters
const messagesPublished = new Counter('mqtt_messages_published');
const messagesReceived = new Counter('mqtt_messages_received');
const deviceErrors = new Counter('device_errors');
const connectionTimeouts = new Counter('connection_timeouts');
const authFailures = new Counter('auth_failures');

// Response times
const publishLatency = new Trend('mqtt_publish_latency_ms', true);
const subscribeLatency = new Trend('mqtt_subscribe_latency_ms', true);
const authLatency = new Trend('device_auth_latency_ms', true);

// Active devices
const activeDevices = new Gauge('active_iot_devices');

// ═══════════════════════════════════════════════════════════════════════════════
// DEVICE CONFIGURATIONS
// ═══════════════════════════════════════════════════════════════════════════════

const SOIL_SENSOR_MODELS = [
    { model: 'SM-100', manufacturer: 'SoilTech', protocol: 'mqtt', firmware: '2.3.1' },
    { model: 'SM-200-PRO', manufacturer: 'SoilTech', protocol: 'mqtt', firmware: '3.0.0' },
    { model: 'MS-500', manufacturer: 'AgriSense', protocol: 'mqtt', firmware: '1.5.2' },
];

const WEATHER_STATION_MODELS = [
    { model: 'WS-3000', manufacturer: 'WeatherPro', protocol: 'mqtt', firmware: '4.1.0' },
    { model: 'AWS-100', manufacturer: 'AgriWeather', protocol: 'mqtt', firmware: '2.0.5' },
];

const IRRIGATION_MODELS = [
    { model: 'IC-2000', manufacturer: 'IrriControl', protocol: 'mqtt', firmware: '3.2.1' },
    { model: 'SmartDrip-500', manufacturer: 'HydroSystems', protocol: 'mqtt', firmware: '1.8.0' },
];

const GPS_TRACKER_MODELS = [
    { model: 'GT-100', manufacturer: 'TrackPro', protocol: 'mqtt', firmware: '2.1.0' },
    { model: 'FieldTracker-X', manufacturer: 'AgriTrack', protocol: 'mqtt', firmware: '1.2.3' },
];

const SAUDI_FARM_LOCATIONS = [
    { name: 'Al-Kharj Farm', lat: 24.1500, lng: 47.3000, region: 'Riyadh' },
    { name: 'Al-Ahsa Oasis', lat: 25.3800, lng: 49.5900, region: 'Eastern' },
    { name: 'Tabuk Agricultural Zone', lat: 28.3838, lng: 36.5550, region: 'Tabuk' },
    { name: 'Wadi Al-Dawasir', lat: 20.4910, lng: 44.7800, region: 'Riyadh' },
    { name: 'Jizan Farm', lat: 16.8892, lng: 42.5511, region: 'Jizan' },
    { name: 'Al-Jouf Agricultural', lat: 29.7850, lng: 40.1000, region: 'Al-Jouf' },
];

// ═══════════════════════════════════════════════════════════════════════════════
// K6 OPTIONS
// ═══════════════════════════════════════════════════════════════════════════════

export const options = {
    scenarios: {
        // Soil Moisture Sensors (frequent readings)
        soil_sensors: {
            executor: 'constant-arrival-rate',
            rate: Math.ceil(TOTAL_DEVICES * SOIL_SENSOR_RATIO) * 2, // 2 readings per minute per device
            timeUnit: '1m',
            duration: TEST_DURATION,
            preAllocatedVUs: Math.ceil(TOTAL_DEVICES * SOIL_SENSOR_RATIO),
            exec: 'soilSensorFlow',
            tags: { device_type: 'soil_sensor', protocol: 'mqtt' },
        },

        // Weather Stations (periodic updates)
        weather_stations: {
            executor: 'constant-arrival-rate',
            rate: Math.ceil(TOTAL_DEVICES * WEATHER_STATION_RATIO), // 1 update per minute
            timeUnit: '1m',
            duration: TEST_DURATION,
            preAllocatedVUs: Math.ceil(TOTAL_DEVICES * WEATHER_STATION_RATIO),
            exec: 'weatherStationFlow',
            tags: { device_type: 'weather_station', protocol: 'mqtt' },
        },

        // Irrigation Controllers (command-driven)
        irrigation_controllers: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '1m', target: Math.ceil(TOTAL_DEVICES * IRRIGATION_RATIO) },
                { duration: '3m', target: Math.ceil(TOTAL_DEVICES * IRRIGATION_RATIO) },
                { duration: '1m', target: 0 },
            ],
            exec: 'irrigationControllerFlow',
            tags: { device_type: 'irrigation', protocol: 'mqtt' },
        },

        // GPS Trackers (continuous location updates)
        gps_trackers: {
            executor: 'constant-arrival-rate',
            rate: Math.ceil(TOTAL_DEVICES * GPS_TRACKER_RATIO) * 6, // 6 updates per minute (every 10s)
            timeUnit: '1m',
            duration: TEST_DURATION,
            preAllocatedVUs: Math.ceil(TOTAL_DEVICES * GPS_TRACKER_RATIO),
            exec: 'gpsTrackerFlow',
            tags: { device_type: 'gps_tracker', protocol: 'mqtt' },
        },
    },

    thresholds: {
        // Overall IoT metrics
        'iot_publish_success_rate': ['rate>0.95'],
        'device_auth_success_rate': ['rate>0.99'],
        'telemetry_success_rate': ['rate>0.95'],

        // Device-specific thresholds
        'soil_sensor_success': ['rate>0.95'],
        'weather_station_success': ['rate>0.95'],
        'irrigation_success': ['rate>0.90'],
        'gps_tracker_success': ['rate>0.95'],

        // Latency thresholds
        'mqtt_publish_latency_ms': ['p(95)<500', 'avg<200'],
        'device_auth_latency_ms': ['p(95)<300', 'avg<100'],

        // Error thresholds
        'device_errors': ['count<50'],
        'connection_timeouts': ['count<20'],
        'auth_failures': ['count<10'],
    },
};

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

function generateDeviceId(type, vu) {
    return `${type}_${vu.toString().padStart(4, '0')}_${Date.now().toString(36)}`;
}

function generateMacAddress() {
    const hex = '0123456789ABCDEF';
    let mac = '';
    for (let i = 0; i < 6; i++) {
        if (i > 0) mac += ':';
        mac += hex.charAt(Math.floor(Math.random() * 16));
        mac += hex.charAt(Math.floor(Math.random() * 16));
    }
    return mac;
}

function getDeviceHeaders(deviceId, deviceType, model) {
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Device-ID': deviceId,
        'X-Device-Type': deviceType,
        'X-Device-Model': model.model,
        'X-Device-Manufacturer': model.manufacturer,
        'X-Device-Firmware': model.firmware,
        'X-Protocol': 'mqtt-http-bridge',
        'X-API-Key': `iot_${deviceType}_${__VU}`,
    };
}

function generateGPS(location) {
    return {
        latitude: location.lat + (Math.random() - 0.5) * 0.02,
        longitude: location.lng + (Math.random() - 0.5) * 0.02,
        altitude: randomIntBetween(100, 500),
        accuracy: randomIntBetween(3, 15),
        speed: Math.random() * 5, // m/s
        heading: randomIntBetween(0, 360),
    };
}

function authenticateDevice(deviceId, deviceType, headers) {
    const start = Date.now();
    const res = http.post(`${IOT_GATEWAY_URL}/auth/device`, JSON.stringify({
        device_id: deviceId,
        device_type: deviceType,
        mac_address: generateMacAddress(),
        timestamp: new Date().toISOString(),
    }), { headers, tags: { name: 'device_auth' }, timeout: '10s' });

    authLatency.add(Date.now() - start);

    const success = check(res, {
        'device auth status OK': (r) => r.status === 200 || r.status === 201 || r.status === 404,
    });

    deviceAuthSuccess.add(success ? 1 : 0);

    if (!success) {
        authFailures.add(1);
        return null;
    }

    try {
        const body = JSON.parse(res.body);
        return body.token || body.access_token || `mock_token_${deviceId}`;
    } catch {
        return `mock_token_${deviceId}`;
    }
}

function publishTelemetry(topic, payload, headers) {
    const start = Date.now();
    const res = http.post(`${IOT_GATEWAY_URL}/telemetry`, JSON.stringify({
        topic: topic,
        payload: payload,
        qos: 1,
        retain: false,
        timestamp: new Date().toISOString(),
    }), { headers, tags: { name: 'mqtt_publish' }, timeout: '10s' });

    publishLatency.add(Date.now() - start);
    messagesPublished.add(1);

    const success = check(res, {
        'publish status OK': (r) => r.status === 200 || r.status === 201 || r.status === 202 || r.status === 404,
    });

    iotPublishSuccess.add(success ? 1 : 0);
    telemetrySuccess.add(success ? 1 : 0);

    if (!success) {
        deviceErrors.add(1);
        if (res.error && res.error.includes('timeout')) {
            connectionTimeouts.add(1);
        }
    }

    return success;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SOIL MOISTURE SENSOR FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function soilSensorFlow() {
    const model = randomItem(SOIL_SENSOR_MODELS);
    const location = randomItem(SAUDI_FARM_LOCATIONS);
    const deviceId = generateDeviceId('soil', __VU);
    const headers = getDeviceHeaders(deviceId, 'soil_sensor', model);

    activeDevices.add(1);

    group('Soil Sensor: Publish Reading', () => {
        // Authenticate first
        const token = authenticateDevice(deviceId, 'soil_sensor', headers);
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // Generate soil moisture data
        const depth1 = randomIntBetween(10, 30); // cm
        const depth2 = randomIntBetween(30, 60); // cm

        const payload = {
            device_id: deviceId,
            readings: [
                {
                    type: 'soil_moisture',
                    depth_cm: depth1,
                    value: 15 + Math.random() * 45, // 15-60%
                    unit: 'percent',
                },
                {
                    type: 'soil_moisture',
                    depth_cm: depth2,
                    value: 20 + Math.random() * 40, // 20-60%
                    unit: 'percent',
                },
                {
                    type: 'soil_temperature',
                    depth_cm: depth1,
                    value: 15 + Math.random() * 25, // 15-40°C
                    unit: 'celsius',
                },
                {
                    type: 'soil_ec', // Electrical conductivity
                    depth_cm: depth1,
                    value: 0.5 + Math.random() * 3, // dS/m
                    unit: 'dS/m',
                },
            ],
            location: {
                ...generateGPS(location),
                farm_name: location.name,
                region: location.region,
            },
            battery_level: randomIntBetween(20, 100),
            signal_strength: -30 - randomIntBetween(0, 60), // dBm
            timestamp: new Date().toISOString(),
        };

        const topic = `${MQTT_TOPIC_PREFIX}/soil/${location.region.toLowerCase()}/${deviceId}`;
        const success = publishTelemetry(topic, payload, headers);
        soilSensorSuccess.add(success ? 1 : 0);
    });

    activeDevices.add(-1);
    sleep(randomIntBetween(1, 3));
}

// ═══════════════════════════════════════════════════════════════════════════════
// WEATHER STATION FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function weatherStationFlow() {
    const model = randomItem(WEATHER_STATION_MODELS);
    const location = randomItem(SAUDI_FARM_LOCATIONS);
    const deviceId = generateDeviceId('weather', __VU);
    const headers = getDeviceHeaders(deviceId, 'weather_station', model);

    activeDevices.add(1);

    group('Weather Station: Publish Data', () => {
        const token = authenticateDevice(deviceId, 'weather_station', headers);
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const payload = {
            device_id: deviceId,
            readings: {
                temperature: {
                    value: 20 + Math.random() * 30, // 20-50°C (Saudi Arabia)
                    unit: 'celsius',
                },
                humidity: {
                    value: 10 + Math.random() * 50, // 10-60%
                    unit: 'percent',
                },
                pressure: {
                    value: 1000 + Math.random() * 30, // hPa
                    unit: 'hPa',
                },
                wind_speed: {
                    value: Math.random() * 30, // 0-30 m/s
                    unit: 'm/s',
                },
                wind_direction: {
                    value: randomIntBetween(0, 360),
                    unit: 'degrees',
                },
                solar_radiation: {
                    value: 200 + Math.random() * 800, // W/m²
                    unit: 'W/m2',
                },
                uv_index: {
                    value: Math.random() * 11, // 0-11
                    unit: 'index',
                },
                precipitation: {
                    value: Math.random() < 0.1 ? Math.random() * 10 : 0, // mm
                    unit: 'mm',
                },
                evapotranspiration: {
                    value: 2 + Math.random() * 8, // mm/day
                    unit: 'mm/day',
                },
            },
            location: {
                ...generateGPS(location),
                farm_name: location.name,
                region: location.region,
                elevation: randomIntBetween(100, 1500),
            },
            battery_level: randomIntBetween(50, 100),
            solar_panel_voltage: 12 + Math.random() * 6,
            timestamp: new Date().toISOString(),
        };

        const topic = `${MQTT_TOPIC_PREFIX}/weather/${location.region.toLowerCase()}/${deviceId}`;
        const success = publishTelemetry(topic, payload, headers);
        weatherStationSuccess.add(success ? 1 : 0);
    });

    activeDevices.add(-1);
    sleep(randomIntBetween(2, 5));
}

// ═══════════════════════════════════════════════════════════════════════════════
// IRRIGATION CONTROLLER FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function irrigationControllerFlow() {
    const model = randomItem(IRRIGATION_MODELS);
    const location = randomItem(SAUDI_FARM_LOCATIONS);
    const deviceId = generateDeviceId('irrigation', __VU);
    const headers = getDeviceHeaders(deviceId, 'irrigation_controller', model);

    activeDevices.add(1);

    // Subscribe to commands
    group('Irrigation: Subscribe to Commands', () => {
        const start = Date.now();
        const res = http.get(`${IOT_GATEWAY_URL}/commands/${deviceId}`, {
            headers,
            tags: { name: 'mqtt_subscribe' },
            timeout: '10s',
        });
        subscribeLatency.add(Date.now() - start);

        const success = check(res, {
            'subscribe status OK': (r) => r.status === 200 || r.status === 204 || r.status === 404,
        });
        iotSubscribeSuccess.add(success ? 1 : 0);

        if (res.status === 200) {
            messagesReceived.add(1);
        }
    });

    sleep(1);

    // Publish status
    group('Irrigation: Publish Status', () => {
        const token = authenticateDevice(deviceId, 'irrigation_controller', headers);
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const zones = randomIntBetween(4, 12);
        const zoneStatuses = [];
        for (let i = 1; i <= zones; i++) {
            zoneStatuses.push({
                zone_id: i,
                status: randomItem(['active', 'idle', 'scheduled', 'fault']),
                flow_rate: Math.random() * 50, // L/min
                duration_today: randomIntBetween(0, 120), // minutes
                next_schedule: new Date(Date.now() + randomIntBetween(1, 24) * 3600000).toISOString(),
            });
        }

        const payload = {
            device_id: deviceId,
            controller_status: randomItem(['running', 'standby', 'maintenance']),
            zones: zoneStatuses,
            total_water_today: randomIntBetween(100, 5000), // liters
            pressure: 2 + Math.random() * 4, // bar
            location: {
                ...generateGPS(location),
                farm_name: location.name,
            },
            power_source: randomItem(['solar', 'grid', 'battery']),
            battery_level: randomIntBetween(30, 100),
            timestamp: new Date().toISOString(),
        };

        const topic = `${MQTT_TOPIC_PREFIX}/irrigation/${location.region.toLowerCase()}/${deviceId}/status`;
        const success = publishTelemetry(topic, payload, headers);
        irrigationSuccess.add(success ? 1 : 0);
    });

    activeDevices.add(-1);
    sleep(randomIntBetween(5, 15));
}

// ═══════════════════════════════════════════════════════════════════════════════
// GPS TRACKER FLOW
// ═══════════════════════════════════════════════════════════════════════════════

export function gpsTrackerFlow() {
    const model = randomItem(GPS_TRACKER_MODELS);
    const location = randomItem(SAUDI_FARM_LOCATIONS);
    const deviceId = generateDeviceId('gps', __VU);
    const headers = getDeviceHeaders(deviceId, 'gps_tracker', model);

    activeDevices.add(1);

    group('GPS Tracker: Publish Location', () => {
        const token = authenticateDevice(deviceId, 'gps_tracker', headers);
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const gps = generateGPS(location);
        const payload = {
            device_id: deviceId,
            tracker_type: randomItem(['vehicle', 'equipment', 'personnel']),
            position: {
                ...gps,
                timestamp: new Date().toISOString(),
            },
            motion: {
                is_moving: Math.random() > 0.3,
                speed_kmh: gps.speed * 3.6,
                heading: gps.heading,
                distance_today: randomIntBetween(0, 100), // km
            },
            geofence: {
                inside_boundary: Math.random() > 0.1,
                nearest_boundary_m: randomIntBetween(10, 1000),
                zone_name: location.name,
            },
            telemetry: {
                battery_level: randomIntBetween(10, 100),
                signal_strength: -30 - randomIntBetween(0, 70),
                satellites_in_view: randomIntBetween(6, 14),
                hdop: 0.5 + Math.random() * 2,
            },
            timestamp: new Date().toISOString(),
        };

        const topic = `${MQTT_TOPIC_PREFIX}/gps/${location.region.toLowerCase()}/${deviceId}`;
        const success = publishTelemetry(topic, payload, headers);
        gpsTrackerSuccess.add(success ? 1 : 0);
    });

    activeDevices.add(-1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SETUP & TEARDOWN
// ═══════════════════════════════════════════════════════════════════════════════

export function setup() {
    console.log('═══════════════════════════════════════════════════════════════════════════════');
    console.log('           SAHOOL IDP - MQTT/IoT Device Simulation');
    console.log('           محاكاة أجهزة إنترنت الأشياء لمنصة سهول');
    console.log('═══════════════════════════════════════════════════════════════════════════════');
    console.log('');
    console.log(`  TOTAL SIMULATED DEVICES: ${TOTAL_DEVICES}`);
    console.log('');
    console.log('  DEVICE DISTRIBUTION:');
    console.log('  ────────────────────────────────────────────────────────────────────────────');
    console.log(`  Soil Moisture Sensors (40%): ${Math.ceil(TOTAL_DEVICES * SOIL_SENSOR_RATIO)} devices`);
    console.log(`  Weather Stations (25%):       ${Math.ceil(TOTAL_DEVICES * WEATHER_STATION_RATIO)} devices`);
    console.log(`  Irrigation Controllers (20%): ${Math.ceil(TOTAL_DEVICES * IRRIGATION_RATIO)} devices`);
    console.log(`  GPS Trackers (15%):           ${Math.ceil(TOTAL_DEVICES * GPS_TRACKER_RATIO)} devices`);
    console.log('');
    console.log(`  IoT Gateway URL: ${IOT_GATEWAY_URL}`);
    console.log(`  MQTT Topic Prefix: ${MQTT_TOPIC_PREFIX}`);
    console.log(`  Test Duration: ${TEST_DURATION}`);
    console.log('═══════════════════════════════════════════════════════════════════════════════');
    console.log('');

    // Health check
    const healthRes = http.get(`${BASE_URL}/health`);
    if (healthRes.status !== 200) {
        console.warn('Warning: IoT Gateway health check failed');
    } else {
        console.log('IoT Gateway health check passed');
    }

    return { startTime: Date.now() };
}

export function teardown(data) {
    const duration = (Date.now() - data.startTime) / 1000;
    console.log('');
    console.log('═══════════════════════════════════════════════════════════════════════════════');
    console.log('  MQTT/IoT Simulation Complete');
    console.log(`  Duration: ${duration.toFixed(2)}s`);
    console.log('═══════════════════════════════════════════════════════════════════════════════');
}

// ═══════════════════════════════════════════════════════════════════════════════
// SUMMARY HANDLER
// ═══════════════════════════════════════════════════════════════════════════════

export function handleSummary(data) {
    const summary = {
        timestamp: new Date().toISOString(),
        test_type: 'mqtt_iot_simulation',
        configuration: {
            total_devices: TOTAL_DEVICES,
            duration: TEST_DURATION,
            topic_prefix: MQTT_TOPIC_PREFIX,
        },
        device_distribution: {
            soil_sensors: Math.ceil(TOTAL_DEVICES * SOIL_SENSOR_RATIO),
            weather_stations: Math.ceil(TOTAL_DEVICES * WEATHER_STATION_RATIO),
            irrigation_controllers: Math.ceil(TOTAL_DEVICES * IRRIGATION_RATIO),
            gps_trackers: Math.ceil(TOTAL_DEVICES * GPS_TRACKER_RATIO),
        },
        mqtt_metrics: {
            messages_published: data.metrics.mqtt_messages_published?.values?.count || 0,
            messages_received: data.metrics.mqtt_messages_received?.values?.count || 0,
            publish_success_rate: ((data.metrics.iot_publish_success_rate?.values?.rate || 0) * 100).toFixed(2) + '%',
            subscribe_success_rate: ((data.metrics.iot_subscribe_success_rate?.values?.rate || 0) * 100).toFixed(2) + '%',
        },
        device_success_rates: {
            soil_sensors: ((data.metrics.soil_sensor_success?.values?.rate || 0) * 100).toFixed(2) + '%',
            weather_stations: ((data.metrics.weather_station_success?.values?.rate || 0) * 100).toFixed(2) + '%',
            irrigation: ((data.metrics.irrigation_success?.values?.rate || 0) * 100).toFixed(2) + '%',
            gps_trackers: ((data.metrics.gps_tracker_success?.values?.rate || 0) * 100).toFixed(2) + '%',
        },
        latency: {
            publish_p95: (data.metrics.mqtt_publish_latency_ms?.values?.['p(95)'] || 0).toFixed(0) + 'ms',
            publish_avg: (data.metrics.mqtt_publish_latency_ms?.values?.avg || 0).toFixed(0) + 'ms',
            auth_p95: (data.metrics.device_auth_latency_ms?.values?.['p(95)'] || 0).toFixed(0) + 'ms',
        },
        errors: {
            device_errors: data.metrics.device_errors?.values?.count || 0,
            connection_timeouts: data.metrics.connection_timeouts?.values?.count || 0,
            auth_failures: data.metrics.auth_failures?.values?.count || 0,
        },
    };

    const textSummary = `
═══════════════════════════════════════════════════════════════════════════════════════
                    MQTT/IoT SIMULATION RESULTS
                    نتائج محاكاة إنترنت الأشياء
═══════════════════════════════════════════════════════════════════════════════════════

DEVICE STATISTICS:
────────────────────────────────────────────────────────────────────────────────────────
  Total Devices Simulated: ${TOTAL_DEVICES}
  Messages Published: ${summary.mqtt_metrics.messages_published}
  Messages Received: ${summary.mqtt_metrics.messages_received}

SUCCESS RATES:
────────────────────────────────────────────────────────────────────────────────────────
  Publish Success: ${summary.mqtt_metrics.publish_success_rate}
  Device Auth Success: ${((data.metrics.device_auth_success_rate?.values?.rate || 0) * 100).toFixed(2)}%

  By Device Type:
  Soil Sensors:     ${summary.device_success_rates.soil_sensors}
  Weather Stations: ${summary.device_success_rates.weather_stations}
  Irrigation:       ${summary.device_success_rates.irrigation}
  GPS Trackers:     ${summary.device_success_rates.gps_trackers}

LATENCY:
────────────────────────────────────────────────────────────────────────────────────────
  Publish P95: ${summary.latency.publish_p95}
  Publish Avg: ${summary.latency.publish_avg}
  Auth P95:    ${summary.latency.auth_p95}

ERRORS:
────────────────────────────────────────────────────────────────────────────────────────
  Device Errors:       ${summary.errors.device_errors}
  Connection Timeouts: ${summary.errors.connection_timeouts}
  Auth Failures:       ${summary.errors.auth_failures}

═══════════════════════════════════════════════════════════════════════════════════════
`;

    return {
        'stdout': textSummary,
        './results/mqtt-iot-simulation-summary.json': JSON.stringify(summary, null, 2),
    };
}

// Default function for standalone execution
export default function() {
    const rand = Math.random();
    if (rand < SOIL_SENSOR_RATIO) {
        soilSensorFlow();
    } else if (rand < SOIL_SENSOR_RATIO + WEATHER_STATION_RATIO) {
        weatherStationFlow();
    } else if (rand < SOIL_SENSOR_RATIO + WEATHER_STATION_RATIO + IRRIGATION_RATIO) {
        irrigationControllerFlow();
    } else {
        gpsTrackerFlow();
    }
}
