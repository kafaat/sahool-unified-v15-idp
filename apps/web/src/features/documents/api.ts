/**
 * Documents Feature - API Layer
 * طبقة API لميزة الوثائق
 */

import { DOCUMENT_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type { Document, DocumentFilters, DocumentStats } from './types';

const api = createApiClient();

export const documentsApi = {
  getDocuments: async (filters?: DocumentFilters): Promise<Document[]> => {
    return safeFetch(DOCUMENT_ENDPOINTS.LIST, async () => {
      const params = new URLSearchParams();
      if (filters?.category) params.set('category', filters.category);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.farmId) params.set('farm_id', filters.farmId);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${DOCUMENT_ENDPOINTS.LIST}?${params.toString()}`);
      const data = extractData<Document[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getDocumentById: async (id: string): Promise<Document> => {
    return safeFetch(DOCUMENT_ENDPOINTS.GET, async () => {
      const response = await api.get(buildUrl(DOCUMENT_ENDPOINTS.GET, { documentId: id }));
      return extractData<Document>(response);
    });
  },

  uploadDocument: async (data: FormData): Promise<Document> => {
    return safeFetch(DOCUMENT_ENDPOINTS.UPLOAD, async () => {
      const response = await api.post(DOCUMENT_ENDPOINTS.UPLOAD, data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return extractData<Document>(response);
    });
  },

  deleteDocument: async (id: string): Promise<void> => {
    return safeFetch(DOCUMENT_ENDPOINTS.DELETE, async () => {
      await api.delete(buildUrl(DOCUMENT_ENDPOINTS.DELETE, { documentId: id }));
    });
  },

  downloadDocument: async (id: string): Promise<Blob> => {
    return safeFetch(DOCUMENT_ENDPOINTS.GET, async () => {
      const response = await api.get(
        `${buildUrl(DOCUMENT_ENDPOINTS.GET, { documentId: id })}/download`,
        {
          responseType: 'blob',
        }
      );
      return response.data;
    });
  },

  getStats: async (): Promise<DocumentStats> => {
    return safeFetch(DOCUMENT_ENDPOINTS.LIST, async () => {
      const response = await api.get(`${DOCUMENT_ENDPOINTS.LIST}/stats`);
      return extractData<DocumentStats>(response);
    });
  },
};
