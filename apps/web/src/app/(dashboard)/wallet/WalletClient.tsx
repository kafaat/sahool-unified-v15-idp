'use client';

/**
 * SAHOOL Wallet Page Client Component
 * صفحة المحفظة
 */

import React, { useState } from 'react';
import { ArrowUpRight, ArrowDownLeft, Send, Loader2 } from 'lucide-react';
import { WalletDashboard, TransactionHistory, TransferForm, useDeposit, useWithdraw, type PaymentMethod } from '@/features/wallet';
import { useToast } from '@/components/ui/toast';

type ViewMode = 'dashboard' | 'transfer' | 'deposit' | 'withdraw';

export default function WalletClient() {
  const [viewMode, setViewMode] = useState<ViewMode>('dashboard');
  const { showToast } = useToast();

  const deposit = useDeposit();
  const withdraw = useWithdraw();

  // Deposit form state
  const [depositAmount, setDepositAmount] = useState('');
  const [depositMethod, setDepositMethod] = useState<PaymentMethod>('bank_transfer');
  const [depositReference, setDepositReference] = useState('');

  // Withdraw form state
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [withdrawMethod, setWithdrawMethod] = useState<'bank_transfer' | 'cash'>('bank_transfer');
  const [withdrawBankAccount, setWithdrawBankAccount] = useState('');

  const handleTransferSuccess = () => {
    setViewMode('dashboard');
    // Show success notification
    showToast({
      type: 'success',
      message: 'Transfer successful',
      messageAr: 'تم التحويل بنجاح',
    });
  };

  const handleDepositClick = () => {
    setViewMode('deposit');
  };

  const handleWithdrawClick = () => {
    setViewMode('withdraw');
  };

  const handleDepositSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const amount = parseFloat(depositAmount);
    if (Number.isNaN(amount) || amount <= 0) return;
    deposit.mutate(
      {
        amount,
        paymentMethod: depositMethod,
        reference: depositReference || undefined,
      },
      {
        onSuccess: () => {
          setViewMode('dashboard');
          setDepositAmount('');
          setDepositReference('');
          showToast({
            type: 'success',
            message: 'Deposit successful',
            messageAr: 'تم الإيداع بنجاح',
          });
        },
        onError: () => {
          showToast({
            type: 'error',
            message: 'Deposit failed. Please try again.',
            messageAr: 'فشل الإيداع. يرجى المحاولة مرة أخرى.',
          });
        },
      }
    );
  };

  const handleWithdrawSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const amount = parseFloat(withdrawAmount);
    if (Number.isNaN(amount) || amount <= 0) return;
    withdraw.mutate(
      {
        amount,
        method: withdrawMethod,
        bankAccount: withdrawBankAccount || undefined,
      },
      {
        onSuccess: () => {
          setViewMode('dashboard');
          setWithdrawAmount('');
          setWithdrawBankAccount('');
          showToast({
            type: 'success',
            message: 'Withdrawal successful',
            messageAr: 'تم السحب بنجاح',
          });
        },
        onError: () => {
          showToast({
            type: 'error',
            message: 'Withdrawal failed. Please try again.',
            messageAr: 'فشل السحب. يرجى المحاولة مرة أخرى.',
          });
        },
      }
    );
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">المحفظة</h1>
            <p className="text-gray-600 mt-1">Wallet & Payments</p>
          </div>
          {viewMode !== 'dashboard' && (
            <button
              onClick={() => setViewMode('dashboard')}
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

      {viewMode === 'deposit' && (
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">إيداع</h2>
          <form onSubmit={handleDepositSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">المبلغ</label>
              <input
                type="number"
                min="1"
                step="0.01"
                required
                value={depositAmount}
                onChange={(e) => setDepositAmount(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                placeholder="أدخل المبلغ"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">طريقة الدفع</label>
              <select
                value={depositMethod}
                onChange={(e) => setDepositMethod(e.target.value as PaymentMethod)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
              >
                <option value="bank_transfer">تحويل بنكي</option>
                <option value="card">بطاقة ائتمان</option>
                <option value="cash">نقداً</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">المرجع (اختياري)</label>
              <input
                type="text"
                value={depositReference}
                onChange={(e) => setDepositReference(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                placeholder="رقم المرجع"
              />
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={deposit.isPending}
                className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold disabled:opacity-50"
              >
                {deposit.isPending ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : 'إيداع'}
              </button>
              <button
                type="button"
                onClick={() => setViewMode('dashboard')}
                className="px-6 py-3 border-2 border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
              >
                إلغاء
              </button>
            </div>
          </form>
        </div>
      )}

      {viewMode === 'withdraw' && (
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">سحب</h2>
          <form onSubmit={handleWithdrawSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">المبلغ</label>
              <input
                type="number"
                min="1"
                step="0.01"
                required
                value={withdrawAmount}
                onChange={(e) => setWithdrawAmount(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                placeholder="أدخل المبلغ"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">طريقة السحب</label>
              <select
                value={withdrawMethod}
                onChange={(e) => setWithdrawMethod(e.target.value as 'bank_transfer' | 'cash')}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
              >
                <option value="bank_transfer">تحويل بنكي</option>
                <option value="cash">نقداً</option>
              </select>
            </div>
            {withdrawMethod === 'bank_transfer' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">رقم الحساب البنكي (اختياري)</label>
                <input
                  type="text"
                  value={withdrawBankAccount}
                  onChange={(e) => setWithdrawBankAccount(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                  placeholder="أدخل رقم الحساب"
                />
              </div>
            )}
            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={withdraw.isPending}
                className="flex-1 px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-semibold disabled:opacity-50"
              >
                {withdraw.isPending ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : 'سحب'}
              </button>
              <button
                type="button"
                onClick={() => setViewMode('dashboard')}
                className="px-6 py-3 border-2 border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
              >
                إلغاء
              </button>
            </div>
          </form>
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
