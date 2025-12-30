'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernModal Component - نافذة منبثقة حديثة
// Glass effect modal with smooth animations and focus management
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { ReactNode, useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import { FocusTrap } from './FocusTrap';

export interface ModernModalProps {
  open: boolean;
  onClose: () => void;
  title?: string | ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  variant?: 'default' | 'glass' | 'gradient';
  closeOnBackdrop?: boolean;
  closeOnEscape?: boolean;
  showCloseButton?: boolean;
  blur?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  contentClassName?: string;
  overlayClassName?: string;
}

const sizeClasses = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
  full: 'max-w-[95vw] max-h-[95vh]',
};

const blurClasses = {
  sm: 'backdrop-blur-sm',
  md: 'backdrop-blur-md',
  lg: 'backdrop-blur-lg',
  xl: 'backdrop-blur-xl',
};

export function ModernModal({
  open,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  variant = 'default',
  closeOnBackdrop = true,
  closeOnEscape = true,
  showCloseButton = true,
  blur = 'md',
  className = '',
  contentClassName = '',
  overlayClassName = '',
}: ModernModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  // Handle Escape key
  useEffect(() => {
    if (!open || !closeOnEscape) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [open, closeOnEscape, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (open) {
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
      document.body.style.overflow = 'hidden';
      document.body.style.paddingRight = `${scrollbarWidth}px`;
    } else {
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    }

    return () => {
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    };
  }, [open]);

  if (!open) return null;

  const handleBackdropClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (closeOnBackdrop && event.target === event.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className={cn(
        'fixed inset-0 z-50 flex items-center justify-center p-4',
        'animate-in fade-in duration-200'
      )}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
    >
      {/* Backdrop */}
      <div
        className={cn(
          'absolute inset-0 bg-black/50 dark:bg-black/70',
          blurClasses[blur],
          'animate-in fade-in duration-200',
          overlayClassName
        )}
        onClick={handleBackdropClick}
        aria-hidden="true"
      />

      {/* Modal Content */}
      <FocusTrap>
        <div
          ref={modalRef}
          className={cn(
            'relative w-full mx-auto',
            'animate-in zoom-in-95 slide-in-from-bottom-4 duration-300',
            sizeClasses[size],
            className
          )}
        >
          <div
            className={cn(
              'relative rounded-2xl shadow-2xl overflow-hidden',
              'transform transition-all',

              // Variant-specific styles
              variant === 'default' &&
                'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700',
              variant === 'glass' &&
                cn(
                  'bg-white/80 dark:bg-gray-900/80',
                  'backdrop-blur-xl',
                  'border border-white/20 dark:border-white/10'
                ),
              variant === 'gradient' &&
                cn(
                  'bg-gradient-to-br from-white via-sahool-50/30 to-purple-50/30',
                  'dark:from-gray-900 dark:via-sahool-950/30 dark:to-purple-950/30',
                  'border border-sahool-200/50 dark:border-sahool-800/50'
                ),
              contentClassName
            )}
          >
            {/* Header */}
            {(title || showCloseButton) && (
              <div
                className={cn(
                  'flex items-center justify-between gap-4',
                  'px-6 py-4 border-b border-gray-200 dark:border-gray-700',
                  variant === 'glass' && 'border-white/20 dark:border-white/10'
                )}
              >
                {title && (
                  <h2
                    id="modal-title"
                    className="text-xl font-semibold text-gray-900 dark:text-gray-100"
                  >
                    {title}
                  </h2>
                )}
                {showCloseButton && (
                  <button
                    onClick={onClose}
                    className={cn(
                      'ml-auto p-2 rounded-lg',
                      'text-gray-500 hover:text-gray-700',
                      'dark:text-gray-400 dark:hover:text-gray-200',
                      'hover:bg-gray-100 dark:hover:bg-gray-800',
                      'focus:outline-none focus:ring-2 focus:ring-sahool-500',
                      'transition-all duration-200'
                    )}
                    aria-label="Close modal"
                  >
                    <X size={20} />
                  </button>
                )}
              </div>
            )}

            {/* Body */}
            <div className="px-6 py-4 max-h-[calc(100vh-16rem)] overflow-y-auto">
              {children}
            </div>

            {/* Footer */}
            {footer && (
              <div
                className={cn(
                  'px-6 py-4 border-t border-gray-200 dark:border-gray-700',
                  'bg-gray-50 dark:bg-gray-800/50',
                  variant === 'glass' && 'bg-white/50 dark:bg-gray-800/30 border-white/20 dark:border-white/10'
                )}
              >
                {footer}
              </div>
            )}
          </div>
        </div>
      </FocusTrap>
    </div>
  );
}

ModernModal.displayName = 'ModernModal';
