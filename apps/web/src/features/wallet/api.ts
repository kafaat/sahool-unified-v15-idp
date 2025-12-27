/**
 * Wallet Feature - API
 * واجهة برمجية لميزة المحفظة
 */

import type {
  Wallet,
  Transaction,
  TransactionFilters,
  TransferFormData,
  DepositFormData,
  WithdrawalFormData,
  WalletStats,
} from './types';

const API_BASE = '/api/v1/billing';

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
 * Error messages in Arabic
 * رسائل الخطأ بالعربية
 */
const errorMessages = {
  networkError: 'فشل الاتصال بالخادم. يرجى التحقق من اتصال الإنترنت.',
  walletNotFound: 'لم يتم العثور على المحفظة.',
  transactionNotFound: 'لم يتم العثور على المعاملة.',
  insufficientBalance: 'رصيد غير كاف لإتمام العملية.',
  invalidAmount: 'المبلغ المدخل غير صحيح.',
  serverError: 'حدث خطأ في الخادم. يرجى المحاولة لاحقاً.',
  unauthorized: 'غير مصرح لك بهذه العملية.',
};

/**
 * Make API request with error handling
 */
async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<{ data?: T; error?: string; errorAr?: string }> {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      const errorAr =
        response.status === 404 ? errorMessages.walletNotFound :
        response.status === 401 ? errorMessages.unauthorized :
        response.status === 400 ? errorMessages.invalidAmount :
        errorMessages.serverError;

      return {
        error: data.message || data.error || 'Request failed',
        errorAr,
      };
    }

    return { data };
  } catch (error) {
    console.error('API request error:', error);
    return {
      error: error instanceof Error ? error.message : 'Network error',
      errorAr: errorMessages.networkError,
    };
  }
}

/**
 * Filter transactions locally (for mock data)
 */
function filterTransactions(transactions: Transaction[], filters?: TransactionFilters): Transaction[] {
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
    const response = await apiRequest<Wallet>('/wallet');

    if (response.error || !response.data) {
      console.warn('Failed to fetch wallet, using mock data:', response.error);
      return mockWallet;
    }

    return response.data;
  },

  /**
   * Get wallet statistics
   * الحصول على إحصائيات المحفظة
   */
  async getStats(): Promise<WalletStats> {
    const response = await apiRequest<WalletStats>('/wallet/stats');

    if (response.error || !response.data) {
      console.warn('Failed to fetch wallet stats, using mock data:', response.error);

      // Calculate stats from mock wallet
      const stats: WalletStats = {
        currentBalance: mockWallet.balance,
        pendingBalance: mockWallet.pendingBalance,
        totalIncome: mockWallet.totalDeposits,
        totalExpenses: mockWallet.totalWithdrawals,
        monthlyIncome: 1500,
        monthlyExpenses: 557,
        transactionCount: mockWallet.totalTransactions,
        currency: mockWallet.currency,
      };

      return stats;
    }

    return response.data;
  },

  /**
   * Get transactions list
   * الحصول على قائمة المعاملات
   */
  async getTransactions(filters?: TransactionFilters): Promise<Transaction[]> {
    // Build query parameters
    const params = new URLSearchParams();
    if (filters?.type) params.append('type', filters.type);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.dateFrom) params.append('dateFrom', filters.dateFrom);
    if (filters?.dateTo) params.append('dateTo', filters.dateTo);
    if (filters?.minAmount !== undefined) params.append('minAmount', filters.minAmount.toString());
    if (filters?.maxAmount !== undefined) params.append('maxAmount', filters.maxAmount.toString());

    const queryString = params.toString();
    const endpoint = `/transactions${queryString ? `?${queryString}` : ''}`;

    const response = await apiRequest<Transaction[]>(endpoint);

    if (response.error || !response.data) {
      console.warn('Failed to fetch transactions, using mock data:', response.error);
      return filterTransactions(mockTransactions, filters);
    }

    return response.data;
  },

  /**
   * Get transaction by ID
   * الحصول على معاملة حسب المعرف
   */
  async getTransactionById(id: string): Promise<Transaction> {
    const response = await apiRequest<Transaction>(`/transactions/${id}`);

    if (response.error || !response.data) {
      console.warn('Failed to fetch transaction, using mock data:', response.error);

      const transaction = mockTransactions.find((t) => t.id === id);
      if (!transaction) {
        throw new Error(errorMessages.transactionNotFound);
      }
      return transaction;
    }

    return response.data;
  },

  /**
   * Create deposit
   * إنشاء إيداع
   */
  async deposit(data: DepositFormData): Promise<Transaction> {
    const response = await apiRequest<Transaction>('/deposit', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (response.error || !response.data) {
      // If API fails, throw error with Arabic message
      throw new Error(response.errorAr || errorMessages.serverError);
    }

    return response.data;
  },

  /**
   * Create withdrawal
   * إنشاء سحب
   */
  async withdraw(data: WithdrawalFormData): Promise<Transaction> {
    const response = await apiRequest<Transaction>('/withdraw', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (response.error || !response.data) {
      // If API fails, throw error with Arabic message
      throw new Error(response.errorAr || errorMessages.serverError);
    }

    return response.data;
  },

  /**
   * Transfer money to another user
   * تحويل الأموال إلى مستخدم آخر
   */
  async transfer(data: TransferFormData): Promise<Transaction> {
    const response = await apiRequest<Transaction>('/transfer', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (response.error || !response.data) {
      // If API fails, throw error with Arabic message
      throw new Error(response.errorAr || errorMessages.serverError);
    }

    return response.data;
  },
};
