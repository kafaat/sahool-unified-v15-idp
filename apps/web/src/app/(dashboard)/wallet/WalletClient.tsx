'use client';

/**
 * SAHOOL Wallet Page Client Component
 * صفحة المحفظة
 */

import React, { useState } from 'react';
import { ArrowUpRight, ArrowDownLeft, Send } from 'lucide-react';
import {
  WalletDashboard,
  TransactionHistory,
  TransferForm,
} from '@/features/wallet';

type ViewMode = 'dashboard' | 'transfer' | 'deposit' | 'withdraw';

export default function WalletClient() {
  const [viewMode, setViewMode] = useState<ViewMode>('dashboard');

  const handleTransferSuccess = () => {
    setViewMode('dashboard');
    // Show success notification
    alert('تم التحويل بنجاح | Transfer successful');
  };

  const handleDepositClick = () => {
    // TODO: Implement deposit flow
    alert('ميزة الإيداع قيد التطوير | Deposit feature coming soon');
  };

  const handleWithdrawClick = () => {
    // TODO: Implement withdrawal flow
    alert('ميزة السحب قيد التطوير | Withdrawal feature coming soon');
  };

  return (
    <div className="space-y-6" data-testid="wallet-page">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="wallet-page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900" data-testid="wallet-page-title">المحفظة</h1>
            <p className="text-gray-600 mt-1" data-testid="wallet-page-subtitle">Wallet & Payments</p>
          </div>
          {viewMode !== 'dashboard' && (
            <button
              onClick={() => setViewMode('dashboard')}
              data-testid="wallet-back-button"
              className="px-6 py-3 border-2 border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
            >
              رجوع إلى المحفظة
            </button>
          )}
        </div>
      </div>

      {/* Main Content */}
      {viewMode === 'dashboard' && (
        <>
          {/* Wallet Dashboard */}
          <WalletDashboard
            onTransferClick={() => setViewMode('transfer')}
            onDepositClick={handleDepositClick}
            onWithdrawClick={handleWithdrawClick}
          />

          {/* Transaction History */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <TransactionHistory />
          </div>
        </>
      )}

      {viewMode === 'transfer' && (
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <TransferForm
            onSuccess={handleTransferSuccess}
            onCancel={() => setViewMode('dashboard')}
          />
        </div>
      )}

      {/* Quick Actions Floating Button (Mobile) */}
      <div className="fixed bottom-6 left-6 md:hidden flex flex-col gap-3">
        <button
          onClick={() => setViewMode('transfer')}
          className="w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all flex items-center justify-center"
          title="تحويل"
        >
          <Send className="w-6 h-6" />
        </button>
        <button
          onClick={handleDepositClick}
          className="w-14 h-14 bg-green-600 text-white rounded-full shadow-lg hover:bg-green-700 transition-all flex items-center justify-center"
          title="إيداع"
        >
          <ArrowDownLeft className="w-6 h-6" />
        </button>
        <button
          onClick={handleWithdrawClick}
          className="w-14 h-14 bg-orange-600 text-white rounded-full shadow-lg hover:bg-orange-700 transition-all flex items-center justify-center"
          title="سحب"
        >
          <ArrowUpRight className="w-6 h-6" />
        </button>
      </div>
    </div>
  );
}
