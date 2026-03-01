import type { Metadata } from "next";
import DashboardShell from "@/components/layout/DashboardShell";

export const metadata: Metadata = {
  title: "SAHOOL - Disease Diagnostics",
  description: "Crop disease detection and diagnosis management for agricultural fields",
};

export default function DiseasesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DashboardShell requiredRole="viewer">{children}</DashboardShell>;
}
