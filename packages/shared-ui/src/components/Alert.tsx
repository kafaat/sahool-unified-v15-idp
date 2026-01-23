"use client";

// ═══════════════════════════════════════════════════════════════════════════════
// Alert Component - تنبيه
// Unified alert component for notifications and messages
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from "@sahool/shared-utils";
import { forwardRef, HTMLAttributes, ReactNode } from "react";
import { AlertCircle, AlertTriangle, CheckCircle, Info, X } from "lucide-react";

/** Alert type variants */
export type AlertType = "info" | "success" | "warning" | "error";

export interface AlertProps extends Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  /** Type/severity of the alert */
  type: AlertType;
  /** Optional title for the alert */
  title?: string;
  /** Alert content/message */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Whether the alert can be dismissed */
  dismissible?: boolean;
  /** Callback when dismiss button is clicked */
  onDismiss?: () => void;
  /** Accessible label for dismiss button */
  dismissLabel?: string;
}

const typeClasses = {
  info: "bg-blue-50 border-blue-200 text-blue-800",
  success: "bg-green-50 border-green-200 text-green-800",
  warning: "bg-yellow-50 border-yellow-200 text-yellow-800",
  error: "bg-red-50 border-red-200 text-red-800",
};

const iconClasses = {
  info: "text-blue-500",
  success: "text-green-500",
  warning: "text-yellow-500",
  error: "text-red-500",
};

const TypeIcon = {
  info: Info,
  success: CheckCircle,
  warning: AlertTriangle,
  error: AlertCircle,
};

export const Alert = forwardRef<HTMLDivElement, AlertProps>(
  (
    {
      type,
      title,
      children,
      className = "",
      dismissible = false,
      onDismiss,
      dismissLabel = "إغلاق التنبيه",
      ...props
    },
    ref,
  ) => {
    const Icon = TypeIcon[type];

    return (
      <div
        ref={ref}
        className={cn(
          "flex gap-3 p-4 rounded-lg border",
          typeClasses[type],
          className,
        )}
        role="alert"
        aria-live={type === "error" ? "assertive" : "polite"}
        {...props}
      >
        <Icon
          className={cn("w-5 h-5 flex-shrink-0 mt-0.5", iconClasses[type])}
          aria-hidden="true"
        />

        <div className="flex-1">
          {title && <h4 className="font-semibold mb-1">{title}</h4>}
          <div className="text-sm">{children}</div>
        </div>

        {dismissible && onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            className={cn(
              "flex-shrink-0 p-1 rounded transition-colors",
              "hover:opacity-70",
              "focus:outline-none focus:ring-2 focus:ring-offset-2",
              type === "info" && "focus:ring-blue-500",
              type === "success" && "focus:ring-green-500",
              type === "warning" && "focus:ring-yellow-500",
              type === "error" && "focus:ring-red-500",
            )}
            aria-label={dismissLabel}
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        )}
      </div>
    );
  },
);

Alert.displayName = "Alert";
