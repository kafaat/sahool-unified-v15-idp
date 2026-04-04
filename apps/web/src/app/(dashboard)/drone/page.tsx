/**
 * SAHOOL Drone Fleet Management Page
 * صفحة إدارة الطائرات بدون طيار
 */

import { Metadata } from 'next';
import DroneClient from '@/features/drone/components/DroneClient';

export const metadata: Metadata = {
  title: 'Drone Management | SAHOOL',
  description:
    'الطائرات بدون طيار - Manage drone fleet, plan missions, and generate VRA maps',
  keywords: ['drone', 'الطائرات بدون طيار', 'VRA', 'missions', 'مهمات', 'sahool'],
  openGraph: {
    title: 'Drone Management | SAHOOL',
    description: 'Drone fleet management, mission planning, and VRA map generation',
    type: 'website',
  },
};

export default function DronePage() {
  return <DroneClient />;
}
