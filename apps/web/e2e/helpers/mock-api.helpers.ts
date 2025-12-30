/**
 * Mock API Helpers for E2E Tests
 * مساعدات API الوهمية للاختبارات
 */

import { Page } from '@playwright/test';
import {
  mockSensors,
  mockActuators,
  mockAlertRules,
  mockSensorReadings,
  mockSensorStats,
} from '../mocks/iot-data';

/**
 * Setup mock API responses for IoT endpoints
 * إعداد استجابات API وهمية لنقاط نهاية IoT
 */
export async function setupIoTMocks(page: Page): Promise<void> {
  // Mock sensors endpoint
  await page.route('**/api/v1/iot/sensors', async (route) => {
    const url = new URL(route.request().url());
    const params = url.searchParams;

    let filteredSensors = [...mockSensors];

    // Apply filters
    if (params.get('type')) {
      filteredSensors = filteredSensors.filter((s) => s.type === params.get('type'));
    }
    if (params.get('status')) {
      filteredSensors = filteredSensors.filter((s) => s.status === params.get('status'));
    }
    if (params.get('field_id')) {
      filteredSensors = filteredSensors.filter((s) => s.location?.fieldId === params.get('field_id'));
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(filteredSensors),
    });
  });

  // Mock sensor by ID endpoint
  await page.route('**/api/v1/iot/sensors/*', async (route) => {
    const url = route.request().url();
    const sensorId = url.split('/').pop();
    const sensor = mockSensors.find((s) => s.id === sensorId);

    if (sensor) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(sensor),
      });
    } else {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Sensor not found' }),
      });
    }
  });

  // Mock sensor readings endpoint
  await page.route('**/api/v1/iot/sensors/readings*', async (route) => {
    const url = new URL(route.request().url());
    const sensorId = url.searchParams.get('sensor_id');
    const readings = sensorId ? mockSensorReadings[sensorId] || [] : [];

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(readings),
    });
  });

  // Mock latest reading endpoint
  await page.route('**/api/v1/iot/sensors/*/latest', async (route) => {
    const url = route.request().url();
    const sensorId = url.split('/').slice(-2, -1)[0];
    const sensor = mockSensors.find((s) => s.id === sensorId);

    if (sensor && sensor.lastReading) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(sensor.lastReading),
      });
    } else {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Reading not found' }),
      });
    }
  });

  // Mock sensor stats endpoint
  await page.route('**/api/v1/iot/sensors/stats', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockSensorStats),
    });
  });

  // Mock actuators endpoint
  await page.route('**/api/v1/iot/actuators*', async (route) => {
    if (route.request().method() === 'GET') {
      const url = new URL(route.request().url());
      const fieldId = url.searchParams.get('field_id');
      let filteredActuators = [...mockActuators];

      if (fieldId) {
        filteredActuators = filteredActuators.filter((a) => a.location?.fieldId === fieldId);
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(filteredActuators),
      });
    } else {
      await route.continue();
    }
  });

  // Mock actuator by ID endpoint
  await page.route('**/api/v1/iot/actuators/*/?(control|mode)?', async (route) => {
    const url = route.request().url();
    const parts = url.split('/');
    const actuatorId = parts[parts.indexOf('actuators') + 1];
    const actuator = mockActuators.find((a) => a.id === actuatorId);

    if (route.request().method() === 'GET' && actuator) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(actuator),
      });
    } else if (route.request().method() === 'POST' && url.includes('control')) {
      // Mock control action
      if (actuator) {
        const updatedActuator = {
          ...actuator,
          status: actuator.status === 'on' ? 'off' : 'on',
          updatedAt: new Date().toISOString(),
        };

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(updatedActuator),
        });
      } else {
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Actuator not found' }),
        });
      }
    } else if (route.request().method() === 'PATCH' && url.includes('mode')) {
      // Mock mode change
      if (actuator) {
        const body = JSON.parse(route.request().postData() || '{}');
        const updatedActuator = {
          ...actuator,
          controlMode: body.mode,
          updatedAt: new Date().toISOString(),
        };

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(updatedActuator),
        });
      } else {
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Actuator not found' }),
        });
      }
    } else {
      await route.continue();
    }
  });

  // Mock alert rules endpoint
  await page.route('**/api/v1/iot/alert-rules*', async (route) => {
    if (route.request().method() === 'GET') {
      const url = new URL(route.request().url());
      const sensorId = url.searchParams.get('sensor_id');
      let filteredRules = [...mockAlertRules];

      if (sensorId) {
        filteredRules = filteredRules.filter((r) => r.sensorId === sensorId);
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(filteredRules),
      });
    } else {
      await route.continue();
    }
  });

  // Mock alert rule by ID endpoints
  await page.route('**/api/v1/iot/alert-rules/*', async (route) => {
    const url = route.request().url();
    const parts = url.split('/');
    const ruleId = parts[parts.indexOf('alert-rules') + 1];
    const rule = mockAlertRules.find((r) => r.id === ruleId);

    if (route.request().method() === 'GET' && rule) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(rule),
      });
    } else if (route.request().method() === 'PATCH' && url.includes('toggle')) {
      // Mock toggle action
      if (rule) {
        const body = JSON.parse(route.request().postData() || '{}');
        const updatedRule = {
          ...rule,
          enabled: body.enabled,
          updatedAt: new Date().toISOString(),
        };

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(updatedRule),
        });
      } else {
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Alert rule not found' }),
        });
      }
    } else if (route.request().method() === 'DELETE') {
      // Mock delete action
      await route.fulfill({
        status: 204,
        contentType: 'application/json',
      });
    } else {
      await route.continue();
    }
  });

  console.log('IoT API mocks setup complete');
}

/**
 * Clear all mock API routes
 * مسح جميع مسارات API الوهمية
 */
export async function clearIoTMocks(page: Page): Promise<void> {
  await page.unroute('**/api/v1/iot/**');
  console.log('IoT API mocks cleared');
}
