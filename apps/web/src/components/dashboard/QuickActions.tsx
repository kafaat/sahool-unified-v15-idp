/**
 * SAHOOL Quick Actions Component
 * إجراءات سريعة
 *
 * Performance optimizations:
 * - React.memo prevents re-renders when props don't change
 * - useMemo memoizes actions array to prevent recreation on every render
 * - useCallback memoizes action handlers
 */

import React, { useMemo, useCallback } from "react";

interface QuickAction {
  id: string;
  label: string;
  icon: string;
  color: string;
}

interface QuickActionsProps {
  onAction?: (actionId: string) => void;
}

// Static action definitions (defined outside component to prevent recreation)
const ACTION_DEFINITIONS: Omit<QuickAction, "onClick">[] = [
  {
    id: "new-field",
    label: "حقل جديد",
    icon: "➕",
    color: "bg-green-500 hover:bg-green-600",
  },
  {
    id: "ndvi",
    label: "تحليل NDVI",
    icon: "📊",
    color: "bg-blue-500 hover:bg-blue-600",
  },
  {
    id: "irrigation",
    label: "جدولة الري",
    icon: "💧",
    color: "bg-cyan-500 hover:bg-cyan-600",
  },
  {
    id: "tasks",
    label: "المهام",
    icon: "📋",
    color: "bg-orange-500 hover:bg-orange-600",
  },
];

export const QuickActions = React.memo<QuickActionsProps>(
  function QuickActions({ onAction }) {
    // Memoized action handler
    const handleAction = useCallback(
      (actionId: string) => {
        onAction?.(actionId);
      },
      [onAction]
    );

    // Memoize actions array
    const actions = useMemo(() => ACTION_DEFINITIONS, []);

    return (
      <div
        className="bg-white rounded-xl shadow-sm border border-gray-200 p-4"
        role="region"
        aria-label="إجراءات سريعة"
      >
        <h3 className="font-semibold text-gray-900 mb-4">إجراءات سريعة</h3>
        <div className="grid grid-cols-2 gap-3">
          {actions.map((action) => (
            <button
              key={action.id}
              onClick={() => handleAction(action.id)}
              aria-label={action.label}
              className={`
              ${action.color}
              text-white rounded-lg p-3
              flex flex-col items-center gap-2
              transition-all duration-200
              focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2
            `}
            >
              <span className="text-2xl" aria-hidden="true">
                {action.icon}
              </span>
              <span className="text-sm font-medium">{action.label}</span>
            </button>
          ))}
        </div>
      </div>
    );
  },
);

export default QuickActions;
