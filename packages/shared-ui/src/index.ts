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
export { ErrorBoundary, withErrorBoundary, AsyncErrorBoundary, type ErrorBoundaryProps } from './components/ErrorBoundary';
export { LanguageSwitcher, type LanguageSwitcherProps } from './components/LanguageSwitcher';
export { LoadingSpinner, type LoadingSpinnerProps } from './components/LoadingSpinner';
export { LoadingOverlay, type LoadingOverlayProps } from './components/LoadingOverlay';
export { SkipLink, type SkipLinkProps } from './components/SkipLink';
export { VisuallyHidden, type VisuallyHiddenProps } from './components/VisuallyHidden';
export { FocusTrap, type FocusTrapProps } from './components/FocusTrap';

// Form Components
export { Input, type InputProps } from './components/Input';
export { Select, type SelectProps, type SelectOption } from './components/Select';

// Layout Components
export { Modal, ModalFooter, type ModalProps, type ModalFooterProps } from './components/Modal';
export { Tabs, TabPanel, type TabsProps, type TabPanelProps, type Tab } from './components/Tabs';

// Auth Components
export { PermissionGate, RoleGate, AdminGate, withPermission, type PermissionGateProps } from './components/auth/PermissionGate';

// Re-export utilities for convenience
export * from '@sahool/shared-utils';
