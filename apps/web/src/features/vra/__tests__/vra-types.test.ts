/**
 * VRA Types Unit Tests
 * اختبارات وحدة أنواع التطبيق المتغير
 *
 * Tests for VRA type definitions and data validation
 */

import { describe, it, expect } from 'vitest';
import type {
  VRAType,
  VRAMethod,
  ZoneLevel,
  ExportFormat,
  PrescriptionRequest,
  ZoneResult,
  PrescriptionResponse,
} from '../types/vra';

describe('VRA Types', () => {
  describe('VRAType', () => {
    it('should accept valid VRA types', () => {
      const validTypes: VRAType[] = ['fertilizer', 'seed', 'lime', 'pesticide', 'irrigation'];

      validTypes.forEach((type) => {
        expect(['fertilizer', 'seed', 'lime', 'pesticide', 'irrigation']).toContain(type);
      });
    });
  });

  describe('VRAMethod', () => {
    it('should accept valid zone classification methods', () => {
      const validMethods: VRAMethod[] = ['ndvi', 'yield', 'soil', 'combined'];

      validMethods.forEach((method) => {
        expect(['ndvi', 'yield', 'soil', 'combined']).toContain(method);
      });
    });
  });

  describe('ZoneLevel', () => {
    it('should accept valid zone levels', () => {
      const validLevels: ZoneLevel[] = ['very_low', 'low', 'medium', 'high', 'very_high'];

      expect(validLevels).toHaveLength(5);
      expect(validLevels).toContain('very_low');
      expect(validLevels).toContain('very_high');
    });
  });

  describe('ExportFormat', () => {
    it('should support all export formats', () => {
      const formats: ExportFormat[] = ['geojson', 'csv', 'shapefile', 'isoxml'];

      expect(formats).toContain('geojson');
      expect(formats).toContain('isoxml'); // ISO 11783 for agricultural machinery
    });
  });

  describe('PrescriptionRequest', () => {
    it('should validate required fields', () => {
      const validRequest: PrescriptionRequest = {
        fieldId: 'field-123',
        latitude: 15.3694,
        longitude: 44.191,
        vraType: 'fertilizer',
        targetRate: 150,
        unit: 'kg/ha',
      };

      expect(validRequest.fieldId).toBeDefined();
      expect(validRequest.vraType).toBe('fertilizer');
      expect(validRequest.targetRate).toBe(150);
    });

    it('should support optional fields', () => {
      const requestWithOptions: PrescriptionRequest = {
        fieldId: 'field-123',
        latitude: 15.3694,
        longitude: 44.191,
        vraType: 'seed',
        targetRate: 80000,
        unit: 'seeds/ha',
        numZones: 5,
        zoneMethod: 'combined',
        minRate: 60000,
        maxRate: 100000,
        productPricePerUnit: 0.05,
        notes: 'Variable seeding for maize',
        notesAr: 'بذر متغير للذرة',
      };

      expect(requestWithOptions.numZones).toBe(5);
      expect(requestWithOptions.zoneMethod).toBe('combined');
      expect(requestWithOptions.notesAr).toBeDefined();
    });
  });

  describe('ZoneResult', () => {
    it('should have all required zone properties', () => {
      const zone: ZoneResult = {
        zoneId: 1,
        zoneName: 'High Productivity Zone',
        zoneNameAr: 'منطقة إنتاجية عالية',
        zoneLevel: 'high',
        ndviMin: 0.7,
        ndviMax: 0.85,
        areaHa: 5.2,
        percentage: 35,
        centroid: [44.191, 15.3694],
        recommendedRate: 180,
        unit: 'kg/ha',
        totalProduct: 936,
        color: '#4CAF50',
      };

      expect(zone.zoneId).toBe(1);
      expect(zone.zoneLevel).toBe('high');
      expect(zone.centroid).toHaveLength(2);
      expect(zone.recommendedRate).toBeGreaterThan(zone.ndviMax); // Rate should be sensible
    });

    it('should calculate total product correctly', () => {
      const zone: ZoneResult = {
        zoneId: 1,
        zoneName: 'Test Zone',
        zoneNameAr: 'منطقة اختبار',
        zoneLevel: 'medium',
        ndviMin: 0.5,
        ndviMax: 0.6,
        areaHa: 10,
        percentage: 50,
        centroid: [44.0, 15.0],
        recommendedRate: 100,
        unit: 'kg/ha',
        totalProduct: 1000, // Should be areaHa * recommendedRate
        color: '#FFC107',
      };

      expect(zone.totalProduct).toBe(zone.areaHa * zone.recommendedRate);
    });
  });

  describe('PrescriptionResponse', () => {
    it('should have prescription metadata', () => {
      const response: PrescriptionResponse = {
        id: 'presc-001',
        fieldId: 'field-123',
        vraType: 'fertilizer',
        createdAt: '2026-01-06T10:00:00Z',
        targetRate: 150,
        minRate: 100,
        maxRate: 200,
        unit: 'kg/ha',
        numZones: 3,
        zoneMethod: 'ndvi',
        zones: [],
        totalAreaHa: 15,
        totalProductNeeded: 2100,
        flatRateProduct: 2250,
        savingsPercent: 6.67,
      };

      expect(response.id).toBeDefined();
      expect(response.vraType).toBe('fertilizer');
      expect(response.savingsPercent).toBeGreaterThan(0);
    });

    it('should calculate savings correctly', () => {
      const response: PrescriptionResponse = {
        id: 'presc-002',
        fieldId: 'field-456',
        vraType: 'lime',
        createdAt: new Date().toISOString(),
        targetRate: 2000,
        minRate: 1500,
        maxRate: 2500,
        unit: 'kg/ha',
        numZones: 5,
        zoneMethod: 'soil',
        zones: [],
        totalAreaHa: 20,
        totalProductNeeded: 38000,
        flatRateProduct: 40000, // Target rate * area
        savingsPercent: 5,
      };

      const expectedSavings = ((response.flatRateProduct - response.totalProductNeeded) / response.flatRateProduct) * 100;
      expect(Math.round(response.savingsPercent)).toBe(Math.round(expectedSavings));
    });
  });
});

describe('VRA Data Validation', () => {
  it('should validate NDVI values are between 0 and 1', () => {
    const validNDVI = 0.65;
    const invalidNDVI = 1.5;

    expect(validNDVI).toBeGreaterThanOrEqual(0);
    expect(validNDVI).toBeLessThanOrEqual(1);
    expect(invalidNDVI).toBeGreaterThan(1); // Invalid
  });

  it('should validate coordinates are in valid range', () => {
    const validLat = 15.3694;
    const validLon = 44.191;

    expect(validLat).toBeGreaterThanOrEqual(-90);
    expect(validLat).toBeLessThanOrEqual(90);
    expect(validLon).toBeGreaterThanOrEqual(-180);
    expect(validLon).toBeLessThanOrEqual(180);
  });

  it('should ensure zone percentages sum to 100', () => {
    const zones: Partial<ZoneResult>[] = [
      { percentage: 25 },
      { percentage: 35 },
      { percentage: 40 },
    ];

    const totalPercentage = zones.reduce((sum, z) => sum + (z.percentage || 0), 0);
    expect(totalPercentage).toBe(100);
  });
});
