'use client';

/**
 * SAHOOL Field Alerts Panel Component
 * مكون لوحة تنبيهات الحقل
 *
 * Displays field alerts with real-time updates, filtering, and action buttons
 * يعرض تنبيهات الحقل مع التحديثات الفورية والفلترة وأزرار الإجراءات
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  AlertTriangle,
  Cloud,
  Droplet,
  TrendingDown,
  Clock,
  X,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  ListTodo,
  Eye,
  Filter,
  Bell,
  BellOff,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Modal } from '@/components/ui/modal';
import { TaskForm } from '@/features/tasks/components/TaskForm';
import { useWebSocket } from '@/hooks/useWebSocket';
import type { TaskFormData } from '@/features/tasks/types';

// ═══════════════════════════════════════════════════════════════════════════
// Types & Interfaces
// ═══════════════════════════════════════════════════════════════════════════

export type AlertType = 'ndvi_drop' | 'weather_warning' | 'soil_moisture' | 'task_overdue';
export type AlertSeverity = 'critical' | 'warning' | 'info';

export interface FieldAlert {
  id: string;
  fieldId: string;
  type: AlertType;
  severity: AlertSeverity;
  title: string;
  message: string;
  data: Record<string, any>;
  createdAt: Date;
  acknowledged: boolean;
}

interface AlertsPanelProps {
  fieldId: string;
  alerts?: FieldAlert[];
  onDismiss?: (alertId: string) => void | Promise<void>;
  onCreateTask?: (data: TaskFormData) => void | Promise<void>;
  onViewDetails?: (alert: FieldAlert) => void;
  enableWebSocket?: boolean;
  wsUrl?: string;
  pollingInterval?: number;
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Constants & Helpers
// ═══════════════════════════════════════════════════════════════════════════

const ALERT_TYPE_CONFIG: Record<AlertType, {
  icon: typeof AlertTriangle;
  label: string;
  labelAr: string;
  color: string;
}> = {
  ndvi_drop: {
    icon: TrendingDown,
    label: 'NDVI Drop',
    labelAr: 'انخفاض NDVI',
    color: 'text-orange-600',
  },
  weather_warning: {
    icon: Cloud,
    label: 'Weather Warning',
    labelAr: 'تحذير جوي',
    color: 'text-blue-600',
  },
  soil_moisture: {
    icon: Droplet,
    label: 'Soil Moisture',
    labelAr: 'رطوبة التربة',
    color: 'text-cyan-600',
  },
  task_overdue: {
    icon: Clock,
    label: 'Task Overdue',
    labelAr: 'مهمة متأخرة',
    color: 'text-red-600',
  },
};

const SEVERITY_CONFIG: Record<AlertSeverity, {
  variant: 'danger' | 'warning' | 'info';
  label: string;
  labelAr: string;
}> = {
  critical: {
    variant: 'danger',
    label: 'Critical',
    labelAr: 'حرج',
  },
  warning: {
    variant: 'warning',
    label: 'Warning',
    labelAr: 'تحذير',
  },
  info: {
    variant: 'info',
    label: 'Info',
    labelAr: 'معلومة',
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Alert Item Component
// ═══════════════════════════════════════════════════════════════════════════

interface AlertItemProps {
  alert: FieldAlert;
  isExpanded: boolean;
  onToggle: () => void;
  onDismiss: () => void;
  onCreateTask: () => void;
  onViewDetails: () => void;
  isDismissing: boolean;
}

const AlertItem: React.FC<AlertItemProps> = ({
  alert,
  isExpanded,
  onToggle,
  onDismiss,
  onCreateTask,
  onViewDetails,
  isDismissing,
}) => {
  const typeConfig = ALERT_TYPE_CONFIG[alert.type];
  const severityConfig = SEVERITY_CONFIG[alert.severity];
  const Icon = typeConfig.icon;

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('ar-EG', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <Card
      variant="bordered"
      padding="none"
      className={`transition-all ${alert.acknowledged ? 'opacity-60' : ''}`}
    >
      {/* Alert Header */}
      <div
        className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div className={`p-2 rounded-lg bg-gray-100 ${typeConfig.color}`}>
            <Icon className="w-5 h-5" />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-1">
              <h4 className="font-semibold text-gray-900 leading-tight">
                {alert.title}
              </h4>
              <Badge variant={severityConfig.variant} size="sm">
                {severityConfig.labelAr}
              </Badge>
            </div>

            <p className="text-sm text-gray-600 mb-2 line-clamp-2">
              {alert.message}
            </p>

            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span>{typeConfig.labelAr}</span>
              <span>•</span>
              <span>{formatDate(alert.createdAt)}</span>
              {alert.acknowledged && (
                <>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    تم الاطلاع
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Expand Toggle */}
          <button
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              onToggle();
            }}
          >
            {isExpanded ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>
        </div>
      </div>

      {/* Alert Details (Expanded) */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50">
          {/* Alert Data */}
          {Object.keys(alert.data).length > 0 && (
            <div className="p-4 border-b border-gray-200 bg-white">
              <h5 className="font-medium text-gray-900 mb-3 text-sm">
                تفاصيل التنبيه
              </h5>
              <div className="space-y-2">
                {Object.entries(alert.data).map(([key, value]) => (
                  <div
                    key={key}
                    className="flex items-start justify-between gap-2 text-sm"
                  >
                    <span className="text-gray-600 capitalize">
                      {key.replace(/_/g, ' ')}:
                    </span>
                    <span className="font-medium text-gray-900 text-left">
                      {typeof value === 'object'
                        ? JSON.stringify(value)
                        : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="p-4 flex items-center justify-end gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={onViewDetails}
              className="gap-2"
            >
              <Eye className="w-4 h-4" />
              <span>التفاصيل</span>
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={onCreateTask}
              className="gap-2"
            >
              <ListTodo className="w-4 h-4" />
              <span>إنشاء مهمة</span>
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={onDismiss}
              disabled={isDismissing || alert.acknowledged}
              className="gap-2 text-gray-600 hover:text-red-600"
            >
              <X className="w-4 h-4" />
              <span>{isDismissing ? 'جاري الإغلاق...' : 'إغلاق'}</span>
            </Button>
          </div>
        </div>
      )}
    </Card>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Main Component
// ═══════════════════════════════════════════════════════════════════════════

export const AlertsPanel: React.FC<AlertsPanelProps> = ({
  fieldId,
  alerts: initialAlerts = [],
  onDismiss,
  onCreateTask,
  onViewDetails,
  enableWebSocket = false,
  wsUrl,
  pollingInterval = 30000, // 30 seconds default
  className = '',
}) => {
  // State
  const [alerts, setAlerts] = useState<FieldAlert[]>(initialAlerts);
  const [expandedAlertId, setExpandedAlertId] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<AlertType | 'all'>('all');
  const [showAcknowledged, setShowAcknowledged] = useState(false);
  const [dismissingAlertId, setDismissingAlertId] = useState<string | null>(null);
  const [taskModalOpen, setTaskModalOpen] = useState(false);
  const [selectedAlertForTask, setSelectedAlertForTask] = useState<FieldAlert | null>(null);
  const [isSubmittingTask, setIsSubmittingTask] = useState(false);

  // Update alerts when initialAlerts prop changes
  useEffect(() => {
    setAlerts(initialAlerts);
  }, [initialAlerts]);

  // WebSocket for real-time updates
  const handleWebSocketMessage = useCallback((message: any) => {
    if (message.type === 'field_alert' && message.fieldId === fieldId) {
      const newAlert: FieldAlert = {
        ...message.data,
        createdAt: new Date(message.data.createdAt),
      };
      setAlerts((prev) => [newAlert, ...prev]);
    } else if (message.type === 'alert_dismissed' && message.fieldId === fieldId) {
      setAlerts((prev) =>
        prev.map((alert) =>
          alert.id === message.alertId
            ? { ...alert, acknowledged: true }
            : alert
        )
      );
    }
  }, [fieldId]);

  useWebSocket({
    url: wsUrl || '',
    onMessage: handleWebSocketMessage,
    enabled: enableWebSocket && !!wsUrl,
  });

  // Polling for updates (fallback when WebSocket is disabled)
  useEffect(() => {
    if (enableWebSocket || !pollingInterval) return;

    const interval = setInterval(() => {
      // Fetch fresh alerts here
      // This would typically call an API endpoint to get updated alerts
      // For now, we'll just use the initial alerts
      console.log('Polling for alerts...');
    }, pollingInterval);

    return () => clearInterval(interval);
  }, [enableWebSocket, pollingInterval]);

  // Handlers
  const handleDismiss = useCallback(
    async (alertId: string) => {
      setDismissingAlertId(alertId);
      try {
        await onDismiss?.(alertId);
        setAlerts((prev) =>
          prev.map((alert) =>
            alert.id === alertId ? { ...alert, acknowledged: true } : alert
          )
        );
      } catch (error) {
        console.error('Failed to dismiss alert:', error);
      } finally {
        setDismissingAlertId(null);
      }
    },
    [onDismiss]
  );

  const handleCreateTask = useCallback((alert: FieldAlert) => {
    setSelectedAlertForTask(alert);
    setTaskModalOpen(true);
  }, []);

  const handleTaskSubmit = useCallback(
    async (data: TaskFormData) => {
      setIsSubmittingTask(true);
      try {
        await onCreateTask?.(data);
        setTaskModalOpen(false);
        setSelectedAlertForTask(null);
        // Optionally dismiss the alert after creating a task
        if (selectedAlertForTask) {
          await handleDismiss(selectedAlertForTask.id);
        }
      } catch (error) {
        console.error('Failed to create task:', error);
      } finally {
        setIsSubmittingTask(false);
      }
    },
    [onCreateTask, selectedAlertForTask, handleDismiss]
  );

  const handleViewDetails = useCallback(
    (alert: FieldAlert) => {
      onViewDetails?.(alert);
    },
    [onViewDetails]
  );

  // Pre-fill task form data from alert
  const getTaskFormDataFromAlert = useCallback(
    (alert: FieldAlert): Partial<TaskFormData> => {
      const priorityMap: Record<AlertSeverity, 'low' | 'medium' | 'high'> = {
        critical: 'high',
        warning: 'medium',
        info: 'low',
      };

      return {
        title: alert.title,
        title_ar: alert.title,
        description: alert.message,
        description_ar: alert.message,
        field_id: alert.fieldId,
        priority: priorityMap[alert.severity],
        status: 'open',
        due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0], // 7 days from now
      };
    },
    []
  );

  // Filtered alerts
  const filteredAlerts = useMemo(() => {
    return alerts.filter((alert) => {
      if (filterType !== 'all' && alert.type !== filterType) return false;
      if (!showAcknowledged && alert.acknowledged) return false;
      return true;
    });
  }, [alerts, filterType, showAcknowledged]);

  // Statistics
  const stats = useMemo(() => {
    return {
      total: alerts.length,
      active: alerts.filter((a) => !a.acknowledged).length,
      critical: alerts.filter((a) => a.severity === 'critical' && !a.acknowledged).length,
      byType: {
        ndvi_drop: alerts.filter((a) => a.type === 'ndvi_drop' && !a.acknowledged).length,
        weather_warning: alerts.filter((a) => a.type === 'weather_warning' && !a.acknowledged).length,
        soil_moisture: alerts.filter((a) => a.type === 'soil_moisture' && !a.acknowledged).length,
        task_overdue: alerts.filter((a) => a.type === 'task_overdue' && !a.acknowledged).length,
      },
    };
  }, [alerts]);

  // ═════════════════════════════════════════════════════════════════════════
  // Render
  // ═════════════════════════════════════════════════════════════════════════

  return (
    <>
      <div className={`space-y-4 ${className}`}>
        {/* Header */}
        <Card variant="elevated" padding="md">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-red-100 rounded-lg">
                  <Bell className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <CardTitle>تنبيهات الحقل</CardTitle>
                  <p className="text-sm text-gray-600 mt-1">
                    {stats.active > 0
                      ? `${stats.active} تنبيه نشط`
                      : 'لا توجد تنبيهات نشطة'}
                    {stats.critical > 0 && (
                      <span className="text-red-600 font-semibold mr-2">
                        ({stats.critical} حرج)
                      </span>
                    )}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Badge variant={stats.active > 0 ? 'danger' : 'success'} size="lg">
                  {stats.total} إجمالي
                </Badge>
              </div>
            </div>
          </CardHeader>

          {/* Filter Controls */}
          <CardContent>
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">تصفية:</span>
              </div>

              <button
                onClick={() => setFilterType('all')}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  filterType === 'all'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                الكل ({stats.total})
              </button>

              {(Object.keys(ALERT_TYPE_CONFIG) as AlertType[]).map((type) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    filterType === type
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {ALERT_TYPE_CONFIG[type].labelAr} ({stats.byType[type]})
                </button>
              ))}

              <div className="mr-auto">
                <button
                  onClick={() => setShowAcknowledged(!showAcknowledged)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    showAcknowledged
                      ? 'bg-gray-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {showAcknowledged ? (
                    <Bell className="w-4 h-4" />
                  ) : (
                    <BellOff className="w-4 h-4" />
                  )}
                  {showAcknowledged ? 'إخفاء المغلقة' : 'إظهار المغلقة'}
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Alerts List */}
        <div className="space-y-3">
          {filteredAlerts.length > 0 ? (
            filteredAlerts.map((alert) => (
              <AlertItem
                key={alert.id}
                alert={alert}
                isExpanded={expandedAlertId === alert.id}
                onToggle={() =>
                  setExpandedAlertId(
                    expandedAlertId === alert.id ? null : alert.id
                  )
                }
                onDismiss={() => handleDismiss(alert.id)}
                onCreateTask={() => handleCreateTask(alert)}
                onViewDetails={() => handleViewDetails(alert)}
                isDismissing={dismissingAlertId === alert.id}
              />
            ))
          ) : (
            // Empty State
            <Card variant="bordered" padding="lg">
              <div className="text-center py-12">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 mb-4">
                  <CheckCircle2 className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {filterType === 'all'
                    ? 'لا توجد تنبيهات'
                    : `لا توجد تنبيهات من نوع "${ALERT_TYPE_CONFIG[filterType as AlertType]?.labelAr}"`}
                </h3>
                <p className="text-gray-600">
                  {showAcknowledged
                    ? 'جميع التنبيهات تم الاطلاع عليها'
                    : 'حقلك في حالة جيدة'}
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* Task Creation Modal */}
      <Modal
        isOpen={taskModalOpen}
        onClose={() => {
          setTaskModalOpen(false);
          setSelectedAlertForTask(null);
        }}
        titleAr="إنشاء مهمة من التنبيه"
        title="Create Task from Alert"
        size="lg"
      >
        {selectedAlertForTask && (
          <TaskForm
            task={getTaskFormDataFromAlert(selectedAlertForTask) as any}
            onSubmit={handleTaskSubmit}
            onCancel={() => {
              setTaskModalOpen(false);
              setSelectedAlertForTask(null);
            }}
            isSubmitting={isSubmittingTask}
          />
        )}
      </Modal>
    </>
  );
};

export default AlertsPanel;
