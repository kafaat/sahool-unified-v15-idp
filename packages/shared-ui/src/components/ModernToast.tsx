'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernToast Component - إشعار منبثق حديث
// Toast notifications with variants and toast manager context
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
  useEffect,
} from 'react';
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Info,
  X,
  LucideIcon,
} from 'lucide-react';

export interface Toast {
  id: string;
  title: string;
  description?: string;
  variant: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

export interface ModernToastProps extends Toast {
  onClose: (id: string) => void;
}

export interface ToastContextType {
  toasts: Toast[];
  addToast: (
    toast: Omit<Toast, 'id'> & { id?: string }
  ) => string;
  removeToast: (id: string) => void;
  success: (title: string, description?: string) => string;
  error: (title: string, description?: string) => string;
  warning: (title: string, description?: string) => string;
  info: (title: string, description?: string) => string;
}

const ToastContext = createContext<ToastContextType | null>(null);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

const variantConfig: Record<
  Toast['variant'],
  {
    icon: LucideIcon;
    classes: string;
    iconClasses: string;
  }
> = {
  success: {
    icon: CheckCircle,
    classes:
      'bg-green-50 border-green-200 text-green-900 dark:bg-green-950/50 dark:border-green-800 dark:text-green-100',
    iconClasses: 'text-green-600 dark:text-green-400',
  },
  error: {
    icon: XCircle,
    classes:
      'bg-red-50 border-red-200 text-red-900 dark:bg-red-950/50 dark:border-red-800 dark:text-red-100',
    iconClasses: 'text-red-600 dark:text-red-400',
  },
  warning: {
    icon: AlertCircle,
    classes:
      'bg-yellow-50 border-yellow-200 text-yellow-900 dark:bg-yellow-950/50 dark:border-yellow-800 dark:text-yellow-100',
    iconClasses: 'text-yellow-600 dark:text-yellow-400',
  },
  info: {
    icon: Info,
    classes:
      'bg-blue-50 border-blue-200 text-blue-900 dark:bg-blue-950/50 dark:border-blue-800 dark:text-blue-100',
    iconClasses: 'text-blue-600 dark:text-blue-400',
  },
};

const ToastItem = ({ id, title, description, variant, onClose, duration = 5000 }: ModernToastProps) => {
  const [isExiting, setIsExiting] = useState(false);
  const config = variantConfig[variant];
  const Icon = config.icon;

  useEffect(() => {
    const timer = setTimeout(() => {
      handleClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, id]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      onClose(id);
    }, 300);
  };

  return (
    <div
      role="alert"
      aria-live="polite"
      aria-atomic="true"
      className={cn(
        'flex items-start gap-3 p-4 rounded-xl border shadow-lg backdrop-blur-sm',
        'transition-all duration-300 ease-out',
        'min-w-[320px] max-w-md',
        config.classes,
        isExiting
          ? 'opacity-0 translate-x-full scale-95'
          : 'opacity-100 translate-x-0 scale-100 animate-slide-in-right'
      )}
    >
      <Icon className={cn('flex-shrink-0 mt-0.5', config.iconClasses)} size={20} aria-hidden="true" />

      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-sm leading-tight">{title}</h3>
        {description && (
          <p className="mt-1 text-sm opacity-90 leading-snug">{description}</p>
        )}
      </div>

      <button
        onClick={handleClose}
        className={cn(
          'flex-shrink-0 p-1 rounded-lg transition-colors',
          'hover:bg-black/10 dark:hover:bg-white/10',
          'focus:outline-none focus:ring-2 focus:ring-current focus:ring-offset-1'
        )}
        aria-label="Close notification"
      >
        <X size={16} />
      </button>
    </div>
  );
};

export interface ToastProviderProps {
  children: ReactNode;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  maxToasts?: number;
}

export const ToastProvider = ({
  children,
  position = 'top-right',
  maxToasts = 5,
}: ToastProviderProps) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback(
    (toast: Omit<Toast, 'id'> & { id?: string }): string => {
      const id = toast.id || Math.random().toString(36).substring(2, 9);
      const newToast: Toast = {
        ...toast,
        id,
        duration: toast.duration || 5000,
      };

      setToasts((prev) => {
        const updated = [newToast, ...prev];
        return updated.slice(0, maxToasts);
      });

      return id;
    },
    [maxToasts]
  );

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const success = useCallback(
    (title: string, description?: string) =>
      addToast({ title, description, variant: 'success' }),
    [addToast]
  );

  const error = useCallback(
    (title: string, description?: string) =>
      addToast({ title, description, variant: 'error' }),
    [addToast]
  );

  const warning = useCallback(
    (title: string, description?: string) =>
      addToast({ title, description, variant: 'warning' }),
    [addToast]
  );

  const info = useCallback(
    (title: string, description?: string) =>
      addToast({ title, description, variant: 'info' }),
    [addToast]
  );

  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
  };

  return (
    <ToastContext.Provider
      value={{ toasts, addToast, removeToast, success, error, warning, info }}
    >
      {children}
      <div
        className={cn(
          'fixed z-50 flex flex-col gap-2',
          positionClasses[position]
        )}
        aria-label="Notifications"
      >
        {toasts.map((toast) => (
          <ToastItem key={toast.id} {...toast} onClose={removeToast} />
        ))}
      </div>
    </ToastContext.Provider>
  );
};

// Standalone toast component export for direct usage
export const ModernToast = ToastItem;
