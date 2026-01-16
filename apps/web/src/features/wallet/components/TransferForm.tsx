/**
 * TransferForm Component
 * نموذج تحويل الأموال
 */

"use client";

import React, { useState } from "react";
import { Send, User, DollarSign, AlertCircle } from "lucide-react";
import { useTransfer } from "../hooks/useWallet";
import type { TransferFormData } from "../types";
import { logger } from "@/lib/logger";

interface TransferFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const TransferForm: React.FC<TransferFormProps> = ({
  onSuccess,
  onCancel,
}) => {
  const [formData, setFormData] = useState<TransferFormData>({
    recipientId: "",
    amount: 0,
    description: "",
    descriptionAr: "",
  });
  const [errors, setErrors] = useState<
    Partial<Record<keyof TransferFormData, string>>
  >({});

  const transfer = useTransfer();

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof TransferFormData, string>> = {};

    if (!formData.recipientId.trim()) {
      newErrors.recipientId = "معرف المستلم مطلوب | Recipient ID is required";
    }

    if (!formData.amount || formData.amount <= 0) {
      newErrors.amount =
        "المبلغ يجب أن يكون أكبر من صفر | Amount must be greater than zero";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      await transfer.mutateAsync(formData);
      onSuccess?.();
    } catch (error) {
      logger.error("Transfer failed:", error);
    }
  };

  const handleChange = (
    field: keyof TransferFormData,
    value: string | number,
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  const fee = formData.amount * 0.01; // 1% fee
  const total = formData.amount + fee;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          تحويل أموال | Transfer Money
        </h2>
        <p className="text-gray-600">أرسل أموال إلى مستخدم آخر</p>
      </div>

      {/* Recipient ID */}
      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">
          معرف المستلم | Recipient ID
        </label>
        <div className="relative">
          <User className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={formData.recipientId}
            onChange={(e) => handleChange("recipientId", e.target.value)}
            placeholder="أدخل معرف المستخدم..."
            className={`w-full pr-10 pl-4 py-3 border-2 rounded-lg focus:outline-none ${
              errors.recipientId
                ? "border-red-500 focus:border-red-500"
                : "border-gray-200 focus:border-blue-500"
            }`}
          />
        </div>
        {errors.recipientId && (
          <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
            <AlertCircle className="w-4 h-4" />
            {errors.recipientId}
          </p>
        )}
      </div>

      {/* Amount */}
      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">
          المبلغ | Amount (SAR)
        </label>
        <div className="relative">
          <DollarSign className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="number"
            step="0.01"
            min="0"
            value={formData.amount || ""}
            onChange={(e) =>
              handleChange("amount", parseFloat(e.target.value) || 0)
            }
            placeholder="0.00"
            className={`w-full pr-10 pl-4 py-3 border-2 rounded-lg focus:outline-none ${
              errors.amount
                ? "border-red-500 focus:border-red-500"
                : "border-gray-200 focus:border-blue-500"
            }`}
          />
        </div>
        {errors.amount && (
          <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
            <AlertCircle className="w-4 h-4" />
            {errors.amount}
          </p>
        )}
      </div>

      {/* Description (Arabic) */}
      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">
          الوصف (عربي) | Description (Arabic)
        </label>
        <input
          type="text"
          value={formData.descriptionAr || ""}
          onChange={(e) => handleChange("descriptionAr", e.target.value)}
          placeholder="اختياري..."
          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
        />
      </div>

      {/* Description (English) */}
      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">
          الوصف (إنجليزي) | Description (English)
        </label>
        <input
          type="text"
          value={formData.description || ""}
          onChange={(e) => handleChange("description", e.target.value)}
          placeholder="Optional..."
          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
        />
      </div>

      {/* Fee & Total Summary */}
      {formData.amount > 0 && (
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 space-y-2">
          <div className="flex justify-between text-sm text-gray-700">
            <span>المبلغ | Amount</span>
            <span className="font-semibold">
              {formData.amount.toFixed(2)} SAR
            </span>
          </div>
          <div className="flex justify-between text-sm text-gray-700">
            <span>الرسوم (1%) | Fee</span>
            <span className="font-semibold">{fee.toFixed(2)} SAR</span>
          </div>
          <div className="flex justify-between text-lg font-bold text-blue-600 pt-2 border-t-2 border-blue-200">
            <span>الإجمالي | Total</span>
            <span>{total.toFixed(2)} SAR</span>
          </div>
        </div>
      )}

      {/* Error Message */}
      {transfer.isError && (
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-red-700">
            <p className="font-semibold">فشل التحويل</p>
            <p>حدث خطأ أثناء معالجة التحويل. يرجى المحاولة مرة أخرى.</p>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 px-6 py-3 border-2 border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
          >
            إلغاء
          </button>
        )}
        <button
          type="submit"
          disabled={transfer.isPending}
          className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold"
        >
          {transfer.isPending ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>جارٍ التحويل...</span>
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span>تحويل الآن</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};

export default TransferForm;
