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
export { ErrorBoundary, withErrorBoundary, type ErrorBoundaryProps } from './components/ErrorBoundary';
export { LanguageSwitcher, type LanguageSwitcherProps } from './components/LanguageSwitcher';
export { LoadingSpinner, type LoadingSpinnerProps } from './components/LoadingSpinner';
export { LoadingOverlay, type LoadingOverlayProps } from './components/LoadingOverlay';
export { SkipLink, type SkipLinkProps } from './components/SkipLink';
export { VisuallyHidden, type VisuallyHiddenProps } from './components/VisuallyHidden';
export { FocusTrap, type FocusTrapProps } from './components/FocusTrap';

// Modern Components
export { GlassCard, type GlassCardProps } from './components/GlassCard';
export { ModernButton, type ModernButtonProps } from './components/ModernButton';
export { AnimatedCard, type AnimatedCardProps } from './components/AnimatedCard';
export { GradientText, type GradientTextProps } from './components/GradientText';
export { FloatingLabel, type FloatingLabelProps } from './components/FloatingLabel';
export { Shimmer, ShimmerGroup, type ShimmerProps, type ShimmerGroupProps } from './components/Shimmer';
export { ProgressRing, type ProgressRingProps } from './components/ProgressRing';
export { Tooltip, TooltipProvider, type TooltipProps, type TooltipProviderProps } from './components/Tooltip';

// Feedback & Notification Components
export { ModernToast, ToastProvider, useToast, type Toast, type ModernToastProps, type ToastContextType, type ToastProviderProps } from './components/ModernToast';
export { ModernAlert, type ModernAlertProps } from './components/ModernAlert';
export { ModernBadge, type ModernBadgeProps } from './components/ModernBadge';
export { ModernProgress, CircularProgress, type ModernProgressProps, type CircularProgressProps } from './components/ModernProgress';
export { ModernSpinner, SpinnerOverlay, type ModernSpinnerProps, type SpinnerOverlayProps } from './components/ModernSpinner';
export { ConfirmDialog, type ConfirmDialogProps } from './components/ConfirmDialog';

// Data Display Components
export { ModernTable, type ModernTableProps, type Column } from './components/ModernTable';
export { ModernTabs, type ModernTabsProps, type Tab } from './components/ModernTabs';
export { ModernAccordion, type ModernAccordionProps, type AccordionItem } from './components/ModernAccordion';
export { ModernModal, type ModernModalProps } from './components/ModernModal';
export { ModernDrawer, type ModernDrawerProps } from './components/ModernDrawer';
export { ModernDropdown, type ModernDropdownProps, type DropdownItem } from './components/ModernDropdown';

// Form Components
export { ModernSelect, type ModernSelectProps, type SelectOption } from './components/ModernSelect';
export { ModernCheckbox, type ModernCheckboxProps } from './components/ModernCheckbox';
export { ModernRadio, type ModernRadioProps, type RadioOption } from './components/ModernRadio';
export { ModernSwitch, type ModernSwitchProps } from './components/ModernSwitch';
export { ModernSlider, type ModernSliderProps, type SliderMark } from './components/ModernSlider';
export { DatePicker, type DatePickerProps } from './components/DatePicker';

// Animation Components
export {
  AnimatedContainer,
  FadeIn,
  SlideUp,
  SlideDown,
  ScaleIn,
  BounceIn,
  type AnimatedContainerProps,
  type FadeInProps,
  type SlideUpProps,
  type SlideDownProps,
  type ScaleInProps,
  type BounceInProps,
} from './components/AnimatedContainer';

export {
  StaggeredList,
  StaggerFadeIn,
  StaggerSlideUp,
  StaggerScaleIn,
  StaggeredGrid,
  type StaggeredListProps,
  type StaggerFadeInProps,
  type StaggerSlideUpProps,
  type StaggerScaleInProps,
  type StaggeredGridProps,
} from './components/StaggeredList';

export {
  PageTransition,
  FadePageTransition,
  SlideUpPageTransition,
  ScalePageTransition,
  TransitionLayout,
  RouteTransition,
  type PageTransitionProps,
  type FadePageTransitionProps,
  type SlideUpPageTransitionProps,
  type ScalePageTransitionProps,
  type TransitionLayoutProps,
  type RouteTransitionProps,
  type TransitionType,
} from './components/PageTransition';

// Animation Utilities
export * from './animations';
export * from './animations/variants';

// Responsive Design Components
export {
  ResponsiveContainer,
  NarrowContainer,
  WideContainer,
  FullWidthContainer,
  Section,
  Article,
  PageContainer,
  FluidContainer,
  type ResponsiveContainerProps,
} from './components/ResponsiveContainer';

export {
  MobileNav,
  useMobileNav,
  type MobileNavProps,
  type NavItem,
} from './components/MobileNav';

export {
  ResponsiveGrid,
  MasonryGrid,
  AutoGrid,
  GridItem,
  SimpleGrid,
  FlexGrid,
  type ResponsiveGridProps,
  type MasonryGridProps,
  type AutoGridProps,
  type GridItemProps,
  type SimpleGridProps,
  type FlexGridProps,
} from './components/ResponsiveGrid';

// Responsive Design Hooks
export {
  useMediaQuery,
  usePrefersReducedMotion,
  usePrefersDarkMode,
  useOrientation,
  useHoverSupport,
  useTouchDevice,
} from './hooks/useMediaQuery';

export {
  useBreakpoint,
  useBreakpointValue,
  useResponsiveValue,
  useBreakpointEffect,
  breakpoints,
  type Breakpoint,
  type BreakpointInfo,
} from './hooks/useBreakpoint';

// Re-export utilities for convenience
export * from '@sahool/shared-utils';
