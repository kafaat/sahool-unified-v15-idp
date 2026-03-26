/**
 * User Management Page
 * صفحة إدارة المستخدمين
 */

import { Metadata } from "next";
import { requireAdmin } from "@/lib/auth/route-guard";
import UsersClient from "./UsersClient";

export const metadata: Metadata = {
  title: "User Management | SAHOOL",
  description: "إدارة المستخدمين - Manage platform users, roles, and permissions",
  keywords: ["users", "المستخدمين", "roles", "أدوار", "permissions", "sahool"],
};

export default async function UsersPage() {
  await requireAdmin();
  return <UsersClient />;
}
