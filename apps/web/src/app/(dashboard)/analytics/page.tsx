/**
 * Analytics Page
 * صفحة التحليلات والتقارير
 */

import { Metadata } from 'next';
import { AnalyticsDashboard } from '@/features/analytics';

export const metadata: Metadata = {
  title: 'Analytics & Reports | SAHOOL',
  description: 'View your farm analytics, yield reports, and cost analysis',
};

export default function AnalyticsPage() {
  return <AnalyticsDashboard />;
}
