# Responsive Components Visual Guide

## Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    RESPONSIVE DESIGN SYSTEM                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📦 CONTAINERS                                               │
│  ├── ResponsiveContainer    [Base container, configurable]  │
│  ├── NarrowContainer        [max-width: md, for articles]   │
│  ├── WideContainer          [max-width: 2xl, for dashboards]│
│  ├── FullWidthContainer     [No max-width]                  │
│  ├── PageContainer          [Main page wrapper]             │
│  ├── Section                [Semantic section]              │
│  ├── Article                [Semantic article]              │
│  └── FluidContainer         [Responsive padding, no max-w]  │
│                                                              │
│  📐 GRIDS                                                    │
│  ├── ResponsiveGrid         [Main grid, columns per breakpt]│
│  ├── AutoGrid               [Auto-fit columns]              │
│  ├── MasonryGrid            [Column-based masonry]          │
│  ├── SimpleGrid             [Fixed columns]                 │
│  ├── FlexGrid               [Flexbox-based]                 │
│  └── GridItem               [Individual item with span]     │
│                                                              │
│  🧭 NAVIGATION                                               │
│  └── MobileNav              [Bottom bar + drawer]           │
│      ├── variant="bottom"   [Fixed bottom navigation]       │
│      ├── variant="drawer"   [Hamburger menu]                │
│      └── variant="auto"     [Adaptive]                      │
│                                                              │
│  🎣 HOOKS                                                    │
│  ├── useMediaQuery          [Custom media queries]          │
│  ├── useBreakpoint          [Current breakpoint]            │
│  ├── useBreakpointValue     [Check min breakpoint]          │
│  ├── useResponsiveValue     [Get value per breakpoint]      │
│  ├── usePrefersReducedMotion [Accessibility]                │
│  ├── usePrefersDarkMode     [Theme preference]              │
│  ├── useOrientation         [Portrait/landscape]            │
│  ├── useHoverSupport        [Mouse vs touch]                │
│  └── useTouchDevice         [Touch detection]               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Breakpoint System

```
┌────────────────────────────────────────────────────────────────┐
│ BREAKPOINTS (Mobile-First)                                     │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  xs (base)  ─────────────────────►  0px                       │
│  📱 Mobile Portrait                                             │
│                                                                 │
│  sm  ────────────────────────────►  640px                     │
│  📱 Mobile Landscape                                            │
│                                                                 │
│  md  ────────────────────────────►  768px                     │
│  📱 Tablets                                                     │
│                                                                 │
│  lg  ────────────────────────────►  1024px                    │
│  💻 Desktops                                                    │
│                                                                 │
│  xl  ────────────────────────────►  1280px                    │
│  💻 Large Desktops                                              │
│                                                                 │
│  2xl ────────────────────────────►  1536px                    │
│  🖥️  Extra Large Desktops                                      │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Layout Examples

### 1. Basic Page Layout

```
┌─────────────────────────────────────────────────┐
│  ResponsiveContainer (max-width: xl)            │
│  ┌───────────────────────────────────────────┐  │
│  │                                           │  │
│  │  <h1>Page Title</h1>                     │  │
│  │                                           │  │
│  │  ResponsiveGrid (cols: xs=1, md=2, lg=3)│  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐       │  │
│  │  │ Card 1 │ │ Card 2 │ │ Card 3 │       │  │
│  │  └────────┘ └────────┘ └────────┘       │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐       │  │
│  │  │ Card 4 │ │ Card 5 │ │ Card 6 │       │  │
│  │  └────────┘ └────────┘ └────────┘       │  │
│  │                                           │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 2. Dashboard Layout

```
┌───────────────────────────────────────────────────┐
│  WideContainer (max-width: 2xl)                   │
│  ┌─────────────────────────────────────────────┐  │
│  │  <h1>Dashboard</h1>                         │  │
│  │                                              │  │
│  │  ResponsiveGrid (cols: xs=1, sm=2, lg=4)   │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │  │
│  │  │Stat 1│ │Stat 2│ │Stat 3│ │Stat 4│       │  │
│  │  └──────┘ └──────┘ └──────┘ └──────┘       │  │
│  │                                              │  │
│  │  ResponsiveGrid (cols: xs=1, lg=2)         │  │
│  │  ┌────────────────┐ ┌────────────────┐     │  │
│  │  │    Chart 1     │ │    Chart 2     │     │  │
│  │  │                │ │                │     │  │
│  │  └────────────────┘ └────────────────┘     │  │
│  │                                              │  │
│  └─────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────┘
```

### 3. Article Layout

