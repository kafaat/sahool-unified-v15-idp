"use client";

/**
 * SAHOOL Quick Actions Component
 * مكون الإجراءات السريعة
 */

import React from "react";
import {
  Plus,
  MapPin,
  ListTodo,
  CloudSun,
  FileText,
  Settings,
} from "lucide-react";
import Link from "next/link";

interface ActionButtonProps {
  icon: React.ReactNode;
  label: string;
  labelAr: string;
  href: string;
  color: string;
}

const ActionButton: React.FC<ActionButtonProps> = ({
  icon,
  label,
  labelAr,
  href,
  color,
}) => {
  return (
    <Link
      href={href}
      className={`flex flex-col items-center justify-center p-6 rounded-xl border-2 ${color} bg-white hover:shadow-lg transition-all hover:scale-105`}
    >
      <div className={`p-3 rounded-full ${color} bg-opacity-10 mb-3`}>
        {icon}
      </div>
      <p className="font-semibold text-gray-900 text-center">{labelAr}</p>
      <p className="text-xs text-gray-500 text-center mt-1">{label}</p>
    </Link>
  );
};

export const QuickActions: React.FC = () => {
  const actions: ActionButtonProps[] = [
    {
      icon: <MapPin className="w-6 h-6 text-blue-600" />,
      label: "Add Field",
      labelAr: "إضافة حقل",
      href: "/fields?action=new",
      color: "border-blue-200",
    },
    {
      icon: <Plus className="w-6 h-6 text-green-600" />,
      label: "New Task",
      labelAr: "مهمة جديدة",
      href: "/tasks?action=new",
      color: "border-green-200",
    },
    {
      icon: <CloudSun className="w-6 h-6 text-cyan-600" />,
      label: "Weather",
      labelAr: "الطقس",
      href: "/weather",
      color: "border-cyan-200",
    },
    {
      icon: <FileText className="w-6 h-6 text-purple-600" />,
      label: "Reports",
      labelAr: "التقارير",
      href: "/reports",
      color: "border-purple-200",
    },
    {
      icon: <ListTodo className="w-6 h-6 text-orange-600" />,
      label: "All Tasks",
      labelAr: "جميع المهام",
      href: "/tasks",
      color: "border-orange-200",
    },
    {
      icon: <Settings className="w-6 h-6 text-gray-600" />,
      label: "Settings",
      labelAr: "الإعدادات",
      href: "/settings",
      color: "border-gray-200",
    },
  ];

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-gray-900">الإجراءات السريعة</h3>
        <span className="text-sm text-gray-500">Quick Actions</span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {actions.map((action, index) => (
          <ActionButton key={index} {...action} />
        ))}
      </div>
    </div>
  );
};

export default QuickActions;
