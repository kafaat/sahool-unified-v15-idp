/**
 * Compliance Feature - API Layer
 * طبقة API لميزة الامتثال والجودة
 */

import { COMPLIANCE_ENDPOINTS, API_PREFIX } from "@sahool/shared-types/contracts";
import { createApiClient, logger } from "@/lib/api/factory";
import type {
  ComplianceItem,
  Certification,
  AuditReport,
  ComplianceFilters,
  ComplianceStats,
} from "./types";

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: "Network error. Using offline data.",
    ar: "خطأ في الاتصال. استخدام البيانات المحفوظة.",
  },
  FETCH_FAILED: {
    en: "Failed to fetch compliance data.",
    ar: "فشل في جلب بيانات الامتثال.",
  },
};

const MOCK_COMPLIANCE: ComplianceItem[] = [
  {
    id: "1",
    category: "Food Safety",
    categoryAr: "سلامة الغذاء",
    requirement: "Pesticide Residue Limits",
    requirementAr: "حدود بقايا المبيدات",
    status: "compliant",
    score: 95,
    maxScore: 100,
    lastAudit: "2026-01-15",
    nextAudit: "2026-04-15",
    metadata: {},
    createdAt: "2025-01-01T10:00:00Z",
    updatedAt: "2026-01-15T14:30:00Z",
  },
  {
    id: "2",
    category: "Worker Safety",
    categoryAr: "سلامة العمال",
    requirement: "PPE Requirements",
    requirementAr: "متطلبات معدات الحماية",
    status: "compliant",
    score: 100,
    maxScore: 100,
    lastAudit: "2026-01-10",
    nextAudit: "2026-04-10",
    metadata: {},
    createdAt: "2025-01-01T10:00:00Z",
    updatedAt: "2026-01-10T11:00:00Z",
  },
  {
    id: "3",
    category: "Environment",
    categoryAr: "البيئة",
    requirement: "Water Usage Records",
    requirementAr: "سجلات استخدام المياه",
    status: "partial",
    score: 75,
    maxScore: 100,
    lastAudit: "2026-01-12",
    nextAudit: "2026-04-12",
    notes: "Missing irrigation logs for December",
    notesAr: "سجلات الري مفقودة لشهر ديسمبر",
    metadata: {},
    createdAt: "2025-01-01T10:00:00Z",
    updatedAt: "2026-01-12T16:00:00Z",
  },
  {
    id: "4",
    category: "Traceability",
    categoryAr: "التتبع",
    requirement: "Batch Identification",
    requirementAr: "تعريف الدفعات",
    status: "compliant",
    score: 92,
    maxScore: 100,
    lastAudit: "2026-01-08",
    nextAudit: "2026-04-08",
    metadata: {},
    createdAt: "2025-01-01T10:00:00Z",
    updatedAt: "2026-01-08T09:00:00Z",
  },
  {
    id: "5",
    category: "Documentation",
    categoryAr: "التوثيق",
    requirement: "Training Records",
    requirementAr: "سجلات التدريب",
    status: "pending_review",
    score: 85,
    maxScore: 100,
    lastAudit: "2026-01-20",
    nextAudit: "2026-04-20",
    metadata: {},
    createdAt: "2025-01-01T10:00:00Z",
    updatedAt: "2026-01-20T10:00:00Z",
  },
];

const MOCK_CERTIFICATIONS: Certification[] = [
  {
    id: "1",
    name: "GlobalGAP",
    nameAr: "جلوبال جاب",
    type: "globalgap",
    issuer: "GLOBALG.A.P.",
    issuerAr: "منظمة جلوبال جاب",
    status: "active",
    certificateNumber: "GGN-12345-6789",
    issueDate: "2025-06-01",
    expiryDate: "2026-06-01",
    metadata: {},
  },
  {
    id: "2",
    name: "Organic Certification",
    nameAr: "شهادة العضوية",
    type: "organic",
    issuer: "Saudi Organic Authority",
    issuerAr: "هيئة الزراعة العضوية",
    status: "active",
    certificateNumber: "ORG-SA-2025-001",
    issueDate: "2025-03-15",
    expiryDate: "2026-03-15",
    metadata: {},
  },
  {
    id: "3",
    name: "ISO 22000",
    nameAr: "آيزو 22000",
    type: "iso",
    issuer: "SGS",
    issuerAr: "إس جي إس",
    status: "pending",
    certificateNumber: "",
    issueDate: "",
    expiryDate: "",
    metadata: {},
  },
];

