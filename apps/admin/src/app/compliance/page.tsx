'use client';

// Compliance Reports Page
// صفحة تقارير الامتثال

import { useEffect, useState, useMemo } from 'react';
import Header from '@/components/layout/Header';
import DataTable from '@/components/ui/DataTable';
import { formatDate, cn } from '@/lib/utils';
import {
  Search,
  RefreshCw,
  Download,
  Eye,
  CheckCircle,
  AlertTriangle,
  FileText,
  Award,
  Clock,
} from 'lucide-react';
import { downloadCSV } from '@/lib/api';
import { complianceService } from '@/lib/api/advanced-services';
import type { ComplianceRecord as ApiComplianceRecord } from '@/lib/api/advanced-services';
import { logger } from '../../lib/logger';
import { MOCK_RECORDS } from './compliance.mock';
import type { ComplianceRecord } from './compliance.mock';

/** Map API ComplianceRecord (snake_case) → UI ComplianceRecord (camelCase) */
function adaptApiCompliance(api: ApiComplianceRecord): ComplianceRecord {
  const statusMap: Record<string, ComplianceRecord['status']> = {
    compliant: 'compliant',
    non_compliant: 'non_compliant',
    pending_review: 'pending',
    in_progress: 'partial',
  };
  return {
    id: api.id,
    farmId: api.farm_id,
    farmName: api.farm_id,
    farmNameAr: api.farm_id,
    standard: (api.standard as ComplianceRecord['standard']) || 'globalgap',
    status: statusMap[api.status] ?? 'pending',
    score: api.score ?? 0,
    lastAudit: api.audit_date ?? '',
    nextAudit: api.next_audit_date ?? '',
    auditor: '',
    findings: api.findings ?? 0,
    criticalFindings: 0,
  };
}

