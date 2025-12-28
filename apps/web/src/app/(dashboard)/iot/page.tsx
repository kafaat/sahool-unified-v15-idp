/**
 * SAHOOL IoT & Sensors Page
 * صفحة إنترنت الأشياء والمستشعرات
 */

import { Metadata } from 'next';
import IoTClient from './IoTClient';

export const metadata: Metadata = {
  title: 'IoT & Sensors | SAHOOL',
  description: 'إنترنت الأشياء والمستشعرات - Monitor sensors, control actuators, and manage IoT devices on your farm',
  keywords: ['iot', 'sensors', 'مستشعرات', 'internet of things', 'smart farming', 'sahool'],
  openGraph: {
    title: 'IoT & Sensors | SAHOOL',
    description: 'Smart farm IoT and sensor management',
    type: 'website',
  },
};

export default function IoTPage() {
  return <IoTClient />;
}
