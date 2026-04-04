/**
 * Epidemic Monitoring Page
 * صفحة مركز رصد الأوبئة
 */

import { Metadata } from 'next';
import EpidemicClient from '@/features/epidemic/components/EpidemicClient';

export const metadata: Metadata = {
  title: 'Epidemic Center | SAHOOL',
  description: 'مركز رصد الأوبئة - Disease outbreak monitoring and epidemic management',
};

export default function EpidemicPage() {
  return <EpidemicClient />;
}
