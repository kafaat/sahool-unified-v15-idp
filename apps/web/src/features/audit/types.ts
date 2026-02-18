/**
 * Audit Feature - Types
 * أنواع ميزة التدقيق
 */

export interface AuditLog {
  id: string;
  action: string;
  actionAr: string;
  userId: string;
  userName: string;
  userNameAr: string;
  resource: string;
  resourceId: string;
  details: string;
  detailsAr: string;
  ipAddress?: string;
  metadata?: Record<string, unknown>;
  timestamp: string;
}

export interface AuditStats {
  totalLogs: number;
  todayLogs: number;
  byAction: Record<string, number>;
  byResource: Record<string, number>;
  topUsers: Array<{ userId: string; userName: string; count: number }>;
}

export interface AuditFilters {
  action?: string;
  userId?: string;
  resource?: string;
  startDate?: string;
  endDate?: string;
  search?: string;
}
