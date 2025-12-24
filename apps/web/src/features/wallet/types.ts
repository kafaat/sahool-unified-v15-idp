/**
 * Wallet Feature - Types
 * أنواع ميزة المحفظة
 */

export type TransactionType = 'deposit' | 'withdrawal' | 'payment' | 'refund' | 'transfer_in' | 'transfer_out';
export type TransactionStatus = 'pending' | 'completed' | 'failed' | 'cancelled';
export type PaymentMethod = 'card' | 'bank_transfer' | 'cash' | 'wallet' | 'tharwatt' | 'mobile_money';

/**
 * Transaction - معاملة
 * Represents a wallet transaction (deposit, withdrawal, transfer, payment)
 */
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
    bankAccount?: string;
    phoneNumber?: string;
    [key: string]: unknown;
  };
  createdAt: string;
  completedAt?: string;
  failureReason?: string; // For failed transactions
}

/**
 * Wallet - محفظة
 * User wallet information
 */
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

/**
 * TransactionFilters - مرشحات المعاملات
 * Filters for querying transactions
 */
export interface TransactionFilters {
  type?: TransactionType;
  status?: TransactionStatus;
  dateFrom?: string;
  dateTo?: string;
  minAmount?: number;
  maxAmount?: number;
}

/**
 * TransferFormData - بيانات نموذج التحويل
 * Form data for transferring money to another user
 */
export interface TransferFormData {
  recipientId: string;
  amount: number;
  description?: string;
  descriptionAr?: string;
}

/**
 * DepositFormData - بيانات نموذج الإيداع
 * Form data for depositing money
 */
export interface DepositFormData {
  amount: number;
  paymentMethod: PaymentMethod;
  reference?: string; // For bank transfer reference
  phoneNumber?: string; // For mobile money
}

/**
 * WithdrawalFormData - بيانات نموذج السحب
 * Form data for withdrawing money
 */
export interface WithdrawalFormData {
  amount: number;
  bankAccount?: string;
  method: 'bank_transfer' | 'cash' | 'mobile_money';
  phoneNumber?: string; // For mobile money withdrawal
}

/**
 * WalletStats - إحصائيات المحفظة
 * Wallet statistics and summary
 */
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

/**
 * API Response Types - أنواع استجابة API
 * Response types from billing-core service
 */

export interface WalletApiResponse {
  success: boolean;
  data?: Wallet;
  error?: string;
  message?: string;
  message_ar?: string;
}

export interface TransactionsApiResponse {
  success: boolean;
  data?: Transaction[];
  total?: number;
  error?: string;
  message?: string;
  message_ar?: string;
}

export interface TransactionApiResponse {
  success: boolean;
  data?: Transaction;
  error?: string;
  message?: string;
  message_ar?: string;
}
