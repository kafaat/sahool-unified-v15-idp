/**
 * Wallet Feature - Types
 * أنواع ميزة المحفظة
 */

export type TransactionType = 'deposit' | 'withdrawal' | 'payment' | 'refund' | 'transfer_in' | 'transfer_out';
export type TransactionStatus = 'pending' | 'completed' | 'failed' | 'cancelled';
export type PaymentMethod = 'card' | 'bank_transfer' | 'cash' | 'wallet';

export interface Transaction {
  id: string;
  userId: string;
  type: TransactionType;
  status: TransactionStatus;
  amount: number;
  currency: string;
  fee?: number;
  description: string;
  descriptionAr: string;
  paymentMethod?: PaymentMethod;
  reference?: string;
  metadata?: {
    orderId?: string;
    productName?: string;
    recipientId?: string;
    recipientName?: string;
    [key: string]: unknown;
  };
  createdAt: string;
  completedAt?: string;
}

export interface Wallet {
  id: string;
  userId: string;
  balance: number;
  currency: string;
  availableBalance: number;
  pendingBalance: number;
  totalDeposits: number;
  totalWithdrawals: number;
  totalTransactions: number;
  lastTransactionAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TransactionFilters {
  type?: TransactionType;
  status?: TransactionStatus;
  dateFrom?: string;
  dateTo?: string;
  minAmount?: number;
  maxAmount?: number;
}

export interface TransferFormData {
  recipientId: string;
  amount: number;
  description?: string;
  descriptionAr?: string;
}

export interface DepositFormData {
  amount: number;
  paymentMethod: PaymentMethod;
}

export interface WithdrawalFormData {
  amount: number;
  bankAccount?: string;
  method: 'bank_transfer' | 'cash';
}

export interface WalletStats {
  currentBalance: number;
  pendingBalance: number;
  totalIncome: number;
  totalExpenses: number;
  monthlyIncome: number;
  monthlyExpenses: number;
  transactionCount: number;
  currency: string;
}
