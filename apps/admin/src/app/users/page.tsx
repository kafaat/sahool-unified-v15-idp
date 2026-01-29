"use client";

// Users Management Page
// صفحة إدارة المستخدمين

import { useEffect, useState, useMemo } from "react";
import Header from "@/components/layout/Header";
import StatusBadge from "@/components/ui/StatusBadge";
import DataTable from "@/components/ui/DataTable";
import { formatDate, cn } from "@/lib/utils";
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
  Mail,
  Phone,
} from "lucide-react";
import { logger } from "../../lib/logger";

interface User {
  id: string;
  name: string;
  nameAr: string;
  email: string;
  phone: string;
  role: "admin" | "expert" | "farmer" | "viewer";
  status: "active" | "inactive" | "suspended" | "pending";
  farmCount: number;
  lastLogin: string;
  createdAt: string;
  avatar?: string;
}

// Mock data
const MOCK_USERS: User[] = [
  {
    id: "1",
    name: "Ahmed Al-Rashid",
    nameAr: "أحمد الراشد",
    email: "ahmed@example.com",
    phone: "+966501234567",
    role: "admin",
    status: "active",
    farmCount: 0,
    lastLogin: "2026-01-25T10:30:00",
    createdAt: "2024-01-15",
  },
  {
    id: "2",
    name: "Mohammed Saeed",
    nameAr: "محمد سعيد",
    email: "mohammed@example.com",
    phone: "+966502345678",
    role: "expert",
    status: "active",
    farmCount: 0,
    lastLogin: "2026-01-24T14:20:00",
    createdAt: "2024-03-10",
  },
  {
    id: "3",
    name: "Khalid Omar",
    nameAr: "خالد عمر",
    email: "khalid@example.com",
    phone: "+966503456789",
    role: "farmer",
    status: "active",
    farmCount: 3,
    lastLogin: "2026-01-25T08:00:00",
    createdAt: "2024-06-20",
  },
  {
    id: "4",
    name: "Ali Hassan",
    nameAr: "علي حسن",
    email: "ali@example.com",
    phone: "+966504567890",
    role: "farmer",
    status: "inactive",
    farmCount: 1,
    lastLogin: "2026-01-10T16:45:00",
    createdAt: "2024-08-05",
  },
  {
    id: "5",
    name: "Fatima Abdullah",
    nameAr: "فاطمة عبدالله",
    email: "fatima@example.com",
    phone: "+966505678901",
    role: "farmer",
    status: "pending",
    farmCount: 2,
    lastLogin: "",
    createdAt: "2026-01-20",
  },
];

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  useEffect(() => {
    loadUsers();
  }, []);

  async function loadUsers() {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));
      setUsers(MOCK_USERS);
    } catch (error) {
      logger.error("Failed to load users:", error);
    } finally {
      setIsLoading(false);
    }
  }

  const filteredUsers = useMemo(() => {
    return users.filter((u) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !u.name.toLowerCase().includes(query) &&
          !u.nameAr.includes(query) &&
          !u.email.toLowerCase().includes(query)
        ) {
          return false;
        }
      }
      if (roleFilter && u.role !== roleFilter) return false;
      if (statusFilter && u.status !== statusFilter) return false;
      return true;
    });
  }, [users, searchQuery, roleFilter, statusFilter]);

  const stats = useMemo(() => ({
    total: users.length,
    active: users.filter((u) => u.status === "active").length,
    farmers: users.filter((u) => u.role === "farmer").length,
    pending: users.filter((u) => u.status === "pending").length,
  }), [users]);

  const getRoleLabel = (role: User["role"]) => {
    const labels: Record<User["role"], string> = {
      admin: "مدير",
      expert: "خبير",
      farmer: "مزارع",
      viewer: "مشاهد",
    };
    return labels[role];
  };

  const getRoleColor = (role: User["role"]) => {
    const colors: Record<User["role"], string> = {
      admin: "bg-purple-100 text-purple-800",
      expert: "bg-blue-100 text-blue-800",
      farmer: "bg-green-100 text-green-800",
      viewer: "bg-gray-100 text-gray-800",
    };
    return colors[role];
  };

  const columns = [
    {
      key: "name",
      header: "المستخدم",
      render: (user: User) => (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-sahool-100 rounded-full flex items-center justify-center">
            <Users className="w-5 h-5 text-sahool-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">{user.nameAr}</p>
            <p className="text-xs text-gray-500">{user.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: "phone",
      header: "الهاتف",
      render: (user: User) => (
        <span className="text-gray-700 text-sm" dir="ltr">{user.phone}</span>
      ),
    },
    {
      key: "role",
      header: "الدور",
      render: (user: User) => (
        <span className={cn("px-2 py-1 rounded-full text-xs font-medium", getRoleColor(user.role))}>
          {getRoleLabel(user.role)}
        </span>
      ),
    },
    {
      key: "farmCount",
      header: "المزارع",
      render: (user: User) => (
        <span className="text-gray-700">{user.farmCount}</span>
      ),
    },
    {
      key: "status",
      header: "الحالة",
      render: (user: User) => <StatusBadge status={user.status} />,
    },
    {
      key: "lastLogin",
      header: "آخر دخول",
      render: (user: User) => (
        <span className="text-gray-500 text-sm">
          {user.lastLogin ? formatDate(user.lastLogin) : "لم يسجل دخول"}
        </span>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (user: User) => (
        <div className="flex items-center gap-1">
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Eye className="w-4 h-4 text-gray-500" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Edit className="w-4 h-4 text-blue-500" />
          </button>
          <button className="p-2 hover:bg-red-50 rounded-lg transition-colors">
            <Trash2 className="w-4 h-4 text-red-500" />
          </button>
        </div>
      ),
      className: "w-32",
    },
  ];

  return (
    <div className="p-6">
      <Header title="إدارة المستخدمين" subtitle={`${users.length} مستخدم مسجل`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-sm text-gray-500">إجمالي المستخدمين</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <UserCheck className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.active}</p>
              <p className="text-sm text-gray-500">نشط</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-100 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-sahool-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.farmers}</p>
              <p className="text-sm text-gray-500">مزارع</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <UserX className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.pending}</p>
              <p className="text-sm text-gray-500">في الانتظار</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-6 bg-white rounded-xl p-4 border border-gray-100">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث بالاسم أو البريد..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
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
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="active">نشط</option>
            <option value="inactive">غير نشط</option>
            <option value="suspended">موقوف</option>
            <option value="pending">في الانتظار</option>
          </select>

          <button
            onClick={loadUsers}
            className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <RefreshCw className={cn("w-5 h-5 text-gray-600", isLoading && "animate-spin")} />
          </button>
          <button className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Download className="w-5 h-5 text-gray-600" />
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors">
            <Plus className="w-5 h-5" />
            إضافة مستخدم
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6">
        {isLoading ? (
          <div className="bg-white rounded-xl border border-gray-100 p-8">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-12 bg-gray-200 rounded"></div>
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
    </div>
  );
}
