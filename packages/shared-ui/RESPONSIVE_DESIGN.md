# Responsive Design System

Complete responsive design implementation for SAHOOL web and admin applications.

## Overview

This responsive design system provides a comprehensive set of components and hooks for building mobile-first, touch-friendly, and RTL-compatible user interfaces.

## Features

- **Mobile-First Approach**: All components are designed with mobile devices as the primary target
- **Touch-Friendly**: Minimum 44px touch targets for optimal mobile usability
- **RTL Support**: Full right-to-left language support for Arabic and Hebrew
- **Breakpoint System**: Consistent breakpoints across all components (sm, md, lg, xl, 2xl)
- **Accessibility**: ARIA labels, keyboard navigation, and screen reader support
- **TypeScript**: Fully typed with comprehensive interfaces

## Breakpoints

Following Tailwind CSS defaults:

| Breakpoint | Min Width | Description |
|------------|-----------|-------------|
| xs (base)  | 0px       | Mobile phones (portrait) |
| sm         | 640px     | Mobile phones (landscape) |
| md         | 768px     | Tablets |
| lg         | 1024px    | Desktops |
| xl         | 1280px    | Large desktops |
| 2xl        | 1536px    | Extra large desktops |

## Components

### 1. ResponsiveContainer

A container component with breakpoint-aware padding and max-width.

#### Usage

```tsx
import { ResponsiveContainer, NarrowContainer, WideContainer } from '@sahool/shared-ui';

// Basic usage
<ResponsiveContainer maxWidth="lg" padding="responsive">
  <h1>Content</h1>
</ResponsiveContainer>

// Narrow container (max-width: md)
<NarrowContainer>
  <article>Article content...</article>
</NarrowContainer>

// Wide container (max-width: 2xl)
<WideContainer>
  <div>Dashboard content...</div>
</WideContainer>

// With RTL support
<ResponsiveContainer rtl>
  <div>محتوى عربي</div>
</ResponsiveContainer>
```

#### Props

```tsx
interface ResponsiveContainerProps {
  children: ReactNode;
  className?: string;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full' | 'none';
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'responsive';
  center?: boolean;
  rtl?: boolean;
  as?: 'div' | 'section' | 'article' | 'main' | 'aside' | 'header' | 'footer';
}
```

#### Variants

- `ResponsiveContainer` - Base container
- `NarrowContainer` - For articles and focused content (max-width: md)
- `WideContainer` - For dashboards and data-heavy layouts (max-width: 2xl)
- `FullWidthContainer` - No max-width constraint
- `Section` - Semantic section with spacing
- `Article` - Semantic article container
- `PageContainer` - Main page wrapper
- `FluidContainer` - Responsive padding without max-width

### 2. ResponsiveGrid

Grid layout with responsive columns.

#### Usage

```tsx
import { ResponsiveGrid, AutoGrid, GridItem } from '@sahool/shared-ui';

// Basic responsive grid
<ResponsiveGrid cols={{ xs: 1, sm: 2, md: 3, lg: 4 }} gap="md">
  {items.map(item => (
    <Card key={item.id}>{item.name}</Card>
  ))}
</ResponsiveGrid>

// Auto-fit grid (columns adjust based on space)
<AutoGrid minColWidth="250px" gap="lg">
  {items.map(item => (
    <Card key={item.id}>{item.name}</Card>
  ))}
</AutoGrid>

// Grid with spanning items
<ResponsiveGrid cols={{ xs: 1, md: 2, lg: 4 }} gap="md">
  <GridItem colSpan={{ xs: 1, md: 2, lg: 2 }}>
    <FeaturedCard />
  </GridItem>
  {items.map(item => (
    <Card key={item.id}>{item.name}</Card>
  ))}
</ResponsiveGrid>
```

#### Props

