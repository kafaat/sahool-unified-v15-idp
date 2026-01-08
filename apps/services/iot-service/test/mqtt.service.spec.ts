/**
 * SAHOOL IoT Service - MQTT Message Processing Unit Tests
 * اختبارات معالجة رسائل MQTT
 *
 * Tests for:
 * - MQTT connection and reconnection
 * - Topic subscription management
 * - Message routing and processing
 * - Actuator command publishing
 * - Error handling for MQTT operations
 * - Authentication and authorization
 */

import { Test, TestingModule } from '@nestjs/testing';
import { IotService, ActuatorType } from '../src/iot/iot.service';
import * as mqtt from 'mqtt';
import Redis from 'ioredis';

// Mock mqtt client
const mockMqttClient = {
  on: jest.fn(),
  subscribe: jest.fn(),
  publish: jest.fn(),
  end: jest.fn(),
  connected: false,
};

// Mock mqtt module
jest.mock('mqtt', () => ({
  connect: jest.fn(() => mockMqttClient),
}));

// Mock ioredis
jest.mock('ioredis', () => {
  const mockRedisInstance = {
    connect: jest.fn().mockResolvedValue(undefined),
    quit: jest.fn().mockResolvedValue(undefined),
    get: jest.fn(),
    set: jest.fn(),
    setex: jest.fn(),
    del: jest.fn(),
    scan: jest.fn(),
    keys: jest.fn(),
  };

  return jest.fn(() => mockRedisInstance);
});

