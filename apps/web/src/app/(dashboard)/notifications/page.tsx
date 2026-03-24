/**
 * Notifications Page
 * صفحة الإشعارات
 */

import { Metadata } from 'next';
import NotificationsClient from './NotificationsClient';

export const metadata: Metadata = {
  title: 'Notifications | SAHOOL',
  description: 'View and manage notifications and preferences',
};

export default function NotificationsPage() {
  return <NotificationsClient />;
}
