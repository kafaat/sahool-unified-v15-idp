import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SAHOOL - Crop Health',
  description: 'Crop health monitoring, NDVI analysis, and vegetation assessment',
};

export default function CropHealthLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
