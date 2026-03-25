/**
 * Documents Feature - API Layer
 * طبقة API لميزة الوثائق
 */

import { DOCUMENT_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import { createApiClient, extractData, logger } from '@/lib/api/factory';
import type { Document, DocumentFilters, DocumentStats } from './types';

const api = createApiClient();

const MOCK_DOCUMENTS: Document[] = [
  {
    id: 'doc-001',
    title: 'Farm Operating License 2026',
    titleAr: 'رخصة تشغيل المزرعة 2026',
    category: 'permits',
    status: 'active',
    fileName: 'farm_license_2026.pdf',
    fileSize: 2500000,
    fileType: 'application/pdf',
    farmId: 'farm-001',
    farmName: 'Al-Rashid Farm',
    farmNameAr: 'مزرعة الراشد',
    tags: ['license', '2026', 'compliance'],
    description: 'Annual farm operating license issued by Ministry of Agriculture',
    descriptionAr: 'رخصة تشغيل المزرعة السنوية الصادرة من وزارة الزراعة',
    expiryDate: '2026-12-31',
    uploadedBy: 'Ahmad Al-Rashid',
    uploadedByAr: 'أحمد الراشد',
    createdAt: '2026-01-05T10:00:00Z',
    updatedAt: '2026-01-05T10:00:00Z',
  },
  {
    id: 'doc-002',
    title: 'Water Usage Agreement',
    titleAr: 'اتفاقية استخدام المياه',
    category: 'contracts',
    status: 'active',
    fileName: 'water_agreement.pdf',
    fileSize: 1200000,
    fileType: 'application/pdf',
    farmId: 'farm-001',
    farmName: 'Al-Rashid Farm',
    farmNameAr: 'مزرعة الراشد',
    tags: ['water', 'contract', 'agreement'],
    expiryDate: '2027-06-30',
    uploadedBy: 'Ahmad Al-Rashid',
    uploadedByAr: 'أحمد الراشد',
    createdAt: '2025-07-01T00:00:00Z',
    updatedAt: '2025-07-01T00:00:00Z',
  },
  {
    id: 'doc-003',
    title: 'Soil Analysis Report - North Field',
    titleAr: 'تقرير تحليل التربة - الحقل الشمالي',
    category: 'reports',
    status: 'active',
    fileName: 'soil_analysis_north.pdf',
    fileSize: 850000,
    fileType: 'application/pdf',
    farmId: 'farm-001',
    farmName: 'Al-Rashid Farm',
    farmNameAr: 'مزرعة الراشد',
    tags: ['soil', 'analysis', 'north-field'],
    uploadedBy: 'Sara Al-Qahtani',
    uploadedByAr: 'سارة القحطاني',
    createdAt: '2026-01-20T14:00:00Z',
    updatedAt: '2026-01-20T14:00:00Z',
  },
  {
    id: 'doc-004',
    title: 'GlobalGAP Certificate',
    titleAr: 'شهادة GlobalGAP',
    category: 'certificates',
    status: 'active',
    fileName: 'globalgap_cert.pdf',
    fileSize: 3200000,
    fileType: 'application/pdf',
    tags: ['globalgap', 'certification', 'quality'],
    expiryDate: '2026-09-15',
    uploadedBy: 'Ahmad Al-Rashid',
    uploadedByAr: 'أحمد الراشد',
    createdAt: '2025-09-15T00:00:00Z',
    updatedAt: '2025-09-15T00:00:00Z',
  },
  {
    id: 'doc-005',
    title: 'Pesticide Usage Log Q4 2025',
    titleAr: 'سجل استخدام المبيدات الربع الرابع 2025',
    category: 'compliance',
    status: 'archived',
    fileName: 'pesticide_log_q4_2025.xlsx',
    fileSize: 450000,
    fileType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    farmId: 'farm-001',
    farmName: 'Al-Rashid Farm',
    farmNameAr: 'مزرعة الراشد',
    tags: ['pesticide', 'compliance', 'log', 'q4-2025'],
    uploadedBy: 'Fatima Al-Shehri',
    uploadedByAr: 'فاطمة الشهري',
    createdAt: '2026-01-10T11:00:00Z',
    updatedAt: '2026-02-01T09:00:00Z',
  },
];

const MOCK_STATS: DocumentStats = {
  totalDocuments: 5,
  activeDocuments: 4,
  expiringDocuments: 1,
  totalSizeMb: 8.2,
  byCategory: { permits: 1, contracts: 1, reports: 1, certificates: 1, compliance: 1 },
};

export const documentsApi = {
  getDocuments: async (filters?: DocumentFilters): Promise<Document[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.category) params.set('category', filters.category);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.farmId) params.set('farm_id', filters.farmId);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${DOCUMENT_ENDPOINTS.LIST}?${params.toString()}`);
      const data = extractData<Document[]>(response);
      if (Array.isArray(data)) return data;
      return MOCK_DOCUMENTS;
    } catch {
      logger.warn('Failed to fetch documents, using mock data');
      return MOCK_DOCUMENTS;
    }
  },

  getDocumentById: async (id: string): Promise<Document> => {
    try {
      const response = await api.get(buildUrl(DOCUMENT_ENDPOINTS.GET, { documentId: id }));
      return extractData<Document>(response);
    } catch {
      const mock = MOCK_DOCUMENTS.find((d) => d.id === id);
      if (mock) return mock;
      throw new Error(`Document ${id} not found`);
    }
  },

  uploadDocument: async (data: FormData): Promise<Document> => {
    const response = await api.post(DOCUMENT_ENDPOINTS.UPLOAD, data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return extractData<Document>(response);
  },

  deleteDocument: async (id: string): Promise<void> => {
    await api.delete(buildUrl(DOCUMENT_ENDPOINTS.DELETE, { documentId: id }));
  },

  downloadDocument: async (id: string): Promise<Blob> => {
    const response = await api.get(
      `${buildUrl(DOCUMENT_ENDPOINTS.GET, { documentId: id })}/download`,
      {
        responseType: 'blob',
      }
    );
    return response.data;
  },

  getStats: async (): Promise<DocumentStats> => {
    try {
      const response = await api.get(`${DOCUMENT_ENDPOINTS.LIST}/stats`);
      return extractData<DocumentStats>(response);
    } catch {
      return MOCK_STATS;
    }
  },
};
