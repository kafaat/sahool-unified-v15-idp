import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SAHOOL - Irrigation Management",
  description: "Smart irrigation scheduling, water usage monitoring, and efficiency optimization",
};

export default function IrrigationLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
