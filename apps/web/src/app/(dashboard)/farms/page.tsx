/**
 * Farm Management Page
 * صفحة إدارة المزارع
 */

import { Metadata } from 'next';
import FarmsClient from './FarmsClient';

export const metadata: Metadata = {
  title: 'Farm Management | SAHOOL',
  description: 'إدارة المزارع - Manage farms, track areas, and monitor operations',
  keywords: ['farms', 'المزارع', 'agriculture', 'الزراعة', 'sahool'],
};

export default function FarmsPage() {
  return <FarmsClient />;
}
