'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// Tooltip Component - تلميح
// Modern tooltip with arrow, animations, and positioning
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import {
  forwardRef,
  HTMLAttributes,
  ReactNode,
  useState,
  useRef,
  useEffect,
} from 'react';

export interface TooltipProps extends Omit<HTMLAttributes<HTMLDivElement>, 'content'> {
  content: ReactNode;
  children: ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  variant?: 'dark' | 'light' | 'primary';
  delay?: number;
  arrow?: boolean;
  disabled?: boolean;
}

const positionClasses = {
  top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
  bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
  left: 'right-full top-1/2 -translate-y-1/2 mr-2',
  right: 'left-full top-1/2 -translate-y-1/2 ml-2',
};

const arrowClasses = {
  top: 'top-full left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent',
  bottom: 'bottom-full left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent',
  left: 'left-full top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent',
  right: 'right-full top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent',
};

const variantClasses = {
  dark: {
    tooltip: 'bg-gray-900 dark:bg-gray-800 text-white border-gray-900 dark:border-gray-800',
    arrow: 'border-gray-900 dark:border-gray-800',
  },
  light: {
    tooltip: 'bg-white dark:bg-gray-100 text-gray-900 dark:text-gray-800 border-gray-200 dark:border-gray-300',
    arrow: 'border-white dark:border-gray-100',
  },
  primary: {
    tooltip: 'bg-sahool-600 dark:bg-sahool-500 text-white border-sahool-600 dark:border-sahool-500',
    arrow: 'border-sahool-600 dark:border-sahool-500',
  },
};

export const Tooltip = forwardRef<HTMLDivElement, TooltipProps>(
  (
    {
      content,
      children,
      position = 'top',
      variant = 'dark',
      delay = 200,
      arrow = true,
      disabled = false,
      className = '',
      ...props
    },
    ref
  ) => {
    const [isVisible, setIsVisible] = useState(false);
    const [shouldRender, setShouldRender] = useState(false);
    const timeoutRef = useRef<NodeJS.Timeout>();
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
      return () => {
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
      };
    }, []);

    const handleMouseEnter = () => {
      if (disabled) return;

      timeoutRef.current = setTimeout(() => {
        setShouldRender(true);
        // Small delay for render before animation
        requestAnimationFrame(() => {
          setIsVisible(true);
        });
      }, delay);
    };

    const handleMouseLeave = () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      setIsVisible(false);
      // Wait for animation to complete before removing from DOM
      setTimeout(() => {
        setShouldRender(false);
      }, 200);
    };

    const handleFocus = () => {
      if (disabled) return;
      setShouldRender(true);
      requestAnimationFrame(() => {
        setIsVisible(true);
      });
    };

    const handleBlur = () => {
      setIsVisible(false);
      setTimeout(() => {
        setShouldRender(false);
      }, 200);
    };

    return (
      <div
        ref={ref}
        className={cn('relative inline-flex', className)}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onFocus={handleFocus}
        onBlur={handleBlur}
        {...props}
      >
        {children}

        {shouldRender && (
          <div
            ref={containerRef}
            role="tooltip"
            aria-hidden={!isVisible}
            className={cn(
              'absolute z-50 px-3 py-2 text-sm rounded-lg shadow-lg',
              'border whitespace-nowrap pointer-events-none',
              'transition-all duration-200 ease-out',
              positionClasses[position],
              variantClasses[variant].tooltip,
              isVisible
                ? 'opacity-100 scale-100'
                : 'opacity-0 scale-95'
            )}
          >
            {content}

            {/* Arrow */}
            {arrow && (
              <div
                className={cn(
                  'absolute w-0 h-0 border-4',
                  arrowClasses[position],
                  variantClasses[variant].arrow
                )}
                aria-hidden="true"
              />
            )}
          </div>
        )}
      </div>
    );
  }
);

Tooltip.displayName = 'Tooltip';

// TooltipProvider for advanced usage with custom positioning
export interface TooltipProviderProps {
  children: ReactNode;
  delayDuration?: number;
}

export const TooltipProvider = ({
  children,
  delayDuration = 200,
}: TooltipProviderProps) => {
  // This can be expanded with React Context for global tooltip configuration
  return <>{children}</>;
};

TooltipProvider.displayName = 'TooltipProvider';
