import type { Metadata } from "next";
import DashboardShell from "@/components/layout/DashboardShell";
import { PageErrorBoundary } from "@/components/common/PageErrorBoundary";

export const metadata: Metadata = {
  title: "SAHOOL - Dashboard",
  description: "Central operations dashboard for the SAHOOL Agricultural Intelligence Platform",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <DashboardShell requiredRole="viewer">
      <PageErrorBoundary pageName="Dashboard" pageNameAr="لوحة التحكم">
        {children}
      </PageErrorBoundary>
    </DashboardShell>
  );
}
