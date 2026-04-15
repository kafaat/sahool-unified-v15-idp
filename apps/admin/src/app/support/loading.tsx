/**
 * Support Loading Skeleton
 * هيكل تحميل صفحة الدعم الفني
 */

import TablePageSkeleton from '@/components/ui/TablePageSkeleton';

export default function SupportLoading() {
  return <TablePageSkeleton statCards={4} filterInputs={3} tableRows={6} showAddButton />;
}