```tsx
interface ResponsiveGridProps {
  children: ReactNode;
  className?: string;
  cols?: {
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
    '2xl'?: number;
  };
  gap?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | number;
  alignItems?: 'start' | 'center' | 'end' | 'stretch';
  justifyItems?: 'start' | 'center' | 'end' | 'stretch';
  rtl?: boolean;
  autoFit?: boolean;
  minColWidth?: string;
}
```

#### Variants

- `ResponsiveGrid` - Main grid with configurable columns per breakpoint
- `AutoGrid` - Automatically sizes columns based on content
- `MasonryGrid` - Masonry-style column layout
- `SimpleGrid` - Fixed number of columns across all breakpoints
- `FlexGrid` - Flexbox-based alternative to CSS Grid
- `GridItem` - Individual grid item with span control

### 3. MobileNav

Mobile navigation with bottom bar and drawer menu.

#### Usage

```tsx
import { MobileNav, useMobileNav } from '@sahool/shared-ui';
import { Home, Search, User, Bell } from 'lucide-react';

function MyApp() {
  const { createNavItem, activeItem } = useMobileNav('home');

  const navItems = [
    createNavItem('home', 'Home', <Home size={24} />),
    createNavItem('search', 'Search', <Search size={24} />),
    createNavItem('notifications', 'Notifications', <Bell size={24} />, { badge: 5 }),
    createNavItem('profile', 'Profile', <User size={24} />),
  ];

  return (
    <>
      <div className="pb-20">{/* Your content */}</div>

      {/* Bottom navigation (mobile only) */}
      <MobileNav variant="bottom" items={navItems} />

      {/* Drawer navigation (hamburger menu) */}
      <MobileNav
        variant="drawer"
        items={navItems}
        logo={<Logo />}
        footer={<UserProfile />}
      />

      {/* Auto mode: bottom on mobile, drawer on desktop */}
      <MobileNav variant="auto" items={navItems} />
    </>
  );
}
```

#### Props

```tsx
interface MobileNavProps {
  items: NavItem[];
  className?: string;
  rtl?: boolean;
  variant?: 'bottom' | 'drawer' | 'auto';
  logo?: ReactNode;
  header?: ReactNode;
  footer?: ReactNode;
  showLabels?: boolean;
  compact?: boolean;
}

interface NavItem {
  id: string;
  label: string;
  icon?: ReactNode;
  onClick?: () => void;
  href?: string;
  active?: boolean;
  badge?: string | number;
  disabled?: boolean;
}
```

#### Features

- **Bottom Navigation**: Fixed bottom bar with 3-5 items
- **Drawer Menu**: Slide-out menu with hamburger button
- **Auto Mode**: Adapts based on screen size
- **Touch Targets**: Minimum 44px for accessibility
- **Badges**: Show notification counts
- **Keyboard Support**: ESC to close, tab navigation
- **Auto-close**: Closes on navigation or outside click

## Hooks

### 1. useMediaQuery

Custom hook for media queries with SSR support.

#### Usage

```tsx
import { useMediaQuery } from '@sahool/shared-ui';

function MyComponent() {
  const isMobile = useMediaQuery('(max-width: 640px)');
  const isLandscape = useMediaQuery('(orientation: landscape)');
  const prefersReducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)');

  return isMobile ? <MobileView /> : <DesktopView />;
}
```

#### Utility Hooks

```tsx
// Accessibility
const prefersReducedMotion = usePrefersReducedMotion();

// Theme
const prefersDark = usePrefersDarkMode();

// Device detection
const orientation = useOrientation(); // 'portrait' | 'landscape' | null
const hasHover = useHoverSupport(); // true for mouse, false for touch
const isTouchDevice = useTouchDevice(); // true for touch-primary devices
```

### 2. useBreakpoint

Hook for detecting current breakpoint and device type.

#### Usage

