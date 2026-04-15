/**
 * Edge Devices Management Page
 * صفحة إدارة أجهزة الحوسبة الطرفية
 */

import { Metadata } from 'next';
import EdgeDevicesClient from '@/features/edge-devices/components/EdgeDevicesClient';

export const metadata: Metadata = {
  title: 'Edge Devices | SAHOOL',
  description: 'Manage edge computing devices, monitor deployment status and device health',
};

export default function EdgeDevicesPage() {
  return <EdgeDevicesClient />;
}
