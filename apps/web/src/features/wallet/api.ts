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

const API_BASE = '/api/wallet';

// Mock data for development
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

export const walletApi = {
  /**
   * Get wallet details
   */
  async getWallet(): Promise<Wallet> {
    return new Promise((resolve) => setTimeout(() => resolve(mockWallet), 300));
  },

  /**
   * Get wallet statistics
   */
  async getStats(): Promise<WalletStats> {
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
    return new Promise((resolve) => setTimeout(() => resolve(stats), 300));
  },

  /**
   * Get transactions list
   */
  async getTransactions(filters?: TransactionFilters): Promise<Transaction[]> {
    let transactions = [...mockTransactions];

    if (filters?.type) {
      transactions = transactions.filter((t) => t.type === filters.type);
    }

    if (filters?.status) {
      transactions = transactions.filter((t) => t.status === filters.status);
    }

    if (filters?.dateFrom) {
      const fromDate = new Date(filters.dateFrom);
      transactions = transactions.filter((t) => new Date(t.createdAt) >= fromDate);
    }

    if (filters?.dateTo) {
      const toDate = new Date(filters.dateTo);
      transactions = transactions.filter((t) => new Date(t.createdAt) <= toDate);
    }

    if (filters?.minAmount !== undefined) {
      transactions = transactions.filter((t) => t.amount >= filters.minAmount!);
    }

    if (filters?.maxAmount !== undefined) {
      transactions = transactions.filter((t) => t.amount <= filters.maxAmount!);
    }

    // Sort by date (newest first)
    transactions.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

    return new Promise((resolve) => setTimeout(() => resolve(transactions), 500));
  },

  /**
   * Get transaction by ID
   */
  async getTransactionById(id: string): Promise<Transaction> {
    const transaction = mockTransactions.find((t) => t.id === id);
    if (!transaction) {
      throw new Error('Transaction not found');
    }
    return new Promise((resolve) => setTimeout(() => resolve(transaction), 300));
  },

  /**
   * Create deposit
   */
  async deposit(data: DepositFormData): Promise<Transaction> {
    const transaction: Transaction = {
      id: Date.now().toString(),
      userId: 'current-user',
      type: 'deposit',
      status: 'pending',
      amount: data.amount,
      currency: 'SAR',
      description: 'Deposit',
      descriptionAr: 'إيداع',
      paymentMethod: data.paymentMethod,
      createdAt: new Date().toISOString(),
    };
    return new Promise((resolve) => setTimeout(() => resolve(transaction), 500));
  },

  /**
   * Create withdrawal
   */
  async withdraw(data: WithdrawalFormData): Promise<Transaction> {
    const transaction: Transaction = {
      id: Date.now().toString(),
      userId: 'current-user',
      type: 'withdrawal',
      status: 'pending',
      amount: data.amount,
      currency: 'SAR',
      description: 'Withdrawal',
      descriptionAr: 'سحب',
      metadata: {
        bankAccount: data.bankAccount,
      },
      createdAt: new Date().toISOString(),
    };
    return new Promise((resolve) => setTimeout(() => resolve(transaction), 500));
  },

  /**
   * Transfer money to another user
   */
  async transfer(data: TransferFormData): Promise<Transaction> {
    const transaction: Transaction = {
      id: Date.now().toString(),
      userId: 'current-user',
      type: 'transfer_out',
      status: 'completed',
      amount: data.amount,
      currency: 'SAR',
      fee: data.amount * 0.01, // 1% fee
      description: data.description || 'Transfer',
      descriptionAr: data.descriptionAr || 'تحويل',
      metadata: {
        recipientId: data.recipientId,
      },
      createdAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
    };
    return new Promise((resolve) => setTimeout(() => resolve(transaction), 500));
  },
};