```tsx
import { useBreakpoint, useBreakpointValue, useResponsiveValue } from '@sahool/shared-ui';

function MyComponent() {
  const { current, isMobile, isTablet, isDesktop } = useBreakpoint();

  // Get responsive value based on current breakpoint
  const columns = useResponsiveValue({
    xs: 1,
    sm: 2,
    md: 3,
    lg: 4,
    xl: 5,
  });

  // Check if at least a certain breakpoint
  const isLargeScreen = useBreakpointValue('lg');

  return (
    <div>
      <p>Current breakpoint: {current}</p>
      <p>Columns: {columns}</p>
      {isMobile && <MobileBanner />}
    </div>
  );
}
```

#### Return Value

```tsx
interface BreakpointInfo {
  current: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  isSm: boolean;
  isMd: boolean;
  isLg: boolean;
  isXl: boolean;
  is2xl: boolean;
  isMobile: boolean;   // < 768px
  isTablet: boolean;   // ≥768px and <1024px
  isDesktop: boolean;  // ≥1024px
}
```

## Best Practices

### Mobile-First Design

Always start with mobile layout and progressively enhance for larger screens:

```tsx
<ResponsiveGrid
  cols={{
    xs: 1,    // Mobile first
    md: 2,    // Then tablet
    lg: 3,    // Then desktop
  }}
/>
```

### Touch Targets

Ensure all interactive elements meet minimum touch target size (44px):

```tsx
// Good - MobileNav components have 44px+ targets
<MobileNav variant="bottom" items={navItems} />

// Good - Custom buttons with adequate size
<button className="min-h-[44px] min-w-[44px] p-3">
  <Icon size={24} />
</button>
```

### RTL Support

Enable RTL for Arabic/Hebrew content:

```tsx
const isRTL = locale === 'ar' || locale === 'he';

<ResponsiveContainer rtl={isRTL}>
  <ResponsiveGrid rtl={isRTL}>
    {items.map(item => <Card key={item.id}>{item.name}</Card>)}
  </ResponsiveGrid>
</ResponsiveContainer>
```

### Responsive Spacing

Use responsive padding for better mobile experience:

```tsx
// Responsive padding adapts to screen size
<ResponsiveContainer padding="responsive">
  {content}
</ResponsiveContainer>

// Custom responsive spacing with Tailwind
<div className="px-4 py-4 sm:px-6 sm:py-6 md:px-8 md:py-8">
  {content}
</div>
```

### Conditional Rendering

Use breakpoint hooks for conditional rendering:

```tsx
const { isMobile, isDesktop } = useBreakpoint();

return (
  <>
    {isMobile && <MobileLayout />}
    {isDesktop && <DesktopLayout />}
  </>
);
```

### Performance

Avoid unnecessary re-renders by memoizing breakpoint-dependent values:

```tsx
const { isMobile } = useBreakpoint();
const memoizedComponent = useMemo(
  () => isMobile ? <MobileView /> : <DesktopView />,
  [isMobile]
);
```

## Examples

### Complete Page Layout

```tsx
import {
  PageContainer,
  Section,
  ResponsiveGrid,
  MobileNav,
  useMobileNav,
} from '@sahool/shared-ui';

function Dashboard() {
  const { createNavItem } = useMobileNav('dashboard');

  const navItems = [
    createNavItem('dashboard', 'Dashboard', <HomeIcon />),
    createNavItem('analytics', 'Analytics', <ChartIcon />),
    createNavItem('settings', 'Settings', <SettingsIcon />),
  ];

  return (
    <>
      <PageContainer maxWidth="xl" padding="responsive">
        <Section>
          <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
        </Section>

        <Section>
          <ResponsiveGrid cols={{ xs: 1, sm: 2, lg: 4 }} gap="lg">
            <StatCard title="Users" value="12,345" />
            <StatCard title="Revenue" value="$45,678" />
            <StatCard title="Orders" value="890" />
            <StatCard title="Conversion" value="3.4%" />
          </ResponsiveGrid>
        </Section>
      </PageContainer>

      <MobileNav variant="auto" items={navItems} />
    </>
  );
}
```

### Responsive Product Grid

