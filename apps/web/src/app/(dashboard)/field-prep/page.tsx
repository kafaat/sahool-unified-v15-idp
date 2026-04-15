/**
 * Field Preparation Page
 * تحضير الحقل — سير عمل التحضير قبل الزراعة
 */

import { Metadata } from 'next';
import FieldPrepClient from '@/features/fields/components/FieldPrepClient';

export const metadata: Metadata = {
  title: 'Field Preparation | SAHOOL',
  description:
    'تحضير الحقل - Pre-season field preparation workflow from soil testing to planting readiness',
  keywords: ['field preparation', 'تحضير الحقل', 'soil test', 'leveling', 'planting', 'sahool'],
  openGraph: {
    title: 'Field Preparation | SAHOOL',
    description: 'Field preparation workflow and pre-season planning',
    type: 'website',
  },
};

export default function FieldPrepPage() {
  return <FieldPrepClient />;
}
