/**
 * Alerts Management Page
 * صفحة إدارة التنبيهات
 */

import { Metadata } from 'next';
import AlertsClient from './AlertsClient';

export const metadata: Metadata = {
  title: 'Alerts | SAHOOL',
  description: 'View and manage farm alerts, notifications and warnings',
};

export default function AlertsPage() {
  return <AlertsClient />;
}
