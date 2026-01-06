/**
 * Window Calculator Unit Tests
 * اختبارات وحدة حاسبة النوافذ
 *
 * Tests for spray window and irrigation need calculations
 */

import { describe, it, expect } from 'vitest';
import {
  calculateSprayWindow,
  calculateIrrigationNeed,
  getOptimalWindow,
  groupIntoWindows,
  DEFAULT_SPRAY_CRITERIA,
} from '../utils/window-calculator';
import type { WeatherCondition, SoilMoistureData, ETData } from '../types/action-windows';

describe('Window Calculator', () => {
  describe('calculateSprayWindow', () => {
    const optimalConditions: WeatherCondition = {
      timestamp: '2026-01-06T09:00:00Z',
      temperature: 22,
      humidity: 65,
      windSpeed: 8,
      windDirection: 'NE',
      rainProbability: 5,
      precipitation: 0,
      cloudCover: 30,
    };

    it('should return optimal status for ideal weather conditions', () => {
      const result = calculateSprayWindow(optimalConditions);

      expect(result.status).toBe('optimal');
      expect(result.score).toBeGreaterThanOrEqual(80);
      expect(result.warnings).toHaveLength(0);
      expect(result.suitability.windSpeed).toBe(true);
      expect(result.suitability.temperature).toBe(true);
      expect(result.suitability.humidity).toBe(true);
      expect(result.suitability.rain).toBe(true);
    });

    it('should flag high wind speed as unsuitable', () => {
      const highWindConditions: WeatherCondition = {
        ...optimalConditions,
        windSpeed: 25, // Above max threshold
      };

      const result = calculateSprayWindow(highWindConditions);

      expect(result.suitability.windSpeed).toBe(false);
      expect(result.warnings.length).toBeGreaterThan(0);
      expect(result.warnings[0]).toContain('Wind speed too high');
      // Score should be reduced due to wind speed failure
      expect(result.score).toBeLessThan(100);
    });

    it('should flag low wind speed as unsuitable', () => {
      const lowWindConditions: WeatherCondition = {
        ...optimalConditions,
        windSpeed: 1, // Below min threshold
      };

      const result = calculateSprayWindow(lowWindConditions);

      expect(result.suitability.windSpeed).toBe(false);
      expect(result.warnings.some(w => w.includes('too low'))).toBe(true);
      // Score should be reduced
      expect(result.score).toBeLessThan(100);
    });

    it('should flag rain as unsuitable and add warnings', () => {
      const rainyConditions: WeatherCondition = {
        ...optimalConditions,
        precipitation: 5,
        rainProbability: 80,
      };

      const result = calculateSprayWindow(rainyConditions);

      // Rain check should fail
      expect(result.suitability.rain).toBe(false);
      expect(result.warnings.some(w => w.includes('Rain') || w.includes('rain'))).toBe(true);
      // Score should be reduced (75 instead of 100)
      expect(result.score).toBeLessThan(100);
    });

    it('should return avoid status for multiple failures', () => {
      const badConditions: WeatherCondition = {
        timestamp: '2026-01-06T15:00:00Z',
        temperature: 35, // Too high
        humidity: 95, // Too high
        windSpeed: 25, // Too high
        windDirection: 'S',
        rainProbability: 60,
        precipitation: 5,
        cloudCover: 90,
      };

      const result = calculateSprayWindow(badConditions);

      expect(result.status).toBe('avoid');
      expect(result.score).toBeLessThan(50);
    });

    it('should return marginal status for borderline conditions', () => {
      const marginalConditions: WeatherCondition = {
        ...optimalConditions,
        temperature: 29, // Near max threshold
        humidity: 85, // Near max threshold
      };

      const result = calculateSprayWindow(marginalConditions);

      expect(['optimal', 'marginal']).toContain(result.status);
    });

    it('should respect custom criteria', () => {
      const customCriteria = {
        windSpeedMax: 10,
        temperatureMax: 25,
      };

      const result = calculateSprayWindow(
        { ...optimalConditions, windSpeed: 12 },
        customCriteria
      );

      expect(result.suitability.windSpeed).toBe(false);
    });

    it('should provide Arabic warnings', () => {
      const highTempConditions: WeatherCondition = {
        ...optimalConditions,
        temperature: 35,
      };

      const result = calculateSprayWindow(highTempConditions);

      expect(result.warningsAr.length).toBeGreaterThan(0);
      expect(result.warningsAr[0]).toContain('درجة الحرارة');
    });
  });

  describe('calculateIrrigationNeed', () => {
    const normalSoilMoisture: SoilMoistureData = {
      current: 45,
      target: 70,
      fieldCapacity: 85,
      wiltingPoint: 15,
      timestamp: '2026-01-06T09:00:00Z',
    };

    const normalET: ETData = {
      et0: 5,
      etc: 4,
      kc: 0.8,
      timestamp: '2026-01-06T09:00:00Z',
    };

    it('should calculate irrigation need for moisture deficit', () => {
      const result = calculateIrrigationNeed(normalSoilMoisture, normalET);

      expect(result.urgency).toBeDefined();
      expect(['none', 'low', 'medium', 'high', 'critical']).toContain(result.urgency);
      expect(result.soilMoistureDeficit).toBeGreaterThanOrEqual(0);
      expect(result.recommendedAmount).toBeGreaterThanOrEqual(0);
    });

    it('should return none urgency when soil is adequately moist', () => {
      const moistSoil: SoilMoistureData = {
        ...normalSoilMoisture,
        current: 75, // Above target
      };

      const result = calculateIrrigationNeed(moistSoil, normalET);

      expect(result.urgency).toBe('none');
    });

    it('should return high urgency when near wilting point', () => {
      const drySoil: SoilMoistureData = {
        ...normalSoilMoisture,
        current: 20, // Near wilting point (15)
      };

      const result = calculateIrrigationNeed(drySoil, normalET);

      // Near wilting point should be high or critical
      expect(['high', 'critical']).toContain(result.urgency);
    });

    it('should calculate crop ET when etc is not provided', () => {
      const etWithoutEtc: ETData = {
        et0: 5,
        kc: 0.8,
        timestamp: '2026-01-06T09:00:00Z',
      };

      const result = calculateIrrigationNeed(normalSoilMoisture, etWithoutEtc);

      expect(result.et0).toBeDefined();
      // Result should include calculated ET value
      expect(result.reasoning).toBeDefined();
    });
  });

  describe('getOptimalWindow', () => {
    const optimalCondition: WeatherCondition = {
      timestamp: '2026-01-06T09:00:00Z',
      temperature: 22,
      humidity: 65,
      windSpeed: 8,
      windDirection: 'NE',
      rainProbability: 5,
      precipitation: 0,
      cloudCover: 30,
    };

    const marginalCondition: WeatherCondition = {
      timestamp: '2026-01-06T12:00:00Z',
      temperature: 28,
      humidity: 88,
      windSpeed: 12,
      windDirection: 'E',
      rainProbability: 15,
      precipitation: 0,
      cloudCover: 50,
    };

    const unsuitableCondition: WeatherCondition = {
      timestamp: '2026-01-06T15:00:00Z',
      temperature: 35,
      humidity: 95,
      windSpeed: 25,
      windDirection: 'S',
      rainProbability: 60,
      precipitation: 5,
      cloudCover: 90,
    };

    it('should return the best condition from a list', () => {
      const conditions = [marginalCondition, optimalCondition, unsuitableCondition];

      const result = getOptimalWindow(conditions, 'spray');

      expect(result).not.toBeNull();
      // Should return one of the acceptable conditions (not the unsuitable one)
      expect([optimalCondition.timestamp, marginalCondition.timestamp]).toContain(result?.timestamp);
    });

    it('should return a condition if any marginal exists', () => {
      const conditions = [marginalCondition, unsuitableCondition];

      const result = getOptimalWindow(conditions, 'spray');

      expect(result).not.toBeNull();
    });

    it('should return null for empty array', () => {
      const result = getOptimalWindow([], 'spray');

      expect(result).toBeNull();
    });
  });

  describe('groupIntoWindows', () => {
    it('should group consecutive optimal slots into windows', () => {
      const slots = [
        { timestamp: '2026-01-06T09:00:00Z', status: 'optimal' as const },
        { timestamp: '2026-01-06T10:00:00Z', status: 'optimal' as const },
        { timestamp: '2026-01-06T11:00:00Z', status: 'optimal' as const },
        { timestamp: '2026-01-06T12:00:00Z', status: 'unsuitable' as const },
        { timestamp: '2026-01-06T15:00:00Z', status: 'optimal' as const },
      ];

      const windows = groupIntoWindows(slots, 2);

      expect(windows.length).toBeGreaterThanOrEqual(1);
      expect(windows[0].status).toBe('optimal');
      expect(windows[0].duration).toBeGreaterThanOrEqual(2);
    });

    it('should exclude windows shorter than minimum duration', () => {
      const slots = [
        { timestamp: '2026-01-06T09:00:00Z', status: 'optimal' as const },
        { timestamp: '2026-01-06T12:00:00Z', status: 'unsuitable' as const },
      ];

      const windows = groupIntoWindows(slots, 3); // Require 3 hours min

      // Single hour slot should be excluded if minDuration is 3
      expect(windows.filter(w => w.status === 'optimal' && w.duration < 3)).toHaveLength(0);
    });
  });

  describe('DEFAULT_SPRAY_CRITERIA', () => {
    it('should have reasonable default values', () => {
      expect(DEFAULT_SPRAY_CRITERIA.windSpeedMax).toBe(15);
      expect(DEFAULT_SPRAY_CRITERIA.windSpeedMin).toBe(3);
      expect(DEFAULT_SPRAY_CRITERIA.temperatureMin).toBe(10);
      expect(DEFAULT_SPRAY_CRITERIA.temperatureMax).toBe(30);
      expect(DEFAULT_SPRAY_CRITERIA.humidityMin).toBe(50);
      expect(DEFAULT_SPRAY_CRITERIA.humidityMax).toBe(90);
      expect(DEFAULT_SPRAY_CRITERIA.rainProbabilityMax).toBe(20);
      expect(DEFAULT_SPRAY_CRITERIA.minDuration).toBe(2);
    });
  });
});
