/**
 * SAHOOL AI Vision Detection Page
 * صفحة الكشف البصري بالذكاء الاصطناعي
 */

import { Metadata } from 'next';
import VisionClient from '@/features/vision/components/VisionClient';

export const metadata: Metadata = {
  title: 'AI Vision Detection | SAHOOL',
  description:
    'الكشف البصري بالذكاء الاصطناعي - AI-powered disease and pest detection from field images',
  keywords: ['vision', 'الكشف البصري', 'AI', 'disease detection', 'pest detection', 'sahool'],
  openGraph: {
    title: 'AI Vision Detection | SAHOOL',
    description: 'AI-powered crop disease and pest detection',
    type: 'website',
  },
};

export default function VisionPage() {
  return <VisionClient />;
}
