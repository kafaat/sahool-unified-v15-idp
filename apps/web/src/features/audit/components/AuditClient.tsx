'use client';

import React, { useState, useMemo, useEffect } from 'react';
import {
  Search,
  Shield,
  User,
  FileText,
  Download,
  AlertTriangle,
  Settings,
  LogIn,
  Trash2,
  Edit,
  Plus,
  Clock,
  Loader2,
} from 'lucide-react';
import { useAuditLogs, useAuditStats } from '@/features/audit';
import type { AuditLog, AuditFilters } from '@/features/audit';

type AuditAction = 'create' | 'update' | 'delete' | 'login' | 'logout' | 'export' | 'config_change';
type AuditSeverity = 'info' | 'warning' | 'critical';

const actionIcons: Record<AuditAction, React.ReactNode> = {
  create: <Plus className="w-4 h-4" />,
  update: <Edit className="w-4 h-4" />,
  delete: <Trash2 className="w-4 h-4" />,
  login: <LogIn className="w-4 h-4" />,
  logout: <LogIn className="w-4 h-4" />,
  export: <Download className="w-4 h-4" />,
  config_change: <Settings className="w-4 h-4" />,
};

const actionLabels: Record<AuditAction, string> = {
  create: 'إنشاء',
  update: 'تحديث',
  delete: 'حذف',
  login: 'دخول',
  logout: 'خروج',
  export: 'تصدير',
  config_change: 'تغيير إعدادات',
};

// Cap rows rendered at once to keep the DOM bounded. Full export lives behind
// the (currently disabled) export button. The backend already paginates the
// query, but we still enforce a client-side guard for safety.
const MAX_VISIBLE_ROWS = 100;

