'use client';
import * as React from 'react';
import { clsx } from 'clsx';
import { X } from 'lucide-react';
import FocusLock from 'react-focus-lock';

export interface ModalProps extends React.HTMLAttributes<HTMLDivElement> {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  titleAr?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  closeOnOverlay?: boolean;
  showCloseButton?: boolean;
  /** Optional description ID for aria-describedby */
  descriptionId?: string;
}

export function Modal({
  isOpen,
  onClose,
  title,
  titleAr,
  size = 'md',
  closeOnOverlay = true,
  showCloseButton = true,
  descriptionId,
  children,
  className,
  ...props
}: ModalProps) {
  const modalRef = React.useRef<HTMLDivElement>(null);
  const titleId = React.useId();

  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4',
  };

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (closeOnOverlay && e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <FocusLock returnFocus>
      <div
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
        onClick={handleOverlayClick}
        aria-hidden="true"
      >
        <div
          ref={modalRef}
          role="dialog"
          aria-modal="true"
          aria-labelledby={(title || titleAr) ? titleId : undefined}
          aria-describedby={descriptionId}
          className={clsx(
            'relative bg-white rounded-lg shadow-xl w-full',
            sizes[size],
            'max-h-[90vh] flex flex-col',
            className
          )}
          {...props}
        >
          {/* Header */}
          {(title || titleAr || showCloseButton) && (
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              {(title || titleAr) && (
                <h2 id={titleId} className="text-xl font-bold text-gray-900">
                  <span className="text-gray-900">{titleAr}</span>
                  {titleAr && title && <span className="mx-2">•</span>}
                  {title && <span className="text-gray-600 text-base">{title}</span>}
                </h2>
              )}
              {showCloseButton && (
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-lg hover:bg-gray-100"
                  aria-label="Close"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
          )}

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {children}
          </div>
        </div>
      </div>
    </FocusLock>
  );
}

export function ModalFooter({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={clsx(
        'flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50',
        className
      )}
      {...props}
    />
  );
}

ModalFooter.displayName = 'ModalFooter';
