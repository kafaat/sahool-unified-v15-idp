/**
 * Documents Feature - API Layer
 * طبقة API لميزة الوثائق
 *
 * NOTE: DOCUMENT_ENDPOINTS is currently marked @deprecated in contracts
 * because the backend service is not yet implemented. These calls will
 * return empty data via safeFetch fallback until the backend lands.
 */

import { DOCUMENT_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type { Document, DocumentFilters, DocumentStats } from './types';

const api = createApiClient();

// Client-side pagination defaults (backend may or may not support these)
const DEFAULT_PAGE_SIZE = 50;
const MAX_PAGE_SIZE = 200;

export const documentsApi = {
  getDocuments: async (filters?: DocumentFilters): Promise<Document[]> => {
    return safeFetch(DOCUMENT_ENDPOINTS.LIST, async () => {
      const params = new URLSearchParams();
      if (filters?.category) params.set('category', filters.category);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.farmId) params.set('farm_id', filters.farmId);
      if (filters?.search) params.set('search', filters.search);
      // Enforce a bounded page size to prevent unbounded fetches
      params.set('limit', String(DEFAULT_PAGE_SIZE));
      params.set('offset', '0');
      const response = await api.get(`${DOCUMENT_ENDPOINTS.LIST}?${params.toString()}`);
      const data = extractData<Document[]>(response);
      if (Array.isArray(data)) return data.slice(0, MAX_PAGE_SIZE);
      return [];
    });
  },

  getDocumentById: async (id: string): Promise<Document> => {
    const endpoint = buildUrl(DOCUMENT_ENDPOINTS.GET, { documentId: id });
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return extractData<Document>(response);
    });
  },

  uploadDocument: async (data: FormData): Promise<Document> => {
    return safeFetch(DOCUMENT_ENDPOINTS.UPLOAD, async () => {
      // NOTE: Do NOT manually set Content-Type for multipart/form-data — the
      // browser must set the boundary. Overriding it breaks the upload.
      const response = await api.post(DOCUMENT_ENDPOINTS.UPLOAD, data);
      return extractData<Document>(response);
    });
  },

  deleteDocument: async (id: string): Promise<void> => {
    const endpoint = buildUrl(DOCUMENT_ENDPOINTS.DELETE, { documentId: id });
    return safeFetch(endpoint, async () => {
      await api.delete(endpoint);
    });
  },

  downloadDocument: async (id: string): Promise<Blob> => {
    const endpoint = `${buildUrl(DOCUMENT_ENDPOINTS.GET, { documentId: id })}/download`;
    // Download hits a protected endpoint; the unified client attaches the JWT
    // automatically. Do NOT expose a plain file URL to <a href> — always
    // fetch the blob through the authenticated client.
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint, { responseType: 'blob' });
      return response.data;
    });
  },

  getStats: async (): Promise<DocumentStats> => {
    const endpoint = `${DOCUMENT_ENDPOINTS.LIST}/stats`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return extractData<DocumentStats>(response);
    });
  },
};
