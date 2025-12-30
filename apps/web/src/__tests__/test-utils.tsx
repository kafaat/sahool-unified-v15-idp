/**
 * Test Utilities for SAHOOL Web App
 * أدوات الاختبار لتطبيق سحول الويب
 */

import React, { ReactElement, ReactNode } from 'react';
import { render, RenderOptions, RenderResult } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Create a fresh QueryClient for each test
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

interface WrapperProps {
  children: ReactNode;
}

// All providers wrapper
const AllProviders = ({ children }: WrapperProps) => {
  const queryClient = createTestQueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

// Custom render function with all providers
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
): RenderResult => render(ui as any, { wrapper: AllProviders as any, ...options });

// Re-export everything from testing-library
export * from '@testing-library/react';
export { customRender as render };

// Mock data generators
export const mockUser = (overrides = {}) => ({
  id: 'user-1',
  email: 'test@sahool.ye',
  name: 'مستخدم اختبار',
  role: 'farmer',
  tenantId: 'tenant-1',
  ...overrides,
});

export const mockField = (overrides = {}) => ({
  id: 'field-1',
  name: 'حقل الاختبار',
  area: 10.5,
  crop: 'wheat',
  status: 'active',
  coordinates: [15.3694, 44.1910],
  ...overrides,
});

export const mockAlert = (overrides = {}) => ({
  id: 'alert-1',
  type: 'pest',
  severity: 'medium',
  message: 'تنبيه اختباري',
  timestamp: new Date().toISOString(),
  isRead: false,
  ...overrides,
});

// Wait for loading states to resolve
export const waitForLoadingToFinish = async () => {
  // Wait for any pending promises
  await new Promise(resolve => setTimeout(resolve, 0));
};

// Mock fetch responses
export const mockFetchResponse = (data: unknown, status = 200) => {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
  });
};
