"use client";

/**
 * Confirm Dialog Component
 * حوار التأكيد للعمليات الحساسة
 */

import React, { useEffect, useRef, useCallback } from "react";
import { cn } from "@/lib/utils";
import { AlertTriangle, Trash2, Info } from "lucide-react";

type DialogVariant = "danger" | "warning" | "info";

interface ConfirmDialogProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  title: string;
  titleAr?: string;
  message: string;
  messageAr?: string;
  confirmLabel?: string;
  confirmLabelAr?: string;
  cancelLabel?: string;
  cancelLabelAr?: string;
  variant?: DialogVariant;
  isLoading?: boolean;
}

const variantConfig: Record<
  DialogVariant,
  { icon: React.ElementType; iconBg: string; iconColor: string; btnColor: string }
> = {
  danger: {
    icon: Trash2,
    iconBg: "bg-red-100 dark:bg-red-900/30",
    iconColor: "text-red-600 dark:text-red-400",
    btnColor: "bg-red-600 hover:bg-red-700 focus:ring-red-500",
  },
  warning: {
    icon: AlertTriangle,
    iconBg: "bg-yellow-100 dark:bg-yellow-900/30",
    iconColor: "text-yellow-600 dark:text-yellow-400",
    btnColor: "bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500",
  },
  info: {
    icon: Info,
    iconBg: "bg-blue-100 dark:bg-blue-900/30",
    iconColor: "text-blue-600 dark:text-blue-400",
    btnColor: "bg-blue-600 hover:bg-blue-700 focus:ring-blue-500",
  },
};

export default function ConfirmDialog({
  isOpen,
  onConfirm,
  onCancel,
  title,
  titleAr,
  message,
  messageAr,
  confirmLabel = "Confirm",
  confirmLabelAr = "تأكيد",
  cancelLabel = "Cancel",
  cancelLabelAr = "إلغاء",
  variant = "danger",
  isLoading = false,
}: ConfirmDialogProps) {
  const cancelRef = useRef<HTMLButtonElement>(null);
  const dialogRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const config = variantConfig[variant];
  const Icon = config.icon;

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement | null;
      cancelRef.current?.focus();
    } else if (previousFocusRef.current) {
      previousFocusRef.current.focus();
      previousFocusRef.current = null;
    }
  }, [isOpen]);

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (!isOpen) return;

    if (e.key === "Escape" && !isLoading) {
      onCancel();
      return;
    }

    if (e.key === "Tab" && dialogRef.current) {
      const focusable = dialogRef.current.querySelectorAll<HTMLElement>(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      if (focusable.length === 0) return;

      const first = focusable[0] as HTMLElement | undefined;
      const last = focusable[focusable.length - 1] as HTMLElement | undefined;
      if (!first || !last) return;

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }, [isOpen, isLoading, onCancel]);

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[9998] flex items-center justify-center"
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="confirm-title"
      aria-describedby="confirm-message"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm animate-fade-in"
        onClick={() => !isLoading && onCancel()}
      />

      {/* Dialog */}
      <div ref={dialogRef} className="relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md w-full mx-4 p-6 animate-scale-in">
        <div className="flex flex-col items-center text-center">
          {/* Icon */}
          <div
            className={cn(
              "w-14 h-14 rounded-full flex items-center justify-center mb-4",
              config.iconBg,
            )}
          >
            <Icon className={cn("w-7 h-7", config.iconColor)} />
          </div>

          {/* Title */}
          <h3
            id="confirm-title"
            className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2"
          >
            {titleAr || title}
          </h3>

          {/* Message */}
          <p
            id="confirm-message"
            className="text-sm text-gray-600 dark:text-gray-400 mb-6 leading-relaxed"
          >
            {messageAr || message}
          </p>

          {/* Actions */}
          <div className="flex gap-3 w-full">
            <button
              ref={cancelRef}
              onClick={onCancel}
              disabled={isLoading}
              className="flex-1 px-4 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition disabled:opacity-50"
            >
              {cancelLabelAr || cancelLabel}
            </button>
            <button
              onClick={onConfirm}
              disabled={isLoading}
              className={cn(
                "flex-1 px-4 py-2.5 text-sm font-medium text-white rounded-lg focus:ring-2 focus:ring-offset-2 transition disabled:opacity-50 flex items-center justify-center gap-2",
                config.btnColor,
              )}
            >
              {isLoading && (
                <svg
                  className="animate-spin w-4 h-4"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
              )}
              {confirmLabelAr || confirmLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
