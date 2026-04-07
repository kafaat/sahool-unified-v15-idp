'use client';

// Disaster Reports Page
// صفحة تقارير الكوارث

import { useEffect, useState, useMemo } from 'react';
import Header from '@/components/layout/Header';
import DataTable from '@/components/ui/DataTable';
import { formatDate, cn } from '@/lib/utils';
import {
  AlertTriangle,
  Search,
  RefreshCw,
  Download,
  Eye,
  CloudRain,
  Thermometer,
  Bug,
  Flame,
  Wind,
  MapPin,
  DollarSign,
} from 'lucide-react';
import { downloadCSV } from '@/lib/api';
import { disasterService } from '@/lib/api/advanced-services';
import type { DisasterAssessment as ApiDisasterAssessment } from '@/lib/api/advanced-services';
import { logger } from '../../lib/logger';
import { MOCK_REPORTS } from './disasters.mock';
import type { DisasterReport } from './disasters.mock';

type DisasterType = DisasterReport['type'];

const DISASTER_TYPE_AR: Record<string, string> = {
  flood: 'فيضان', drought: 'جفاف', frost: 'صقيع', hail: 'برد',
  pest_outbreak: 'آفات', disease_outbreak: 'أمراض', fire: 'حريق',
  storm: 'عاصفة', pest: 'آفات', disease: 'أمراض',
};

const SEVERITY_MAP: Record<string, DisasterReport['severity']> = {
  low: 'minor', medium: 'moderate', high: 'severe', critical: 'catastrophic',
};

const STATUS_MAP: Record<string, DisasterReport['status']> = {
  reported: 'active', assessed: 'monitoring', mitigated: 'monitoring', resolved: 'resolved',
};

/** Map API DisasterAssessment → UI DisasterReport */
function adaptApiDisaster(api: ApiDisasterAssessment): DisasterReport {
  const typeKey = api.disaster_type ?? 'flood';
  return {
    id: api.id,
    type: (typeKey === 'pest_outbreak' ? 'pest' : typeKey === 'disease_outbreak' ? 'disease' : typeKey) as DisasterType,
    typeAr: DISASTER_TYPE_AR[typeKey] ?? typeKey,
    location: api.field_id ?? '',
    locationAr: api.field_id ?? '',
    affectedFarms: 1,
    affectedArea: api.affected_area_ha ?? 0,
    severity: SEVERITY_MAP[api.severity] ?? 'moderate',
    status: STATUS_MAP[api.status] ?? 'active',
    damageEstimate: api.estimated_loss ?? 0,
    currency: 'SAR',
    reportedBy: '',
    reportedByAr: '',
    reportedAt: api.reported_at ?? '',
    resolvedAt: undefined,
    description: api.description ?? '',
    descriptionAr: api.description ?? '',
  };
}

