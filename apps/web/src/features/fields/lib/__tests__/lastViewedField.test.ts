import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  clearLastViewedField,
  getLastViewedField,
  lastViewedFieldKey,
  saveLastViewedField,
} from '../lastViewedField';

/**
 * The global test setup (`src/__tests__/setup.ts`) replaces
 * `window.localStorage` with `vi.fn()` stubs that return `undefined`.
 * For these tests we want real storage semantics, so we install an
 * in-memory backing store before each test and restore the stubs
 * afterwards.
 */
function installInMemoryLocalStorage(): { restore: () => void } {
  const original = Object.getOwnPropertyDescriptor(window, 'localStorage');
  const store = new Map<string, string>();
  const fake: Storage = {
    get length() {
      return store.size;
    },
    clear: () => store.clear(),
    getItem: (k: string) => (store.has(k) ? store.get(k)! : null),
    key: (i: number) => Array.from(store.keys())[i] ?? null,
    removeItem: (k: string) => {
      store.delete(k);
    },
    setItem: (k: string, v: string) => {
      store.set(k, String(v));
    },
  };
  Object.defineProperty(window, 'localStorage', {
    value: fake,
    configurable: true,
  });
  return {
    restore: () => {
      if (original) {
        Object.defineProperty(window, 'localStorage', original);
      }
    },
  };
}

describe('lastViewedField storage helpers', () => {
  let restoreStorage: () => void;

  beforeEach(() => {
    ({ restore: restoreStorage } = installInMemoryLocalStorage());
  });

  afterEach(() => {
    vi.restoreAllMocks();
    restoreStorage();
  });

  describe('lastViewedFieldKey', () => {
    it('namespaces keys per tenant', () => {
      expect(lastViewedFieldKey('tenant-a')).not.toEqual(
        lastViewedFieldKey('tenant-b'),
      );
    });

    it('falls back to a default namespace when tenant id is missing', () => {
      expect(lastViewedFieldKey(undefined)).toEqual(lastViewedFieldKey(null));
      expect(lastViewedFieldKey('')).toEqual(lastViewedFieldKey(undefined));
    });
  });

  describe('save/get/clear', () => {
    it('round-trips a field id under the tenant namespace', () => {
      saveLastViewedField('tenant-a', 'field-123');
      expect(getLastViewedField('tenant-a')).toBe('field-123');
      // A different tenant must not see another tenant's value.
      expect(getLastViewedField('tenant-b')).toBeNull();
    });

    it('returns null when nothing is stored', () => {
      expect(getLastViewedField('tenant-a')).toBeNull();
    });

    it('clears the stored value', () => {
      saveLastViewedField('tenant-a', 'field-123');
      clearLastViewedField('tenant-a');
      expect(getLastViewedField('tenant-a')).toBeNull();
    });

    it('does not save empty field ids', () => {
      saveLastViewedField('tenant-a', '');
      expect(getLastViewedField('tenant-a')).toBeNull();
    });

    it('handles undefined/null tenant ids consistently', () => {
      saveLastViewedField(undefined, 'field-xyz');
      expect(getLastViewedField(null)).toBe('field-xyz');
    });
  });

  describe('resilience', () => {
    it('does not throw if localStorage.setItem throws (quota exceeded)', () => {
      const setItemSpy = vi
        .spyOn(window.localStorage, 'setItem')
        .mockImplementation(() => {
          throw new Error('QuotaExceededError');
        });
      expect(() => saveLastViewedField('tenant-a', 'field-123')).not.toThrow();
      setItemSpy.mockRestore();
    });

    it('returns null and does not throw if localStorage.getItem throws', () => {
      const getItemSpy = vi
        .spyOn(window.localStorage, 'getItem')
        .mockImplementation(() => {
          throw new Error('SecurityError');
        });
      expect(getLastViewedField('tenant-a')).toBeNull();
      getItemSpy.mockRestore();
    });

    it('does not throw if localStorage.removeItem throws', () => {
      const removeItemSpy = vi
        .spyOn(window.localStorage, 'removeItem')
        .mockImplementation(() => {
          throw new Error('SecurityError');
        });
      expect(() => clearLastViewedField('tenant-a')).not.toThrow();
      removeItemSpy.mockRestore();
    });
  });
});
