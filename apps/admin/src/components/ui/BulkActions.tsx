'use client';

/**
 * Bulk Actions Component
 * مكون العمليات الجماعية
 */

import { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import {
  Trash2,
  Download,
  Send,
  Archive,
  Tag,
  Edit2,
  MoreHorizontal,
  CheckCircle,
  AlertTriangle,
  Loader2,
} from 'lucide-react';

export interface BulkAction {
  id: string;
  label: string;
  labelAr: string;
  icon: React.ElementType;
  variant?: 'default' | 'primary' | 'danger' | 'warning';
  confirmMessage?: string;
  confirmMessageAr?: string;
  requireConfirmation?: boolean;
}

interface BulkActionsProps {
  selectedCount: number;
  totalCount: number;
  onSelectAll?: () => void;
  onDeselectAll?: () => void;
  actions?: BulkAction[];
  onAction?: (actionId: string) => Promise<void>;
  className?: string;
  isLoading?: boolean;
  loadingAction?: string;
}

const defaultActions: BulkAction[] = [
  {
    id: 'export',
    label: 'Export',
    labelAr: 'تصدير',
    icon: Download,
    variant: 'default',
  },
  {
    id: 'archive',
    label: 'Archive',
    labelAr: 'أرشفة',
    icon: Archive,
    variant: 'default',
  },
  {
    id: 'tag',
    label: 'Add Tag',
    labelAr: 'إضافة وسم',
    icon: Tag,
    variant: 'default',
  },
  {
    id: 'delete',
    label: 'Delete',
    labelAr: 'حذف',
    icon: Trash2,
    variant: 'danger',
    requireConfirmation: true,
    confirmMessageAr: 'هل أنت متأكد من حذف العناصر المحددة؟',
    confirmMessage: 'Are you sure you want to delete the selected items?',
  },
];

export default function BulkActions({
  selectedCount,
  totalCount,
  onSelectAll,
  onDeselectAll,
  actions = defaultActions,
  onAction,
  className = '',
  isLoading = false,
  loadingAction,
}: BulkActionsProps) {
  const [showMore, setShowMore] = useState(false);
  const [confirmAction, setConfirmAction] = useState<BulkAction | null>(null);
  const [actionResult, setActionResult] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);

  const handleAction = useCallback(
    async (action: BulkAction) => {
      if (action.requireConfirmation && !confirmAction) {
        setConfirmAction(action);
        return;
      }

      setConfirmAction(null);
      setActionResult(null);

      try {
        await onAction?.(action.id);
        setActionResult({
          type: 'success',
          message: `تم تنفيذ "${action.labelAr}" بنجاح`,
        });
        setTimeout(() => setActionResult(null), 3000);
      } catch {
        setActionResult({
          type: 'error',
          message: `فشل تنفيذ "${action.labelAr}"`,
        });
        setTimeout(() => setActionResult(null), 5000);
      }
    },
    [confirmAction, onAction]
  );

  const getVariantClasses = (variant: BulkAction['variant']) => {
    switch (variant) {
      case 'primary':
        return 'bg-sahool-600 hover:bg-sahool-700 text-white';
      case 'danger':
        return 'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20';
      case 'warning':
        return 'text-yellow-600 dark:text-yellow-400 hover:bg-yellow-50 dark:hover:bg-yellow-900/20';
      default:
        return 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700';
    }
  };

  if (selectedCount === 0) {
    return null;
  }

  // Show first 4 actions, rest in dropdown
  const visibleActions = actions.slice(0, 4);
  const moreActions = actions.slice(4);

  return (
    <>
      {/* Bulk Actions Bar */}
      <div
        className={cn(
          'sticky top-0 z-20 flex items-center justify-between px-6 py-3 bg-sahool-50 dark:bg-sahool-900/30 border border-sahool-200 dark:border-sahool-700 rounded-xl',
          className
        )}
      >
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="flex items-center justify-center w-8 h-8 bg-sahool-600 text-white rounded-full text-sm font-bold">
              {selectedCount}
            </span>
            <span className="text-sm text-gray-700 dark:text-gray-300">
              عنصر محدد من {totalCount}
            </span>
          </div>

          <div className="h-6 w-px bg-sahool-200 dark:bg-sahool-700" />

          <div className="flex items-center gap-1">
            {selectedCount < totalCount && onSelectAll && (
              <button
                onClick={onSelectAll}
                className="px-3 py-1.5 text-sm text-sahool-700 dark:text-sahool-300 hover:bg-sahool-100 dark:hover:bg-sahool-800/50 rounded-lg transition-colors"
              >
                تحديد الكل ({totalCount})
              </button>
            )}
            {onDeselectAll && (
              <button
                onClick={onDeselectAll}
                className="px-3 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                إلغاء التحديد
              </button>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Action Result Toast */}
          {actionResult && (
            <div
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm animate-in slide-in-from-right',
                actionResult.type === 'success'
                  ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                  : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
              )}
            >
              {actionResult.type === 'success' ? (
                <CheckCircle className="w-4 h-4" />
              ) : (
                <AlertTriangle className="w-4 h-4" />
              )}
              {actionResult.message}
            </div>
          )}

          {/* Visible Actions */}
          {visibleActions.map((action) => {
            const Icon = action.icon;
            const isActionLoading = isLoading && loadingAction === action.id;

            return (
              <button
                key={action.id}
                onClick={() => handleAction(action)}
                disabled={isLoading}
                className={cn(
                  'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed',
                  getVariantClasses(action.variant)
                )}
                title={action.labelAr}
              >
                {isActionLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Icon className="w-4 h-4" />
                )}
                <span className="hidden sm:inline">{action.labelAr}</span>
              </button>
            );
          })}

          {/* More Actions Dropdown */}
          {moreActions.length > 0 && (
            <div className="relative">
              <button
                onClick={() => setShowMore(!showMore)}
                className="p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <MoreHorizontal className="w-5 h-5" />
              </button>

              {showMore && (
                <div className="absolute left-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 py-2 z-50">
                  {moreActions.map((action) => {
                    const Icon = action.icon;
                    return (
                      <button
                        key={action.id}
                        onClick={() => {
                          handleAction(action);
                          setShowMore(false);
                        }}
                        className={cn(
                          'w-full flex items-center gap-2 px-4 py-2 text-sm transition-colors',
                          getVariantClasses(action.variant)
                        )}
                      >
                        <Icon className="w-4 h-4" />
                        {action.labelAr}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Confirmation Modal */}
      {confirmAction && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="w-full max-w-md bg-white dark:bg-gray-800 rounded-2xl shadow-xl">
            <div className="p-6">
              <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 rounded-full bg-red-100 dark:bg-red-900/30">
                <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
              </div>

              <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 text-center mb-2">
                تأكيد العملية
              </h3>

              <p className="text-gray-600 dark:text-gray-400 text-center mb-6">
                {confirmAction.confirmMessageAr ||
                  `هل أنت متأكد من تنفيذ "${confirmAction.labelAr}" على ${selectedCount} عنصر؟`}
              </p>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => setConfirmAction(null)}
                  className="flex-1 px-4 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  إلغاء
                </button>
                <button
                  onClick={() => handleAction(confirmAction)}
                  className="flex-1 px-4 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-xl transition-colors"
                >
                  تأكيد
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// Preset action sets for common use cases
export const presetActions = {
  crud: [
    {
      id: 'edit',
      label: 'Edit',
      labelAr: 'تعديل',
      icon: Edit2,
      variant: 'default' as const,
    },
    {
      id: 'archive',
      label: 'Archive',
      labelAr: 'أرشفة',
      icon: Archive,
      variant: 'default' as const,
    },
    {
      id: 'delete',
      label: 'Delete',
      labelAr: 'حذف',
      icon: Trash2,
      variant: 'danger' as const,
      requireConfirmation: true,
      confirmMessageAr: 'هل أنت متأكد من حذف العناصر المحددة؟',
    },
  ],
  export: [
    {
      id: 'export-csv',
      label: 'Export CSV',
      labelAr: 'تصدير CSV',
      icon: Download,
      variant: 'default' as const,
    },
    {
      id: 'export-pdf',
      label: 'Export PDF',
      labelAr: 'تصدير PDF',
      icon: Download,
      variant: 'default' as const,
    },
    {
      id: 'export-excel',
      label: 'Export Excel',
      labelAr: 'تصدير Excel',
      icon: Download,
      variant: 'default' as const,
    },
  ],
  communication: [
    {
      id: 'send-notification',
      label: 'Send Notification',
      labelAr: 'إرسال إشعار',
      icon: Send,
      variant: 'primary' as const,
    },
    {
      id: 'send-email',
      label: 'Send Email',
      labelAr: 'إرسال بريد',
      icon: Send,
      variant: 'default' as const,
    },
  ],
};
