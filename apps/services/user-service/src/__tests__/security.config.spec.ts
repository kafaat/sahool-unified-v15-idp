/**
 * Tests for security.config.ts utility functions
 * اختبارات وظائف الأمان
 */

import { splitFullName, DEFAULT_TENANT_ID } from '../utils/security.config';

describe('splitFullName', () => {
  it('should split a full name into firstName and lastName', () => {
    const result = splitFullName('Ahmed Ali');
    expect(result).toEqual({ firstName: 'Ahmed', lastName: 'Ali' });
  });

  it('should handle Arabic names', () => {
    const result = splitFullName('أحمد محمد علي');
    expect(result).toEqual({ firstName: 'أحمد', lastName: 'محمد علي' });
  });

  it('should use the same value for both if only one name part', () => {
    const result = splitFullName('Ahmed');
    expect(result).toEqual({ firstName: 'Ahmed', lastName: 'Ahmed' });
  });

  it('should return null if name is undefined and no firstName/lastName', () => {
    const result = splitFullName(undefined, undefined, undefined);
    expect(result).toBeNull();
  });

  it('should return null if name is empty string', () => {
    const result = splitFullName('');
    expect(result).toBeNull();
  });

  it('should prefer explicit firstName/lastName over name', () => {
    const result = splitFullName('Full Name', 'First', 'Last');
    expect(result).toEqual({ firstName: 'First', lastName: 'Last' });
  });

  it('should use name to fill missing firstName', () => {
    const result = splitFullName('Ahmed Ali', undefined, 'Existing');
    expect(result).toEqual({ firstName: 'Ahmed', lastName: 'Existing' });
  });

  it('should use name to fill missing lastName', () => {
    const result = splitFullName('Ahmed Ali', 'Existing');
    expect(result).toEqual({ firstName: 'Existing', lastName: 'Ali' });
  });

  it('should handle extra whitespace', () => {
    const result = splitFullName('  Ahmed   Ali  ');
    expect(result).toEqual({ firstName: 'Ahmed', lastName: 'Ali' });
  });

  it('should handle three-part names', () => {
    const result = splitFullName('Ahmed bin Ali');
    expect(result).toEqual({ firstName: 'Ahmed', lastName: 'bin Ali' });
  });

  it('should return null if only firstName provided without lastName or name', () => {
    const result = splitFullName(undefined, 'First', undefined);
    expect(result).toBeNull();
  });
});

describe('DEFAULT_TENANT_ID', () => {
  it('should be a valid UUID format', () => {
    expect(DEFAULT_TENANT_ID).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    );
  });
});
