'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// MobileNav Component - التنقل المحمول
// Bottom navigation for mobile and hamburger menu with drawer
// ═══════════════════════════════════════════════════════════════════════════════

import { ReactNode, useState, useEffect, useRef } from 'react';
import { cn } from '@sahool/shared-utils';
import { Menu, X } from 'lucide-react';
import { useBreakpoint } from '../hooks/useBreakpoint';

export interface NavItem {
  /** Unique identifier */
  id: string;
  /** Display label */
  label: string;
  /** Icon component or element */
  icon?: ReactNode;
  /** Click handler */
  onClick?: () => void;
  /** Link href (if using as anchor) */
  href?: string;
  /** Is item active/selected */
  active?: boolean;
  /** Badge count or text */
  badge?: string | number;
  /** Disable item */
  disabled?: boolean;
}

export interface MobileNavProps {
  /** Navigation items */
  items: NavItem[];
  /** Additional CSS classes */
  className?: string;
  /** RTL support */
  rtl?: boolean;
  /** Navigation style */
  variant?: 'bottom' | 'drawer' | 'auto';
  /** Logo or brand component for drawer */
  logo?: ReactNode;
  /** Header content for drawer */
  header?: ReactNode;
  /** Footer content for drawer */
  footer?: ReactNode;
  /** Show labels in bottom nav */
  showLabels?: boolean;
  /** Compact mode (smaller touch targets) */
  compact?: boolean;
}

/**
 * BottomNav - Bottom navigation bar for mobile devices
 */
function BottomNav({
  items,
  className = '',
  rtl = false,
  showLabels = true,
  compact = false,
}: Omit<MobileNavProps, 'variant' | 'logo' | 'header' | 'footer'>) {
  return (
    <nav
      className={cn(
        'fixed bottom-0 left-0 right-0 z-50',
        'bg-white border-t border-gray-200',
        'safe-area-inset-bottom',
        rtl && 'rtl',
        className
      )}
      dir={rtl ? 'rtl' : undefined}
      role="navigation"
      aria-label="Mobile navigation"
    >
      <div
        className={cn(
          'flex items-center justify-around',
          compact ? 'h-14' : 'h-16',
          'max-w-screen-xl mx-auto'
        )}
      >
        {items.map((item) => {
          const Component = item.href ? 'a' : 'button';

          return (
            <Component
              key={item.id}
              href={item.href}
              onClick={item.onClick}
              disabled={item.disabled}
              className={cn(
                'relative flex flex-col items-center justify-center',
                'flex-1 h-full',
                'transition-colors duration-200',
                // Touch-friendly minimum size
                'min-w-[64px]',
                item.active
                  ? 'text-blue-600'
                  : 'text-gray-600 hover:text-gray-900',
                item.disabled && 'opacity-50 cursor-not-allowed',
                // Active indicator
                item.active && 'after:absolute after:top-0 after:left-1/2 after:-translate-x-1/2 after:w-12 after:h-0.5 after:bg-blue-600 after:rounded-full'
              )}
              aria-current={item.active ? 'page' : undefined}
              aria-label={item.label}
            >
              {/* Icon */}
              {item.icon && (
                <span className={cn('mb-1', compact ? 'text-xl' : 'text-2xl')}>
                  {item.icon}
                </span>
              )}

              {/* Label */}
              {showLabels && (
                <span className={cn('text-xs font-medium', compact && 'text-[10px]')}>
                  {item.label}
                </span>
              )}

              {/* Badge */}
              {item.badge && (
                <span
                  className={cn(
                    'absolute',
                    showLabels ? 'top-1 right-1/4' : 'top-2 right-1/4',
                    'min-w-[18px] h-[18px] px-1',
                    'flex items-center justify-center',
                    'bg-red-500 text-white text-[10px] font-bold',
                    'rounded-full',
                    'border-2 border-white'
                  )}
                  aria-label={`${item.badge} notifications`}
                >
                  {item.badge}
                </span>
              )}
            </Component>
          );
        })}
      </div>
    </nav>
  );
}

/**
 * DrawerNav - Hamburger menu with slide-out drawer
 */
