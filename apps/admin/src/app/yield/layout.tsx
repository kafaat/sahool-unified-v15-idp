import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SAHOOL - Yield Prediction',
  description: 'Crop yield forecasting, analysis, and historical trend tracking',
};

export default function YieldLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
