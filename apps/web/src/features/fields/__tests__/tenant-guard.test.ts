import { describe, expect, it, vi, beforeEach } from 'vitest';

// Mock the logger to silence the production error log path
vi.mock('@/lib/logger', () => ({
  logger: { production: vi.fn(), error: vi.fn(), warn: vi.fn(), info: vi.fn() },
}));

// Mock the underlying axios client so the tests don't hit the network.
vi.mock('@/lib/api/client', () => ({
  api: {
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    get: vi.fn(),
  },
}));

import { fieldsApi } from '../api';
import type { FieldFormData } from '../types';

const sampleField: FieldFormData = {
  name: 'Field 1',
  nameAr: 'حقل 1',
  crop: 'wheat',
  cropAr: 'قمح',
  area: 10,
  polygon: {
    type: 'Polygon',
    coordinates: [[[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8], [46.7, 24.7]]],
  },
  description: 'desc',
  descriptionAr: 'وصف',
};

describe('Fields API — tenant guard (P0 fix)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('createField rejects when tenantId is undefined (no silent default-tenant)', async () => {
    await expect(fieldsApi.createField(sampleField, undefined)).rejects.toThrow(
      /tenantId is required/i,
    );
  });

  it('createField rejects when tenantId is empty string', async () => {
    await expect(fieldsApi.createField(sampleField, '')).rejects.toThrow(
      /tenantId is required/i,
    );
  });

  it('updateField rejects when tenantId is undefined', async () => {
    await expect(fieldsApi.updateField('field-1', sampleField, undefined)).rejects.toThrow(
      /tenantId is required/i,
    );
  });
});