export default function CompliancePage() {
  const [records, setRecords] = useState<ComplianceRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [standardFilter, setStandardFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadRecords();
  }, []);

  async function loadRecords() {
    setIsLoading(true);
    try {
      const response = await complianceService.list();
      if (response.data.length > 0) {
        setRecords(response.data.map(adaptApiCompliance));
      } else {
        setRecords(MOCK_RECORDS);
      }
    } catch {
      logger.error('Failed to load compliance records from API, using mock data');
      setRecords(MOCK_RECORDS);
    } finally {
      setIsLoading(false);
    }
  }

  const filteredRecords = useMemo(() => {
    return records.filter((r) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !r.farmName.toLowerCase().includes(query) &&
          !r.farmNameAr.toLowerCase().includes(query)
        ) {
          return false;
        }
      }
      if (standardFilter && r.standard !== standardFilter) return false;
      if (statusFilter && r.status !== statusFilter) return false;
      return true;
    });
  }, [records, searchQuery, standardFilter, statusFilter]);

  const stats = useMemo(
    () => ({
      total: records.length,
      compliant: records.filter((r) => r.status === 'compliant').length,
      partial: records.filter((r) => r.status === 'partial').length,
      expired: records.filter((r) => r.status === 'expired').length,
      avgScore:
        Math.round(
          records.filter((r) => r.score > 0).reduce((acc, r) => acc + r.score, 0) /
            records.filter((r) => r.score > 0).length
        ) || 0,
    }),
    [records]
  );

  const getStandardLabel = (standard: ComplianceRecord['standard']) => {
    const labels: Record<ComplianceRecord['standard'], string> = {
      globalgap: 'GlobalGAP',
      organic: 'عضوي',
      iso: 'ISO 22000',
      haccp: 'HACCP',
    };
    return labels[standard];
  };

  const getStatusLabel = (status: ComplianceRecord['status']) => {
    const labels: Record<ComplianceRecord['status'], string> = {
      compliant: 'متوافق',
      partial: 'جزئي',
      non_compliant: 'غير متوافق',
      pending: 'قيد التدقيق',
      expired: 'منتهي',
    };
    return labels[status];
  };

  const getStatusColor = (status: ComplianceRecord['status']) => {
    const colors: Record<ComplianceRecord['status'], string> = {
      compliant: 'bg-green-100 text-green-800',
      partial: 'bg-yellow-100 text-yellow-800',
      non_compliant: 'bg-red-100 text-red-800',
      pending: 'bg-blue-100 text-blue-800',
      expired: 'bg-gray-100 text-gray-800',
    };
    return colors[status];
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    if (score > 0) return 'text-red-600';
    return 'text-gray-400';
  };

  const columns = [
    {
      key: 'farm',
      header: 'المزرعة',
      render: (record: ComplianceRecord) => (
        <div>
          <p className="font-medium text-gray-900 dark:text-gray-100">{record.farmNameAr}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{record.farmId}</p>
        </div>
      ),
    },
    {
      key: 'standard',
      header: 'المعيار',
      render: (record: ComplianceRecord) => (
        <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
          {getStandardLabel(record.standard)}
        </span>
      ),
    },
    {
      key: 'score',
      header: 'النتيجة',
      render: (record: ComplianceRecord) => (
        <span className={cn('text-lg font-bold', getScoreColor(record.score))}>
          {record.score > 0 ? `${record.score}%` : '—'}
        </span>
      ),
    },
    {
      key: 'findings',
      header: 'الملاحظات',
      render: (record: ComplianceRecord) => (
        <div className="text-sm">
          <span className="text-gray-600 dark:text-gray-400">{record.findings} ملاحظة</span>
          {record.criticalFindings > 0 && (
            <span className="text-red-600 font-medium mr-2">({record.criticalFindings} حرجة)</span>
          )}
        </div>
      ),
    },
    {
      key: 'audit',
      header: 'التدقيق',
      render: (record: ComplianceRecord) => (
        <div className="text-sm">
          {record.lastAudit && (
            <p className="text-gray-500 dark:text-gray-400">آخر: {formatDate(record.lastAudit)}</p>
          )}
          <p className="text-sahool-600">التالي: {formatDate(record.nextAudit)}</p>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'الحالة',
      render: (record: ComplianceRecord) => (
        <span
          className={cn(
            'px-2 py-1 rounded-full text-xs font-medium',
            getStatusColor(record.status)
          )}
        >
          {getStatusLabel(record.status)}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (_record: ComplianceRecord) => (
        <div className="flex items-center gap-1">
          <button
            disabled
            className="p-2 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            title="عرض التقرير (قريبًا)"
          >
            <Eye className="w-4 h-4 text-gray-500" />
          </button>
          <button
            disabled
            className="p-2 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            title="تحميل (قريبًا)"
          >
            <Download className="w-4 h-4 text-gray-500" />
          </button>
        </div>
      ),
      className: 'w-24',
    },
  ];

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6">
      <Header title="تقارير الامتثال" subtitle={`${records.length} سجل امتثال`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي السجلات</p>
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
                {stats.compliant}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">متوافق</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.partial}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">جزئي</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.expired}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">منتهي</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-100 rounded-lg flex items-center justify-center">
              <Award className="w-5 h-5 text-sahool-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stats.avgScore}%
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">متوسط النتيجة</p>
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
              placeholder="بحث بالمزرعة..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <select
            value={standardFilter}
            onChange={(e) => setStandardFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل المعايير</option>
            <option value="globalgap">GlobalGAP</option>
            <option value="organic">عضوي</option>
            <option value="iso">ISO 22000</option>
            <option value="haccp">HACCP</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="compliant">متوافق</option>
            <option value="partial">جزئي</option>
            <option value="non_compliant">غير متوافق</option>
            <option value="pending">قيد التدقيق</option>
            <option value="expired">منتهي</option>
          </select>

          <button
            onClick={loadRecords}
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
            onClick={() => downloadCSV(records, 'compliance-records')}
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
            data={filteredRecords}
            keyExtractor={(record) => record.id}
            emptyMessage="لا توجد سجلات مطابقة للبحث"
          />
        )}
      </div>
    </div>
  );
}
