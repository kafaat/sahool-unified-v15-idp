/**
 * Billing Hooks
 * خطافات الفوترة - React Query hooks for billing data and mutations
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { billingApi } from '../api';
import type {
  BillingPlan,
  Subscription,
  Invoice,
  Payment,
  CreatePaymentRequest,
  UpdateSubscriptionRequest,
} from '../types';

export const billingKeys = {
  all: ['billing'] as const,
  plans: () => [...billingKeys.all, 'plans'] as const,
  plan: (planId: string) => [...billingKeys.all, 'plans', planId] as const,
  subscription: (tenantId: string) => [...billingKeys.all, 'subscription', tenantId] as const,
  usage: (tenantId: string) => [...billingKeys.all, 'usage', tenantId] as const,
  quota: (tenantId: string) => [...billingKeys.all, 'quota', tenantId] as const,
  invoices: (tenantId: string) => [...billingKeys.all, 'invoices', tenantId] as const,
  invoice: (invoiceId: string) => [...billingKeys.all, 'invoice', invoiceId] as const,
  payments: (tenantId: string) => [...billingKeys.all, 'payments', tenantId] as const,
};

// =============================================================================
// Plans - الخطط
// =============================================================================

/**
 * Hook to fetch all billing plans
 * خطاف لجلب جميع خطط الفوترة
 */
export function useBillingPlans() {
  return useQuery({
    queryKey: billingKeys.plans(),
    queryFn: billingApi.getPlans,
    staleTime: 60 * 60 * 1000, // 1 hour - plans rarely change
  });
}

/**
 * Hook to fetch a single plan by ID
 * خطاف لجلب خطة واحدة بالمعرف
 */
export function useBillingPlan(planId: string) {
  return useQuery({
    queryKey: billingKeys.plan(planId),
    queryFn: () => billingApi.getPlanById(planId),
    enabled: !!planId,
    staleTime: 60 * 60 * 1000,
  });
}

// =============================================================================
// Subscriptions - الاشتراكات
// =============================================================================

/**
 * Hook to fetch tenant subscription
 * خطاف لجلب اشتراك المستأجر
 */
export function useSubscription(tenantId: string) {
  return useQuery({
    queryKey: billingKeys.subscription(tenantId),
    queryFn: () => billingApi.getSubscription(tenantId),
    enabled: !!tenantId,
    staleTime: 30 * 1000, // 30 seconds
  });
}

/**
 * Hook to update subscription (change plan)
 * خطاف لتحديث الاشتراك (تغيير الخطة)
 */
export function useUpdateSubscription(tenantId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateSubscriptionRequest) =>
      billingApi.updateSubscription(tenantId, data),
    onSuccess: (updatedSub: Subscription) => {
      queryClient.setQueryData(billingKeys.subscription(tenantId), updatedSub);
      queryClient.invalidateQueries({ queryKey: billingKeys.subscription(tenantId) });
      queryClient.invalidateQueries({ queryKey: billingKeys.quota(tenantId) });
      queryClient.invalidateQueries({ queryKey: billingKeys.usage(tenantId) });
    },
  });
}

/**
 * Hook to cancel subscription
 * خطاف لإلغاء الاشتراك
 */
export function useCancelSubscription(tenantId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => billingApi.cancelSubscription(tenantId),
    onSuccess: (cancelledSub: Subscription) => {
      queryClient.setQueryData(billingKeys.subscription(tenantId), cancelledSub);
      queryClient.invalidateQueries({ queryKey: billingKeys.subscription(tenantId) });
    },
  });
}

// =============================================================================
// Usage & Quota - الاستخدام والحصص
// =============================================================================

/**
 * Hook to fetch tenant usage records
 * خطاف لجلب سجلات الاستخدام
 */
export function useUsage(tenantId: string) {
  return useQuery({
    queryKey: billingKeys.usage(tenantId),
    queryFn: () => billingApi.getUsage(tenantId),
    enabled: !!tenantId,
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
}

/**
 * Hook to fetch tenant quota information
 * خطاف لجلب معلومات الحصة
 */
export function useQuota(tenantId: string) {
  return useQuery({
    queryKey: billingKeys.quota(tenantId),
    queryFn: () => billingApi.getQuota(tenantId),
    enabled: !!tenantId,
    staleTime: 60 * 1000,
    refetchInterval: 5 * 60 * 1000,
  });
}

// =============================================================================
// Invoices - الفواتير
// =============================================================================

/**
 * Hook to fetch tenant invoices
 * خطاف لجلب فواتير المستأجر
 */
export function useInvoices(tenantId: string) {
  return useQuery({
    queryKey: billingKeys.invoices(tenantId),
    queryFn: () => billingApi.getInvoices(tenantId),
    enabled: !!tenantId,
    staleTime: 30 * 1000,
  });
}

/**
 * Hook to fetch a single invoice
 * خطاف لجلب فاتورة واحدة
 */
export function useInvoice(invoiceId: string) {
  return useQuery({
    queryKey: billingKeys.invoice(invoiceId),
    queryFn: () => billingApi.getInvoiceById(invoiceId),
    enabled: !!invoiceId,
  });
}

/**
 * Hook to generate a new invoice
 * خطاف لتوليد فاتورة جديدة
 */
export function useGenerateInvoice(tenantId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => billingApi.generateInvoice(tenantId),
    onSuccess: (newInvoice: Invoice) => {
      queryClient.setQueryData<Invoice[]>(billingKeys.invoices(tenantId), (old) =>
        old ? [newInvoice, ...old] : [newInvoice]
      );
      queryClient.invalidateQueries({ queryKey: billingKeys.invoices(tenantId) });
    },
  });
}

// =============================================================================
// Payments - المدفوعات
// =============================================================================

/**
 * Hook to fetch tenant payments
 * خطاف لجلب مدفوعات المستأجر
 */
export function usePayments(tenantId: string) {
  return useQuery({
    queryKey: billingKeys.payments(tenantId),
    queryFn: () => billingApi.getPayments(tenantId),
    enabled: !!tenantId,
    staleTime: 30 * 1000,
  });
}

/**
 * Hook to create a new payment
 * خطاف لإنشاء دفعة جديدة
 */
export function useCreatePayment(tenantId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreatePaymentRequest) => billingApi.createPayment(data),
    onSuccess: (newPayment: Payment) => {
      queryClient.setQueryData<Payment[]>(billingKeys.payments(tenantId), (old) =>
        old ? [newPayment, ...old] : [newPayment]
      );
      queryClient.invalidateQueries({ queryKey: billingKeys.payments(tenantId) });
      // Refresh invoices since payment status may have changed
      queryClient.invalidateQueries({ queryKey: billingKeys.invoices(tenantId) });
      // Refresh subscription in case payment activates/updates it
      queryClient.invalidateQueries({ queryKey: billingKeys.subscription(tenantId) });
    },
  });
}
