/**
 * Harvest Quality Page
 * صفحة جودة الحصاد
 */

import { Metadata } from 'next';
import HarvestQualityClient from '@/features/harvest-quality/components/HarvestQualityClient';

export const metadata: Metadata = {
  title: 'Harvest Quality | SAHOOL',
  description: 'Post-harvest grading, quality metrics, and export certification tracking',
};

export default function HarvestQualityPage() {
  return <HarvestQualityClient />;
}
