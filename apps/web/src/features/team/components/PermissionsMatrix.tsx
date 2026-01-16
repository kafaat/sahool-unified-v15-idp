"use client";

/**
 * SAHOOL Permissions Matrix Component
 * مكون مصفوفة الصلاحيات
 */

import React from "react";
import {
  Check,
  X,
  FileText,
  ListTodo,
  BarChart3,
  Users,
  Settings,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Role,
  ROLE_CONFIGS,
  PermissionCategory,
  PermissionAction,
} from "../types/team";

const CATEGORY_LABELS: Record<
  PermissionCategory,
  { ar: string; en: string; icon: any }
> = {
  [PermissionCategory.FIELDS]: { ar: "الحقول", en: "Fields", icon: FileText },
  [PermissionCategory.TASKS]: { ar: "المهام", en: "Tasks", icon: ListTodo },
  [PermissionCategory.REPORTS]: {
    ar: "التقارير",
    en: "Reports",
    icon: BarChart3,
  },
  [PermissionCategory.TEAM]: { ar: "الفريق", en: "Team", icon: Users },
  [PermissionCategory.SETTINGS]: {
    ar: "الإعدادات",
    en: "Settings",
    icon: Settings,
  },
};

const ACTION_LABELS: Record<PermissionAction, { ar: string; en: string }> = {
  [PermissionAction.VIEW]: { ar: "عرض", en: "View" },
  [PermissionAction.CREATE]: { ar: "إنشاء", en: "Create" },
  [PermissionAction.EDIT]: { ar: "تعديل", en: "Edit" },
  [PermissionAction.DELETE]: { ar: "حذف", en: "Delete" },
  [PermissionAction.MANAGE]: { ar: "إدارة كاملة", en: "Full Manage" },
};

interface PermissionsMatrixProps {
  selectedRole?: Role;
}

export const PermissionsMatrix: React.FC<PermissionsMatrixProps> = ({
  selectedRole,
}) => {
  const roles = Object.values(Role);
  const categories = Object.values(PermissionCategory);

  const hasPermission = (role: Role, category: PermissionCategory): boolean => {
    const config = ROLE_CONFIGS[role];
    const permission = config.permissions.find((p) => p.category === category);
    return permission ? permission.allowed : false;
  };

  const getPermissionAction = (
    role: Role,
    category: PermissionCategory,
  ): PermissionAction | null => {
    const config = ROLE_CONFIGS[role];
    const permission = config.permissions.find((p) => p.category === category);
    return permission ? permission.action : null;
  };

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden">
      <div className="p-6 border-b-2 border-gray-200 bg-gray-50">
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          مصفوفة الصلاحيات
        </h3>
        <p className="text-gray-600 text-sm">
          عرض الصلاحيات المتاحة لكل دور في النظام
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b-2 border-gray-200">
            <tr>
              <th className="px-6 py-4 text-right text-sm font-bold text-gray-700 sticky right-0 bg-gray-50">
                الفئة / Category
              </th>
              {roles.map((role) => {
                const config = ROLE_CONFIGS[role];
                const isSelected = selectedRole === role;
                return (
                  <th
                    key={role}
                    className={`px-4 py-4 text-center min-w-[140px] ${
                      isSelected ? "bg-blue-50" : ""
                    }`}
                  >
                    <div className="flex flex-col items-center gap-2">
                      <Badge className={config.color} size="sm">
                        {config.nameAr}
                      </Badge>
                      <span className="text-xs text-gray-500">
                        {config.nameEn}
                      </span>
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {categories.map((category, idx) => {
              const categoryInfo = CATEGORY_LABELS[category];
              const Icon = categoryInfo.icon;

              return (
                <tr
                  key={category}
                  className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
                >
                  <td className="px-6 py-4 sticky right-0 bg-inherit border-l border-gray-200">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <Icon className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">
                          {categoryInfo.ar}
                        </div>
                        <div className="text-xs text-gray-500">
                          {categoryInfo.en}
                        </div>
                      </div>
                    </div>
                  </td>
                  {roles.map((role) => {
                    const allowed = hasPermission(role, category);
                    const action = getPermissionAction(role, category);
                    const isSelected = selectedRole === role;

                    return (
                      <td
                        key={role}
                        className={`px-4 py-4 text-center ${
                          isSelected ? "bg-blue-50" : ""
                        }`}
                      >
                        {allowed && action ? (
                          <div className="flex flex-col items-center gap-1">
                            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                              <Check className="w-5 h-5 text-green-600" />
                            </div>
                            <span className="text-xs text-gray-600">
                              {ACTION_LABELS[action].ar}
                            </span>
                          </div>
                        ) : (
                          <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center mx-auto">
                            <X className="w-5 h-5 text-red-600" />
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="p-6 bg-gray-50 border-t-2 border-gray-200">
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
              <Check className="w-4 h-4 text-green-600" />
            </div>
            <span className="text-gray-700">مسموح / Allowed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center">
              <X className="w-4 h-4 text-red-600" />
            </div>
            <span className="text-gray-700">غير مسموح / Not Allowed</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PermissionsMatrix;
