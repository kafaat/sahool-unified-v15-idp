"use client";

/**
 * Tabs Component
 * مكون التبويبات
 *
 * An accessible tab navigation component
 */

import * as React from "react";
import { cn } from "@sahool/shared-utils";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
}

export interface TabsProps {
  /** Tab items */
  tabs: Tab[];
  /** Active tab id */
  activeTab?: string;
  /** Callback when tab changes */
  onTabChange?: (tabId: string) => void;
  /** Tab content keyed by tab id */
  children?: React.ReactNode;
  /** Visual variant */
  variant?: "line" | "pills" | "enclosed";
  /** Orientation */
  orientation?: "horizontal" | "vertical";
  /** Additional class name */
  className?: string;
}

export interface TabPanelProps {
  /** Tab id this panel belongs to */
  tabId: string;
  /** Currently active tab */
  activeTab: string;
  /** Panel content */
  children: React.ReactNode;
  /** Additional class name */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Tab Panel
// ═══════════════════════════════════════════════════════════════════════════

export function TabPanel({
  tabId,
  activeTab,
  children,
  className,
}: TabPanelProps) {
  if (tabId !== activeTab) return null;

  return (
    <div
      role="tabpanel"
      id={`tabpanel-${tabId}`}
      aria-labelledby={`tab-${tabId}`}
      tabIndex={0}
      className={cn("focus:outline-none", className)}
    >
      {children}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Tabs Component
// ═══════════════════════════════════════════════════════════════════════════

export function Tabs({
  tabs,
  activeTab: controlledActiveTab,
  onTabChange,
  children,
  variant = "line",
  orientation = "horizontal",
  className,
}: TabsProps) {
  const [internalActiveTab, setInternalActiveTab] = React.useState(
    tabs[0]?.id || "",
  );

  const activeTab = controlledActiveTab ?? internalActiveTab;

  const handleTabChange = (tabId: string) => {
    if (controlledActiveTab === undefined) {
      setInternalActiveTab(tabId);
    }
    onTabChange?.(tabId);
  };

  // Keyboard navigation
  const handleKeyDown = (event: React.KeyboardEvent, currentIndex: number) => {
    const enabledTabs = tabs.filter((tab) => !tab.disabled);
    const currentEnabledIndex = enabledTabs.findIndex(
      (tab) => tab.id === tabs[currentIndex].id,
    );

    let nextIndex: number;

    const isHorizontal = orientation === "horizontal";
    const prevKey = isHorizontal ? "ArrowLeft" : "ArrowUp";
    const nextKey = isHorizontal ? "ArrowRight" : "ArrowDown";

    switch (event.key) {
      case prevKey:
        event.preventDefault();
        nextIndex =
          currentEnabledIndex > 0
            ? currentEnabledIndex - 1
            : enabledTabs.length - 1;
        handleTabChange(enabledTabs[nextIndex].id);
        break;
      case nextKey:
        event.preventDefault();
        nextIndex =
          currentEnabledIndex < enabledTabs.length - 1
            ? currentEnabledIndex + 1
            : 0;
        handleTabChange(enabledTabs[nextIndex].id);
        break;
      case "Home":
        event.preventDefault();
        handleTabChange(enabledTabs[0].id);
        break;
      case "End":
        event.preventDefault();
        handleTabChange(enabledTabs[enabledTabs.length - 1].id);
        break;
    }
  };

  // Variant styles
  const variantStyles = {
    line: {
      list: "border-b border-gray-200",
      tab: cn(
        "px-4 py-2 -mb-px border-b-2 transition-colors",
        "hover:text-sahool-600 hover:border-gray-300",
        "focus:outline-none focus:ring-2 focus:ring-sahool-200 focus:ring-inset",
      ),
      active: "border-sahool-500 text-sahool-600 font-medium",
      inactive: "border-transparent text-gray-500",
    },
    pills: {
      list: "gap-2",
      tab: cn(
        "px-4 py-2 rounded-lg transition-colors",
        "hover:bg-gray-100",
        "focus:outline-none focus:ring-2 focus:ring-sahool-200",
      ),
      active: "bg-sahool-100 text-sahool-700 font-medium",
      inactive: "text-gray-600",
    },
    enclosed: {
      list: "border-b border-gray-200",
      tab: cn(
        "px-4 py-2 -mb-px border border-transparent rounded-t-lg transition-colors",
        "hover:bg-gray-50",
        "focus:outline-none focus:ring-2 focus:ring-sahool-200 focus:ring-inset",
      ),
      active:
        "bg-white border-gray-200 border-b-white text-sahool-600 font-medium",
      inactive: "text-gray-500",
    },
  };

  const styles = variantStyles[variant];

  return (
    <div className={cn(orientation === "vertical" && "flex gap-4", className)}>
      {/* Tab List */}
      <div
        role="tablist"
        aria-orientation={orientation}
        className={cn(
          "flex",
          orientation === "vertical" ? "flex-col" : "flex-row",
          styles.list,
        )}
      >
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            id={`tab-${tab.id}`}
            role="tab"
            type="button"
            aria-selected={activeTab === tab.id}
            aria-controls={`tabpanel-${tab.id}`}
            aria-disabled={tab.disabled}
            tabIndex={activeTab === tab.id ? 0 : -1}
            disabled={tab.disabled}
            onClick={() => !tab.disabled && handleTabChange(tab.id)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            className={cn(
              "flex items-center gap-2 whitespace-nowrap",
              styles.tab,
              activeTab === tab.id ? styles.active : styles.inactive,
              tab.disabled && "opacity-50 cursor-not-allowed",
            )}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Panels */}
      {children && (
        <div className={cn("flex-1", orientation === "horizontal" && "mt-4")}>
          {children}
        </div>
      )}
    </div>
  );
}

export default Tabs;
