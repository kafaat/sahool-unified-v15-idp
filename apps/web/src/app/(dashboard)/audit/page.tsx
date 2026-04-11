/**
 * Audit Log Page
 * صفحة سجل التدقيق
 */

import { Metadata } from 'next';
import { requireAdmin } from '@/lib/auth/route-guard';
import AuditClient from '@/features/audit/components/AuditClient';

export const metadata: Metadata = {
  title: 'Audit Log | SAHOOL',
  description: 'View audit trail, filter events, and export compliance reports',
};

// Audit logs contain security-sensitive data (IPs, user actions, PII).
// Enforce admin role server-side — client-only guards are not sufficient.
export default async function AuditPage() {
  await requireAdmin();
  return <AuditClient />;
}
