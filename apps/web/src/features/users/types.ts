/**
 * Users Feature - Types
 * أنواع ميزة المستخدمين
 */

export type UserRole = 'admin' | 'manager' | 'farmer' | 'viewer' | 'agronomist';
export type UserStatus = 'active' | 'inactive' | 'suspended' | 'pending';

export interface User {
  id: string;
  email: string;
  name: string;
  nameAr: string;
  phone?: string;
  role: UserRole;
  status: UserStatus;
  avatar?: string;
  tenantId: string;
  farmIds: string[];
  lastLogin?: string;
  twoFactorEnabled: boolean;
  language: 'ar' | 'en';
  createdAt: string;
  updatedAt: string;
}

export interface UserFilters {
  role?: UserRole;
  status?: UserStatus;
  search?: string;
}

export interface UserFormData {
  email: string;
  name: string;
  nameAr: string;
  phone?: string;
  role: UserRole;
  language?: 'ar' | 'en';
  farmIds?: string[];
}

export interface UserStats {
  totalUsers: number;
  activeUsers: number;
  admins: number;
  farmers: number;
  pendingApprovals: number;
}
