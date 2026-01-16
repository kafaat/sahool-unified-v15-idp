/**
 * SAHOOL Team Management Types
 * أنواع إدارة الفريق
 */

/**
 * User Role Enum
 * تعداد أدوار المستخدم
 */
export enum Role {
  ADMIN = "ADMIN",
  MANAGER = "MANAGER",
  FARMER = "FARMER",
  WORKER = "WORKER",
  VIEWER = "VIEWER",
}

/**
 * User Status Enum
 * تعداد حالات المستخدم
 */
export enum UserStatus {
  ACTIVE = "ACTIVE",
  INACTIVE = "INACTIVE",
  SUSPENDED = "SUSPENDED",
  PENDING = "PENDING",
}

/**
 * Permission Categories
 * فئات الصلاحيات
 */
export enum PermissionCategory {
  FIELDS = "fields",
  TASKS = "tasks",
  REPORTS = "reports",
  TEAM = "team",
  SETTINGS = "settings",
}

/**
 * Permission Actions
 * إجراءات الصلاحيات
 */
export enum PermissionAction {
  VIEW = "view",
  CREATE = "create",
  EDIT = "edit",
  DELETE = "delete",
  MANAGE = "manage",
}

/**
 * Permission Interface
 * واجهة الصلاحية
 */
export interface Permission {
  category: PermissionCategory;
  action: PermissionAction;
  allowed: boolean;
}

/**
 * Role Configuration with Permissions
 * تكوين الدور مع الصلاحيات
 */
export interface RoleConfig {
  role: Role;
  nameEn: string;
  nameAr: string;
  descriptionEn: string;
  descriptionAr: string;
  color: string;
  permissions: Permission[];
}

/**
 * Team Member Interface
 * واجهة عضو الفريق
 */
export interface TeamMember {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone?: string;
  role: Role;
  status: UserStatus;
  avatarUrl?: string;
  lastLoginAt?: string;
  emailVerified: boolean;
  phoneVerified: boolean;
  createdAt: string;
  updatedAt: string;
  profile?: {
    nationalId?: string;
    city?: string;
    region?: string;
    country?: string;
  };
}

/**
 * Invite Member Request
 * طلب دعوة عضو
 */
export interface InviteRequest {
  email: string;
  firstName: string;
  lastName: string;
  role: Role;
  phone?: string;
}

/**
 * Role Update Request
 * طلب تحديث الدور
 */
export interface RoleUpdate {
  userId: string;
  role: Role;
}

/**
 * Team Statistics
 * إحصائيات الفريق
 */
export interface TeamStats {
  total: number;
  active: number;
  pending: number;
  byRole: {
    [key in Role]: number;
  };
}

/**
 * Team Filters
 * فلاتر الفريق
 */
export interface TeamFilters {
  search?: string;
  role?: Role;
  status?: UserStatus;
}

/**
 * API Response Wrapper
 * غلاف استجابة API
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  messageAr?: string;
}

/**
 * Role Configurations with Bilingual Labels
 * تكوينات الأدوار مع التسميات ثنائية اللغة
 */
