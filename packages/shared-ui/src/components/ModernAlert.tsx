'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernAlert Component - تنبيه حديث
// Alert banner with dismiss animation and variants
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { ReactNode, useState, forwardRef } from 'react';
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Info,
  X,
  LucideIcon,
} from 'lucide-react';

export interface ModernAlertProps {
  variant?: 'success' | 'error' | 'warning' | 'info';
  title: string;
  description?: string;
  children?: ReactNode;
  dismissible?: boolean;
  onDismiss?: () => void;
  icon?: LucideIcon | false;
  className?: string;
  actions?: ReactNode;
}

const variantConfig: Record<
  NonNullable<ModernAlertProps['variant']>,
  {
    icon: LucideIcon;
    classes: string;
    iconClasses: string;
    borderClasses: string;
  }
> = {
  success: {
    icon: CheckCircle,
    classes:
      'bg-green-50 text-green-900 dark:bg-green-950/30 dark:text-green-100',
    iconClasses: 'text-green-600 dark:text-green-400',
    borderClasses: 'border-l-green-600 dark:border-l-green-500',
  },
  error: {
    icon: XCircle,
    classes:
      'bg-red-50 text-red-900 dark:bg-red-950/30 dark:text-red-100',
    iconClasses: 'text-red-600 dark:text-red-400',
    borderClasses: 'border-l-red-600 dark:border-l-red-500',
  },
  warning: {
    icon: AlertCircle,
    classes:
      'bg-yellow-50 text-yellow-900 dark:bg-yellow-950/30 dark:text-yellow-100',
    iconClasses: 'text-yellow-600 dark:text-yellow-400',
    borderClasses: 'border-l-yellow-600 dark:border-l-yellow-500',
  },
  info: {
    icon: Info,
    classes:
      'bg-blue-50 text-blue-900 dark:bg-blue-950/30 dark:text-blue-100',
    iconClasses: 'text-blue-600 dark:text-blue-400',
    borderClasses: 'border-l-blue-600 dark:border-l-blue-500',
  },
};

export const ModernAlert = forwardRef<HTMLDivElement, ModernAlertProps>(
  (
    {
      variant = 'info',
      title,
      description,
      children,
      dismissible = false,
      onDismiss,
      icon,
      className = '',
      actions,
    },
    ref
  ) => {
    const [isVisible, setIsVisible] = useState(true);
    const [isExiting, setIsExiting] = useState(false);

    const config = variantConfig[variant];
    const Icon = icon === false ? null : icon || config.icon;

    const handleDismiss = () => {
      setIsExiting(true);
      setTimeout(() => {
        setIsVisible(false);
        onDismiss?.();
      }, 300);
    };

    if (!isVisible) return null;

    return (
      <div
        ref={ref}
        role="alert"
        aria-live="polite"
        className={cn(
          'relative flex gap-3 p-4 rounded-xl border-l-4 shadow-sm',
          'transition-all duration-300 ease-out',
          config.classes,
          config.borderClasses,
          isExiting
            ? 'opacity-0 -translate-y-2 scale-95'
            : 'opacity-100 translate-y-0 scale-100 animate-slide-down',
          className
        )}
      >
        {Icon && (
          <Icon
            className={cn('flex-shrink-0 mt-0.5', config.iconClasses)}
            size={20}
            aria-hidden="true"
          />
        )}

        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm leading-tight mb-1">{title}</h3>

          {description && (
            <p className="text-sm opacity-90 leading-relaxed mb-2">
              {description}
            </p>
          )}

          {children && (
            <div className="text-sm leading-relaxed">{children}</div>
          )}

          {actions && (
            <div className="mt-3 flex gap-2">{actions}</div>
          )}
        </div>

        {dismissible && (
          <button
            onClick={handleDismiss}
            className={cn(
              'flex-shrink-0 p-1 rounded-lg transition-colors h-fit',
              'hover:bg-black/10 dark:hover:bg-white/10',
              'focus:outline-none focus:ring-2 focus:ring-current focus:ring-offset-1'
            )}
            aria-label="Dismiss alert"
          >
            <X size={16} />
          </button>
        )}
      </div>
    );
  }
);

ModernAlert.displayName = 'ModernAlert';
