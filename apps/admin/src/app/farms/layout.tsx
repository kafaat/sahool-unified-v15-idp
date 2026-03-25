import type { Metadata } from 'next';
import DashboardShell from '@/components/layout/DashboardShell';

export const metadata: Metadata = {
  title: 'SAHOOL - Farm Management',
  description: 'Farm registration, field mapping, and agricultural operations management',
};

export default function FarmsLayout({ children }: { children: React.ReactNode }) {
  return <DashboardShell requiredRole="viewer">{children}</DashboardShell>;
}
