/**
 * Wallet Feature - API
 * واجهة برمجية لميزة المحفظة
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch, ApiError } from '@/lib/api/safe-fetch';
import { BILLING_ENDPOINTS } from '@sahool/shared-types/contracts';
import type {
  Wallet,
  Transaction,
  TransactionFilters,
  TransferFormData,
  DepositFormData,
  WithdrawalFormData,
  WalletStats,
} from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

/**
 * Error messages in Arabic and English
 * رسائل الخطأ بالعربية والإنجليزية
 */
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  WALLET_NOT_FOUND: {
    en: 'Wallet not found.',
    ar: 'لم يتم العثور على المحفظة.',
  },
  TRANSACTION_NOT_FOUND: {
    en: 'Transaction not found.',
    ar: 'لم يتم العثور على المعاملة.',
  },
  INSUFFICIENT_BALANCE: {
    en: 'Insufficient balance.',
    ar: 'رصيد غير كاف لإتمام العملية.',
  },
  INVALID_AMOUNT: {
    en: 'Invalid amount.',
    ar: 'المبلغ المدخل غير صحيح.',
  },
  SERVER_ERROR: {
    en: 'Server error. Please try again later.',
    ar: 'حدث خطأ في الخادم. يرجى المحاولة لاحقاً.',
  },
  UNAUTHORIZED: {
    en: 'Unauthorized access.',
    ar: 'غير مصرح لك بهذه العملية.',
  },
  FETCH_FAILED: {
    en: 'Wallet data is unavailable. Please try again later.',
    ar: 'بيانات المحفظة غير متاحة. يرجى المحاولة لاحقاً.',
  },
};

