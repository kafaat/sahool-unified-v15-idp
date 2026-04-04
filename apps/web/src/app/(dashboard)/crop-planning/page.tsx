/**
 * Crop Planning Page
 * صفحة تخطيط الموسم الزراعي
 */

import { Metadata } from 'next';
import CropPlanningClient from '@/features/crop-planning/components/CropPlanningClient';

export const metadata: Metadata = {
  title: 'Crop Planning | SAHOOL',
  description: 'تخطيط الموسم الزراعي - Season planning wizard from field preparation to harvest',
};

export default function CropPlanningPage() {
  return <CropPlanningClient />;
}
