import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SAHOOL - Compliance',
  description: 'Agricultural compliance management and regulatory standards tracking',
};

export default function ComplianceLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
