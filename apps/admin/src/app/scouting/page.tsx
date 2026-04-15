'use client';

/**
 * Field Scouting Page — الاستكشاف الميداني
 * Displays scouting reports with severity, filters, and CSV export
 */

import { useEffect, useState, useCallback } from 'react';
import { useToast } from '@/components/ui/Toast';
import Header from '@/components/layout/Header';
import DataTable from '@/components/ui/DataTable';
import { formatDate } from '@/lib/utils';
import { FileText, Bug, AlertTriangle, Clock, Search, Download, RefreshCw } from 'lucide-react';
import { logger } from '@/lib/logger';
import { scoutingService, downloadCSV, type ScoutingReport } from '@/lib/api';

export default function ScoutingPage() {
  const { toast } = useToast();
  const [reports, setReports] = useState<ScoutingReport[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await scoutingService.getAll({
        page,
        limit: 20,
        search: searchQuery || undefined,
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
      });
      setReports(res.data);
      setTotalPages(res.meta.totalPages);
    } catch (error) {
      logger.error('Failed to load scouting reports:', error);
      toast.error('خطأ في التحميل', 'فشل تحميل تقارير الاستكشاف');
    } finally {
      setIsLoading(false);
    }
  }, [page, searchQuery, severityFilter, statusFilter, toast]);

  useEffect(() => { loadData(); }, [loadData]);

  const pestsFound = reports.filter((r) => r.pest_found).length;
  const highSeverity = reports.filter((r) => r.severity === 'high' || r.severity === 'critical').length;
  const pending = reports.filter((r) => r.status === 'pending').length;

  const handleExport = () => {
    downloadCSV(
      reports.map(({ id, date, scout_name, field_id, pest_found, pest_type, severity, status, notes }) => ({
        id, date, scout_name, field_id, pest_found: pest_found ? 'نعم' : 'لا', pest_type: pest_type ?? '', severity: severity ?? '', status, notes,
      })),
      'scouting-reports'
    );
  };

  const severityBadge = (severity?: string) => {
    if (!severity) return <span className="text-gray-400">—</span>;
    const colors: Record<string, string> = {
      low: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
      medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
      high: 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300',
      critical: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
    };
    const labels: Record<string, string> = { low: 'منخفض', medium: 'متوسط', high: 'عالي', critical: 'حرج' };
    return <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[severity] ?? ''}`}>{labels[severity] ?? severity}</span>;
  };

  const statusBadge = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
      reviewed: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
      resolved: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    };
    const labels: Record<string, string> = { pending: 'قيد المراجعة', reviewed: 'تمت المراجعة', resolved: 'تم الحل' };
    return <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] ?? ''}`}>{labels[status] ?? status}</span>;
  };

  const columns = [
    { key: 'date', header: 'التاريخ', render: (item: ScoutingReport) => formatDate(item.date) },
    { key: 'scout_name', header: 'المستكشف' },
    { key: 'field_id', header: 'الحقل' },
    {
      key: 'pest_found',
      header: 'آفات',
      render: (item: ScoutingReport) => (
        <span className={item.pest_found ? 'text-red-600 font-medium' : 'text-green-600'}>
          {item.pest_found ? 'نعم' : 'لا'}
        </span>
      ),
    },
    { key: 'pest_type', header: 'نوع الآفة', render: (item: ScoutingReport) => item.pest_type ?? '—' },
    { key: 'severity', header: 'الشدة', render: (item: ScoutingReport) => severityBadge(item.severity) },
    { key: 'status', header: 'الحالة', render: (item: ScoutingReport) => statusBadge(item.status) },
  ];

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <Header title="الاستكشاف الميداني" subtitle="Field Scouting" />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center"><FileText className="w-5 h-5 text-blue-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{reports.length}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي التقارير</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center"><Bug className="w-5 h-5 text-red-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{pestsFound}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">آفات مكتشفة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center"><AlertTriangle className="w-5 h-5 text-orange-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{highSeverity}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">شدة عالية</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center"><Clock className="w-5 h-5 text-yellow-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{pending}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">قيد المراجعة</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 mb-4">
        <div className="flex flex-wrap gap-3 items-center">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input type="text" placeholder="بحث..." value={searchQuery}
              onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
              className="w-full pr-10 pl-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm" />
          </div>
          <select value={severityFilter} onChange={(e) => { setSeverityFilter(e.target.value); setPage(1); }}
            className="border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm">
            <option value="">كل الشدّات</option>
            <option value="low">منخفض</option>
            <option value="medium">متوسط</option>
            <option value="high">عالي</option>
            <option value="critical">حرج</option>
          </select>
          <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm">
            <option value="">كل الحالات</option>
            <option value="pending">قيد المراجعة</option>
            <option value="reviewed">تمت المراجعة</option>
            <option value="resolved">تم الحل</option>
          </select>
          <button onClick={loadData} className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"><RefreshCw className="w-4 h-4" /></button>
          <button onClick={handleExport} disabled={reports.length === 0}
            className="flex items-center gap-1 px-3 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50">
            <Download className="w-4 h-4" /> تصدير CSV
          </button>
        </div>
      </div>

      <DataTable columns={columns} data={reports} keyExtractor={(item) => item.id} isLoading={isLoading} emptyMessage="لا توجد تقارير" />

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
