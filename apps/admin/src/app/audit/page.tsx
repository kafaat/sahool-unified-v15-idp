'use client';

/**
 * Audit Trail Page — سجل التدقيق
 * Displays audit logs with filters, stats, and CSV export
 */

import { useEffect, useState, useCallback } from 'react';
import { useToast } from '@/components/ui/Toast';
import Header from '@/components/layout/Header';
import DataTable from '@/components/ui/DataTable';
import { formatDate } from '@/lib/utils';
import { FileText, ClipboardList, AlertTriangle, Users, Search, Download, RefreshCw } from 'lucide-react';
import { logger } from '@/lib/logger';
import { auditService, downloadCSV, type AuditLog, type AuditStats } from '@/lib/api';

export default function AuditPage() {
  const { toast } = useToast();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [stats, setStats] = useState<AuditStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [resourceFilter, setResourceFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [logsRes, statsRes] = await Promise.all([
        auditService.getAll({
          page,
          limit: 20,
          search: searchQuery || undefined,
          action: actionFilter || undefined,
          resource_type: resourceFilter || undefined,
          status: statusFilter || undefined,
        }),
        auditService.getStats(),
      ]);
      setLogs(logsRes.data);
      setTotalPages(logsRes.meta.totalPages);
      setStats(statsRes);
    } catch (error) {
      logger.error('Failed to load audit data:', error);
      toast.error('خطأ في التحميل', 'فشل تحميل سجلات التدقيق');
    } finally {
      setIsLoading(false);
    }
  }, [page, searchQuery, actionFilter, resourceFilter, statusFilter, toast]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleExport = () => {
    downloadCSV(
      logs.map(({ id, timestamp, user_email, action, resource_type, resource_id, status, ip_address }) => ({
        id, timestamp, user_email, action, resource_type, resource_id, status, ip_address,
      })),
      'audit-logs'
    );
  };

  const columns = [
    { key: 'timestamp', header: 'التاريخ', render: (item: AuditLog) => formatDate(item.timestamp) },
    { key: 'user_email', header: 'المستخدم' },
    { key: 'action', header: 'الإجراء' },
    { key: 'resource_type', header: 'نوع المورد' },
    {
      key: 'status',
      header: 'الحالة',
      render: (item: AuditLog) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          item.status === 'success'
            ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
            : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
        }`}>
          {item.status === 'success' ? 'نجاح' : 'فشل'}
        </span>
      ),
    },
    { key: 'ip_address', header: 'عنوان IP' },
  ];

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <Header title="سجل التدقيق" subtitle="Audit Trail" />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats?.total_logs?.toLocaleString() ?? '—'}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي الأحداث</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <ClipboardList className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats?.actions_today?.toLocaleString() ?? '—'}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">أحداث اليوم</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats?.unique_users ?? '—'}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">مستخدمون نشطون</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats ? `${(stats.failure_rate * 100).toFixed(1)}%` : '—'}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">نسبة الفشل</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 mb-4">
        <div className="flex flex-wrap gap-3 items-center">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="بحث..."
              value={searchQuery}
              onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
              className="w-full pr-10 pl-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm"
            />
          </div>
          <select value={actionFilter} onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
            className="border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm">
            <option value="">كل الإجراءات</option>
            <option value="create">إنشاء</option>
            <option value="update">تعديل</option>
            <option value="delete">حذف</option>
            <option value="login">تسجيل دخول</option>
          </select>
          <select value={resourceFilter} onChange={(e) => { setResourceFilter(e.target.value); setPage(1); }}
            className="border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm">
            <option value="">كل الموارد</option>
            <option value="field">حقول</option>
            <option value="user">مستخدمون</option>
            <option value="sensor">مستشعرات</option>
            <option value="task">مهام</option>
          </select>
          <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm">
            <option value="">كل الحالات</option>
            <option value="success">نجاح</option>
            <option value="failure">فشل</option>
          </select>
          <button onClick={loadData} className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300" title="تحديث">
            <RefreshCw className="w-4 h-4" />
          </button>
          <button onClick={handleExport} disabled={logs.length === 0}
            className="flex items-center gap-1 px-3 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50">
            <Download className="w-4 h-4" /> تصدير CSV
          </button>
        </div>
      </div>

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={logs}
        keyExtractor={(item) => item.id}
        isLoading={isLoading}
        emptyMessage="لا توجد سجلات تدقيق"
      />

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-2 mt-4">
          <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}
            className="px-3 py-1 rounded border border-gray-300 dark:border-gray-600 text-sm disabled:opacity-50 dark:text-gray-100">السابق</button>
          <span className="px-3 py-1 text-sm text-gray-700 dark:text-gray-300">{page} / {totalPages}</span>
          <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}
            className="px-3 py-1 rounded border border-gray-300 dark:border-gray-600 text-sm disabled:opacity-50 dark:text-gray-100">التالي</button>
        </div>
      )}
    </div>
  );
}
