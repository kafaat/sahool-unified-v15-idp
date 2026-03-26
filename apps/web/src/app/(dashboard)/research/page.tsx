/**
 * Research Trials Page
 * صفحة التجارب البحثية
 */

import { Metadata } from "next";
import { requireAdmin } from "@/lib/auth/route-guard";
import ResearchClient from "./ResearchClient";

export const metadata: Metadata = {
  title: "Research Trials | SAHOOL",
  description: "Manage agricultural research trials and experiments",
};

export default async function ResearchPage() {
  await requireAdmin();
  return <ResearchClient />;
}
