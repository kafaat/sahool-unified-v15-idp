/**
 * WalletDashboard Component
 * لوحة معلومات المحفظة
 */

'use client';

import React from 'react';
import {
  Wallet as WalletIcon,
  TrendingUp,
  TrendingDown,
  Clock,
  ArrowUpRight,
  ArrowDownLeft,
  CreditCard,
} from 'lucide-react';
import { useWallet, useWalletStats } from '../hooks/useWallet';

interface WalletDashboardProps {
  onTransferClick?: () => void;
  onDepositClick?: () => void;
  onWithdrawClick?: () => void;
}

export const WalletDashboard: React.FC<WalletDashboardProps> = ({
  onTransferClick,
  onDepositClick,
  onWithdrawClick,
}) => {
  const { data: wallet, isLoading: walletLoading } = useWallet();
  const { data: stats, isLoading: statsLoading } = useWalletStats();

  if (walletLoading || statsLoading) {
    return (
      <div className="space-y-6">
        <div className="h-48 bg-gray-200 rounded-xl animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-32 bg-gray-200 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (!wallet || !stats) {
    return (
      <div className="text-center py-16">
        <WalletIcon className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">لا توجد بيانات للمحفظة</h3>
        <p className="text-gray-500">حدث خطأ في تحميل بيانات المحفظة</p>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="wallet-dashboard">
      {/* Balance Card */}
      <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-2xl p-8 text-white shadow-xl" data-testid="wallet-balance-card">
        <div className="flex items-start justify-between mb-6">
          <div>
            <p className="text-blue-100 mb-2" data-testid="wallet-balance-label">رصيد المحفظة | Wallet Balance</p>
            <h1 className="text-4xl font-bold mb-1" data-testid="wallet-balance-amount">
              {wallet.balance.toFixed(2)} {wallet.currency}
            </h1>
            {wallet.pendingBalance > 0 && (
              <p className="text-blue-200 text-sm flex items-center gap-1" data-testid="wallet-pending-balance">
                <Clock className="w-4 h-4" />
                قيد الانتظار: {wallet.pendingBalance.toFixed(2)} {wallet.currency}
              </p>
            )}
          </div>
          <WalletIcon className="w-12 h-12 opacity-80" data-testid="wallet-icon" />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-3 gap-3" data-testid="wallet-quick-actions">
          <button
            onClick={onDepositClick}
            data-testid="wallet-deposit-button"
            className="flex flex-col items-center gap-2 p-4 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-xl transition-all backdrop-blur-sm"
          >
            <ArrowDownLeft className="w-6 h-6" />
            <span className="text-sm font-semibold">إيداع</span>
          </button>
          <button
            onClick={onWithdrawClick}
            data-testid="wallet-withdraw-button"
            className="flex flex-col items-center gap-2 p-4 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-xl transition-all backdrop-blur-sm"
          >
            <ArrowUpRight className="w-6 h-6" />
            <span className="text-sm font-semibold">سحب</span>
          </button>
          <button
            onClick={onTransferClick}
            data-testid="wallet-transfer-button"
            className="flex flex-col items-center gap-2 p-4 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-xl transition-all backdrop-blur-sm"
          >
            <CreditCard className="w-6 h-6" />
            <span className="text-sm font-semibold">تحويل</span>
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6" data-testid="wallet-statistics-grid">
        {/* Total Income */}
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="wallet-stat-income">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <span className="text-xs text-gray-500">هذا الشهر</span>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1" data-testid="wallet-stat-income-amount">
            {stats.monthlyIncome.toFixed(2)} {stats.currency}
          </h3>
          <p className="text-sm text-gray-600">إجمالي الإيداعات | Total Income</p>
        </div>

        {/* Total Expenses */}
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="wallet-stat-expenses">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-red-100 rounded-lg">
              <TrendingDown className="w-6 h-6 text-red-600" />
            </div>
            <span className="text-xs text-gray-500">هذا الشهر</span>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1" data-testid="wallet-stat-expenses-amount">
            {stats.monthlyExpenses.toFixed(2)} {stats.currency}
          </h3>
          <p className="text-sm text-gray-600">إجمالي المصروفات | Total Expenses</p>
        </div>

        {/* Transactions Count */}
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="wallet-stat-transactions">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <CreditCard className="w-6 h-6 text-blue-600" />
            </div>
            <span className="text-xs text-gray-500">جميع المعاملات</span>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1" data-testid="wallet-stat-transactions-count">{stats.transactionCount}</h3>
          <p className="text-sm text-gray-600">عدد المعاملات | Transactions</p>
        </div>
      </div>

      {/* Wallet Info */}
      <div className="bg-gray-50 rounded-xl p-6" data-testid="wallet-info-section">
        <h3 className="text-lg font-bold text-gray-900 mb-4">معلومات المحفظة | Wallet Info</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div data-testid="wallet-info-id">
            <p className="text-gray-600 mb-1">معرف المحفظة</p>
            <p className="font-mono font-semibold text-gray-900">{wallet.id}</p>
          </div>
          <div data-testid="wallet-info-deposits">
            <p className="text-gray-600 mb-1">إجمالي الإيداعات</p>
            <p className="font-semibold text-green-600">
              {wallet.totalDeposits.toFixed(2)} {wallet.currency}
            </p>
          </div>
          <div data-testid="wallet-info-withdrawals">
            <p className="text-gray-600 mb-1">إجمالي السحوبات</p>
            <p className="font-semibold text-red-600">
              {wallet.totalWithdrawals.toFixed(2)} {wallet.currency}
            </p>
          </div>
          <div data-testid="wallet-info-last-transaction">
            <p className="text-gray-600 mb-1">آخر معاملة</p>
            <p className="font-semibold text-gray-900">
              {wallet.lastTransactionAt
                ? new Date(wallet.lastTransactionAt).toLocaleDateString('ar-SA')
                : '-'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WalletDashboard;
