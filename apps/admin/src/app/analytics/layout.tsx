import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SAHOOL - Analytics",
  description: "Agricultural analytics, satellite imagery, and profitability analysis",
};

export default function AnalyticsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
