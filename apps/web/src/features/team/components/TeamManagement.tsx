'use client';

/**
 * SAHOOL Team Management Page
 * صفحة إدارة الفريق
 */

import React, { useState } from 'react';
import {
  Users,
  UserPlus,
  Search,
  Filter,
  LayoutGrid,
  LayoutList,
  Shield,
  Edit,
  Trash2,
  AlertCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { MemberCard } from './MemberCard';
import { InviteMemberDialog } from './InviteMemberDialog';
import { PermissionsMatrix } from './PermissionsMatrix';
import { RoleSelector } from './RoleSelector';
import { useTeamMembers, useUpdateRole, useRemoveMember, useTeamStats } from '../hooks/useTeam';
import { TeamMember, Role, UserStatus, ROLE_CONFIGS } from '../types/team';

type ViewMode = 'grid' | 'table' | 'permissions';

export const TeamManagement: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<Role | ''>('');
  const [statusFilter, setStatusFilter] = useState<UserStatus | ''>('');
  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [editingMember, setEditingMember] = useState<TeamMember | null>(null);
  const [removingMember, setRemovingMember] = useState<TeamMember | null>(null);

  // Hooks
  const { data: members = [], isLoading, error } = useTeamMembers({
    search: searchQuery,
    role: roleFilter || undefined,
    status: statusFilter || undefined,
  });
  const { data: stats } = useTeamStats();
  const updateRoleMutation = useUpdateRole();
  const removeMemberMutation = useRemoveMember();

  // Handlers
  const handleEditRole = (member: TeamMember) => {
    setEditingMember(member);
  };

  const handleUpdateRole = async (role: Role) => {
    if (!editingMember) return;

    try {
      await updateRoleMutation.mutateAsync({
        userId: editingMember.id,
        role,
      });
      setEditingMember(null);
    } catch (error) {
      console.error('Failed to update role:', error);
    }
  };

  const handleRemove = (member: TeamMember) => {
    setRemovingMember(member);
  };

  const handleConfirmRemove = async () => {
    if (!removingMember) return;

    try {
      await removeMemberMutation.mutateAsync(removingMember.id);
      setRemovingMember(null);
    } catch (error) {
      console.error('Failed to remove member:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                إدارة الفريق
              </h1>
              <p className="text-gray-600">
                إدارة أعضاء الفريق والصلاحيات
              </p>
            </div>
            <Button
              variant="primary"
              onClick={() => setShowInviteDialog(true)}
              className="flex items-center gap-2"
            >
              <UserPlus className="w-5 h-5" />
              دعوة عضو جديد
            </Button>
          </div>

          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
              <div className="bg-white rounded-lg border-2 border-gray-200 p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Users className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
                    <div className="text-sm text-gray-600">إجمالي الأعضاء</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border-2 border-gray-200 p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Shield className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900">{stats.active}</div>
                    <div className="text-sm text-gray-600">نشط</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border-2 border-gray-200 p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <AlertCircle className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900">{stats.pending}</div>
                    <div className="text-sm text-gray-600">قيد الانتظار</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border-2 border-gray-200 p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Users className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900">{stats.byRole.ADMIN}</div>
                    <div className="text-sm text-gray-600">مدراء</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border-2 border-gray-200 p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Users className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900">{stats.byRole.MANAGER}</div>
                    <div className="text-sm text-gray-600">مدراء فريق</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Filters & View Mode */}
          <div className="bg-white rounded-lg border-2 border-gray-200 p-4">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="ابحث عن عضو..."
                  className="w-full pr-10 px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
                />
              </div>

              {/* Role Filter */}
              <div className="w-full md:w-48">
                <select
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value as Role | '')}
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
                >
                  <option value="">كل الأدوار</option>
                  {Object.values(Role).map((role) => (
                    <option key={role} value={role}>
                      {ROLE_CONFIGS[role].nameAr}
                    </option>
                  ))}
                </select>
              </div>

              {/* Status Filter */}
              <div className="w-full md:w-48">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as UserStatus | '')}
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
                >
                  <option value="">كل الحالات</option>
                  <option value="ACTIVE">نشط</option>
                  <option value="PENDING">قيد الانتظار</option>
                  <option value="INACTIVE">غير نشط</option>
                  <option value="SUSPENDED">موقوف</option>
                </select>
              </div>

              {/* View Mode Toggles */}
              <div className="flex items-center gap-2 border-2 border-gray-200 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded transition-colors ${
                    viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                  title="عرض الشبكة"
                >
                  <LayoutGrid className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setViewMode('table')}
                  className={`p-2 rounded transition-colors ${
                    viewMode === 'table' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                  title="عرض الجدول"
                >
                  <LayoutList className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setViewMode('permissions')}
                  className={`p-2 rounded transition-colors ${
                    viewMode === 'permissions' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                  title="مصفوفة الصلاحيات"
                >
                  <Shield className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">جاري تحميل أعضاء الفريق...</p>
            </div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6 text-center">
            <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-3" />
            <p className="text-red-700">فشل في تحميل أعضاء الفريق</p>
          </div>
        ) : viewMode === 'permissions' ? (
          <PermissionsMatrix selectedRole={roleFilter || undefined} />
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {members.map((member) => (
              <MemberCard
                key={member.id}
                member={member}
                onEditRole={handleEditRole}
                onRemove={handleRemove}
              />
            ))}
          </div>
        ) : (
          // Table View
          <div className="bg-white rounded-lg border-2 border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b-2 border-gray-200">
                  <tr>
                    <th className="px-6 py-4 text-right text-sm font-bold text-gray-700">العضو</th>
                    <th className="px-6 py-4 text-right text-sm font-bold text-gray-700">البريد الإلكتروني</th>
                    <th className="px-6 py-4 text-right text-sm font-bold text-gray-700">الدور</th>
                    <th className="px-6 py-4 text-right text-sm font-bold text-gray-700">الحالة</th>
                    <th className="px-6 py-4 text-right text-sm font-bold text-gray-700">آخر نشاط</th>
                    <th className="px-6 py-4 text-center text-sm font-bold text-gray-700">الإجراءات</th>
                  </tr>
                </thead>
                <tbody>
                  {members.map((member, idx) => {
                    const roleConfig = ROLE_CONFIGS[member.role];
                    const formatLastActive = (date?: string) => {
                      if (!date) return 'لم يسجل دخول بعد';
                      const diffMinutes = Math.floor((new Date().getTime() - new Date(date).getTime()) / (1000 * 60));
                      if (diffMinutes < 60) return `منذ ${diffMinutes} دقيقة`;
                      if (diffMinutes < 1440) return `منذ ${Math.floor(diffMinutes / 60)} ساعة`;
                      return `منذ ${Math.floor(diffMinutes / 1440)} يوم`;
                    };

                    return (
                      <tr
                        key={member.id}
                        className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                              {member.firstName[0]}{member.lastName[0]}
                            </div>
                            <div>
                              <div className="font-semibold text-gray-900">
                                {member.firstName} {member.lastName}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-gray-600">{member.email}</td>
                        <td className="px-6 py-4">
                          <Badge className={roleConfig.color} size="sm">
                            {roleConfig.nameAr}
                          </Badge>
                        </td>
                        <td className="px-6 py-4">
                          <Badge
                            variant={
                              member.status === 'ACTIVE' ? 'success' :
                              member.status === 'PENDING' ? 'warning' : 'default'
                            }
                            size="sm"
                          >
                            {member.status === 'ACTIVE' ? 'نشط' :
                             member.status === 'PENDING' ? 'قيد الانتظار' : 'غير نشط'}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 text-gray-600 text-sm">
                          {formatLastActive(member.lastLoginAt)}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => handleEditRole(member)}
                              className="p-2 hover:bg-blue-100 rounded-lg transition-colors text-blue-600"
                              title="تعديل الدور"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleRemove(member)}
                              className="p-2 hover:bg-red-100 rounded-lg transition-colors text-red-600"
                              title="إزالة"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Invite Dialog */}
      <InviteMemberDialog
        isOpen={showInviteDialog}
        onClose={() => setShowInviteDialog(false)}
      />

      {/* Edit Role Dialog */}
      {editingMember && (
        <Modal
          isOpen={!!editingMember}
          onClose={() => setEditingMember(null)}
          title="Edit Member Role"
          titleAr="تعديل دور العضو"
          size="sm"
        >
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="font-semibold text-gray-900 mb-1">
                {editingMember.firstName} {editingMember.lastName}
              </div>
              <div className="text-sm text-gray-600">{editingMember.email}</div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                الدور الجديد
              </label>
              <RoleSelector
                value={editingMember.role}
                onChange={handleUpdateRole}
                disabled={updateRoleMutation.isPending}
              />
            </div>
          </div>

          <ModalFooter>
            <Button
              variant="ghost"
              onClick={() => setEditingMember(null)}
              disabled={updateRoleMutation.isPending}
            >
              إلغاء
            </Button>
          </ModalFooter>
        </Modal>
      )}

      {/* Remove Confirmation Dialog */}
      {removingMember && (
        <Modal
          isOpen={!!removingMember}
          onClose={() => setRemovingMember(null)}
          title="Remove Member"
          titleAr="إزالة عضو"
          size="sm"
        >
          <div className="space-y-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-6 h-6 text-red-600" />
                <div>
                  <div className="font-semibold text-red-900 mb-1">
                    هل أنت متأكد من إزالة هذا العضو؟
                  </div>
                  <div className="text-sm text-red-700">
                    لا يمكن التراجع عن هذا الإجراء
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="font-semibold text-gray-900 mb-1">
                {removingMember.firstName} {removingMember.lastName}
              </div>
              <div className="text-sm text-gray-600">{removingMember.email}</div>
            </div>
          </div>

          <ModalFooter>
            <Button
              variant="ghost"
              onClick={() => setRemovingMember(null)}
              disabled={removeMemberMutation.isPending}
            >
              إلغاء
            </Button>
            <Button
              variant="danger"
              onClick={handleConfirmRemove}
              isLoading={removeMemberMutation.isPending}
              disabled={removeMemberMutation.isPending}
            >
              <Trash2 className="w-4 h-4 ml-2" />
              {removeMemberMutation.isPending ? 'جاري الإزالة...' : 'إزالة'}
            </Button>
          </ModalFooter>
        </Modal>
      )}
    </div>
  );
};

export default TeamManagement;
