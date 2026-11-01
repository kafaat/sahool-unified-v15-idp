import { describe, expect, it, vi, beforeEach } from 'vitest';

// Mock the logger to silence the production error log path
vi.mock('@/lib/logger', () => ({
  logger: { production: vi.fn(), error: vi.fn(), warn: vi.fn(), info: vi.fn() },
}));

// Mock the actual request boundary; missing tenant context must stop here.
const { client, getCookie } = vi.hoisted(() => ({
  client: { post: vi.fn(), put: vi.fn(), delete: vi.fn(), get: vi.fn() },
  getCookie: vi.fn(),
}));
vi.mock('@/lib/api/factory', () => ({ createApiClient: () => client }));
vi.mock('js-cookie', () => ({ default: { get: getCookie } }));

import { FIELD_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
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
    getCookie.mockReset();
    client.post.mockResolvedValue({ data: { id: 'field-1' } });
    client.put.mockResolvedValue({ data: { id: 'field-1' } });
  });

  it.each([undefined, ''])('createField rejects missing tenant %j without a cookie fallback', async (tenantId) => {
    await expect(fieldsApi.createField(sampleField, tenantId)).rejects.toThrow(
      /Authentication required/i,
    );
    expect(client.post).not.toHaveBeenCalled();
    expect(client.put).not.toHaveBeenCalled();
  });

  it.each([undefined, ''])('updateField rejects missing tenant %j without a cookie fallback', async (tenantId) => {
    await expect(fieldsApi.updateField('field-1', sampleField, tenantId)).rejects.toThrow(
      /Authentication required/i,
    );
    expect(client.post).not.toHaveBeenCalled();
    expect(client.put).not.toHaveBeenCalled();
  });

  it('uses the explicit tenant from auth state when a fallback cookie also exists', async () => {
    getCookie.mockReturnValue('cookie-tenant');

    await fieldsApi.createField(sampleField, 'auth-tenant');

    expect(client.post).toHaveBeenCalledExactlyOnceWith(
      FIELD_ENDPOINTS.CREATE,
      expect.objectContaining({ tenantId: 'auth-tenant', name: sampleField.name }),
    );
  });

  it('uses the tenant cookie while auth state is temporarily unavailable during creation', async () => {
    getCookie.mockImplementation((name: string) => name === 'tenant_id' ? 'cookie-tenant' : undefined);

    await fieldsApi.createField(sampleField, undefined);

    expect(getCookie).toHaveBeenCalledWith('tenant_id');
    expect(client.post).toHaveBeenCalledExactlyOnceWith(
      FIELD_ENDPOINTS.CREATE,
      expect.objectContaining({ tenantId: 'cookie-tenant' }),
    );
  });

  it('uses the same cookie fallback during updates', async () => {
    getCookie.mockImplementation((name: string) => name === 'tenant_id' ? 'cookie-tenant' : undefined);

    await fieldsApi.updateField('field-1', sampleField, undefined);

    expect(client.put).toHaveBeenCalledExactlyOnceWith(
      buildUrl(FIELD_ENDPOINTS.UPDATE, { fieldId: 'field-1' }),
      expect.objectContaining({ tenantId: 'cookie-tenant' }),
    );
  });
});
