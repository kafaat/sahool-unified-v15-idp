import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SAHOOL - Precision Agriculture',
  description:
    'Precision agriculture tools including pivot irrigation, VRA, GDD tracking, and spray management',
};

export default function PrecisionAgricultureLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
