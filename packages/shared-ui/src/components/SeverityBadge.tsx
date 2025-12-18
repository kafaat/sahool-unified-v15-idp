'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// SeverityBadge Component - شارة الخطورة
// Unified severity badge for displaying severity levels
// ═══════════════════════════════════════════════════════════════════════════════

import { cn, getSeverityColor, getSeverityLabel } from '@sahool/shared-utils';
import { AlertTriangle, AlertCircle, AlertOctagon, Info } from 'lucide-react';

export interface SeverityBadgeProps {
  severity: 'low' | 'medium' | 'high' | 'critical';
  className?: string;
  locale?: 'ar' | 'en';
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-0.5 text-sm',
  lg: 'px-3 py-1 text-base',
};

const iconSizes = {
  sm: 12,
  md: 14,
  lg: 16,
};

const SeverityIcon = {
  low: Info,
  medium: AlertTriangle,
  high: AlertCircle,
  critical: AlertOctagon,
};

export function SeverityBadge({
  severity,
  className = '',
  locale = 'ar',
  showIcon = true,
  size = 'sm'
}: SeverityBadgeProps) {
  const Icon = SeverityIcon[severity];

  return (
    <span className={cn(
      'inline-flex items-center gap-1 rounded-full font-medium',
      sizeClasses[size],
      getSeverityColor(severity),
      className
    )}>
      {showIcon && <Icon size={iconSizes[size]} />}
      {getSeverityLabel(severity, locale)}
    </span>
  );
}
