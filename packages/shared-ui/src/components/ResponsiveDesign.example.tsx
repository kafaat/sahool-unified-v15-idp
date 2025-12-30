'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// Responsive Design Components - Usage Examples
// تصميم متجاوب - أمثلة الاستخدام
// ═══════════════════════════════════════════════════════════════════════════════

import {
  ResponsiveContainer,
  NarrowContainer,
  WideContainer,
  PageContainer,
  Section,
  ResponsiveGrid,
  AutoGrid,
  GridItem,
  MobileNav,
  useMobileNav,
  useBreakpoint,
  useMediaQuery,
  useResponsiveValue,
} from '../index';

import { Home, Search, User, Bell, Settings } from 'lucide-react';

/**
 * Example 1: Basic Responsive Container
 */
export function BasicContainerExample() {
  return (
    <ResponsiveContainer maxWidth="lg" padding="responsive">
      <h1 className="text-3xl font-bold mb-4">Welcome to SAHOOL</h1>
      <p className="text-gray-600">
        This content is centered and has responsive padding that adapts to screen size.
      </p>
    </ResponsiveContainer>
  );
}

/**
 * Example 2: Multiple Container Types
 */
export function ContainerTypesExample() {
  return (
    <>
      {/* Narrow container for articles */}
      <NarrowContainer padding="responsive">
        <article>
          <h2 className="text-2xl font-bold mb-4">Article Title</h2>
          <p className="text-gray-700 leading-relaxed">
            This narrow container is perfect for reading long-form content.
            It keeps the line length optimal for readability.
          </p>
        </article>
      </NarrowContainer>

      {/* Wide container for dashboards */}
      <WideContainer padding="responsive" className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Dashboard</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-6 rounded-lg shadow">Metric 1</div>
          <div className="bg-white p-6 rounded-lg shadow">Metric 2</div>
          <div className="bg-white p-6 rounded-lg shadow">Metric 3</div>
        </div>
      </WideContainer>
    </>
  );
}

/**
 * Example 3: Responsive Grid with Cards
 */
export function ResponsiveGridExample() {
  const items = Array.from({ length: 12 }, (_, i) => ({
    id: i + 1,
    title: `Item ${i + 1}`,
    description: 'Sample description for this item',
  }));

  return (
    <ResponsiveContainer maxWidth="xl" padding="responsive">
      <h2 className="text-2xl font-bold mb-6">Product Grid</h2>

      {/* 1 column on mobile, 2 on tablet, 3 on desktop */}
      <ResponsiveGrid
        cols={{ xs: 1, sm: 2, md: 3, lg: 4 }}
        gap="lg"
      >
        {items.map((item) => (
          <div
            key={item.id}
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
          >
            <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
            <p className="text-gray-600">{item.description}</p>
          </div>
        ))}
      </ResponsiveGrid>
    </ResponsiveContainer>
  );
}

/**
 * Example 4: Auto-Fit Grid
 */
export function AutoGridExample() {
  const items = Array.from({ length: 8 }, (_, i) => ({
    id: i + 1,
    title: `Card ${i + 1}`,
  }));

  return (
    <ResponsiveContainer maxWidth="xl" padding="responsive">
      <h2 className="text-2xl font-bold mb-6">Auto-Fit Grid</h2>

      {/* Automatically fits as many columns as possible */}
      <AutoGrid minColWidth="250px" gap="md">
        {items.map((item) => (
          <div
            key={item.id}
            className="bg-white p-6 rounded-lg shadow"
          >
            <h3 className="text-lg font-semibold">{item.title}</h3>
          </div>
        ))}
      </AutoGrid>
    </ResponsiveContainer>
  );
}

/**
 * Example 5: Grid with Spanning Items
 */
export function GridSpanExample() {
  return (
    <ResponsiveContainer maxWidth="xl" padding="responsive">
      <h2 className="text-2xl font-bold mb-6">Featured Layout</h2>

      <ResponsiveGrid
        cols={{ xs: 1, md: 2, lg: 4 }}
        gap="md"
      >
        {/* Featured item spans 2 columns on desktop */}
        <GridItem colSpan={{ xs: 1, md: 2, lg: 2 }} rowSpan={{ lg: 2 }}>
          <div className="bg-blue-100 p-8 rounded-lg h-full flex items-center justify-center">
            <h3 className="text-2xl font-bold">Featured</h3>
          </div>
        </GridItem>

        {/* Regular items */}
        {Array.from({ length: 6 }, (_, i) => (
          <div
            key={i}
            className="bg-white p-6 rounded-lg shadow"
          >
            <h3 className="text-lg font-semibold">Item {i + 1}</h3>
          </div>
        ))}
      </ResponsiveGrid>
    </ResponsiveContainer>
  );
}