export default function AuditClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState<AuditSeverity | 'all'>('all');
  const [actionFilter, setActionFilter] = useState<AuditAction | 'all'>('all');
  const [page, setPage] = useState(0);

  const filters: AuditFilters = useMemo(() => {
    const f: AuditFilters = {};
    if (actionFilter !== 'all') f.action = actionFilter;
    if (searchTerm) f.search = searchTerm;
    return f;
  }, [actionFilter, searchTerm]);

  const { data: auditLogs, isLoading: logsLoading, error: logsError } = useAuditLogs(filters);
  const { data: auditStats, isLoading: statsLoading } = useAuditStats();

  const filteredLogs = useMemo(() => {
    if (!auditLogs) return [];
    return auditLogs.filter((entry: AuditLog) => {
      const matchesSearch =
        !searchTerm ||
        (entry.detailsAr ?? '').includes(searchTerm) ||
        (entry.userNameAr ?? entry.userName ?? '').includes(searchTerm) ||
        (entry.details ?? '').toLowerCase().includes(searchTerm.toLowerCase());
      // severityFilter is client-side only since AuditLog doesn't have severity from API
      const matchesAction = actionFilter === 'all' || entry.action === actionFilter;
      return matchesSearch && matchesAction;
    });
  }, [auditLogs, searchTerm, actionFilter]);

  // Reset to first page whenever the filter scope changes.
  useEffect(() => {
    setPage(0);
  }, [searchTerm, actionFilter, severityFilter]);

  const totalPages = Math.max(1, Math.ceil(filteredLogs.length / MAX_VISIBLE_ROWS));
  const safePage = Math.min(page, totalPages - 1);
  const pagedLogs = useMemo(
    () =>
      filteredLogs.slice(
        safePage * MAX_VISIBLE_ROWS,
        safePage * MAX_VISIBLE_ROWS + MAX_VISIBLE_ROWS
      ),
    [filteredLogs, safePage]
  );

  const getActionColor = (action: AuditAction) => {
    const colors: Record<AuditAction, string> = {
      create: 'bg-green-100 text-green-600',
      update: 'bg-blue-100 text-blue-600',
      delete: 'bg-red-100 text-red-600',
      login: 'bg-indigo-100 text-indigo-600',
      logout: 'bg-gray-100 text-gray-600',
      export: 'bg-purple-100 text-purple-600',
      config_change: 'bg-orange-100 text-orange-600',
    };
    return colors[action];
  };

  const totalLogs = auditStats?.totalLogs ?? auditLogs?.length ?? 0;
  const todayLogs = auditStats?.todayLogs ?? 0;
  const topUsersCount = auditStats?.topUsers?.length ?? (auditLogs ? new Set(auditLogs.map((e: AuditLog) => e.userId)).size : 0);
  const deleteCount = auditStats?.byAction?.['delete'] ?? 0;

  if (logsError) {
    return (
      <div className="space-y-6" dir="rtl">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
          <p className="text-red-700 font-medium">فشل في تحميل سجل التدقيق</p>
          <p className="text-red-500 text-sm mt-1">Failed to load audit logs</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">سجل التدقيق</h1>
          <p className="text-gray-500 mt-1">Audit Log</p>
        </div>
        <button
          disabled
          title="قريبا - Coming soon"
          className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          تصدير السجل
        </button>
      </div>

      {/* Critical alert */}
      {deleteCount > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="font-medium text-red-800">
              {deleteCount} إجراء حذف يتطلب مراجعة خلال الـ 24 ساعة الماضية
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي السجلات</div>
              <div className="text-xl font-bold text-gray-900">{statsLoading ? '...' : totalLogs}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <User className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">مستخدمون نشطون</div>
              <div className="text-xl font-bold text-green-600">
                {statsLoading ? '...' : topUsersCount}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">سجلات اليوم</div>
              <div className="text-xl font-bold text-red-600">{statsLoading ? '...' : todayLogs}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">آخر نشاط</div>
              <div className="text-sm font-bold text-purple-600">
                {auditLogs && auditLogs.length > 0
                  ? new Date(auditLogs[0]!.timestamp).toLocaleTimeString('ar-SA')
                  : '-'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث في سجل التدقيق..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value as AuditSeverity | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
        >
          <option value="all">جميع المستويات</option>
          <option value="info">معلومات</option>
          <option value="warning">تحذير</option>
          <option value="critical">حرج</option>
        </select>
        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value as AuditAction | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
        >
          <option value="all">جميع الإجراءات</option>
          <option value="create">إنشاء</option>
          <option value="update">تحديث</option>
          <option value="delete">حذف</option>
          <option value="login">دخول</option>
          <option value="export">تصدير</option>
          <option value="config_change">تغيير إعدادات</option>
        </select>
      </div>

      {/* Audit Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        {logsLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-green-600" />
            <span className="mr-2 text-gray-500">جاري التحميل...</span>
          </div>
        )}
        {!logsLoading && filteredLogs.length === 0 && (
          <div className="p-10 text-center text-gray-500">لا توجد سجلات تدقيق</div>
        )}
        {!logsLoading && filteredLogs.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">الوقت</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">المستخدم</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">الإجراء</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">المورد</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">الوصف</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">IP</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {pagedLogs.map((entry: AuditLog) => {
                  const action = (entry.action ?? 'update') as AuditAction;
                  return (
                    <tr key={entry.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                        {new Date(entry.timestamp).toLocaleString('ar-SA', {
                          hour: '2-digit',
                          minute: '2-digit',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </td>
                      <td className="px-4 py-3 font-medium text-gray-900">{entry.userNameAr || entry.userName}</td>
                      <td className="px-4 py-3">
                        <div className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${getActionColor(action)}`}>
                          {actionIcons[action]}
                          {entry.actionAr || actionLabels[action] || entry.action}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-gray-700">{entry.resource}</td>
                      <td className="px-4 py-3 text-gray-600 max-w-xs truncate">{entry.detailsAr || entry.details}</td>
                      <td className="px-4 py-3 text-gray-400 font-mono text-xs">{entry.ipAddress ?? '-'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t bg-gray-50">
                <div className="text-xs text-gray-500">
                  عرض {safePage * MAX_VISIBLE_ROWS + 1}
                  {' - '}
                  {Math.min((safePage + 1) * MAX_VISIBLE_ROWS, filteredLogs.length)}
                  {' من '}
                  {filteredLogs.length}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setPage((p) => Math.max(0, p - 1))}
                    disabled={safePage === 0}
                    className="px-3 py-1 border rounded text-xs disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    السابق
                  </button>
                  <span className="text-xs text-gray-600">
                    {safePage + 1} / {totalPages}
                  </span>
                  <button
                    type="button"
                    onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                    disabled={safePage >= totalPages - 1}
                    className="px-3 py-1 border rounded text-xs disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    التالي
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
