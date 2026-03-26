import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SAHOOL - Equipment',
  description: 'Farm equipment tracking, maintenance scheduling, and lifecycle management',
};

export default function EquipmentLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
