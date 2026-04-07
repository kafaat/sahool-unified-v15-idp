'use client';

/**
 * Terrain Analysis Page — تحليل التضاريس
 * Displays terrain analyses with filters and CSV export
 */

import { useEffect, useState, useCallback } from 'react';
import { useToast } from '@/components/ui/Toast';
import Header from '@/components/layout/Header';
import DataTable from '@/components/ui/DataTable';
import { formatDate } from '@/lib/utils';
import { Mountain, CheckCircle, Clock, AlertTriangle, Search, Download, RefreshCw } from 'lucide-react';
import { logger } from '@/lib/logger';
import { terrainService, downloadCSV, type TerrainAnalysis } from '@/lib/api';

export default function TerrainPage() {
  const { toast } = useToast();
  const [analyses, setAnalyses] = useState<TerrainAnalysis[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await terrainService.getAnalyses({
        page,
        limit: 20,
        search: searchQuery || undefined,
        analysis_type: typeFilter || undefined,
      });
      setAnalyses(res.data);
      setTotalPages(res.meta.totalPages);
    } catch (error) {
      logger.error('Failed to load terrain analyses:', error);
      toast.error('خطأ في التحميل', 'فشل تحميل تحليلات التضاريس');
    } finally {
      setIsLoading(false);
    }
  }, [page, searchQuery, typeFilter, statusFilter, toast]);

  useEffect(() => { loadData(); }, [loadData]);

  const completed = analyses.filter((a) => a.status === 'completed').length;
  const processing = analyses.filter((a) => a.status === 'processing').length;
  const failed = analyses.filter((a) => a.status === 'failed').length;

  const handleExport = () => {
    downloadCSV(
      analyses.map(({ id, field_id, analysis_type, status, created_at }) => ({
        id, field_id, analysis_type, status, created_at,
      })),
      'terrain-analyses'
    );
  };

  const statusBadge = (status: string) => {
    const colors: Record<string, string> = {
      completed: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
      processing: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
      failed: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
    };
    const labels: Record<string, string> = { completed: 'مكتمل', processing: 'قيد التنفيذ', failed: 'فشل' };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] ?? ''}`}>
        {labels[status] ?? status}
      </span>
    );
  };

  const columns = [
    { key: 'id', header: 'المعرف', render: (item: TerrainAnalysis) => item.id.slice(0, 8) + '...' },
    { key: 'field_id', header: 'معرف الحقل' },
    { key: 'analysis_type', header: 'نوع التحليل', render: (item: TerrainAnalysis) => item.analysis_type.toUpperCase() },
    { key: 'status', header: 'الحالة', render: (item: TerrainAnalysis) => statusBadge(item.status) },
    { key: 'created_at', header: 'التاريخ', render: (item: TerrainAnalysis) => formatDate(item.created_at) },
  ];

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <Header title="تحليل التضاريس" subtitle="Terrain Analysis" />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Mountain className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{analyses.length}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي التحليلات</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{completed}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">مكتملة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{processing}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">قيد التنفيذ</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{failed}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">فشلت</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 mb-4">
        <div className="flex flex-wrap gap-3 items-center">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input type="text" placeholder="بحث بمعرف الحقل..." value={searchQuery}
              onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
              className="w-full pr-10 pl-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm" />
          </div>
          <select value={typeFilter} onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
            className="border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm">
            <option value="">كل الأنواع</option>
            <option value="dem">DEM</option>
            <option value="slope">Slope</option>
            <option value="aspect">Aspect</option>
          </select>
          <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm">
            <option value="">كل الحالات</option>
            <option value="completed">مكتمل</option>
            <option value="processing">قيد التنفيذ</option>
            <option value="failed">فشل</option>
          </select>
          <button onClick={loadData} className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"><RefreshCw className="w-4 h-4" /></button>
          <button onClick={handleExport} disabled={analyses.length === 0}
            className="flex items-center gap-1 px-3 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50">
            <Download className="w-4 h-4" /> تصدير CSV
          </button>
        </div>
      </div>

      <DataTable columns={columns} data={analyses} keyExtractor={(item) => item.id} isLoading={isLoading} emptyMessage="لا توجد تحليلات" />

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