function DrawerNav({
  items,
  className = '',
  rtl = false,
  logo,
  header,
  footer,
}: Omit<MobileNavProps, 'variant' | 'showLabels' | 'compact'>) {
  const [isOpen, setIsOpen] = useState(false);
  const drawerRef = useRef<HTMLDivElement>(null);

  // Close drawer on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen]);

  // Prevent body scroll when drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Close drawer when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (drawerRef.current && !drawerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <>
      {/* Hamburger Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={cn(
          'fixed top-4 z-50',
          rtl ? 'left-4' : 'right-4',
          'p-2 rounded-lg',
          'bg-white border border-gray-200 shadow-sm',
          'hover:bg-gray-50 active:bg-gray-100',
          'transition-colors duration-200',
          // Touch-friendly size
          'w-12 h-12 flex items-center justify-center',
          className
        )}
        aria-label="Open menu"
        aria-expanded={isOpen}
      >
        <Menu className="w-6 h-6 text-gray-700" />
      </button>

      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-[60] transition-opacity"
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Drawer */}
      <div
        ref={drawerRef}
        className={cn(
          'fixed top-0 bottom-0 z-[70] w-80 max-w-[85vw]',
          rtl ? 'left-0' : 'right-0',
          'bg-white shadow-2xl',
          'transform transition-transform duration-300 ease-in-out',
          isOpen
            ? 'translate-x-0'
            : rtl
            ? '-translate-x-full'
            : 'translate-x-full',
          rtl && 'rtl'
        )}
        dir={rtl ? 'rtl' : undefined}
        role="dialog"
        aria-modal="true"
        aria-label="Navigation menu"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          {logo || header || <div className="text-lg font-semibold">Menu</div>}

          <button
            onClick={() => setIsOpen(false)}
            className={cn(
              'p-2 rounded-lg',
              'hover:bg-gray-100 active:bg-gray-200',
              'transition-colors duration-200',
              'w-10 h-10 flex items-center justify-center'
            )}
            aria-label="Close menu"
          >
            <X className="w-5 h-5 text-gray-700" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 overflow-y-auto p-2">
          {items.map((item) => {
            const Component = item.href ? 'a' : 'button';

            return (
              <Component
                key={item.id}
                href={item.href}
                onClick={() => {
                  item.onClick?.();
                  setIsOpen(false);
                }}
                disabled={item.disabled}
                className={cn(
                  'w-full flex items-center gap-3 p-4 rounded-lg',
                  'text-left transition-colors duration-200',
                  // Touch-friendly minimum height
                  'min-h-[56px]',
                  item.active
                    ? 'bg-blue-50 text-blue-700 font-medium'
                    : 'text-gray-700 hover:bg-gray-50 active:bg-gray-100',
                  item.disabled && 'opacity-50 cursor-not-allowed'
                )}
                aria-current={item.active ? 'page' : undefined}
              >
                {/* Icon */}
                {item.icon && (
                  <span className="text-2xl flex-shrink-0">
                    {item.icon}
                  </span>
                )}

                {/* Label */}
                <span className="flex-1 text-base">
                  {item.label}
                </span>

                {/* Badge */}
                {item.badge && (
                  <span
                    className={cn(
                      'min-w-[24px] h-6 px-2',
                      'flex items-center justify-center',
                      'bg-red-500 text-white text-xs font-bold',
                      'rounded-full'
                    )}
                    aria-label={`${item.badge} notifications`}
                  >
                    {item.badge}
                  </span>
                )}
              </Component>
            );
          })}
        </nav>

        {/* Footer */}
        {footer && (
          <div className="p-4 border-t border-gray-200">
            {footer}
          </div>
        )}
      </div>
    </>
  );
}

/**
 * MobileNav - Adaptive mobile navigation component
 *
 * Features:
 * - Bottom navigation bar for mobile devices (< 768px)
 * - Hamburger menu with slide-out drawer
 * - Touch-friendly tap targets (min 44px)
 * - RTL support for Arabic/Hebrew
 * - Active state indicators
 * - Badge support for notifications
 * - Keyboard accessible (ESC to close)
 * - Auto-close drawer on navigation
 *
 * @example
 * ```tsx
 * const navItems = [
 *   { id: 'home', label: 'Home', icon: <HomeIcon />, active: true },
 *   { id: 'search', label: 'Search', icon: <SearchIcon /> },
 *   { id: 'profile', label: 'Profile', icon: <UserIcon />, badge: 3 },
 * ];
 *
 * // Bottom navigation (mobile only)
 * <MobileNav variant="bottom" items={navItems} />
 *
 * // Drawer navigation (hamburger menu)
 * <MobileNav
 *   variant="drawer"
 *   items={navItems}
 *   logo={<Logo />}
 *   footer={<UserProfile />}
 * />
 *
 * // Auto mode (bottom nav on mobile, drawer on larger screens)
 * <MobileNav variant="auto" items={navItems} />
 * ```
 */
export function MobileNav(props: MobileNavProps) {
  const { variant = 'auto' } = props;
  const { isMobile } = useBreakpoint();

  // Auto mode: bottom nav on mobile, drawer on larger screens
  if (variant === 'auto') {
    return isMobile ? <BottomNav {...props} /> : <DrawerNav {...props} />;
  }

  // Explicit variant
  if (variant === 'bottom') {
    return <BottomNav {...props} />;
  }

  return <DrawerNav {...props} />;
}

/**
 * Hook to manage mobile navigation state
 */
export function useMobileNav(initialActive?: string) {
  const [activeItem, setActiveItem] = useState<string | undefined>(initialActive);

  const createNavItem = (
    id: string,
    label: string,
    icon?: ReactNode,
    options?: Partial<Omit<NavItem, 'id' | 'label' | 'icon'>>
  ): NavItem => ({
    id,
    label,
    icon,
    active: activeItem === id,
    onClick: () => setActiveItem(id),
    ...options,
  });

  return {
    activeItem,
    setActiveItem,
    createNavItem,
  };
}
