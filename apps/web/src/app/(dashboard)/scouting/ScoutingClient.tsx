'use client';

/**
 * Scouting Client Component
 * مكون الاستكشاف الميداني
 */

import React, { useState, useMemo } from 'react';
import {
  Users,
  FileText,
  AlertTriangle,
  Map,
  Eye,
  Calendar,
  MapPin,
  Camera,
  Bug,
  Leaf,
  Clock,
  Loader2,
} from 'lucide-react';
import { useScoutingStatistics, useScoutingHistory } from '@/features/scouting';
import type { ScoutingSession } from '@/features/scouting';

const TABS = [
  { id: 'active', label: 'الجولات النشطة', icon: Eye },
  { id: 'history', label: 'السجل', icon: Calendar },
  { id: 'issues', label: 'المشاكل', icon: AlertTriangle },
] as const;

type TabId = (typeof TABS)[number]['id'];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const SEVERITY_STYLES: Record<string, string> = {
  critical: 'bg-red-100 text-red-700',
  high: 'bg-orange-100 text-orange-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-green-100 text-green-700',
};

const SEVERITY_LABELS: Record<string, string> = {
  critical: 'حرج',
  high: 'مرتفع',
  medium: 'متوسط',
  low: 'منخفض',
};

const STATUS_LABELS: Record<string, string> = {
  open: 'مفتوح',
  in_progress: 'قيد المعالجة',
  resolved: 'تم الحل',
};

