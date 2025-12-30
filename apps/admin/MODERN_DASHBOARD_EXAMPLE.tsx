'use client';

/**
 * MODERN DASHBOARD EXAMPLE
 * مثال على لوحة التحكم الحديثة
 *
 * This file demonstrates how to use the new modern components
 * together to create a contemporary dashboard design.
 *
 * يوضح هذا الملف كيفية استخدام المكونات الحديثة الجديدة
 * معًا لإنشاء تصميم عصري للوحة التحكم.
 */

import ModernHeader from '@/components/ui/ModernHeader';
import ModernSidebar from '@/components/ui/ModernSidebar';
import ModernMetricsGrid, {
  QuickStatsSummary,
  MetricComparison,
  CircularProgressMetric,
} from '@/components/dashboard/ModernMetricsGrid';
import {
  Users,
  TrendingUp,
  Activity,
  Droplets,
  Thermometer,
  DollarSign,
} from 'lucide-react';

export default function ModernDashboardExample() {
  // Sample metrics data
  const metrics = [
    {
      title: 'إجمالي المزارع',
      value: 1234,
      icon: Users,
      trend: { value: 12.5, isPositive: true },
      iconColor: 'text-sahool-600',
      variant: 'glass' as const,
    },
    {
      title: 'معدل النمو',
      value: 87,
      icon: TrendingUp,
      trend: { value: 8.3, isPositive: true },
      suffix: '%',
      iconColor: 'text-blue-600',
      variant: 'gradient' as const,
    },
    {
      title: 'المستشعرات النشطة',
      value: 456,
      icon: Activity,
      trend: { value: 3.2, isPositive: false },
      iconColor: 'text-purple-600',
      variant: 'glass' as const,
    },
    {
      title: 'استهلاك المياه',
      value: 2345,
      icon: Droplets,
      trend: { value: 15.7, isPositive: false },
      suffix: 'م³',
      iconColor: 'text-blue-600',
      variant: 'glass' as const,
    },
  ];

  const quickStats = [
    { label: 'تنبيهات نشطة', value: 23, color: 'text-red-500' },
    { label: 'مهام مكتملة', value: 145, color: 'text-green-500' },
    { label: 'قيد المعالجة', value: 67, color: 'text-yellow-500' },
    { label: 'معلقة', value: 12, color: 'text-gray-500' },
  ];

  return (
    <div className="min-h-screen gradient-mesh">
      {/* Modern Sidebar */}
      <ModernSidebar />

      {/* Main Content */}
      <div className="mr-64">
        {/* Modern Header */}
        <ModernHeader
          title="لوحة التحكم الحديثة"
          subtitle="مرحبًا بك في النظام المتطور لإدارة المزارع"
        />

        {/* Content Area */}
        <main className="p-6 space-y-6">
          {/* Main Metrics Grid */}
          <ModernMetricsGrid
            metrics={metrics}
            columns={4}
            animated={true}
            staggerDelay={100}
          />

          {/* Quick Stats Summary */}
          <QuickStatsSummary
            title="ملخص سريع"
            stats={quickStats}
          />

          {/* Comparison and Progress Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Metric Comparison */}
            <MetricComparison
              title="مقارنة الإنتاجية"
              current={{ label: 'هذا الشهر', value: 3456 }}
              previous={{ label: 'الشهر السابق', value: 2890 }}
              suffix="كجم"
              className="lg:col-span-2"
            />

            {/* Circular Progress */}
            <CircularProgressMetric
              title="نسبة الإنجاز"
              value={856}
              max={1000}
              suffix="مزرعة"
              color="sahool"
            />
          </div>

          {/* Additional Metrics in Different Variants */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <ModernMetricsGrid
              metrics={[
                {
                  title: 'درجة الحرارة',
                  value: 28,
                  icon: Thermometer,
                  suffix: '°C',
                  iconColor: 'text-orange-600',
                  variant: 'gradient',
                },
              ]}
              columns={1}
              animated={true}
            />

            <ModernMetricsGrid
              metrics={[
                {
                  title: 'الإيرادات',
                  value: 125000,
                  icon: DollarSign,
                  trend: { value: 22.5, isPositive: true },
                  suffix: 'ر.س',
                  iconColor: 'text-sahool-600',
                  variant: 'glass',
                },
              ]}
              columns={1}
              animated={true}
            />

            <CircularProgressMetric
              title="استخدام الموارد"
              value={750}
              max={1000}
              suffix="وحدة"
              color="blue"
            />
          </div>

          {/* Usage Instructions */}
          <div className="glass-card rounded-2xl p-8 animate-fade-in">
            <h2 className="text-2xl font-bold gradient-text mb-4">
              كيفية استخدام المكونات الحديثة
            </h2>

            <div className="space-y-6 text-gray-700 dark:text-gray-300">
              <section>
                <h3 className="text-lg font-semibold mb-2">1. ModernStatCard</h3>
                <p className="text-sm">بطاقة إحصائيات حديثة مع تأثيرات زجاجية وحركات انتقالية:</p>
                <pre className="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-xs overflow-x-auto">
{`import ModernStatCard from '@/components/ui/ModernStatCard';

<ModernStatCard
  title="عنوان البطاقة"
  value={1234}
  icon={Users}
  trend={{ value: 12.5, isPositive: true }}
  variant="glass" // glass | gradient | solid
  animated={true}
/>`}
                </pre>
              </section>

              <section>
                <h3 className="text-lg font-semibold mb-2">2. ModernSidebar</h3>
                <p className="text-sm">شريط جانبي بتأثير الزجاج مع انتقالات سلسة:</p>
                <pre className="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-xs overflow-x-auto">
{`import ModernSidebar from '@/components/ui/ModernSidebar';

<ModernSidebar />`}
                </pre>
              </section>

              <section>
                <h3 className="text-lg font-semibold mb-2">3. ModernHeader</h3>
                <p className="text-sm">رأس صفحة حديث مع بحث وإشعارات:</p>
                <pre className="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-xs overflow-x-auto">
{`import ModernHeader from '@/components/ui/ModernHeader';

<ModernHeader
  title="عنوان الصفحة"
  subtitle="وصف فرعي اختياري"
/>`}
                </pre>
              </section>

              <section>
                <h3 className="text-lg font-semibold mb-2">4. ModernMetricsGrid</h3>
                <p className="text-sm">شبكة مقاييس متحركة مع تأخير متدرج:</p>
                <pre className="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-xs overflow-x-auto">
{`import ModernMetricsGrid from '@/components/dashboard/ModernMetricsGrid';

<ModernMetricsGrid
  metrics={metricsArray}
  columns={4}
  animated={true}
  staggerDelay={100}
/>`}
                </pre>
              </section>

              <section>
                <h3 className="text-lg font-semibold mb-2">5. Dark Mode Support</h3>
                <p className="text-sm">دعم الوضع المظلم باستخدام CSS Variables:</p>
                <pre className="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-xs overflow-x-auto">
{`// في globals.css تم تعريف متغيرات للوضع الفاتح والمظلم
// استخدم الأزرار في الـ Header للتبديل بين الأوضاع

// CSS Classes المتاحة:
.glass              // تأثير زجاجي خفيف
.glass-strong       // تأثير زجاجي قوي
.glass-card         // بطاقة زجاجية مع ظلال
.gradient-sahool    // تدرج ألوان سهول
.gradient-text      // نص بتدرج لوني
.animate-glow       // تأثير توهج متحرك
.card-modern        // بطاقة حديثة مع تأثيرات`}
                </pre>
              </section>

              <section>
                <h3 className="text-lg font-semibold mb-2">6. Additional Components</h3>
                <ul className="list-disc list-inside space-y-2 text-sm">
                  <li><code className="text-sahool-600 dark:text-sahool-400">QuickStatsSummary</code> - ملخص إحصائيات سريع</li>
                  <li><code className="text-sahool-600 dark:text-sahool-400">MetricComparison</code> - مقارنة بين مقياسين</li>
                  <li><code className="text-sahool-600 dark:text-sahool-400">CircularProgressMetric</code> - مقياس تقدم دائري</li>
                </ul>
              </section>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
