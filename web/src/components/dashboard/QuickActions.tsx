/**
 * SAHOOL Quick Actions Component
 * إجراءات سريعة
 */

import React from 'react';

interface QuickAction {
  id: string;
  label: string;
  icon: string;
  color: string;
  onClick: () => void;
}

interface QuickActionsProps {
  onAction?: (actionId: string) => void;
}

export const QuickActions: React.FC<QuickActionsProps> = ({ onAction }) => {
  const actions: QuickAction[] = [
    {
      id: 'new-field',
      label: 'حقل جديد',
      icon: '➕',
      color: 'bg-green-500 hover:bg-green-600',
      onClick: () => onAction?.('new-field'),
    },
    {
      id: 'ndvi',
      label: 'تحليل NDVI',
      icon: '📊',
      color: 'bg-blue-500 hover:bg-blue-600',
      onClick: () => onAction?.('ndvi'),
    },
    {
      id: 'irrigation',
      label: 'جدولة الري',
      icon: '💧',
      color: 'bg-cyan-500 hover:bg-cyan-600',
      onClick: () => onAction?.('irrigation'),
    },
    {
      id: 'tasks',
      label: 'المهام',
      icon: '📋',
      color: 'bg-orange-500 hover:bg-orange-600',
      onClick: () => onAction?.('tasks'),
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <h3 className="font-semibold text-gray-900 mb-4">إجراءات سريعة</h3>
      <div className="grid grid-cols-2 gap-3">
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={action.onClick}
            className={`
              ${action.color}
              text-white rounded-lg p-3
              flex flex-col items-center gap-2
              transition-all duration-200
            `}
          >
            <span className="text-2xl">{action.icon}</span>
            <span className="text-sm font-medium">{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActions;
