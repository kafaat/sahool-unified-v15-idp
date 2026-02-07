"use client";

/**
 * SAHOOL Admin App Providers
 * مزودات تطبيق الإدارة
 */

import { AuthProvider } from "@/stores/auth.store";
import { ThemeProvider } from "@/stores/theme.store";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <AuthProvider>{children}</AuthProvider>
    </ThemeProvider>
  );
}
