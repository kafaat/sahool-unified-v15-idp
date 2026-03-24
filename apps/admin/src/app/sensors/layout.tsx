import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SAHOOL - Sensors & IoT',
  description: 'IoT sensor monitoring, data visualization, and device management',
};

export default function SensorsLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
