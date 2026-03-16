"use client";

/**
 * SAHOOL Admin App Providers
 * مزودات تطبيق الإدارة
 */

import { AuthProvider } from "@/stores/auth.store";
import { ThemeProvider } from "@/stores/theme.store";
import { ToastProvider } from "@/components/ui/Toast";
import dynamic from "next/dynamic";

const CommandPalette = dynamic(
  () => import("@/components/ui/CommandPalette"),
  { ssr: false },
);

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AuthProvider>
          {children}
          <CommandPalette />
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}
