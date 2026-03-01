import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SAHOOL - Marketplace",
  description: "Agricultural marketplace for buying and selling crops, equipment, and services",
};

export default function MarketplaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
