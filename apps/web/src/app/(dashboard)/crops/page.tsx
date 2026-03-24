/**
 * Crop Management Page
 * صفحة إدارة المحاصيل
 */

import { Metadata } from 'next';
import CropsClient from './CropsClient';

export const metadata: Metadata = {
  title: 'Crop Management | SAHOOL',
  description: 'إدارة المحاصيل - Monitor crops, growth stages, and health scores',
  keywords: ['crops', 'المحاصيل', 'agriculture', 'growth', 'نمو', 'sahool'],
};

export default function CropsPage() {
  return <CropsClient />;
}
