/**
 * Auth Route Group Layout
 * تخطيط مجموعة صفحات المصادقة
 *
 * Minimal layout for authentication pages (login, register, forgot-password,
 * reset-password, verify-otp). This layout intentionally omits heavy providers
 * (sidebar, header, dashboard context) to keep the auth bundle small and fast.
 */

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SAHOOL - Authentication",
  description: "Sign in to the SAHOOL Agricultural Intelligence Platform admin portal",
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
