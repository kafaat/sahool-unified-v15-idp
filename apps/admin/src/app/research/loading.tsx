/**
 * Research Loading Skeleton
 * هيكل تحميل صفحة الأبحاث
 */

import TablePageSkeleton from '@/components/ui/TablePageSkeleton';

export default function ResearchLoading() {
  return <TablePageSkeleton statCards={4} filterInputs={2} tableRows={5} />;
}
