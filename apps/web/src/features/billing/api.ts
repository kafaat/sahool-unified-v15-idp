/**
 * Billing Feature - API Layer
 * طبقة API لميزة الفوترة - Real API with mock fallback
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { API_PREFIX, BILLING_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
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

const BILLING_BASE = `${API_PREFIX}/billing`;

export const billingApi = {
  // =========================================================================
  // Plans - الخطط
  // =========================================================================

  /**
   * Fetch all billing plans
   * جلب جميع خطط الفوترة
   */
  getPlans: async (): Promise<BillingPlan[]> => {
    return safeFetch(BILLING_ENDPOINTS.PLANS, async () => {
      const response = await api.get(BILLING_ENDPOINTS.PLANS);
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
    const url = `${BILLING_ENDPOINTS.PLANS}/${planId}`;
    return safeFetch(url, async () => {
      const response = await api.get(url);
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
    const url = buildUrl(BILLING_ENDPOINTS.TENANT_SUBSCRIPTION, { tenantId });
    return safeFetch(url, async () => {
      const response = await api.get(url);
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
    const url = buildUrl(BILLING_ENDPOINTS.TENANT_SUBSCRIPTION, { tenantId });
    return safeFetch(url, async () => {
      const response = await api.patch(url, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Cancel tenant subscription
   * إلغاء اشتراك المستأجر
   */
  cancelSubscription: async (tenantId: string): Promise<Subscription> => {
    const url = `${BILLING_BASE}/tenants/${tenantId}/cancel`;
    return safeFetch(url, async () => {
      const response = await api.post(url);
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
    const url = buildUrl(BILLING_ENDPOINTS.TENANT_USAGE, { tenantId });
    return safeFetch(url, async () => {
      const response = await api.get(url);
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
    const url = `${BILLING_BASE}/tenants/${tenantId}/quota`;
    return safeFetch(url, async () => {
      const response = await api.get(url);
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
    const url = buildUrl(BILLING_ENDPOINTS.TENANT_INVOICES, { tenantId });
    return safeFetch(url, async () => {
      const response = await api.get(url);
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
    const url = buildUrl(BILLING_ENDPOINTS.INVOICE_GET, { invoiceId });
    return safeFetch(url, async () => {
      const response = await api.get(url);
      return response.data.data || response.data;
    });
  },

  /**
   * Generate a new invoice for tenant
   * توليد فاتورة جديدة للمستأجر
   */
  generateInvoice: async (tenantId: string): Promise<Invoice> => {
    const url = `${buildUrl(BILLING_ENDPOINTS.TENANT_INVOICES, { tenantId })}/generate`;
    return safeFetch(url, async () => {
      const response = await api.post(url);
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
    const url = `${BILLING_BASE}/payments`;
    return safeFetch(url, async () => {
      const response = await api.post(url, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Fetch tenant payments
   * جلب مدفوعات المستأجر
   */
  getPayments: async (tenantId: string): Promise<Payment[]> => {
    const url = `${BILLING_BASE}/tenants/${tenantId}/payments`;
    return safeFetch(url, async () => {
      const response = await api.get(url);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      if (data?.payments && Array.isArray(data.payments)) return data.payments;
      return [];
    });
  },
};
