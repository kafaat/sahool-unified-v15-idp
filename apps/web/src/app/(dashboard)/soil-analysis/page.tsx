/**
 * Soil Analysis Page
 * تحليل التربة — تحليل وتفسير نتائج فحص التربة
 */

import { Metadata } from 'next';
import SoilAnalysisClient from '@/features/soil-analysis/components/SoilAnalysisClient';

export const metadata: Metadata = {
  title: 'Soil Analysis | SAHOOL',
  description:
    'تحليل التربة - Soil test results interpretation, nutrient analysis, and recommendations',
  keywords: ['soil analysis', 'تحليل التربة', 'nutrients', 'soil testing', 'sahool'],
  openGraph: {
    title: 'Soil Analysis | SAHOOL',
    description: 'Soil analysis and nutrient management',
    type: 'website',
  },
};

export default function SoilAnalysisPage() {
  return <SoilAnalysisClient />;
}
