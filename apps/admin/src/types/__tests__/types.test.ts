/**
 * Types & Constants Tests
 * اختبارات الأنواع والثوابت
 */

import { describe, it, expect } from 'vitest';
import { YEMEN_GOVERNORATES } from '../index';

describe('YEMEN_GOVERNORATES', () => {
  it('contains all 22 governorates', () => {
    expect(YEMEN_GOVERNORATES).toHaveLength(22);
  });

  it('each governorate has required fields', () => {
    YEMEN_GOVERNORATES.forEach((gov) => {
      expect(gov.id).toBeTruthy();
      expect(gov.name).toBeTruthy();
      expect(gov.nameAr).toBeTruthy();
      expect(gov.coordinates).toBeDefined();
      expect(gov.coordinates.lat).toBeTypeOf('number');
      expect(gov.coordinates.lng).toBeTypeOf('number');
    });
  });

  it('includes Sanaa', () => {
    const sanaa = YEMEN_GOVERNORATES.find((g) => g.id === 'sanaa');
    expect(sanaa).toBeDefined();
    expect(sanaa?.nameAr).toBe('صنعاء');
  });

  it('includes Aden', () => {
    const aden = YEMEN_GOVERNORATES.find((g) => g.id === 'aden');
    expect(aden).toBeDefined();
    expect(aden?.nameAr).toBe('عدن');
  });

  it('includes Hadramaut', () => {
    const hadramaut = YEMEN_GOVERNORATES.find((g) => g.id === 'hadramaut');
    expect(hadramaut).toBeDefined();
    expect(hadramaut?.nameAr).toBe('حضرموت');
  });

  it('includes Socotra', () => {
    const socotra = YEMEN_GOVERNORATES.find((g) => g.id === 'socotra');
    expect(socotra).toBeDefined();
    expect(socotra?.nameAr).toBe('سقطرى');
  });

  it('has unique IDs', () => {
    const ids = YEMEN_GOVERNORATES.map((g) => g.id);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(ids.length);
  });

  it('has valid coordinate ranges for Yemen', () => {
    YEMEN_GOVERNORATES.forEach((gov) => {
      // Yemen latitude roughly 12-17N, longitude 42-54E
      expect(gov.coordinates.lat).toBeGreaterThan(11);
      expect(gov.coordinates.lat).toBeLessThan(18);
      expect(gov.coordinates.lng).toBeGreaterThan(42);
      expect(gov.coordinates.lng).toBeLessThan(55);
    });
  });
});