const STAT_COLORS: Record<string, { bg: string; icon: string }> = {
  blue: { bg: 'bg-blue-100', icon: 'text-blue-600' },
  green: { bg: 'bg-green-100', icon: 'text-green-600' },
  red: { bg: 'bg-red-100', icon: 'text-red-600' },
  purple: { bg: 'bg-purple-100', icon: 'text-purple-600' },
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ScoutingClient() {
  const [activeTab, setActiveTab] = useState<TabId>('active');

  const { data: statistics, isLoading: statsLoading, error: statsError, refetch: refetchStats } = useScoutingStatistics();
  const { data: activeSessions, isLoading: activeLoading, error: activeError, refetch: refetchActive } = useScoutingHistory({ status: 'active' });
  const { data: completedSessions, isLoading: historyLoading, error: historyError, refetch: refetchHistory } = useScoutingHistory({ status: 'completed' });

  // Derive issues from all sessions' observations with high severity
  const recentIssues = useMemo(() => {
    if (!activeSessions) return [];
    return activeSessions
      .filter((s: ScoutingSession) => (s.averageSeverity ?? 0) >= 3)
      .map((s: ScoutingSession) => ({
        id: s.id,
        type: s.categoryCounts ? (Object.entries(s.categoryCounts).sort(([, a], [, b]) => b - a)[0]?.[0] ?? 'other') : 'other',
        label: s.fieldNameAr || s.fieldName,
        field: s.fieldNameAr || s.fieldName,
        severity: (s.averageSeverity ?? 0) >= 4 ? 'critical' : (s.averageSeverity ?? 0) >= 3 ? 'high' : 'medium',
        date: s.createdAt?.slice(0, 10) ?? '',
        status: s.status === 'active' ? 'open' : s.status === 'completed' ? 'resolved' : 'in_progress',
      }));
  }, [activeSessions]);

  const STATS = [
    { label: 'مستكشفون نشطون', value: activeSessions?.length ?? 0, icon: Users, color: 'blue' },
    { label: 'تقارير اليوم', value: statistics?.totalObservations ?? 0, icon: FileText, color: 'green' },
    { label: 'مشاكل مكتشفة', value: recentIssues.length, icon: AlertTriangle, color: 'red' },
    { label: 'حقول مغطاة', value: statistics?.sessionsThisMonth ?? 0, icon: Map, color: 'purple' },
  ];

  const isLoading = statsLoading || activeLoading || historyLoading;
  const error = statsError || activeError || historyError;

  if (error) {
    const handleRetry = () => {
      refetchStats();
      refetchActive();
      refetchHistory();
    };
    return (
      <div dir="rtl" className="min-h-screen bg-gray-50 p-6">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
          <p className="text-red-700 font-medium">فشل في تحميل بيانات الاستكشاف</p>
          <p className="text-red-500 text-sm mt-1">Failed to load scouting data</p>
          <button
            type="button"
            onClick={handleRetry}
            className="mt-4 inline-flex items-center gap-2 px-4 py-2 text-sm font-medium bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <span>إعادة المحاولة</span>
            <span className="text-xs opacity-80">| Retry</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">الاستكشاف الميداني</h1>
        <p className="text-sm text-gray-500 mt-1">جولات الفحص الميداني وتتبع المشاكل الزراعية</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {STATS.map((s) => {
          const Icon = s.icon;
          const colors = (STAT_COLORS[s.color] ?? STAT_COLORS.blue)!;
          return (
            <div key={s.label} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 ${colors.bg} rounded-lg flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 ${colors.icon}`} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{isLoading ? '...' : s.value}</p>
                  <p className="text-sm text-gray-500">{s.label}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm rounded-md transition-colors ${
                activeTab === tab.id
                  ? 'bg-white text-green-700 shadow-sm font-medium'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Active Sessions Tab */}
      {activeTab === 'active' && (
        <div className="space-y-4">
          {activeLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-green-600" />
              <span className="mr-2 text-gray-500">جاري التحميل...</span>
            </div>
          )}
          {!activeLoading && (!activeSessions || activeSessions.length === 0) && (
            <div className="bg-white rounded-xl p-10 shadow-sm border border-gray-100 text-center text-gray-500">
              لا توجد جولات نشطة حالياً
            </div>
          )}
          {activeSessions?.map((session: ScoutingSession) => {
            const criticalCount = session.severityDistribution
              ? (session.severityDistribution[4] ?? 0) + (session.severityDistribution[5] ?? 0)
              : 0;
            return (
              <div key={session.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <Eye className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <p className="font-bold text-gray-900">{session.scoutName ?? session.scoutId}</p>
                      <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                        <MapPin className="w-3 h-3" />
                        <span>{session.fieldNameAr || session.fieldName}</span>
                        <Clock className="w-3 h-3 mr-2" />
                        <span>بدأ {new Date(session.startTime).toLocaleTimeString('ar-SA', { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1 text-gray-600">
                      <Camera className="w-4 h-4" />
                      <span>{session.observationsCount} ملاحظة</span>
                    </div>
                    {criticalCount > 0 && (
                      <div className="flex items-center gap-1 text-red-600">
                        <AlertTriangle className="w-4 h-4" />
                        <span>{criticalCount} مشكلة</span>
                      </div>
                    )}
                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                      نشط
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          {historyLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-green-600" />
              <span className="mr-2 text-gray-500">جاري التحميل...</span>
            </div>
          )}
          {!historyLoading && (!completedSessions || completedSessions.length === 0) && (
            <div className="p-10 text-center text-gray-500">لا يوجد سجل جلسات سابقة</div>
          )}
          {!historyLoading && completedSessions && completedSessions.length > 0 && (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-right p-4 font-medium text-gray-600">المستكشف</th>
                  <th className="text-right p-4 font-medium text-gray-600">الحقل</th>
                  <th className="text-right p-4 font-medium text-gray-600">التاريخ</th>
                  <th className="text-right p-4 font-medium text-gray-600">الملاحظات</th>
                  <th className="text-right p-4 font-medium text-gray-600">المشاكل</th>
                  <th className="text-right p-4 font-medium text-gray-600">المدة</th>
                </tr>
              </thead>
              <tbody>
                {completedSessions.map((h: ScoutingSession) => {
                  const criticalCount = h.severityDistribution
                    ? (h.severityDistribution[4] ?? 0) + (h.severityDistribution[5] ?? 0)
                    : 0;
                  const durationMin = h.duration ?? 0;
                  const durationStr = durationMin > 0
                    ? `${Math.floor(durationMin / 60)}:${String(durationMin % 60).padStart(2, '0')} ساعة`
                    : '-';
                  return (
                    <tr key={h.id} className="border-b last:border-0 hover:bg-gray-50">
                      <td className="p-4 font-medium text-gray-900">{h.scoutName ?? h.scoutId}</td>
                      <td className="p-4 text-gray-600">{h.fieldNameAr || h.fieldName}</td>
                      <td className="p-4 text-gray-600">{h.createdAt?.slice(0, 10) ?? ''}</td>
                      <td className="p-4 text-gray-600">{h.observationsCount}</td>
                      <td className="p-4">
                        <span className={criticalCount > 0 ? 'text-red-600 font-medium' : 'text-green-600'}>
                          {criticalCount}
                        </span>
                      </td>
                      <td className="p-4 text-gray-600">{durationStr}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Issues Tab */}
      {activeTab === 'issues' && (
        <div className="space-y-3">
          {activeLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-green-600" />
              <span className="mr-2 text-gray-500">جاري التحميل...</span>
            </div>
          )}
          {!activeLoading && recentIssues.length === 0 && (
            <div className="bg-white rounded-xl p-10 shadow-sm border border-gray-100 text-center text-gray-500">
              لا توجد مشاكل مكتشفة حالياً
            </div>
          )}
          {recentIssues.map((issue) => (
            <div key={issue.id} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  issue.type === 'pest' ? 'bg-orange-100' : issue.type === 'disease' ? 'bg-red-100' : 'bg-yellow-100'
                }`}>
                  {issue.type === 'pest' ? <Bug className="w-5 h-5 text-orange-600" /> :
                   issue.type === 'disease' ? <Leaf className="w-5 h-5 text-red-600" /> :
                   <AlertTriangle className="w-5 h-5 text-yellow-600" />}
                </div>
                <div>
                  <p className="font-bold text-gray-900">{issue.label}</p>
                  <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                    <MapPin className="w-3 h-3" />
                    <span>{issue.field}</span>
                    <span className="text-gray-300">|</span>
                    <span>{issue.date}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${SEVERITY_STYLES[issue.severity] ?? ''}`}>
                  {SEVERITY_LABELS[issue.severity] ?? issue.severity}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  issue.status === 'resolved' ? 'bg-green-100 text-green-700' :
                  issue.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {STATUS_LABELS[issue.status] ?? issue.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
