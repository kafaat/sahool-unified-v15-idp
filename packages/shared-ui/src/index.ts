// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Shared UI Components
// Unified UI library for all frontend applications
// مكتبة واجهة المستخدم الموحدة لجميع تطبيقات الواجهة الأمامية
// ═══════════════════════════════════════════════════════════════════════════════

// Components
export { StatusBadge, type StatusBadgeProps } from './components/StatusBadge';
export { SeverityBadge, type SeverityBadgeProps } from './components/SeverityBadge';
export { Card, CardHeader, CardContent, CardFooter, type CardProps, type CardHeaderProps, type CardContentProps, type CardFooterProps } from './components/Card';
export { StatCard, type StatCardProps } from './components/StatCard';
export { Button, type ButtonProps } from './components/Button';
export { Skeleton, SkeletonCard, SkeletonTable, type SkeletonProps } from './components/Skeleton';
export { Alert, type AlertProps } from './components/Alert';

// Re-export utilities for convenience
export * from '@sahool/shared-utils';
