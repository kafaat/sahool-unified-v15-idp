'use client';

// Users Management Page - Dynamic with Full CRUD
// صفحة إدارة المستخدمين - ديناميكية مع جميع عمليات CRUD

import { useEffect, useState, useMemo, useCallback } from 'react';
import { useToast } from '@/components/ui/Toast';
import Header from '@/components/layout/Header';
import StatusBadge from '@/components/ui/StatusBadge';
import DataTable from '@/components/ui/DataTable';
import { formatDate, cn } from '@/lib/utils';
import { t } from '@/lib/i18n';
import {
  Users,
  Search,
  Plus,
  RefreshCw,
  Download,
  Eye,
  Edit,
  Trash2,
  Shield,
  UserCheck,
  UserX,
  X,
  Save,
} from 'lucide-react';
import { logger } from '../../lib/logger';
import {
  userService,
  type User as ApiUser,
  type CreateUserData,
  type UpdateUserData,
} from '@/lib/api';
import { useAuth } from '@/stores/auth.store';

// Extended User interface for UI
interface User extends Omit<ApiUser, 'role'> {
  nameAr?: string;
  farmCount?: number;
  lastLogin?: string;
  avatar?: string;
  role: 'admin' | 'manager' | 'farmer' | 'researcher' | 'expert' | 'viewer';
}

