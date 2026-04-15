import type { Metadata } from 'next';
import DashboardShell from '@/components/layout/DashboardShell';

export const metadata: Metadata = {
  title: 'SAHOOL - Settings',
  description: 'Platform configuration and administration settings',
};

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  return <DashboardShell requiredRole="admin">{children}</DashboardShell>;
}
