/**
 * Wallet Feature
 * ميزة المحفظة
 *
 * This feature handles:
 * - Wallet balance and transactions
 * - Deposits and withdrawals
 * - Money transfers between users
 * - Transaction history
 */

// API
export { walletApi } from './api';

// Types
export type {
  Wallet,
  Transaction,
  TransactionType,
  TransactionStatus,
  TransactionFilters,
  PaymentMethod,
  WalletStats,
  TransferFormData,
  DepositFormData,
  WithdrawalFormData,
} from './types';

// Hooks
export {
  useWallet,
  useWalletStats,
  useTransactions,
  useTransaction,
  useDeposit,
  useWithdraw,
  useTransfer,
  walletKeys,
} from './hooks/useWallet';

// Components
export { WalletDashboard } from './components/WalletDashboard';
export { TransactionHistory } from './components/TransactionHistory';
export { TransferForm } from './components/TransferForm';
