'use client';

import React, { useState, useMemo } from 'react';
import {
  CheckCircle2,
  XCircle,
  Clock,
  CalendarClock,
  RefreshCw,
  Search,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  CloudOff,
  Satellite,
  ExternalLink,
  RotateCcw,
  Minus,
  Play,
} from 'lucide-react';
import { useSchedulerLogs, useSchedulerStats, schedulerLogsApi } from '@/features/scheduler-logs';
import type { SchedulerFilters, SchedulerLogEntry, SchedulerPeriod, SchedulerStatus } from '@/features/scheduler-logs';
import { useQueryClient } from '@tanstack/react-query';
import { schedulerLogsKeys } from '@/features/scheduler-logs';

// ─── Constants ────────────────────────────────────────────────────────────────

const PERIOD_OPTIONS: { value: SchedulerPeriod; labelAr: string; label: string }[] = [
  { value: '7d', labelAr: '7 أيام', label: '7 days' },
  { value: '30d', labelAr: '30 يوم', label: '30 days' },
  { value: '90d', labelAr: '90 يوم', label: '90 days' },
];

const STATUS_OPTIONS: { value: SchedulerStatus | 'all'; labelAr: string; label: string }[] = [
  { value: 'all', labelAr: 'الكل', label: 'All' },
  { value: 'completed', labelAr: 'مكتمل', label: 'Completed' },
  { value: 'missed', labelAr: 'فائت', label: 'Missed' },
  { value: 'failed', labelAr: 'فاشل', label: 'Failed' },
  { value: 'retry_pending', labelAr: 'إعادة محاولة', label: 'Retry' },
  { value: 'skipped', labelAr: 'متخطى', label: 'Skipped' },
];

const STATUS_CONFIG: Record<
  SchedulerStatus,
  { labelAr: string; label: string; color: string; bg: string; icon: React.ReactNode }
> = {
  completed: {
    labelAr: 'مكتمل',
    label: 'Completed',
    color: 'text-green-700',
    bg: 'bg-green-100',
    icon: <CheckCircle2 className="w-3.5 h-3.5 text-green-600" />,
  },
  missed: {
    labelAr: 'فائت',
    label: 'Missed',
    color: 'text-yellow-700',
    bg: 'bg-yellow-100',
    icon: <CloudOff className="w-3.5 h-3.5 text-yellow-600" />,
  },
  failed: {
    labelAr: 'فاشل',
    label: 'Failed',
    color: 'text-red-700',
    bg: 'bg-red-100',
    icon: <XCircle className="w-3.5 h-3.5 text-red-600" />,
  },
  retry_pending: {
    labelAr: 'إعادة محاولة',
    label: 'Retry',
    color: 'text-orange-700',
    bg: 'bg-orange-100',
    icon: <RotateCcw className="w-3.5 h-3.5 text-orange-600" />,
  },
  skipped: {
    labelAr: 'متخطى',
    label: 'Skipped',
    color: 'text-gray-600',
    bg: 'bg-gray-100',
    icon: <Minus className="w-3.5 h-3.5 text-gray-500" />,
  },
};

