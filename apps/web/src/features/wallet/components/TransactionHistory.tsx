/**
 * TransactionHistory Component
 * سجل المعاملات
 */

'use client';

import React, { useState } from 'react';
import {
  ArrowUpRight,
  ArrowDownLeft,
  CreditCard,
  Search,
  Filter,
  Calendar,
} from 'lucide-react';
import { useTransactions } from '../hooks/useWallet';
import type { Transaction, TransactionFilters, TransactionType } from '../types';

interface TransactionHistoryProps {
  onTransactionClick?: (transactionId: string) => void;
}

export const TransactionHistory: React.FC<TransactionHistoryProps> = ({ onTransactionClick }) => {
  const [filters, setFilters] = useState<TransactionFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  const { data: transactions, isLoading } = useTransactions(filters);

  const handleTypeFilter = (type?: TransactionType) => {
    setFilters((prev) => ({ ...prev, type }));
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-20 bg-gray-200 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h2 className="text-2xl font-bold">سجل المعاملات | Transaction History</h2>

        <div className="flex items-center gap-2">
          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 px-4 py-2 border-2 border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <Filter className="w-5 h-5" />
            <span>فلتر</span>
          </button>
        </div>
      </div>

      {/* Type Filters */}
      {showFilters && (
        <div className="flex flex-wrap gap-2 p-4 bg-gray-50 rounded-lg">
          <button
            onClick={() => handleTypeFilter(undefined)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              !filters.type
                ? 'bg-blue-600 text-white'
                : 'bg-white border-2 border-gray-200 hover:border-blue-400'
            }`}
          >
            الكل
          </button>
          <button
            onClick={() => handleTypeFilter('deposit')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filters.type === 'deposit'
                ? 'bg-blue-600 text-white'
                : 'bg-white border-2 border-gray-200 hover:border-blue-400'
            }`}
          >
            إيداع
          </button>
          <button
            onClick={() => handleTypeFilter('withdrawal')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filters.type === 'withdrawal'
                ? 'bg-blue-600 text-white'
                : 'bg-white border-2 border-gray-200 hover:border-blue-400'
            }`}
          >
            سحب
          </button>
          <button
            onClick={() => handleTypeFilter('payment')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filters.type === 'payment'
                ? 'bg-blue-600 text-white'
                : 'bg-white border-2 border-gray-200 hover:border-blue-400'
            }`}
          >
            دفع
          </button>
          <button
            onClick={() => handleTypeFilter('transfer_out')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filters.type === 'transfer_out'
                ? 'bg-blue-600 text-white'
                : 'bg-white border-2 border-gray-200 hover:border-blue-400'
            }`}
          >
            تحويل
          </button>
        </div>
      )}

      {/* Transactions List */}
      {!transactions || transactions.length === 0 ? (
        <div className="text-center py-16">
          <CreditCard className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">لا توجد معاملات</h3>
          <p className="text-gray-500">لم يتم العثور على معاملات بالفلاتر المحددة</p>
        </div>
      ) : (
        <div className="space-y-3">
          {transactions.map((transaction) => (
            <TransactionItem
              key={transaction.id}
              transaction={transaction}
              onClick={() => onTransactionClick?.(transaction.id)}
            />
          ))}

          {/* Results Count */}
          <div className="text-center text-sm text-gray-500 pt-4">
            عرض {transactions.length} معاملة | Showing {transactions.length} transactions
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Transaction Item Component
 */
interface TransactionItemProps {
  transaction: Transaction;
  onClick?: () => void;
}

const TransactionItem: React.FC<TransactionItemProps> = ({ transaction, onClick }) => {
  const isIncoming = ['deposit', 'transfer_in', 'refund'].includes(transaction.type);
  const isOutgoing = ['withdrawal', 'payment', 'transfer_out'].includes(transaction.type);

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl border-2 border-gray-200 hover:border-blue-400 p-4 cursor-pointer transition-all"
    >
      <div className="flex items-center justify-between gap-4">
        {/* Icon & Details */}
        <div className="flex items-center gap-4 flex-1 min-w-0">
          {/* Icon */}
          <div
            className={`p-3 rounded-lg ${
              isIncoming
                ? 'bg-green-100 text-green-600'
                : isOutgoing
                ? 'bg-red-100 text-red-600'
                : 'bg-blue-100 text-blue-600'
            }`}
          >
            {isIncoming ? (
              <ArrowDownLeft className="w-6 h-6" />
            ) : isOutgoing ? (
              <ArrowUpRight className="w-6 h-6" />
            ) : (
              <CreditCard className="w-6 h-6" />
            )}
          </div>

          {/* Details */}
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-gray-900 line-clamp-1">{transaction.descriptionAr}</h4>
            <p className="text-sm text-gray-600 line-clamp-1">{transaction.description}</p>
            <div className="flex items-center gap-2 mt-1">
              <span
                className={`text-xs px-2 py-1 rounded-full ${
                  transaction.status === 'completed'
                    ? 'bg-green-100 text-green-700'
                    : transaction.status === 'pending'
                    ? 'bg-yellow-100 text-yellow-700'
                    : transaction.status === 'failed'
                    ? 'bg-red-100 text-red-700'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {getStatusLabel(transaction.status)}
              </span>
              <span className="text-xs text-gray-500">
                {new Date(transaction.createdAt).toLocaleDateString('ar-SA')}
              </span>
            </div>
          </div>
        </div>

        {/* Amount */}
        <div className="text-right">
          <div
            className={`text-lg font-bold ${
              isIncoming ? 'text-green-600' : isOutgoing ? 'text-red-600' : 'text-gray-900'
            }`}
          >
            {isIncoming ? '+' : isOutgoing ? '-' : ''}
            {transaction.amount.toFixed(2)} {transaction.currency}
          </div>
          {transaction.fee && transaction.fee > 0 && (
            <div className="text-xs text-gray-500">رسوم: {transaction.fee.toFixed(2)}</div>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Get status label in Arabic
 */
function getStatusLabel(status: Transaction['status']): string {
  const labels: Record<typeof status, string> = {
    pending: 'قيد الانتظار',
    completed: 'مكتمل',
    failed: 'فشل',
    cancelled: 'ملغي',
  };
  return labels[status] || status;
}

export default TransactionHistory;
