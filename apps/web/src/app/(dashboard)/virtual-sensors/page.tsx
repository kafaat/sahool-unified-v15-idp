/**
 * Virtual Sensors Page
 * صفحة المستشعرات الافتراضية
 */

import { Metadata } from 'next';
import VirtualSensorsClient from '@/features/virtual-sensors/components/VirtualSensorsClient';

export const metadata: Metadata = {
  title: 'Virtual Sensors | SAHOOL',
  description: 'View computed virtual sensors, algorithms, and calibration settings',
};

export default function VirtualSensorsPage() {
  return <VirtualSensorsClient />;
}
