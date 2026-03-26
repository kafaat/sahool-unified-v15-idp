/**
 * SAHOOL Quick Actions Component
 * مكون الإجراءات السريعة
 */

import React from 'react';
import { Plus, MapPin, ListTodo, CloudSun, FileText, Settings } from 'lucide-react';
import Link from 'next/link';

interface ActionButtonProps {
  icon: React.ReactNode;
  label: string;
  labelAr: string;
  href: string;
  color: string;
}

const ActionButton: React.FC<ActionButtonProps & { index: number }> = ({
  icon,
  label,
  labelAr,
  href,
  color,
  index,
}) => {
  return (
    <Link
      href={href}
      className={`group flex flex-col items-center justify-center p-6 rounded-xl border-2 ${color} bg-white dark:bg-gray-800 hover:shadow-lg transition-all hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 animate-slide-in-up`}
      style={{
        animationDelay: `${index * 60}ms`,
        animationFillMode: 'both',
      }}
    >
      <div
        className={`p-3 rounded-full ${color} bg-opacity-10 dark:bg-opacity-20 mb-3 transition-transform group-hover:scale-110`}
      >
        {icon}
      </div>
      <p className="font-semibold text-gray-900 dark:text-white text-center">{labelAr}</p>
      <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-1">{label}</p>
    </Link>
  );
};

export const QuickActions: React.FC = () => {
  const actions: ActionButtonProps[] = [
    {
      icon: <MapPin className="w-6 h-6 text-blue-600 dark:text-blue-400" />,
      label: 'Add Field',
      labelAr: 'إضافة حقل',
      href: '/fields?action=new',
      color: 'border-blue-200 dark:border-blue-800',
    },
    {
      icon: <Plus className="w-6 h-6 text-green-600 dark:text-green-400" />,
      label: 'New Task',
      labelAr: 'مهمة جديدة',
      href: '/tasks?action=new',
      color: 'border-green-200 dark:border-green-800',
    },
    {
      icon: <CloudSun className="w-6 h-6 text-cyan-600 dark:text-cyan-400" />,
      label: 'Weather',
      labelAr: 'الطقس',
      href: '/weather',
      color: 'border-cyan-200 dark:border-cyan-800',
    },
    {
      icon: <FileText className="w-6 h-6 text-purple-600 dark:text-purple-400" />,
      label: 'Reports',
      labelAr: 'التقارير',
      href: '/reports',
      color: 'border-purple-200 dark:border-purple-800',
    },
    {
      icon: <ListTodo className="w-6 h-6 text-orange-600 dark:text-orange-400" />,
      label: 'All Tasks',
      labelAr: 'جميع المهام',
      href: '/tasks',
      color: 'border-orange-200 dark:border-orange-800',
    },
    {
      icon: <Settings className="w-6 h-6 text-gray-600 dark:text-gray-400" />,
      label: 'Settings',
      labelAr: 'الإعدادات',
      href: '/settings',
      color: 'border-gray-200 dark:border-gray-700',
    },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 p-6 transition-colors">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white">الإجراءات السريعة</h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">Quick Actions</span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {actions.map((action, index) => (
          <ActionButton key={index} {...action} index={index} />
        ))}
      </div>
    </div>
  );
};

export default QuickActions;
