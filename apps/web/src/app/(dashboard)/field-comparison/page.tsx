/**
 * Field Comparison Page
 * مقارنة الحقول — مقارنة جنبًا إلى جنب
 */

import { Metadata } from 'next';
import FieldComparisonClient from '@/features/fields/components/FieldComparisonClient';

export const metadata: Metadata = {
  title: 'Field Comparison | SAHOOL',
  description:
    'مقارنة الحقول - Side-by-side field comparison for NDVI, weather, yield, and soil metrics',
  keywords: ['field comparison', 'مقارنة الحقول', 'NDVI', 'yield', 'sahool'],
  openGraph: {
    title: 'Field Comparison | SAHOOL',
    description: 'Compare field performance side by side',
    type: 'website',
  },
};

export default function FieldComparisonPage() {
  return <FieldComparisonClient />;
}
