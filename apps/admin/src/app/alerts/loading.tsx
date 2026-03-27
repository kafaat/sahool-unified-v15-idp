/**
 * Alerts Loading Skeleton
 * هيكل تحميل صفحة التنبيهات
 */

import TablePageSkeleton from '@/components/ui/TablePageSkeleton';

export default function AlertsLoading() {
  return <TablePageSkeleton statCards={4} filterInputs={3} tableRows={6} />;
}
