'use client';

/**
 * SAHOOL Admin App Providers
 * مزودات تطبيق الإدارة
 */

import { AuthProvider } from '@/stores/auth.store';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
}
