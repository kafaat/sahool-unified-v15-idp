// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Page Transition Component
// Smooth page transitions for route changes
// انتقالات صفحة سلسة
// ═══════════════════════════════════════════════════════════════════════════════

import React, { useEffect, useState, useRef } from 'react';
import {
  AnimationPreset,
  AnimationDuration,
  AnimationEasing,
  getAnimationClass,
  getDurationClass,
  getEasingClass,
} from '../animations';

export type TransitionType = 'fade' | 'slide-up' | 'slide-down' | 'slide-left' | 'slide-right' | 'scale' | 'none';

export interface PageTransitionProps {
  children: React.ReactNode;
  /** Type of transition */
  type?: TransitionType;
  /** Animation duration */
  duration?: AnimationDuration;
  /** Animation easing */
  easing?: AnimationEasing;
  /** Additional CSS classes */
  className?: string;
  /** Additional inline styles */
  style?: React.CSSProperties;
  /** Key to trigger re-animation (e.g., route path) */
  transitionKey?: string | number;
  /** Callback when transition starts */
  onTransitionStart?: () => void;
  /** Callback when transition completes */
  onTransitionComplete?: () => void;
  /** Show loading state during transition */
  showLoading?: boolean;
  /** Custom loading component */
  loadingComponent?: React.ReactNode;
  /** Test ID for testing */
  testId?: string;
}

/**
 * Map transition types to animation presets
 */
const TRANSITION_PRESET_MAP: Record<Exclude<TransitionType, 'none'>, AnimationPreset> = {
  fade: 'fadeIn',
  'slide-up': 'slideUp',
  'slide-down': 'slideDown',
  'slide-left': 'slideLeft',
  'slide-right': 'slideRight',
  scale: 'scaleIn',
};

/**
 * PageTransition - Wrapper component for smooth page transitions
 *
 * Features:
 * - Multiple transition types (fade, slide, scale)
 * - Customizable duration and easing
 * - Loading state support
 * - Key-based re-animation
 * - TypeScript support
 *
 * @example
 * ```tsx
 * <PageTransition type="slide-up" transitionKey={pathname}>
 *   <YourPageContent />
 * </PageTransition>
 * ```
 *
 * @example With loading state
 * ```tsx
 * <PageTransition
 *   type="fade"
 *   showLoading
 *   loadingComponent={<LoadingSpinner />}
 *   transitionKey={currentPage}
 * >
 *   <PageContent />
 * </PageTransition>
 * ```
 */
export function PageTransition({
  children,
  type = 'fade',
  duration = 'normal',
  easing = 'ease-in-out',
  className = '',
  style,
  transitionKey,
  onTransitionStart,
  onTransitionComplete,
  showLoading = false,
  loadingComponent,
  testId,
}: PageTransitionProps) {
  const [isAnimating, setIsAnimating] = useState(true);
  const [isLoading, setIsLoading] = useState(showLoading);
  const elementRef = useRef<HTMLDivElement>(null);
  const previousKeyRef = useRef(transitionKey);

  // Handle transition key changes
  useEffect(() => {
    if (transitionKey !== undefined && transitionKey !== previousKeyRef.current) {
      // Start transition
      setIsAnimating(true);
      setIsLoading(showLoading);
      onTransitionStart?.();
      previousKeyRef.current = transitionKey;
    }
  }, [transitionKey, onTransitionStart, showLoading]);

  // Handle animation end
  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const handleAnimationEnd = () => {
      setIsAnimating(false);
      setIsLoading(false);
      onTransitionComplete?.();
    };

    element.addEventListener('animationend', handleAnimationEnd);
    return () => {
      element.removeEventListener('animationend', handleAnimationEnd);
    };
  }, [onTransitionComplete]);

  // Get animation classes
  let animationClasses = '';
  if (type !== 'none' && isAnimating) {
    const preset = TRANSITION_PRESET_MAP[type];
    animationClasses = [
      getAnimationClass(preset),
      getDurationClass(duration),
      getEasingClass(easing),
    ].join(' ');
  }

  const combinedClassName = `${animationClasses} ${className}`.trim();

  // Show loading component if loading
  if (isLoading && loadingComponent) {
    return <div className="flex items-center justify-center min-h-screen">{loadingComponent}</div>;
  }

  return (
    <div
      ref={elementRef}
      className={combinedClassName}
      style={style}
      data-testid={testId}
    >
      {children}
    </div>
  );
}

