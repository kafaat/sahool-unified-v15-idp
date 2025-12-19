'use client';

// Status Badge Component
// شارة الحالة

import { cn, getStatusColor, getStatusLabel } from '@/lib/utils';

interface StatusBadgeProps {
  status: string;
  className?: string;
  locale?: string;
}

export default function StatusBadge({ status, className = '', locale = 'ar' }: StatusBadgeProps) {
  return (
    <span className={cn(
      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
      getStatusColor(status),
      className
    )}>
      {getStatusLabel(status, locale)}
    </span>
  );
}