/**
 * Example 6: Mobile Navigation - Bottom Bar
 */
export function MobileBottomNavExample() {
  const { createNavItem, activeItem } = useMobileNav('home');

  const navItems = [
    createNavItem('home', 'Home', <Home size={24} />),
    createNavItem('search', 'Search', <Search size={24} />),
    createNavItem('notifications', 'Alerts', <Bell size={24} />, { badge: 5 }),
    createNavItem('profile', 'Profile', <User size={24} />),
  ];

  return (
    <>
      <div className="pb-20">
        {/* Your page content */}
        <ResponsiveContainer maxWidth="lg" padding="responsive">
          <h1 className="text-2xl font-bold mb-4">Current: {activeItem}</h1>
          <p className="text-gray-600">
            The bottom navigation appears on mobile devices.
            Tap the icons below to navigate.
          </p>
        </ResponsiveContainer>
      </div>

      {/* Bottom navigation */}
      <MobileNav variant="bottom" items={navItems} />
    </>
  );
}

/**
 * Example 7: Mobile Navigation - Drawer Menu
 */
export function MobileDrawerNavExample() {
  const { createNavItem } = useMobileNav('dashboard');

  const navItems = [
    createNavItem('dashboard', 'Dashboard', <Home size={24} />),
    createNavItem('search', 'Search', <Search size={24} />),
    createNavItem('notifications', 'Notifications', <Bell size={24} />, { badge: 3 }),
    createNavItem('settings', 'Settings', <Settings size={24} />),
    createNavItem('profile', 'Profile', <User size={24} />),
  ];

  return (
    <>
      <ResponsiveContainer maxWidth="lg" padding="responsive">
        <h1 className="text-2xl font-bold mb-4">Drawer Navigation Example</h1>
        <p className="text-gray-600">
          Click the hamburger menu in the top-right corner to open the navigation drawer.
        </p>
      </ResponsiveContainer>

      {/* Drawer navigation */}
      <MobileNav
        variant="drawer"
        items={navItems}
        logo={<div className="text-xl font-bold">SAHOOL</div>}
        footer={
          <div className="text-sm text-gray-500">
            Version 1.0.0
          </div>
        }
      />
    </>
  );
}

/**
 * Example 8: Auto Navigation (Bottom on Mobile, Drawer on Desktop)
 */
export function AutoNavExample() {
  const { createNavItem } = useMobileNav('home');

  const navItems = [
    createNavItem('home', 'Home', <Home size={24} />),
    createNavItem('search', 'Search', <Search size={24} />),
    createNavItem('notifications', 'Notifications', <Bell size={24} />, { badge: 5 }),
    createNavItem('profile', 'Profile', <User size={24} />),
  ];

  return (
    <>
      <div className="pb-20 md:pb-0">
        <ResponsiveContainer maxWidth="lg" padding="responsive">
          <h1 className="text-2xl font-bold mb-4">Auto Navigation</h1>
          <p className="text-gray-600">
            Shows bottom nav on mobile, drawer on larger screens.
          </p>
        </ResponsiveContainer>
      </div>

      {/* Auto navigation */}
      <MobileNav variant="auto" items={navItems} />
    </>
  );
}

/**
 * Example 9: Using Breakpoint Hooks
 */
export function BreakpointHooksExample() {
  const { current, isMobile, isTablet, isDesktop } = useBreakpoint();
  const isTouchDevice = useMediaQuery('(hover: none)');

  // Responsive value
  const columns = useResponsiveValue({
    xs: 1,
    sm: 2,
    md: 3,
    lg: 4,
  });

  return (
    <ResponsiveContainer maxWidth="lg" padding="responsive">
      <h2 className="text-2xl font-bold mb-4">Breakpoint Information</h2>

      <div className="bg-white p-6 rounded-lg shadow space-y-2">
        <p>
          <strong>Current Breakpoint:</strong> {current}
        </p>
        <p>
          <strong>Device Type:</strong>{' '}
          {isMobile ? 'Mobile' : isTablet ? 'Tablet' : 'Desktop'}
        </p>
        <p>
          <strong>Touch Device:</strong> {isTouchDevice ? 'Yes' : 'No'}
        </p>
        <p>
          <strong>Responsive Columns:</strong> {columns}
        </p>
      </div>

      {/* Conditional rendering based on breakpoint */}
      {isMobile ? (
        <div className="mt-4 bg-blue-100 p-4 rounded">
          Mobile-specific content
        </div>
      ) : (
        <div className="mt-4 bg-green-100 p-4 rounded">
          Desktop-specific content
        </div>
      )}
    </ResponsiveContainer>
  );
}

