/**
 * Crop Insurance Feature - API Layer
 * طبقة API لميزة التأمين على المحاصيل
 */

import { API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  InsurancePolicy,
  InsuranceClaim,
  InsuranceProvider,
  InsuranceStats,
  FieldRiskProfile,
  PolicyPremium,
  PolicyFilters,
  ClaimFilters,
  PolicyFormData,
  ClaimFormData,
} from './types';

const api = createApiClient();
const BASE = `${API_PREFIX}/crop-insurance`;

export const cropInsuranceApi = {
  getPolicies: async (filters?: PolicyFilters): Promise<InsurancePolicy[]> => {
    return safeFetch(`${BASE}/policies`, async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.insuranceType) params.set('insurance_type', filters.insuranceType);
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${BASE}/policies?${params.toString()}`);
      const data = extractData<InsurancePolicy[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getPolicy: async (id: string): Promise<InsurancePolicy> => {
    return safeFetch(`${BASE}/policies/${id}`, async () => {
      const response = await api.get(`${BASE}/policies/${encodeURIComponent(id)}`);
      return extractData<InsurancePolicy>(response);
    });
  },

  createPolicy: async (data: PolicyFormData): Promise<InsurancePolicy> => {
    return safeFetch(`${BASE}/policies`, async () => {
      const response = await api.post(`${BASE}/policies`, data);
      return extractData<InsurancePolicy>(response);
    });
  },

  updatePolicy: async (
    id: string,
    data: Partial<PolicyFormData>,
  ): Promise<InsurancePolicy> => {
    return safeFetch(`${BASE}/policies/${id}`, async () => {
      const response = await api.put(
        `${BASE}/policies/${encodeURIComponent(id)}`,
        data,
      );
      return extractData<InsurancePolicy>(response);
    });
  },

  getProviders: async (): Promise<InsuranceProvider[]> => {
    return safeFetch(`${BASE}/providers`, async () => {
      const response = await api.get(`${BASE}/providers`);
      const data = extractData<InsuranceProvider[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getClaims: async (filters?: ClaimFilters): Promise<InsuranceClaim[]> => {
    return safeFetch(`${BASE}/claims`, async () => {
      const params = new URLSearchParams();
      if (filters?.claimStatus) params.set('claim_status', filters.claimStatus);
      if (filters?.claimType) params.set('claim_type', filters.claimType);
      if (filters?.policyId) params.set('policy_id', filters.policyId);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${BASE}/claims?${params.toString()}`);
      const data = extractData<InsuranceClaim[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getClaim: async (id: string): Promise<InsuranceClaim> => {
    return safeFetch(`${BASE}/claims/${id}`, async () => {
      const response = await api.get(`${BASE}/claims/${encodeURIComponent(id)}`);
      return extractData<InsuranceClaim>(response);
    });
  },

  submitClaim: async (data: ClaimFormData): Promise<InsuranceClaim> => {
    return safeFetch(`${BASE}/claims`, async () => {
      const response = await api.post(`${BASE}/claims`, data);
      return extractData<InsuranceClaim>(response);
    });
  },

  uploadEvidence: async (claimId: string, files: File[]): Promise<void> => {
    return safeFetch(`${BASE}/claims/${claimId}/evidence`, async () => {
      const formData = new FormData();
      for (const file of files) {
        formData.append('files', file);
      }
      await api.post(
        `${BASE}/claims/${encodeURIComponent(claimId)}/evidence`,
        formData,
      );
    });
  },

  getRiskProfile: async (fieldId: string): Promise<FieldRiskProfile> => {
    return safeFetch(`${BASE}/risk-profile/${fieldId}`, async () => {
      const response = await api.get(
        `${BASE}/risk-profile/${encodeURIComponent(fieldId)}`,
      );
      return extractData<FieldRiskProfile>(response);
    });
  },

  calculatePremium: async (
    policyData: PolicyFormData,
  ): Promise<PolicyPremium> => {
    return safeFetch(`${BASE}/premium/calculate`, async () => {
      const response = await api.post(`${BASE}/premium/calculate`, policyData);
      return extractData<PolicyPremium>(response);
    });
  },

  getStats: async (): Promise<InsuranceStats> => {
    return safeFetch(`${BASE}/stats`, async () => {
      const response = await api.get(`${BASE}/stats`);
      return extractData<InsuranceStats>(response);
    });
  },
};
