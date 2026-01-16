/**
 * Settings Page
 * صفحة الإعدادات
 */

import { Metadata } from "next";
import { SettingsPage } from "@/features/settings";

export const metadata: Metadata = {
  title: "Settings | SAHOOL",
  description: "Manage your account settings and preferences",
};

export default function Settings() {
  return <SettingsPage />;
}
