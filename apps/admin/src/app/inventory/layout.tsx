import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SAHOOL - Inventory",
  description: "Agricultural inventory management and stock tracking",
};

export default function InventoryLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
