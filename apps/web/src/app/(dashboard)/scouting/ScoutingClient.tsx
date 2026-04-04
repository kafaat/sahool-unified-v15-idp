'use client';

/**
 * Scouting Client Component
 * مكون الاستكشاف الميداني
 */

import React, { useState } from 'react';
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
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Mock Data
// ---------------------------------------------------------------------------

const STATS = [
  { label: 'مستكشفون نشطون', value: 23, icon: Users, color: 'blue' },
  { label: 'تقارير اليوم', value: 47, icon: FileText, color: 'green' },
  { label: 'مشاكل مكتشفة', value: 12, icon: AlertTriangle, color: 'red' },
  { label: 'حقول مغطاة', value: 38, icon: Map, color: 'purple' },
];

const TABS = [
  { id: 'active', label: 'الجولات النشطة', icon: Eye },
  { id: 'history', label: 'السجل', icon: Calendar },
  { id: 'issues', label: 'المشاكل', icon: AlertTriangle },
] as const;

type TabId = (typeof TABS)[number]['id'];

const ACTIVE_SESSIONS = [
  { id: 's1', scout: 'أحمد محمد', field: 'حقل القمح الشمالي', startTime: '07:30', observations: 5, issues: 1, status: 'active' },
  { id: 's2', scout: 'علي حسن', field: 'بستان النخيل', startTime: '08:15', observations: 3, issues: 0, status: 'active' },
  { id: 's3', scout: 'محمد عبدالله', field: 'حقل الطماطم', startTime: '06:45', observations: 8, issues: 2, status: 'active' },
];

const RECENT_ISSUES = [
  { id: 'i1', type: 'pest', label: 'حشرة المن', field: 'حقل القمح', severity: 'high', date: '2026-04-03', status: 'open' },
  { id: 'i2', type: 'disease', label: 'صدأ الأوراق', field: 'حقل الشعير', severity: 'critical', date: '2026-04-02', status: 'open' },
  { id: 'i3', type: 'nutrient', label: 'نقص النيتروجين', field: 'حقل القمح الشمالي', severity: 'medium', date: '2026-04-01', status: 'resolved' },
  { id: 'i4', type: 'water', label: 'جفاف جزئي', field: 'حقل الذرة', severity: 'high', date: '2026-03-31', status: 'open' },
  { id: 'i5', type: 'pest', label: 'دودة الحشد', field: 'حقل الذرة الرفيعة', severity: 'critical', date: '2026-03-30', status: 'in_progress' },
];

const HISTORY = [
  { id: 'h1', scout: 'أحمد محمد', field: 'حقل القمح', date: '2026-04-02', observations: 12, issues: 2, duration: '2:30 ساعة' },
  { id: 'h2', scout: 'علي حسن', field: 'بستان النخيل', date: '2026-04-01', observations: 8, issues: 0, duration: '1:45 ساعة' },
  { id: 'h3', scout: 'سارة أحمد', field: 'حقل الطماطم', date: '2026-03-31', observations: 15, issues: 3, duration: '3:00 ساعة' },
];

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
                  <p className="text-2xl font-bold text-gray-900">{s.value}</p>
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
          {ACTIVE_SESSIONS.map((session) => (
            <div key={session.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                    <Eye className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="font-bold text-gray-900">{session.scout}</p>
                    <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                      <MapPin className="w-3 h-3" />
                      <span>{session.field}</span>
                      <Clock className="w-3 h-3 mr-2" />
                      <span>بدأ {session.startTime}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1 text-gray-600">
                    <Camera className="w-4 h-4" />
                    <span>{session.observations} ملاحظة</span>
                  </div>
                  {session.issues > 0 && (
                    <div className="flex items-center gap-1 text-red-600">
                      <AlertTriangle className="w-4 h-4" />
                      <span>{session.issues} مشكلة</span>
                    </div>
                  )}
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                    نشط
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
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
              {HISTORY.map((h) => (
                <tr key={h.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="p-4 font-medium text-gray-900">{h.scout}</td>
                  <td className="p-4 text-gray-600">{h.field}</td>
                  <td className="p-4 text-gray-600">{h.date}</td>
                  <td className="p-4 text-gray-600">{h.observations}</td>
                  <td className="p-4">
                    <span className={h.issues > 0 ? 'text-red-600 font-medium' : 'text-green-600'}>
                      {h.issues}
                    </span>
                  </td>
                  <td className="p-4 text-gray-600">{h.duration}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Issues Tab */}
      {activeTab === 'issues' && (
        <div className="space-y-3">
          {RECENT_ISSUES.map((issue) => (
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
