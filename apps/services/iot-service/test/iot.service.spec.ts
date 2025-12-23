/**
 * SAHOOL IoT Service - Service Unit Tests
 * اختبارات خدمة إنترنت الأشياء
 */

import { Test, TestingModule } from '@nestjs/testing';
import { IotService, SensorType, SensorReading, DeviceStatus } from '../src/iot/iot.service';

// Mock mqtt
jest.mock('mqtt', () => ({
  connect: jest.fn().mockReturnValue({
    on: jest.fn(),
    subscribe: jest.fn(),
    publish: jest.fn(),
    end: jest.fn(),
  }),
}));

describe('IotService', () => {
  let service: IotService;
  let mockMqttClient: any;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [IotService],
    }).compile();

    service = module.get<IotService>(IotService);

    // Get the mocked mqtt client
    const mqtt = require('mqtt');
    mockMqttClient = mqtt.connect();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('Pump Control', () => {
    it('should toggle pump ON', () => {
      const result = service.togglePump('field_001', 'ON');
      expect(result.success).toBe(true);
      expect(result.message).toContain('field_001');
      expect(mockMqttClient.publish).toHaveBeenCalled();
    });

    it('should toggle pump ON with duration', () => {
      const result = service.togglePump('field_001', 'ON', { duration: 30 });
      expect(result.success).toBe(true);
      expect(result.message).toContain('30');
      expect(mockMqttClient.publish).toHaveBeenCalled();
    });

    it('should toggle pump OFF', () => {
      const result = service.togglePump('field_001', 'OFF');
      expect(result.success).toBe(true);
      expect(result.message).toContain('إيقاف');
    });
  });

  describe('Valve Control', () => {
    it('should toggle valve ON', () => {
      const result = service.toggleValve('field_001', 'valve_1', 'ON');
      expect(result.success).toBe(true);
      expect(result.message).toContain('فتح');
      expect(mockMqttClient.publish).toHaveBeenCalled();
    });

    it('should toggle valve OFF', () => {
      const result = service.toggleValve('field_001', 'valve_1', 'OFF');
      expect(result.success).toBe(true);
      expect(result.message).toContain('إغلاق');
    });
  });

  describe('Irrigation Schedule', () => {
    it('should set irrigation schedule', () => {
      const schedule = {
        startTime: '06:00',
        duration: 45,
        days: ['sunday', 'tuesday'],
        enabled: true,
      };
      const result = service.setIrrigationSchedule('field_001', schedule);
      expect(result.success).toBe(true);
      expect(result.message).toContain('تفعيل');
      expect(mockMqttClient.publish).toHaveBeenCalled();
    });

    it('should disable irrigation schedule', () => {
      const schedule = {
        startTime: '06:00',
        duration: 0,
        days: [],
        enabled: false,
      };
      const result = service.setIrrigationSchedule('field_001', schedule);
      expect(result.success).toBe(true);
      expect(result.message).toContain('إيقاف');
    });
  });

  describe('Sensor Data Retrieval', () => {
    it('should return empty array when no sensors exist', () => {
      const result = service.getFieldSensorData('field_unknown');
      expect(result).toEqual([]);
    });

    it('should return null for non-existent sensor reading', () => {
      const result = service.getSensorReading('field_unknown', SensorType.SOIL_MOISTURE);
      expect(result).toBeNull();
    });
  });

  describe('Actuator States', () => {
    it('should return empty object when no actuators exist', () => {
      const result = service.getFieldActuatorStates('field_unknown');
      expect(result).toEqual({});
    });
  });

  describe('Device Management', () => {
    it('should return empty array when no devices connected', () => {
      const result = service.getConnectedDevices();
      expect(result).toEqual([]);
    });

    it('should return zero stats when no devices exist', () => {
      const result = service.getDeviceStats();
      expect(result.online).toBe(0);
      expect(result.offline).toBe(0);
      expect(result.error).toBe(0);
    });
  });
});

describe('IotService - Sensor Types', () => {
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
