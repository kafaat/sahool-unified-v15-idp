/**
 * Wallet Feature - API
 * واجهة برمجية لميزة المحفظة
 */

import { createApiClient, logger } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
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

// Mock data for development fallback
const mockTransactions: Transaction[] = [
  {
    id: '1',
    userId: 'current-user',
    type: 'deposit',
    status: 'completed',
    amount: 1000,
    currency: 'SAR',
    description: 'Initial deposit',
    descriptionAr: 'إيداع أولي',
    paymentMethod: 'bank_transfer',
    createdAt: new Date(Date.now() - 86400000 * 7).toISOString(),
    completedAt: new Date(Date.now() - 86400000 * 7).toISOString(),
  },
  {
    id: '2',
    userId: 'current-user',
    type: 'payment',
    status: 'completed',
    amount: 350,
    currency: 'SAR',
    fee: 5,
    description: 'Product purchase - Wheat Seeds',
    descriptionAr: 'شراء منتج - بذور قمح',
    paymentMethod: 'wallet',
    metadata: {
      orderId: 'ORD-123',
      productName: 'Wheat Seeds',
    },
    createdAt: new Date(Date.now() - 86400000 * 5).toISOString(),
    completedAt: new Date(Date.now() - 86400000 * 5).toISOString(),
  },
  {
    id: '3',
    userId: 'current-user',
    type: 'transfer_out',
    status: 'completed',
    amount: 200,
    currency: 'SAR',
    fee: 2,
    description: 'Transfer to Ahmad',
    descriptionAr: 'تحويل إلى أحمد',
    metadata: {
      recipientId: 'user-123',
      recipientName: 'Ahmad Ali',
    },
    createdAt: new Date(Date.now() - 86400000 * 3).toISOString(),
    completedAt: new Date(Date.now() - 86400000 * 3).toISOString(),
  },
  {
    id: '4',
    userId: 'current-user',
    type: 'deposit',
    status: 'completed',
    amount: 500,
    currency: 'SAR',
    description: 'Bank transfer',
    descriptionAr: 'تحويل بنكي',
    paymentMethod: 'bank_transfer',
    createdAt: new Date(Date.now() - 86400000 * 1).toISOString(),
    completedAt: new Date(Date.now() - 86400000 * 1).toISOString(),
  },
];

const mockWallet: Wallet = {
  id: 'wallet-1',
  userId: 'current-user',
  balance: 943,
  currency: 'SAR',
  availableBalance: 943,
  pendingBalance: 0,
  totalDeposits: 1500,
  totalWithdrawals: 557,
  totalTransactions: 4,
  lastTransactionAt: new Date().toISOString(),
  createdAt: new Date(Date.now() - 86400000 * 30).toISOString(),
  updatedAt: new Date().toISOString(),
};

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
    en: 'Failed to fetch wallet data. Using cached data.',
    ar: 'فشل في جلب بيانات المحفظة. استخدام البيانات المخزنة.',
  },
};

/**
 * Filter transactions locally (for mock data)
 */
function filterTransactions(
  transactions: Transaction[],
  filters?: TransactionFilters
): Transaction[] {
  let filtered = [...transactions];

  if (filters?.type) {
    filtered = filtered.filter((t) => t.type === filters.type);
  }

  if (filters?.status) {
    filtered = filtered.filter((t) => t.status === filters.status);
  }

  if (filters?.dateFrom) {
    const fromDate = new Date(filters.dateFrom);
    filtered = filtered.filter((t) => new Date(t.createdAt) >= fromDate);
  }

  if (filters?.dateTo) {
    const toDate = new Date(filters.dateTo);
    filtered = filtered.filter((t) => new Date(t.createdAt) <= toDate);
  }

  if (filters?.minAmount !== undefined) {
    filtered = filtered.filter((t) => t.amount >= filters.minAmount!);
  }

  if (filters?.maxAmount !== undefined) {
    filtered = filtered.filter((t) => t.amount <= filters.maxAmount!);
  }

  // Sort by date (newest first)
  filtered.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

  return filtered;
}

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

      logger.warn('API returned unexpected format, using mock data');
      return mockWallet;
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

      logger.warn('API returned unexpected format for stats, using mock data');
      return {
        currentBalance: mockWallet.balance,
        pendingBalance: mockWallet.pendingBalance,
        totalIncome: mockWallet.totalDeposits,
        totalExpenses: mockWallet.totalWithdrawals,
        monthlyIncome: 1500,
        monthlyExpenses: 557,
        transactionCount: mockWallet.totalTransactions,
        currency: mockWallet.currency,
      };
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

      logger.warn('API returned unexpected format for transactions, using mock data');
      return filterTransactions(mockTransactions, filters);
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

      logger.warn('API returned unexpected format for transaction, using mock data');
      const transaction = mockTransactions.find((t) => t.id === id);
      if (!transaction) {
        throw new Error(`${ERROR_MESSAGES.TRANSACTION_NOT_FOUND.en} | ${ERROR_MESSAGES.TRANSACTION_NOT_FOUND.ar}`);
      }
      return transaction;
    });
  },

  /**
   * Create deposit
   * إنشاء إيداع
   */
  async deposit(data: DepositFormData): Promise<Transaction> {
    return safeFetch(BILLING_ENDPOINTS.WALLET_DEPOSIT, async () => {
      const response = await api.post(BILLING_ENDPOINTS.WALLET_DEPOSIT, data);
      const result = response.data.data || response.data;

      if (result && typeof result === 'object' && 'id' in result) {
        return result as Transaction;
      }

      throw new Error(`${ERROR_MESSAGES.SERVER_ERROR.en} | ${ERROR_MESSAGES.SERVER_ERROR.ar}`);
    });
  },

  /**
   * Create withdrawal
   * إنشاء سحب
   */
  async withdraw(data: WithdrawalFormData): Promise<Transaction> {
    return safeFetch(BILLING_ENDPOINTS.WALLET_WITHDRAW, async () => {
      const response = await api.post(BILLING_ENDPOINTS.WALLET_WITHDRAW, data);
      const result = response.data.data || response.data;

      if (result && typeof result === 'object' && 'id' in result) {
        return result as Transaction;
      }

      throw new Error(`${ERROR_MESSAGES.SERVER_ERROR.en} | ${ERROR_MESSAGES.SERVER_ERROR.ar}`);
    });
  },

  /**
   * Transfer money to another user
   * تحويل الأموال إلى مستخدم آخر
   */
  async transfer(data: TransferFormData): Promise<Transaction> {
    return safeFetch(BILLING_ENDPOINTS.WALLET_TRANSFER, async () => {
      const response = await api.post(BILLING_ENDPOINTS.WALLET_TRANSFER, data);
      const result = response.data.data || response.data;

      if (result && typeof result === 'object' && 'id' in result) {
        return result as Transaction;
      }

      throw new Error(`${ERROR_MESSAGES.SERVER_ERROR.en} | ${ERROR_MESSAGES.SERVER_ERROR.ar}`);
    });
  },
};
