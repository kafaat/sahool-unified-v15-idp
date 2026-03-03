import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SAHOOL - Disaster Assessment",
  description: "Natural disaster risk assessment and agricultural impact monitoring",
};

export default function DisastersLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