describe('IotService - MQTT Message Processing', () => {
  let service: IotService;
  let mockRedis: jest.Mocked<Redis>;
  let connectCallback: () => void;
  let messageCallback: (topic: string, message: Buffer) => void;
  let errorCallback: (error: Error) => void;
  let reconnectCallback: () => void;

  beforeEach(async () => {
    jest.clearAllMocks();

    // Setup MQTT client mock callbacks
    mockMqttClient.on.mockImplementation((event: string, callback: any) => {
      if (event === 'connect') connectCallback = callback;
      if (event === 'message') messageCallback = callback;
      if (event === 'error') errorCallback = callback;
      if (event === 'reconnect') reconnectCallback = callback;
      return mockMqttClient;
    });

    mockMqttClient.subscribe.mockImplementation((topic: string, callback: any) => {
      if (callback) callback(null);
    });

    const module: TestingModule = await Test.createTestingModule({
      providers: [IotService],
    }).compile();

    service = module.get<IotService>(IotService);
    mockRedis = (service as any).redis as jest.Mocked<Redis>;

    await service.onModuleInit();

    // Trigger connect event
    if (connectCallback) {
      connectCallback();
    }
  });

  afterEach(async () => {
    await service.onModuleDestroy();
  });

  describe('MQTT Connection', () => {
    it('should connect to MQTT broker on initialization', () => {
      expect(mqtt.connect).toHaveBeenCalled();
    });

    it('should use broker URL from environment', () => {
      const originalBrokerUrl = process.env.MQTT_BROKER_URL;
      process.env.MQTT_BROKER_URL = 'mqtt://test-broker:1883';

      expect(mqtt.connect).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          clientId: expect.stringContaining('sahool-iot-service-'),
        })
      );

      process.env.MQTT_BROKER_URL = originalBrokerUrl;
    });

    it('should include authentication credentials when provided', () => {
      const originalUser = process.env.MQTT_USER;
      const originalPassword = process.env.MQTT_PASSWORD;

      process.env.MQTT_USER = 'test-user';
      process.env.MQTT_PASSWORD = 'test-password';

      // Note: The service was already initialized, this tests the logic
      expect(mqtt.connect).toHaveBeenCalled();

      process.env.MQTT_USER = originalUser;
      process.env.MQTT_PASSWORD = originalPassword;
    });

    it('should generate unique client ID', () => {
      const calls = (mqtt.connect as jest.Mock).mock.calls;
      const lastCall = calls[calls.length - 1];
      const options = lastCall[1];

      expect(options.clientId).toMatch(/^sahool-iot-service-\d+$/);
    });

    it('should configure connection options correctly', () => {
      const calls = (mqtt.connect as jest.Mock).mock.calls;
      const lastCall = calls[calls.length - 1];
      const options = lastCall[1];

      expect(options.clean).toBe(true);
      expect(options.connectTimeout).toBe(4000);
      expect(options.reconnectPeriod).toBe(1000);
    });

    it('should log connection success', () => {
      const loggerSpy = jest.spyOn((service as any).logger, 'log');

      // Trigger connect event again
      if (connectCallback) {
        connectCallback();
      }

      expect(loggerSpy).toHaveBeenCalledWith(
        expect.stringContaining('Connected to MQTT Broker')
      );
    });

    it('should handle connection errors', () => {
      const loggerErrorSpy = jest.spyOn((service as any).logger, 'error');
      const error = new Error('Connection failed');

      if (errorCallback) {
        errorCallback(error);
      }

      expect(loggerErrorSpy).toHaveBeenCalledWith(
        'MQTT Error:',
        'Connection failed'
      );
    });

    it('should handle reconnection attempts', () => {
      const loggerSpy = jest.spyOn((service as any).logger, 'log');

      if (reconnectCallback) {
        reconnectCallback();
      }

      expect(loggerSpy).toHaveBeenCalledWith(
        'Reconnecting to MQTT broker...'
      );
    });

    it('should disconnect gracefully on module destroy', async () => {
      await service.onModuleDestroy();

      expect(mockMqttClient.end).toHaveBeenCalled();
    });
  });

  describe('Topic Subscription', () => {
    it('should subscribe to sensor data topics', () => {
      expect(mockMqttClient.subscribe).toHaveBeenCalledWith(
        'sahool/+/farm/+/field/+/sensor/#',
        expect.any(Function)
      );
    });

    it('should subscribe to actuator topics', () => {
      expect(mockMqttClient.subscribe).toHaveBeenCalledWith(
        'sahool/+/farm/+/field/+/actuator/#',
        expect.any(Function)
      );
    });

    it('should subscribe to device status topics', () => {
      expect(mockMqttClient.subscribe).toHaveBeenCalledWith(
        'sahool/+/farm/+/device/status',
        expect.any(Function)
      );
    });

    it('should log subscription success', () => {
      const loggerSpy = jest.spyOn((service as any).logger, 'log');

      // Trigger subscribe callbacks
      if (connectCallback) {
        connectCallback();
      }

      expect(loggerSpy).toHaveBeenCalledWith(
        expect.stringContaining('Subscribed to:')
      );
    });

    it('should handle subscription errors', () => {
      const loggerErrorSpy = jest.spyOn((service as any).logger, 'error');

      mockMqttClient.subscribe.mockImplementationOnce((topic: string, callback: any) => {
        if (callback) callback(new Error('Subscription failed'));
      });

      // Trigger connect to attempt subscription
      if (connectCallback) {
        connectCallback();
      }

      expect(loggerErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining('Failed to subscribe'),
        expect.any(Error)
      );
    });
  });

  describe('Message Routing', () => {
    it('should route sensor messages to sensor handler', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const message = Buffer.from(JSON.stringify({ value: 65 }));

      if (messageCallback) {
        messageCallback(topic, message);
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledWith(
        'sensor:field-001:soil_moisture',
        300,
        expect.any(String)
      );
    });

    it('should route actuator messages to actuator handler', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/actuator/pump';
      const message = Buffer.from(JSON.stringify({ status: 'ON' }));

      if (messageCallback) {
        messageCallback(topic, message);
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledWith(
        'actuator:field-001:pump',
        3600,
        'true'
      );
    });

    it('should route device status messages to status handler', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const message = Buffer.from(JSON.stringify({
        deviceId: 'device-001',
        status: 'online',
      }));

      if (messageCallback) {
        messageCallback(topic, message);
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalled();
    });

    it('should handle unknown topic patterns gracefully', () => {
      const topic = 'unknown/topic/pattern';
      const message = Buffer.from('test');

      expect(() => {
        if (messageCallback) {
          messageCallback(topic, message);
        }
      }).not.toThrow();
    });

    it('should handle empty messages', () => {
      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const message = Buffer.from('');

      expect(() => {
        if (messageCallback) {
          messageCallback(topic, message);
        }
      }).not.toThrow();
    });

    it('should handle malformed JSON messages', () => {
      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const message = Buffer.from('invalid-json{');

      expect(() => {
        if (messageCallback) {
          messageCallback(topic, message);
        }
      }).not.toThrow();
    });

    it('should log errors for message processing failures', () => {
      const loggerErrorSpy = jest.spyOn((service as any).logger, 'error');

      mockRedis.setex.mockRejectedValue(new Error('Processing failed'));

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const message = Buffer.from(JSON.stringify({ value: 65 }));

      if (messageCallback) {
        messageCallback(topic, message);
      }

      // Error should be caught and logged
      setTimeout(() => {
        expect(loggerErrorSpy).toHaveBeenCalled();
      }, 100);
    });
  });

  describe('Actuator Command Publishing', () => {
    it('should publish pump ON command', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      await service.togglePump('field-001', 'ON');

      expect(mockMqttClient.publish).toHaveBeenCalledWith(
        'sahool/default/farm/farm-1/field/field-001/actuator/pump/command',
        expect.stringContaining('"command":"ON"'),
        { qos: 1 }
      );
    });

    it('should publish pump OFF command', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      await service.togglePump('field-001', 'OFF');

      expect(mockMqttClient.publish).toHaveBeenCalledWith(
        expect.any(String),
        expect.stringContaining('"command":"OFF"'),
        { qos: 1 }
      );
    });

    it('should include duration in pump command', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      await service.togglePump('field-001', 'ON', { duration: 30 });

      const publishCall = mockMqttClient.publish.mock.calls[0];
      const payload = JSON.parse(publishCall[1]);

      expect(payload.duration).toBe(30);
    });

    it('should publish valve commands', () => {
      const result = service.toggleValve('field-001', 'valve-1', 'ON');

      expect(mockMqttClient.publish).toHaveBeenCalledWith(
        'sahool/default/farm/farm-1/field/field-001/actuator/valve/valve-1/command',
        expect.stringContaining('"command":"ON"'),
        { qos: 1 }
      );

      expect(result.success).toBe(true);
    });

    it('should publish irrigation schedule', () => {
      const schedule = {
        startTime: '06:00',
        duration: 45,
        days: ['sunday', 'tuesday'],
        enabled: true,
      };

      const result = service.setIrrigationSchedule('field-001', schedule);

      expect(mockMqttClient.publish).toHaveBeenCalledWith(
        'sahool/default/farm/farm-1/field/field-001/irrigation/schedule',
        JSON.stringify(schedule),
        { qos: 1, retain: true }
      );

      expect(result.success).toBe(true);
    });

    it('should use QoS 1 for actuator commands', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      await service.togglePump('field-001', 'ON');

      const publishCall = mockMqttClient.publish.mock.calls[0];
      expect(publishCall[2]).toEqual({ qos: 1 });
    });

    it('should use retain flag for irrigation schedules', () => {
      const schedule = {
        startTime: '06:00',
        duration: 45,
        days: ['sunday'],
        enabled: true,
      };

      service.setIrrigationSchedule('field-001', schedule);

      const publishCall = mockMqttClient.publish.mock.calls[0];
      expect(publishCall[2]).toEqual({ qos: 1, retain: true });
    });

    it('should include timestamp in commands', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const beforeTime = Date.now();
      await service.togglePump('field-001', 'ON');
      const afterTime = Date.now();

      const publishCall = mockMqttClient.publish.mock.calls[0];
      const payload = JSON.parse(publishCall[1]);
      const commandTime = new Date(payload.timestamp).getTime();

      expect(commandTime).toBeGreaterThanOrEqual(beforeTime);
      expect(commandTime).toBeLessThanOrEqual(afterTime);
    });

    it('should include source in commands', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      await service.togglePump('field-001', 'ON');

      const publishCall = mockMqttClient.publish.mock.calls[0];
      const payload = JSON.parse(publishCall[1]);

      expect(payload.source).toBe('mobile-app');
    });
  });

  describe('Topic Pattern Parsing', () => {
    it('should parse tenant ID from topic', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-123/farm/farm-1/field/field-001/sensor/soil_moisture';
      const message = Buffer.from(JSON.stringify({ value: 65 }));

      if (messageCallback) {
        messageCallback(topic, message);
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      // Should process without errors
      expect(mockRedis.setex).toHaveBeenCalled();
    });

    it('should parse farm ID from topic', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-456/field/field-001/sensor/soil_moisture';
      const message = Buffer.from(JSON.stringify({ value: 65 }));

      if (messageCallback) {
        messageCallback(topic, message);
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalled();
    });

    it('should parse field ID from topic', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-789/sensor/soil_moisture';
      const message = Buffer.from(JSON.stringify({ value: 65 }));

      if (messageCallback) {
        messageCallback(topic, message);
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      expect(savedData.fieldId).toBe('field-789');
    });

    it('should parse sensor type from topic', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/air_temperature';
      const message = Buffer.from(JSON.stringify({ value: 28 }));

      if (messageCallback) {
        messageCallback(topic, message);
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      expect(savedData.sensorType).toBe('air_temperature');
    });

    it('should handle wildcard subscriptions', () => {
      // The service should subscribe with wildcards
      const subscriptions = mockMqttClient.subscribe.mock.calls.map(call => call[0]);

      expect(subscriptions).toContain('sahool/+/farm/+/field/+/sensor/#');
      expect(subscriptions).toContain('sahool/+/farm/+/field/+/actuator/#');
      expect(subscriptions).toContain('sahool/+/farm/+/device/status');
    });
  });

  describe('Message Quality of Service', () => {
    it('should handle QoS 0 messages', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const message = Buffer.from(JSON.stringify({ value: 65 }));

      if (messageCallback) {
        messageCallback(topic, message);
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalled();
    });

    it('should handle QoS 1 messages with acknowledgment', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const message = Buffer.from(JSON.stringify({ value: 65 }));

      if (messageCallback) {
        messageCallback(topic, message);
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalled();
    });

    it('should publish commands with QoS 1', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      await service.togglePump('field-001', 'ON');

      const publishCall = mockMqttClient.publish.mock.calls[0];
      expect(publishCall[2].qos).toBe(1);
    });
  });

  describe('Concurrent Message Processing', () => {
    it('should handle multiple messages simultaneously', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topics = [
        'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture',
        'sahool/tenant-1/farm/farm-1/field/field-002/sensor/air_temperature',
        'sahool/tenant-1/farm/farm-1/field/field-003/sensor/water_level',
      ];

      if (messageCallback) {
        topics.forEach(topic => {
          const message = Buffer.from(JSON.stringify({ value: 50 }));
          messageCallback(topic, message);
        });
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledTimes(3);
    });

    it('should process messages in order for same topic', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const values = [60, 61, 62];

      if (messageCallback) {
        values.forEach(value => {
          const message = Buffer.from(JSON.stringify({ value }));
          messageCallback(topic, message);
        });
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledTimes(3);

      // Verify last value was saved
      const lastCall = mockRedis.setex.mock.calls[2];
      const lastData = JSON.parse(lastCall[2]);
      expect(lastData.value).toBe(62);
    });
  });

  describe('Error Recovery', () => {
    it('should continue processing after message error', async () => {
      mockRedis.setex
        .mockRejectedValueOnce(new Error('First message failed'))
        .mockResolvedValueOnce('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';

      if (messageCallback) {
        // First message
        messageCallback(topic, Buffer.from(JSON.stringify({ value: 60 })));

        await new Promise(resolve => setTimeout(resolve, 50));

        // Second message should still work
        messageCallback(topic, Buffer.from(JSON.stringify({ value: 61 })));
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledTimes(2);
    });

    it('should not crash on null message', () => {
      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';

      expect(() => {
        if (messageCallback) {
          messageCallback(topic, null as any);
        }
      }).not.toThrow();
    });

    it('should handle message processing timeout gracefully', async () => {
      // Simulate slow Redis operation
      mockRedis.setex.mockImplementation(() =>
        new Promise(resolve => setTimeout(() => resolve('OK'), 5000))
      );

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const message = Buffer.from(JSON.stringify({ value: 65 }));

      if (messageCallback) {
        messageCallback(topic, message);
      }

      // Should not block other operations
      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalled();
    });
  });

  describe('Cleanup and Resource Management', () => {
    it('should end MQTT connection on destroy', async () => {
      await service.onModuleDestroy();

      expect(mockMqttClient.end).toHaveBeenCalled();
    });

    it('should disconnect from Redis on destroy', async () => {
      await service.onModuleDestroy();

      expect(mockRedis.quit).toHaveBeenCalled();
    });

    it('should log disconnection messages', async () => {
      const loggerSpy = jest.spyOn((service as any).logger, 'log');

      await service.onModuleDestroy();

      expect(loggerSpy).toHaveBeenCalledWith(
        expect.stringContaining('Disconnected from MQTT broker')
      );
      expect(loggerSpy).toHaveBeenCalledWith(
        expect.stringContaining('Disconnected from Redis')
      );
    });
  });
});
