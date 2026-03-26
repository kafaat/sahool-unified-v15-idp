/**
 * SAHOOL Pivot Irrigation Page
 * صفحة الري المحوري
 */

import { Metadata } from 'next';
import PivotIrrigationClient from './PivotIrrigationClient';

export const metadata: Metadata = {
  title: 'Pivot Irrigation | SAHOOL',
  description:
    'الري المحوري - Valley-style center pivot irrigation management with VRI zones, sector control, and real-time monitoring',
  keywords: [
    'pivot irrigation',
    'الري المحوري',
    'center pivot',
    'VRI',
    'valley irrigation',
    'smart irrigation',
    'sahool',
  ],
  openGraph: {
    title: 'Pivot Irrigation | SAHOOL',
    description: 'Valley-style pivot irrigation management',
    type: 'website',
  },
};

export default function PivotIrrigationPage() {
  return <PivotIrrigationClient />;
}
