/**
 * Irrigation Management Page
 * صفحة إدارة الري
 */

import { Metadata } from 'next';
import IrrigationClient from './IrrigationClient';

export const metadata: Metadata = {
  title: 'Irrigation | SAHOOL',
  description: 'Manage irrigation schedules, monitor water usage and optimize water efficiency',
};

export default function IrrigationPage() {
  return <IrrigationClient />;
}
