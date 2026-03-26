/**
 * Spray Planning Page
 * صفحة تخطيط الرش
 */

import { Metadata } from 'next';
import SprayClient from './SprayClient';

export const metadata: Metadata = {
  title: 'Spray Planning | SAHOOL',
  description: 'Plan and track spray applications for pest and disease control',
};

export default function SprayPage() {
  return <SprayClient />;
}
