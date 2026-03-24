import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SAHOOL - Support',
  description: 'Technical support and help center for the SAHOOL platform',
};

export default function SupportLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
