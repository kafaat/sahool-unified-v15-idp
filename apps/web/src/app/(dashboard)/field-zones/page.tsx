/**
 * Field Zones Page
 * مناطق الحقل — إدارة مناطق الري المتغير والزراعة الدقيقة
 */

import { Metadata } from 'next';
import FieldZonesClient from '@/features/fields/components/FieldZonesClient';

export const metadata: Metadata = {
  title: 'Field Zones | SAHOOL',
  description:
    'مناطق الحقل - VRI zone management for precision agriculture and variable rate irrigation',
  keywords: ['field zones', 'مناطق الحقل', 'VRI', 'precision agriculture', 'sahool'],
  openGraph: {
    title: 'Field Zones | SAHOOL',
    description: 'VRI zone management and precision agriculture',
    type: 'website',
  },
};

export default function FieldZonesPage() {
  return <FieldZonesClient />;
}
