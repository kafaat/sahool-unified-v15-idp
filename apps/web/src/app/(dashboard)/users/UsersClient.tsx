'use client';

import React, { useState, useMemo } from 'react';
import {
  Users,
  Plus,
  Search,
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  UserX,
} from 'lucide-react';
import { useUsers, useUserStats } from '@/features/users';
import type { UserRole, UserStatus } from '@/features/users';

const roles: Array<{ value: UserRole | 'all'; label: string; labelAr: string }> = [
  { value: 'all', label: 'All Roles', labelAr: 'جميع الأدوار' },
  { value: 'admin', label: 'Admin', labelAr: 'مدير' },
  { value: 'manager', label: 'Manager', labelAr: 'مشرف' },
  { value: 'farmer', label: 'Farmer', labelAr: 'مزارع' },
  { value: 'agronomist', label: 'Agronomist', labelAr: 'مهندس زراعي' },
  { value: 'viewer', label: 'Viewer', labelAr: 'مشاهد' },
];

const statusConfig: Record<
  UserStatus,
  { color: string; labelAr: string; icon: React.ElementType }
> = {
  active: { color: 'bg-green-100 text-green-800', labelAr: 'نشط', icon: CheckCircle },
  inactive: { color: 'bg-gray-100 text-gray-800', labelAr: 'غير نشط', icon: UserX },
  suspended: { color: 'bg-red-100 text-red-800', labelAr: 'موقوف', icon: AlertTriangle },
  pending: { color: 'bg-yellow-100 text-yellow-800', labelAr: 'معلق', icon: Clock },
};

const roleLabelsAr: Record<UserRole, string> = {
  admin: 'مدير النظام',
  manager: 'مشرف',
  farmer: 'مزارع',
  viewer: 'مشاهد',
  agronomist: 'مهندس زراعي',
};

export default function UsersClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState<UserRole | 'all'>('all');

  const {
    data: users = [],
    isLoading,
    error,
  } = useUsers(selectedRole !== 'all' ? { role: selectedRole } : undefined);
  const { data: stats } = useUserStats();

  const filteredUsers = useMemo(() => {
    if (!searchTerm) return users;
    const term = searchTerm.toLowerCase();
    return users.filter(
      (u) =>
        u.name.toLowerCase().includes(term) ||
        u.nameAr.includes(searchTerm) ||
        u.email.toLowerCase().includes(term)
    );
  }, [users, searchTerm]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sahool-green-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">فشل في تحميل بيانات المستخدمين</p>
          <p className="text-gray-500 text-sm">Failed to load users data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة المستخدمين</h1>
          <p className="text-gray-500 mt-1">User Management</p>
        </div>
        <button
          disabled
          title="قريباً - Coming soon"
          className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus className="w-4 h-4" />
          <span>إضافة مستخدم</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">إجمالي المستخدمين</div>
          <div className="text-2xl font-bold text-gray-900">
            {stats?.totalUsers ?? users.length}
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">نشطون</div>
          <div className="text-2xl font-bold text-green-600">{stats?.activeUsers ?? 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">مديرون</div>
          <div className="text-2xl font-bold text-blue-600">{stats?.admins ?? 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">مزارعون</div>
          <div className="text-2xl font-bold text-sahool-green-600">{stats?.farmers ?? 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">في الانتظار</div>
          <div className="text-2xl font-bold text-yellow-600">{stats?.pendingApprovals ?? 0}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث بالاسم أو البريد..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-sahool-green-500"
          />
        </div>
        <select
          value={selectedRole}
          onChange={(e) => setSelectedRole(e.target.value as UserRole | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {roles.map((r) => (
            <option key={r.value} value={r.value}>
              {r.labelAr}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">المستخدم</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الدور</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحالة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">المزارع</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">آخر دخول</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">2FA</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                  الإجراءات
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                    لا يوجد مستخدمون
                  </td>
                </tr>
              ) : (
                filteredUsers.map((user) => {
                  const st = statusConfig[user.status];
                  const StIcon = st.icon;
                  return (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-sahool-green-100 rounded-full flex items-center justify-center">
                            <Users className="w-5 h-5 text-sahool-green-600" />
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{user.nameAr}</div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center gap-1 text-sm">
                          <Shield className="w-3.5 h-3.5 text-gray-400" />
                          {roleLabelsAr[user.role]}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${st.color}`}
                        >
                          <StIcon className="w-3 h-3" />
                          {st.labelAr}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{user.farmIds.length}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {user.lastLogin
                          ? new Date(user.lastLogin).toLocaleDateString('ar-SA')
                          : '—'}
                      </td>
                      <td className="px-4 py-3">
                        {user.twoFactorEnabled ? (
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        ) : (
                          <span className="text-xs text-gray-400">غير مفعل</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <button className="text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium">
                          تعديل
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
