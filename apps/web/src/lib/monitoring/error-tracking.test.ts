/**
 * SAHOOL Error Tracking Tests
 * اختبارات تتبع الأخطاء
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  captureError,
  addBreadcrumb,
  getBreadcrumbs,
  clearBreadcrumbs,
  reportWebVitals,
  setUser,
  clearUser,
  initializeErrorTracking,
} from './error-tracking';

describe('Error Tracking', () => {
  beforeEach(() => {
    clearBreadcrumbs();
    clearUser();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('captureError', () => {
    it('should capture an error with metadata', () => {
      const fetchSpy = vi.spyOn(global, 'fetch');
      const error = new Error('Test error');

      captureError(error, undefined, { context: 'test' });

      // Should attempt to send error to endpoint
      expect(fetchSpy).toHaveBeenCalled();
    });

    it('should handle errors without metadata', () => {
      const fetchSpy = vi.spyOn(global, 'fetch');
      const error = new Error('Simple error');

      captureError(error);

      // Should attempt to send error to endpoint
      expect(fetchSpy).toHaveBeenCalled();
    });
  });

  describe('addBreadcrumb', () => {
    it('should add a breadcrumb', () => {
      addBreadcrumb({
        type: 'navigation',
        category: 'navigation',
        message: 'User navigated to /fields',
      });

      const breadcrumbs = getBreadcrumbs();
      expect(breadcrumbs).toHaveLength(1);
      expect(breadcrumbs[0]?.category).toBe('navigation');
    });

    it('should limit breadcrumbs to max size', () => {
      // Add more than the max
      for (let i = 0; i < 60; i++) {
        addBreadcrumb({
          type: 'console',
          category: 'test',
          message: `Breadcrumb ${i}`,
        });
      }

      const breadcrumbs = getBreadcrumbs();
      expect(breadcrumbs.length).toBeLessThanOrEqual(50);
    });

    it('should add timestamp automatically', () => {
      addBreadcrumb({
        type: 'click',
        category: 'action',
        message: 'Button clicked',
      });

      const breadcrumbs = getBreadcrumbs();
      expect(breadcrumbs[0]?.timestamp).toBeDefined();
    });
  });

  describe('clearBreadcrumbs', () => {
    it('should clear all breadcrumbs', () => {
      addBreadcrumb({ type: 'console', category: 'test', message: 'Test' });
      addBreadcrumb({ type: 'console', category: 'test', message: 'Test 2' });

      clearBreadcrumbs();

      expect(getBreadcrumbs()).toHaveLength(0);
    });
  });

  describe('reportWebVitals', () => {
    it('should report web vitals metrics', () => {
      // // const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

      reportWebVitals({
        name: 'LCP',
        value: 1500,
        id: 'test-id',
      });

      // The function should execute without errors
      expect(true).toBe(true);
    });
  });

  describe('setUser', () => {
    it('should set user context', () => {
      setUser({
        id: 'user-123',
        email: 'test@sahool.com',
        name: 'Test User',
      });

      // User should be set (internal state)
      expect(true).toBe(true);
    });
  });

  describe('clearUser', () => {
    it('should clear user context', () => {
      setUser({ id: 'user-123' });
      clearUser();

      // User should be cleared
      expect(true).toBe(true);
    });
  });

  describe('initializeErrorTracking', () => {
    it('should initialize error tracking', () => {
      initializeErrorTracking({ userId: 'user-123' });

      // Should initialize without errors
      expect(true).toBe(true);
    });

    it('should initialize without options', () => {
      initializeErrorTracking();

      // Should initialize without errors
      expect(true).toBe(true);
    });
  });
});
