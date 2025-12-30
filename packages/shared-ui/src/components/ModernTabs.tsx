'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernTabs Component - تبويبات حديثة
// Animated tabs with smooth indicator and transitions
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { ReactNode, useState, useRef, useEffect } from 'react';
import { LucideIcon } from 'lucide-react';

export interface Tab {
  id: string;
  label: string;
  content: ReactNode;
  icon?: LucideIcon;
  disabled?: boolean;
  badge?: string | number;
}

export interface ModernTabsProps {
  tabs: Tab[];
  defaultTab?: string;
  onChange?: (tabId: string) => void;
  variant?: 'default' | 'pills' | 'underline';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  className?: string;
  tabListClassName?: string;
  contentClassName?: string;
}

const sizeClasses = {
  sm: 'text-sm px-4 py-2',
  md: 'text-base px-6 py-3',
  lg: 'text-lg px-8 py-4',
};

const iconSizes = {
  sm: 16,
  md: 18,
  lg: 20,
};

export function ModernTabs({
  tabs,
  defaultTab,
  onChange,
  variant = 'default',
  size = 'md',
  fullWidth = false,
  className = '',
  tabListClassName = '',
  contentClassName = '',
}: ModernTabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);
  const [indicatorStyle, setIndicatorStyle] = useState({ left: 0, width: 0 });
  const tabRefs = useRef<Map<string, HTMLButtonElement>>(new Map());

  const activeTabContent = tabs.find((tab) => tab.id === activeTab)?.content;

  // Update indicator position
  useEffect(() => {
    const activeTabElement = tabRefs.current.get(activeTab);
    if (activeTabElement) {
      const { offsetLeft, offsetWidth } = activeTabElement;
      setIndicatorStyle({ left: offsetLeft, width: offsetWidth });
    }
  }, [activeTab, tabs]);

  const handleTabChange = (tabId: string) => {
    const tab = tabs.find((t) => t.id === tabId);
    if (tab && !tab.disabled) {
      setActiveTab(tabId);
      onChange?.(tabId);
    }
  };

  const renderTabButton = (tab: Tab, index: number) => {
    const isActive = activeTab === tab.id;
    const Icon = tab.icon;

    return (
      <button
        key={tab.id}
        ref={(el) => {
          if (el) tabRefs.current.set(tab.id, el);
        }}
        onClick={() => handleTabChange(tab.id)}
        disabled={tab.disabled}
        role="tab"
        aria-selected={isActive}
        aria-controls={`tabpanel-${tab.id}`}
        id={`tab-${tab.id}`}
        tabIndex={isActive ? 0 : -1}
        className={cn(
          'relative inline-flex items-center justify-center gap-2',
          'font-medium transition-all duration-300 ease-out',
          'focus:outline-none focus:ring-2 focus:ring-sahool-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          sizeClasses[size],
          fullWidth && 'flex-1',

          // Variant-specific styles
          variant === 'default' &&
            cn(
              'rounded-lg',
              isActive
                ? 'text-white'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            ),
          variant === 'pills' &&
            cn(
              'rounded-full',
              isActive
                ? 'bg-sahool-600 text-white shadow-lg shadow-sahool-500/50'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
            ),
          variant === 'underline' &&
            cn(
              'rounded-none border-b-2',
              isActive
                ? 'border-sahool-600 text-sahool-600 dark:text-sahool-400'
                : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
            )
        )}
      >
        {Icon && <Icon size={iconSizes[size]} aria-hidden="true" />}
        <span>{tab.label}</span>
        {tab.badge && (
          <span
            className={cn(
              'ml-1 px-2 py-0.5 text-xs font-semibold rounded-full',
              isActive
                ? 'bg-white/20 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            )}
          >
            {tab.badge}
          </span>
        )}
      </button>
    );
  };

  return (
    <div className={cn('w-full', className)}>
      {/* Tab List */}
      <div
        role="tablist"
        aria-label="Tabs"
        className={cn(
          'relative flex',
          variant === 'default' && 'bg-gray-100 dark:bg-gray-800 p-1 rounded-xl',
          variant === 'pills' && 'gap-2',
          variant === 'underline' && 'border-b border-gray-200 dark:border-gray-700',
          !fullWidth && 'inline-flex',
          fullWidth && 'w-full',
          tabListClassName
        )}
      >
        {/* Animated Indicator for default variant */}
        {variant === 'default' && (
          <div
            className="absolute bg-sahool-600 rounded-lg shadow-lg transition-all duration-300 ease-out"
            style={{
              left: indicatorStyle.left,
              width: indicatorStyle.width,
              height: 'calc(100% - 0.5rem)',
              top: '0.25rem',
            }}
            aria-hidden="true"
          />
        )}

        {/* Tab Buttons */}
        {tabs.map((tab, index) => (
          <div key={tab.id} className={cn('relative', fullWidth && 'flex-1')}>
            {renderTabButton(tab, index)}
          </div>
        ))}
      </div>

      {/* Tab Content */}
      <div
        role="tabpanel"
        id={`tabpanel-${activeTab}`}
        aria-labelledby={`tab-${activeTab}`}
        className={cn(
          'mt-6 focus:outline-none',
          contentClassName
        )}
        tabIndex={0}
      >
        <div
          className="animate-in fade-in slide-in-from-bottom-2 duration-300"
          key={activeTab}
        >
          {activeTabContent}
        </div>
      </div>
    </div>
  );
}

ModernTabs.displayName = 'ModernTabs';
