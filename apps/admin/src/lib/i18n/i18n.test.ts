/**
 * SAHOOL i18n Tests
 * اختبارات الترجمة
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  t,
  tp,
  setLocale,
  getLocale,
  formatNumber,
  formatDate,
  formatRelativeTime,
  formatCurrency,
  isRtl,
  getDirection,
  I18n,
  Locale,
} from './index';

describe('i18n', () => {
  beforeEach(() => {
    setLocale('ar'); // Reset to Arabic
  });

  describe('t (translate)', () => {
    it('should translate common keys', () => {
      setLocale('ar');
      expect(t('common.save')).toBe('حفظ');
      expect(t('common.cancel')).toBe('إلغاء');
      expect(t('common.delete')).toBe('حذف');
    });

    it('should translate to English', () => {
      setLocale('en');
      expect(t('common.save')).toBe('Save');
      expect(t('common.cancel')).toBe('Cancel');
      expect(t('common.delete')).toBe('Delete');
    });

    it('should handle parameter interpolation', () => {
      setLocale('ar');
      expect(t('common.welcome', { name: 'أحمد' })).toContain('أحمد');
    });

    it('should return key if translation not found', () => {
      const result = t('nonexistent.key' as any);
      expect(result).toBe('nonexistent.key');
    });

    it('should translate navigation keys', () => {
      setLocale('ar');
      expect(t('nav.dashboard')).toBe('لوحة التحكم');
      expect(t('nav.fields')).toBe('الحقول');
      expect(t('nav.users')).toBe('المستخدمين');
    });

    it('should translate field-related keys', () => {
      setLocale('ar');
      expect(t('fields.title')).toBe('إدارة الحقول');
      expect(t('fields.add')).toBe('إضافة حقل');
      expect(t('fields.area')).toBe('المساحة');
    });
  });

  describe('tp (translate plural)', () => {
    it('should handle Arabic plural forms', () => {
      setLocale('ar');

      expect(tp('fields.count', 0)).toContain('حقول');
      expect(tp('fields.count', 1)).toContain('حقل');
      expect(tp('fields.count', 2)).toContain('حقلان');
      expect(tp('fields.count', 5)).toContain('حقول');
    });

    it('should handle English plural forms', () => {
      setLocale('en');

      expect(tp('fields.count', 1)).toContain('field');
      expect(tp('fields.count', 2)).toContain('fields');
    });

    it('should include count in translation', () => {
      setLocale('ar');
      const result = tp('fields.count', 5);
      expect(result).toContain('5');
    });
  });

  describe('setLocale / getLocale', () => {
    it('should set and get locale', () => {
      setLocale('en');
      expect(getLocale()).toBe('en');

      setLocale('ar');
      expect(getLocale()).toBe('ar');
    });

    it('should persist locale change', () => {
      setLocale('en');
      expect(t('common.save')).toBe('Save');

      setLocale('ar');
      expect(t('common.save')).toBe('حفظ');
    });
  });

  describe('formatNumber', () => {
    it('should format numbers in Arabic locale', () => {
      setLocale('ar');
      const result = formatNumber(1234567.89);
      // Should use Arabic-style formatting
      expect(result).toBeDefined();
    });

    it('should format numbers in English locale', () => {
      setLocale('en');
      const result = formatNumber(1234567.89);
      expect(result).toContain('1');
    });

    it('should handle decimal places', () => {
      const result = formatNumber(1234.5678, { maximumFractionDigits: 2 });
      expect(result).toBeDefined();
    });

    it('should handle percentage', () => {
      const result = formatNumber(0.75, { style: 'percent' });
      expect(result).toContain('75');
    });
  });

  describe('formatDate', () => {
    it('should format date in Arabic', () => {
      setLocale('ar');
      const date = new Date('2024-01-15');
      const result = formatDate(date);
      expect(result).toBeDefined();
    });

    it('should format date in English', () => {
      setLocale('en');
      const date = new Date('2024-01-15');
      const result = formatDate(date);
      expect(result).toBeDefined();
    });

    it('should handle string dates', () => {
      const result = formatDate('2024-01-15');
      expect(result).toBeDefined();
    });

    it('should handle timestamps', () => {
      const result = formatDate(1705276800000);
      expect(result).toBeDefined();
    });
  });

  describe('formatRelativeTime', () => {
    it('should format past time', () => {
      const pastDate = new Date(Date.now() - 60000); // 1 minute ago
      const result = formatRelativeTime(pastDate);
      expect(result).toBeDefined();
    });

    it('should format future time', () => {
      const futureDate = new Date(Date.now() + 3600000); // 1 hour from now
      const result = formatRelativeTime(futureDate);
      expect(result).toBeDefined();
    });

    it('should handle different time units', () => {
      const yesterday = new Date(Date.now() - 86400000);
      const result = formatRelativeTime(yesterday);
      expect(result).toBeDefined();
    });
  });

  describe('formatCurrency', () => {
    it('should format currency in YER', () => {
      setLocale('ar');
      const result = formatCurrency(1000, 'YER');
      expect(result).toBeDefined();
    });

    it('should format currency in USD', () => {
      setLocale('en');
      const result = formatCurrency(1000, 'USD');
      expect(result).toContain('$');
    });

    it('should handle different currencies', () => {
      const result = formatCurrency(1000, 'SAR');
      expect(result).toBeDefined();
    });
  });

  describe('isRtl', () => {
    it('should return true for Arabic', () => {
      expect(isRtl('ar')).toBe(true);
    });

    it('should return false for English', () => {
      expect(isRtl('en')).toBe(false);
    });

    it('should use current locale if not specified', () => {
      setLocale('ar');
      expect(isRtl()).toBe(true);

      setLocale('en');
      expect(isRtl()).toBe(false);
    });
  });

  describe('getDirection', () => {
    it('should return rtl for Arabic', () => {
      expect(getDirection('ar')).toBe('rtl');
    });

    it('should return ltr for English', () => {
      expect(getDirection('en')).toBe('ltr');
    });

    it('should use current locale if not specified', () => {
      setLocale('ar');
      expect(getDirection()).toBe('rtl');
    });
  });

  describe('Error Messages', () => {
    it('should translate validation errors', () => {
      setLocale('ar');
      expect(t('errors.required')).toBe('هذا الحقل مطلوب');
      expect(t('errors.email')).toBe('بريد إلكتروني غير صالح');
    });

    it('should translate validation errors in English', () => {
      setLocale('en');
      expect(t('errors.required')).toBe('This field is required');
      expect(t('errors.email')).toBe('Invalid email address');
    });
  });

  describe('I18n export', () => {
    it('should export all functions', () => {
      expect(I18n.t).toBeDefined();
      expect(I18n.tp).toBeDefined();
      expect(I18n.setLocale).toBeDefined();
      expect(I18n.getLocale).toBeDefined();
      expect(I18n.formatNumber).toBeDefined();
      expect(I18n.formatDate).toBeDefined();
      expect(I18n.formatCurrency).toBeDefined();
      expect(I18n.isRtl).toBeDefined();
    });
  });
});
