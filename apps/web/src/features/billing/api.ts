/**
 * Billing Feature - API Layer
 * طبقة API لميزة الفوترة - Real API with mock fallback
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  BillingPlan,
  Subscription,
  Invoice,
  Payment,
  UsageRecord,
  QuotaInfo,
  CreatePaymentRequest,
  UpdateSubscriptionRequest,
} from './types';

const api = createApiClient();

const BILLING_BASE = '/api/v1';

export const billingApi = {
  // =========================================================================
  // Plans - الخطط
  // =========================================================================

  /**
   * Fetch all billing plans
   * جلب جميع خطط الفوترة
   */
  getPlans: async (): Promise<BillingPlan[]> => {
    return safeFetch(`${BILLING_BASE}/plans`, async () => {
      const response = await api.get(`${BILLING_BASE}/plans`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      if (data?.plans && Array.isArray(data.plans)) return data.plans;
      return [];
    });
  },

  /**
   * Fetch a single plan by ID
   * جلب خطة واحدة بالمعرف
   */
  getPlanById: async (planId: string): Promise<BillingPlan> => {
    return safeFetch(`${BILLING_BASE}/plans/${planId}`, async () => {
      const response = await api.get(`${BILLING_BASE}/plans/${planId}`);
      return response.data.data || response.data;
    });
  },

  // =========================================================================
  // Subscriptions - الاشتراكات
  // =========================================================================

  /**
   * Fetch tenant subscription
   * جلب اشتراك المستأجر
   */
  getSubscription: async (tenantId: string): Promise<Subscription> => {
    return safeFetch(`${BILLING_BASE}/tenants/${tenantId}/subscription`, async () => {
      const response = await api.get(`${BILLING_BASE}/tenants/${tenantId}/subscription`);
      return response.data.data || response.data;
    });
  },

  /**
   * Update tenant subscription (change plan)
   * تحديث اشتراك المستأجر (تغيير الخطة)
   */
  updateSubscription: async (
    tenantId: string,
    data: UpdateSubscriptionRequest
  ): Promise<Subscription> => {
    return safeFetch(`${BILLING_BASE}/tenants/${tenantId}/subscription`, async () => {
      const response = await api.patch(`${BILLING_BASE}/tenants/${tenantId}/subscription`, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Cancel tenant subscription
   * إلغاء اشتراك المستأجر
   */
  cancelSubscription: async (tenantId: string): Promise<Subscription> => {
    return safeFetch(`${BILLING_BASE}/tenants/${tenantId}/cancel`, async () => {
      const response = await api.post(`${BILLING_BASE}/tenants/${tenantId}/cancel`);
      return response.data.data || response.data;
    });
  },

  // =========================================================================
  // Usage & Quota - الاستخدام والحصص
  // =========================================================================

  /**
   * Fetch tenant usage records
   * جلب سجلات استخدام المستأجر
   */
  getUsage: async (tenantId: string): Promise<UsageRecord[]> => {
    return safeFetch(`${BILLING_BASE}/tenants/${tenantId}/usage`, async () => {
      const response = await api.get(`${BILLING_BASE}/tenants/${tenantId}/usage`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      if (data?.usage && Array.isArray(data.usage)) return data.usage;
      return [];
    });
  },

  /**
   * Fetch tenant quota information
   * جلب معلومات حصة المستأجر
   */
  getQuota: async (tenantId: string): Promise<QuotaInfo> => {
    return safeFetch(`${BILLING_BASE}/tenants/${tenantId}/quota`, async () => {
      const response = await api.get(`${BILLING_BASE}/tenants/${tenantId}/quota`);
      return response.data.data || response.data;
    });
  },

  // =========================================================================
  // Invoices - الفواتير
  // =========================================================================

  /**
   * Fetch tenant invoices
   * جلب فواتير المستأجر
   */
  getInvoices: async (tenantId: string): Promise<Invoice[]> => {
    return safeFetch(`${BILLING_BASE}/tenants/${tenantId}/invoices`, async () => {
      const response = await api.get(`${BILLING_BASE}/tenants/${tenantId}/invoices`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      if (data?.invoices && Array.isArray(data.invoices)) return data.invoices;
      return [];
    });
  },

  /**
   * Fetch a single invoice by ID
   * جلب فاتورة واحدة بالمعرف
   */
  getInvoiceById: async (invoiceId: string): Promise<Invoice> => {
    return safeFetch(`${BILLING_BASE}/invoices/${invoiceId}`, async () => {
      const response = await api.get(`${BILLING_BASE}/invoices/${invoiceId}`);
      return response.data.data || response.data;
    });
  },

  /**
   * Generate a new invoice for tenant
   * توليد فاتورة جديدة للمستأجر
   */
  generateInvoice: async (tenantId: string): Promise<Invoice> => {
    return safeFetch(`${BILLING_BASE}/tenants/${tenantId}/invoices/generate`, async () => {
      const response = await api.post(`${BILLING_BASE}/tenants/${tenantId}/invoices/generate`);
      return response.data.data || response.data;
    });
  },

  // =========================================================================
  // Payments - المدفوعات
  // =========================================================================

  /**
   * Create a new payment
   * إنشاء دفعة جديدة
   */
  createPayment: async (data: CreatePaymentRequest): Promise<Payment> => {
    return safeFetch(`${BILLING_BASE}/payments`, async () => {
      const response = await api.post(`${BILLING_BASE}/payments`, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Fetch tenant payments
   * جلب مدفوعات المستأجر
   */
  getPayments: async (tenantId: string): Promise<Payment[]> => {
    return safeFetch(`${BILLING_BASE}/tenants/${tenantId}/payments`, async () => {
      const response = await api.get(`${BILLING_BASE}/tenants/${tenantId}/payments`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      if (data?.payments && Array.isArray(data.payments)) return data.payments;
      return [];
    });
  },
};
