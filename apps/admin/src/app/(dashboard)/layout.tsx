import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SAHOOL - Admin Dashboard",
  description: "SAHOOL Agricultural Intelligence Platform administration panel",
};

export default function DashboardGroupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
