"use client";

import { cn } from "@sahool/shared-utils";
import { forwardRef, HTMLAttributes, ReactNode, useEffect, useRef, useCallback } from "react";

/** Focusable elements selector */
const FOCUSABLE_SELECTOR =
  'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"]):not([disabled])';

export interface FocusTrapProps extends HTMLAttributes<HTMLDivElement> {
  /** Content to trap focus within */
  children: ReactNode;
  /** Whether the focus trap is active */
  active?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Whether to restore focus to previous element on deactivation */
  restoreFocus?: boolean;
  /** Whether to auto-focus the first element on activation */
  autoFocus?: boolean;
  /** Callback when focus escapes (for debugging/logging) */
  onFocusEscape?: () => void;
}

/**
 * Focus Trap Component for Modal Accessibility
 * مكون حصر التركيز لإمكانية الوصول في النوافذ المنبثقة
 *
 * Traps keyboard focus within a container, essential for modal dialogs.
 *
 * @example
 * <FocusTrap active={isModalOpen}>
 *   <ModalContent />
 * </FocusTrap>
 */
export const FocusTrap = forwardRef<HTMLDivElement, FocusTrapProps>(
  (
    {
      children,
      active = true,
      className,
      restoreFocus = true,
      autoFocus = true,
      onFocusEscape,
      ...props
    },
    forwardedRef,
  ) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const previousFocusRef = useRef<HTMLElement | null>(null);

    // Get focusable elements
    const getFocusableElements = useCallback(() => {
      const container = containerRef.current;
      if (!container) return [];
      return Array.from(container.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR));
    }, []);

    // Handle activation and deactivation
    useEffect(() => {
      if (!active) return;

      // Store previously focused element
      if (restoreFocus) {
        previousFocusRef.current = document.activeElement as HTMLElement;
      }

      const focusableElements = getFocusableElements();
      const firstElement = focusableElements[0];

      // Auto-focus first element
      if (autoFocus && firstElement) {
        // Small delay to ensure DOM is ready
        requestAnimationFrame(() => {
          firstElement.focus();
        });
      }

      // Restore focus on deactivation
      return () => {
        if (restoreFocus && previousFocusRef.current) {
          previousFocusRef.current.focus();
        }
      };
    }, [active, autoFocus, restoreFocus, getFocusableElements]);

    // Handle tab key navigation
    useEffect(() => {
      if (!active) return;

      const container = containerRef.current;
      if (!container) return;

      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key !== "Tab") return;

        const focusableElements = getFocusableElements();
        if (focusableElements.length === 0) {
          e.preventDefault();
          return;
        }

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey) {
          // Shift + Tab
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          // Tab
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      };

      // Prevent focus from leaving the container
      const handleFocusIn = (e: FocusEvent) => {
        if (!container.contains(e.target as Node)) {
          e.preventDefault();
          const focusableElements = getFocusableElements();
          if (focusableElements.length > 0) {
            focusableElements[0].focus();
          }
          onFocusEscape?.();
        }
      };

      container.addEventListener("keydown", handleKeyDown);
      document.addEventListener("focusin", handleFocusIn);

      return () => {
        container.removeEventListener("keydown", handleKeyDown);
        document.removeEventListener("focusin", handleFocusIn);
      };
    }, [active, getFocusableElements, onFocusEscape]);

    // Merge refs
    const setRefs = useCallback(
      (node: HTMLDivElement | null) => {
        containerRef.current = node;
        if (typeof forwardedRef === "function") {
          forwardedRef(node);
        } else if (forwardedRef) {
          forwardedRef.current = node;
        }
      },
      [forwardedRef],
    );

    return (
      <div ref={setRefs} className={cn(className)} {...props}>
        {children}
      </div>
    );
  },
);

FocusTrap.displayName = "FocusTrap";