export default function DisastersPage() {
  const [reports, setReports] = useState<DisasterReport[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadReports();
  }, []);

  async function loadReports() {
    setIsLoading(true);
    try {
      const response = await disasterService.list();
      if (response.data.length > 0) {
        setReports(response.data.map(adaptApiDisaster));
      } else {
        setReports(MOCK_REPORTS);
      }
    } catch {
      logger.error('Failed to load disaster reports from API, using mock data');
      setReports(MOCK_REPORTS);
    } finally {
      setIsLoading(false);
    }
  }

  const filteredReports = useMemo(() => {
    return reports.filter((r) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !r.locationAr.toLowerCase().includes(query) &&
          !r.descriptionAr.toLowerCase().includes(query)
        ) {
          return false;
        }
      }
      if (typeFilter && r.type !== typeFilter) return false;
      if (statusFilter && r.status !== statusFilter) return false;
      return true;
    });
  }, [reports, searchQuery, typeFilter, statusFilter]);

  const stats = useMemo(
    () => ({
      total: reports.length,
      active: reports.filter((r) => r.status === 'active').length,
      totalDamage: reports.reduce((acc, r) => acc + r.damageEstimate, 0),
      affectedFarms: reports
        .filter((r) => r.status === 'active')
        .reduce((acc, r) => acc + r.affectedFarms, 0),
    }),
    [reports]
  );

  const getTypeIcon = (type: DisasterType) => {
    const icons: Record<DisasterType, React.ReactNode> = {
      flood: <CloudRain className="w-5 h-5" />,
      drought: <Thermometer className="w-5 h-5" />,
      frost: <Thermometer className="w-5 h-5" />,
      pest: <Bug className="w-5 h-5" />,
      disease: <Bug className="w-5 h-5" />,
      storm: <Wind className="w-5 h-5" />,
      fire: <Flame className="w-5 h-5" />,
    };
    return icons[type];
  };

  const getSeverityLabel = (severity: DisasterReport['severity']) => {
    const labels: Record<DisasterReport['severity'], string> = {
      minor: 'طفيف',
      moderate: 'متوسط',
      severe: 'شديد',
      catastrophic: 'كارثي',
    };
    return labels[severity];
  };

  const getSeverityColor = (severity: DisasterReport['severity']) => {
    const colors: Record<DisasterReport['severity'], string> = {
      minor: 'bg-yellow-100 text-yellow-800',
      moderate: 'bg-orange-100 text-orange-800',
      severe: 'bg-red-100 text-red-800',
      catastrophic: 'bg-purple-100 text-purple-800',
    };
    return colors[severity];
  };

  const getStatusLabel = (status: DisasterReport['status']) => {
    const labels: Record<DisasterReport['status'], string> = {
      active: 'نشط',
      monitoring: 'قيد المراقبة',
      resolved: 'تم الحل',
      closed: 'مغلق',
    };
    return labels[status];
  };

  const getStatusColor = (status: DisasterReport['status']) => {
    const colors: Record<DisasterReport['status'], string> = {
      active: 'bg-red-100 text-red-800',
      monitoring: 'bg-blue-100 text-blue-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800',
    };
    return colors[status];
  };

  const columns = [
    {
      key: 'type',
      header: 'النوع',
      render: (report: DisasterReport) => (
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center text-red-600">
            {getTypeIcon(report.type)}
          </div>
          <span className="font-medium text-gray-900 dark:text-gray-100">{report.typeAr}</span>
        </div>
      ),
    },
    {
      key: 'location',
      header: 'الموقع',
      render: (report: DisasterReport) => (
        <div className="flex items-center gap-1 text-gray-700 dark:text-gray-300">
          <MapPin className="w-4 h-4 text-gray-400" />
          {report.locationAr}
        </div>
      ),
    },
    {
      key: 'impact',
      header: 'التأثير',
      render: (report: DisasterReport) => (
        <div className="text-sm">
          <p className="text-gray-900 dark:text-gray-100">{report.affectedFarms} مزرعة</p>
          <p className="text-gray-500 dark:text-gray-400">{report.affectedArea} هكتار</p>
        </div>
      ),
    },
    {
      key: 'damage',
      header: 'الأضرار',
      render: (report: DisasterReport) => (
        <span className="font-medium text-red-600">
          {report.damageEstimate.toLocaleString()} {report.currency}
        </span>
      ),
    },
    {
      key: 'severity',
      header: 'الشدة',
      render: (report: DisasterReport) => (
        <span
          className={cn(
            'px-2 py-1 rounded-full text-xs font-medium',
            getSeverityColor(report.severity)
          )}
        >
          {getSeverityLabel(report.severity)}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'الحالة',
      render: (report: DisasterReport) => (
        <span
          className={cn(
            'px-2 py-1 rounded-full text-xs font-medium',
            getStatusColor(report.status)
          )}
        >
          {getStatusLabel(report.status)}
        </span>
      ),
    },
    {
      key: 'date',
      header: 'التاريخ',
      render: (report: DisasterReport) => (
        <span className="text-gray-500 dark:text-gray-400 text-sm">
          {formatDate(report.reportedAt)}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (_report: DisasterReport) => (
        <button
          disabled
          className="p-2 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          title="عرض (قريبًا)"
        >
          <Eye className="w-4 h-4 text-gray-500" />
        </button>
      ),
      className: 'w-16',
    },
  ];

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6">
      <Header title="تقارير الكوارث" subtitle={`${reports.length} تقرير`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي التقارير</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.active}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">نشط حالياً</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {(stats.totalDamage / 1000000).toFixed(1)}M
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي الأضرار (SAR)</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-100 rounded-lg flex items-center justify-center">
              <MapPin className="w-5 h-5 text-sahool-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stats.affectedFarms}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">مزارع متأثرة (نشط)</p>
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
              placeholder="بحث بالموقع أو الوصف..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الأنواع</option>
            <option value="drought">جفاف</option>
            <option value="flood">فيضان</option>
            <option value="frost">صقيع</option>
            <option value="pest">آفات</option>
            <option value="disease">أمراض</option>
            <option value="storm">عاصفة</option>
            <option value="fire">حريق</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="active">نشط</option>
            <option value="monitoring">قيد المراقبة</option>
            <option value="resolved">تم الحل</option>
            <option value="closed">مغلق</option>
          </select>

          <button
            onClick={loadReports}
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <RefreshCw
              className={cn(
                'w-5 h-5 text-gray-600 dark:text-gray-300',
                isLoading && 'animate-spin'
              )}
            />
          </button>
          <button
            onClick={() => downloadCSV(reports as Record<string, unknown>[], 'disaster-reports')}
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            title="تصدير CSV"
          >
            <Download className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6">
        {isLoading ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-8">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ))}
            </div>
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={filteredReports}
            keyExtractor={(report) => report.id}
            emptyMessage="لا توجد تقارير مطابقة للبحث"
          />
        )}
      </div>
    </div>
  );
}
