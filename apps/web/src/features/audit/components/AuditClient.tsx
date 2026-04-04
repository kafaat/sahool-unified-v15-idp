'use client';

import React, { useState, useMemo } from 'react';
import {
  Search,
  Shield,
  User,
  FileText,
  Download,
  AlertTriangle,
  Settings,
  LogIn,
  Trash2,
  Edit,
  Plus,
  Clock,
} from 'lucide-react';

type AuditAction = 'create' | 'update' | 'delete' | 'login' | 'logout' | 'export' | 'config_change';
type AuditSeverity = 'info' | 'warning' | 'critical';

interface AuditEntry {
  id: string;
  timestamp: string;
  userId: string;
  userName: string;
  action: AuditAction;
  resource: string;
  resourceAr: string;
  description: string;
  descriptionAr: string;
  severity: AuditSeverity;
  ipAddress: string;
  tenantId: string;
}

const mockAuditLog: AuditEntry[] = [
  {
    id: 'aud-001',
    timestamp: '2026-04-04T08:45:00Z',
    userId: 'user-1',
    userName: 'أحمد الرشيدي',
    action: 'create',
    resource: 'Field',
    resourceAr: 'حقل',
    description: 'Created field FIELD-012 "North Wheat Plot"',
    descriptionAr: 'إنشاء حقل FIELD-012 "قطعة القمح الشمالية"',
    severity: 'info',
    ipAddress: '192.168.1.45',
    tenantId: 'farm-001',
  },
  {
    id: 'aud-002',
    timestamp: '2026-04-04T08:30:00Z',
    userId: 'user-2',
    userName: 'فاطمة المنصور',
    action: 'config_change',
    resource: 'Irrigation',
    resourceAr: 'الري',
    description: 'Changed irrigation schedule for Field-003',
    descriptionAr: 'تغيير جدول الري للحقل 003',
    severity: 'warning',
    ipAddress: '192.168.1.22',
    tenantId: 'farm-001',
  },
  {
    id: 'aud-003',
    timestamp: '2026-04-04T08:15:00Z',
    userId: 'user-3',
    userName: 'خالد العمري',
    action: 'delete',
    resource: 'Sensor',
    resourceAr: 'حساس',
    description: 'Deleted sensor SNS-045 from Field-002',
    descriptionAr: 'حذف الحساس SNS-045 من الحقل 002',
    severity: 'critical',
    ipAddress: '10.0.0.15',
    tenantId: 'farm-001',
  },
  {
    id: 'aud-004',
    timestamp: '2026-04-04T07:50:00Z',
    userId: 'user-1',
    userName: 'أحمد الرشيدي',
    action: 'login',
    resource: 'Auth',
    resourceAr: 'المصادقة',
    description: 'User logged in via mobile app',
    descriptionAr: 'تسجيل دخول عبر تطبيق الجوال',
    severity: 'info',
    ipAddress: '192.168.1.45',
    tenantId: 'farm-001',
  },
  {
    id: 'aud-005',
    timestamp: '2026-04-04T07:30:00Z',
    userId: 'user-4',
    userName: 'سارة الحربي',
    action: 'export',
    resource: 'Report',
    resourceAr: 'تقرير',
    description: 'Exported monthly harvest report PDF',
    descriptionAr: 'تصدير تقرير الحصاد الشهري PDF',
    severity: 'info',
    ipAddress: '192.168.1.88',
    tenantId: 'farm-001',
  },
  {
    id: 'aud-006',
    timestamp: '2026-04-04T07:00:00Z',
    userId: 'system',
    userName: 'النظام',
    action: 'update',
    resource: 'Model',
    resourceAr: 'نموذج',
    description: 'Auto-deployed yolo26-pest-v3 to edge-001',
    descriptionAr: 'نشر تلقائي لنموذج yolo26-pest-v3 على الجهاز edge-001',
    severity: 'warning',
    ipAddress: '10.0.0.1',
    tenantId: 'farm-001',
  },
  {
    id: 'aud-007',
    timestamp: '2026-04-03T22:15:00Z',
    userId: 'user-5',
    userName: 'محمد القحطاني',
    action: 'config_change',
    resource: 'RBAC',
    resourceAr: 'الصلاحيات',
    description: 'Changed role permissions for "Field Worker" role',
    descriptionAr: 'تغيير صلاحيات دور "عامل الحقل"',
    severity: 'critical',
    ipAddress: '192.168.1.10',
    tenantId: 'farm-001',
  },
];

const actionIcons: Record<AuditAction, React.ReactNode> = {
  create: <Plus className="w-4 h-4" />,
  update: <Edit className="w-4 h-4" />,
  delete: <Trash2 className="w-4 h-4" />,
  login: <LogIn className="w-4 h-4" />,
  logout: <LogIn className="w-4 h-4" />,
  export: <Download className="w-4 h-4" />,
  config_change: <Settings className="w-4 h-4" />,
};

