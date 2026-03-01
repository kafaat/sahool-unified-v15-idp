import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SAHOOL - Epidemic Tracking",
  description: "Crop disease epidemic monitoring and outbreak tracking",
};

export default function EpidemicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
