'use client';

// Alerts Panel Component
// لوحة التنبيهات

import { useState, useEffect } from 'react';
import { AlertTriangle, Bell, X, Eye, CheckCircle } from 'lucide-react';
import AlertBadge from '@/components/ui/AlertBadge';
import { formatDate } from '@/lib/utils';
import Link from 'next/link';

export interface Alert {
  id: string;
  type: 'disease' | 'weather' | 'sensor' | 'irrigation' | 'pest' | 'general';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  farmId?: string;
  farmName?: string;
  timestamp: string;
  read: boolean;
  actionUrl?: string;
}

interface AlertsPanelProps {
  alerts: Alert[];
  maxItems?: number;
  showFilters?: boolean;
  onMarkAsRead?: (alertId: string) => void;
  onDismiss?: (alertId: string) => void;
  className?: string;
}

export default function AlertsPanel({
  alerts,
  maxItems = 10,
  showFilters = true,
  onMarkAsRead,
  onDismiss,
  className = ''
}: AlertsPanelProps) {
  const [filter, setFilter] = useState<'all' | 'critical' | 'unread'>('all');
  const [filteredAlerts, setFilteredAlerts] = useState<Alert[]>(alerts);

  useEffect(() => {
    let filtered = [...alerts];

    if (filter === 'critical') {
      filtered = filtered.filter(a => a.severity === 'critical');
    } else if (filter === 'unread') {
      filtered = filtered.filter(a => !a.read);
    }

    setFilteredAlerts(filtered.slice(0, maxItems));
  }, [alerts, filter, maxItems]);

  const getAlertIcon = (type: string) => {
    return AlertTriangle;
  };

  const getAlertTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      disease: 'مرض',
      weather: 'طقس',
      sensor: 'مستشعر',
      irrigation: 'ري',
      pest: 'آفة',
      general: 'عام'
    };
    return labels[type] || type;
  };

  const unreadCount = alerts.filter(a => !a.read).length;
  const criticalCount = alerts.filter(a => a.severity === 'critical').length;

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-100 ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-sahool-600" />
            <h2 className="font-bold text-gray-900">التنبيهات</h2>
            {unreadCount > 0 && (
              <span className="px-2 py-0.5 bg-red-500 text-white text-xs font-semibold rounded-full">
                {unreadCount}
              </span>
            )}
          </div>
          {showFilters && (
            <div className="flex items-center gap-2" role="group" aria-label="فلترة التنبيهات">
              <button
                onClick={() => setFilter('all')}
                aria-pressed={filter === 'all'}
                className={`px-3 py-1 text-xs font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-sahool-500 ${
                  filter === 'all'
                    ? 'bg-sahool-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                الكل ({alerts.length})
              </button>
              <button
                onClick={() => setFilter('critical')}
                aria-pressed={filter === 'critical'}
                className={`px-3 py-1 text-xs font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 ${
                  filter === 'critical'
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                حرجة ({criticalCount})
              </button>
              <button
                onClick={() => setFilter('unread')}
                aria-pressed={filter === 'unread'}
                className={`px-3 py-1 text-xs font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  filter === 'unread'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                غير مقروءة ({unreadCount})
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Alerts List */}
      <div className="divide-y divide-gray-100 max-h-[600px] overflow-y-auto">
        {filteredAlerts.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Bell className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>لا توجد تنبيهات</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const Icon = getAlertIcon(alert.type);
            return (
              <div
                key={alert.id}
                className={`p-4 hover:bg-gray-50 transition-colors ${!alert.read ? 'bg-blue-50/50' : ''}`}
              >
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${
                    alert.severity === 'critical'
                      ? 'bg-red-100'
                      : alert.severity === 'high'
                      ? 'bg-orange-100'
                      : alert.severity === 'medium'
                      ? 'bg-yellow-100'
                      : 'bg-blue-100'
                  }`}>
                    <Icon className={`w-5 h-5 ${
                      alert.severity === 'critical'
                        ? 'text-red-600'
                        : alert.severity === 'high'
                        ? 'text-orange-600'
                        : alert.severity === 'medium'
                        ? 'text-yellow-600'
                        : 'text-blue-600'
                    }`} />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{alert.titleAr}</h3>
                        {alert.farmName && (
                          <p className="text-xs text-gray-500 mt-0.5">{alert.farmName}</p>
                        )}
                      </div>
                      <div className="flex items-center gap-1 flex-shrink-0">
                        <AlertBadge severity={alert.severity} />
                        {!alert.read && (
                          <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                        )}
                      </div>
                    </div>

                    <p className="text-sm text-gray-600 mb-2">{alert.messageAr}</p>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span>{getAlertTypeLabel(alert.type)}</span>
                        <span>•</span>
                        <span>{formatDate(alert.timestamp)}</span>
                      </div>

                      <div className="flex items-center gap-2">
                        {alert.actionUrl && (
                          <Link
                            href={alert.actionUrl}
                            className="text-xs text-sahool-600 hover:text-sahool-700 font-medium flex items-center gap-1"
                          >
                            <Eye className="w-3 h-3" />
                            عرض
                          </Link>
                        )}
                        {onMarkAsRead && !alert.read && (
                          <button
                            onClick={() => onMarkAsRead(alert.id)}
                            className="text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
                            aria-label="وضع علامة كمقروء"
                            title="وضع علامة كمقروء"
                          >
                            <CheckCircle className="w-3 h-3" aria-hidden="true" />
                          </button>
                        )}
                        {onDismiss && (
                          <button
                            onClick={() => onDismiss(alert.id)}
                            className="text-xs text-gray-400 hover:text-gray-600"
                            aria-label="إخفاء التنبيه"
                            title="إخفاء"
                          >
                            <X className="w-3 h-3" aria-hidden="true" />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      {filteredAlerts.length > 0 && filteredAlerts.length < alerts.length && (
        <div className="p-3 border-t border-gray-100 text-center">
          <Link
            href="/alerts"
            className="text-sm text-sahool-600 hover:text-sahool-700 font-medium"
          >
            عرض جميع التنبيهات ({alerts.length}) ←
          </Link>
        </div>
      )}
    </div>
  );
}