const MOCK_STATS: ComplianceStats = {
  overallScore: 89,
  totalRequirements: 5,
  compliantCount: 3,
  partialCount: 1,
  nonCompliantCount: 0,
  pendingAudits: 1,
  activeCertifications: 2,
  expiringCertifications: 1,
  openFindings: 2,
  byCategory: {
    "Food Safety": { score: 95, total: 100 },
    "Worker Safety": { score: 100, total: 100 },
    Environment: { score: 75, total: 100 },
    Traceability: { score: 92, total: 100 },
    Documentation: { score: 85, total: 100 },
  },
};

export const complianceApi = {
  getCompliance: async (filters?: ComplianceFilters): Promise<ComplianceItem[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.category) params.set("category", filters.category);
      if (filters?.status) params.set("status", filters.status);
      if (filters?.search) params.set("search", filters.search);

      const response = await api.get(`${COMPLIANCE_ENDPOINTS.CHECKLISTS}?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn("API returned unexpected format, using mock data");
      return MOCK_COMPLIANCE;
    } catch (error) {
      logger.warn("Failed to fetch compliance data, using mock data:", error);
      return MOCK_COMPLIANCE;
    }
  },

  getComplianceById: async (id: string): Promise<ComplianceItem> => {
    try {
      const response = await api.get(`${API_PREFIX}/compliance/${id}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch compliance item ${id}, using mock data:`, error);
      const mockItem = MOCK_COMPLIANCE.find((c) => c.id === id);
      if (mockItem) return mockItem;
      throw new Error(`Compliance item with ID ${id} not found`);
    }
  },

  updateCompliance: async (id: string, data: Partial<ComplianceItem>): Promise<ComplianceItem> => {
    try {
      const response = await api.put(`${API_PREFIX}/compliance/${id}`, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update compliance item ${id}:`, error);
      throw error;
    }
  },

  getCertifications: async (): Promise<Certification[]> => {
    try {
      const response = await api.get(COMPLIANCE_ENDPOINTS.CERTIFICATES);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      return MOCK_CERTIFICATIONS;
    } catch (error) {
      logger.warn("Failed to fetch certifications, using mock data:", error);
      return MOCK_CERTIFICATIONS;
    }
  },

  getCertificationById: async (id: string): Promise<Certification> => {
    try {
      const response = await api.get(`${COMPLIANCE_ENDPOINTS.CERTIFICATES}/${id}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch certification ${id}, using mock data:`, error);
      const mockCert = MOCK_CERTIFICATIONS.find((c) => c.id === id);
      if (mockCert) return mockCert;
      throw new Error(`Certification with ID ${id} not found`);
    }
  },

  getAuditReports: async (): Promise<AuditReport[]> => {
    try {
      const response = await api.get(COMPLIANCE_ENDPOINTS.AUDITS);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Failed to fetch audit reports:", error);
      return [];
    }
  },

  createAuditReport: async (data: Partial<AuditReport>): Promise<AuditReport> => {
    try {
      const response = await api.post(COMPLIANCE_ENDPOINTS.AUDITS, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to create audit report:", error);
      throw error;
    }
  },

  getStats: async (): Promise<ComplianceStats> => {
    try {
      const response = await api.get(`${API_PREFIX}/compliance/stats`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Failed to fetch compliance stats, using mock data:", error);
      return MOCK_STATS;
    }
  },
};
