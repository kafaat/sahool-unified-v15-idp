import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SAHOOL - Session Management',
  description: 'View and manage active user sessions across the platform',
};

export default function SessionsLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
