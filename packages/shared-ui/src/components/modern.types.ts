// ═══════════════════════════════════════════════════════════════════════════════
// Modern Components Type Definitions
// Centralized type exports for modern UI components
// ═══════════════════════════════════════════════════════════════════════════════

export type {
  GlassCardProps
} from './GlassCard';

export type {
  ModernButtonProps
} from './ModernButton';

export type {
  AnimatedCardProps
} from './AnimatedCard';

export type {
  GradientTextProps
} from './GradientText';

export type {
  FloatingLabelProps
} from './FloatingLabel';

export type {
  ShimmerProps,
  ShimmerGroupProps
} from './Shimmer';

export type {
  ProgressRingProps
} from './ProgressRing';

export type {
  TooltipProps,
  TooltipProviderProps
} from './Tooltip';

export type {
  Toast,
  ModernToastProps,
  ToastContextType,
  ToastProviderProps
} from './ModernToast';

export type {
  ModernAlertProps
} from './ModernAlert';

export type {
  ModernBadgeProps
} from './ModernBadge';

export type {
  ModernProgressProps,
  CircularProgressProps
} from './ModernProgress';

export type {
  ModernSpinnerProps,
  SpinnerOverlayProps
} from './ModernSpinner';

export type {
  ConfirmDialogProps
} from './ConfirmDialog';

export type {
  ModernTableProps,
  Column
} from './ModernTable';

export type {
  ModernTabsProps,
  Tab
} from './ModernTabs';

export type {
  ModernAccordionProps,
  AccordionItem
} from './ModernAccordion';

export type {
  ModernModalProps
} from './ModernModal';

export type {
  ModernDrawerProps
} from './ModernDrawer';

export type {
  ModernDropdownProps,
  DropdownItem
} from './ModernDropdown';

export type {
  ModernSelectProps,
  SelectOption
} from './ModernSelect';

export type {
  ModernCheckboxProps
} from './ModernCheckbox';

export type {
  ModernRadioProps,
  RadioOption
} from './ModernRadio';

export type {
  ModernSwitchProps
} from './ModernSwitch';

export type {
  ModernSliderProps,
  SliderMark
} from './ModernSlider';

export type {
  DatePickerProps
} from './DatePicker';

// ═══════════════════════════════════════════════════════════════════════════════
// Common Types for Modern Components
// ═══════════════════════════════════════════════════════════════════════════════

export type Size = 'sm' | 'md' | 'lg' | 'xl';
export type Variant = 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
export type Position = 'top' | 'bottom' | 'left' | 'right';
export type Intensity = 'subtle' | 'medium' | 'strong';
export type BlurLevel = 'sm' | 'md' | 'lg' | 'xl';

// ═══════════════════════════════════════════════════════════════════════════════
// Component Variant Types
// ═══════════════════════════════════════════════════════════════════════════════

export type ButtonVariant = 'gradient' | 'glow' | 'outline' | 'ghost' | 'solid';
export type CardVariant = 'light' | 'medium' | 'dark';
export type AnimationVariant = 'lift' | 'tilt' | 'glow' | 'border' | 'scale';
export type GradientVariant = 'primary' | 'secondary' | 'rainbow' | 'sunset' | 'ocean' | 'forest';
export type InputVariant = 'default' | 'filled' | 'outlined';
export type ShimmerVariant = 'text' | 'rectangular' | 'circular' | 'rounded';
export type ProgressVariant = 'primary' | 'success' | 'warning' | 'danger' | 'gradient';
export type TooltipVariant = 'dark' | 'light' | 'primary';
export type ToastVariant = 'success' | 'error' | 'warning' | 'info';
export type AlertVariant = 'success' | 'error' | 'warning' | 'info';
export type BadgeVariant = 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'neutral';
export type SpinnerVariant = 'dots' | 'ring' | 'bars' | 'pulse' | 'bounce' | 'gradient';
export type DialogVariant = 'info' | 'warning' | 'danger' | 'success';

// ═══════════════════════════════════════════════════════════════════════════════
// Utility Types
// ═══════════════════════════════════════════════════════════════════════════════

export type AnimationSpeed = 'slow' | 'normal' | 'fast';
export type Spacing = 'sm' | 'md' | 'lg';
export type Thickness = 'thin' | 'medium' | 'thick';

// ═══════════════════════════════════════════════════════════════════════════════
// Helper Types for Component Composition
// ═══════════════════════════════════════════════════════════════════════════════

export interface BaseComponentProps {
  className?: string;
  id?: string;
  role?: string;
  'aria-label'?: string;
  'aria-describedby'?: string;
  'aria-labelledby'?: string;
}

export interface InteractiveComponentProps extends BaseComponentProps {
  disabled?: boolean;
  onClick?: () => void;
  onFocus?: () => void;
  onBlur?: () => void;
}

export interface AnimatableComponentProps extends BaseComponentProps {
  animated?: boolean;
  animationDuration?: number;
  animationDelay?: number;
}
