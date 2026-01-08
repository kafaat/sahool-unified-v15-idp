'use client';

/**
 * SAHOOL Field Dashboard Component
 * مكون لوحة معلومات الحقل
 *
 * A unified dashboard for field monitoring with:
 * - Map view (60%) and info panel (40%)
 * - NDVI trend analysis
 * - Today's tasks
 * - Irrigation recommendations
 * - Weather risk assessment
 * - Astronomical calendar signals
 * - Active alerts
 * - Quick action buttons
 * - Zone summary
 */

import React, { useState } from 'react';
import { useLocale } from 'next-intl';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Droplets,
  AlertTriangle,
  CheckCircle2,
  Plus,
  History,
  Settings,
  RefreshCw,
  Calendar,
  MapPin,
  Activity,
  Moon,
  CloudRain,
  Thermometer,
  Wind,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FieldMap } from './FieldMap';
import { useField } from '../hooks/useField';
import { useFieldNDVI, useNDVITimeSeries } from '@/features/ndvi/hooks/useNDVI';
import { useTasksByField } from '@/features/tasks/hooks/useTasks';
import { useAlerts } from '@/features/alerts/hooks/useAlerts';
import { useCurrentWeather } from '@/features/weather/hooks/useWeather';
import { useToday as useAstronomicalToday } from '@/features/astronomical/hooks/useAstronomical';
import type { Task } from '@/features/tasks/types';
import type { Alert } from '@/features/alerts/types';
import { clsx } from 'clsx';

// ═══════════════════════════════════════════════════════════════════════════
// Interfaces
// ═══════════════════════════════════════════════════════════════════════════

interface FieldDashboardProps {
  fieldId: string;
  onCreateTask?: () => void;
  onViewHistory?: () => void;
  onSettings?: () => void;
}

interface NDVITrendData {
  current: number;
  previous: number;
  trend: 'up' | 'down' | 'stable';
  change: number;
}

interface IrrigationRecommendation {
  amount: number; // in mm
  recommended: boolean;
  reason: string;
  reasonAr: string;
}

interface WeatherRiskLevel {
  level: 'low' | 'medium' | 'high';
  label: string;
  labelAr: string;
  factors: string[];
}

