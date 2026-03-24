/**
 * Sensors Monitoring Page
 * صفحة مراقبة الحساسات
 */

import { Metadata } from 'next';
import SensorsClient from './SensorsClient';

export const metadata: Metadata = {
  title: 'Sensors | SAHOOL',
  description: 'Monitor IoT sensors, view real-time data and sensor health status',
};

export default function SensorsPage() {
  return <SensorsClient />;
}
