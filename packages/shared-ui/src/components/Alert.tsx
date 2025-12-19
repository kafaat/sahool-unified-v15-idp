'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// Alert Component - تنبيه
// Unified alert component for notifications and messages
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { ReactNode } from 'react';
import { AlertCircle, AlertTriangle, CheckCircle, Info, X } from 'lucide-react';

export interface AlertProps {
  type: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  children: ReactNode;
  className?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
}

const typeClasses = {
  info: 'bg-blue-50 border-blue-200 text-blue-800',
  success: 'bg-green-50 border-green-200 text-green-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  error: 'bg-red-50 border-red-200 text-red-800',
};

const iconClasses = {
  info: 'text-blue-500',
  success: 'text-green-500',
  warning: 'text-yellow-500',
  error: 'text-red-500',
};

const TypeIcon = {
  info: Info,
  success: CheckCircle,
  warning: AlertTriangle,
  error: AlertCircle,
};

export function Alert({
  type,
  title,
  children,
  className = '',
  dismissible = false,
  onDismiss,
}: AlertProps) {
  const Icon = TypeIcon[type];

  return (
    <div
      className={cn(
        'flex gap-3 p-4 rounded-lg border',
        typeClasses[type],
        className
      )}
      role="alert"
    >
      <Icon className={cn('w-5 h-5 flex-shrink-0 mt-0.5', iconClasses[type])} />

      <div className="flex-1">
        {title && <h4 className="font-semibold mb-1">{title}</h4>}
        <div className="text-sm">{children}</div>
      </div>

      {dismissible && onDismiss && (
        <button
          onClick={onDismiss}
          className="flex-shrink-0 hover:opacity-70 transition-opacity"
          aria-label="Dismiss"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
