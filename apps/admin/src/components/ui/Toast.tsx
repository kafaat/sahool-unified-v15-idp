'use client';

/**
 * Toast Notification System
 * نظام الإشعارات المنبثقة
 *
 * Usage:
 *   import { useToast, ToastProvider } from "@/components/ui/Toast";
 *   const { toast } = useToast();
 *   toast.success("تمت العملية بنجاح");
 *   toast.error("حدث خطأ");
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  useEffect,
  useRef,
} from 'react';
import { cn } from '@/lib/utils';
import { X, CheckCircle2, AlertCircle, Info, AlertTriangle } from 'lucide-react';

// ─── Types ───────────────────────────────────────────────────────────────────

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastItem {
  id: string;
  type: ToastType;
  message: string;
  messageAr?: string;
  duration?: number;
}

interface ToastContextValue {
  toast: {
    success: (message: string, messageAr?: string) => void;
    error: (message: string, messageAr?: string) => void;
    warning: (message: string, messageAr?: string) => void;
    info: (message: string, messageAr?: string) => void;
  };
}

// ─── Context ─────────────────────────────────────────────────────────────────

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}

// ─── Toast Item Component ────────────────────────────────────────────────────

const toastConfig: Record<
  ToastType,
  { icon: React.ElementType; bg: string; border: string; text: string }
> = {
  success: {
    icon: CheckCircle2,
    bg: 'bg-green-50 dark:bg-green-900/30',
    border: 'border-green-500',
    text: 'text-green-800 dark:text-green-200',
  },
  error: {
    icon: AlertCircle,
    bg: 'bg-red-50 dark:bg-red-900/30',
    border: 'border-red-500',
    text: 'text-red-800 dark:text-red-200',
  },
  warning: {
    icon: AlertTriangle,
    bg: 'bg-yellow-50 dark:bg-yellow-900/30',
    border: 'border-yellow-500',
    text: 'text-yellow-800 dark:text-yellow-200',
  },
  info: {
    icon: Info,
    bg: 'bg-blue-50 dark:bg-blue-900/30',
    border: 'border-blue-500',
    text: 'text-blue-800 dark:text-blue-200',
  },
};

function ToastItemView({ item, onDismiss }: { item: ToastItem; onDismiss: (id: string) => void }) {
  const config = toastConfig[item.type];
  const Icon = config.icon;
  const [isExiting, setIsExiting] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  const exitTimerRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    const duration = item.duration ?? 4000;
    timerRef.current = setTimeout(() => {
      setIsExiting(true);
      exitTimerRef.current = setTimeout(() => onDismiss(item.id), 300);
    }, duration);
    return () => {
      clearTimeout(timerRef.current);
      clearTimeout(exitTimerRef.current);
    };
  }, [item.id, item.duration, onDismiss]);

  const handleDismiss = () => {
    clearTimeout(timerRef.current);
    setIsExiting(true);
    exitTimerRef.current = setTimeout(() => onDismiss(item.id), 300);
  };

  return (
    <div
      role="alert"
      aria-live="polite"
      aria-atomic="true"
      className={cn(
        'flex items-start gap-3 px-4 py-3 rounded-lg border-r-4 shadow-lg max-w-sm w-full',
        'transition-all duration-300 ease-in-out',
        isExiting ? 'opacity-0 translate-x-full' : 'opacity-100 translate-x-0 animate-slide-in',
        config.bg,
        config.border
      )}
    >
      <Icon className={cn('w-5 h-5 mt-0.5 flex-shrink-0', config.text)} />
      <div className="flex-1 min-w-0">
        {item.messageAr && (
          <p className={cn('text-sm font-medium', config.text)}>{item.messageAr}</p>
        )}
        {item.message && (
          <p className={cn('text-xs mt-0.5', config.text, 'opacity-75')}>{item.message}</p>
        )}
      </div>
      <button
        onClick={handleDismiss}
        className={cn(
          'flex-shrink-0 p-0.5 rounded hover:bg-black/10 transition-colors',
          config.text
        )}
        aria-label="إغلاق الإشعار"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}

// ─── Toast Provider ──────────────────────────────────────────────────────────

let toastCounter = 0;

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback((type: ToastType, message: string, messageAr?: string) => {
    const id = `toast-${Date.now()}-${(++toastCounter).toString(36)}`;
    setToasts((prev) => [...prev.slice(-4), { id, type, message, messageAr }]);
  }, []);

  const toast = useMemo(
    () => ({
      success: (message: string, messageAr?: string) => addToast('success', message, messageAr),
      error: (message: string, messageAr?: string) => addToast('error', message, messageAr),
      warning: (message: string, messageAr?: string) => addToast('warning', message, messageAr),
      info: (message: string, messageAr?: string) => addToast('info', message, messageAr),
    }),
    [addToast]
  );

  const value = useMemo(() => ({ toast }), [toast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      {/* Toast Container - fixed at top-left for RTL layout */}
      <div
        className="fixed top-4 left-4 z-[9999] flex flex-col gap-2 pointer-events-none"
        aria-label="الإشعارات"
      >
        {toasts.map((item) => (
          <div key={item.id} className="pointer-events-auto">
            <ToastItemView item={item} onDismiss={dismiss} />
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
