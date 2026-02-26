/**
 * Auth Route Group Layout
 * تخطيط مجموعة صفحات المصادقة
 *
 * Minimal layout for authentication pages (login, register, forgot-password,
 * reset-password, verify-otp). This layout intentionally omits heavy providers
 * (sidebar, header, dashboard context) to keep the auth bundle small and fast.
 */

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
