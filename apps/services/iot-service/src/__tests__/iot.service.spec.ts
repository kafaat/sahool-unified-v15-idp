/**
 * اختبارات خدمة إنترنت الأشياء
 * IoT Service Tests
 *
 * Comprehensive tests for the SAHOOL IoT Service.
 */

import { Test, TestingModule } from '@nestjs/testing';
import { IotService, SensorType, ActuatorType, SensorReading, DeviceStatus } from '../iot/iot.service';

// ─────────────────────────────────────────────────────────────────────────────
// Mock Redis
// ─────────────────────────────────────────────────────────────────────────────

const mockRedis = {
  connect: jest.fn().mockResolvedValue(undefined),
  quit: jest.fn().mockResolvedValue(undefined),
  get: jest.fn(),
  setex: jest.fn().mockResolvedValue('OK'),
  scan: jest.fn(),
};

jest.mock('ioredis', () => {
  return jest.fn().mockImplementation(() => mockRedis);
});

// ─────────────────────────────────────────────────────────────────────────────
// Mock MQTT
// ─────────────────────────────────────────────────────────────────────────────

const mockMqttClient = {
  on: jest.fn(),
  subscribe: jest.fn(),
  publish: jest.fn(),
  end: jest.fn(),
};

jest.mock('mqtt', () => ({
  connect: jest.fn().mockReturnValue(mockMqttClient),
}));

// ─────────────────────────────────────────────────────────────────────────────
// Test Suite
// ─────────────────────────────────────────────────────────────────────────────

