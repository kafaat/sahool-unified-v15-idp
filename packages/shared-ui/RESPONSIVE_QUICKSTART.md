# Responsive Design - Quick Start Guide

Get started with SAHOOL's responsive design system in 5 minutes.

## Installation

The responsive components are part of `@sahool/shared-ui`:

```bash
# Already installed in monorepo
npm install @sahool/shared-ui
```

## Basic Usage

### 1. Simple Page Layout

```tsx
import { ResponsiveContainer, ResponsiveGrid } from '@sahool/shared-ui';

function MyPage() {
  return (
    <ResponsiveContainer maxWidth="lg" padding="responsive">
      <h1 className="text-3xl font-bold mb-6">My Page</h1>

      <ResponsiveGrid cols={{ xs: 1, md: 2, lg: 3 }} gap="md">
        <Card>Item 1</Card>
        <Card>Item 2</Card>
        <Card>Item 3</Card>
      </ResponsiveGrid>
    </ResponsiveContainer>
  );
}
```

### 2. Mobile Navigation

```tsx
import { MobileNav, useMobileNav } from '@sahool/shared-ui';
import { Home, Search, User } from 'lucide-react';

function App() {
  const { createNavItem } = useMobileNav('home');

  const navItems = [
    createNavItem('home', 'Home', <Home size={24} />),
    createNavItem('search', 'Search', <Search size={24} />),
    createNavItem('profile', 'Profile', <User size={24} />),
  ];

  return (
    <>
      <div className="pb-20">{/* Your content */}</div>
      <MobileNav variant="bottom" items={navItems} />
    </>
  );
}
```

### 3. Responsive Hooks

```tsx
import { useBreakpoint } from '@sahool/shared-ui';

function MyComponent() {
  const { isMobile, isDesktop } = useBreakpoint();

  return (
    <div>
      {isMobile ? <MobileView /> : <DesktopView />}
    </div>
  );
}
```

## Common Patterns

### Dashboard Layout

```tsx
import { WideContainer, ResponsiveGrid } from '@sahool/shared-ui';

function Dashboard() {
  return (
    <WideContainer padding="responsive">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      {/* Stats */}
      <ResponsiveGrid cols={{ xs: 1, sm: 2, lg: 4 }} gap="lg" className="mb-8">
        <StatCard title="Users" value="12,345" />
        <StatCard title="Revenue" value="$45,678" />
        <StatCard title="Orders" value="890" />
        <StatCard title="Conversion" value="3.4%" />
      </ResponsiveGrid>

      {/* Charts */}
      <ResponsiveGrid cols={{ xs: 1, lg: 2 }} gap="lg">
        <ChartCard title="Sales" />
        <ChartCard title="Traffic" />
      </ResponsiveGrid>
    </WideContainer>
  );
}
```

### Article Page

```tsx
import { NarrowContainer } from '@sahool/shared-ui';

function Article() {
  return (
    <NarrowContainer padding="responsive">
      <article className="prose prose-lg">
        <h1>Article Title</h1>
        <p>Article content with optimal reading width...</p>
      </article>
    </NarrowContainer>
  );
}
```

### Product Grid

```tsx
import { ResponsiveContainer, AutoGrid } from '@sahool/shared-ui';

function Products() {
  return (
    <ResponsiveContainer maxWidth="xl" padding="responsive">
      <h2 className="text-2xl font-bold mb-6">Products</h2>

      <AutoGrid minColWidth="280px" gap="lg">
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </AutoGrid>
    </ResponsiveContainer>
  );
}
```

### Conditional Rendering

```tsx
import { useBreakpoint, useMediaQuery } from '@sahool/shared-ui';

function AdaptiveComponent() {
  const { current, isMobile } = useBreakpoint();
  const isTouchDevice = useMediaQuery('(hover: none)');

  return (
    <div>
      <p>Breakpoint: {current}</p>
      {isMobile && <MobileBanner />}
      {isTouchDevice && <TouchInstructions />}
    </div>
  );
}
```

### RTL Support (Arabic/Hebrew)

```tsx
import { ResponsiveContainer, ResponsiveGrid } from '@sahool/shared-ui';

function ArabicPage() {
  return (
    <ResponsiveContainer maxWidth="lg" padding="responsive" rtl>
      <h1 className="text-3xl font-bold mb-6">العنوان</h1>

      <ResponsiveGrid cols={{ xs: 1, sm: 2, md: 3 }} gap="md" rtl>
        <Card>بطاقة 1</Card>
        <Card>بطاقة 2</Card>
        <Card>بطاقة 3</Card>
      </ResponsiveGrid>
    </ResponsiveContainer>
  );
}
```

