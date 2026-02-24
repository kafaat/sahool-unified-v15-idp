/**
 * Epidemic Monitoring Loading Skeleton
 * هيكل تحميل صفحة مراقبة الأوبئة
 */

import TablePageSkeleton from "@/components/ui/TablePageSkeleton";

export default function EpidemicLoading() {
  return <TablePageSkeleton statCards={4} filterInputs={3} tableRows={6} />;
}
