/**
 * Community Page
 * صفحة مجتمع المزارعين
 */

import { Metadata } from "next";
import { Feed } from "@/features/community";

export const metadata: Metadata = {
  title: "Farmer Community | SAHOOL",
  description: "Connect with other farmers, share experiences, and get advice",
};

export default function CommunityPage() {
  return <Feed />;
}
