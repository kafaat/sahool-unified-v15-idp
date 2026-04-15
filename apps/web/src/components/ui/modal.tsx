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
  /** Close button aria-label */
  closeLabel?: string;
  /** Close button aria-label in Arabic */
  closeLabelAr?: string;
  /** Initial focus element ref */
  initialFocusRef?: React.RefObject<HTMLElement>;
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
  closeLabel = 'Close',
  closeLabelAr = 'إغلاق',
  initialFocusRef,
  children,
  className,
  ...props
}: ModalProps) {
  const modalRef = React.useRef<HTMLDivElement>(null);
  const titleId = React.useId();
  const previousActiveElement = React.useRef<Element | null>(null);

  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        e.preventDefault();
        e.stopPropagation();
        onClose();
      }
    };

    if (isOpen) {
      // Store currently focused element
      previousActiveElement.current = document.activeElement;

      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';

      // Focus initial element or modal
      if (initialFocusRef?.current) {
        initialFocusRef.current.focus();
      } else if (modalRef.current) {
        modalRef.current.focus();
      }

      // Announce modal to screen readers
      const announcement = titleAr || title || 'Dialog opened';
      const ariaLive = document.createElement('div');
      ariaLive.setAttribute('role', 'status');
      ariaLive.setAttribute('aria-live', 'polite');
      ariaLive.setAttribute('aria-atomic', 'true');
      ariaLive.className = 'sr-only';
      ariaLive.textContent = announcement;
      document.body.appendChild(ariaLive);

      return () => {
        document.removeEventListener('keydown', handleEscape);
        document.body.style.overflow = 'unset';
        ariaLive.remove();

        // Restore focus to previous element
        if (previousActiveElement.current instanceof HTMLElement) {
          previousActiveElement.current.focus();
        }
      };
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose, title, titleAr, initialFocusRef]);

  if (!isOpen) return null;

  const isFullscreen = size === 'full';

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'w-full h-full rounded-none',
  };

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (closeOnOverlay && e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <FocusLock returnFocus>
      <div
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
        onClick={handleOverlayClick}
        role="presentation"
        style={isFullscreen ? {} : { display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}
      >
        <div
          ref={modalRef}
          role="dialog"
          aria-modal="true"
          aria-labelledby={title || titleAr ? titleId : undefined}
          aria-describedby={descriptionId}
          tabIndex={-1}
          className={clsx(
            'bg-white dark:bg-gray-800 shadow-xl flex flex-col focus:outline-none',
            isFullscreen
              ? 'absolute inset-0 rounded-none'
              : `relative rounded-lg max-h-[90vh] w-full ${sizes[size]}`,
            className
          )}
          {...props}
        >
          {/* Header */}
          {(title || titleAr || showCloseButton) && (
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              {(title || titleAr) && (
                <h2 id={titleId} className="text-xl font-bold text-gray-900 dark:text-white">
                  <span className="text-gray-900 dark:text-white">{titleAr}</span>
                  {titleAr && title && <span className="mx-2">•</span>}
                  {title && <span className="text-gray-600 dark:text-gray-300 text-base">{title}</span>}
                </h2>
              )}
              {showCloseButton && (
                <button
                  type="button"
                  onClick={onClose}
                  className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-sahool-green-500"
                  aria-label={`${closeLabelAr} - ${closeLabel}`}
                >
                  <X className="w-5 h-5" aria-hidden="true" />
                </button>
              )}
            </div>
          )}

          {/* Content */}
          <div className={clsx('flex-1 overflow-y-auto', isFullscreen ? 'p-0' : 'p-6')}>{children}</div>
        </div>
      </div>
    </FocusLock>
  );
}

export function ModalFooter({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={clsx(
        'flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50',
        className
      )}
      {...props}
    />
  );
}

ModalFooter.displayName = 'ModalFooter';
