// Utility functions for Sahool Admin Dashboard
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date, locale: string = 'ar'): string {
  const d = new Date(date);
  return d.toLocaleDateString(locale === 'ar' ? 'ar-YE' : 'en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatNumber(num: number, locale: string = 'ar'): string {
  return num.toLocaleString(locale === 'ar' ? 'ar-YE' : 'en-US');
}

export function formatArea(hectares: number, locale: string = 'ar'): string {
  return `${formatNumber(hectares, locale)} ${locale === 'ar' ? 'هكتار' : 'ha'}`;
}

export function getHealthScoreColor(score: number): string {
  if (score >= 80) return 'text-green-600 bg-green-100';
  if (score >= 60) return 'text-yellow-600 bg-yellow-100';
  if (score >= 40) return 'text-orange-600 bg-orange-100';
  return 'text-red-600 bg-red-100';
}

export function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'low':
      return 'text-green-600 bg-green-100';
    case 'medium':
      return 'text-yellow-600 bg-yellow-100';
    case 'high':
      return 'text-orange-600 bg-orange-100';
    case 'critical':
      return 'text-red-600 bg-red-100';
    default:
      return 'text-gray-600 bg-gray-100';
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'pending':
      return 'text-yellow-600 bg-yellow-100';
    case 'confirmed':
      return 'text-blue-600 bg-blue-100';
    case 'rejected':
      return 'text-gray-600 bg-gray-100';
    case 'treated':
      return 'text-green-600 bg-green-100';
    case 'active':
      return 'text-green-600 bg-green-100';
    case 'inactive':
      return 'text-red-600 bg-red-100';
    default:
      return 'text-gray-600 bg-gray-100';
  }
}

export function getSeverityLabel(severity: string, locale: string = 'ar'): string {
  const labels: Record<string, Record<string, string>> = {
    ar: {
      low: 'منخفض',
      medium: 'متوسط',
      high: 'مرتفع',
      critical: 'حرج',
    },
    en: {
      low: 'Low',
      medium: 'Medium',
      high: 'High',
      critical: 'Critical',
    },
  };
  return labels[locale]?.[severity] || severity;
}

export function getStatusLabel(status: string, locale: string = 'ar'): string {
  const labels: Record<string, Record<string, string>> = {
    ar: {
      pending: 'قيد المراجعة',
      confirmed: 'مؤكد',
      rejected: 'مرفوض',
      treated: 'تم العلاج',
      active: 'نشط',
      inactive: 'غير نشط',
    },
    en: {
      pending: 'Pending',
      confirmed: 'Confirmed',
      rejected: 'Rejected',
      treated: 'Treated',
      active: 'Active',
      inactive: 'Inactive',
    },
  };
  return labels[locale]?.[status] || status;
}
