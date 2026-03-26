/**
 * SAHOOL Admin Test Utilities
 * أدوات اختبار لوحة الإدارة
 *
 * Provides render helpers, mock factories, and provider wrappers for tests.
 */

import React, { type ReactElement } from 'react';
import { render, type RenderOptions } from '@testing-library/react';

// ═══════════════════════════════════════════════════════════════════════════
// Mock Factories
// ═══════════════════════════════════════════════════════════════════════════

export function mockUser(overrides: Record<string, unknown> = {}) {
  return {
    id: 'user-1',
    email: 'admin@sahool.io',
    name: 'Test Admin',
    name_ar: 'مدير اختباري',
    role: 'admin' as const,
    tenant_id: 'tenant-1',
    ...overrides,
  };
}

export function mockField(overrides: Record<string, unknown> = {}) {
  return {
    id: 'field-1',
    name: 'Test Field',
    nameAr: 'حقل الاختبار',
    area: 10.5,
    crop: 'wheat',
    status: 'active',
    coordinates: { lat: 15.3694, lng: 44.191 },
    ...overrides,
  };
}

export function mockAlert(overrides: Record<string, unknown> = {}) {
  return {
    id: 'alert-1',
    type: 'pest',
    severity: 'medium',
    title: 'Test Alert',
    titleAr: 'تنبيه اختباري',
    message: 'Test alert message',
    messageAr: 'رسالة تنبيه اختبارية',
    source: 'test',
    status: 'unread',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ...overrides,
  };
}

export function mockEquipment(overrides: Record<string, unknown> = {}) {
  return {
    id: 'equip-1',
    name: 'Tractor A',
    nameAr: 'جرار أ',
    type: 'tractor',
    status: 'available',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ...overrides,
  };
}

export function mockIoTDevice(overrides: Record<string, unknown> = {}) {
  return {
    id: 'device-1',
    name: 'Soil Sensor 01',
    type: 'soil_moisture',
    fieldId: 'field-1',
    serialNumber: 'SN-001',
    status: 'online',
    batteryLevel: 85,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ...overrides,
  };
}

export function mockIrrigationSchedule(overrides: Record<string, unknown> = {}) {
  return {
    id: 'irr-1',
    fieldId: 'field-1',
    name: 'Morning Schedule',
    type: 'scheduled',
    status: 'active',
    startDate: new Date().toISOString(),
    frequency: 'daily',
    duration: 60,
    waterAmount: 500,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ...overrides,
  };
}

export function mockFetchResponse(data: unknown, ok = true, status = 200) {
  return Promise.resolve({
    ok,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
    headers: new Headers(),
  }) as unknown as Promise<Response>;
}

export function mockPaginatedResponse<T>(data: T[], total?: number) {
  return {
    data,
    meta: {
      total: total ?? data.length,
      page: 1,
      limit: 10,
      totalPages: Math.ceil((total ?? data.length) / 10),
    },
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Custom Render
// ═══════════════════════════════════════════════════════════════════════════

function AllProviders({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

function customRender(ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) {
  return render(ui, { wrapper: AllProviders, ...options });
}

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };
