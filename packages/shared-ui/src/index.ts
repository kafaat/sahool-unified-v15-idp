// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Shared UI Components
// Unified UI library for all frontend applications
// مكتبة واجهة المستخدم الموحدة لجميع تطبيقات الواجهة الأمامية
// ═══════════════════════════════════════════════════════════════════════════════

// Components
export {
  StatusBadge,
  type StatusBadgeProps,
  type BadgeSize,
  type Locale,
} from "./components/StatusBadge";
export {
  SeverityBadge,
  type SeverityBadgeProps,
  type SeverityLevel,
  type SeverityBadgeSize,
} from "./components/SeverityBadge";
export {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
  type CardProps,
  type CardHeaderProps,
  type CardContentProps,
  type CardFooterProps,
  type CardPadding,
} from "./components/Card";
export {
  StatCard,
  type StatCardProps,
  type StatCardColor,
} from "./components/StatCard";
export {
  Button,
  type ButtonProps,
  type ButtonVariant,
  type ButtonSize,
} from "./components/Button";
export {
  Skeleton,
  SkeletonCard,
  SkeletonTable,
  type SkeletonProps,
  type SkeletonVariant,
  type SkeletonCardProps,
  type SkeletonTableProps,
} from "./components/Skeleton";
export {
  Alert,
  type AlertProps,
  type AlertType,
} from "./components/Alert";
export {
  ErrorBoundary,
  withErrorBoundary,
  AsyncErrorBoundary,
  type ErrorBoundaryProps,
  type AsyncErrorBoundaryProps,
} from "./components/ErrorBoundary";
export {
  LanguageSwitcher,
  type LanguageSwitcherProps,
  type SupportedLocale,
} from "./components/LanguageSwitcher";
export {
  LoadingSpinner,
  type LoadingSpinnerProps,
  type SpinnerSize,
  type SpinnerColor,
} from "./components/LoadingSpinner";
export {
  LoadingOverlay,
  type LoadingOverlayProps,
} from "./components/LoadingOverlay";
export { SkipLink, type SkipLinkProps } from "./components/SkipLink";
export {
  VisuallyHidden,
  type VisuallyHiddenProps,
  type VisuallyHiddenElement,
} from "./components/VisuallyHidden";
export { FocusTrap, type FocusTrapProps } from "./components/FocusTrap";

// Form Components
export { Input, type InputProps } from "./components/Input";
export {
  Select,
  type SelectProps,
  type SelectOption,
  type SelectSize,
} from "./components/Select";

// Layout Components
export {
  Modal,
  ModalFooter,
  type ModalProps,
  type ModalFooterProps,
} from "./components/Modal";
export {
  Tabs,
  TabPanel,
  type TabsProps,
  type TabPanelProps,
  type Tab,
} from "./components/Tabs";

// Auth Components
export {
  PermissionGate,
  RoleGate,
  AdminGate,
  withPermission,
  type PermissionGateProps,
} from "./components/auth/PermissionGate";

// Re-export utilities for convenience
export * from "@sahool/shared-utils";