```
┌─────────────────────────────────┐
│ NarrowContainer (max-width: md) │
│  ┌───────────────────────────┐  │
│  │                           │  │
│  │  <article>                │  │
│  │    <h1>Article Title</h1>│  │
│  │                           │  │
│  │    <p>Paragraph 1...</p>  │  │
│  │                           │  │
│  │    <p>Paragraph 2...</p>  │  │
│  │                           │  │
│  │    <p>Paragraph 3...</p>  │  │
│  │                           │  │
│  │  </article>               │  │
│  │                           │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### 4. Mobile Navigation - Bottom Bar

```
┌─────────────────────────────────┐
│                                 │
│     Your Page Content           │
│                                 │
│                                 │
│                                 │
├─────────────────────────────────┤ ◄─ Fixed Bottom
│  🏠     🔍     🔔(3)    👤      │
│ Home  Search  Alerts  Profile   │
└─────────────────────────────────┘
```

### 5. Mobile Navigation - Drawer

```
┌───────────┐  ┌─────────────────┐
│ [☰] LOGO  │  │     Content     │
├───────────┤  │                 │
│           │  │                 │
│ 🏠 Home   │  │                 │
│           │  │                 │
│ 🔍 Search │  │                 │
│           │  │                 │
│ 🔔 Alerts │  │                 │
│    (3)    │  │                 │
│           │  │                 │
│ ⚙️ Settings│  │                 │
│           │  │                 │
│ 👤 Profile│  │                 │
│           │  │                 │
├───────────┤  │                 │
│  Footer   │  │                 │
└───────────┘  └─────────────────┘
   Drawer           Page
```

## Responsive Behavior

### Container Padding (Responsive Mode)

```
Mobile (xs, sm):
┌────┬──────────────────────────┬────┐
│16px│      Content             │16px│
└────┴──────────────────────────┴────┘

Tablet (md):
┌──────┬────────────────────────┬──────┐
│ 32px │      Content           │ 32px │
└──────┴────────────────────────┴──────┘

Desktop (lg, xl):
┌─────────┬──────────────────┬─────────┐
│  48px   │    Content       │  48px   │
└─────────┴──────────────────┴─────────┘

Large Desktop (2xl):
┌──────────┬────────────────┬──────────┐
│   64px   │   Content      │   64px   │
└──────────┴────────────────┴──────────┘
```

### Grid Columns Behavior

```
Mobile (xs):
┌─────────────────┐
│     Item 1      │
├─────────────────┤
│     Item 2      │
├─────────────────┤
│     Item 3      │
└─────────────────┘

Tablet (md):
┌────────┬────────┐
│ Item 1 │ Item 2 │
├────────┼────────┤
│ Item 3 │ Item 4 │
└────────┴────────┘

Desktop (lg):
┌──────┬──────┬──────┐
│Item 1│Item 2│Item 3│
├──────┼──────┼──────┤
│Item 4│Item 5│Item 6│
└──────┴──────┴──────┘
```

## RTL Support

### LTR (Left-to-Right)

```
┌─────────────────────────────────┐
│ Logo                    Menu ☰  │  ◄─ Header
├─────────────────────────────────┤
│ ┌──────┐ ┌──────┐ ┌──────┐     │
│ │  1   │ │  2   │ │  3   │     │  ◄─ Content flows →
│ └──────┘ └──────┘ └──────┘     │
└─────────────────────────────────┘
```

### RTL (Right-to-Left)

```
┌─────────────────────────────────┐
│  ☰ Menu                    Logo │  ◄─ Header
├─────────────────────────────────┤
│     ┌──────┐ ┌──────┐ ┌──────┐ │
│     │  3   │ │  2   │ │  1   │ │  ◄─ Content flows ←
│     └──────┘ └──────┘ └──────┘ │
└─────────────────────────────────┘
```

## Touch Targets

### Mobile Touch Targets (Minimum 44px)

```
❌ Too Small (32px):
┌────────┐
│  Icon  │  ◄─ Hard to tap accurately
└────────┘

✅ Good (44px):
┌──────────┐
│   Icon   │  ◄─ Easy to tap
└──────────┘

✅ Better (56px):
┌────────────┐
│    Icon    │  ◄─ Very comfortable
└────────────┘
```

## Common Patterns

### Pattern 1: Feature Grid

```tsx
<ResponsiveContainer maxWidth="xl" padding="responsive">
  <ResponsiveGrid cols={{ xs: 1, sm: 2, lg: 3 }} gap="lg">
    <FeatureCard icon="🚀" title="Fast" />
    <FeatureCard icon="🔒" title="Secure" />
    <FeatureCard icon="📱" title="Mobile" />
  </ResponsiveGrid>
