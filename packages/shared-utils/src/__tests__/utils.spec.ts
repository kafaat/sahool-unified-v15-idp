/**
 * Unit Tests for Shared Utilities
 * Tests utility functions from @sahool/shared-utils
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  // Class name utilities
  cn,
  // Date formatting
  formatDate,
  formatDateTime,
  // Number formatting
  formatNumber,
  formatArea,
  formatCurrency,
  formatPercentage,
  // Color utilities
  getHealthScoreColor,
  getSeverityColor,
  getStatusColor,
  // Label utilities
  getSeverityLabel,
  getStatusLabel,
  // Validation utilities
  isEmpty,
  isValidEmail,
  isValidYemenPhone,
  // String utilities
  truncate,
  capitalize,
  generateId,
} from '../index';

// ═══════════════════════════════════════════════════════════════════════════
// Class Name Utilities Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Class Name Utilities', () => {
  describe('cn', () => {
    it('should merge class names', () => {
      const result = cn('class1', 'class2');
      expect(result).toContain('class1');
      expect(result).toContain('class2');
    });

    it('should handle conditional classes', () => {
      const result = cn('base', true && 'conditional', false && 'hidden');
      expect(result).toContain('base');
      expect(result).toContain('conditional');
      expect(result).not.toContain('hidden');
    });

    it('should merge Tailwind classes correctly', () => {
      const result = cn('p-4', 'p-8'); // Should keep only p-8
      expect(result).toBe('p-8');
    });

    it('should handle arrays of classes', () => {
      const result = cn(['class1', 'class2'], 'class3');
      expect(result).toContain('class1');
      expect(result).toContain('class2');
      expect(result).toContain('class3');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Date Formatting Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Date Formatting', () => {
  describe('formatDate', () => {
    it('should format date in Arabic locale', () => {
      const date = new Date('2024-01-15');
      const result = formatDate(date, 'ar');
      expect(result).toBeTruthy();
      expect(typeof result).toBe('string');
    });

    it('should format date in English locale', () => {
      const date = new Date('2024-01-15');
      const result = formatDate(date, 'en');
      expect(result).toBeTruthy();
      expect(result).toMatch(/Jan/i);
    });

    it('should handle string dates', () => {
      const result = formatDate('2024-01-15', 'en');
      expect(result).toBeTruthy();
    });

    it('should default to Arabic locale', () => {
      const date = new Date('2024-01-15');
      const result = formatDate(date);
      expect(result).toBeTruthy();
    });
  });

  describe('formatDateTime', () => {
    it('should format date with time in Arabic', () => {
      const date = new Date('2024-01-15T14:30:00');
      const result = formatDateTime(date, 'ar');
      expect(result).toBeTruthy();
      expect(typeof result).toBe('string');
    });

    it('should format date with time in English', () => {
      const date = new Date('2024-01-15T14:30:00');
      const result = formatDateTime(date, 'en');
      expect(result).toBeTruthy();
    });

    it('should handle string dates', () => {
      const result = formatDateTime('2024-01-15T14:30:00', 'en');
      expect(result).toBeTruthy();
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Number Formatting Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Number Formatting', () => {
  describe('formatNumber', () => {
    it('should format number in Arabic locale', () => {
      const result = formatNumber(1234567, 'ar');
      expect(result).toBeTruthy();
      expect(typeof result).toBe('string');
    });

    it('should format number in English locale', () => {
      const result = formatNumber(1234567, 'en');
      expect(result).toBe('1,234,567');
    });

    it('should handle decimal numbers', () => {
      const result = formatNumber(1234.56, 'en');
      expect(result).toContain('1,234');
    });

    it('should default to Arabic locale', () => {
      const result = formatNumber(1234);
      expect(result).toBeTruthy();
    });
  });

  describe('formatArea', () => {
    it('should format area in hectares (Arabic)', () => {
      const result = formatArea(50.5, 'ar');
      expect(result).toContain('50');
      expect(result).toContain('هكتار');
    });

    it('should format area in hectares (English)', () => {
      const result = formatArea(50.5, 'en');
      expect(result).toContain('50.5');
      expect(result).toContain('ha');
    });

    it('should handle large areas', () => {
      const result = formatArea(1000, 'en');
      expect(result).toContain('1,000');
    });
  });

  describe('formatCurrency', () => {
    it('should format currency in YER (Arabic)', () => {
      const result = formatCurrency(1000, 'ar', 'YER');
      expect(result).toBeTruthy();
    });

    it('should format currency in YER (English)', () => {
      const result = formatCurrency(1000, 'en', 'YER');
      expect(result).toBeTruthy();
    });

    it('should handle different currencies', () => {
      const result = formatCurrency(100, 'en', 'USD');
      expect(result).toBeTruthy();
    });

    it('should default to YER', () => {
      const result = formatCurrency(1000, 'en');
      expect(result).toBeTruthy();
    });
  });

  describe('formatPercentage', () => {
    it('should format percentage', () => {
      const result = formatPercentage(75.5, 'en');
      expect(result).toBe('75.5%');
    });

    it('should round to 2 decimal places', () => {
      const result = formatPercentage(75.556, 'en');
      expect(result).toBe('75.56%');
    });

    it('should handle zero', () => {
      const result = formatPercentage(0, 'en');
      expect(result).toBe('0%');
    });

    it('should handle 100%', () => {
      const result = formatPercentage(100, 'en');
      expect(result).toBe('100%');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Color Utilities Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Color Utilities', () => {
  describe('getHealthScoreColor', () => {
    it('should return green for high scores (>= 80)', () => {
      const result = getHealthScoreColor(85);
      expect(result).toContain('green');
    });

    it('should return yellow for medium scores (60-79)', () => {
      const result = getHealthScoreColor(70);
      expect(result).toContain('yellow');
    });

    it('should return orange for low scores (40-59)', () => {
      const result = getHealthScoreColor(50);
      expect(result).toContain('orange');
    });

    it('should return red for very low scores (< 40)', () => {
      const result = getHealthScoreColor(30);
      expect(result).toContain('red');
    });

    it('should handle edge cases', () => {
      expect(getHealthScoreColor(80)).toContain('green');
      expect(getHealthScoreColor(60)).toContain('yellow');
      expect(getHealthScoreColor(40)).toContain('orange');
      expect(getHealthScoreColor(0)).toContain('red');
    });
  });

  describe('getSeverityColor', () => {
    it('should return correct color for low severity', () => {
      const result = getSeverityColor('low');
      expect(result).toContain('green');
    });

    it('should return correct color for medium severity', () => {
      const result = getSeverityColor('medium');
      expect(result).toContain('yellow');
    });

    it('should return correct color for high severity', () => {
      const result = getSeverityColor('high');
      expect(result).toContain('orange');
    });

    it('should return correct color for critical severity', () => {
      const result = getSeverityColor('critical');
      expect(result).toContain('red');
    });

    it('should handle unknown severity', () => {
      const result = getSeverityColor('unknown');
      expect(result).toContain('gray');
    });
  });

  describe('getStatusColor', () => {
    it('should return correct color for pending status', () => {
      const result = getStatusColor('pending');
      expect(result).toContain('yellow');
    });

    it('should return correct color for active status', () => {
      const result = getStatusColor('active');
      expect(result).toContain('green');
    });

    it('should return correct color for error status', () => {
      const result = getStatusColor('error');
      expect(result).toContain('red');
    });

    it('should handle unknown status', () => {
      const result = getStatusColor('unknown');
      expect(result).toContain('gray');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Label Utilities Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Label Utilities', () => {
  describe('getSeverityLabel', () => {
    it('should return Arabic labels', () => {
      expect(getSeverityLabel('low', 'ar')).toBe('منخفض');
      expect(getSeverityLabel('medium', 'ar')).toBe('متوسط');
      expect(getSeverityLabel('high', 'ar')).toBe('مرتفع');
      expect(getSeverityLabel('critical', 'ar')).toBe('حرج');
    });

    it('should return English labels', () => {
      expect(getSeverityLabel('low', 'en')).toBe('Low');
      expect(getSeverityLabel('medium', 'en')).toBe('Medium');
      expect(getSeverityLabel('high', 'en')).toBe('High');
      expect(getSeverityLabel('critical', 'en')).toBe('Critical');
    });

    it('should return original value for unknown severity', () => {
      expect(getSeverityLabel('unknown', 'ar')).toBe('unknown');
    });

    it('should default to Arabic', () => {
      const result = getSeverityLabel('low');
      expect(result).toBe('منخفض');
    });
  });

  describe('getStatusLabel', () => {
    it('should return Arabic labels', () => {
      expect(getStatusLabel('pending', 'ar')).toBe('قيد المراجعة');
      expect(getStatusLabel('active', 'ar')).toBe('نشط');
      expect(getStatusLabel('success', 'ar')).toBe('نجاح');
    });

    it('should return English labels', () => {
      expect(getStatusLabel('pending', 'en')).toBe('Pending');
      expect(getStatusLabel('active', 'en')).toBe('Active');
      expect(getStatusLabel('success', 'en')).toBe('Success');
    });

    it('should return original value for unknown status', () => {
      expect(getStatusLabel('unknown', 'ar')).toBe('unknown');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Validation Utilities Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Validation Utilities', () => {
  describe('isEmpty', () => {
    it('should return true for null and undefined', () => {
      expect(isEmpty(null)).toBe(true);
      expect(isEmpty(undefined)).toBe(true);
    });

    it('should return true for empty string', () => {
      expect(isEmpty('')).toBe(true);
      expect(isEmpty('   ')).toBe(true);
    });

    it('should return true for empty array', () => {
      expect(isEmpty([])).toBe(true);
    });

    it('should return true for empty object', () => {
      expect(isEmpty({})).toBe(true);
    });

    it('should return false for non-empty values', () => {
      expect(isEmpty('text')).toBe(false);
      expect(isEmpty([1, 2, 3])).toBe(false);
      expect(isEmpty({ key: 'value' })).toBe(false);
      expect(isEmpty(0)).toBe(false);
      expect(isEmpty(false)).toBe(false);
    });
  });

  describe('isValidEmail', () => {
    it('should validate correct email addresses', () => {
      expect(isValidEmail('user@example.com')).toBe(true);
      expect(isValidEmail('test.user@example.co.uk')).toBe(true);
      expect(isValidEmail('user+tag@domain.com')).toBe(true);
    });

    it('should reject invalid email addresses', () => {
      expect(isValidEmail('invalid')).toBe(false);
      expect(isValidEmail('invalid@')).toBe(false);
      expect(isValidEmail('@example.com')).toBe(false);
      expect(isValidEmail('user@')).toBe(false);
      expect(isValidEmail('user @example.com')).toBe(false);
    });

    it('should handle empty string', () => {
      expect(isValidEmail('')).toBe(false);
    });
  });

  describe('isValidYemenPhone', () => {
    it('should validate Yemen phone numbers', () => {
      expect(isValidYemenPhone('+967712345678')).toBe(true);
      expect(isValidYemenPhone('967712345678')).toBe(true);
      expect(isValidYemenPhone('00967712345678')).toBe(true);
      expect(isValidYemenPhone('712345678')).toBe(true);
    });

    it('should validate phone with spaces', () => {
      expect(isValidYemenPhone('+967 71 234 5678')).toBe(true);
      expect(isValidYemenPhone('967 712 345 678')).toBe(true);
    });

    it('should reject invalid phone numbers', () => {
      expect(isValidYemenPhone('123456')).toBe(false);
      expect(isValidYemenPhone('+966712345678')).toBe(false); // Wrong country code
      expect(isValidYemenPhone('012345678')).toBe(false); // Starts with 0
      expect(isValidYemenPhone('')).toBe(false);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// String Utilities Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('String Utilities', () => {
  describe('truncate', () => {
    it('should truncate long strings', () => {
      const longString = 'This is a very long string that needs to be truncated';
      const result = truncate(longString, 20);
      expect(result.length).toBeLessThanOrEqual(23); // 20 + '...'
      expect(result).toContain('...');
    });

    it('should not truncate short strings', () => {
      const shortString = 'Short';
      const result = truncate(shortString, 20);
      expect(result).toBe(shortString);
    });

    it('should handle exact length', () => {
      const text = 'Exactly twenty chars';
      const result = truncate(text, 20);
      expect(result).toBe(text);
    });
  });

  describe('capitalize', () => {
    it('should capitalize first letter', () => {
      expect(capitalize('hello')).toBe('Hello');
      expect(capitalize('world')).toBe('World');
    });

    it('should handle already capitalized strings', () => {
      expect(capitalize('Hello')).toBe('Hello');
    });

    it('should handle single character', () => {
      expect(capitalize('a')).toBe('A');
    });

    it('should handle empty string', () => {
      expect(capitalize('')).toBe('');
    });
  });

  describe('generateId', () => {
    it('should generate unique IDs', () => {
      const id1 = generateId();
      const id2 = generateId();
      expect(id1).not.toBe(id2);
    });

    it('should include prefix', () => {
      const id = generateId('test');
      expect(id).toMatch(/^test_/);
    });

    it('should use default prefix', () => {
      const id = generateId();
      expect(id).toMatch(/^id_/);
    });

    it('should generate valid format', () => {
      const id = generateId('prefix');
      expect(id).toMatch(/^prefix_\d+_[a-z0-9]+$/);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Integration Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Integration Tests', () => {
  describe('Formatting Pipeline', () => {
    it('should format complete user data', () => {
      const userData = {
        email: 'user@example.com',
        phone: '+967712345678',
        createdAt: new Date('2024-01-15'),
        balance: 1000.50,
        completionRate: 75.5,
      };

      expect(isValidEmail(userData.email)).toBe(true);
      expect(isValidYemenPhone(userData.phone)).toBe(true);

      const formattedDate = formatDate(userData.createdAt, 'en');
      const formattedBalance = formatCurrency(userData.balance, 'en', 'YER');
      const formattedRate = formatPercentage(userData.completionRate, 'en');

      expect(formattedDate).toBeTruthy();
      expect(formattedBalance).toBeTruthy();
      expect(formattedRate).toBe('75.5%');
    });
  });

  describe('Field Data Formatting', () => {
    it('should format agricultural field data', () => {
      const fieldData = {
        name: 'North Field',
        area: 50.5,
        healthScore: 85,
        status: 'active',
        severity: 'low',
      };

      const formattedArea = formatArea(fieldData.area, 'en');
      const healthColor = getHealthScoreColor(fieldData.healthScore);
      const statusColor = getStatusColor(fieldData.status);
      const severityLabel = getSeverityLabel(fieldData.severity, 'en');

      expect(formattedArea).toContain('50.5');
      expect(healthColor).toContain('green');
      expect(statusColor).toContain('green');
      expect(severityLabel).toBe('Low');
    });
  });

  describe('Bilingual Support', () => {
    it('should support both Arabic and English', () => {
      const score = 85;
      const severity = 'high';
      const status = 'active';

      // Arabic
      const arabicSeverity = getSeverityLabel(severity, 'ar');
      const arabicStatus = getStatusLabel(status, 'ar');
      expect(arabicSeverity).toBe('مرتفع');
      expect(arabicStatus).toBe('نشط');

      // English
      const englishSeverity = getSeverityLabel(severity, 'en');
      const englishStatus = getStatusLabel(status, 'en');
      expect(englishSeverity).toBe('High');
      expect(englishStatus).toBe('Active');
    });
  });
});
