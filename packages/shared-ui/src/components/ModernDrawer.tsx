'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernDrawer Component - درج منزلق حديث
// Slide-in drawer from any direction with animations
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { ReactNode, useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import { FocusTrap } from './FocusTrap';

export interface ModernDrawerProps {
  open: boolean;
  onClose: () => void;
  title?: string | ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  position?: 'left' | 'right' | 'top' | 'bottom';
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  variant?: 'default' | 'glass';
  closeOnBackdrop?: boolean;
  closeOnEscape?: boolean;
  showCloseButton?: boolean;
  blur?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  contentClassName?: string;
  overlayClassName?: string;
}

const sizeClasses = {
  left: {
    sm: 'w-80',
    md: 'w-96',
    lg: 'w-[28rem]',
    xl: 'w-[36rem]',
    full: 'w-full',
  },
  right: {
    sm: 'w-80',
    md: 'w-96',
    lg: 'w-[28rem]',
    xl: 'w-[36rem]',
    full: 'w-full',
  },
  top: {
    sm: 'h-80',
    md: 'h-96',
    lg: 'h-[28rem]',
    xl: 'h-[36rem]',
    full: 'h-full',
  },
  bottom: {
    sm: 'h-80',
    md: 'h-96',
    lg: 'h-[28rem]',
    xl: 'h-[36rem]',
    full: 'h-full',
  },
};

const positionClasses = {
  left: 'left-0 top-0 h-full',
  right: 'right-0 top-0 h-full',
  top: 'top-0 left-0 w-full',
  bottom: 'bottom-0 left-0 w-full',
};

const animationClasses = {
  left: 'animate-in slide-in-from-left duration-300',
  right: 'animate-in slide-in-from-right duration-300',
  top: 'animate-in slide-in-from-top duration-300',
  bottom: 'animate-in slide-in-from-bottom duration-300',
};

const blurClasses = {
  sm: 'backdrop-blur-sm',
  md: 'backdrop-blur-md',
  lg: 'backdrop-blur-lg',
  xl: 'backdrop-blur-xl',
};

export function ModernDrawer({
  open,
  onClose,
  title,
  children,
  footer,
  position = 'right',
  size = 'md',
  variant = 'default',
  closeOnBackdrop = true,
  closeOnEscape = true,
  showCloseButton = true,
  blur = 'md',
  className = '',
  contentClassName = '',
  overlayClassName = '',
}: ModernDrawerProps) {
  const drawerRef = useRef<HTMLDivElement>(null);

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

  // Prevent body scroll when drawer is open
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

  const isHorizontal = position === 'left' || position === 'right';

  return (
    <div
      className={cn(
        'fixed inset-0 z-50',
        'animate-in fade-in duration-200'
      )}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'drawer-title' : undefined}
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

      {/* Drawer Content */}
      <FocusTrap>
        <div
          ref={drawerRef}
          className={cn(
            'fixed flex flex-col',
            positionClasses[position],
            sizeClasses[position][size],
            animationClasses[position],

            // Variant-specific styles
            variant === 'default' &&
              'bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700',
            variant === 'glass' &&
              cn(
                'bg-white/90 dark:bg-gray-900/90',
                'backdrop-blur-xl',
                'border-white/20 dark:border-white/10'
              ),

            // Border based on position
            position === 'left' && 'border-r',
            position === 'right' && 'border-l',
            position === 'top' && 'border-b',
            position === 'bottom' && 'border-t',

            'shadow-2xl',
            className
          )}
        >
          {/* Header */}
          {(title || showCloseButton) && (
            <div
              className={cn(
                'flex items-center justify-between gap-4 flex-shrink-0',
                'px-6 py-4 border-b border-gray-200 dark:border-gray-700',
                variant === 'glass' && 'border-white/20 dark:border-white/10'
              )}
            >
              {title && (
                <h2
                  id="drawer-title"
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
                  aria-label="Close drawer"
                >
                  <X size={20} />
                </button>
              )}
            </div>
          )}

          {/* Body */}
          <div
            className={cn(
              'flex-1 overflow-y-auto px-6 py-4',
              contentClassName
            )}
          >
            {children}
          </div>

          {/* Footer */}
          {footer && (
            <div
              className={cn(
                'flex-shrink-0 px-6 py-4 border-t border-gray-200 dark:border-gray-700',
                'bg-gray-50 dark:bg-gray-800/50',
                variant === 'glass' && 'bg-white/50 dark:bg-gray-800/30 border-white/20 dark:border-white/10'
              )}
            >
              {footer}
            </div>
          )}
        </div>
      </FocusTrap>
    </div>
  );
}

ModernDrawer.displayName = 'ModernDrawer';