describe('IotService', () => {
  let service: IotService;
  let module: TestingModule;

  beforeEach(async () => {
    jest.clearAllMocks();

    module = await Test.createTestingModule({
      providers: [IotService],
    }).compile();

    service = module.get<IotService>(IotService);
  });

  afterEach(async () => {
    await module?.close();
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Initialization Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('Initialization', () => {
    it('should be defined', () => {
      expect(service).toBeDefined();
    });

    it('should connect to Redis on module init', async () => {
      await service.onModuleInit();
      expect(mockRedis.connect).toHaveBeenCalled();
    });

    it('should disconnect from Redis and MQTT on module destroy', async () => {
      await service.onModuleInit();
      await service.onModuleDestroy();
      expect(mockRedis.quit).toHaveBeenCalled();
      expect(mockMqttClient.end).toHaveBeenCalled();
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Sensor Type Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('SensorType Enum', () => {
    it('should have all required sensor types', () => {
      expect(SensorType.SOIL_MOISTURE).toBe('soil_moisture');
      expect(SensorType.SOIL_TEMPERATURE).toBe('soil_temperature');
      expect(SensorType.AIR_TEMPERATURE).toBe('air_temperature');
      expect(SensorType.AIR_HUMIDITY).toBe('air_humidity');
      expect(SensorType.LIGHT_INTENSITY).toBe('light_intensity');
      expect(SensorType.WATER_LEVEL).toBe('water_level');
      expect(SensorType.WATER_FLOW).toBe('water_flow');
      expect(SensorType.PH_LEVEL).toBe('ph_level');
      expect(SensorType.EC_LEVEL).toBe('ec_level');
      expect(SensorType.WIND_SPEED).toBe('wind_speed');
      expect(SensorType.RAIN_GAUGE).toBe('rain_gauge');
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Actuator Type Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('ActuatorType Enum', () => {
    it('should have all required actuator types', () => {
      expect(ActuatorType.PUMP).toBe('pump');
      expect(ActuatorType.VALVE).toBe('valve');
      expect(ActuatorType.MOTOR).toBe('motor');
      expect(ActuatorType.SPRINKLER).toBe('sprinkler');
      expect(ActuatorType.FAN).toBe('fan');
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Pump Control Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('togglePump', () => {
    beforeEach(async () => {
      await service.onModuleInit();
    });

    it('should turn pump ON successfully', async () => {
      const result = await service.togglePump('field-123', 'ON');

      expect(result.success).toBe(true);
      expect(result.message).toContain('field-123');
      expect(mockMqttClient.publish).toHaveBeenCalled();
      expect(mockRedis.setex).toHaveBeenCalled();
    });

    it('should turn pump OFF successfully', async () => {
      const result = await service.togglePump('field-456', 'OFF');

      expect(result.success).toBe(true);
      expect(result.message).toContain('إيقاف');
      expect(mockMqttClient.publish).toHaveBeenCalled();
    });

    it('should include duration in message when provided', async () => {
      const result = await service.togglePump('field-123', 'ON', { duration: 30 });

      expect(result.success).toBe(true);
      expect(result.message).toContain('30');
      expect(result.message).toContain('دقيقة');
    });

    it('should publish to correct MQTT topic', async () => {
      await service.togglePump('field-123', 'ON');

      expect(mockMqttClient.publish).toHaveBeenCalledWith(
        expect.stringContaining('field-123'),
        expect.any(String),
        expect.objectContaining({ qos: 1 }),
      );
    });

    it('should cache actuator state in Redis', async () => {
      await service.togglePump('field-123', 'ON');

      expect(mockRedis.setex).toHaveBeenCalledWith(
        'actuator:field-123:pump',
        expect.any(Number),
        'true',
      );
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Valve Control Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('toggleValve', () => {
    beforeEach(async () => {
      await service.onModuleInit();
    });

    it('should open valve successfully', () => {
      const result = service.toggleValve('field-123', 'valve-1', 'ON');

      expect(result.success).toBe(true);
      expect(result.message).toContain('فتح');
      expect(mockMqttClient.publish).toHaveBeenCalled();
    });

    it('should close valve successfully', () => {
      const result = service.toggleValve('field-123', 'valve-1', 'OFF');

      expect(result.success).toBe(true);
      expect(result.message).toContain('إغلاق');
    });

    it('should publish to correct MQTT topic with valve ID', () => {
      service.toggleValve('field-123', 'valve-2', 'ON');

      expect(mockMqttClient.publish).toHaveBeenCalledWith(
        expect.stringContaining('valve/valve-2'),
        expect.any(String),
        expect.objectContaining({ qos: 1 }),
      );
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Irrigation Schedule Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('setIrrigationSchedule', () => {
    beforeEach(async () => {
      await service.onModuleInit();
    });

    it('should enable irrigation schedule', () => {
      const schedule = {
        startTime: '06:00',
        duration: 30,
        days: ['sunday', 'tuesday', 'thursday'],
        enabled: true,
      };

      const result = service.setIrrigationSchedule('field-123', schedule);

      expect(result.success).toBe(true);
      expect(result.message).toContain('تفعيل');
    });

    it('should disable irrigation schedule', () => {
      const schedule = {
        startTime: '06:00',
        duration: 30,
        days: ['sunday'],
        enabled: false,
      };

      const result = service.setIrrigationSchedule('field-123', schedule);

      expect(result.success).toBe(true);
      expect(result.message).toContain('إيقاف');
    });

    it('should publish with retain flag', () => {
      const schedule = {
        startTime: '06:00',
        duration: 30,
        days: ['sunday'],
        enabled: true,
      };

      service.setIrrigationSchedule('field-123', schedule);

      expect(mockMqttClient.publish).toHaveBeenCalledWith(
        expect.any(String),
        expect.any(String),
        expect.objectContaining({ retain: true }),
      );
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Sensor Data Retrieval Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('getFieldSensorData', () => {
    beforeEach(async () => {
      await service.onModuleInit();
    });

    it('should return empty array when no data', async () => {
      mockRedis.scan.mockResolvedValue(['0', []]);

      const result = await service.getFieldSensorData('field-123');

      expect(result).toEqual([]);
    });

    it('should return sensor readings from Redis', async () => {
      const mockReading: SensorReading = {
        deviceId: 'sensor-1',
        fieldId: 'field-123',
        sensorType: SensorType.SOIL_MOISTURE,
        value: 45.5,
        unit: '%',
        timestamp: new Date(),
        quality: 'good',
      };

      mockRedis.scan
        .mockResolvedValueOnce(['0', ['sensor:field-123:soil_moisture']])
        .mockResolvedValueOnce(['0', []]);
      mockRedis.get.mockResolvedValue(JSON.stringify(mockReading));

      const result = await service.getFieldSensorData('field-123');

      expect(result).toHaveLength(1);
      expect(result[0].deviceId).toBe('sensor-1');
      expect(result[0].value).toBe(45.5);
    });

    it('should handle Redis errors gracefully', async () => {
      mockRedis.scan.mockRejectedValue(new Error('Redis error'));

      const result = await service.getFieldSensorData('field-123');

      expect(result).toEqual([]);
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Get Sensor Reading Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('getSensorReading', () => {
    beforeEach(async () => {
      await service.onModuleInit();
    });

    it('should return sensor reading when found', async () => {
      const mockReading: SensorReading = {
        deviceId: 'sensor-1',
        fieldId: 'field-123',
        sensorType: SensorType.AIR_TEMPERATURE,
        value: 28.5,
        unit: '°C',
        timestamp: new Date(),
        quality: 'good',
      };

      mockRedis.get.mockResolvedValue(JSON.stringify(mockReading));

      const result = await service.getSensorReading('field-123', SensorType.AIR_TEMPERATURE);

      expect(result).not.toBeNull();
      expect(result?.value).toBe(28.5);
      expect(result?.sensorType).toBe(SensorType.AIR_TEMPERATURE);
    });

    it('should return null when not found', async () => {
      mockRedis.get.mockResolvedValue(null);

      const result = await service.getSensorReading('field-123', SensorType.WIND_SPEED);

      expect(result).toBeNull();
    });

    it('should handle Redis errors gracefully', async () => {
      mockRedis.get.mockRejectedValue(new Error('Redis error'));

      const result = await service.getSensorReading('field-123', SensorType.SOIL_MOISTURE);

      expect(result).toBeNull();
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Actuator States Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('getFieldActuatorStates', () => {
    beforeEach(async () => {
      await service.onModuleInit();
    });

    it('should return empty object when no actuators', async () => {
      mockRedis.scan.mockResolvedValue(['0', []]);

      const result = await service.getFieldActuatorStates('field-123');

      expect(result).toEqual({});
    });

    it('should return actuator states from Redis', async () => {
      mockRedis.scan
        .mockResolvedValueOnce(['0', ['actuator:field-123:pump', 'actuator:field-123:valve']])
        .mockResolvedValueOnce(['0', []]);
      mockRedis.get
        .mockResolvedValueOnce('true')
        .mockResolvedValueOnce('false');

      const result = await service.getFieldActuatorStates('field-123');

      expect(result.pump).toBe(true);
      expect(result.valve).toBe(false);
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Connected Devices Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('getConnectedDevices', () => {
    beforeEach(async () => {
      await service.onModuleInit();
    });

    it('should return empty array when no devices', async () => {
      mockRedis.scan.mockResolvedValue(['0', []]);

      const result = await service.getConnectedDevices();

      expect(result).toEqual([]);
    });

    it('should return device statuses from Redis', async () => {
      const mockDevice: DeviceStatus = {
        deviceId: 'device-1',
        fieldId: 'field-123',
        type: 'sensor',
        name: 'Soil Sensor 1',
        status: 'online',
        lastSeen: new Date(),
        batteryLevel: 85,
      };

      mockRedis.scan
        .mockResolvedValueOnce(['0', ['device:device-1']])
        .mockResolvedValueOnce(['0', []]);
      mockRedis.get.mockResolvedValue(JSON.stringify(mockDevice));

      const result = await service.getConnectedDevices();

      expect(result).toHaveLength(1);
      expect(result[0].deviceId).toBe('device-1');
      expect(result[0].status).toBe('online');
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Device Statistics Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('getDeviceStats', () => {
    beforeEach(async () => {
      await service.onModuleInit();
    });

    it('should return zeros when no devices', async () => {
      mockRedis.scan.mockResolvedValue(['0', []]);

      const result = await service.getDeviceStats();

      expect(result.online).toBe(0);
      expect(result.offline).toBe(0);
      expect(result.error).toBe(0);
    });

    it('should count devices by status', async () => {
      const devices: DeviceStatus[] = [
        { deviceId: 'd1', fieldId: 'f1', type: 'sensor', name: 'S1', status: 'online', lastSeen: new Date() },
        { deviceId: 'd2', fieldId: 'f1', type: 'sensor', name: 'S2', status: 'online', lastSeen: new Date() },
        { deviceId: 'd3', fieldId: 'f1', type: 'sensor', name: 'S3', status: 'offline', lastSeen: new Date() },
        { deviceId: 'd4', fieldId: 'f1', type: 'sensor', name: 'S4', status: 'error', lastSeen: new Date() },
      ];

      mockRedis.scan
        .mockResolvedValueOnce(['0', ['device:d1', 'device:d2', 'device:d3', 'device:d4']])
        .mockResolvedValueOnce(['0', []]);

      devices.forEach((d) => {
        mockRedis.get.mockResolvedValueOnce(JSON.stringify(d));
      });

      const result = await service.getDeviceStats();

      expect(result.online).toBe(2);
      expect(result.offline).toBe(1);
      expect(result.error).toBe(1);
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Helper Methods Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('Helper Methods', () => {
    describe('getUnitForSensorType', () => {
      it('should return correct unit for soil moisture', () => {
        const unit = (service as any).getUnitForSensorType(SensorType.SOIL_MOISTURE);
        expect(unit).toBe('%');
      });

      it('should return correct unit for temperature', () => {
        const unit = (service as any).getUnitForSensorType(SensorType.AIR_TEMPERATURE);
        expect(unit).toBe('°C');
      });

      it('should return correct unit for pH level', () => {
        const unit = (service as any).getUnitForSensorType(SensorType.PH_LEVEL);
        expect(unit).toBe('pH');
      });

      it('should return correct unit for EC level', () => {
        const unit = (service as any).getUnitForSensorType(SensorType.EC_LEVEL);
        expect(unit).toBe('mS/cm');
      });
    });

    describe('assessReadingQuality', () => {
      it('should return good for valid soil moisture', () => {
        const quality = (service as any).assessReadingQuality(SensorType.SOIL_MOISTURE, 50);
        expect(quality).toBe('good');
      });

      it('should return error for out-of-range value', () => {
        const quality = (service as any).assessReadingQuality(SensorType.SOIL_MOISTURE, 150);
        expect(quality).toBe('error');
      });

      it('should return error for negative temperature below range', () => {
        const quality = (service as any).assessReadingQuality(SensorType.AIR_TEMPERATURE, -30);
        expect(quality).toBe('error');
      });

      it('should return good for valid pH', () => {
        const quality = (service as any).assessReadingQuality(SensorType.PH_LEVEL, 7);
        expect(quality).toBe('good');
      });

      it('should return error for pH above 14', () => {
        const quality = (service as any).assessReadingQuality(SensorType.PH_LEVEL, 15);
        expect(quality).toBe('error');
      });
    });
  });
});