</ResponsiveContainer>
```

### Pattern 2: Hero + Content

```tsx
<>
  <Section as="section">
    <h1>Hero Title</h1>
    <p>Hero description</p>
  </Section>

  <Section>
    <ResponsiveGrid cols={{ xs: 1, md: 2, lg: 3 }} gap="md">
      {/* Cards */}
    </ResponsiveGrid>
  </Section>
</>
```

### Pattern 3: Sidebar Layout

```tsx
<ResponsiveGrid cols={{ xs: 1, lg: 4 }} gap="lg">
  <GridItem colSpan={{ xs: 1, lg: 3 }}>
    {/* Main content */}
  </GridItem>
  <aside>
    {/* Sidebar */}
  </aside>
</ResponsiveGrid>
```

## Decision Tree

```
Need a container?
│
├─ Reading content (article, blog)
│  └─ Use: NarrowContainer
│
├─ Dashboard with lots of data
│  └─ Use: WideContainer
│
├─ Standard page
│  └─ Use: ResponsiveContainer (maxWidth="lg" or "xl")
│
└─ Full-width section
   └─ Use: FullWidthContainer

Need a grid?
│
├─ Fixed columns per breakpoint
│  └─ Use: ResponsiveGrid with cols prop
│
├─ Flexible, auto-sizing columns
│  └─ Use: AutoGrid with minColWidth
│
├─ Same columns everywhere
│  └─ Use: SimpleGrid with cols number
│
└─ Pinterest-style layout
   └─ Use: MasonryGrid

Need navigation?
│
├─ Mobile app with 3-5 main sections
│  └─ Use: MobileNav variant="bottom"
│
├─ Many menu items
│  └─ Use: MobileNav variant="drawer"
│
└─ Want automatic adaptation
   └─ Use: MobileNav variant="auto"

Need breakpoint detection?
│
├─ Custom media query
│  └─ Use: useMediaQuery()
│
├─ Current breakpoint or device type
│  └─ Use: useBreakpoint()
│
└─ Different values per breakpoint
   └─ Use: useResponsiveValue()
```

## Best Practices Checklist

### Design
- ✅ Start with mobile layout first
- ✅ Test at all breakpoints (xs, sm, md, lg, xl, 2xl)
- ✅ Ensure 44px minimum touch targets
- ✅ Use consistent spacing (4, 8, 16, 24, 32, 48, 64)
- ✅ Test RTL layout for Arabic/Hebrew

### Code
- ✅ Use semantic HTML (section, article, main, etc.)
- ✅ Add proper ARIA labels
- ✅ Include keyboard navigation
- ✅ Handle SSR properly (avoid hydration mismatches)
- ✅ Memoize expensive responsive calculations

### Accessibility
- ✅ Test with screen reader
- ✅ Ensure keyboard navigation works
- ✅ Respect prefers-reduced-motion
- ✅ Maintain color contrast (WCAG AA)
- ✅ Add focus indicators

### Performance
- ✅ Use CSS for hiding/showing when possible
- ✅ Avoid unnecessary re-renders
- ✅ Lazy load images on mobile
- ✅ Optimize bundle size (tree-shaking)
- ✅ Test on slow connections

## Quick Reference Card

```
Component          | When to Use
-------------------|----------------------------------
ResponsiveContainer| Standard content container
NarrowContainer   | Articles, reading content
WideContainer     | Dashboards, data tables
ResponsiveGrid    | Product grids, card layouts
AutoGrid          | Unknown number of items
MobileNav         | App navigation (bottom/drawer)

Hook              | Returns
------------------|----------------------------------
useBreakpoint     | { current, isMobile, isDesktop }
useMediaQuery     | boolean (matches query)
useResponsiveValue| Value based on breakpoint
useTouchDevice    | boolean (is touch device)
```

## Getting Started

1. **Import components**:
   ```tsx
   import { ResponsiveContainer, ResponsiveGrid } from '@sahool/shared-ui';
   ```

2. **Wrap your content**:
   ```tsx
   <ResponsiveContainer maxWidth="lg" padding="responsive">
     {/* Your content */}
   </ResponsiveContainer>
   ```

3. **Add responsive grid**:
   ```tsx
   <ResponsiveGrid cols={{ xs: 1, md: 2, lg: 3 }} gap="md">
     {items.map(item => <Card key={item.id} />)}
   </ResponsiveGrid>
   ```

4. **Use breakpoint hooks**:
   ```tsx
   const { isMobile } = useBreakpoint();
   ```

5. **Test at different sizes**: Open DevTools and test mobile, tablet, and desktop views

---

For detailed documentation, see [RESPONSIVE_DESIGN.md](./RESPONSIVE_DESIGN.md)
For quick start guide, see [RESPONSIVE_QUICKSTART.md](./RESPONSIVE_QUICKSTART.md)
