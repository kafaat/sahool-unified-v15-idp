import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SAHOOL - User Management",
  description: "User accounts, roles, and access control management",
};

export default function UsersLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
