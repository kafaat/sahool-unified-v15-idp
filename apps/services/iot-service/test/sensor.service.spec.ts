/**
 * SAHOOL IoT Service - Sensor Data Management Unit Tests
 * اختبارات إدارة بيانات الحساسات
 *
 * Tests for:
 * - Sensor data ingestion and processing
 * - Sensor data validation
 * - Real-time data streams
 * - Sensor reading quality assessment
 * - Sensor alert thresholds
 * - Data caching and retrieval
 */

import { Test, TestingModule } from '@nestjs/testing';
import { IotService, SensorType, SensorReading } from '../src/iot/iot.service';
import Redis from 'ioredis';

// Mock mqtt
jest.mock('mqtt', () => ({
  connect: jest.fn().mockReturnValue({
    on: jest.fn((event, callback) => {
      if (event === 'connect') {
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

describe('IotService - Sensor Data Management', () => {
  let service: IotService;
  let mockRedis: jest.Mocked<Redis>;

  beforeEach(async () => {
    jest.clearAllMocks();

    const module: TestingModule = await Test.createTestingModule({
      providers: [IotService],
    }).compile();

    service = module.get<IotService>(IotService);
    mockRedis = (service as any).redis as jest.Mocked<Redis>;

    await service.onModuleInit();
  });

  afterEach(async () => {
    await service.onModuleDestroy();
  });

  describe('Sensor Data Ingestion', () => {
    it('should process soil moisture sensor data', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const payload = JSON.stringify({
        deviceId: 'sensor-001',
        value: 65,
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledWith(
        'sensor:field-001:soil_moisture',
        300, // SENSOR_READING_TTL
        expect.stringContaining('"value":65')
      );
    });

    it('should process temperature sensor data', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-002/sensor/air_temperature';
      const payload = JSON.stringify({
        deviceId: 'temp-sensor-001',
        value: 28.5,
      });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledWith(
        'sensor:field-002:air_temperature',
        300,
        expect.stringContaining('"value":28.5')
      );
    });

    it('should process raw numeric sensor data', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const payload = '55'; // Raw number without JSON

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalled();
      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      expect(savedData.value).toBe(55);
    });

    it('should handle multiple sensor readings in sequence', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const readings = [
        { type: 'soil_moisture', value: 45 },
        { type: 'soil_temperature', value: 22 },
        { type: 'air_humidity', value: 68 },
      ];

      for (const reading of readings) {
        const topic = `sahool/tenant-1/farm/farm-1/field/field-001/sensor/${reading.type}`;
        const payload = JSON.stringify({ value: reading.value });
        (service as any).handleMessage(topic, payload);
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledTimes(3);
    });

    it('should generate deviceId when not provided', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/water_level';
      const payload = JSON.stringify({ value: 150 });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      expect(savedData.deviceId).toMatch(/sensor-field-001-water_level/);
    });
  });

  describe('Sensor Data Validation', () => {
    it('should validate soil moisture within acceptable range', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const payload = JSON.stringify({ value: 75 });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      expect(savedData.quality).toBe('good');
    });

    it('should flag invalid soil moisture reading as error', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const payload = JSON.stringify({ value: 150 }); // Invalid: over 100%

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      expect(savedData.quality).toBe('error');
    });

    it('should validate temperature within acceptable range', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/air_temperature';
      const payload = JSON.stringify({ value: 25 });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      expect(savedData.quality).toBe('good');
    });

    it('should flag extremely high temperature as error', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/air_temperature';
      const payload = JSON.stringify({ value: 70 }); // Too high

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      expect(savedData.quality).toBe('error');
    });

    it('should validate pH level within acceptable range', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/ph_level';
      const payload = JSON.stringify({ value: 6.5 });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      expect(savedData.quality).toBe('good');
    });

    it('should flag negative values as error for sensors', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/water_flow';
      const payload = JSON.stringify({ value: -5 }); // Invalid negative

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      expect(savedData.quality).toBe('error');
    });

    it('should assign correct units to sensor readings', async () => {
      const testCases = [
        { type: SensorType.SOIL_MOISTURE, unit: '%' },
        { type: SensorType.AIR_TEMPERATURE, unit: '°C' },
        { type: SensorType.WATER_FLOW, unit: 'L/min' },
        { type: SensorType.PH_LEVEL, unit: 'pH' },
        { type: SensorType.LIGHT_INTENSITY, unit: 'lux' },
      ];

      mockRedis.setex.mockResolvedValue('OK');

      for (const testCase of testCases) {
        const topic = `sahool/tenant-1/farm/farm-1/field/field-001/sensor/${testCase.type}`;
        const payload = JSON.stringify({ value: 50 });

        (service as any).handleMessage(topic, payload);
      }

      await new Promise(resolve => setTimeout(resolve, 100));

      testCases.forEach((testCase, index) => {
        const savedData = JSON.parse(mockRedis.setex.mock.calls[index][2]);
        expect(savedData.unit).toBe(testCase.unit);
      });
    });
  });

  describe('Sensor Alert Thresholds', () => {
    it('should trigger alert for low soil moisture', async () => {
      const loggerWarnSpy = jest.spyOn((service as any).logger, 'warn');
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const payload = JSON.stringify({ value: 25 }); // Below 30% threshold

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(loggerWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining('Low soil_moisture alert')
      );
    });

    it('should trigger alert for high soil moisture', async () => {
      const loggerWarnSpy = jest.spyOn((service as any).logger, 'warn');
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const payload = JSON.stringify({ value: 90 }); // Above 85% threshold

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(loggerWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining('High soil_moisture alert')
      );
    });

    it('should trigger alert for high air temperature', async () => {
      const loggerWarnSpy = jest.spyOn((service as any).logger, 'warn');
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/air_temperature';
      const payload = JSON.stringify({ value: 45 }); // Above 40°C threshold

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(loggerWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining('High air_temperature alert')
      );
    });

    it('should trigger alert for low water level', async () => {
      const loggerWarnSpy = jest.spyOn((service as any).logger, 'warn');
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/water_level';
      const payload = JSON.stringify({ value: 5 }); // Below 10cm threshold

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(loggerWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining('Low water_level alert')
      );
    });

    it('should not trigger alert for normal readings', async () => {
      const loggerWarnSpy = jest.spyOn((service as any).logger, 'warn');
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const payload = JSON.stringify({ value: 55 }); // Normal range

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(loggerWarnSpy).not.toHaveBeenCalledWith(
        expect.stringContaining('alert')
      );
    });
  });

  describe('Sensor Data Retrieval', () => {
    it('should retrieve specific sensor reading', async () => {
      const reading: SensorReading = {
        deviceId: 'sensor-001',
        fieldId: 'field-001',
        sensorType: SensorType.SOIL_MOISTURE,
        value: 65,
        unit: '%',
        timestamp: new Date(),
        quality: 'good',
      };

      mockRedis.get.mockResolvedValue(JSON.stringify(reading));

      const result = await service.getSensorReading('field-001', SensorType.SOIL_MOISTURE);

      expect(result).not.toBeNull();
      expect(result?.value).toBe(65);
      expect(result?.sensorType).toBe(SensorType.SOIL_MOISTURE);
    });

    it('should return null for non-existent sensor', async () => {
      mockRedis.get.mockResolvedValue(null);

      const result = await service.getSensorReading('field-999', SensorType.SOIL_MOISTURE);

      expect(result).toBeNull();
    });

    it('should retrieve all sensor readings for a field', async () => {
      const readings: SensorReading[] = [
        {
          deviceId: 'sensor-001',
          fieldId: 'field-001',
          sensorType: SensorType.SOIL_MOISTURE,
          value: 65,
          unit: '%',
          timestamp: new Date(),
          quality: 'good',
        },
        {
          deviceId: 'sensor-002',
          fieldId: 'field-001',
          sensorType: SensorType.AIR_TEMPERATURE,
          value: 28,
          unit: '°C',
          timestamp: new Date(),
          quality: 'good',
        },
      ];

      mockRedis.scan.mockResolvedValue([
        '0',
        ['sensor:field-001:soil_moisture', 'sensor:field-001:air_temperature'],
      ]);

      mockRedis.get
        .mockResolvedValueOnce(JSON.stringify(readings[0]))
        .mockResolvedValueOnce(JSON.stringify(readings[1]));

      const result = await service.getFieldSensorData('field-001');

      expect(result).toHaveLength(2);
      expect(result[0].sensorType).toBe(SensorType.SOIL_MOISTURE);
      expect(result[1].sensorType).toBe(SensorType.AIR_TEMPERATURE);
    });

    it('should return empty array for field with no sensors', async () => {
      mockRedis.scan.mockResolvedValue(['0', []]);

      const result = await service.getFieldSensorData('field-empty');

      expect(result).toEqual([]);
    });

    it('should handle pagination when scanning sensor keys', async () => {
      mockRedis.scan
        .mockResolvedValueOnce(['1', ['sensor:field-001:soil_moisture']])
        .mockResolvedValueOnce(['0', ['sensor:field-001:air_temperature']]);

      mockRedis.get
        .mockResolvedValueOnce(JSON.stringify({
          deviceId: 'sensor-001',
          fieldId: 'field-001',
          sensorType: SensorType.SOIL_MOISTURE,
          value: 65,
          unit: '%',
          timestamp: new Date(),
          quality: 'good',
        }))
        .mockResolvedValueOnce(JSON.stringify({
          deviceId: 'sensor-002',
          fieldId: 'field-001',
          sensorType: SensorType.AIR_TEMPERATURE,
          value: 28,
          unit: '°C',
          timestamp: new Date(),
          quality: 'good',
        }));

      const result = await service.getFieldSensorData('field-001');

      expect(result).toHaveLength(2);
    });
  });

  describe('Real-time Data Streams', () => {
    it('should cache sensor reading with TTL', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const payload = JSON.stringify({ value: 60 });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledWith(
        'sensor:field-001:soil_moisture',
        300, // 5 minutes TTL
        expect.any(String)
      );
    });

    it('should update existing sensor reading in real-time', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';

      // First reading
      (service as any).handleMessage(topic, JSON.stringify({ value: 60 }));
      await new Promise(resolve => setTimeout(resolve, 50));

      // Updated reading
      (service as any).handleMessage(topic, JSON.stringify({ value: 55 }));
      await new Promise(resolve => setTimeout(resolve, 50));

      expect(mockRedis.setex).toHaveBeenCalledTimes(2);

      const lastCall = mockRedis.setex.mock.calls[1];
      const lastReading = JSON.parse(lastCall[2]);
      expect(lastReading.value).toBe(55);
    });

    it('should handle rapid successive sensor readings', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const values = [60, 59, 58, 57, 56];

      values.forEach(value => {
        (service as any).handleMessage(topic, JSON.stringify({ value }));
      });

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledTimes(5);
    });

    it('should maintain timestamp accuracy for real-time data', async () => {
      mockRedis.setex.mockResolvedValue('OK');
      const beforeTime = Date.now();

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const payload = JSON.stringify({ value: 65 });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      const afterTime = Date.now();
      const savedData = JSON.parse(mockRedis.setex.mock.calls[0][2]);
      const timestamp = new Date(savedData.timestamp).getTime();

      expect(timestamp).toBeGreaterThanOrEqual(beforeTime);
      expect(timestamp).toBeLessThanOrEqual(afterTime);
    });

    it('should handle concurrent sensor readings from different fields', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const fields = ['field-001', 'field-002', 'field-003'];

      fields.forEach(fieldId => {
        const topic = `sahool/tenant-1/farm/farm-1/field/${fieldId}/sensor/soil_moisture`;
        (service as any).handleMessage(topic, JSON.stringify({ value: 65 }));
      });

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledTimes(3);

      // Verify different keys for different fields
      const keys = mockRedis.setex.mock.calls.map(call => call[0]);
      expect(keys).toContain('sensor:field-001:soil_moisture');
      expect(keys).toContain('sensor:field-002:soil_moisture');
      expect(keys).toContain('sensor:field-003:soil_moisture');
    });
  });

  describe('All Sensor Types', () => {
    const sensorTests = [
      { type: SensorType.SOIL_MOISTURE, value: 65, unit: '%' },
      { type: SensorType.SOIL_TEMPERATURE, value: 22, unit: '°C' },
      { type: SensorType.AIR_TEMPERATURE, value: 28, unit: '°C' },
      { type: SensorType.AIR_HUMIDITY, value: 70, unit: '%' },
      { type: SensorType.LIGHT_INTENSITY, value: 50000, unit: 'lux' },
      { type: SensorType.WATER_LEVEL, value: 150, unit: 'cm' },
      { type: SensorType.WATER_FLOW, value: 25, unit: 'L/min' },
      { type: SensorType.PH_LEVEL, value: 6.8, unit: 'pH' },
      { type: SensorType.EC_LEVEL, value: 2.5, unit: 'mS/cm' },
      { type: SensorType.WIND_SPEED, value: 15, unit: 'km/h' },
      { type: SensorType.RAIN_GAUGE, value: 5, unit: 'mm' },
    ];

    sensorTests.forEach(({ type, value, unit }) => {
      it(`should process ${type} sensor data correctly`, async () => {
        mockRedis.setex.mockResolvedValue('OK');

        const topic = `sahool/tenant-1/farm/farm-1/field/field-001/sensor/${type}`;
        const payload = JSON.stringify({ value });

        (service as any).handleMessage(topic, payload);

        await new Promise(resolve => setTimeout(resolve, 100));

        const savedData = JSON.parse(mockRedis.setex.mock.calls[mockRedis.setex.mock.calls.length - 1][2]);
        expect(savedData.value).toBe(value);
        expect(savedData.unit).toBe(unit);
        expect(savedData.sensorType).toBe(type);
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle malformed sensor data gracefully', async () => {
      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const payload = 'invalid-json{';

      expect(() => {
        (service as any).handleMessage(topic, payload);
      }).not.toThrow();
    });

    it('should handle missing value in sensor data', async () => {
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const payload = JSON.stringify({ deviceId: 'sensor-001' }); // Missing value

      expect(() => {
        (service as any).handleMessage(topic, payload);
      }).not.toThrow();
    });

    it('should handle Redis errors when caching sensor data', async () => {
      const loggerErrorSpy = jest.spyOn((service as any).logger, 'error');
      mockRedis.setex.mockRejectedValue(new Error('Redis write failed'));

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const payload = JSON.stringify({ value: 65 });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(loggerErrorSpy).toHaveBeenCalled();
    });

    it('should handle Redis errors when retrieving sensor data', async () => {
      mockRedis.get.mockRejectedValue(new Error('Redis read failed'));

      const result = await service.getSensorReading('field-001', SensorType.SOIL_MOISTURE);

      expect(result).toBeNull();
    });

    it('should handle corrupted sensor data in Redis', async () => {
      mockRedis.get.mockResolvedValue('invalid-json{');

      await expect(
        service.getSensorReading('field-001', SensorType.SOIL_MOISTURE)
      ).rejects.toThrow();
    });

    it('should handle Redis scan errors gracefully', async () => {
      mockRedis.scan.mockRejectedValue(new Error('Redis scan failed'));

      const result = await service.getFieldSensorData('field-001');

      expect(result).toEqual([]);
    });

    it('should skip null sensor readings when scanning', async () => {
      mockRedis.scan.mockResolvedValue([
        '0',
        ['sensor:field-001:soil_moisture', 'sensor:field-001:air_temperature'],
      ]);

      mockRedis.get
        .mockResolvedValueOnce(JSON.stringify({
          deviceId: 'sensor-001',
          fieldId: 'field-001',
          sensorType: SensorType.SOIL_MOISTURE,
          value: 65,
          unit: '%',
          timestamp: new Date(),
          quality: 'good',
        }))
        .mockResolvedValueOnce(null); // Null reading

      const result = await service.getFieldSensorData('field-001');

      expect(result).toHaveLength(1);
    });
  });

  describe('Data Logging', () => {
    it('should log sensor data with debug level', async () => {
      const loggerDebugSpy = jest.spyOn((service as any).logger, 'debug');
      mockRedis.setex.mockResolvedValue('OK');

      const topic = 'sahool/tenant-1/farm/farm-1/field/field-001/sensor/soil_moisture';
      const payload = JSON.stringify({ value: 65 });

      (service as any).handleMessage(topic, payload);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(loggerDebugSpy).toHaveBeenCalledWith(
        expect.stringContaining('Sensor soil_moisture')
      );
    });
  });
});
