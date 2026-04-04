/**
 * Audit Log Page
 * صفحة سجل التدقيق
 */

import { Metadata } from 'next';
import AuditClient from '@/features/audit/components/AuditClient';

export const metadata: Metadata = {
  title: 'Audit Log | SAHOOL',
  description: 'View audit trail, filter events, and export compliance reports',
};

export default function AuditPage() {
  return <AuditClient />;
}
