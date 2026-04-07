'use client';

/**
 * Virtual Sensors Page — المستشعرات الافتراضية
 * Displays virtual sensors with stats, filters, and CSV export
 */

import { useEffect, useState, useCallback } from 'react';
import { useToast } from '@/components/ui/Toast';
import Header from '@/components/layout/Header';
import DataTable from '@/components/ui/DataTable';
import { formatDate } from '@/lib/utils';
import { Radio, Activity, AlertTriangle, Target, Search, Download, RefreshCw } from 'lucide-react';
import { logger } from '@/lib/logger';
import { virtualSensorService, downloadCSV, type VirtualSensor } from '@/lib/api';

export default function VirtualSensorsPage() {
  const { toast } = useToast();
  const [sensors, setSensors] = useState<VirtualSensor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await virtualSensorService.getAll({
        page,
        limit: 20,
        search: searchQuery || undefined,
        sensor_type: typeFilter || undefined,
        status: statusFilter || undefined,
      });
      setSensors(res.data);
      setTotalPages(res.meta.totalPages);
    } catch (error) {
      logger.error('Failed to load virtual sensors:', error);
      toast.error('خطأ في التحميل', 'فشل تحميل المستشعرات الافتراضية');
    } finally {
      setIsLoading(false);
    }
  }, [page, searchQuery, typeFilter, statusFilter, toast]);

  useEffect(() => { loadData(); }, [loadData]);

  const active = sensors.filter((s) => s.status === 'active').length;
  const inactive = sensors.filter((s) => s.status === 'inactive').length;
  const avgAccuracy = sensors.length > 0
    ? (sensors.reduce((sum, s) => sum + s.accuracy, 0) / sensors.length * 100).toFixed(1)
    : '—';

  const handleExport = () => {
    downloadCSV(
      sensors.map(({ id, name, sensor_type, status, algorithm, last_reading, unit, accuracy, last_updated }) => ({
        id, name, sensor_type, status, algorithm, last_reading, unit, accuracy, last_updated,
      })),
      'virtual-sensors'
    );
  };

  const statusBadge = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
      inactive: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
      error: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
    };
    const labels: Record<string, string> = { active: 'نشط', inactive: 'غير نشط', error: 'خطأ' };
    return <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] ?? ''}`}>{labels[status] ?? status}</span>;
  };

  const columns = [
    { key: 'name', header: 'الاسم' },
    { key: 'sensor_type', header: 'النوع' },
    { key: 'status', header: 'الحالة', render: (item: VirtualSensor) => statusBadge(item.status) },
    { key: 'algorithm', header: 'الخوارزمية' },
    { key: 'last_reading', header: 'آخر قراءة', render: (item: VirtualSensor) => `${item.last_reading} ${item.unit}` },
    { key: 'accuracy', header: 'الدقة', render: (item: VirtualSensor) => `${(item.accuracy * 100).toFixed(1)}%` },
    { key: 'last_updated', header: 'آخر تحديث', render: (item: VirtualSensor) => formatDate(item.last_updated) },
  ];

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <Header title="المستشعرات الافتراضية" subtitle="Virtual Sensors" />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center"><Radio className="w-5 h-5 text-blue-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{sensors.length}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي المستشعرات</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center"><Activity className="w-5 h-5 text-green-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{active}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">نشطة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center"><AlertTriangle className="w-5 h-5 text-gray-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{inactive}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">غير نشطة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center"><Target className="w-5 h-5 text-purple-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{avgAccuracy}%</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">متوسط الدقة</p>
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
          <select value={typeFilter} onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
            className="border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm">
            <option value="">كل الأنواع</option>
            <option value="temperature">حرارة</option>
            <option value="humidity">رطوبة</option>
            <option value="soil_moisture">رطوبة التربة</option>
            <option value="et0">ET0</option>
          </select>
          <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm">
            <option value="">كل الحالات</option>
            <option value="active">نشط</option>
            <option value="inactive">غير نشط</option>
            <option value="error">خطأ</option>
          </select>
          <button onClick={loadData} className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"><RefreshCw className="w-4 h-4" /></button>
          <button onClick={handleExport} disabled={sensors.length === 0}
            className="flex items-center gap-1 px-3 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50">
            <Download className="w-4 h-4" /> تصدير CSV
          </button>
        </div>
      </div>

      <DataTable columns={columns} data={sensors} keyExtractor={(item) => item.id} isLoading={isLoading} emptyMessage="لا توجد مستشعرات" />

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