/**
 * Pre-configured page transition variants
 */

export interface FadePageTransitionProps extends Omit<PageTransitionProps, 'type'> {}

export function FadePageTransition(props: FadePageTransitionProps) {
  return <PageTransition type="fade" {...props} />;
}

export interface SlideUpPageTransitionProps extends Omit<PageTransitionProps, 'type'> {}

export function SlideUpPageTransition(props: SlideUpPageTransitionProps) {
  return <PageTransition type="slide-up" {...props} />;
}

export interface ScalePageTransitionProps extends Omit<PageTransitionProps, 'type'> {}

export function ScalePageTransition(props: ScalePageTransitionProps) {
  return <PageTransition type="scale" duration="slow" easing="spring" {...props} />;
}

/**
 * Layout wrapper with persistent header/footer
 */
export interface TransitionLayoutProps {
  children: React.ReactNode;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  sidebar?: React.ReactNode;
  transitionType?: TransitionType;
  transitionDuration?: AnimationDuration;
  transitionKey?: string | number;
  className?: string;
}

export function TransitionLayout({
  children,
  header,
  footer,
  sidebar,
  transitionType = 'fade',
  transitionDuration = 'normal',
  transitionKey,
  className = '',
}: TransitionLayoutProps) {
  return (
    <div className={`flex flex-col min-h-screen ${className}`}>
      {/* Persistent header */}
      {header && <header className="flex-shrink-0">{header}</header>}

      <div className="flex flex-1 overflow-hidden">
        {/* Persistent sidebar */}
        {sidebar && <aside className="flex-shrink-0">{sidebar}</aside>}

        {/* Main content with transitions */}
        <main className="flex-1 overflow-auto">
          <PageTransition
            type={transitionType}
            duration={transitionDuration}
            transitionKey={transitionKey}
          >
            {children}
          </PageTransition>
        </main>
      </div>

      {/* Persistent footer */}
      {footer && <footer className="flex-shrink-0">{footer}</footer>}
    </div>
  );
}

/**
 * Route transition wrapper for Next.js or React Router
 */
export interface RouteTransitionProps {
  children: React.ReactNode;
  /** Current route path or key */
  routeKey: string;
  /** Transition type */
  type?: TransitionType;
  /** Animation duration */
  duration?: AnimationDuration;
  /** Show loading indicator */
  loading?: boolean;
  /** Loading component */
  loadingComponent?: React.ReactNode;
  /** Callback when route changes */
  onRouteChange?: (newRoute: string) => void;
}

export function RouteTransition({
  children,
  routeKey,
  type = 'slide-up',
  duration = 'normal',
  loading = false,
  loadingComponent,
  onRouteChange,
}: RouteTransitionProps) {
  const previousRoute = useRef(routeKey);

  useEffect(() => {
    if (routeKey !== previousRoute.current) {
      onRouteChange?.(routeKey);
      previousRoute.current = routeKey;
    }
  }, [routeKey, onRouteChange]);

  return (
    <PageTransition
      type={type}
      duration={duration}
      transitionKey={routeKey}
      showLoading={loading}
      loadingComponent={loadingComponent}
    >
      {children}
    </PageTransition>
  );
}

/**
 * Example usage:
 *
 * ```tsx
 * // Next.js App Router
 * export default function RootLayout({ children }) {
 *   const pathname = usePathname();
 *
 *   return (
 *     <PageTransition type="slide-up" transitionKey={pathname}>
 *       {children}
 *     </PageTransition>
 *   );
 * }
 *
 * // With persistent layout
 * <TransitionLayout
 *   header={<Header />}
 *   footer={<Footer />}
 *   sidebar={<Sidebar />}
 *   transitionType="fade"
 *   transitionKey={currentPage}
 * >
 *   <YourPageContent />
 * </TransitionLayout>
 *
 * // React Router
 * function App() {
 *   const location = useLocation();
 *
 *   return (
 *     <RouteTransition routeKey={location.pathname} type="slide-up">
 *       <Routes>
 *         <Route path="/" element={<Home />} />
 *         <Route path="/about" element={<About />} />
 *       </Routes>
 *     </RouteTransition>
 *   );
 * }
 * ```
 */
