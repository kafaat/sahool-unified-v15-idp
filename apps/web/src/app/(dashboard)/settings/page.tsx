/**
 * Settings Page
 * صفحة الإعدادات
 */

import { Metadata } from 'next';
import { requireAuth } from '@/lib/auth/route-guard';
import { SettingsPage } from '@/features/settings';

export const metadata: Metadata = {
  title: 'Settings | SAHOOL',
  description: 'Manage your account settings and preferences',
};

// Settings expose PII, security settings, 2FA, and subscription data.
// Enforce authentication server-side so the page cannot render for anonymous users.
export default async function Settings() {
  await requireAuth();
  return <SettingsPage />;
}
