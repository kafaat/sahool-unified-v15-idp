/**
 * User Mock Data
 * بيانات المستخدمين الوهمية
 */

import { generateId, randomItem, arabicNames } from './utils';

export type UserRole = 'admin' | 'manager' | 'operator' | 'viewer';

export interface MockUser {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  tenantId: string;
  tenantName: string;
  phone?: string;
  avatar?: string;
  isActive: boolean;
  lastLogin: string;
  createdAt: string;
}

/**
 * Generate a mock user
 */
export function generateMockUser(overrides: Partial<MockUser> = {}): MockUser {
  const firstName = randomItem(arabicNames.firstNames);
  const lastName = randomItem(arabicNames.lastNames);
  const name = `${firstName} ${lastName}`;

  return {
    id: generateId(),
    email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@sahool.ye`.replace(/[\u0600-\u06FF]/g, 'user'),
    name,
    role: randomItem<UserRole>(['admin', 'manager', 'operator', 'viewer']),
    tenantId: generateId(),
    tenantName: `مزرعة ${randomItem(arabicNames.lastNames)}`,
    phone: `+967${Math.floor(Math.random() * 900000000 + 100000000)}`,
    isActive: Math.random() > 0.1,
    lastLogin: new Date().toISOString(),
    createdAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
    ...overrides,
  };
}

/**
 * Generate multiple mock users
 */
export function generateMockUsers(count: number = 10): MockUser[] {
  return Array.from({ length: count }, () => generateMockUser());
}
