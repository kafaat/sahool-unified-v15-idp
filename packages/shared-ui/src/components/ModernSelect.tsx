'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernSelect Component - قائمة منسدلة حديثة
// Advanced dropdown with search, multi-select, and custom styling
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef, useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Check, ChevronDown, X, Search } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
  icon?: React.ReactNode;
}

export interface ModernSelectProps {
  options: SelectOption[];
  value?: string | string[];
  onChange?: (value: string | string[]) => void;
  placeholder?: string;
  label?: string;
  error?: string;
  disabled?: boolean;
  searchable?: boolean;
  multiple?: boolean;
  clearable?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'filled' | 'outlined';
  className?: string;
  id?: string;
  name?: string;
  required?: boolean;
  'aria-label'?: string;
  'aria-describedby'?: string;
}

const sizeClasses = {
  sm: 'px-3 py-2 text-sm rounded-lg',
  md: 'px-4 py-3 text-base rounded-xl',
  lg: 'px-5 py-4 text-lg rounded-2xl',
};

const variantClasses = {
  default:
    'bg-white dark:bg-gray-900 border-2 border-gray-300 dark:border-gray-700 focus-within:border-sahool-500 dark:focus-within:border-sahool-400',
  filled:
    'bg-gray-100 dark:bg-gray-800 border-2 border-transparent focus-within:border-sahool-500 dark:focus-within:border-sahool-400',
  outlined:
    'bg-transparent border-2 border-sahool-500 dark:border-sahool-400 focus-within:border-sahool-600 dark:focus-within:border-sahool-300',
};