interface ZoneSummary {
  totalZones: number;
  healthyZones: number;
  attentionZones: number;
  criticalZones: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Calculate NDVI trend from time series data
 */
function calculateNDVITrend(timeSeriesData?: Array<{ date: string; ndvi: number }>): NDVITrendData {
  if (!timeSeriesData || timeSeriesData.length < 2) {
    return { current: 0, previous: 0, trend: 'stable', change: 0 };
  }

  const current = timeSeriesData[timeSeriesData.length - 1]?.ndvi ?? 0;
  const previous = timeSeriesData[timeSeriesData.length - 2]?.ndvi ?? 0;
  const change = previous !== 0 ? ((current - previous) / previous) * 100 : 0;

  let trend: 'up' | 'down' | 'stable' = 'stable';
  if (change > 2) trend = 'up';
  else if (change < -2) trend = 'down';

  return { current, previous, trend, change };
}

/**
 * Calculate irrigation recommendation based on weather and NDVI
 */
function calculateIrrigationRecommendation(
  ndvi?: number,
  temperature?: number,
  humidity?: number
): IrrigationRecommendation {
  // Simple heuristic - in production, this would use more sophisticated algorithms
  const baseAmount = 5; // mm
  let multiplier = 1;
  let recommended = false;
  let reason = 'Normal conditions';
  let reasonAr = 'ظروف عادية';

  if (ndvi && ndvi < 0.3) {
    multiplier = 1.5;
    recommended = true;
    reason = 'Low vegetation health detected';
    reasonAr = 'انخفاض صحة النبات';
  }

  if (temperature && temperature > 35) {
    multiplier *= 1.3;
    recommended = true;
    reason = 'High temperature stress';
    reasonAr = 'إجهاد حراري عالي';
  }

  if (humidity && humidity < 30) {
    multiplier *= 1.2;
    recommended = true;
    reason = 'Low humidity conditions';
    reasonAr = 'انخفاض الرطوبة';
  }

  return {
    amount: Math.round(baseAmount * multiplier * 10) / 10,
    recommended,
    reason,
    reasonAr,
  };
}

/**
 * Assess weather risk based on current conditions and forecasts
 */
function assessWeatherRisk(
  temperature?: number,
  windSpeed?: number,
  alerts?: Alert[]
): WeatherRiskLevel {
  let riskScore = 0;
  const factors: string[] = [];

  if (temperature && temperature > 38) {
    riskScore += 30;
    factors.push('Extreme heat');
  } else if (temperature && temperature > 35) {
    riskScore += 15;
    factors.push('High temperature');
  }

  if (windSpeed && windSpeed > 40) {
    riskScore += 25;
    factors.push('Strong winds');
  } else if (windSpeed && windSpeed > 25) {
    riskScore += 10;
    factors.push('Moderate winds');
  }

  if (alerts && alerts.length > 0) {
    riskScore += alerts.length * 15;
    factors.push(`${alerts.length} active alerts`);
  }

  let level: 'low' | 'medium' | 'high' = 'low';
  let label = 'Low Risk';
  let labelAr = 'مخاطر منخفضة';

  if (riskScore >= 50) {
    level = 'high';
    label = 'High Risk';
    labelAr = 'مخاطر عالية';
  } else if (riskScore >= 25) {
    level = 'medium';
    label = 'Medium Risk';
    labelAr = 'مخاطر متوسطة';
  }

  return { level, label, labelAr, factors };
}

/**
 * Get today's tasks count
 */
function getTodayTasksCount(tasks?: Task[]): { total: number; completed: number; pending: number } {
  if (!tasks) return { total: 0, completed: 0, pending: 0 };

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const todayTasks = tasks.filter((task) => {
    if (!task.due_date) return false;
    const dueDate = new Date(task.due_date);
    dueDate.setHours(0, 0, 0, 0);
    return dueDate.getTime() === today.getTime();
  });

  const completed = todayTasks.filter((t) => t.status === 'completed').length;
  const pending = todayTasks.length - completed;

  return { total: todayTasks.length, completed, pending };
}

/**
 * Mock zone summary calculation
 * In production, this would analyze field zones based on NDVI map data
 */
function calculateZoneSummary(ndviValue?: number): ZoneSummary {
  // Simple mock implementation
  const totalZones = 12;

  if (!ndviValue) {
    return { totalZones, healthyZones: 8, attentionZones: 3, criticalZones: 1 };
  }

  if (ndviValue > 0.6) {
    return { totalZones, healthyZones: 10, attentionZones: 2, criticalZones: 0 };
  } else if (ndviValue > 0.4) {
    return { totalZones, healthyZones: 8, attentionZones: 3, criticalZones: 1 };
  } else {
    return { totalZones, healthyZones: 5, attentionZones: 4, criticalZones: 3 };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Sub-Components
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Loading Skeleton Component
 */
const LoadingSkeleton: React.FC<{ height?: string }> = ({ height = 'h-24' }) => (
  <div className={clsx('animate-pulse bg-gray-200 rounded-lg', height)} />
);

/**
 * Error Display Component
 */
const ErrorDisplay: React.FC<{ message: string; messageAr: string; onRetry?: () => void }> = ({
  message,
  messageAr,
  onRetry,
}) => {
  const locale = useLocale();
  const isArabic = locale === 'ar';

  return (
    <div className="flex flex-col items-center justify-center p-4 text-center space-y-2">
      <AlertTriangle className="w-8 h-8 text-red-500" />
      <p className="text-sm text-gray-600">{isArabic ? messageAr : message}</p>
      {onRetry && (
        <Button size="sm" variant="outline" onClick={onRetry}>
          <RefreshCw className="w-4 h-4 mr-2" />
          {isArabic ? 'إعادة المحاولة' : 'Retry'}
        </Button>
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Main Component
// ═══════════════════════════════════════════════════════════════════════════

export const FieldDashboard: React.FC<FieldDashboardProps> = ({
  fieldId,
  onCreateTask,
  onViewHistory,
  onSettings,
}) => {
  const locale = useLocale();
  const isArabic = locale === 'ar';

  // State
  const [selectedView, setSelectedView] = useState<'map' | 'satellite'>('map');

  // Queries
  const { data: field, isLoading: fieldLoading, isError: fieldError, refetch: refetchField } = useField(fieldId);
  const { data: ndviData, isLoading: ndviLoading, refetch: refetchNDVI } = useFieldNDVI(fieldId);
  const { data: ndviTimeSeries, isLoading: timeSeriesLoading } = useNDVITimeSeries(fieldId);
  const { data: tasks, isLoading: tasksLoading, refetch: refetchTasks } = useTasksByField(fieldId);
  const { data: alerts, isLoading: alertsLoading, refetch: refetchAlerts } = useAlerts({ fieldId });
  const { data: weather, isLoading: weatherLoading, refetch: refetchWeather } = useCurrentWeather();
  const { data: astronomical, isLoading: astroLoading, refetch: refetchAstro } = useAstronomicalToday();

  // Computed values
  const ndviTrend = calculateNDVITrend(ndviTimeSeries?.data);
  const irrigation = calculateIrrigationRecommendation(
    ndviData?.ndviMean,
    weather?.temperature,
    weather?.humidity
  );
  const weatherRisk = assessWeatherRisk(weather?.temperature, weather?.windSpeed, alerts);
  const todayTasks = getTodayTasksCount(tasks);
  const activeAlerts = alerts?.filter((a) => a.status === 'active') ?? [];
  const zoneSummary = calculateZoneSummary(ndviData?.ndviMean);

  // Handlers
  const handleRefreshAll = () => {
    refetchField();
    refetchNDVI();
    refetchTasks();
    refetchAlerts();
    refetchWeather();
    refetchAstro();
  };

  // Loading state
  if (fieldLoading) {
    return (
      <div className="w-full h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <RefreshCw className="w-12 h-12 animate-spin text-sahool-green-600 mx-auto" />
          <p className="text-gray-600">{isArabic ? 'جاري التحميل...' : 'Loading...'}</p>
        </div>
      </div>
    );
  }

  // Error state
  if (fieldError || !field) {
    return (
      <div className="w-full h-screen flex items-center justify-center">
        <ErrorDisplay
          message="Failed to load field data"
          messageAr="فشل تحميل بيانات الحقل"
          onRetry={refetchField}
        />
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4 space-x-reverse">
            <MapPin className="w-6 h-6 text-sahool-green-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {isArabic ? field.nameAr : field.name}
              </h1>
              <p className="text-sm text-gray-600">
                {field.area} {isArabic ? 'هكتار' : 'hectares'} • {isArabic ? field.cropAr : field.crop}
              </p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleRefreshAll}>
              <RefreshCw className="w-4 h-4 mr-2" />
              {isArabic ? 'تحديث' : 'Refresh'}
            </Button>
            <Button variant="outline" size="sm" onClick={onSettings}>
              <Settings className="w-4 h-4 mr-2" />
              {isArabic ? 'الإعدادات' : 'Settings'}
            </Button>
            <Button variant="outline" size="sm" onClick={onViewHistory}>
              <History className="w-4 h-4 mr-2" />
              {isArabic ? 'السجل' : 'History'}
            </Button>
            <Button variant="primary" size="sm" onClick={onCreateTask}>
              <Plus className="w-4 h-4 mr-2" />
              {isArabic ? 'إنشاء مهمة' : 'Create Task'}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-col lg:flex-row h-[calc(100vh-100px)] overflow-hidden">
        {/* Left: Map (60%) */}
        <div className="w-full lg:w-[60%] h-1/2 lg:h-full p-4">
          <Card className="h-full flex flex-col">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">
                  {isArabic ? 'عرض الخريطة' : 'Map View'}
                </CardTitle>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant={selectedView === 'map' ? 'primary' : 'outline'}
                    onClick={() => setSelectedView('map')}
                  >
                    {isArabic ? 'خريطة' : 'Map'}
                  </Button>
                  <Button
                    size="sm"
                    variant={selectedView === 'satellite' ? 'primary' : 'outline'}
                    onClick={() => setSelectedView('satellite')}
                  >
                    {isArabic ? 'قمر صناعي' : 'Satellite'}
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="flex-1 p-0">
              <FieldMap field={field} height="100%" />
            </CardContent>
          </Card>
        </div>

        {/* Right: Info Panel (40%) */}
        <div className="w-full lg:w-[40%] h-1/2 lg:h-full overflow-y-auto p-4 space-y-4">
          {/* NDVI Trend */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Activity className="w-5 h-5 text-green-600" />
                {isArabic ? 'اتجاه NDVI' : 'NDVI Trend'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {ndviLoading || timeSeriesLoading ? (
                <LoadingSkeleton height="h-20" />
              ) : (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-3xl font-bold text-gray-900">
                        {ndviTrend.current.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {isArabic ? 'القيمة الحالية' : 'Current Value'}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {ndviTrend.trend === 'up' && (
                        <>
                          <TrendingUp className="w-6 h-6 text-green-600" />
                          <span className="text-green-600 font-semibold">
                            +{ndviTrend.change.toFixed(1)}%
                          </span>
                        </>
                      )}
                      {ndviTrend.trend === 'down' && (
                        <>
                          <TrendingDown className="w-6 h-6 text-red-600" />
                          <span className="text-red-600 font-semibold">
                            {ndviTrend.change.toFixed(1)}%
                          </span>
                        </>
                      )}
                      {ndviTrend.trend === 'stable' && (
                        <>
                          <Minus className="w-6 h-6 text-gray-600" />
                          <span className="text-gray-600 font-semibold">
                            {isArabic ? 'مستقر' : 'Stable'}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full transition-all"
                      style={{ width: `${(ndviTrend.current / 1) * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Today's Tasks */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Calendar className="w-5 h-5 text-blue-600" />
                {isArabic ? 'مهام اليوم' : "Today's Tasks"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {tasksLoading ? (
                <LoadingSkeleton height="h-20" />
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-3xl font-bold text-gray-900">{todayTasks.total}</p>
                      <p className="text-xs text-gray-500">
                        {isArabic ? 'إجمالي المهام' : 'Total Tasks'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-green-600 font-semibold">
                        {todayTasks.completed} {isArabic ? 'مكتملة' : 'completed'}
                      </p>
                      <p className="text-sm text-orange-600">
                        {todayTasks.pending} {isArabic ? 'قيد الانتظار' : 'pending'}
                      </p>
                    </div>
                  </div>
                  {todayTasks.total > 0 && (
                    <div className="pt-2 border-t border-gray-200">
                      {tasks?.slice(0, 3).map((task) => (
                        <div key={task.id} className="flex items-center gap-2 py-1">
                          <CheckCircle2
                            className={clsx(
                              'w-4 h-4',
                              task.status === 'completed' ? 'text-green-600' : 'text-gray-400'
                            )}
                          />
                          <span className="text-sm text-gray-700 truncate">
                            {isArabic ? task.title_ar : task.title}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Irrigation Status */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Droplets className="w-5 h-5 text-blue-600" />
                {isArabic ? 'حالة الري' : 'Irrigation Status'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-3xl font-bold text-blue-600">
                      {irrigation.amount} {isArabic ? 'مم' : 'mm'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {isArabic ? 'الكمية الموصى بها' : 'Recommended Amount'}
                    </p>
                  </div>
                  <Badge variant={irrigation.recommended ? 'warning' : 'success'}>
                    {irrigation.recommended
                      ? isArabic
                        ? 'يحتاج ري'
                        : 'Needs Irrigation'
                      : isArabic
                      ? 'جيد'
                      : 'Good'}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600">
                  {isArabic ? irrigation.reasonAr : irrigation.reason}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Weather Risk */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <CloudRain className="w-5 h-5 text-gray-600" />
                {isArabic ? 'مخاطر الطقس' : 'Weather Risk'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {weatherLoading ? (
                <LoadingSkeleton height="h-20" />
              ) : (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Badge
                      variant={
                        weatherRisk.level === 'high'
                          ? 'danger'
                          : weatherRisk.level === 'medium'
                          ? 'warning'
                          : 'success'
                      }
                      size="lg"
                    >
                      {isArabic ? weatherRisk.labelAr : weatherRisk.label}
                    </Badge>
                    <div className="flex gap-2">
                      <div className="text-center">
                        <Thermometer className="w-5 h-5 mx-auto text-red-500" />
                        <p className="text-xs">{weather?.temperature}°C</p>
                      </div>
                      <div className="text-center">
                        <Wind className="w-5 h-5 mx-auto text-blue-500" />
                        <p className="text-xs">{weather?.windSpeed} km/h</p>
                      </div>
                    </div>
                  </div>
                  {weatherRisk.factors.length > 0 && (
                    <ul className="text-xs text-gray-600 list-disc list-inside">
                      {weatherRisk.factors.map((factor, i) => (
                        <li key={i}>{factor}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Astral Signal */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Moon className="w-5 h-5 text-indigo-600" />
                {isArabic ? 'الإشارة الفلكية' : 'Astral Signal'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {astroLoading ? (
                <LoadingSkeleton height="h-20" />
              ) : astronomical ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-gray-900">
                        {isArabic ? astronomical.lunar_mansion?.name : astronomical.lunar_mansion?.name_en}
                      </p>
                      <p className="text-xs text-gray-500">
                        {isArabic ? 'المنزلة القمرية' : 'Lunar Mansion'}
                      </p>
                    </div>
                    <Badge variant="info">
                      {isArabic ? astronomical.moon_phase?.name : astronomical.moon_phase?.name_en}
                    </Badge>
                  </div>
                  {astronomical.recommendations?.[0] && (
                    <p className="text-sm text-gray-600">
                      {isArabic ? astronomical.recommendations[0].reason : astronomical.recommendations[0].activity}
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-500">
                  {isArabic ? 'لا توجد بيانات فلكية' : 'No astronomical data available'}
                </p>
              )}
            </CardContent>
          </Card>

          {/* Active Alerts */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-600" />
                {isArabic ? 'التنبيهات النشطة' : 'Active Alerts'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {alertsLoading ? (
                <LoadingSkeleton height="h-20" />
              ) : activeAlerts.length > 0 ? (
                <div className="space-y-2">
                  {activeAlerts.slice(0, 3).map((alert) => (
                    <div
                      key={alert.id}
                      className={clsx(
                        'p-3 rounded-lg border-l-4',
                        alert.severity === 'critical' && 'bg-red-50 border-red-600',
                        alert.severity === 'warning' && 'bg-yellow-50 border-yellow-600',
                        alert.severity === 'info' && 'bg-blue-50 border-blue-600'
                      )}
                    >
                      <p className="text-sm font-semibold text-gray-900">
                        {isArabic ? alert.titleAr : alert.title}
                      </p>
                      <p className="text-xs text-gray-600 mt-1">
                        {isArabic ? alert.messageAr : alert.message}
                      </p>
                    </div>
                  ))}
                  {activeAlerts.length > 3 && (
                    <p className="text-xs text-gray-500 text-center">
                      +{activeAlerts.length - 3}{' '}
                      {isArabic ? 'تنبيهات أخرى' : 'more alerts'}
                    </p>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center py-6">
                  <CheckCircle2 className="w-8 h-8 text-green-600 mr-2" />
                  <p className="text-sm text-gray-600">
                    {isArabic ? 'لا توجد تنبيهات نشطة' : 'No active alerts'}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Zone Summary Bar (Bottom) */}
      <div className="bg-white border-t border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-sm text-gray-700">
                {zoneSummary.healthyZones} {isArabic ? 'مناطق صحية' : 'Healthy Zones'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <span className="text-sm text-gray-700">
                {zoneSummary.attentionZones} {isArabic ? 'مناطق تحتاج انتباه' : 'Attention Zones'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-sm text-gray-700">
                {zoneSummary.criticalZones} {isArabic ? 'مناطق حرجة' : 'Critical Zones'}
              </span>
            </div>
          </div>
          <p className="text-sm text-gray-500">
            {isArabic ? 'إجمالي المناطق' : 'Total Zones'}: {zoneSummary.totalZones}
          </p>
        </div>
      </div>
    </div>
  );
};

export default FieldDashboard;
