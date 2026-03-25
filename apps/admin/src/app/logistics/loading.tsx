/**
 * Logistics Loading Skeleton
 * هيكل تحميل صفحة اللوجستيات
 */

import TablePageSkeleton from '@/components/ui/TablePageSkeleton';

export default function LogisticsLoading() {
  return <TablePageSkeleton statCards={4} filterInputs={2} tableRows={5} />;
}
