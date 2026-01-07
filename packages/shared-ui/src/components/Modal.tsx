'use client';

/**
 * Modal Component
 * مكون النافذة المنبثقة
 *
 * An accessible modal dialog with focus trap and keyboard support
 */

import * as React from 'react';
import { X } from 'lucide-react';
import { cn } from '@sahool/shared-utils';
import { FocusTrap } from './FocusTrap';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface ModalProps {
  /** Whether the modal is open */
  open: boolean;
  /** Callback when modal should close */
  onClose: () => void;
  /** Modal title */
  title?: string;
  /** Modal content */
  children: React.ReactNode;
  /** Modal footer content */
  footer?: React.ReactNode;
  /** Modal size */
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  /** Whether clicking outside closes the modal */
  closeOnOverlayClick?: boolean;
  /** Whether pressing Escape closes the modal */
  closeOnEscape?: boolean;
  /** Whether to show close button */
  showCloseButton?: boolean;
  /** Additional class name */
  className?: string;
}

export interface ModalFooterProps {
  children: React.ReactNode;
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Size Classes
// ═══════════════════════════════════════════════════════════════════════════

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  full: 'max-w-full mx-4',
};

// ═══════════════════════════════════════════════════════════════════════════
// Modal Footer
// ═══════════════════════════════════════════════════════════════════════════

export function ModalFooter({ children, className }: ModalFooterProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-end gap-3 px-6 py-4 bg-gray-50 border-t border-gray-200',
        className
      )}
    >
      {children}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Modal Component
// ═══════════════════════════════════════════════════════════════════════════

export function Modal({
  open,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  closeOnOverlayClick = true,
  closeOnEscape = true,
  showCloseButton = true,
  className,
}: ModalProps) {
  const modalRef = React.useRef<HTMLDivElement>(null);
  const titleId = React.useId();

  // Handle Escape key
  React.useEffect(() => {
    if (!open || !closeOnEscape) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [open, closeOnEscape, onClose]);

  // Prevent body scroll when modal is open
  React.useEffect(() => {
    if (open) {
      const originalOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = originalOverflow;
      };
    }
  }, [open]);

  // Handle overlay click
  const handleOverlayClick = (event: React.MouseEvent) => {
    if (closeOnOverlayClick && event.target === event.currentTarget) {
      onClose();
    }
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="presentation"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        aria-hidden="true"
        onClick={handleOverlayClick}
      />

      {/* Modal */}
      <FocusTrap active={open}>
        <div
          ref={modalRef}
          role="dialog"
          aria-modal="true"
          aria-labelledby={title ? titleId : undefined}
          className={cn(
            'relative z-10 w-full bg-white rounded-xl shadow-xl',
            'max-h-[90vh] overflow-hidden flex flex-col',
            sizeClasses[size],
            className
          )}
        >
          {/* Header */}
          {(title || showCloseButton) && (
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              {title && (
                <h2
                  id={titleId}
                  className="text-lg font-semibold text-gray-900"
                >
                  {title}
                </h2>
              )}
              {showCloseButton && (
                <button
                  type="button"
                  onClick={onClose}
                  className={cn(
                    'p-2 rounded-lg text-gray-400 hover:text-gray-600',
                    'hover:bg-gray-100 transition-colors',
                    'focus:outline-none focus:ring-2 focus:ring-sahool-500',
                    !title && 'ms-auto'
                  )}
                  aria-label="Close"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
          )}

          {/* Content */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            {children}
          </div>

          {/* Footer */}
          {footer}
        </div>
      </FocusTrap>
    </div>
  );
}

export default Modal;
