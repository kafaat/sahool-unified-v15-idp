/**
 * SAHOOL Equipment Management Page
 * صفحة إدارة المعدات
 */

import { Metadata } from 'next';
import EquipmentClient from './EquipmentClient';

export const metadata: Metadata = {
  title: 'Equipment Management | SAHOOL',
  description: 'إدارة المعدات - Manage farm equipment, track maintenance schedules, and monitor equipment status',
  keywords: ['equipment', 'المعدات', 'maintenance', 'صيانة', 'farm machinery', 'sahool'],
  openGraph: {
    title: 'Equipment Management | SAHOOL',
    description: 'Farm equipment management and maintenance tracking',
    type: 'website',
  },
};

export default function EquipmentPage() {
  return <EquipmentClient />;
}
