/**
 * Home/Dashboard Feature - Mock Data (Development Fallback)
 * بيانات وهمية للوحة التحكم
 *
 * Separated from the API layer to reduce client bundle size.
 * This data is used as fallback when the API is unavailable.
 */

import type { DashboardData } from './api';

export const MOCK_DASHBOARD_DATA: DashboardData = {
  stats: {
    totalFields: 12,
    activeTasks: 8,
    activeAlerts: 3,
    completedTasks: 45,
  },
  weather: {
    temperature: 28,
    humidity: 65,
    windSpeed: 12,
    condition: 'Partly Cloudy',
    conditionAr: 'غائم جزئياً',
    location: 'صنعاء، اليمن',
  },
  recentActivity: [
    {
      id: '1',
      type: 'task',
      title: 'Irrigation completed',
      titleAr: 'تم إكمال الري',
      description: 'Field #3 irrigation completed',
      descriptionAr: 'تم إكمال ري الحقل رقم 3',
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    },
    {
      id: '2',
      type: 'alert',
      title: 'Weather alert',
      titleAr: 'تنبيه طقس',
      description: 'High temperature expected',
      descriptionAr: 'من المتوقع درجات حرارة عالية',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    },
    {
      id: '3',
      type: 'field',
      title: 'New field added',
      titleAr: 'تمت إضافة حقل جديد',
      description: 'Field #12 has been registered',
      descriptionAr: 'تم تسجيل الحقل رقم 12',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    },
  ],
  upcomingTasks: [
    {
      id: '1',
      title: 'Water Field #3',
      titleAr: 'ري الحقل رقم 3',
      dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString(),
      priority: 'high',
      status: 'pending',
    },
    {
      id: '2',
      title: 'Fertilize Field #5',
      titleAr: 'تسميد الحقل رقم 5',
      dueDate: new Date(Date.now() + 1000 * 60 * 60 * 48).toISOString(),
      priority: 'medium',
      status: 'pending',
    },
    {
      id: '3',
      title: 'Pest inspection',
      titleAr: 'فحص الآفات',
      dueDate: new Date(Date.now() + 1000 * 60 * 60 * 72).toISOString(),
      priority: 'low',
      status: 'pending',
    },
  ],
};
