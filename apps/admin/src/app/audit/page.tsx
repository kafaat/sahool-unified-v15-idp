'use client';

/**
 * Audit Trail Page — Developer Platform Tool
 * سجل التدقيق — أداة مطوري المنصة
 *
 * Admin-only: Protected by route-protection.ts
 * Connects to: audit-service (port 8114) via /api/audit proxy
 */

import { useCallback, useEffect, useState } from 'react';
import Header from '@/components/layout/Header';
import {
  Shield,
  FileText,
  AlertTriangle,
  Users,
  ClipboardList,
  Search,
  RefreshCw,
  Download,
  Filter,
  ChevronDown,
  ChevronUp,
  Loader2,
  XCircle,
  CheckCircle2,
  Info,
} from 'lucide-react';

// ─── Types ──────────────────────────────────────────────────────────────────

interface AuditLog {
  id: string;
  tenant_id: string;
  user_id: string;
  action: string;
  category: string;
  severity: string;
  resource_type?: string;
  resource_id?: string;
  ip_address?: string;
  success: boolean;
  details?: Record<string, unknown>;
  created_at: string;
}

interface AuditStats {
  total_events: number;
  events_by_category: Record<string, number>;
  events_by_severity: Record<string, number>;
  failed_events: number;
  unique_users: number;
  chain_coverage_percent: number;
}

