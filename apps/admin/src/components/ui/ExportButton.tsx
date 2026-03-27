'use client';

/**
 * Export Button Component
 * زر التصدير
 */

import { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Download, FileSpreadsheet, FileText, ChevronDown, Loader2 } from 'lucide-react';
import { exportData, ExportFormat, ExportColumn, exportFormatLabels } from '@/lib/export';

interface ExportButtonProps {
  data: Record<string, unknown>[];
  columns: ExportColumn[];
  filename: string;
  title?: string;
  titleAr?: string;
  formats?: ExportFormat[];
  className?: string;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
}

export default function ExportButton({
  data,
  columns,
  filename,
  title,
  titleAr,
  formats = ['csv', 'excel', 'pdf'],
  className = '',
  variant = 'default',
  size = 'md',
  disabled = false,
}: ExportButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [exportingFormat, setExportingFormat] = useState<ExportFormat | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleExport = async (format: ExportFormat) => {
    if (disabled || isExporting) return;

    setIsExporting(true);
    setExportingFormat(format);

    try {
      // Small delay for UI feedback
      await new Promise((resolve) => setTimeout(resolve, 300));

      exportData({
        filename,
        title,
        titleAr,
        columns,
        data,
        format,
        includeHeader: true,
      });

      setIsOpen(false);
    } catch {
      // Export failed - error is handled by the export utility
    } finally {
      setIsExporting(false);
      setExportingFormat(null);
    }
  };

  const getFormatIcon = (format: ExportFormat) => {
    switch (format) {
      case 'csv':
        return FileText;
      case 'excel':
        return FileSpreadsheet;
      case 'pdf':
        return FileText;
      default:
        return Download;
    }
  };

  const getFormatColor = (format: ExportFormat) => {
    switch (format) {
      case 'csv':
        return 'text-green-600 bg-green-50 dark:bg-green-900/30';
      case 'excel':
        return 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/30';
      case 'pdf':
        return 'text-red-600 bg-red-50 dark:bg-red-900/30';
      default:
        return 'text-gray-600 bg-gray-50 dark:bg-gray-800';
    }
  };

  const variantClasses = {
    default: 'bg-sahool-600 hover:bg-sahool-700 text-white',
    outline:
      'border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700',
    ghost: 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-2.5 text-base',
  };

  // If only one format, show direct button
  if (formats.length === 1) {
    const format = formats[0] as ExportFormat;
    const Icon = getFormatIcon(format);

    return (
      <button
        onClick={() => handleExport(format)}
        disabled={disabled || isExporting || data.length === 0}
        className={cn(
          'inline-flex items-center gap-2 rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed',
          variantClasses[variant],
          sizeClasses[size],
          className
        )}
      >
        {isExporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Icon className="w-4 h-4" />}
        <span>تصدير {exportFormatLabels[format].ar}</span>
      </button>
    );
  }

  return (
    <div ref={dropdownRef} className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled || data.length === 0}
        className={cn(
          'inline-flex items-center gap-2 rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed',
          variantClasses[variant],
          sizeClasses[size],
          className
        )}
      >
        {isExporting ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Download className="w-4 h-4" />
        )}
        <span>تصدير</span>
        <ChevronDown className={cn('w-4 h-4 transition-transform', isOpen && 'rotate-180')} />
      </button>

      {isOpen && (
        <div className="absolute left-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 py-2 z-50 animate-in fade-in slide-in-from-top-2">
          {formats.map((format) => {
            const Icon = getFormatIcon(format);
            const isFormatExporting = isExporting && exportingFormat === format;

            return (
              <button
                key={format}
                onClick={() => handleExport(format)}
                disabled={isExporting}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
              >
                <div className={cn('p-1.5 rounded-lg', getFormatColor(format))}>
                  {isFormatExporting ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Icon className="w-4 h-4" />
                  )}
                </div>
                <div className="flex-1 text-right">
                  <div className="font-medium">{exportFormatLabels[format].ar}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {format === 'csv' && 'ملف نصي مفصول بفاصلة'}
                    {format === 'excel' && 'جدول بيانات Microsoft'}
                    {format === 'pdf' && 'مستند قابل للطباعة'}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