export const ModernSelect = forwardRef<HTMLDivElement, ModernSelectProps>(
  (
    {
      options,
      value,
      onChange,
      placeholder = 'اختر خيار / Select option',
      label,
      error,
      disabled = false,
      searchable = false,
      multiple = false,
      clearable = false,
      size = 'md',
      variant = 'default',
      className = '',
      id,
      name,
      required = false,
      'aria-label': ariaLabel,
      'aria-describedby': ariaDescribedBy,
    },
    ref
  ) => {
    const [isOpen, setIsOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [focusedIndex, setFocusedIndex] = useState(-1);
    const containerRef = useRef<HTMLDivElement>(null);
    const searchInputRef = useRef<HTMLInputElement>(null);

    const selectedValues = Array.isArray(value) ? value : value ? [value] : [];

    const filteredOptions = searchable
      ? options.filter((option) =>
          option.label.toLowerCase().includes(searchQuery.toLowerCase())
        )
      : options;

    const selectedLabels = options
      .filter((opt) => selectedValues.includes(opt.value))
      .map((opt) => opt.label)
      .join(', ');

    useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (
          containerRef.current &&
          !containerRef.current.contains(event.target as Node)
        ) {
          setIsOpen(false);
          setSearchQuery('');
        }
      };

      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    useEffect(() => {
      if (isOpen && searchable && searchInputRef.current) {
        searchInputRef.current.focus();
      }
    }, [isOpen, searchable]);

    const handleSelect = (optionValue: string) => {
      if (multiple) {
        const newValues = selectedValues.includes(optionValue)
          ? selectedValues.filter((v) => v !== optionValue)
          : [...selectedValues, optionValue];
        onChange?.(newValues);
      } else {
        onChange?.(optionValue);
        setIsOpen(false);
        setSearchQuery('');
      }
    };

    const handleClear = (e: React.MouseEvent) => {
      e.stopPropagation();
      onChange?.(multiple ? [] : '');
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
      if (disabled) return;

      switch (e.key) {
        case 'Enter':
        case ' ':
          if (!isOpen) {
            setIsOpen(true);
          } else if (focusedIndex >= 0 && focusedIndex < filteredOptions.length) {
            handleSelect(filteredOptions[focusedIndex].value);
          }
          e.preventDefault();
          break;
        case 'Escape':
          setIsOpen(false);
          setSearchQuery('');
          break;
        case 'ArrowDown':
          if (!isOpen) {
            setIsOpen(true);
          } else {
            setFocusedIndex((prev) =>
              prev < filteredOptions.length - 1 ? prev + 1 : prev
            );
          }
          e.preventDefault();
          break;
        case 'ArrowUp':
          if (isOpen) {
            setFocusedIndex((prev) => (prev > 0 ? prev - 1 : 0));
          }
          e.preventDefault();
          break;
      }
    };

    return (
      <div ref={ref} className={cn('relative w-full', className)}>
        {label && (
          <label
            htmlFor={id}
            className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            {label}
            {required && <span className="text-red-500 ms-1">*</span>}
          </label>
        )}

        <div
          ref={containerRef}
          className={cn(
            'relative w-full transition-all duration-200',
            variantClasses[variant],
            sizeClasses[size],
            disabled
              ? 'opacity-50 cursor-not-allowed'
              : 'cursor-pointer hover:shadow-lg',
            error && 'border-red-500 dark:border-red-400',
            'focus-within:ring-4 focus-within:ring-sahool-500/20'
          )}
          onClick={() => !disabled && setIsOpen(!isOpen)}
          onKeyDown={handleKeyDown}
          role="combobox"
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          aria-label={ariaLabel}
          aria-describedby={ariaDescribedBy || (error ? `${id}-error` : undefined)}
          aria-required={required}
          aria-disabled={disabled}
          tabIndex={disabled ? -1 : 0}
        >
          <div className="flex items-center justify-between gap-2">
            <span
              className={cn(
                'flex-1 truncate',
                !selectedLabels && 'text-gray-400 dark:text-gray-500'
              )}
            >
              {selectedLabels || placeholder}
            </span>

            <div className="flex items-center gap-2">
              {clearable && selectedLabels && !disabled && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                  aria-label="Clear selection"
                >
                  <X size={16} className="text-gray-500 dark:text-gray-400" />
                </button>
              )}
              <ChevronDown
                size={20}
                className={cn(
                  'text-gray-500 dark:text-gray-400 transition-transform duration-200',
                  isOpen && 'rotate-180'
                )}
              />
            </div>
          </div>

          {/* Hidden input for form submission */}
          <input
            type="hidden"
            id={id}
            name={name}
            value={Array.isArray(value) ? value.join(',') : value || ''}
            required={required}
          />
        </div>

        {/* Dropdown Menu */}
        {isOpen && (
          <div
            className={cn(
              'absolute z-50 w-full mt-2 bg-white dark:bg-gray-800',
              'border-2 border-gray-200 dark:border-gray-700',
              'rounded-xl shadow-xl max-h-64 overflow-hidden',
              'animate-in fade-in slide-in-from-top-2 duration-200'
            )}
            role="listbox"
            aria-multiselectable={multiple}
          >
            {searchable && (
              <div className="p-2 border-b border-gray-200 dark:border-gray-700">
                <div className="relative">
                  <Search
                    size={18}
                    className="absolute start-3 top-1/2 -translate-y-1/2 text-gray-400"
                  />
                  <input
                    ref={searchInputRef}
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="بحث... / Search..."
                    className={cn(
                      'w-full ps-10 pe-3 py-2 rounded-lg',
                      'bg-gray-100 dark:bg-gray-700',
                      'text-gray-900 dark:text-gray-100',
                      'placeholder:text-gray-500 dark:placeholder:text-gray-400',
                      'focus:outline-none focus:ring-2 focus:ring-sahool-500'
                    )}
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>
              </div>
            )}

            <div className="max-h-48 overflow-y-auto">
              {filteredOptions.length === 0 ? (
                <div className="px-4 py-3 text-center text-gray-500 dark:text-gray-400">
                  لا توجد نتائج / No results found
                </div>
              ) : (
                filteredOptions.map((option, index) => {
                  const isSelected = selectedValues.includes(option.value);
                  const isFocused = index === focusedIndex;

                  return (
                    <div
                      key={option.value}
                      onClick={(e) => {
                        e.stopPropagation();
                        if (!option.disabled) {
                          handleSelect(option.value);
                        }
                      }}
                      className={cn(
                        'flex items-center gap-3 px-4 py-3 cursor-pointer transition-all duration-150',
                        option.disabled
                          ? 'opacity-50 cursor-not-allowed'
                          : 'hover:bg-sahool-50 dark:hover:bg-sahool-900/20',
                        isSelected &&
                          'bg-sahool-100 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300',
                        isFocused && 'bg-gray-100 dark:bg-gray-700'
                      )}
                      role="option"
                      aria-selected={isSelected}
                      aria-disabled={option.disabled}
                    >
                      {option.icon && <span className="shrink-0">{option.icon}</span>}
                      <span className="flex-1">{option.label}</span>
                      {isSelected && (
                        <Check
                          size={18}
                          className="shrink-0 text-sahool-600 dark:text-sahool-400"
                        />
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <p
            id={`${id}-error`}
            className="mt-2 text-sm text-red-600 dark:text-red-400"
            role="alert"
          >
            {error}
          </p>
        )}
      </div>
    );
  }
);

ModernSelect.displayName = 'ModernSelect';
