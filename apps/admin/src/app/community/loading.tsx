/**
 * Community Loading Skeleton
 * هيكل تحميل صفحة المجتمع
 */

import TablePageSkeleton from "@/components/ui/TablePageSkeleton";

export default function CommunityLoading() {
  return <TablePageSkeleton statCards={4} filterInputs={2} tableRows={5} />;
}
