import { Metadata } from "next";
import HomeClient from "./HomeClient";

export const metadata: Metadata = {
  title: "سهول | SAHOOL - Smart Agriculture Platform",
  description:
    "منصة سهول الزراعية الذكية - SAHOOL Smart Agricultural Platform for Yemen. Manage your farm with advanced tools for crops, equipment, weather, and more.",
  keywords: [
    "سهول",
    "زراعة",
    "اليمن",
    "sahool",
    "agriculture",
    "yemen",
    "smart farming",
    "farm management",
  ],
  openGraph: {
    title: "سهول | SAHOOL - Smart Agriculture Platform",
    description: "Smart Agricultural Platform for Yemen",
    type: "website",
  },
};

export default function Home() {
  return <HomeClient />;
}
