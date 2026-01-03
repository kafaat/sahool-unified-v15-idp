/**
 * SAHOOL Dashboard Data Hook
 * خطاف بيانات لوحة التحكم
 */

import { useQuery } from '@tanstack/react-query';
import { logger } from '@/lib/logger';

export interface DashboardData {
  stats: {
    totalFields: number;
    activeTasks: number;
    activeAlerts: number;
    completedTasks: number;
  };
  weather: {
    temperature: number;
    humidity: number;
    windSpeed: number;
    condition: string;
    conditionAr: string;
    location?: string;
  } | null;
  recentActivity: Array<{
    id: string;
    type: 'task' | 'alert' | 'field' | 'weather';
    title: string;
    titleAr: string;
    description: string;
    descriptionAr: string;
    timestamp: string;
  }>;
  upcomingTasks: Array<{
    id: string;
    title: string;
    titleAr: string;
    dueDate: string;
    priority: 'high' | 'medium' | 'low';
    status: string;
  }>;
}

async function fetchDashboardData(): Promise<DashboardData> {
  try {
    // When backend is ready, replace with:
    // const response = await fetch('/api/dashboard');
    // if (!response.ok) {
    //   throw new Error('Failed to fetch dashboard data');
    // }
    // return response.json();

    // Mock data for now
    return {
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
  } catch (error) {
    logger.error('Failed to fetch dashboard data:', error);
    // Return default/empty data structure on error
    return {
      stats: {
        totalFields: 0,
        activeTasks: 0,
        activeAlerts: 0,
        completedTasks: 0,
      },
      weather: null,
      recentActivity: [],
      upcomingTasks: [],
    };
  }
}

export function useDashboardData() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: fetchDashboardData,
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
}