```tsx
import { ResponsiveContainer, ResponsiveGrid } from '@sahool/shared-ui';

function ProductGrid({ products }) {
  return (
    <ResponsiveContainer maxWidth="xl" padding="responsive">
      <h2 className="text-2xl font-bold mb-6">Products</h2>

      <ResponsiveGrid
        cols={{ xs: 1, sm: 2, md: 3, lg: 4, xl: 5 }}
        gap="lg"
      >
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </ResponsiveGrid>
    </ResponsiveContainer>
  );
}
```

### Adaptive Layout

```tsx
import { useBreakpoint, ResponsiveContainer } from '@sahool/shared-ui';

function AdaptiveLayout() {
  const { isMobile, isDesktop } = useBreakpoint();

  return (
    <ResponsiveContainer maxWidth="xl" padding="responsive">
      {isMobile ? (
        <MobileLayout />
      ) : isDesktop ? (
        <DesktopLayout />
      ) : (
        <TabletLayout />
      )}
    </ResponsiveContainer>
  );
}
```

## Testing

### Testing Responsive Components

```tsx
import { render, screen } from '@testing-library/react';
import { ResponsiveContainer } from '@sahool/shared-ui';

describe('ResponsiveContainer', () => {
  it('renders children', () => {
    render(
      <ResponsiveContainer>
        <div>Test content</div>
      </ResponsiveContainer>
    );

    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('applies RTL direction', () => {
    const { container } = render(
      <ResponsiveContainer rtl>
        <div>محتوى</div>
      </ResponsiveContainer>
    );

    expect(container.firstChild).toHaveAttribute('dir', 'rtl');
  });
});
```

### Testing with Media Queries

```tsx
import { renderHook } from '@testing-library/react-hooks';
import { useMediaQuery } from '@sahool/shared-ui';

describe('useMediaQuery', () => {
  it('returns false initially (SSR)', () => {
    const { result } = renderHook(() => useMediaQuery('(min-width: 768px)'));
    expect(result.current).toBe(false);
  });
});
```

## Migration Guide

### From Custom Responsive Code

If you have custom responsive code, migrate to these components:

#### Before

```tsx
<div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    {items.map(item => <Card key={item.id}>{item.name}</Card>)}
  </div>
</div>
```

#### After

```tsx
<ResponsiveContainer maxWidth="xl" padding="responsive">
  <ResponsiveGrid cols={{ xs: 1, sm: 2, lg: 4 }} gap="md">
    {items.map(item => <Card key={item.id}>{item.name}</Card>)}
  </ResponsiveGrid>
</ResponsiveContainer>
```

### Benefits

- ✅ Consistent spacing across apps
- ✅ Built-in RTL support
- ✅ TypeScript type safety
- ✅ Reduced code duplication
- ✅ Better maintainability

## Troubleshooting

### Hydration Mismatch

If you see hydration warnings, ensure you're handling SSR correctly:

```tsx
const { isMobile } = useBreakpoint();

// ❌ Bad - causes hydration mismatch
return isMobile ? <MobileView /> : <DesktopView />;

// ✅ Good - render both initially, hide with CSS
return (
  <>
    <div className="md:hidden"><MobileView /></div>
    <div className="hidden md:block"><DesktopView /></div>
  </>
);
```

### Mobile Nav Not Showing

Ensure you have space for bottom navigation:

```tsx
// Add padding-bottom to content
<div className="pb-20 md:pb-0">
  {content}
</div>

<MobileNav variant="auto" items={navItems} />
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- iOS Safari 14+
- Chrome Android 90+

## Performance Considerations

- All hooks use `useEffect` to prevent SSR issues
- Media query listeners are automatically cleaned up
- Grid components use CSS Grid for optimal performance
- No unnecessary re-renders with proper memoization

## Accessibility

All components follow WCAG 2.1 Level AA guidelines:

- ✅ Minimum 44px touch targets
- ✅ ARIA labels and roles
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ Color contrast compliance
- ✅ Focus indicators

## License

Part of the SAHOOL Unified Platform - Internal Use Only
