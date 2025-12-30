'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernDropdown Component - قائمة منسدلة حديثة
// Dropdown menu with smooth animations and keyboard navigation
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { ReactNode, useState, useRef, useEffect } from 'react';
import { Check, ChevronRight, LucideIcon } from 'lucide-react';

export interface DropdownItem {
  id: string;
  label: string | ReactNode;
  icon?: LucideIcon;
  disabled?: boolean;
  danger?: boolean;
  divider?: boolean;
  badge?: string | number;
  onClick?: () => void;
  children?: DropdownItem[];
}

export interface ModernDropdownProps {
  trigger: ReactNode;
  items: DropdownItem[];
  align?: 'left' | 'right' | 'center';
  position?: 'bottom' | 'top';
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'glass';
  closeOnSelect?: boolean;
  className?: string;
  menuClassName?: string;
  selectedId?: string;
  showCheck?: boolean;
}

const sizeClasses = {
  sm: 'min-w-[10rem] text-sm',
  md: 'min-w-[12rem] text-base',
  lg: 'min-w-[14rem] text-lg',
};

const alignClasses = {
  left: 'left-0',
  right: 'right-0',
  center: 'left-1/2 -translate-x-1/2',
};

const positionClasses = {
  bottom: 'top-full mt-2',
  top: 'bottom-full mb-2',
};

const animationClasses = {
  bottom: 'animate-in fade-in slide-in-from-top-2 duration-200',
  top: 'animate-in fade-in slide-in-from-bottom-2 duration-200',
};

export function ModernDropdown({
  trigger,
  items,
  align = 'left',
  position = 'bottom',
  size = 'md',
  variant = 'default',
  closeOnSelect = true,
  className = '',
  menuClassName = '',
  selectedId,
  showCheck = false,
}: ModernDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeSubmenu, setActiveSubmenu] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setActiveSubmenu(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  // Handle Escape key
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
        setActiveSubmenu(null);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen]);

  const handleItemClick = (item: DropdownItem) => {
    if (item.disabled) return;

    // If item has children, toggle submenu
    if (item.children && item.children.length > 0) {
      setActiveSubmenu(activeSubmenu === item.id ? null : item.id);
      return;
    }

    // Execute item's onClick
    item.onClick?.();

    // Close dropdown if closeOnSelect is true
    if (closeOnSelect) {
      setIsOpen(false);
      setActiveSubmenu(null);
    }
  };

  return (
    <div ref={dropdownRef} className={cn('relative inline-block', className)}>
      {/* Trigger */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        role="button"
        aria-haspopup="true"
        aria-expanded={isOpen}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setIsOpen(!isOpen);
          }
        }}
      >
        {trigger}
      </div>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          ref={menuRef}
          className={cn(
            'absolute z-50',
            alignClasses[align],
            positionClasses[position],
            animationClasses[position],
            sizeClasses[size],
            'rounded-xl shadow-xl overflow-hidden',

            // Variant-specific styles
            variant === 'default' &&
              'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700',
            variant === 'glass' &&
              cn(
                'bg-white/90 dark:bg-gray-900/90',
                'backdrop-blur-xl',
                'border border-white/20 dark:border-white/10'
              ),
            menuClassName
          )}
          role="menu"
          aria-orientation="vertical"
        >
          <div className="py-1">
            {items.map((item, index) => (
              <DropdownItemComponent
                key={item.id || index}
                item={item}
                isActive={activeSubmenu === item.id}
                isSelected={selectedId === item.id}
                showCheck={showCheck}
                onItemClick={handleItemClick}
                variant={variant}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

interface DropdownItemComponentProps {
  item: DropdownItem;
  isActive: boolean;
  isSelected: boolean;
  showCheck: boolean;
  onItemClick: (item: DropdownItem) => void;
  variant: 'default' | 'glass';
}

function DropdownItemComponent({
  item,
  isActive,
  isSelected,
  showCheck,
  onItemClick,
  variant,
}: DropdownItemComponentProps) {
  const Icon = item.icon;
  const hasChildren = item.children && item.children.length > 0;

  if (item.divider) {
    return (
      <div
        className={cn(
          'my-1 border-t border-gray-200 dark:border-gray-700',
          variant === 'glass' && 'border-white/20 dark:border-white/10'
        )}
        role="separator"
      />
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => onItemClick(item)}
        disabled={item.disabled}
        role="menuitem"
        className={cn(
          'w-full flex items-center gap-3 px-4 py-2.5',
          'text-left transition-all duration-150',
          'focus:outline-none focus:ring-2 focus:ring-inset focus:ring-sahool-500',
          'disabled:opacity-50 disabled:cursor-not-allowed',

          // Color variants
          item.danger
            ? cn(
                'text-red-600 dark:text-red-400',
                'hover:bg-red-50 dark:hover:bg-red-950/30'
              )
            : cn(
                'text-gray-700 dark:text-gray-300',
                'hover:bg-gray-100 dark:hover:bg-gray-800/50'
              ),

          // Selected state
          isSelected && !item.danger && 'bg-sahool-50 dark:bg-sahool-950/30'
        )}
      >
        {/* Check icon for selected item */}
        {showCheck && (
          <div className="w-4 h-4 flex-shrink-0">
            {isSelected && (
              <Check
                size={16}
                className="text-sahool-600 dark:text-sahool-400"
                aria-label="Selected"
              />
            )}
          </div>
        )}

        {/* Item icon */}
        {Icon && (
          <Icon
            size={16}
            className="flex-shrink-0"
            aria-hidden="true"
          />
        )}

        {/* Item label */}
        <span className="flex-1 truncate">{item.label}</span>

        {/* Badge */}
        {item.badge && (
          <span
            className={cn(
              'px-2 py-0.5 text-xs font-semibold rounded-full flex-shrink-0',
              item.danger
                ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            )}
          >
            {item.badge}
          </span>
        )}

        {/* Submenu indicator */}
        {hasChildren && (
          <ChevronRight
            size={16}
            className={cn(
              'flex-shrink-0 transition-transform duration-200',
              isActive && 'rotate-90',
              'rtl:rotate-180 rtl:data-[active=true]:-rotate-90'
            )}
            data-active={isActive}
            aria-hidden="true"
          />
        )}
      </button>

      {/* Submenu */}
      {hasChildren && isActive && (
        <div
          className={cn(
            'pl-8 py-1',
            'border-l-2 border-sahool-200 dark:border-sahool-800 ml-4',
            'animate-in slide-in-from-top-2 duration-200'
          )}
          role="menu"
        >
          {item.children!.map((child, index) => (
            <DropdownItemComponent
              key={child.id || index}
              item={child}
              isActive={false}
              isSelected={false}
              showCheck={showCheck}
              onItemClick={onItemClick}
              variant={variant}
            />
          ))}
        </div>
      )}
    </div>
  );
}

ModernDropdown.displayName = 'ModernDropdown';
