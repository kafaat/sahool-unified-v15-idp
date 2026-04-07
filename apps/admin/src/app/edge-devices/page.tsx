'use client';

/**
 * Edge Devices Page — أجهزة الحافة
 * Displays edge devices with status, metrics, filters, and CSV export
 */

import { useEffect, useState, useCallback } from 'react';
import { useToast } from '@/components/ui/Toast';
import Header from '@/components/layout/Header';
import DataTable from '@/components/ui/DataTable';
import { formatDate } from '@/lib/utils';
import { Server, Wifi, WifiOff, Cpu, Search, Download, RefreshCw } from 'lucide-react';
import { logger } from '@/lib/logger';
import { edgeService, downloadCSV, type EdgeDevice } from '@/lib/api';

export default function EdgeDevicesPage() {
  const { toast } = useToast();
  const [devices, setDevices] = useState<EdgeDevice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await edgeService.getDevices({
        page,
        limit: 20,
        search: searchQuery || undefined,
        status: statusFilter || undefined,
      });
      setDevices(res.data);
      setTotalPages(res.meta.totalPages);
    } catch (error) {
      logger.error('Failed to load edge devices:', error);
      toast.error('خطأ في التحميل', 'فشل تحميل أجهزة الحافة');
    } finally {
      setIsLoading(false);
    }
  }, [page, searchQuery, statusFilter, toast]);

  useEffect(() => { loadData(); }, [loadData]);

  const online = devices.filter((d) => d.status === 'online').length;
  const offline = devices.filter((d) => d.status === 'offline').length;
  const avgCpu = devices.length > 0
    ? (devices.reduce((sum, d) => sum + d.cpu_usage, 0) / devices.length).toFixed(0)
    : '—';

  const handleExport = () => {
    downloadCSV(
      devices.map(({ id, name, device_type, status, ip_address, last_seen, firmware_version, cpu_usage, memory_usage }) => ({
        id, name, device_type, status, ip_address, last_seen, firmware_version, cpu_usage, memory_usage,
      })),
      'edge-devices'
    );
  };

  const statusBadge = (status: string) => {
    const colors: Record<string, string> = {
      online: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
      offline: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
      error: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
    };
    const labels: Record<string, string> = { online: 'متصل', offline: 'غير متصل', error: 'خطأ' };
    return <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] ?? ''}`}>{labels[status] ?? status}</span>;
  };

  const columns = [
    { key: 'name', header: 'الاسم' },
    { key: 'device_type', header: 'النوع' },
    { key: 'status', header: 'الحالة', render: (item: EdgeDevice) => statusBadge(item.status) },
    { key: 'ip_address', header: 'عنوان IP' },
    { key: 'last_seen', header: 'آخر اتصال', render: (item: EdgeDevice) => formatDate(item.last_seen) },
    { key: 'firmware_version', header: 'البرنامج الثابت' },
    { key: 'cpu_usage', header: 'CPU', render: (item: EdgeDevice) => `${item.cpu_usage}%` },
    { key: 'memory_usage', header: 'الذاكرة', render: (item: EdgeDevice) => `${item.memory_usage}%` },
  ];

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <Header title="أجهزة الحافة" subtitle="Edge Devices" />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center"><Server className="w-5 h-5 text-blue-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{devices.length}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي الأجهزة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center"><Wifi className="w-5 h-5 text-green-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{online}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">متصل</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center"><WifiOff className="w-5 h-5 text-red-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{offline}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">غير متصل</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center"><Cpu className="w-5 h-5 text-purple-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{avgCpu}%</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">متوسط CPU</p>
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
          <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm">
            <option value="">كل الحالات</option>
            <option value="online">متصل</option>
            <option value="offline">غير متصل</option>
            <option value="error">خطأ</option>
          </select>
          <button onClick={loadData} className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"><RefreshCw className="w-4 h-4" /></button>
          <button onClick={handleExport} disabled={devices.length === 0}
            className="flex items-center gap-1 px-3 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50">
            <Download className="w-4 h-4" /> تصدير CSV
          </button>
        </div>
      </div>

      <DataTable columns={columns} data={devices} keyExtractor={(item) => item.id} isLoading={isLoading} emptyMessage="لا توجد أجهزة" />

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
