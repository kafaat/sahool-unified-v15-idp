/**
 * SAHOOL Equipment Detail Page
 * صفحة تفاصيل المعدات
 */

import { Metadata } from 'next';
import EquipmentDetailClient from './EquipmentDetailClient';

export const metadata: Metadata = {
  title: 'Equipment Details | SAHOOL',
  description:
    'تفاصيل المعدات - View equipment details, maintenance history, and location tracking',
  keywords: ['equipment', 'المعدات', 'details', 'تفاصيل', 'maintenance', 'صيانة', 'sahool'],
  openGraph: {
    title: 'Equipment Details | SAHOOL',
    description: 'Equipment details and maintenance tracking',
    type: 'website',
  },
};

export default async function EquipmentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <EquipmentDetailClient equipmentId={id} />;
}
