/**
 * Fertilizer Management Page
 * صفحة إدارة الأسمدة
 */

import { Metadata } from 'next';
import FertilizerClient from '@/features/precision-agriculture/components/FertilizerClient';

export const metadata: Metadata = {
  title: 'Fertilizer Management | SAHOOL',
  description: 'Fertilizer management, nutrient calculator, and application scheduling',
};

export default function FertilizerPage() {
  return <FertilizerClient />;
}
