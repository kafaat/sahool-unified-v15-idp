/**
 * Tests for field management hooks
 * اختبارات خطافات إدارة الحقول
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { invalidateQueries } from '../use-api-query';

vi.mock('@/lib/api', () => ({
  fetchFarms: vi.fn().mockResolvedValue([
    { id: 'f1', name: 'Farm 1', area: 5.2, status: 'active' },
    { id: 'f2', name: 'Farm 2', area: 3.8, status: 'active' },
  ]),
  fetchFarmById: vi
    .fn()
    .mockResolvedValue({ id: 'f1', name: 'Farm 1', area: 5.2, status: 'active' }),
  getSatelliteTimeseries: vi.fn().mockResolvedValue([
    { date: '2026-01-01', ndvi: 0.72 },
    { date: '2026-01-15', ndvi: 0.68 },
  ]),
  getSatelliteIndices: vi.fn().mockResolvedValue({ ndvi: 0.72, evi: 0.45 }),
  fetchFieldIntelligence: vi.fn().mockResolvedValue({ health: 'good' }),
  apiClient: {
    post: vi.fn().mockResolvedValue({ data: { id: 'new-1', name: 'New Field' } }),
    put: vi.fn().mockResolvedValue({ data: { id: 'f1', name: 'Updated' } }),
    delete: vi.fn().mockResolvedValue({ data: { success: true } }),
  },
  API_URLS: {
    fieldCore: 'http://localhost:3000',
    fields: {
      list: 'http://localhost:3000/api/v1/fields',
      byId: (id: string) => `http://localhost:3000/api/v1/fields/${id}`,
      create: 'http://localhost:3000/api/v1/fields',
      update: (id: string) => `http://localhost:3000/api/v1/fields/${id}`,
      delete: (id: string) => `http://localhost:3000/api/v1/fields/${id}`,
    },
  },
}));

vi.mock('@/config/api', () => ({
  API_URLS: {
    fieldCore: 'http://localhost:3000',
    fields: {
      list: 'http://localhost:3000/api/v1/fields',
      byId: (id: string) => `http://localhost:3000/api/v1/fields/${id}`,
      create: 'http://localhost:3000/api/v1/fields',
      update: (id: string) => `http://localhost:3000/api/v1/fields/${id}`,
      delete: (id: string) => `http://localhost:3000/api/v1/fields/${id}`,
    },
  },
}));

import {
  useFields,
  useField,
  useFieldNDVI,
  useFieldIndices,
  useFieldIntelligence,
  useCreateField,
  useUpdateField,
  useDeleteField,
} from '../use-fields';

beforeEach(() => {
  invalidateQueries('');
});

describe('useFields', () => {
  it('fetches list of fields', async () => {
    const { result } = renderHook(() => useFields());

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0]).toHaveProperty('id', 'f1');
  });
});

describe('useField', () => {
  it('fetches a single field by ID', async () => {
    const { result } = renderHook(() => useField('f1'));

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual({ id: 'f1', name: 'Farm 1', area: 5.2, status: 'active' });
  });

  it('does not fetch when ID is empty', () => {
    const { result } = renderHook(() => useField(''));

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
  });
});

describe('useFieldNDVI', () => {
  it('fetches NDVI timeseries for a field', async () => {
    const { result } = renderHook(() => useFieldNDVI('f1'));

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0]).toHaveProperty('ndvi');
  });

  it('does not fetch when fieldId is empty', () => {
    const { result } = renderHook(() => useFieldNDVI(''));
    expect(result.current.isLoading).toBe(false);
  });
});

describe('useFieldIndices', () => {
  it('fetches vegetation indices', async () => {
    const { result } = renderHook(() => useFieldIndices('f1'));

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual({ ndvi: 0.72, evi: 0.45 });
  });
});

describe('useFieldIntelligence', () => {
  it('fetches field intelligence data', async () => {
    const { result } = renderHook(() => useFieldIntelligence('f1'));

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual({ health: 'good' });
  });
});

describe('useCreateField', () => {
  it('creates a new field', async () => {
    const { result } = renderHook(() => useCreateField());

    await act(async () => {
      await result.current.mutate({ name: 'New Field' });
    });

    expect(result.current.isSuccess).toBe(true);
  });
});

describe('useUpdateField', () => {
  it('updates a field', async () => {
    const { result } = renderHook(() => useUpdateField());

    await act(async () => {
      await result.current.mutate({ id: 'f1', data: { name: 'Updated' } });
    });

    expect(result.current.isSuccess).toBe(true);
  });
});

describe('useDeleteField', () => {
  it('deletes a field', async () => {
    const { result } = renderHook(() => useDeleteField());

    await act(async () => {
      await result.current.mutate('f1');
    });

    expect(result.current.isSuccess).toBe(true);
  });
});