export const ROLE_CONFIGS: Record<Role, RoleConfig> = {
  [Role.ADMIN]: {
    role: Role.ADMIN,
    nameEn: "Admin",
    nameAr: "مدير",
    descriptionEn: "Full access to all features",
    descriptionAr: "كل الصلاحيات",
    color: "bg-purple-100 text-purple-800 border-purple-300",
    permissions: [
      {
        category: PermissionCategory.FIELDS,
        action: PermissionAction.MANAGE,
        allowed: true,
      },
      {
        category: PermissionCategory.TASKS,
        action: PermissionAction.MANAGE,
        allowed: true,
      },
      {
        category: PermissionCategory.REPORTS,
        action: PermissionAction.MANAGE,
        allowed: true,
      },
      {
        category: PermissionCategory.TEAM,
        action: PermissionAction.MANAGE,
        allowed: true,
      },
      {
        category: PermissionCategory.SETTINGS,
        action: PermissionAction.MANAGE,
        allowed: true,
      },
    ],
  },
  [Role.MANAGER]: {
    role: Role.MANAGER,
    nameEn: "Manager",
    nameAr: "مدير فريق",
    descriptionEn: "Team management",
    descriptionAr: "إدارة الفريق",
    color: "bg-blue-100 text-blue-800 border-blue-300",
    permissions: [
      {
        category: PermissionCategory.FIELDS,
        action: PermissionAction.MANAGE,
        allowed: true,
      },
      {
        category: PermissionCategory.TASKS,
        action: PermissionAction.MANAGE,
        allowed: true,
      },
      {
        category: PermissionCategory.REPORTS,
        action: PermissionAction.VIEW,
        allowed: true,
      },
      {
        category: PermissionCategory.TEAM,
        action: PermissionAction.VIEW,
        allowed: true,
      },
      {
        category: PermissionCategory.SETTINGS,
        action: PermissionAction.VIEW,
        allowed: true,
      },
    ],
  },
  [Role.FARMER]: {
    role: Role.FARMER,
    nameEn: "Scout",
    nameAr: "مراقب ميداني",
    descriptionEn: "Field monitoring",
    descriptionAr: "المراقبة الميدانية",
    color: "bg-green-100 text-green-800 border-green-300",
    permissions: [
      {
        category: PermissionCategory.FIELDS,
        action: PermissionAction.VIEW,
        allowed: true,
      },
      {
        category: PermissionCategory.TASKS,
        action: PermissionAction.EDIT,
        allowed: true,
      },
      {
        category: PermissionCategory.REPORTS,
        action: PermissionAction.CREATE,
        allowed: true,
      },
      {
        category: PermissionCategory.TEAM,
        action: PermissionAction.VIEW,
        allowed: false,
      },
      {
        category: PermissionCategory.SETTINGS,
        action: PermissionAction.VIEW,
        allowed: false,
      },
    ],
  },
  [Role.WORKER]: {
    role: Role.WORKER,
    nameEn: "Operator",
    nameAr: "مشغل",
    descriptionEn: "Task execution",
    descriptionAr: "تنفيذ المهام",
    color: "bg-yellow-100 text-yellow-800 border-yellow-300",
    permissions: [
      {
        category: PermissionCategory.FIELDS,
        action: PermissionAction.VIEW,
        allowed: true,
      },
      {
        category: PermissionCategory.TASKS,
        action: PermissionAction.EDIT,
        allowed: true,
      },
      {
        category: PermissionCategory.REPORTS,
        action: PermissionAction.VIEW,
        allowed: true,
      },
      {
        category: PermissionCategory.TEAM,
        action: PermissionAction.VIEW,
        allowed: false,
      },
      {
        category: PermissionCategory.SETTINGS,
        action: PermissionAction.VIEW,
        allowed: false,
      },
    ],
  },
  [Role.VIEWER]: {
    role: Role.VIEWER,
    nameEn: "Viewer",
    nameAr: "مشاهد",
    descriptionEn: "View only",
    descriptionAr: "عرض فقط",
    color: "bg-gray-100 text-gray-800 border-gray-300",
    permissions: [
      {
        category: PermissionCategory.FIELDS,
        action: PermissionAction.VIEW,
        allowed: true,
      },
      {
        category: PermissionCategory.TASKS,
        action: PermissionAction.VIEW,
        allowed: true,
      },
      {
        category: PermissionCategory.REPORTS,
        action: PermissionAction.VIEW,
        allowed: true,
      },
      {
        category: PermissionCategory.TEAM,
        action: PermissionAction.VIEW,
        allowed: false,
      },
      {
        category: PermissionCategory.SETTINGS,
        action: PermissionAction.VIEW,
        allowed: false,
      },
    ],
  },
};
