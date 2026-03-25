import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SAHOOL - Lab & Experiments',
  description: 'Agricultural research laboratory and experimental feature testing',
};

export default function LabLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
