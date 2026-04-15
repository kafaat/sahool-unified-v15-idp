'use client';

/**
 * Drone Management Page — إدارة الطائرات المسيّرة
 * Two-tab view: Devices and Flights with stats, filters, and CSV export
 */

import { useEffect, useState, useCallback } from 'react';
import { useToast } from '@/components/ui/Toast';
import Header from '@/components/layout/Header';
import DataTable from '@/components/ui/DataTable';
import { formatDate } from '@/lib/utils';
import { Plane, Navigation, Battery, CheckCircle, Search, Download, RefreshCw } from 'lucide-react';
import { logger } from '@/lib/logger';
import { droneService, downloadCSV, type DroneDevice, type DroneFlight } from '@/lib/api';

type TabKey = 'devices' | 'flights';

export default function DronePage() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<TabKey>('devices');
  const [drones, setDrones] = useState<DroneDevice[]>([]);
  const [flights, setFlights] = useState<DroneFlight[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      if (activeTab === 'devices') {
        const res = await droneService.getDevices({ page, limit: 20, search: searchQuery || undefined, status: statusFilter || undefined });
        setDrones(res.data);
        setTotalPages(res.meta.totalPages);
      } else {
        const res = await droneService.getFlights({ page, limit: 20, search: searchQuery || undefined, status: statusFilter || undefined });
        setFlights(res.data);
        setTotalPages(res.meta.totalPages);
      }
    } catch (error) {
      logger.error('Failed to load drone data:', error);
      toast.error('خطأ في التحميل', 'فشل تحميل بيانات الطائرات');
    } finally {
      setIsLoading(false);
    }
  }, [activeTab, page, searchQuery, statusFilter, toast]);

  useEffect(() => { loadData(); }, [loadData]);

  const switchTab = (tab: TabKey) => {
    setActiveTab(tab);
    setPage(1);
    setSearchQuery('');
    setStatusFilter('');
  };

  const available = drones.filter((d) => d.status === 'available').length;
  const inFlight = drones.filter((d) => d.status === 'in_flight').length;
  const avgBattery = drones.length > 0 ? (drones.reduce((s, d) => s + d.battery_level, 0) / drones.length).toFixed(0) : '—';

  const handleExport = () => {
    if (activeTab === 'devices') {
      downloadCSV(drones.map(({ id, name, model, status, battery_level, total_flights, last_flight }) => ({
        id, name, model, status, battery_level, total_flights, last_flight,
      })), 'drone-devices');
    } else {
      downloadCSV(flights.map(({ id, drone_id, field_id, flight_type, status, start_time, area_covered_ha }) => ({
        id, drone_id, field_id, flight_type, status, start_time, area_covered_ha: area_covered_ha ?? '',
      })), 'drone-flights');
    }
  };

  const statusBadge = (status: string, colorMap: Record<string, string>, labelMap: Record<string, string>) => (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${colorMap[status] ?? ''}`}>{labelMap[status] ?? status}</span>
  );

  const droneStatusColors: Record<string, string> = {
    available: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    in_flight: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
    maintenance: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
    offline: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
  };
  const droneStatusLabels: Record<string, string> = { available: 'متاح', in_flight: 'في الجو', maintenance: 'صيانة', offline: 'غير متصل' };

  const flightStatusColors: Record<string, string> = {
    planned: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
    in_progress: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
    completed: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    cancelled: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
  };
  const flightStatusLabels: Record<string, string> = { planned: 'مخطط', in_progress: 'جارية', completed: 'مكتملة', cancelled: 'ملغاة' };

  const deviceColumns = [
    { key: 'name', header: 'الاسم' },
    { key: 'model', header: 'الطراز' },
    { key: 'status', header: 'الحالة', render: (item: DroneDevice) => statusBadge(item.status, droneStatusColors, droneStatusLabels) },
    { key: 'battery_level', header: 'البطارية', render: (item: DroneDevice) => `${item.battery_level}%` },
    { key: 'total_flights', header: 'الرحلات' },
    { key: 'last_flight', header: 'آخر رحلة', render: (item: DroneDevice) => formatDate(item.last_flight) },
  ];

  const flightColumns = [
    { key: 'drone_id', header: 'الطائرة' },
    { key: 'field_id', header: 'الحقل' },
    { key: 'flight_type', header: 'النوع' },
    { key: 'status', header: 'الحالة', render: (item: DroneFlight) => statusBadge(item.status, flightStatusColors, flightStatusLabels) },
    { key: 'start_time', header: 'وقت البدء', render: (item: DroneFlight) => formatDate(item.start_time) },
    { key: 'area_covered_ha', header: 'المساحة (هـ)', render: (item: DroneFlight) => item.area_covered_ha != null ? `${item.area_covered_ha} ha` : '—' },
  ];

  const statusOptions = activeTab === 'devices'
    ? [{ value: 'available', label: 'متاح' }, { value: 'in_flight', label: 'في الجو' }, { value: 'maintenance', label: 'صيانة' }, { value: 'offline', label: 'غير متصل' }]
    : [{ value: 'planned', label: 'مخطط' }, { value: 'in_progress', label: 'جارية' }, { value: 'completed', label: 'مكتملة' }, { value: 'cancelled', label: 'ملغاة' }];

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <Header title="إدارة الطائرات المسيّرة" subtitle="Drone Management" />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center"><Plane className="w-5 h-5 text-blue-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{drones.length}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي الطائرات</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center"><CheckCircle className="w-5 h-5 text-green-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{available}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">متاحة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center"><Navigation className="w-5 h-5 text-purple-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{inFlight}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">في الجو</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center"><Battery className="w-5 h-5 text-orange-600" /></div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{avgBattery}%</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">متوسط البطارية</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        <button onClick={() => switchTab('devices')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'devices' ? 'bg-blue-600 text-white' : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700'}`}>
          الطائرات
        </button>
        <button onClick={() => switchTab('flights')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'flights' ? 'bg-blue-600 text-white' : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700'}`}>
          الرحلات
        </button>
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
            {statusOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
          <button onClick={loadData} className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"><RefreshCw className="w-4 h-4" /></button>
          <button onClick={handleExport} disabled={(activeTab === 'devices' ? drones : flights).length === 0}
            className="flex items-center gap-1 px-3 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50">
            <Download className="w-4 h-4" /> تصدير CSV
          </button>
        </div>
      </div>

      {activeTab === 'devices' ? (
        <DataTable columns={deviceColumns} data={drones} keyExtractor={(item) => item.id} isLoading={isLoading} emptyMessage="لا توجد طائرات" />
      ) : (
        <DataTable columns={flightColumns} data={flights} keyExtractor={(item) => item.id} isLoading={isLoading} emptyMessage="لا توجد رحلات" />
      )}

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