const PAGE_LIMIT = 50;

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatDateTime(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('ar-SA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatDateTimeEn(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function ndviColor(val: number | undefined): string {
  if (val === undefined || val === null) return 'text-gray-400';
  if (val >= 0.6) return 'text-green-700';
  if (val >= 0.4) return 'text-yellow-600';
  if (val >= 0.2) return 'text-orange-600';
  return 'text-red-600';
}

// ─── Sub-components ───────────────────────────────────────────────────────────

interface StatCardProps {
  icon: React.ReactNode;
  iconBg: string;
  labelAr: string;
  label: string;
  value: React.ReactNode;
  sub?: string;
  valueColor?: string;
}

function StatCard({ icon, iconBg, labelAr, label, value, sub, valueColor = 'text-gray-900' }: StatCardProps) {
  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 ${iconBg} rounded-lg flex items-center justify-center flex-shrink-0`}>
          {icon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-xs text-gray-500 truncate">{labelAr}</div>
          <div className="text-[10px] text-gray-400 truncate">{label}</div>
          <div className={`text-xl font-bold leading-tight ${valueColor}`}>{value}</div>
          {sub && <div className="text-[10px] text-gray-400 mt-0.5 truncate">{sub}</div>}
        </div>
      </div>
    </div>
  );
}

interface IndexCellProps {
  val: { mean: number } | null;
}

function IndexCell({ val }: IndexCellProps) {
  if (!val) return <span className="text-gray-300 text-xs">—</span>;
  return (
    <span className={`text-xs font-mono font-semibold ${ndviColor(val.mean)}`}>
      {val.mean.toFixed(3)}
    </span>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function SchedulerLogsClient() {
  const queryClient = useQueryClient();

  const [period, setPeriod] = useState<SchedulerPeriod>('30d');
  const [statusFilter, setStatusFilter] = useState<SchedulerStatus | 'all'>('all');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [triggerState, setTriggerState] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  const filters: SchedulerFilters = useMemo(
    () => ({ period, status: statusFilter, search, page, limit: PAGE_LIMIT }),
    [period, statusFilter, search, page]
  );

  const { data: logsData, isLoading: logsLoading, error: logsError } = useSchedulerLogs(filters);
  const { data: stats, isLoading: statsLoading } = useSchedulerStats(period);

  const totalPages = logsData ? Math.ceil(logsData.total / PAGE_LIMIT) : 0;

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: schedulerLogsKeys.logs(filters) }),
      queryClient.invalidateQueries({ queryKey: schedulerLogsKeys.stats(period) }),
    ]);
    setIsRefreshing(false);
  };

  const handlePeriodChange = (p: SchedulerPeriod) => {
    setPeriod(p);
    setPage(1);
  };

  const handleStatusChange = (s: SchedulerStatus | 'all') => {
    setStatusFilter(s);
    setPage(1);
  };

  const handleSearch = (q: string) => {
    setSearch(q);
    setPage(1);
  };

  const handleTrigger = async () => {
    setTriggerState('loading');
    try {
      await schedulerLogsApi.triggerNow();
      setTriggerState('success');
      // Refresh data after a short delay to let the job start
      setTimeout(async () => {
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: schedulerLogsKeys.logs(filters) }),
          queryClient.invalidateQueries({ queryKey: schedulerLogsKeys.stats(period) }),
        ]);
        setTriggerState('idle');
      }, 3000);
    } catch {
      setTriggerState('error');
      setTimeout(() => setTriggerState('idle'), 4000);
    }
  };

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-5 p-1">

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">سجلات المجدول</h1>
          <p className="text-gray-500 mt-0.5 text-sm">Scheduler Logs — Daily CDSE Satellite Fetch Activity</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Period selector */}
          <div className="flex rounded-lg border overflow-hidden">
            {PERIOD_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => handlePeriodChange(opt.value)}
                className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                  period === opt.value
                    ? 'bg-green-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                {opt.labelAr}
              </button>
            ))}
          </div>
          {/* Manual trigger */}
          <button
            type="button"
            onClick={handleTrigger}
            disabled={triggerState === 'loading'}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border rounded-lg transition-colors disabled:opacity-60 ${
              triggerState === 'success'
                ? 'bg-green-50 border-green-300 text-green-700'
                : triggerState === 'error'
                ? 'bg-red-50 border-red-300 text-red-700'
                : 'bg-green-600 border-green-600 text-white hover:bg-green-700'
            }`}
            title="تشغيل يدوي — تحميل صور اليوم لجميع الحقول"
          >
            {triggerState === 'loading' ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : triggerState === 'success' ? (
              <CheckCircle2 className="w-4 h-4" />
            ) : triggerState === 'error' ? (
              <AlertTriangle className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            {triggerState === 'loading'
              ? 'جارٍ التشغيل…'
              : triggerState === 'success'
              ? 'تم التشغيل ✓'
              : triggerState === 'error'
              ? 'فشل التشغيل'
              : 'تشغيل الآن'}
          </button>
          {/* Refresh */}
          <button
            type="button"
            onClick={handleRefresh}
            disabled={isRefreshing || logsLoading}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border rounded-lg bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            تحديث
          </button>
        </div>
      </div>

      {/* ── Stat tiles ─────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<CheckCircle2 className="w-5 h-5 text-green-600" />}
          iconBg="bg-green-100"
          labelAr="عمليات جلب ناجحة"
          label="Successful Grabs"
          value={
            statsLoading ? (
              <span className="inline-block h-5 w-12 bg-gray-200 rounded animate-pulse" />
            ) : (
              (stats?.successfulRuns ?? 0).toLocaleString()
            )
          }
          sub={
            stats
              ? `معدل النجاح ${(stats.successRate * 100).toFixed(1)}%`
              : undefined
          }
          valueColor="text-green-700"
        />
        <StatCard
          icon={<XCircle className="w-5 h-5 text-red-500" />}
          iconBg="bg-red-100"
          labelAr="عمليات فاشلة / فائتة"
          label="Failed / Missed Grabs"
          value={
            statsLoading ? (
              <span className="inline-block h-5 w-12 bg-gray-200 rounded animate-pulse" />
            ) : (
              ((stats?.failedRuns ?? 0) + (stats?.missedRuns ?? 0)).toLocaleString()
            )
          }
          sub={
            stats
              ? `فاشل ${stats.failedRuns} · فائت ${stats.missedRuns}`
              : undefined
          }
          valueColor="text-red-600"
        />
        <StatCard
          icon={<Clock className="w-5 h-5 text-blue-600" />}
          iconBg="bg-blue-100"
          labelAr="آخر عملية جلب"
          label="Last Grab"
          value={
            statsLoading ? (
              <span className="inline-block h-5 w-32 bg-gray-200 rounded animate-pulse" />
            ) : stats?.lastRunAt ? (
              <span className="text-base font-semibold">{formatDateTimeEn(stats.lastRunAt)}</span>
            ) : (
              <span className="text-gray-400 text-base">—</span>
            )
          }
          sub={stats?.lastRunAt ? formatDateTime(stats.lastRunAt) : undefined}
        />
        <StatCard
          icon={<CalendarClock className="w-5 h-5 text-purple-600" />}
          iconBg="bg-purple-100"
          labelAr="الجلسة القادمة"
          label="Next Scheduled"
          value={
            statsLoading ? (
              <span className="inline-block h-5 w-32 bg-gray-200 rounded animate-pulse" />
            ) : stats?.nextRunAt ? (
              <span className="text-base font-semibold">{formatDateTimeEn(stats.nextRunAt)}</span>
            ) : (
              <span className="text-gray-400 text-base">00:00 يومياً</span>
            )
          }
          sub={`${stats?.totalFieldsProcessed ?? 0} حقل · غطاء سحابي متوسط ${(stats?.averageCloudCover ?? 0).toFixed(1)}%`}
        />
      </div>

      {/* ── Filters ────────────────────────────────────────────────────────── */}
      <div className="bg-white rounded-lg border p-3 flex flex-col sm:flex-row gap-3">
        {/* Status */}
        <select
          value={statusFilter}
          onChange={(e) => handleStatusChange(e.target.value as SchedulerStatus | 'all')}
          className="px-3 py-1.5 border rounded-lg text-sm focus:ring-2 focus:ring-green-500 bg-white"
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.labelAr} · {opt.label}
            </option>
          ))}
        </select>
        {/* Search */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="بحث باسم الحقل... | Search field name..."
            className="w-full pl-3 pr-9 py-1.5 border rounded-lg text-sm focus:ring-2 focus:ring-green-500"
          />
        </div>
        {logsData && (
          <div className="flex items-center text-sm text-gray-500 whitespace-nowrap">
            {logsData.total.toLocaleString()} سجل
          </div>
        )}
      </div>

      {/* ── Table ──────────────────────────────────────────────────────────── */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="font-semibold text-gray-900 text-sm">
            سجلات الجلب اليومي · Daily Fetch Log
          </h2>
          <div className="text-xs text-gray-400">
            CDSE · vegetation-analysis-service:8090
          </div>
        </div>

        {/* Error state */}
        {logsError && (
          <div className="flex items-center gap-3 p-6 text-sm text-red-600">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <div>
              <div className="font-medium">تعذّر تحميل السجلات</div>
              <div className="text-gray-500">Failed to load scheduler logs</div>
            </div>
          </div>
        )}

        {/* Loading skeleton */}
        {logsLoading && !logsError && (
          <div className="divide-y animate-pulse">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="flex gap-4 px-4 py-3">
                {Array.from({ length: 9 }).map((_, j) => (
                  <div key={j} className="h-4 bg-gray-100 rounded flex-1" />
                ))}
              </div>
            ))}
          </div>
        )}

        {/* Empty state */}
        {!logsLoading && !logsError && logsData && logsData.logs.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <Satellite className="w-12 h-12 text-gray-300 mb-3" />
            <div className="text-gray-500 font-medium">لا توجد سجلات</div>
            <div className="text-gray-400 text-sm">No scheduler logs found for the selected filters</div>
          </div>
        )}

        {/* Data table */}
        {!logsLoading && !logsError && logsData && logsData.logs.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-2.5 text-right text-xs font-medium text-gray-500 whitespace-nowrap">
                    التاريخ / الوقت
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-medium text-gray-500">
                    الحقل
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-medium text-gray-500 whitespace-nowrap">
                    القمر الصناعي
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-medium text-gray-500 whitespace-nowrap">
                    الغطاء ☁️
                  </th>
                  <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500">
                    NDVI
                  </th>
                  <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500">
                    EVI
                  </th>
                  <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500">
                    LAI
                  </th>
                  <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500">
                    NDWI
                  </th>
                  <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500">
                    الحالة
                  </th>
                  <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500">
                    ملف
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {logsData.logs.map((entry: SchedulerLogEntry) => {
                  const sc = STATUS_CONFIG[entry.status];
                  return (
                    <tr key={entry.id} className="hover:bg-gray-50 transition-colors">
                      {/* Date/Time */}
                      <td className="px-4 py-2.5 whitespace-nowrap">
                        <div className="text-xs font-mono text-gray-700">
                          {formatDateTimeEn(entry.acquisitionDate)}
                        </div>
                        {entry.processedAt && (
                          <div className="text-[10px] text-gray-400">
                            ✓ {formatDateTimeEn(entry.processedAt)}
                          </div>
                        )}
                      </td>

                      {/* Field */}
                      <td className="px-4 py-2.5">
                        <div className="font-medium text-gray-900 text-xs">
                          {entry.fieldNameAr || entry.fieldName}
                        </div>
                        <div className="text-[10px] text-gray-400 font-mono">
                          {entry.fieldId.slice(0, 8)}…
                        </div>
                      </td>

                      {/* Satellite */}
                      <td className="px-4 py-2.5">
                        <span className="text-xs text-gray-600 font-mono">{entry.satellite}</span>
                      </td>

                      {/* Cloud cover */}
                      <td className="px-4 py-2.5 text-right">
                        <span
                          className={`text-xs font-medium ${
                            entry.cloudCoverPercent > 50
                              ? 'text-red-500'
                              : entry.cloudCoverPercent > 30
                              ? 'text-yellow-600'
                              : 'text-green-600'
                          }`}
                        >
                          {entry.cloudCoverPercent.toFixed(1)}%
                        </span>
                      </td>

                      {/* Indices */}
                      <td className="px-4 py-2.5 text-center">
                        <IndexCell val={entry.indices.ndvi} />
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        <IndexCell val={entry.indices.evi} />
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        <IndexCell val={entry.indices.lai} />
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        <IndexCell val={entry.indices.ndwi} />
                      </td>

                      {/* Status */}
                      <td className="px-4 py-2.5 text-center">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${sc.color} ${sc.bg}`}
                        >
                          {sc.icon}
                          {sc.labelAr}
                        </span>
                        {entry.retryCount > 0 && (
                          <div className="text-[10px] text-gray-400 mt-0.5">
                            {entry.retryCount} محاولة
                          </div>
                        )}
                        {entry.errorMessage && (
                          <div
                            className="text-[10px] text-red-400 mt-0.5 max-w-[140px] truncate"
                            title={entry.errorMessage}
                          >
                            {entry.errorMessage}
                          </div>
                        )}
                      </td>

                      {/* GeoTIFF link */}
                      <td className="px-4 py-2.5 text-center">
                        {entry.geotiffUrl ? (
                          <a
                            href={entry.geotiffUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
                          >
                            <ExternalLink className="w-3 h-3" />
                            GeoTIFF
                          </a>
                        ) : (
                          <span className="text-gray-300 text-xs">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* ── Pagination ───────────────────────────────────────────────────── */}
        {!logsLoading && logsData && logsData.total > PAGE_LIMIT && (
          <div className="px-4 py-3 border-t flex items-center justify-between text-sm text-gray-600">
            <div>
              عرض {((page - 1) * PAGE_LIMIT + 1).toLocaleString()}–
              {Math.min(page * PAGE_LIMIT, logsData.total).toLocaleString()} من{' '}
              {logsData.total.toLocaleString()}
            </div>
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 rounded border bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                aria-label="Previous page"
              >
                <ChevronRight className="w-4 h-4" />
              </button>

              {/* Page numbers — show max 5 around current */}
              {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                const start = Math.max(1, Math.min(page - 2, totalPages - 4));
                const p = start + i;
                return (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setPage(p)}
                    className={`min-w-[32px] h-8 px-2 rounded border text-xs transition-colors ${
                      p === page
                        ? 'bg-green-600 text-white border-green-600'
                        : 'bg-white hover:bg-gray-50'
                    }`}
                  >
                    {p}
                  </button>
                );
              })}

              <button
                type="button"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-1.5 rounded border bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                aria-label="Next page"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ── Footer note ────────────────────────────────────────────────────── */}
      <p className="text-xs text-gray-400 text-center">
        يتم الجلب يومياً الساعة 00:00 · يُعاد المحاولة في 06:00 و 12:00 · البيانات من Sentinel-2 L2A عبر CDSE
      </p>
    </div>
  );
}