export const walletApi = {
  /**
   * Get wallet details
   * الحصول على تفاصيل المحفظة
   */
  async getWallet(): Promise<Wallet> {
    return safeFetch(BILLING_ENDPOINTS.WALLET, async () => {
      const response = await api.get(BILLING_ENDPOINTS.WALLET);
      const data = response.data.data || response.data;

      if (data && typeof data === 'object' && 'balance' in data) {
        return data as Wallet;
      }

      throw new ApiError({
        message: ERROR_MESSAGES.FETCH_FAILED.en,
        messageAr: ERROR_MESSAGES.FETCH_FAILED.ar,
        statusCode: 500,
        endpoint: BILLING_ENDPOINTS.WALLET,
      });
    });
  },

  /**
   * Get wallet statistics
   * الحصول على إحصائيات المحفظة
   */
  async getStats(): Promise<WalletStats> {
    const endpoint = `${BILLING_ENDPOINTS.WALLET}/stats`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      const data = response.data.data || response.data;

      if (data && typeof data === 'object' && 'currentBalance' in data) {
        return data as WalletStats;
      }

      throw new ApiError({
        message: ERROR_MESSAGES.FETCH_FAILED.en,
        messageAr: ERROR_MESSAGES.FETCH_FAILED.ar,
        statusCode: 500,
        endpoint,
      });
    });
  },

  /**
   * Get transactions list
   * الحصول على قائمة المعاملات
   */
  async getTransactions(filters?: TransactionFilters): Promise<Transaction[]> {
    return safeFetch(BILLING_ENDPOINTS.TRANSACTIONS, async () => {
      const params = new URLSearchParams();
      if (filters?.type) params.append('type', filters.type);
      if (filters?.status) params.append('status', filters.status);
      if (filters?.dateFrom) params.append('dateFrom', filters.dateFrom);
      if (filters?.dateTo) params.append('dateTo', filters.dateTo);
      if (filters?.minAmount !== undefined)
        params.append('minAmount', filters.minAmount.toString());
      if (filters?.maxAmount !== undefined)
        params.append('maxAmount', filters.maxAmount.toString());

      const queryString = params.toString();
      const endpoint = `${BILLING_ENDPOINTS.TRANSACTIONS}${queryString ? `?${queryString}` : ''}`;

      const response = await api.get(endpoint);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      throw new ApiError({
        message: ERROR_MESSAGES.FETCH_FAILED.en,
        messageAr: ERROR_MESSAGES.FETCH_FAILED.ar,
        statusCode: 500,
        endpoint: BILLING_ENDPOINTS.TRANSACTIONS,
      });
    });
  },

  /**
   * Get transaction by ID
   * الحصول على معاملة حسب المعرف
   */
  async getTransactionById(id: string): Promise<Transaction> {
    const endpoint = `${BILLING_ENDPOINTS.TRANSACTIONS}/${id}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      const data = response.data.data || response.data;

      if (data && typeof data === 'object' && 'id' in data) {
        return data as Transaction;
      }

      throw new ApiError({
        message: ERROR_MESSAGES.FETCH_FAILED.en,
        messageAr: ERROR_MESSAGES.FETCH_FAILED.ar,
        statusCode: 500,
        endpoint,
      });
    });
  },

  /**
   * Create deposit
   * إنشاء إيداع
   */
  async deposit(data: DepositFormData): Promise<Transaction> {
    return safeFetch(BILLING_ENDPOINTS.WALLET_DEPOSIT, async () => {
      try {
        const response = await api.post(BILLING_ENDPOINTS.WALLET_DEPOSIT, data);
        const result = response.data.data || response.data;

        if (result && typeof result === 'object' && 'id' in result) {
          return result as Transaction;
        }

        throw new ApiError({ message: ERROR_MESSAGES.SERVER_ERROR.en, messageAr: ERROR_MESSAGES.SERVER_ERROR.ar, statusCode: 500, endpoint: BILLING_ENDPOINTS.WALLET_DEPOSIT });
      } catch (err: unknown) {
        if (err instanceof ApiError) throw err;
        const status = (err as { response?: { status?: number } })?.response?.status;
        if (status === 400) throw new ApiError({ message: ERROR_MESSAGES.INVALID_AMOUNT.en, messageAr: ERROR_MESSAGES.INVALID_AMOUNT.ar, statusCode: 400, endpoint: BILLING_ENDPOINTS.WALLET_DEPOSIT });
        if (status === 401) throw new ApiError({ message: ERROR_MESSAGES.UNAUTHORIZED.en, messageAr: ERROR_MESSAGES.UNAUTHORIZED.ar, statusCode: 401, endpoint: BILLING_ENDPOINTS.WALLET_DEPOSIT });
        throw err;
      }
    });
  },

  /**
   * Create withdrawal
   * إنشاء سحب
   */
  async withdraw(data: WithdrawalFormData): Promise<Transaction> {
    return safeFetch(BILLING_ENDPOINTS.WALLET_WITHDRAW, async () => {
      try {
        const response = await api.post(BILLING_ENDPOINTS.WALLET_WITHDRAW, data);
        const result = response.data.data || response.data;

        if (result && typeof result === 'object' && 'id' in result) {
          return result as Transaction;
        }

        throw new ApiError({ message: ERROR_MESSAGES.SERVER_ERROR.en, messageAr: ERROR_MESSAGES.SERVER_ERROR.ar, statusCode: 500, endpoint: BILLING_ENDPOINTS.WALLET_WITHDRAW });
      } catch (err: unknown) {
        if (err instanceof ApiError) throw err;
        const status = (err as { response?: { status?: number } })?.response?.status;
        if (status === 400) throw new ApiError({ message: ERROR_MESSAGES.INVALID_AMOUNT.en, messageAr: ERROR_MESSAGES.INVALID_AMOUNT.ar, statusCode: 400, endpoint: BILLING_ENDPOINTS.WALLET_WITHDRAW });
        if (status === 401) throw new ApiError({ message: ERROR_MESSAGES.UNAUTHORIZED.en, messageAr: ERROR_MESSAGES.UNAUTHORIZED.ar, statusCode: 401, endpoint: BILLING_ENDPOINTS.WALLET_WITHDRAW });
        if (status === 402) throw new ApiError({ message: ERROR_MESSAGES.INSUFFICIENT_BALANCE.en, messageAr: ERROR_MESSAGES.INSUFFICIENT_BALANCE.ar, statusCode: 402, endpoint: BILLING_ENDPOINTS.WALLET_WITHDRAW });
        throw err;
      }
    });
  },

  /**
   * Transfer money to another user
   * تحويل الأموال إلى مستخدم آخر
   */
  async transfer(data: TransferFormData): Promise<Transaction> {
    return safeFetch(BILLING_ENDPOINTS.WALLET_TRANSFER, async () => {
      try {
        const response = await api.post(BILLING_ENDPOINTS.WALLET_TRANSFER, data);
        const result = response.data.data || response.data;

        if (result && typeof result === 'object' && 'id' in result) {
          return result as Transaction;
        }

        throw new ApiError({ message: ERROR_MESSAGES.SERVER_ERROR.en, messageAr: ERROR_MESSAGES.SERVER_ERROR.ar, statusCode: 500, endpoint: BILLING_ENDPOINTS.WALLET_TRANSFER });
      } catch (err: unknown) {
        if (err instanceof ApiError) throw err;
        const status = (err as { response?: { status?: number } })?.response?.status;
        if (status === 400) throw new ApiError({ message: ERROR_MESSAGES.INVALID_AMOUNT.en, messageAr: ERROR_MESSAGES.INVALID_AMOUNT.ar, statusCode: 400, endpoint: BILLING_ENDPOINTS.WALLET_TRANSFER });
        if (status === 401) throw new ApiError({ message: ERROR_MESSAGES.UNAUTHORIZED.en, messageAr: ERROR_MESSAGES.UNAUTHORIZED.ar, statusCode: 401, endpoint: BILLING_ENDPOINTS.WALLET_TRANSFER });
        if (status === 402) throw new ApiError({ message: ERROR_MESSAGES.INSUFFICIENT_BALANCE.en, messageAr: ERROR_MESSAGES.INSUFFICIENT_BALANCE.ar, statusCode: 402, endpoint: BILLING_ENDPOINTS.WALLET_TRANSFER });
        throw err;
      }
    });
  },
};
