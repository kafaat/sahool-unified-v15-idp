import { describe, expect, it, vi, beforeEach } from 'vitest';

// Mock the logger to silence the production error log path
vi.mock('@/lib/logger', () => ({
  logger: { production: vi.fn(), error: vi.fn(), warn: vi.fn(), info: vi.fn() },
}));

// Mock the actual client boundary and cookie fallback; no request may escape.
const { client, getCookie } = vi.hoisted(() => ({
  client: { post: vi.fn(), put: vi.fn(), delete: vi.fn(), get: vi.fn() },
  getCookie: vi.fn(),
}));
vi.mock('@/lib/api/factory', () => ({ createApiClient: () => client }));
vi.mock('js-cookie', () => ({ default: { get: getCookie } }));

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
    getCookie.mockReturnValue(undefined);
  });

  it('createField rejects when tenantId is undefined (no silent default-tenant)', async () => {
    await expect(fieldsApi.createField(sampleField, undefined)).rejects.toThrow(
      /Authentication required/i,
    );
    expect(client.post).not.toHaveBeenCalled();
    expect(client.put).not.toHaveBeenCalled();
  });

  it('createField rejects when tenantId is empty string', async () => {
    await expect(fieldsApi.createField(sampleField, '')).rejects.toThrow(
      /Authentication required/i,
    );
    expect(client.post).not.toHaveBeenCalled();
    expect(client.put).not.toHaveBeenCalled();
  });

  it('updateField rejects when tenantId is undefined', async () => {
    await expect(fieldsApi.updateField('field-1', sampleField, undefined)).rejects.toThrow(
      /Authentication required/i,
    );
    expect(client.post).not.toHaveBeenCalled();
    expect(client.put).not.toHaveBeenCalled();
  });
});
