/**
 * Home/Dashboard Feature - Type Definitions
 * تعريفات أنواع ميزة لوحة التحكم
 */

// ═══════════════════════════════════════════════════════════════════════════
// Activity Types
// ═══════════════════════════════════════════════════════════════════════════

export type ActivityType = 'task' | 'alert' | 'field' | 'weather' | 'irrigation' | 'harvest' | 'maintenance';

export interface ActivityItem {
  id: string;
  type: ActivityType;
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  timestamp: string;
  read?: boolean;
  metadata?: Record<string, unknown>;
}

// ═══════════════════════════════════════════════════════════════════════════
// Task Types
// ═══════════════════════════════════════════════════════════════════════════

export type TaskPriority = 'high' | 'medium' | 'low';
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';

export interface DashboardTask {
  id: string;
  title: string;
  titleAr: string;
  description?: string;
  descriptionAr?: string;
  dueDate: string;
  priority: TaskPriority;
  status: TaskStatus;
  fieldId?: string;
  fieldName?: string;
  fieldNameAr?: string;
  assignedTo?: string;
  createdAt?: string;
  updatedAt?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Weather Types
// ═══════════════════════════════════════════════════════════════════════════

export interface DashboardWeather {
  temperature: number;
  humidity: number;
  windSpeed: number;
  condition: string;
  conditionAr: string;
  location?: string;
  locationAr?: string;
  forecast?: WeatherForecastItem[];
  lastUpdated?: string;
}

export interface WeatherForecastItem {
  date: string;
  tempHigh: number;
  tempLow: number;
  condition: string;
  conditionAr: string;
  precipitation?: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Statistics Types
// ═══════════════════════════════════════════════════════════════════════════

export interface DashboardStats {
  totalFields: number;
  activeTasks: number;
  activeAlerts: number;
  completedTasks: number;
  totalArea?: number;
  healthyFields?: number;
  pendingIrrigation?: number;
  upcomingHarvests?: number;
}

export interface StatTrend {
  value: number;
  direction: 'up' | 'down' | 'stable';
  percentage: number;
  period: 'day' | 'week' | 'month';
}

export interface EnhancedStats extends DashboardStats {
  trends?: {
    fields?: StatTrend;
    tasks?: StatTrend;
    alerts?: StatTrend;
    health?: StatTrend;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Alert Types
// ═══════════════════════════════════════════════════════════════════════════

export type AlertSeverity = 'critical' | 'warning' | 'info';
export type AlertCategory = 'weather' | 'pest' | 'irrigation' | 'health' | 'system';

export interface DashboardAlert {
  id: string;
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  severity: AlertSeverity;
  category: AlertCategory;
  fieldId?: string;
  fieldName?: string;
  createdAt: string;
  dismissedAt?: string;
  acknowledged?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Dashboard Data Types
// ═══════════════════════════════════════════════════════════════════════════

export interface DashboardData {
  stats: DashboardStats;
  weather: DashboardWeather | null;
  recentActivity: ActivityItem[];
  upcomingTasks: DashboardTask[];
  alerts?: DashboardAlert[];
}

export interface DashboardFilters {
  dateRange?: {
    from: string;
    to: string;
  };
  fieldIds?: string[];
  taskStatus?: TaskStatus[];
  alertSeverity?: AlertSeverity[];
}

// ═══════════════════════════════════════════════════════════════════════════
// API Response Types
// ═══════════════════════════════════════════════════════════════════════════

export interface ApiDashboardResponse {
  success: boolean;
  data?: DashboardData;
  error?: string;
  errorAr?: string;
}

export interface ApiStatsResponse {
  success: boolean;
  data?: DashboardStats;
  error?: string;
}

export interface ApiActivityResponse {
  success: boolean;
  data?: ActivityItem[];
  total?: number;
  error?: string;
}

export interface ApiTasksResponse {
  success: boolean;
  data?: DashboardTask[];
  total?: number;
  error?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Types
// ═══════════════════════════════════════════════════════════════════════════

export interface MarkTaskCompletePayload {
  taskId: string;
  notes?: string;
  completedAt?: string;
}

export interface DismissAlertPayload {
  alertId: string;
  reason?: string;
}

export interface MarkActivityReadPayload {
  activityIds: string[];
}

export interface RefreshDashboardPayload {
  force?: boolean;
  sections?: ('stats' | 'weather' | 'activity' | 'tasks' | 'alerts')[];
}

// ═══════════════════════════════════════════════════════════════════════════
// Quick Action Types
// ═══════════════════════════════════════════════════════════════════════════

export interface QuickAction {
  id: string;
  icon: string;
  label: string;
  labelAr: string;
  href: string;
  color: string;
  badge?: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Hook Return Types
// ═══════════════════════════════════════════════════════════════════════════

export interface UseDashboardDataReturn {
  data: DashboardData | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => void;
}

export interface UseDashboardMutationsReturn {
  markTaskComplete: (payload: MarkTaskCompletePayload) => Promise<void>;
  dismissAlert: (payload: DismissAlertPayload) => Promise<void>;
  markActivityRead: (payload: MarkActivityReadPayload) => Promise<void>;
  isLoading: boolean;
}
