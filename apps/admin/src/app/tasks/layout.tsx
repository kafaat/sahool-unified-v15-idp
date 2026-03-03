import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SAHOOL - Task Management",
  description: "Farm task scheduling, assignment, and progress tracking",
};

export default function TasksLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
