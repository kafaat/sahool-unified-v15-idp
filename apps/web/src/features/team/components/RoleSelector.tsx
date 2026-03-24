'use client';

/**
 * SAHOOL Role Selector Component
 * مكون اختيار الدور
 */

import React from 'react';
import { ChevronDown } from 'lucide-react';
import { Role, ROLE_CONFIGS } from '../types/team';

interface RoleSelectorProps {
  value: Role;
  onChange: (role: Role) => void;
  disabled?: boolean;
  className?: string;
}

export const RoleSelector: React.FC<RoleSelectorProps> = ({
  value,
  onChange,
  disabled = false,
  className = '',
}) => {
  return (
    <div className={`relative ${className}`}>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as Role)}
        disabled={disabled}
        className="w-full px-4 py-2 pr-10 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed appearance-none bg-white"
      >
        {Object.values(Role).map((role) => {
          const config = ROLE_CONFIGS[role];
          return (
            <option key={role} value={role}>
              {config.nameAr} - {config.nameEn} ({config.descriptionAr})
            </option>
          );
        })}
      </select>
      <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
        <ChevronDown className="w-5 h-5 text-gray-400" />
      </div>
    </div>
  );
};

export default RoleSelector;
