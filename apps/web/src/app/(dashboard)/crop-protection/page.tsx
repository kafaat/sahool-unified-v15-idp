/**
 * Crop Protection Page
 * صفحة حماية المحاصيل
 */

import { Metadata } from 'next';
import CropProtectionClient from '@/features/crop-protection/components/CropProtectionClient';

export const metadata: Metadata = {
  title: 'Crop Protection | SAHOOL',
  description: 'حماية المحاصيل - Disease, pest, and spray schedule management',
};

export default function CropProtectionPage() {
  return <CropProtectionClient />;
}
