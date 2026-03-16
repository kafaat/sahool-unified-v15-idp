"use client";
import * as React from "react";
import { clsx } from "clsx";

type ToastType = "success" | "error" | "info" | "warning";

interface Toast {
  id: string;
  type: ToastType;
  message: string;
  messageAr?: string;
  duration?: number;
  action?: {
    label: string;
    labelAr?: string;
    onClick: () => void;
  };
  isExiting?: boolean;
}

interface ToastContextType {
  showToast: (toast: Omit<Toast, "id">) => void;
  hideToast: (id: string) => void;
}

const ToastContext = React.createContext<ToastContextType | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<Toast[]>([]);
  const timeoutsRef = React.useRef<Map<string, NodeJS.Timeout>>(new Map());
  const exitTimeoutsRef = React.useRef<Map<string, NodeJS.Timeout>>(new Map());

  // Clean up all timeouts on unmount
  React.useEffect(() => {
    const timeouts = timeoutsRef.current;
    const exitTimeouts = exitTimeoutsRef.current;
    return () => {
      timeouts.forEach((t) => clearTimeout(t));
      exitTimeouts.forEach((t) => clearTimeout(t));
    };
  }, []);

  const hideToast = React.useCallback((id: string) => {
    // Clear the duration timeout if it exists
    const timeout = timeoutsRef.current.get(id);
    if (timeout) {
      clearTimeout(timeout);
      timeoutsRef.current.delete(id);
    }
    // Clear any existing exit timeout for this toast
    const existingExit = exitTimeoutsRef.current.get(id);
    if (existingExit) {
      clearTimeout(existingExit);
    }
    // Trigger exit animation before removal
    setToasts((prev) =>
      prev.map((toast) => (toast.id === id ? { ...toast, isExiting: true } : toast))
    );
    const exitTimeout = setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id));
      exitTimeoutsRef.current.delete(id);
    }, 200);
    exitTimeoutsRef.current.set(id, exitTimeout);
  }, []);

  const showToast = React.useCallback(
    (toast: Omit<Toast, "id">) => {
      const id = globalThis.crypto.randomUUID().substring(0, 7);
      const newToast = { ...toast, id };

      setToasts((prev) => [...prev, newToast]);

      const duration = toast.duration || 5000;
      const timeout = setTimeout(() => {
        hideToast(id);
      }, duration);

      // Store the timeout ID for cleanup
      timeoutsRef.current.set(id, timeout);
    },
    [hideToast],
  );

  const value = React.useMemo(
    () => ({ showToast, hideToast }),
    [showToast, hideToast],
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer toasts={toasts} onClose={hideToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return context;
}

interface ToastContainerProps {
  toasts: Toast[];
  onClose: (id: string) => void;
}

function ToastContainer({ toasts, onClose }: ToastContainerProps) {
  if (toasts.length === 0) return null;

  return (
    <div
      className="fixed top-4 end-4 z-50 flex flex-col gap-2 max-w-md"
      aria-live="polite"
      aria-atomic="true"
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onClose={onClose} />
      ))}
    </div>
  );
}

interface ToastItemProps {
  toast: Toast;
  onClose: (id: string) => void;
}

// Lazy-load Lucide icons. Toast icons are only rendered when a toast is
// visible (triggered by user action), so they do not need to be in the
// initial bundle. This saves ~5 KB of parsed JS on first load.
const CheckCircle = React.lazy(() => import("lucide-react").then(m => ({ default: m.CheckCircle })));
const AlertCircle = React.lazy(() => import("lucide-react").then(m => ({ default: m.AlertCircle })));
const Info = React.lazy(() => import("lucide-react").then(m => ({ default: m.Info })));
const AlertTriangle = React.lazy(() => import("lucide-react").then(m => ({ default: m.AlertTriangle })));
const X = React.lazy(() => import("lucide-react").then(m => ({ default: m.X })));

function ToastItem({ toast, onClose }: ToastItemProps) {
  const icons = {
    success: <CheckCircle className="w-5 h-5" />,
    error: <AlertCircle className="w-5 h-5" />,
    info: <Info className="w-5 h-5" />,
    warning: <AlertTriangle className="w-5 h-5" />,
  };

  const variants = {
    success: "bg-sahool-green-50 border-sahool-green-500 text-sahool-green-800",
    error: "bg-red-50 border-red-500 text-red-800",
    info: "bg-blue-50 border-blue-500 text-blue-800",
    warning: "bg-yellow-50 border-yellow-500 text-yellow-800",
  };

  return (
    <div
      className={clsx(
        "flex items-start gap-3 p-4 rounded-lg border-s-4 shadow-lg",
        toast.isExiting ? "animate-slide-out-right" : "animate-slide-in-right",
        variants[toast.type],
      )}
    >
      <React.Suspense fallback={<div className="w-5 h-5 flex-shrink-0" />}>
        <div className="flex-shrink-0 mt-0.5">{icons[toast.type]}</div>
      </React.Suspense>
      <div className="flex-1 min-w-0">
        {toast.messageAr && (
          <p className="font-semibold text-sm">{toast.messageAr}</p>
        )}
        <p
          className={clsx(
            "text-sm",
            toast.messageAr && "text-xs mt-0.5 opacity-90",
          )}
        >
          {toast.message}
        </p>
        {toast.action && (
          <button
            type="button"
            onClick={() => {
              toast.action!.onClick();
              onClose(toast.id);
            }}
            className="mt-2 text-xs font-semibold underline underline-offset-2 hover:opacity-80 transition-opacity"
          >
            {toast.action.labelAr || toast.action.label}
          </button>
        )}
      </div>
      <React.Suspense fallback={<div className="w-4 h-4" />}>
        <button
          type="button"
          onClick={() => onClose(toast.id)}
          className="flex-shrink-0 text-current opacity-50 hover:opacity-100 transition-opacity"
          aria-label="Close notification"
        >
          <X className="w-4 h-4" />
        </button>
      </React.Suspense>
    </div>
  );
}