const actionLabels: Record<AuditAction, string> = {
  create: 'إنشاء',
  update: 'تحديث',
  delete: 'حذف',
  login: 'دخول',
  logout: 'خروج',
  export: 'تصدير',
  config_change: 'تغيير إعدادات',
};

export default function AuditClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState<AuditSeverity | 'all'>('all');
  const [actionFilter, setActionFilter] = useState<AuditAction | 'all'>('all');

  const filteredLogs = useMemo(() => {
    return mockAuditLog.filter((entry) => {
      const matchesSearch =
        !searchTerm ||
        entry.descriptionAr.includes(searchTerm) ||
        entry.userName.includes(searchTerm) ||
        entry.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesSeverity = severityFilter === 'all' || entry.severity === severityFilter;
      const matchesAction = actionFilter === 'all' || entry.action === actionFilter;
      return matchesSearch && matchesSeverity && matchesAction;
    });
  }, [searchTerm, severityFilter, actionFilter]);

  const getSeverityBadge = (severity: AuditSeverity) => {
    const styles: Record<AuditSeverity, string> = {
      info: 'bg-blue-100 text-blue-800',
      warning: 'bg-yellow-100 text-yellow-800',
      critical: 'bg-red-100 text-red-800',
    };
    const labels: Record<AuditSeverity, string> = {
      info: 'معلومات',
      warning: 'تحذير',
      critical: 'حرج',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[severity]}`}>
        {labels[severity]}
      </span>
    );
  };

  const getActionColor = (action: AuditAction) => {
    const colors: Record<AuditAction, string> = {
      create: 'bg-green-100 text-green-600',
      update: 'bg-blue-100 text-blue-600',
      delete: 'bg-red-100 text-red-600',
      login: 'bg-indigo-100 text-indigo-600',
      logout: 'bg-gray-100 text-gray-600',
      export: 'bg-purple-100 text-purple-600',
      config_change: 'bg-orange-100 text-orange-600',
    };
    return colors[action];
  };

  const criticalCount = mockAuditLog.filter((e) => e.severity === 'critical').length;

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">سجل التدقيق</h1>
          <p className="text-gray-500 mt-1">Audit Log</p>
        </div>
        <button
          disabled
          title="قريبا - Coming soon"
          className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          تصدير السجل
        </button>
      </div>

      {/* Critical alert */}
      {criticalCount > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="font-medium text-red-800">
              {criticalCount} إجراء حرج يتطلب مراجعة خلال الـ 24 ساعة الماضية
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي السجلات</div>
              <div className="text-xl font-bold text-gray-900">{mockAuditLog.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <User className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">مستخدمون نشطون</div>
              <div className="text-xl font-bold text-green-600">
                {new Set(mockAuditLog.map((e) => e.userId)).size}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجراءات حرجة</div>
              <div className="text-xl font-bold text-red-600">{criticalCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">آخر نشاط</div>
              <div className="text-sm font-bold text-purple-600">
                {new Date(mockAuditLog[0]!.timestamp).toLocaleTimeString('ar-SA')}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث في سجل التدقيق..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value as AuditSeverity | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
        >
          <option value="all">جميع المستويات</option>
          <option value="info">معلومات</option>
          <option value="warning">تحذير</option>
          <option value="critical">حرج</option>
        </select>
        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value as AuditAction | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
        >
          <option value="all">جميع الإجراءات</option>
          <option value="create">إنشاء</option>
          <option value="update">تحديث</option>
          <option value="delete">حذف</option>
          <option value="login">دخول</option>
          <option value="export">تصدير</option>
          <option value="config_change">تغيير إعدادات</option>
        </select>
      </div>

      {/* Audit Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-right px-4 py-3 font-medium text-gray-500">الوقت</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">المستخدم</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">الإجراء</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">المورد</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">الوصف</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">المستوى</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">IP</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredLogs.map((entry) => (
                <tr key={entry.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                    {new Date(entry.timestamp).toLocaleString('ar-SA', {
                      hour: '2-digit',
                      minute: '2-digit',
                      month: 'short',
                      day: 'numeric',
                    })}
                  </td>
                  <td className="px-4 py-3 font-medium text-gray-900">{entry.userName}</td>
                  <td className="px-4 py-3">
                    <div className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${getActionColor(entry.action)}`}>
                      {actionIcons[entry.action]}
                      {actionLabels[entry.action]}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-700">{entry.resourceAr}</td>
                  <td className="px-4 py-3 text-gray-600 max-w-xs truncate">{entry.descriptionAr}</td>
                  <td className="px-4 py-3">{getSeverityBadge(entry.severity)}</td>
                  <td className="px-4 py-3 text-gray-400 font-mono text-xs">{entry.ipAddress}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
