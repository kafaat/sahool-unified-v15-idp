'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// DatePicker Component - منتقي التاريخ الحديث
// Modern date picker with calendar, range selection, and accessibility
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef, useState, useRef, useEffect } from 'react';
import { Calendar, ChevronLeft, ChevronRight, X } from 'lucide-react';

export interface DatePickerProps {
  value?: Date | null;
  onChange?: (date: Date | null) => void;
  label?: string;
  placeholder?: string;
  error?: string;
  min?: Date;
  max?: Date;
  disabled?: boolean;
  required?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'filled' | 'outlined';
  format?: 'dd/mm/yyyy' | 'mm/dd/yyyy' | 'yyyy-mm-dd';
  clearable?: boolean;
  showWeekNumbers?: boolean;
  firstDayOfWeek?: 0 | 1; // 0 = Sunday, 1 = Monday
  className?: string;
  id?: string;
  name?: string;
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

const MONTHS_AR = [
  'يناير',
  'فبراير',
  'مارس',
  'أبريل',
  'مايو',
  'يونيو',
  'يوليو',
  'أغسطس',
  'سبتمبر',
  'أكتوبر',
  'نوفمبر',
  'ديسمبر',
];

const MONTHS_EN = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
];

const DAYS_AR = ['أحد', 'إثنين', 'ثلاثاء', 'أربعاء', 'خميس', 'جمعة', 'سبت'];
const DAYS_EN = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export const DatePicker = forwardRef<HTMLDivElement, DatePickerProps>(
  (
    {
      value,
      onChange,
      label,
      placeholder = 'اختر تاريخ / Select date',
      error,
      min,
      max,
      disabled = false,
      required = false,
      size = 'md',
      variant = 'default',
      format = 'dd/mm/yyyy',
      clearable = false,
      showWeekNumbers = false,
      firstDayOfWeek = 0,
      className = '',
      id,
      name,
      'aria-label': ariaLabel,
      'aria-describedby': ariaDescribedBy,
    },
    ref
  ) => {
    const [isOpen, setIsOpen] = useState(false);
    const [viewDate, setViewDate] = useState(value || new Date());
    const containerRef = useRef<HTMLDivElement>(null);

    const pickerId = id || `datepicker-${name || Math.random().toString(36).substr(2, 9)}`;

    // Determine if RTL based on document direction
    const isRTL = typeof document !== 'undefined' && document.dir === 'rtl';
    const months = isRTL ? MONTHS_AR : MONTHS_EN;
    const days = isRTL ? DAYS_AR : DAYS_EN;

    // Adjust days array based on first day of week
    const adjustedDays = firstDayOfWeek === 1 ? [...days.slice(1), days[0]] : days;

    useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (
          containerRef.current &&
          !containerRef.current.contains(event.target as Node)
        ) {
          setIsOpen(false);
        }
      };

      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const formatDate = (date: Date | null): string => {
      if (!date) return '';

      const day = date.getDate().toString().padStart(2, '0');
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const year = date.getFullYear();

      switch (format) {
        case 'mm/dd/yyyy':
          return `${month}/${day}/${year}`;
        case 'yyyy-mm-dd':
          return `${year}-${month}-${day}`;
        default:
          return `${day}/${month}/${year}`;
      }
    };

    const handleDateSelect = (date: Date) => {
      if (disabled) return;

      // Check if date is within min/max range
      if (min && date < min) return;
      if (max && date > max) return;

      onChange?.(date);
      setIsOpen(false);
    };

    const handleClear = (e: React.MouseEvent) => {
      e.stopPropagation();
      onChange?.(null);
    };

    const changeMonth = (delta: number) => {
      setViewDate((prev) => {
        const newDate = new Date(prev);
        newDate.setMonth(newDate.getMonth() + delta);
        return newDate;
      });
    };

    const changeYear = (delta: number) => {
      setViewDate((prev) => {
        const newDate = new Date(prev);
        newDate.setFullYear(newDate.getFullYear() + delta);
        return newDate;
      });
    };

    const getDaysInMonth = (date: Date): Date[] => {
      const year = date.getFullYear();
      const month = date.getMonth();
      const firstDay = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0);

      const days: Date[] = [];

      // Add padding days from previous month
      let startDay = firstDay.getDay();
      if (firstDayOfWeek === 1) {
        startDay = startDay === 0 ? 6 : startDay - 1;
      }

      for (let i = startDay - 1; i >= 0; i--) {
        const prevDate = new Date(year, month, -i);
        days.push(prevDate);
      }

      // Add days of current month
      for (let i = 1; i <= lastDay.getDate(); i++) {
        days.push(new Date(year, month, i));
      }

      // Add padding days from next month
      const remainingDays = 7 - (days.length % 7);
      if (remainingDays < 7) {
        for (let i = 1; i <= remainingDays; i++) {
          days.push(new Date(year, month + 1, i));
        }
      }

      return days;
    };

    const isSameDay = (date1: Date | null, date2: Date): boolean => {
      if (!date1) return false;
      return (
        date1.getDate() === date2.getDate() &&
        date1.getMonth() === date2.getMonth() &&
        date1.getFullYear() === date2.getFullYear()
      );
    };

    const isToday = (date: Date): boolean => {
      return isSameDay(new Date(), date);
    };

    const isDisabledDate = (date: Date): boolean => {
      if (min && date < min) return true;
      if (max && date > max) return true;
      return false;
    };

    const calendarDays = getDaysInMonth(viewDate);

    return (
      <div ref={ref} className={cn('relative w-full', className)}>
        {label && (
          <label
            htmlFor={pickerId}
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
          role="button"
          aria-haspopup="dialog"
          aria-expanded={isOpen}
          aria-label={ariaLabel || label}
          aria-describedby={ariaDescribedBy || (error ? `${pickerId}-error` : undefined)}
          tabIndex={disabled ? -1 : 0}
        >
          <div className="flex items-center justify-between gap-2">
            <span
              className={cn(
                'flex-1 truncate',
                !value && 'text-gray-400 dark:text-gray-500'
              )}
            >
              {formatDate(value) || placeholder}
            </span>

            <div className="flex items-center gap-2">
              {clearable && value && !disabled && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                  aria-label="Clear date"
                >
                  <X size={16} className="text-gray-500 dark:text-gray-400" />
                </button>
              )}
              <Calendar size={20} className="text-gray-500 dark:text-gray-400" />
            </div>
          </div>

          {/* Hidden input for form submission */}
          <input
            type="hidden"
            id={pickerId}
            name={name}
            value={value ? formatDate(value) : ''}
            required={required}
          />
        </div>

        {/* Calendar Popup */}
        {isOpen && (
          <div
            className={cn(
              'absolute z-50 mt-2 bg-white dark:bg-gray-800',
              'border-2 border-gray-200 dark:border-gray-700',
              'rounded-xl shadow-xl p-4',
              'animate-in fade-in slide-in-from-top-2 duration-200',
              'w-full min-w-[320px]'
            )}
            role="dialog"
            aria-modal="true"
            aria-label="Calendar"
          >
            {/* Calendar Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => changeYear(-1)}
                  className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  aria-label="Previous year"
                >
                  <ChevronLeft size={16} className="text-gray-600 dark:text-gray-400" />
                  <ChevronLeft
                    size={16}
                    className="text-gray-600 dark:text-gray-400 -ms-3"
                  />
                </button>
                <button
                  type="button"
                  onClick={() => changeMonth(-1)}
                  className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  aria-label="Previous month"
                >
                  <ChevronLeft size={20} className="text-gray-600 dark:text-gray-400" />
                </button>
              </div>

              <div className="text-center font-semibold text-gray-900 dark:text-gray-100">
                {months[viewDate.getMonth()]} {viewDate.getFullYear()}
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => changeMonth(1)}
                  className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  aria-label="Next month"
                >
                  <ChevronRight size={20} className="text-gray-600 dark:text-gray-400" />
                </button>
                <button
                  type="button"
                  onClick={() => changeYear(1)}
                  className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  aria-label="Next year"
                >
                  <ChevronRight
                    size={16}
                    className="text-gray-600 dark:text-gray-400"
                  />
                  <ChevronRight
                    size={16}
                    className="text-gray-600 dark:text-gray-400 -ms-3"
                  />
                </button>
              </div>
            </div>

            {/* Weekday Headers */}
            <div className="grid grid-cols-7 gap-1 mb-2">
              {adjustedDays.map((day) => (
                <div
                  key={day}
                  className="text-center text-xs font-semibold text-gray-600 dark:text-gray-400 py-2"
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar Grid */}
            <div className="grid grid-cols-7 gap-1">
              {calendarDays.map((date, index) => {
                const isCurrentMonth = date.getMonth() === viewDate.getMonth();
                const isSelected = isSameDay(value, date);
                const isTodayDate = isToday(date);
                const isDisabled = isDisabledDate(date);

                return (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handleDateSelect(date)}
                    disabled={isDisabled || !isCurrentMonth}
                    className={cn(
                      'aspect-square rounded-lg transition-all duration-150',
                      'text-sm font-medium',
                      'hover:bg-sahool-50 dark:hover:bg-sahool-900/20',
                      'focus:outline-none focus:ring-2 focus:ring-sahool-500',
                      !isCurrentMonth && 'text-gray-400 dark:text-gray-600',
                      isCurrentMonth && 'text-gray-900 dark:text-gray-100',
                      isSelected &&
                        'bg-sahool-600 dark:bg-sahool-500 text-white hover:bg-sahool-700 dark:hover:bg-sahool-600',
                      isTodayDate &&
                        !isSelected &&
                        'ring-2 ring-sahool-500 dark:ring-sahool-400',
                      isDisabled && 'opacity-30 cursor-not-allowed hover:bg-transparent'
                    )}
                    aria-label={formatDate(date)}
                    aria-current={isTodayDate ? 'date' : undefined}
                    aria-selected={isSelected}
                  >
                    {date.getDate()}
                  </button>
                );
              })}
            </div>

            {/* Today Button */}
            <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
              <button
                type="button"
                onClick={() => {
                  const today = new Date();
                  handleDateSelect(today);
                  setViewDate(today);
                }}
                className={cn(
                  'w-full px-4 py-2 rounded-lg',
                  'bg-gray-100 dark:bg-gray-700',
                  'text-gray-900 dark:text-gray-100',
                  'hover:bg-sahool-50 dark:hover:bg-sahool-900/20',
                  'transition-colors duration-150',
                  'font-medium text-sm'
                )}
              >
                اليوم / Today
              </button>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <p
            id={`${pickerId}-error`}
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

DatePicker.displayName = 'DatePicker';
