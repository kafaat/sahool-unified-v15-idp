import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SAHOOL - Logistics",
  description: "Supply chain logistics, transportation, and delivery management",
};

export default function LogisticsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
