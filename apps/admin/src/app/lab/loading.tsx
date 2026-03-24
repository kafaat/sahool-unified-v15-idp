/**
 * Lab Loading Skeleton
 * هيكل تحميل صفحة المختبر
 */

import TablePageSkeleton from '@/components/ui/TablePageSkeleton';

export default function LabLoading() {
  return <TablePageSkeleton statCards={4} filterInputs={2} tableRows={5} />;
}
