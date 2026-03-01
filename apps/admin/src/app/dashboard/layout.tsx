import type { Metadata } from "next";
import DashboardShell from "@/components/layout/DashboardShell";

export const metadata: Metadata = {
  title: "SAHOOL - Dashboard",
  description: "Central operations dashboard for the SAHOOL Agricultural Intelligence Platform",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DashboardShell requiredRole="viewer">{children}</DashboardShell>;
}
