'use client';

// Crop Health Management Page
// صفحة إدارة صحة المحاصيل

import { useEffect, useState, useMemo } from 'react';
import Header from '@/components/layout/Header';
import DataTable from '@/components/ui/DataTable';
import { formatDate, cn } from '@/lib/utils';
import {
  Leaf,
  Search,
  RefreshCw,
  Download,
  Eye,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  Activity,
  MapPin,
} from 'lucide-react';
import { logger } from '../../lib/logger';
import { MOCK_RECORDS } from './crop-health.mock';
import type { CropHealthRecord } from './crop-health.mock';

export default function CropHealthPage() {
  const [records, setRecords] = useState<CropHealthRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadRecords();
  }, []);

  async function loadRecords() {
    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      setRecords(MOCK_RECORDS);
    } catch (error) {
      logger.error('Failed to load crop health records:', error);
    } finally {
      setIsLoading(false);
    }
  }

  const filteredRecords = useMemo(() => {
    return records.filter((r) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !r.farmNameAr.toLowerCase().includes(query) &&
          !r.cropAr.toLowerCase().includes(query) &&
          !r.fieldNameAr.toLowerCase().includes(query)
        ) {
          return false;
        }
      }
      if (statusFilter && r.healthStatus !== statusFilter) return false;
      return true;
    });
  }, [records, searchQuery, statusFilter]);

  const stats = useMemo(
    () => ({
      total: records.length,
      excellent: records.filter((r) => r.healthStatus === 'excellent').length,
      issues: records.filter((r) => r.issues.length > 0).length,
      critical: records.filter((r) => r.healthStatus === 'critical' || r.healthStatus === 'poor')
        .length,
      avgNdvi:
        records.length > 0
          ? (records.reduce((acc, r) => acc + r.ndvi, 0) / records.length).toFixed(2)
          : '0.00',
    }),
    [records]
  );

  const getStatusLabel = (status: CropHealthRecord['healthStatus']) => {
    const labels: Record<CropHealthRecord['healthStatus'], string> = {
      excellent: 'ممتاز',
      good: 'جيد',
      moderate: 'متوسط',
      poor: 'ضعيف',
      critical: 'حرج',
    };
    return labels[status];
  };

  const getStatusColor = (status: CropHealthRecord['healthStatus']) => {
    const colors: Record<CropHealthRecord['healthStatus'], string> = {
      excellent: 'bg-green-100 text-green-800',
      good: 'bg-green-50 text-green-700',
      moderate: 'bg-yellow-100 text-yellow-800',
      poor: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800',
    };
    return colors[status];
  };

  const getNdviColor = (ndvi: number) => {
    if (ndvi >= 0.7) return 'text-green-700';
    if (ndvi >= 0.5) return 'text-green-600';
    if (ndvi >= 0.3) return 'text-yellow-600';
    if (ndvi >= 0.15) return 'text-orange-600';
    return 'text-red-600';
  };

  const columns = [
    {
      key: 'location',
      header: 'الموقع',
      render: (record: CropHealthRecord) => (
        <div>
          <p className="font-medium text-gray-900 dark:text-gray-100">{record.farmNameAr}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {record.fieldNameAr}
          </p>
        </div>
      ),
    },
    {
      key: 'crop',
      header: 'المحصول',
      render: (record: CropHealthRecord) => (
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-sahool-100 rounded-lg flex items-center justify-center">
            <Leaf className="w-4 h-4 text-sahool-600" />
          </div>
          <span className="text-gray-700 dark:text-gray-300">{record.cropAr}</span>
        </div>
      ),
    },
    {
      key: 'ndvi',
      header: 'NDVI',
      render: (record: CropHealthRecord) => (
        <div className="flex items-center gap-2">
          <span className={cn('text-lg font-bold', getNdviColor(record.ndvi))}>
            {record.ndvi.toFixed(2)}
          </span>
          <span
            className={cn(
              'flex items-center text-xs',
              record.ndviChange >= 0 ? 'text-green-600' : 'text-red-600'
            )}
          >
            {record.ndviChange >= 0 ? (
              <TrendingUp className="w-3 h-3" />
            ) : (
              <TrendingDown className="w-3 h-3" />
            )}
            {record.ndviChange >= 0 ? '+' : ''}
            {record.ndviChange.toFixed(2)}
          </span>
        </div>
      ),
    },
    {
      key: 'issues',
      header: 'المشاكل',
      render: (record: CropHealthRecord) => (
        <div>
          {record.issuesAr.length > 0 ? (
            <div className="flex flex-wrap gap-1">
              {record.issuesAr.slice(0, 2).map((issue, idx) => (
                <span key={idx} className="px-2 py-0.5 bg-red-50 text-red-700 rounded text-xs">
                  {issue}
                </span>
              ))}
              {record.issuesAr.length > 2 && (
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  +{record.issuesAr.length - 2}
                </span>
              )}
            </div>
          ) : (
            <span className="text-green-600 text-sm flex items-center gap-1">
              <CheckCircle className="w-4 h-4" />
              لا توجد مشاكل
            </span>
          )}
        </div>
      ),
    },
    {
      key: 'status',
      header: 'الحالة',
      render: (record: CropHealthRecord) => (
        <span
          className={cn(
            'px-2 py-1 rounded-full text-xs font-medium',
            getStatusColor(record.healthStatus)
          )}
        >
          {getStatusLabel(record.healthStatus)}
        </span>
      ),
    },
    {
      key: 'inspection',
      header: 'الفحص',
      render: (record: CropHealthRecord) => (
        <div className="text-sm">
          <p className="text-gray-500 dark:text-gray-400">
            آخر: {formatDate(record.lastInspection)}
          </p>
          <p className="text-sahool-600">التالي: {formatDate(record.nextInspection)}</p>
        </div>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (_record: CropHealthRecord) => (
        <button
          disabled
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          title="عرض (قريبًا)"
        >
          <Eye className="w-4 h-4 text-gray-500 dark:text-gray-400" />
        </button>
      ),
      className: 'w-16',
    },
  ];

  return (
    <div className="p-6">
      <Header title="صحة المحاصيل" subtitle={`${records.length} حقل تحت المراقبة`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي الحقول</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stats.excellent}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">ممتاز</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.issues}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">بها مشاكل</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stats.critical}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">حرج/ضعيف</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-100 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-sahool-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.avgNdvi}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">متوسط NDVI</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث بالمزرعة أو المحصول..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="excellent">ممتاز</option>
            <option value="good">جيد</option>
            <option value="moderate">متوسط</option>
            <option value="poor">ضعيف</option>
            <option value="critical">حرج</option>
          </select>

          <button
            onClick={loadRecords}
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <RefreshCw
              className={cn(
                'w-5 h-5 text-gray-600 dark:text-gray-400',
                isLoading && 'animate-spin'
              )}
            />
          </button>
          <button
            disabled
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            title="تصدير (قريبًا)"
          >
            <Download className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6">
        {isLoading ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-8">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={filteredRecords}
            keyExtractor={(record) => record.id}
            emptyMessage="لا توجد سجلات مطابقة للبحث"
          />
        )}
      </div>
    </div>
  );
}
