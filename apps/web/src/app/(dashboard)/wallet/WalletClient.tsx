"use client";

/**
 * SAHOOL Wallet Page Client Component
 * صفحة المحفظة
 */

import React, { useState } from "react";
import { ArrowUpRight, ArrowDownLeft, Send, Loader2 } from "lucide-react";
import {
  WalletDashboard,
  TransactionHistory,
  TransferForm,
} from "@/features/wallet";
import { useDeposit, useWithdraw } from "@/features/wallet/hooks/useWallet";
import { useToast } from "@/components/ui/toast";

type ViewMode = "dashboard" | "transfer" | "deposit" | "withdraw";

export default function WalletClient() {
  const [viewMode, setViewMode] = useState<ViewMode>("dashboard");
  const [showComingSoon, setShowComingSoon] = useState<{
    type: "deposit" | "withdraw" | null;
  }>({ type: null });
  const { showToast } = useToast();
  const depositMutation = useDeposit();
  const withdrawMutation = useWithdraw();

  // Feature flags - enabled, backed by wallet API
  const isDepositEnabled = true;
  const isWithdrawEnabled = true;

  const handleTransferSuccess = () => {
    setViewMode("dashboard");
    // Show success notification
    showToast({
      type: "success",
      message: "Transfer successful",
      messageAr: "تم التحويل بنجاح",
    });
  };

  const handleDepositClick = () => {
    if (isDepositEnabled) {
      setViewMode("deposit");
    } else {
      setShowComingSoon({ type: "deposit" });
      setTimeout(() => setShowComingSoon({ type: null }), 3000);
    }
  };

  const handleWithdrawClick = () => {
    if (isWithdrawEnabled) {
      setViewMode("withdraw");
    } else {
      setShowComingSoon({ type: "withdraw" });
      setTimeout(() => setShowComingSoon({ type: null }), 3000);
    }
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
          {viewMode !== "dashboard" && (
            <button
              onClick={() => setViewMode("dashboard")}
              className="px-6 py-3 border-2 border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
            >
              رجوع إلى المحفظة
            </button>
          )}
        </div>
      </div>

      {/* Main Content */}
      {viewMode === "dashboard" && (
        <>
          {/* Wallet Dashboard */}
          <WalletDashboard
            onTransferClick={() => setViewMode("transfer")}
            onDepositClick={handleDepositClick}
            onWithdrawClick={handleWithdrawClick}
          />

          {/* Transaction History */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <TransactionHistory />
          </div>
        </>
      )}

      {viewMode === "transfer" && (
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <TransferForm
            onSuccess={handleTransferSuccess}
            onCancel={() => setViewMode("dashboard")}
          />
        </div>
      )}

      {viewMode === "deposit" && (
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">إيداع | Deposit</h2>
          <form onSubmit={async (e) => {
            e.preventDefault();
            const fd = new FormData(e.currentTarget);
            try {
              await depositMutation.mutateAsync({
                amount: Number(fd.get("amount")),
                paymentMethod: "bank_transfer",
                reference: fd.get("description") as string || "",
              });
              setViewMode("dashboard");
              showToast({ type: "success", message: "Deposit successful", messageAr: "تم الإيداع بنجاح" });
            } catch {
              showToast({ type: "error", message: "Deposit failed", messageAr: "فشل الإيداع" });
            }
          }} className="space-y-4 max-w-md">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">المبلغ (ريال يمني) *</label>
              <input name="amount" type="number" min="1" required className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الوصف</label>
              <input name="description" className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" placeholder="سبب الإيداع..." />
            </div>
            <div className="flex gap-3">
              <button type="button" onClick={() => setViewMode("dashboard")} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">إلغاء</button>
              <button type="submit" disabled={depositMutation.isPending} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2">
                {depositMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                إيداع
              </button>
            </div>
          </form>
        </div>
      )}

      {viewMode === "withdraw" && (
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">سحب | Withdraw</h2>
          <form onSubmit={async (e) => {
            e.preventDefault();
            const fd = new FormData(e.currentTarget);
            try {
              await withdrawMutation.mutateAsync({
                amount: Number(fd.get("amount")),
                method: "bank_transfer",
                bankAccount: fd.get("accountDetails") as string || "",
              });
              setViewMode("dashboard");
              showToast({ type: "success", message: "Withdrawal successful", messageAr: "تم السحب بنجاح" });
            } catch {
              showToast({ type: "error", message: "Withdrawal failed", messageAr: "فشل السحب" });
            }
          }} className="space-y-4 max-w-md">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">المبلغ (ريال يمني) *</label>
              <input name="amount" type="number" min="1" required className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">تفاصيل الحساب</label>
              <input name="accountDetails" className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" placeholder="رقم الحساب البنكي..." />
            </div>
            <div className="flex gap-3">
              <button type="button" onClick={() => setViewMode("dashboard")} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">إلغاء</button>
              <button type="submit" disabled={withdrawMutation.isPending} className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 flex items-center gap-2">
                {withdrawMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                سحب
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Quick Actions Floating Button (Mobile) */}
      <div className="fixed bottom-6 left-6 md:hidden flex flex-col gap-3">
        <button
          onClick={() => setViewMode("transfer")}
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

      {/* Coming Soon Notification */}
      {showComingSoon.type && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 animate-fade-in">
          <div className="bg-blue-600 text-white px-6 py-4 rounded-lg shadow-xl border-2 border-blue-500">
            <div className="flex items-center gap-3">
              <div className="text-2xl">🚀</div>
              <div>
                <p className="font-bold">
                  {showComingSoon.type === "deposit"
                    ? "قريباً: ميزة الإيداع"
                    : "قريباً: ميزة السحب"}
                </p>
                <p className="text-sm opacity-90">
                  {showComingSoon.type === "deposit"
                    ? "Coming Soon: Deposit Feature"
                    : "Coming Soon: Withdrawal Feature"}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
