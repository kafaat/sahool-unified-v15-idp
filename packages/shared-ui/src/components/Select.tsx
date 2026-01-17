"use client";

/**
 * Select Component
 * مكون القائمة المنسدلة
 *
 * A dropdown select component with search support
 */

import * as React from "react";
import { ChevronDown, Check, Search, AlertCircle } from "lucide-react";
import { cn } from "@sahool/shared-utils";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps {
  /** Options to display */
  options: SelectOption[];
  /** Selected value */
  value?: string;
  /** Callback when value changes */
  onChange?: (value: string) => void;
  /** Label text */
  label?: string;
  /** Error message */
  error?: string;
  /** Hint text */
  hint?: string;
  /** Placeholder text */
  placeholder?: string;
  /** Whether the select is disabled */
  disabled?: boolean;
  /** Whether the select is required */
  required?: boolean;
  /** Whether to enable search */
  searchable?: boolean;
  /** Input size */
  size?: "sm" | "md" | "lg";
  /** Full width */
  fullWidth?: boolean;
  /** Additional class name */
  className?: string;
  /** Name for form submission */
  name?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export function Select({
  options,
  value,
  onChange,
  label,
  error,
  hint,
  placeholder = "Select an option",
  disabled = false,
  required = false,
  searchable = false,
  size = "md",
  fullWidth = true,
  className,
  name,
}: SelectProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const [searchTerm, setSearchTerm] = React.useState("");
  const selectRef = React.useRef<HTMLDivElement>(null);
  const inputId = React.useId();
  const errorId = `${inputId}-error`;
  const hintId = `${inputId}-hint`;

  const sizeClasses = {
    sm: "px-2.5 py-1.5 text-sm",
    md: "px-3 py-2 text-base",
    lg: "px-4 py-3 text-lg",
  };

  // Filter options based on search
  const filteredOptions = React.useMemo(() => {
    if (!searchTerm) return options;
    return options.filter((option) =>
      option.label.toLowerCase().includes(searchTerm.toLowerCase()),
    );
  }, [options, searchTerm]);

  // Find selected option
  const selectedOption = options.find((opt) => opt.value === value);

  // Handle click outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        selectRef.current &&
        !selectRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setSearchTerm("");
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Handle keyboard navigation
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (disabled) return;

    switch (event.key) {
      case "Enter":
      case " ":
        event.preventDefault();
        setIsOpen(!isOpen);
        break;
      case "Escape":
        setIsOpen(false);
        setSearchTerm("");
        break;
    }
  };

  // Handle option select
  const handleSelect = (optionValue: string) => {
    onChange?.(optionValue);
    setIsOpen(false);
    setSearchTerm("");
  };

  // Non-searchable: use native select for accessibility
  if (!searchable) {
    return (
      <div className={cn("flex flex-col gap-1.5", fullWidth && "w-full")}>
        {label && (
          <label
            htmlFor={inputId}
            className={cn(
              "text-sm font-medium text-gray-700",
              disabled && "text-gray-400",
            )}
          >
            {label}
            {required && <span className="text-red-500 ms-1">*</span>}
          </label>
        )}

        <div className="relative">
          <select
            id={inputId}
            name={name}
            value={value}
            onChange={(e) => onChange?.(e.target.value)}
            disabled={disabled}
            required={required}
            aria-invalid={!!error}
            aria-describedby={error ? errorId : hint ? hintId : undefined}
            className={cn(
              "block w-full rounded-lg border bg-white text-gray-900 appearance-none",
              "focus:outline-none focus:ring-2 focus:ring-offset-0",
              sizeClasses[size],
              "pe-10",
              error
                ? "border-red-500 focus:border-red-500 focus:ring-red-200"
                : "border-gray-300 focus:border-sahool-500 focus:ring-sahool-200",
              disabled && "bg-gray-100 text-gray-500 cursor-not-allowed",
              className,
            )}
          >
            <option value="" disabled>
              {placeholder}
            </option>
            {options.map((option) => (
              <option
                key={option.value}
                value={option.value}
                disabled={option.disabled}
              >
                {option.label}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute end-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
        </div>

        {error && (
          <p id={errorId} role="alert" className="text-sm text-red-600">
            {error}
          </p>
        )}
        {hint && !error && (
          <p id={hintId} className="text-sm text-gray-500">
            {hint}
          </p>
        )}
      </div>
    );
  }

  // Searchable: custom dropdown
  return (
    <div
      ref={selectRef}
      className={cn("flex flex-col gap-1.5", fullWidth && "w-full", className)}
    >
      {label && (
        <label
          htmlFor={inputId}
          className={cn(
            "text-sm font-medium text-gray-700",
            disabled && "text-gray-400",
          )}
        >
          {label}
          {required && <span className="text-red-500 ms-1">*</span>}
        </label>
      )}

      <div className="relative">
        {/* Hidden native select for form submission */}
        <select
          name={name}
          value={value}
          onChange={() => {}}
          className="sr-only"
          tabIndex={-1}
          aria-hidden="true"
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Custom trigger */}
        <button
          type="button"
          id={inputId}
          disabled={disabled}
          onClick={() => setIsOpen(!isOpen)}
          onKeyDown={handleKeyDown}
          aria-haspopup="listbox"
          aria-expanded={isOpen}
          aria-invalid={!!error}
          aria-describedby={error ? errorId : hint ? hintId : undefined}
          className={cn(
            "flex items-center justify-between w-full rounded-lg border bg-white text-start",
            "focus:outline-none focus:ring-2 focus:ring-offset-0",
            sizeClasses[size],
            error
              ? "border-red-500 focus:border-red-500 focus:ring-red-200"
              : "border-gray-300 focus:border-sahool-500 focus:ring-sahool-200",
            disabled && "bg-gray-100 text-gray-500 cursor-not-allowed",
          )}
        >
          <span className={!selectedOption ? "text-gray-400" : "text-gray-900"}>
            {selectedOption?.label || placeholder}
          </span>
          {error ? (
            <AlertCircle className="w-5 h-5 text-red-500" />
          ) : (
            <ChevronDown
              className={cn(
                "w-5 h-5 text-gray-400 transition-transform",
                isOpen && "rotate-180",
              )}
            />
          )}
        </button>

        {/* Dropdown */}
        {isOpen && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg">
            {/* Search input */}
            <div className="p-2 border-b border-gray-200">
              <div className="relative">
                <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search..."
                  className="w-full ps-9 pe-3 py-2 text-sm border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sahool-200"
                  autoFocus
                />
              </div>
            </div>

            {/* Options list */}
            <ul role="listbox" className="max-h-60 overflow-y-auto py-1">
              {filteredOptions.length === 0 ? (
                <li className="px-3 py-2 text-sm text-gray-500">
                  No options found
                </li>
              ) : (
                filteredOptions.map((option) => (
                  <li
                    key={option.value}
                    role="option"
                    aria-selected={option.value === value}
                    aria-disabled={option.disabled}
                    onClick={() =>
                      !option.disabled && handleSelect(option.value)
                    }
                    className={cn(
                      "flex items-center justify-between px-3 py-2 text-sm cursor-pointer",
                      option.value === value
                        ? "bg-sahool-50 text-sahool-700"
                        : "text-gray-900 hover:bg-gray-50",
                      option.disabled && "opacity-50 cursor-not-allowed",
                    )}
                  >
                    {option.label}
                    {option.value === value && (
                      <Check className="w-4 h-4 text-sahool-600" />
                    )}
                  </li>
                ))
              )}
            </ul>
          </div>
        )}
      </div>

      {error && (
        <p id={errorId} role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}
      {hint && !error && (
        <p id={hintId} className="text-sm text-gray-500">
          {hint}
        </p>
      )}
    </div>
  );
}

export default Select;
