/**
 * SAHOOL IoT Service - Device Management Unit Tests
 * اختبارات إدارة الأجهزة
 *
 * Tests for:
 * - Device registration
 * - Device authentication
 * - Device status tracking
 * - Device connection management
 * - Offline device handling
 */

import { Test, TestingModule } from '@nestjs/testing';
import { IotService, DeviceStatus, SensorType } from '../src/iot/iot.service';
import Redis from 'ioredis';

// Mock mqtt
jest.mock('mqtt', () => ({
  connect: jest.fn().mockReturnValue({
    on: jest.fn((event, callback) => {
      if (event === 'connect') {
        // Simulate immediate connection
        setTimeout(() => callback(), 0);
      }
      return this;
    }),
    subscribe: jest.fn((topic, callback) => {
      if (callback) callback(null);
    }),
    publish: jest.fn(),
    end: jest.fn(),
  }),
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

describe('IotService - Device Management', () => {
  let service: IotService;
  let mockRedis: jest.Mocked<Redis>;

  beforeEach(async () => {
    jest.clearAllMocks();

    const module: TestingModule = await Test.createTestingModule({
      providers: [IotService],
    }).compile();

    service = module.get<IotService>(IotService);
    mockRedis = (service as any).redis as jest.Mocked<Redis>;

    // Initialize the service
    await service.onModuleInit();
  });

  afterEach(async () => {
    await service.onModuleDestroy();
  });

  describe('Device Registration', () => {
    it('should register a new device when receiving status message', async () => {
      const deviceStatus: DeviceStatus = {
        deviceId: 'sensor-001',
        fieldId: 'field-001',
        type: 'sensor',
        name: 'Soil Moisture Sensor',
        status: 'online',
        lastSeen: new Date(),
        batteryLevel: 85,
      };

      mockRedis.setex.mockResolvedValue('OK');

      // Simulate device status message
      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        deviceId: 'sensor-001',
        type: 'sensor',
        name: 'Soil Moisture Sensor',
        status: 'online',
        battery: 85,
      });

      // Access private method through class instance
      (service as any).handleMessage(topic, payload);

      // Wait for async operations
      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledWith(
        'device:sensor-001',
        600, // DEVICE_STATUS_TTL
        expect.stringContaining('sensor-001')
      );
    });

    it('should update existing device status', async () => {
      const existingDevice: DeviceStatus = {
        deviceId: 'sensor-002',
        fieldId: 'field-001',
        type: 'sensor',
        name: 'Temperature Sensor',
        status: 'online',
        lastSeen: new Date(Date.now() - 60000),
        batteryLevel: 60,
      };

      mockRedis.get.mockResolvedValue(JSON.stringify(existingDevice));
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        deviceId: 'sensor-002',
        type: 'sensor',
        name: 'Temperature Sensor',
        status: 'online',
        battery: 55, // Battery decreased
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalled();
    });

    it('should handle device registration with minimal data', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        deviceId: 'minimal-device',
        status: 'online',
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledWith(
        'device:minimal-device',
        600,
        expect.any(String)
      );
    });
  });

  describe('Device Authentication', () => {
    it('should accept device with valid topic structure', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-123/farm/farm-456/field/field-789/sensor/soil_moisture';
      const payload = JSON.stringify({
        deviceId: 'auth-device-001',
        value: 45,
      });

      expect(() => {
        (service as any).handleMessage(topic, payload);
      }).not.toThrow();
    });

    it('should handle device message from valid tenant', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/valid-tenant/farm/farm-1/field/field-1/device/status';
      const payload = JSON.stringify({
        deviceId: 'tenant-device',
        status: 'online',
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalled();
    });

    it('should process messages with proper authentication context', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const authenticatedPayload = {
        deviceId: 'secure-device-001',
        status: 'online',
        tenantId: 'tenant-001',
        farmId: 'farm-001',
      };

      const topic = 'sahool/tenant-001/farm/farm-001/field/field-001/device/status';
      (service as any).handleMessage(topic, JSON.stringify(authenticatedPayload));

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalled();
    });
  });

  describe('Device Status Tracking', () => {
    it('should retrieve all connected devices', async () => {
      const devices: DeviceStatus[] = [
        {
          deviceId: 'device-001',
          fieldId: 'field-001',
          type: 'sensor',
          name: 'Sensor 1',
          status: 'online',
          lastSeen: new Date(),
          batteryLevel: 90,
        },
        {
          deviceId: 'device-002',
          fieldId: 'field-002',
          type: 'actuator',
          name: 'Pump 1',
          status: 'online',
          lastSeen: new Date(),
        },
      ];

      // Mock Redis SCAN operation
      mockRedis.scan
        .mockResolvedValueOnce(['0', ['device:device-001', 'device:device-002']])
        .mockResolvedValueOnce(['0', []]);

      mockRedis.get
        .mockResolvedValueOnce(JSON.stringify(devices[0]))
        .mockResolvedValueOnce(JSON.stringify(devices[1]));

      const result = await service.getConnectedDevices();

      expect(result).toHaveLength(2);
      expect(result[0].deviceId).toBe('device-001');
      expect(result[1].deviceId).toBe('device-002');
    });

    it('should calculate device statistics correctly', async () => {
      const devices: DeviceStatus[] = [
        {
          deviceId: 'device-001',
          fieldId: 'field-001',
          type: 'sensor',
          name: 'Online Device',
          status: 'online',
          lastSeen: new Date(),
        },
        {
          deviceId: 'device-002',
          fieldId: 'field-002',
          type: 'sensor',
          name: 'Offline Device',
          status: 'offline',
          lastSeen: new Date(Date.now() - 3600000),
        },
        {
          deviceId: 'device-003',
          fieldId: 'field-003',
          type: 'actuator',
          name: 'Error Device',
          status: 'error',
          lastSeen: new Date(),
        },
      ];

      mockRedis.scan.mockResolvedValue([
        '0',
        ['device:device-001', 'device:device-002', 'device:device-003'],
      ]);

      mockRedis.get
        .mockResolvedValueOnce(JSON.stringify(devices[0]))
        .mockResolvedValueOnce(JSON.stringify(devices[1]))
        .mockResolvedValueOnce(JSON.stringify(devices[2]));

      const stats = await service.getDeviceStats();

      expect(stats.online).toBe(1);
      expect(stats.offline).toBe(1);
      expect(stats.error).toBe(1);
    });

    it('should track device last seen timestamp', async () => {
      const now = new Date();
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        deviceId: 'timestamp-device',
        status: 'online',
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = mockRedis.setex.mock.calls[0][2];
      const deviceData = JSON.parse(savedData);

      expect(new Date(deviceData.lastSeen).getTime()).toBeGreaterThanOrEqual(now.getTime());
    });

    it('should track device battery levels', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        deviceId: 'battery-device',
        status: 'online',
        battery: 45,
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = mockRedis.setex.mock.calls[0][2];
      const deviceData = JSON.parse(savedData);

      expect(deviceData.batteryLevel).toBe(45);
    });
  });

  describe('Offline Device Handling', () => {
    it('should detect and handle offline devices', async () => {
      const offlineDevice: DeviceStatus = {
        deviceId: 'offline-001',
        fieldId: 'field-001',
        type: 'sensor',
        name: 'Offline Sensor',
        status: 'offline',
        lastSeen: new Date(Date.now() - 7200000), // 2 hours ago
        batteryLevel: 15,
      };

      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      (service as any).handleMessage(topic, JSON.stringify({
        deviceId: 'offline-001',
        status: 'offline',
        battery: 15,
      }));

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalled();
    });

    it('should warn about low battery devices', async () => {
      const loggerWarnSpy = jest.spyOn((service as any).logger, 'warn');
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        deviceId: 'low-battery-device',
        name: 'Low Battery Sensor',
        status: 'online',
        battery: 15, // Below 20% threshold
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(loggerWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining('Low battery')
      );
    });

    it('should handle device error state', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        deviceId: 'error-device',
        status: 'error',
        errorCode: 'SENSOR_MALFUNCTION',
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalled();
    });

    it('should handle device reconnection', async () => {
      // First, device goes offline
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';

      // Device offline
      (service as any).handleMessage(topic, JSON.stringify({
        deviceId: 'reconnect-device',
        status: 'offline',
      }));

      await new Promise(resolve => setTimeout(resolve, 100));

      // Device comes back online
      (service as any).handleMessage(topic, JSON.stringify({
        deviceId: 'reconnect-device',
        status: 'online',
        battery: 80,
      }));

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledTimes(2);

      const lastCall = mockRedis.setex.mock.calls[1];
      const lastStatus = JSON.parse(lastCall[2]);
      expect(lastStatus.status).toBe('online');
    });

    it('should return empty array when no devices are online', async () => {
      mockRedis.scan.mockResolvedValue(['0', []]);

      const devices = await service.getConnectedDevices();

      expect(devices).toEqual([]);
    });

    it('should handle Redis errors gracefully when fetching devices', async () => {
      mockRedis.scan.mockRejectedValue(new Error('Redis connection failed'));

      const devices = await service.getConnectedDevices();

      expect(devices).toEqual([]);
    });

    it('should handle corrupted device data in Redis', async () => {
      mockRedis.scan.mockResolvedValue(['0', ['device:corrupted']]);
      mockRedis.get.mockResolvedValue('invalid-json{');

      const devices = await service.getConnectedDevices();

      // Should skip corrupted entries
      expect(devices).toEqual([]);
    });
  });

  describe('Device Connection Management', () => {
    it('should maintain device connection state in Redis', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        deviceId: 'connection-device',
        status: 'online',
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledWith(
        'device:connection-device',
        600, // TTL for device status
        expect.any(String)
      );
    });

    it('should handle multiple devices connecting simultaneously', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';

      // Simulate 3 devices connecting
      const devices = ['device-1', 'device-2', 'device-3'];

      devices.forEach(deviceId => {
        (service as any).handleMessage(topic, JSON.stringify({
          deviceId,
          status: 'online',
        }));
      });

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledTimes(3);
    });

    it('should expire device status after TTL', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      (service as any).handleMessage(topic, JSON.stringify({
        deviceId: 'ttl-device',
        status: 'online',
      }));

      await new Promise(resolve => setTimeout(resolve, 100));

      // Verify TTL is set correctly (600 seconds = 10 minutes)
      expect(mockRedis.setex).toHaveBeenCalledWith(
        'device:ttl-device',
        600,
        expect.any(String)
      );
    });
  });

  describe('Device Type Handling', () => {
    it('should handle sensor type devices', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        deviceId: 'sensor-device',
        type: 'sensor',
        status: 'online',
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      expect(savedData.type).toBe('sensor');
    });

    it('should handle actuator type devices', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        deviceId: 'actuator-device',
        type: 'actuator',
        status: 'online',
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      expect(savedData.type).toBe('actuator');
    });

    it('should default to sensor type if not specified', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        deviceId: 'default-type-device',
        status: 'online',
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      expect(savedData.type).toBe('sensor');
    });
  });

  describe('Error Handling', () => {
    it('should handle malformed device status messages', async () => {
      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = 'invalid-json{';

      expect(() => {
        (service as any).handleMessage(topic, payload);
      }).not.toThrow();
    });

    it('should handle missing deviceId in status message', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        status: 'online',
        // deviceId is missing
      });

      expect(() => {
        (service as any).handleMessage(topic, payload);
      }).not.toThrow();
    });

    it('should handle Redis write failures gracefully', async () => {
      mockRedis.setex.mockRejectedValue(new Error('Redis write failed'));

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        deviceId: 'fail-device',
        status: 'online',
      });

      expect(() => {
        (service as any).handleMessage(topic, payload);
      }).not.toThrow();

      await new Promise(resolve => setTimeout(resolve, 100));
    });

    it('should log errors when caching device status fails', async () => {
      const loggerErrorSpy = jest.spyOn((service as any).logger, 'error');
      mockRedis.setex.mockRejectedValue(new Error('Cache failed'));

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/device/status';
      const payload = JSON.stringify({
        deviceId: 'error-cache-device',
        status: 'online',
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(loggerErrorSpy).toHaveBeenCalled();
    });
  });
});
