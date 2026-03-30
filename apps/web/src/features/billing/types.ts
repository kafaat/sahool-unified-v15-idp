/**
 * Billing Feature - Types
 * أنواع ميزة الفوترة
 *
 * Types for billing plans, subscriptions, invoices, payments, and usage tracking.
 */

// =============================================================================
// Enums - التعدادات
// =============================================================================

export type SubscriptionStatus = 'active' | 'cancelled' | 'expired' | 'suspended' | 'trial' | 'past_due';

export type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded';

export type PaymentMethod = 'stripe' | 'tharwatt' | 'bank_transfer';

export type InvoiceStatus = 'draft' | 'issued' | 'paid' | 'overdue' | 'cancelled' | 'void';

export type PlanTier = 'free' | 'starter' | 'professional' | 'enterprise' | 'research';

export type BillingCycle = 'monthly' | 'yearly';

// =============================================================================
// Plan - الخطط
// =============================================================================

export interface PlanLimits {
  dailyQueries: number;
  imageDetection: number;
  weatherAlerts: boolean;
  marketPrices: boolean;
  fieldCount: number;
  advancedNdvi: boolean;
  aiAdvisorFull: boolean;
}

export interface BillingPlan {
  id: string;
  name: string;
  nameAr: string;
  tier: PlanTier;
  priceMonthly: number;
  priceYearly: number;
  currency: string;
  features: string[];
  limits: PlanLimits;
  isActive: boolean;
}

// =============================================================================
// Subscription - الاشتراكات
// =============================================================================

export interface Subscription {
  id: string;
  tenantId: string;
  planId: string;
  status: SubscriptionStatus;
  billingCycle: BillingCycle;
  startDate: string;
  endDate?: string;
  trialEndDate?: string;
  nextBillingDate?: string;
  autoRenew: boolean;
  cancelledAt?: string;
}

// =============================================================================
// Invoice - الفواتير
// =============================================================================

export interface InvoiceItem {
  description: string;
  descriptionAr: string;
  quantity: number;
  unitPrice: number;
  total: number;
}

export interface Invoice {
  id: string;
  tenantId: string;
  number: string;
  status: InvoiceStatus;
  amount: number;
  amountDue: number;
  currency: string;
  dueDate: string;
  issuedAt: string;
  paidAt?: string;
  items: InvoiceItem[];
}

// =============================================================================
// Payment - المدفوعات
// =============================================================================

export interface Payment {
  id: string;
  invoiceId: string;
  tenantId: string;
  amount: number;
  currency: string;
  method: PaymentMethod;
  status: PaymentStatus;
  processedAt?: string;
  transactionId?: string;
  failureReason?: string;
}

export interface CreatePaymentRequest {
  invoiceId: string;
  tenantId: string;
  amount: number;
  currency: string;
  method: PaymentMethod;
}

// =============================================================================
// Usage & Quota - الاستخدام والحصص
// =============================================================================

export interface UsageRecord {
  tenantId: string;
  metric: string;
  used: number;
  limit: number;
  period: string;
}

export interface QuotaEntry {
  metric: string;
  used: number;
  limit: number;
  percentage: number;
}

export interface QuotaInfo {
  tenantId: string;
  planTier: PlanTier;
  quotas: QuotaEntry[];
}

// =============================================================================
// Request/Response helpers
// =============================================================================

export interface UpdateSubscriptionRequest {
  planId: string;
  billingCycle?: BillingCycle;
}
