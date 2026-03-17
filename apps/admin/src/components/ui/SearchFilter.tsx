"use client";

/**
 * Search Filter Component
 * مكون البحث والفلترة
 */

import { useState, useCallback, useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import {
  Search,
  X,
  Filter,
  ChevronDown,
  Calendar,
  Check,
} from "lucide-react";

export interface FilterOption {
  value: string;
  label: string;
  labelAr?: string;
  count?: number;
}

export interface FilterConfig {
  key: string;
  label: string;
  labelAr?: string;
  type: "select" | "multiselect" | "date" | "daterange";
  options?: FilterOption[];
  placeholder?: string;
}

export interface ActiveFilter {
  key: string;
  value: string | string[] | { from: string; to: string };
  label: string;
}

interface SearchFilterProps {
  searchPlaceholder?: string;
  searchPlaceholderAr?: string;
  searchValue?: string;
  onSearchChange?: (value: string) => void;
  filters?: FilterConfig[];
  activeFilters?: ActiveFilter[];
  onFilterChange?: (key: string, value: unknown) => void;
  onClearFilters?: () => void;
  className?: string;
  showFilterCount?: boolean;
  debounceMs?: number;
}

export default function SearchFilter({
  searchPlaceholder: _searchPlaceholder = "Search...",
  searchPlaceholderAr = "بحث...",
  searchValue: controlledSearchValue,
  onSearchChange,
  filters = [],
  activeFilters = [],
  onFilterChange,
  onClearFilters,
  className = "",
  showFilterCount = true,
  debounceMs = 300,
}: SearchFilterProps) {
  // Note: _searchPlaceholder available for future i18n support
  const [internalSearchValue, setInternalSearchValue] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  const searchValue = controlledSearchValue ?? internalSearchValue;

  // Handle click outside to close dropdowns
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setOpenDropdown(null);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Clear debounce timer on unmount to prevent state updates after unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  // Debounced search
  const handleSearchChange = useCallback(
    (value: string) => {
      setInternalSearchValue(value);

      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }

      debounceRef.current = setTimeout(() => {
        onSearchChange?.(value);
      }, debounceMs);
    },
    [onSearchChange, debounceMs]
  );

  const handleClearSearch = useCallback(() => {
    setInternalSearchValue("");
    onSearchChange?.("");
  }, [onSearchChange]);

  const handleFilterSelect = useCallback(
    (filterKey: string, value: string, isMulti: boolean) => {
      if (isMulti) {
        const currentFilter = activeFilters.find((f) => f.key === filterKey);
        const currentValues = (currentFilter?.value as string[]) || [];
        const newValues = currentValues.includes(value)
          ? currentValues.filter((v) => v !== value)
          : [...currentValues, value];
        onFilterChange?.(filterKey, newValues);
      } else {
        onFilterChange?.(filterKey, value);
        setOpenDropdown(null);
      }
    },
    [activeFilters, onFilterChange]
  );

  const getFilterValue = useCallback(
    (filterKey: string) => {
      return activeFilters.find((f) => f.key === filterKey)?.value;
    },
    [activeFilters]
  );

  const activeFilterCount = activeFilters.filter(
    (f) =>
      f.value &&
      (Array.isArray(f.value) ? f.value.length > 0 : f.value !== "")
  ).length;

  return (
    <div className={cn("space-y-4", className)}>
      {/* Main search bar */}
      <div className="flex items-center gap-4">
        <div className="flex-1 relative">
          <input
            type="text"
            value={searchValue}
            onChange={(e) => handleSearchChange(e.target.value)}
            placeholder={searchPlaceholderAr}
            className="w-full pl-10 pr-12 py-3 text-sm border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
            aria-label={searchPlaceholderAr}
          />
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
            aria-hidden="true"
          />
          {searchValue && (
            <button
              onClick={handleClearSearch}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
              aria-label="مسح البحث"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          )}
        </div>

        {filters.length > 0 && (
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={cn(
              "flex items-center gap-2 px-4 py-3 rounded-xl border transition-colors",
              showFilters
                ? "bg-sahool-50 dark:bg-sahool-900/30 border-sahool-200 dark:border-sahool-700 text-sahool-700 dark:text-sahool-300"
                : "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            )}
          >
            <Filter className="w-5 h-5" />
            <span className="text-sm font-medium">الفلاتر</span>
            {showFilterCount && activeFilterCount > 0 && (
              <span className="flex items-center justify-center w-5 h-5 text-xs font-bold bg-sahool-600 text-white rounded-full">
                {activeFilterCount}
              </span>
            )}
          </button>
        )}
      </div>

      {/* Filter dropdowns */}
      {showFilters && filters.length > 0 && (
        <div
          ref={dropdownRef}
          className="flex flex-wrap items-center gap-3 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl"
        >
          {filters.map((filter) => {
            const isOpen = openDropdown === filter.key;
            const currentValue = getFilterValue(filter.key);
            const isMulti = filter.type === "multiselect";
            const selectedCount = isMulti
              ? (currentValue as string[])?.length || 0
              : 0;

            return (
              <div key={filter.key} className="relative">
                <button
                  onClick={() => setOpenDropdown(isOpen ? null : filter.key)}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-lg border text-sm transition-colors",
                    currentValue &&
                      (Array.isArray(currentValue)
                        ? currentValue.length > 0
                        : currentValue !== "")
                      ? "bg-sahool-50 dark:bg-sahool-900/30 border-sahool-200 dark:border-sahool-700 text-sahool-700 dark:text-sahool-300"
                      : "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                  )}
                >
                  {filter.type === "date" || filter.type === "daterange" ? (
                    <Calendar className="w-4 h-4" />
                  ) : null}
                  <span>{filter.labelAr || filter.label}</span>
                  {isMulti && selectedCount > 0 && (
                    <span className="flex items-center justify-center min-w-[20px] h-5 px-1 text-xs font-bold bg-sahool-600 text-white rounded-full">
                      {selectedCount}
                    </span>
                  )}
                  <ChevronDown
                    className={cn(
                      "w-4 h-4 transition-transform",
                      isOpen && "rotate-180"
                    )}
                  />
                </button>

                {isOpen && filter.options && (
                  <div className="absolute top-full mt-2 left-0 z-50 min-w-[200px] bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 py-2 max-h-64 overflow-y-auto">
                    {filter.options.map((option) => {
                      const isSelected = isMulti
                        ? (currentValue as string[])?.includes(option.value)
                        : currentValue === option.value;

                      return (
                        <button
                          key={option.value}
                          onClick={() =>
                            handleFilterSelect(filter.key, option.value, isMulti)
                          }
                          className={cn(
                            "w-full flex items-center justify-between px-4 py-2 text-sm transition-colors",
                            isSelected
                              ? "bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300"
                              : "text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                          )}
                        >
                          <span>{option.labelAr || option.label}</span>
                          <div className="flex items-center gap-2">
                            {option.count !== undefined && (
                              <span className="text-xs text-gray-400">
                                ({option.count})
                              </span>
                            )}
                            {isSelected && (
                              <Check className="w-4 h-4 text-sahool-600" />
                            )}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}

                {isOpen &&
                  (filter.type === "date" || filter.type === "daterange") && (
                    <div className="absolute top-full mt-2 left-0 z-50 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-4">
                      {filter.type === "date" ? (
                        <input
                          type="date"
                          value={(currentValue as string) || ""}
                          onChange={(e) =>
                            onFilterChange?.(filter.key, e.target.value)
                          }
                          className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                        />
                      ) : (
                        <div className="flex items-center gap-2">
                          <input
                            type="date"
                            value={
                              (currentValue as { from: string; to: string })
                                ?.from || ""
                            }
                            onChange={(e) =>
                              onFilterChange?.(filter.key, {
                                ...(currentValue as { from: string; to: string }),
                                from: e.target.value,
                              })
                            }
                            className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                          />
                          <span className="text-gray-400">-</span>
                          <input
                            type="date"
                            value={
                              (currentValue as { from: string; to: string })
                                ?.to || ""
                            }
                            onChange={(e) =>
                              onFilterChange?.(filter.key, {
                                ...(currentValue as { from: string; to: string }),
                                to: e.target.value,
                              })
                            }
                            className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                          />
                        </div>
                      )}
                    </div>
                  )}
              </div>
            );
          })}

          {activeFilterCount > 0 && (
            <button
              onClick={onClearFilters}
              className="flex items-center gap-1 px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
              مسح الكل
            </button>
          )}
        </div>
      )}

      {/* Active filter chips */}
      {activeFilters.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          {activeFilters
            .filter(
              (f) =>
                f.value &&
                (Array.isArray(f.value) ? f.value.length > 0 : f.value !== "")
            )
            .map((filter) => (
              <div
                key={filter.key}
                className="flex items-center gap-1 px-3 py-1 bg-sahool-100 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300 rounded-full text-sm"
              >
                <span className="font-medium">{filter.label}:</span>
                <span>
                  {Array.isArray(filter.value)
                    ? filter.value.join(", ")
                    : typeof filter.value === "object"
                      ? `${(filter.value as { from: string; to: string }).from} - ${(filter.value as { from: string; to: string }).to}`
                      : filter.value}
                </span>
                <button
                  onClick={() => onFilterChange?.(filter.key, null)}
                  className="p-0.5 rounded-full hover:bg-sahool-200 dark:hover:bg-sahool-800"
                  aria-label="إزالة الفلتر"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
