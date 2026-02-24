/**
 * Inventory Loading Skeleton
 * هيكل تحميل صفحة المخزون
 */

import TablePageSkeleton from "@/components/ui/TablePageSkeleton";

export default function InventoryLoading() {
  return <TablePageSkeleton statCards={4} filterInputs={2} tableRows={5} showAddButton />;
}