/**
 * Example 10: RTL Support
 */
export function RTLExample() {
  return (
    <>
      {/* English (LTR) */}
      <ResponsiveContainer maxWidth="lg" padding="responsive">
        <h2 className="text-2xl font-bold mb-4">English (Left-to-Right)</h2>
        <ResponsiveGrid cols={{ xs: 1, sm: 2, md: 3 }} gap="md">
          <div className="bg-white p-4 rounded shadow">Card 1</div>
          <div className="bg-white p-4 rounded shadow">Card 2</div>
          <div className="bg-white p-4 rounded shadow">Card 3</div>
        </ResponsiveGrid>
      </ResponsiveContainer>

      {/* Arabic (RTL) */}
      <ResponsiveContainer maxWidth="lg" padding="responsive" rtl>
        <h2 className="text-2xl font-bold mb-4">العربية (من اليمين إلى اليسار)</h2>
        <ResponsiveGrid cols={{ xs: 1, sm: 2, md: 3 }} gap="md" rtl>
          <div className="bg-white p-4 rounded shadow">بطاقة 1</div>
          <div className="bg-white p-4 rounded shadow">بطاقة 2</div>
          <div className="bg-white p-4 rounded shadow">بطاقة 3</div>
        </ResponsiveGrid>
      </ResponsiveContainer>
    </>
  );
}

/**
 * Example 11: Complete Page Layout
 */
export function CompletePageExample() {
  const { createNavItem } = useMobileNav('home');

  const navItems = [
    createNavItem('home', 'Home', <Home size={24} />),
    createNavItem('search', 'Search', <Search size={24} />),
    createNavItem('notifications', 'Notifications', <Bell size={24} />, { badge: 3 }),
    createNavItem('profile', 'Profile', <User size={24} />),
  ];

  return (
    <>
      {/* Main page content */}
      <PageContainer maxWidth="xl" padding="responsive">
        {/* Hero section */}
        <Section>
          <h1 className="text-4xl font-bold mb-4">Welcome to SAHOOL</h1>
          <p className="text-xl text-gray-600">
            A complete responsive design system
          </p>
        </Section>

        {/* Features grid */}
        <Section>
          <h2 className="text-3xl font-bold mb-6">Features</h2>
          <ResponsiveGrid
            cols={{ xs: 1, sm: 2, lg: 3 }}
            gap="lg"
          >
            {Array.from({ length: 6 }, (_, i) => (
              <div
                key={i}
                className="bg-white p-6 rounded-lg shadow hover:shadow-xl transition-shadow"
              >
                <h3 className="text-xl font-semibold mb-2">Feature {i + 1}</h3>
                <p className="text-gray-600">
                  Description of this amazing feature.
                </p>
              </div>
            ))}
          </ResponsiveGrid>
        </Section>
      </PageContainer>

      {/* Mobile navigation */}
      <MobileNav variant="auto" items={navItems} />
    </>
  );
}

/**
 * Example 12: Dashboard Layout with Responsive Grid
 */
export function DashboardExample() {
  const { isMobile } = useBreakpoint();

  return (
    <WideContainer padding="responsive">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      {/* Stats grid */}
      <ResponsiveGrid
        cols={{ xs: 1, sm: 2, lg: 4 }}
        gap={isMobile ? 'md' : 'lg'}
        className="mb-8"
      >
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-600">Total Users</div>
          <div className="text-3xl font-bold mt-2">12,345</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-600">Revenue</div>
          <div className="text-3xl font-bold mt-2">$45,678</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-600">Orders</div>
          <div className="text-3xl font-bold mt-2">890</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-600">Conversion</div>
          <div className="text-3xl font-bold mt-2">3.4%</div>
        </div>
      </ResponsiveGrid>

      {/* Charts grid */}
      <ResponsiveGrid
        cols={{ xs: 1, lg: 2 }}
        gap="lg"
      >
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Chart 1</h3>
          <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
            Chart Placeholder
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Chart 2</h3>
          <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
            Chart Placeholder
          </div>
        </div>
      </ResponsiveGrid>
    </WideContainer>
  );
}
