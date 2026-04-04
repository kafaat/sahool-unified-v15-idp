/**
 * SAHOOL Crop Insurance Page
 * صفحة التأمين الزراعي
 */

import { Metadata } from 'next';
import CropInsuranceClient from '@/features/crop-insurance/components/CropInsuranceClient';

export const metadata: Metadata = {
  title: 'Crop Insurance | SAHOOL',
  description:
    'التأمين الزراعي - Manage insurance policies, assess risks, and file claims',
  keywords: ['crop insurance', 'التأمين الزراعي', 'risk assessment', 'claims', 'مطالبات', 'sahool'],
  openGraph: {
    title: 'Crop Insurance | SAHOOL',
    description: 'Crop insurance policy management and risk assessment',
    type: 'website',
  },
};

export default function CropInsurancePage() {
  return <CropInsuranceClient />;
}