interface PaginatedResponse {
  items: AuditLog[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

// ─── Helpers ────────────────────────────────────────────────────────────────

const SEVERITY_CONFIG: Record<string, { color: string; bg: string; icon: typeof Info }> = {
  critical: { color: 'text-red-700', bg: 'bg-red-100', icon: XCircle },
  error: { color: 'text-red-600', bg: 'bg-red-50', icon: XCircle },
  warning: { color: 'text-yellow-700', bg: 'bg-yellow-100', icon: AlertTriangle },
  info: { color: 'text-blue-600', bg: 'bg-blue-50', icon: Info },
};

const CATEGORY_LABELS: Record<string, string> = {
  user: 'مستخدمون',
  field: 'حقول',
  alert: 'تنبيهات',
  task: 'مهام',
  security: 'أمان',
  system: 'نظام',
};

function formatDate(iso: string): string {
  try {
    return new Intl.DateTimeFormat('ar-SA', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [stats, setStats] = useState<AuditStats | null>(null);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [page, setPage] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const limit = 25;

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch('/api/audit?action=stats&period=30d');
      if (res.ok) {
        setStats(await res.json());
      }
    } catch {
      // Stats are non-critical
    }
  }, []);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        action: 'logs',
        skip: String(page * limit),
        limit: String(limit),
      });
      if (categoryFilter) params.set('category', categoryFilter);

      const res = await fetch(`/api/audit?${params.toString()}`);
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || `HTTP ${res.status}`);
      }
      const data: PaginatedResponse = await res.json();
      setLogs(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'فشل تحميل السجلات');
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }, [page, categoryFilter]);

  useEffect(() => {
    fetchStats();
    fetchLogs();
  }, [fetchStats, fetchLogs]);

  const handleExport = async () => {
    const now = new Date();
    const start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString();
    const end = now.toISOString();
    window.open(`/api/audit?action=export&start_date=${start}&end_date=${end}&format=csv`, '_blank');
  };

  // Client-side search filter (on already-fetched data)
  const filteredLogs = logs.filter((log) => {
    if (search) {
      const q = search.toLowerCase();
      const matchesSearch =
        log.action.toLowerCase().includes(q) ||
        log.user_id.toLowerCase().includes(q) ||
        (log.resource_type || '').toLowerCase().includes(q) ||
        (log.ip_address || '').includes(q);
      if (!matchesSearch) return false;
    }
    if (severityFilter && log.severity !== severityFilter) return false;
    return true;
  });

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <Header title="سجل التدقيق" subtitle="Audit Trail — Developer Platform Tool" />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stats ? stats.total_events.toLocaleString('ar-SA') : '—'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي الأحداث</p>
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
                {stats ? stats.failed_events.toLocaleString('ar-SA') : '—'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">أحداث فاشلة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stats ? stats.unique_users.toLocaleString('ar-SA') : '—'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">مستخدمون فريدون</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stats ? `${stats.chain_coverage_percent.toFixed(0)}%` : '—'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">تغطية سلسلة التجزئة</p>
            </div>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 mb-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="بحث في السجلات..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pr-10 pl-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <Filter className="w-4 h-4" />
            فلاتر
            {showFilters ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
          <button
            onClick={() => { fetchLogs(); fetchStats(); }}
            className="flex items-center gap-2 px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <RefreshCw className="w-4 h-4" />
            تحديث
          </button>
          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
          >
            <Download className="w-4 h-4" />
            تصدير CSV
          </button>
        </div>

        {/* Filter row */}
        {showFilters && (
          <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-sm text-gray-900 dark:text-gray-100"
            >
              <option value="">كل المستويات</option>
              <option value="critical">حرج</option>
              <option value="error">خطأ</option>
              <option value="warning">تحذير</option>
              <option value="info">معلومات</option>
            </select>
            <select
              value={categoryFilter}
              onChange={(e) => { setCategoryFilter(e.target.value); setPage(0); }}
              className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-sm text-gray-900 dark:text-gray-100"
            >
              <option value="">كل الفئات</option>
              <option value="user">مستخدمون</option>
              <option value="field">حقول</option>
              <option value="alert">تنبيهات</option>
              <option value="task">مهام</option>
              <option value="security">أمان</option>
              <option value="system">نظام</option>
            </select>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 mb-4 flex items-center gap-3">
          <XCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
        </div>
      )}

      {/* Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
            <span className="mr-3 text-gray-500">جارٍ التحميل...</span>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="text-center py-16">
            <ClipboardList className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">لا توجد سجلات تدقيق</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th className="text-right px-4 py-3 font-medium text-gray-500 dark:text-gray-400">التاريخ</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500 dark:text-gray-400">المستخدم</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500 dark:text-gray-400">الإجراء</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500 dark:text-gray-400">الفئة</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500 dark:text-gray-400">المستوى</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500 dark:text-gray-400">المورد</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500 dark:text-gray-400">الحالة</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500 dark:text-gray-400">IP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                {filteredLogs.map((log) => {
                  const sev = SEVERITY_CONFIG[log.severity] || SEVERITY_CONFIG.info;
                  const SevIcon = sev.icon;
                  return (
                    <tr key={log.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300 whitespace-nowrap">
                        {formatDate(log.created_at)}
                      </td>
                      <td className="px-4 py-3 text-gray-900 dark:text-gray-100 font-mono text-xs">
                        {log.user_id}
                      </td>
                      <td className="px-4 py-3 text-gray-900 dark:text-gray-100">{log.action}</td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-xs text-gray-600 dark:text-gray-300">
                          {CATEGORY_LABELS[log.category] || log.category}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${sev.bg} ${sev.color}`}>
                          <SevIcon className="w-3 h-3" />
                          {log.severity}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300 text-xs font-mono">
                        {log.resource_type ? `${log.resource_type}/${log.resource_id || ''}` : '—'}
                      </td>
                      <td className="px-4 py-3">
                        {log.success ? (
                          <CheckCircle2 className="w-4 h-4 text-green-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-500" />
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-400 text-xs font-mono">{log.ip_address || '—'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {total > limit && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              عرض {page * limit + 1}–{Math.min((page + 1) * limit, total)} من {total.toLocaleString('ar-SA')}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(Math.max(0, page - 1))}
                disabled={page === 0}
                className="px-3 py-1 rounded border text-sm disabled:opacity-40"
              >
                السابق
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={(page + 1) * limit >= total}
                className="px-3 py-1 rounded border text-sm disabled:opacity-40"
              >
                التالي
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
