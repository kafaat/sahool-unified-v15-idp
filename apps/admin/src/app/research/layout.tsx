import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SAHOOL - Research',
  description: 'Agricultural research trials, experiments, and data analysis',
};

export default function ResearchLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
