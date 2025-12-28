/**
 * SAHOOL Dashboard Home Page
 * الصفحة الرئيسية للوحة التحكم
 */

import { Metadata } from 'next';
import DashboardClient from './DashboardClient';

export const metadata: Metadata = {
  title: 'Dashboard | SAHOOL - Smart Agriculture Platform',
  description: 'لوحة التحكم الرئيسية - SAHOOL Dashboard for farm management, monitoring crops, weather, and activities',
  keywords: ['dashboard', 'لوحة التحكم', 'sahool', 'farm management', 'agriculture'],
  openGraph: {
    title: 'Dashboard | SAHOOL',
    description: 'Farm management dashboard',
    type: 'website',
  },
};

export default function DashboardPage() {
  return <DashboardClient />;
}