## Component Cheat Sheet

### Containers

```tsx
// Standard container with responsive padding
<ResponsiveContainer maxWidth="lg" padding="responsive">

// Narrow container for articles (max-width: md)
<NarrowContainer>

// Wide container for dashboards (max-width: 2xl)
<WideContainer>

// Full width with no constraint
<FullWidthContainer>

// Semantic page container
<PageContainer>

// Semantic section with spacing
<Section>
```

### Grids

```tsx
// Responsive grid with breakpoint-specific columns
<ResponsiveGrid cols={{ xs: 1, sm: 2, md: 3, lg: 4 }} gap="md">

// Auto-fit grid (columns adjust automatically)
<AutoGrid minColWidth="250px" gap="lg">

// Simple grid (fixed columns)
<SimpleGrid cols={3} gap="md">

// Grid item with span
<GridItem colSpan={{ xs: 1, md: 2 }}>
```

### Navigation

```tsx
// Bottom navigation (mobile)
<MobileNav variant="bottom" items={navItems} />

// Drawer navigation (hamburger menu)
<MobileNav variant="drawer" items={navItems} logo={<Logo />} />

// Auto mode (adapts to screen size)
<MobileNav variant="auto" items={navItems} />
```

### Hooks

```tsx
// Get current breakpoint and device type
const { current, isMobile, isTablet, isDesktop } = useBreakpoint();

// Custom media query
const isMobile = useMediaQuery('(max-width: 640px)');

// Responsive value based on breakpoint
const columns = useResponsiveValue({ xs: 1, sm: 2, md: 3, lg: 4 });

// Check if at least a certain breakpoint
const isLargeScreen = useBreakpointValue('lg');

// Device detection
const isTouchDevice = useTouchDevice();
const hasHover = useHoverSupport();

// Accessibility
const prefersReducedMotion = usePrefersReducedMotion();
const prefersDark = usePrefersDarkMode();
```

## Props Quick Reference

### ResponsiveContainer

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| maxWidth | 'sm' \| 'md' \| 'lg' \| 'xl' \| '2xl' \| 'full' \| 'none' | 'xl' | Maximum width |
| padding | 'none' \| 'sm' \| 'md' \| 'lg' \| 'xl' \| 'responsive' | 'responsive' | Padding size |
| center | boolean | true | Center horizontally |
| rtl | boolean | false | Right-to-left support |
| as | string | 'div' | HTML element type |

### ResponsiveGrid

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| cols | object | { xs: 1, sm: 2, md: 3, lg: 4 } | Columns per breakpoint |
| gap | 'none' \| 'sm' \| 'md' \| 'lg' \| 'xl' | 'md' | Gap between items |
| autoFit | boolean | false | Auto-fit columns |
| minColWidth | string | '250px' | Min column width (autoFit) |
| rtl | boolean | false | Right-to-left support |

### MobileNav

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| items | NavItem[] | required | Navigation items |
| variant | 'bottom' \| 'drawer' \| 'auto' | 'auto' | Navigation style |
| showLabels | boolean | true | Show labels (bottom) |
| compact | boolean | false | Compact mode |
| logo | ReactNode | - | Logo (drawer) |
| footer | ReactNode | - | Footer content (drawer) |
| rtl | boolean | false | Right-to-left support |

## Tips

1. **Always use mobile-first**: Start with `xs` and add larger breakpoints as needed
2. **Touch targets**: Ensure interactive elements are at least 44px for mobile
3. **RTL support**: Add `rtl` prop for Arabic/Hebrew content
4. **Responsive padding**: Use `padding="responsive"` for optimal spacing across devices
5. **Auto mode**: Use `variant="auto"` for navigation to adapt automatically

## Next Steps

- Read the full documentation: [RESPONSIVE_DESIGN.md](./RESPONSIVE_DESIGN.md)
- View examples: [ResponsiveDesign.example.tsx](./src/components/ResponsiveDesign.example.tsx)
- Explore breakpoints: Check `useBreakpoint.ts` for available helpers

## Need Help?

- Check the full documentation for detailed examples
- Review the example components for implementation patterns
- Test your components at different breakpoints using browser DevTools
