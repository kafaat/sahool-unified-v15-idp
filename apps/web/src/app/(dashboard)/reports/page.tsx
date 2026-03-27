/**
 * Reports Page
 * صفحة التقارير
 */

import { Metadata } from 'next';
import ReportsClient from './ReportsClient';

export const metadata: Metadata = {
  title: 'Reports | SAHOOL',
  description: 'التقارير - Generate and view farm reports, analytics, and insights',
  keywords: ['reports', 'التقارير', 'analytics', 'تحليلات', 'sahool'],
};

export default function ReportsPage() {
  return <ReportsClient />;
}
