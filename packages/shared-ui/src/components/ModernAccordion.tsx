'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernAccordion Component - أكورديون حديث
// Expandable sections with smooth animations
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { ReactNode, useState, useRef, useEffect } from 'react';
import { ChevronDown, LucideIcon } from 'lucide-react';

export interface AccordionItem {
  id: string;
  title: string | ReactNode;
  content: ReactNode;
  icon?: LucideIcon;
  disabled?: boolean;
  badge?: string | number;
}

export interface ModernAccordionProps {
  items: AccordionItem[];
  defaultOpen?: string | string[];
  allowMultiple?: boolean;
  onChange?: (openItems: string[]) => void;
  variant?: 'default' | 'bordered' | 'separated';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  sm: {
    title: 'text-sm px-4 py-3',
    content: 'px-4 py-3',
    icon: 16,
  },
  md: {
    title: 'text-base px-6 py-4',
    content: 'px-6 py-4',
    icon: 18,
  },
  lg: {
    title: 'text-lg px-8 py-5',
    content: 'px-8 py-5',
    icon: 20,
  },
};

export function ModernAccordion({
  items,
  defaultOpen,
  allowMultiple = false,
  onChange,
  variant = 'default',
  size = 'md',
  className = '',
}: ModernAccordionProps) {
  const [openItems, setOpenItems] = useState<string[]>(() => {
    if (defaultOpen) {
      return Array.isArray(defaultOpen) ? defaultOpen : [defaultOpen];
    }
    return [];
  });

  const isItemOpen = (itemId: string) => openItems.includes(itemId);

  const toggleItem = (itemId: string) => {
    const item = items.find((i) => i.id === itemId);
    if (item && item.disabled) return;

    setOpenItems((current) => {
      let newOpenItems: string[];

      if (current.includes(itemId)) {
        // Close the item
        newOpenItems = current.filter((id) => id !== itemId);
      } else {
        // Open the item
        if (allowMultiple) {
          newOpenItems = [...current, itemId];
        } else {
          newOpenItems = [itemId];
        }
      }

      onChange?.(newOpenItems);
      return newOpenItems;
    });
  };

  return (
    <div
      className={cn(
        'w-full',
        variant === 'separated' && 'space-y-3',
        className
      )}
    >
      {items.map((item, index) => (
        <AccordionItemComponent
          key={item.id}
          item={item}
          isOpen={isItemOpen(item.id)}
          onToggle={() => toggleItem(item.id)}
          variant={variant}
          size={size}
          isFirst={index === 0}
          isLast={index === items.length - 1}
        />
      ))}
    </div>
  );
}

interface AccordionItemComponentProps {
  item: AccordionItem;
  isOpen: boolean;
  onToggle: () => void;
  variant: 'default' | 'bordered' | 'separated';
  size: 'sm' | 'md' | 'lg';
  isFirst: boolean;
  isLast: boolean;
}

function AccordionItemComponent({
  item,
  isOpen,
  onToggle,
  variant,
  size,
  isFirst,
  isLast,
}: AccordionItemComponentProps) {
  const contentRef = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState(0);

  const Icon = item.icon;

  useEffect(() => {
    if (contentRef.current) {
      setHeight(isOpen ? contentRef.current.scrollHeight : 0);
    }
  }, [isOpen, item.content]);

  return (
    <div
      className={cn(
        'overflow-hidden transition-all duration-200',
        variant === 'default' &&
          cn(
            'border-b border-gray-200 dark:border-gray-700',
            isLast && 'border-b-0'
          ),
        variant === 'bordered' &&
          cn(
            'border border-gray-200 dark:border-gray-700',
            isFirst && 'rounded-t-xl',
            isLast && 'rounded-b-xl',
            !isFirst && 'border-t-0'
          ),
        variant === 'separated' &&
          'border border-gray-200 dark:border-gray-700 rounded-xl',
        isOpen && variant !== 'default' && 'shadow-lg'
      )}
    >
      {/* Accordion Header */}
      <button
        onClick={onToggle}
        disabled={item.disabled}
        className={cn(
          'w-full flex items-center justify-between gap-3',
          'bg-white dark:bg-gray-900',
          'transition-all duration-200',
          'focus:outline-none focus:ring-2 focus:ring-sahool-500 focus:ring-inset',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          sizeClasses[size].title,
          variant === 'default' && 'hover:bg-gray-50 dark:hover:bg-gray-800/50',
          variant === 'bordered' &&
            cn(
              isFirst && 'rounded-t-xl',
              isLast && !isOpen && 'rounded-b-xl',
              'hover:bg-gray-50 dark:hover:bg-gray-800/50'
            ),
          variant === 'separated' &&
            cn(
              isOpen ? 'rounded-t-xl' : 'rounded-xl',
              'hover:bg-gray-50 dark:hover:bg-gray-800/50'
            ),
          isOpen && 'bg-gray-50 dark:bg-gray-800/50'
        )}
        aria-expanded={isOpen}
        aria-controls={`accordion-content-${item.id}`}
        id={`accordion-header-${item.id}`}
      >
        <div className="flex items-center gap-3 flex-1 text-left">
          {Icon && (
            <Icon
              size={sizeClasses[size].icon}
              className="text-sahool-600 dark:text-sahool-400 flex-shrink-0"
              aria-hidden="true"
            />
          )}
          <span className="font-semibold text-gray-900 dark:text-gray-100">
            {item.title}
          </span>
          {item.badge && (
            <span
              className={cn(
                'ml-auto px-2.5 py-1 text-xs font-semibold rounded-full',
                'bg-sahool-100 dark:bg-sahool-900/30',
                'text-sahool-700 dark:text-sahool-300'
              )}
            >
              {item.badge}
            </span>
          )}
        </div>
        <ChevronDown
          size={sizeClasses[size].icon}
          className={cn(
            'text-gray-500 dark:text-gray-400 transition-transform duration-300 flex-shrink-0',
            isOpen && 'rotate-180'
          )}
          aria-hidden="true"
        />
      </button>

      {/* Accordion Content */}
      <div
        id={`accordion-content-${item.id}`}
        role="region"
        aria-labelledby={`accordion-header-${item.id}`}
        style={{ height: `${height}px` }}
        className="transition-all duration-300 ease-in-out overflow-hidden"
      >
        <div
          ref={contentRef}
          className={cn(
            'bg-white dark:bg-gray-900',
            'border-t border-gray-200 dark:border-gray-700',
            'text-gray-700 dark:text-gray-300',
            sizeClasses[size].content
          )}
        >
          {item.content}
        </div>
      </div>
    </div>
  );
}

ModernAccordion.displayName = 'ModernAccordion';
