import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SAHOOL - Alerts',
  description: 'Real-time agricultural alerts and notification management',
};

export default function AlertsLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
