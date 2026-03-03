import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SAHOOL - Community",
  description: "Farmer community engagement, forums, and collaborative features",
};

export default function CommunityLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