export default function UsersPage() {
  const { toast } = useToast();
  const { user: authUser } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [debouncedSearch, setDebouncedSearch] = useState(searchQuery);

  // Debounce search input to avoid API call on every keystroke
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchQuery), 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const loadUsers = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await userService.getAll({
        page,
        limit: 20,
        search: debouncedSearch || undefined,
        role: roleFilter || undefined,
        status: statusFilter || undefined,
      });

      // Map API users to UI format
      const mappedUsers: User[] = response.data.map((user) => ({
        ...user,
        nameAr: user.name,
        farmCount: user.farmCount ?? 0,
        lastLogin: user.lastLogin ?? '',
      }));

      setUsers(mappedUsers);
      setTotalPages(response.meta.totalPages);
    } catch (error) {
      logger.error('Failed to load users:', error);
      setUsers([]);
    } finally {
      setIsLoading(false);
    }
  }, [page, roleFilter, statusFilter, debouncedSearch]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  // CRUD Handlers
  async function handleCreate(data: Omit<CreateUserData, 'tenantId'>) {
    setIsSubmitting(true);
    try {
      // Inject tenant ID from authenticated admin's context
      if (!authUser?.tenant_id) {
        toast.error('Tenant ID not available', 'معرّف المستأجر غير متوفر. يرجى تسجيل الدخول مجدداً.');
        return;
      }
      await userService.create({ ...data, tenantId: authUser.tenant_id });
      await loadUsers();
      setShowCreateModal(false);
      logger.info('User created successfully');
    } catch (error) {
      logger.error('Failed to create user:', error);
      toast.error('Failed to create user', 'فشل إنشاء المستخدم. يرجى المحاولة مرة أخرى.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUpdate(id: string, data: UpdateUserData) {
    setIsSubmitting(true);
    try {
      await userService.update(id, data);
      await loadUsers();
      setShowEditModal(false);
      setSelectedUser(null);
      logger.info('User updated successfully');
    } catch (error) {
      logger.error('Failed to update user:', error);
      toast.error('Failed to update user', 'فشل تحديث المستخدم. يرجى المحاولة مرة أخرى.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(id: string) {
    setIsSubmitting(true);
    try {
      await userService.delete(id);
      await loadUsers();
      setShowDeleteModal(false);
      setSelectedUser(null);
      logger.info('User deleted successfully');
    } catch (error) {
      logger.error('Failed to delete user:', error);
      toast.error('Failed to delete user', 'فشل حذف المستخدم. يرجى المحاولة مرة أخرى.');
    } finally {
      setIsSubmitting(false);
    }
  }

  const filteredUsers = useMemo(() => {
    // Search already handled in API call
    return users;
  }, [users]);

  const stats = useMemo(
    () => ({
      total: users.length,
      active: users.filter((u) => u.status === 'active').length,
      farmers: users.filter((u) => u.role === 'farmer').length,
      pending: users.filter((u) => u.status === 'pending').length,
    }),
    [users]
  );

  const getRoleLabel = (role: User['role']) => {
    const labels: Record<User['role'], string> = {
      admin: 'مدير',
      manager: 'مشرف',
      expert: 'خبير',
      farmer: 'مزارع',
      researcher: 'باحث',
      viewer: 'مشاهد',
    };
    return labels[role];
  };

  const getRoleColor = (role: User['role']) => {
    const colors: Record<User['role'], string> = {
      admin: 'bg-purple-100 text-purple-800',
      manager: 'bg-indigo-100 text-indigo-800',
      expert: 'bg-blue-100 text-blue-800',
      farmer: 'bg-green-100 text-green-800',
      researcher: 'bg-teal-100 text-teal-800',
      viewer: 'bg-gray-100 text-gray-800',
    };
    return colors[role];
  };

  const columns = [
    {
      key: 'name',
      header: 'المستخدم',
      render: (user: User) => (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-sahool-100 rounded-full flex items-center justify-center">
            <Users className="w-5 h-5 text-sahool-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900 dark:text-gray-100">{user.nameAr}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">{user.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'phone',
      header: 'الهاتف',
      render: (user: User) => (
        <span className="text-gray-700 dark:text-gray-300 text-sm" dir="ltr">
          {user.phone}
        </span>
      ),
    },
    {
      key: 'role',
      header: 'الدور',
      render: (user: User) => (
        <span className={cn('px-2 py-1 rounded-full text-xs font-medium', getRoleColor(user.role))}>
          {getRoleLabel(user.role)}
        </span>
      ),
    },
    {
      key: 'farmCount',
      header: t('nav.farms'),
      render: (user: User) => (
        <span className="text-gray-700 dark:text-gray-300">{user.farmCount}</span>
      ),
    },
    {
      key: 'status',
      header: t('farms.status'),
      render: (user: User) => <StatusBadge status={user.status} />,
    },
    {
      key: 'lastLogin',
      header: 'آخر دخول',
      render: (user: User) => (
        <span className="text-gray-500 dark:text-gray-400 text-sm">
          {user.lastLogin ? formatDate(user.lastLogin) : 'لم يسجل دخول'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (user: User) => (
        <div className="flex items-center gap-1">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedUser(user);
              setShowEditModal(true);
            }}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="عرض التفاصيل"
          >
            <Eye className="w-4 h-4 text-gray-500" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedUser(user);
              setShowEditModal(true);
            }}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title={t('common.edit')}
          >
            <Edit className="w-4 h-4 text-blue-500" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedUser(user);
              setShowDeleteModal(true);
            }}
            className="p-2 hover:bg-red-50 rounded-lg transition-colors"
            title={t('common.delete')}
          >
            <Trash2 className="w-4 h-4 text-red-500" />
          </button>
        </div>
      ),
      className: 'w-32',
    },
  ];

  return (
    <div className="p-6">
      <Header title={t('nav.users')} subtitle={`${users.length} مستخدم مسجل`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي المستخدمين</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <UserCheck className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.active}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">نشط</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-100 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-sahool-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.farmers}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">مزارع</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <UserX className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.pending}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">في الانتظار</p>
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
              placeholder={`${t('common.search')}...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الأدوار</option>
            <option value="admin">مدير</option>
            <option value="expert">خبير</option>
            <option value="farmer">مزارع</option>
            <option value="viewer">مشاهد</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="active">نشط</option>
            <option value="inactive">غير نشط</option>
            <option value="suspended">موقوف</option>
            <option value="pending">في الانتظار</option>
          </select>

          <button
            onClick={loadUsers}
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
            title={t('common.export')}
          >
            <Download className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            {t('common.add')}
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6">
        {isLoading ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-8">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ))}
            </div>
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={filteredUsers}
            keyExtractor={(user) => user.id}
            onRowClick={(user) => setSelectedUser(user)}
            emptyMessage="لا يوجد مستخدمين مطابقين للبحث"
          />
        )}
      </div>

      {/* Create User Modal */}
      {showCreateModal && (
        <UserFormModal
          title="إضافة مستخدم جديد"
          onClose={() => setShowCreateModal(false)}
          onSubmit={(data) => handleCreate(data as Omit<CreateUserData, 'tenantId'>)}
          isSubmitting={isSubmitting}
        />
      )}

      {/* Edit User Modal */}
      {showEditModal && selectedUser && (
        <UserFormModal
          title="تعديل المستخدم"
          user={selectedUser}
          onClose={() => {
            setShowEditModal(false);
            setSelectedUser(null);
          }}
          onSubmit={(data) => handleUpdate(selectedUser.id, data)}
          isSubmitting={isSubmitting}
        />
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && selectedUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full">
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              {t('common.confirm')}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              هل أنت متأكد من حذف المستخدم{' '}
              <strong>{selectedUser.nameAr || selectedUser.name}</strong>؟ هذا الإجراء لا يمكن
              التراجع عنه.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setSelectedUser(null);
                }}
                disabled={isSubmitting}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={() => handleDelete(selectedUser.id)}
                disabled={isSubmitting}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {isSubmitting ? `${t('common.loading')}` : t('common.delete')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {t('common.previous')}
          </button>
          <span className="px-4 py-2 text-gray-600 dark:text-gray-400">
            صفحة {page} من {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {t('common.next')}
          </button>
        </div>
      )}
    </div>
  );
}

// User Form Modal Component
function UserFormModal({
  title,
  user,
  onClose,
  onSubmit,
  isSubmitting,
}: {
  title: string;
  user?: User;
  onClose: () => void;
  onSubmit: (data: Omit<CreateUserData, 'tenantId'> | UpdateUserData) => void;
  isSubmitting: boolean;
}) {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    role: user?.role || ('farmer' as User['role']),
    status: user?.status || ('active' as User['status']),
    password: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!user) {
      // Create mode - password required
      if (!formData.password) {
        toast.warning('Please enter a password', 'يرجى إدخال كلمة المرور');
        return;
      }
      onSubmit(formData as Omit<CreateUserData, 'tenantId'>);
    } else {
      // Edit mode - password optional
      const updateData: UpdateUserData = {
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        role: formData.role,
        status: formData.status,
      };
      onSubmit(updateData);
    }
  };

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{title}</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              الاسم
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              البريد الإلكتروني
            </label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              رقم الهاتف
            </label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
              dir="ltr"
            />
          </div>

          {!user && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                كلمة المرور
              </label>
              <input
                type="password"
                required
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
                minLength={8}
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              الدور
            </label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value as User['role'] })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
            >
              <option value="farmer">مزارع</option>
              <option value="expert">خبير</option>
              <option value="manager">مدير</option>
              <option value="admin">مسؤول</option>
              <option value="viewer">مشاهد</option>
              <option value="researcher">باحث</option>
            </select>
          </div>

          {user && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                الحالة
              </label>
              <select
                value={formData.status}
                onChange={(e) =>
                  setFormData({ ...formData, status: e.target.value as User['status'] })
                }
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
              >
                <option value="active">نشط</option>
                <option value="inactive">غير نشط</option>
                <option value="suspended">موقوف</option>
                <option value="pending">في الانتظار</option>
              </select>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
            >
              {t('common.cancel')}
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Save className="w-4 h-4" />
              {isSubmitting ? t('common.loading') : user ? t('common.save') : t('common.add')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
