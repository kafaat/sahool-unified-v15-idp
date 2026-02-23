/**
 * Marketplace Loading Skeleton
 * هيكل تحميل صفحة السوق
 */

import TablePageSkeleton from "@/components/ui/TablePageSkeleton";

export default function MarketplaceLoading() {
  return <TablePageSkeleton statCards={4} filterInputs={2} tableRows={5} />;
}
