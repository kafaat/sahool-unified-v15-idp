/**
 * SAHOOL Living Field Score Hook
 * خطاف حساب درجة الحقل الحي
 *
 * Combines data from NDVI, irrigation, tasks, weather, and astronomical sources
 * to calculate a comprehensive field health score with actionable insights.
 */

'use client';

import { useMemo } from 'react';
import { useFieldNDVI } from '@/features/ndvi/hooks/useNDVI';
import { useCurrentWeather } from '@/features/weather/hooks/useWeather';
import { useToday as useAstronomicalToday } from '@/features/astronomical/hooks/useAstronomical';
import { useTasksByField } from '@/features/tasks/hooks/useTasks';
import { useSensors } from '@/features/iot/hooks/useSensors';
import type { AlertSeverity, AlertCategory } from '@/features/alerts/types';
import type { RecommendationType, RecommendationPriority } from '@/features/advisor/api';
import type { Task } from '@/features/tasks/types';

// ═══════════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface FieldAlert {
  id: string;
  severity: AlertSeverity;
  category: AlertCategory;
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  timestamp: string;
  threshold?: number;
  currentValue?: number;
}

export interface Recommendation {
  id: string;
  type: RecommendationType;
  priority: RecommendationPriority;
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  actionItems: string[];
  expectedBenefit?: string;
  expectedBenefitAr?: string;
}

export interface LivingFieldScore {
  overall: number;
  health: number;
  hydration: number;
  attention: number;
  astral: number;
  trend: 'improving' | 'stable' | 'declining';
  alerts: FieldAlert[];
  recommendations: Recommendation[];
  lastUpdated: Date;
}

interface UseLivingFieldScoreOptions {
  enabled?: boolean;
  includeAlerts?: boolean;
  includeRecommendations?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════════

const THRESHOLDS = {
  NDVI: {
    EXCELLENT: 0.7,
    GOOD: 0.5,
    MODERATE: 0.3,
    POOR: 0.15,
  },
  SOIL_MOISTURE: {
    OPTIMAL_MIN: 30,
    OPTIMAL_MAX: 60,
    CRITICAL_LOW: 20,
    CRITICAL_HIGH: 80,
  },
  TASKS: {
    OVERDUE_CRITICAL: 5,
    OVERDUE_WARNING: 2,
    PENDING_WARNING: 10,
  },
  ASTRAL: {
    EXCELLENT: 80,
    GOOD: 60,
    MODERATE: 40,
  },
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Main Hook
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hook to calculate comprehensive Living Field Score
 * خطاف لحساب درجة الحقل الحي الشاملة
 *
 * @param fieldId - The field ID to calculate score for
 * @param options - Hook options
 * @returns Living Field Score data with alerts and recommendations
 */
export function useLivingFieldScore(
  fieldId: string,
  options: UseLivingFieldScoreOptions = {}
) {
  const {
    enabled = true,
    includeAlerts = true,
    includeRecommendations = true,
  } = options;

  // Fetch data from multiple sources
  const { data: ndviData, isLoading: isLoadingNDVI } = useFieldNDVI(fieldId);
  const { data: weatherData, isLoading: isLoadingWeather } = useCurrentWeather({ enabled });
  const { data: astronomicalData, isLoading: isLoadingAstro } = useAstronomicalToday({ enabled });
  const { data: tasksData, isLoading: isLoadingTasks } = useTasksByField(fieldId);
  const { data: sensorsData, isLoading: isLoadingSensors } = useSensors({
    fieldId,
    type: 'soil_moisture',
  });

  const isLoading = isLoadingNDVI || isLoadingWeather || isLoadingAstro || isLoadingTasks || isLoadingSensors;

  // Calculate scores with memoization
  const score = useMemo((): LivingFieldScore => {
    // Health Score (0-100) - Based on NDVI
    const health = calculateHealthScore(ndviData);

    // Hydration Score (0-100) - Based on soil moisture and weather
    const hydration = calculateHydrationScore(sensorsData, weatherData);

    // Attention Score (0-100) - Based on task completion and urgency
    const attention = calculateAttentionScore(tasksData || []);

    // Astral Score (0-100) - Based on astronomical conditions
    const astral = calculateAstralScore(astronomicalData);

    // Overall Score - Weighted average
    const overall = calculateOverallScore(health, hydration, attention, astral);

    // Determine trend
    const trend = determineTrend(ndviData, health);

    // Generate alerts
    const alerts = includeAlerts
      ? generateAlerts(fieldId, health, hydration, attention, ndviData, sensorsData, tasksData)
      : [];

    // Generate recommendations
    const recommendations = includeRecommendations
      ? generateRecommendations(health, hydration, attention, astral, ndviData, weatherData, astronomicalData)
      : [];

    return {
      overall,
      health,
      hydration,
      attention,
      astral,
      trend,
      alerts,
      recommendations,
      lastUpdated: new Date(),
    };
  }, [
    ndviData,
    weatherData,
    astronomicalData,
    tasksData,
    sensorsData,
    fieldId,
    includeAlerts,
    includeRecommendations,
  ]);

  return {
    data: score,
    isLoading,
    isError: false, // Individual queries handle their own errors
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// Score Calculation Functions
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Calculate Health Score based on NDVI data
 */
function calculateHealthScore(ndviData: any): number {
  if (!ndviData) return 50; // Neutral score if no data

  const { ndviMean, healthStatus } = ndviData;

  // Map health status to score
  const statusScoreMap = {
    excellent: 95,
    good: 80,
    moderate: 60,
    poor: 35,
    critical: 15,
  };

  // Use status-based score if available, otherwise calculate from NDVI value
  if (healthStatus && healthStatus in statusScoreMap) {
    return statusScoreMap[healthStatus as keyof typeof statusScoreMap];
  }

  // Calculate from NDVI value (0-1 range to 0-100 score)
  if (typeof ndviMean === 'number') {
    if (ndviMean >= THRESHOLDS.NDVI.EXCELLENT) return 95;
    if (ndviMean >= THRESHOLDS.NDVI.GOOD) return 75;
    if (ndviMean >= THRESHOLDS.NDVI.MODERATE) return 50;
    if (ndviMean >= THRESHOLDS.NDVI.POOR) return 25;
    return 10;
  }

  return 50;
}

/**
 * Calculate Hydration Score based on soil moisture sensors and weather
 */
function calculateHydrationScore(sensors: any[] | undefined, weather: any): number {
  let score = 50; // Base score

  // Check soil moisture sensors
  if (sensors && sensors.length > 0) {
    const moistureSensors = sensors.filter(s => s.type === 'soil_moisture');

    if (moistureSensors.length > 0) {
      const avgMoisture = moistureSensors.reduce((sum, s) => {
        const value = s.lastReading?.value || 0;
        return sum + value;
      }, 0) / moistureSensors.length;

      // Optimal range: 30-60%
      if (avgMoisture >= THRESHOLDS.SOIL_MOISTURE.OPTIMAL_MIN &&
          avgMoisture <= THRESHOLDS.SOIL_MOISTURE.OPTIMAL_MAX) {
        score = 90;
      } else if (avgMoisture < THRESHOLDS.SOIL_MOISTURE.CRITICAL_LOW) {
        score = 20; // Critical low
      } else if (avgMoisture > THRESHOLDS.SOIL_MOISTURE.CRITICAL_HIGH) {
        score = 30; // Critical high (over-irrigation)
      } else if (avgMoisture < THRESHOLDS.SOIL_MOISTURE.OPTIMAL_MIN) {
        score = 60; // Slightly low
      } else {
        score = 70; // Slightly high
      }
    }
  }

  // Adjust based on weather conditions
  if (weather) {
    const { humidity, temperature } = weather;

    // High temperature + low humidity = increased water stress
    if (temperature > 35 && humidity < 30) {
      score = Math.max(0, score - 15);
    }

    // Good humidity helps
    if (humidity >= 50 && humidity <= 70) {
      score = Math.min(100, score + 5);
    }
  }

  return Math.round(score);
}

/**
 * Calculate Attention Score based on task completion
 */
function calculateAttentionScore(tasks: Task[]): number {
  if (!tasks || tasks.length === 0) return 100; // No tasks = no issues

  const now = new Date();
  let overdueTasks = 0;
  let pendingTasks = 0;
  let completedTasks = 0;

  tasks.forEach(task => {
    const dueDate = task.due_date ? new Date(task.due_date) : null;

    if (task.status === 'completed') {
      completedTasks++;
    } else if (task.status === 'open' || task.status === 'in_progress') {
      pendingTasks++;

      if (dueDate && dueDate < now) {
        overdueTasks++;
      }
    }
  });

  // Start with perfect score
  let score = 100;

  // Deduct for overdue tasks (critical)
  if (overdueTasks >= THRESHOLDS.TASKS.OVERDUE_CRITICAL) {
    score -= 50;
  } else if (overdueTasks >= THRESHOLDS.TASKS.OVERDUE_WARNING) {
    score -= 25;
  } else if (overdueTasks > 0) {
    score -= (overdueTasks * 10);
  }

  // Deduct for too many pending tasks
  if (pendingTasks >= THRESHOLDS.TASKS.PENDING_WARNING) {
    score -= 20;
  } else if (pendingTasks > 5) {
    score -= 10;
  }

  // Bonus for completion rate
  const total = tasks.length;
  const completionRate = total > 0 ? completedTasks / total : 0;
  if (completionRate > 0.8) {
    score = Math.min(100, score + 10);
  }

  return Math.max(0, Math.round(score));
}

/**
 * Calculate Astral Score based on astronomical conditions
 */
function calculateAstralScore(astronomicalData: any): number {
  if (!astronomicalData) return 50; // Neutral score if no data

  const { overall_farming_score, moon_phase, lunar_mansion } = astronomicalData;

  // Use overall farming score if available (assuming it's 0-100)
  if (typeof overall_farming_score === 'number') {
    return Math.round(overall_farming_score);
  }

  // Calculate from moon phase and lunar mansion
  let score = 50;

  if (moon_phase?.farming_good) {
    score += 20;
  }

  if (lunar_mansion?.farming_score) {
    // Assuming farming_score is 0-10, convert to 0-30 range
    score += Math.round((lunar_mansion.farming_score / 10) * 30);
  }

  return Math.min(100, Math.round(score));
}

/**
 * Calculate Overall Score (weighted average)
 */
function calculateOverallScore(
  health: number,
  hydration: number,
  attention: number,
  astral: number
): number {
  // Weights: Health and Hydration are most critical
  const weights = {
    health: 0.35,
    hydration: 0.35,
    attention: 0.20,
    astral: 0.10,
  };

  const overall =
    health * weights.health +
    hydration * weights.hydration +
    attention * weights.attention +
    astral * weights.astral;

  return Math.round(overall);
}

/**
 * Determine trend based on NDVI history
 */
function determineTrend(ndviData: any, currentHealth: number): 'improving' | 'stable' | 'declining' {
  if (!ndviData) return 'stable';

  // Check if we have historical data or trend info
  if (ndviData.trend) {
    return ndviData.trend;
  }

  // Fallback: use current health level
  if (currentHealth >= 75) return 'stable';
  if (currentHealth >= 50) return 'stable';
  return 'declining';
}

// ═══════════════════════════════════════════════════════════════════════════════
// Alert Generation
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Generate alerts based on field conditions
 */
function generateAlerts(
  fieldId: string,
  health: number,
  _hydration: number,
  _attention: number,
  _ndviData: any,
  sensors: any[] | undefined,
  tasks: Task[] | undefined
): FieldAlert[] {
  const alerts: FieldAlert[] = [];
  const now = new Date().toISOString();

  // Health alerts
  if (health < 30) {
    alerts.push({
      id: `${fieldId}-health-critical`,
      severity: 'critical',
      category: 'crop_health',
      title: 'Critical Crop Health',
      titleAr: 'صحة المحصول حرجة',
      message: 'Crop health is critically low. Immediate action required.',
      messageAr: 'صحة المحصول منخفضة بشكل حرج. مطلوب إجراء فوري.',
      timestamp: now,
      currentValue: health,
      threshold: 30,
    });
  } else if (health < 50) {
    alerts.push({
      id: `${fieldId}-health-warning`,
      severity: 'warning',
      category: 'crop_health',
      title: 'Low Crop Health',
      titleAr: 'صحة المحصول منخفضة',
      message: 'Crop health is below optimal levels. Consider investigation.',
      messageAr: 'صحة المحصول أقل من المستويات المثالية. يُنصح بالفحص.',
      timestamp: now,
      currentValue: health,
      threshold: 50,
    });
  }

  // Hydration alerts
  if (sensors && sensors.length > 0) {
    const moistureSensors = sensors.filter(s => s.type === 'soil_moisture');
    const avgMoisture = moistureSensors.length > 0
      ? moistureSensors.reduce((sum, s) => sum + (s.lastReading?.value || 0), 0) / moistureSensors.length
      : null;

    if (avgMoisture !== null) {
      if (avgMoisture < THRESHOLDS.SOIL_MOISTURE.CRITICAL_LOW) {
        alerts.push({
          id: `${fieldId}-moisture-critical-low`,
          severity: 'critical',
          category: 'irrigation',
          title: 'Critical Low Soil Moisture',
          titleAr: 'رطوبة التربة منخفضة للغاية',
          message: `Soil moisture is critically low at ${avgMoisture.toFixed(1)}%. Immediate irrigation required.`,
          messageAr: `رطوبة التربة منخفضة جداً عند ${avgMoisture.toFixed(1)}٪. مطلوب ري فوري.`,
          timestamp: now,
          currentValue: avgMoisture,
          threshold: THRESHOLDS.SOIL_MOISTURE.CRITICAL_LOW,
        });
      } else if (avgMoisture > THRESHOLDS.SOIL_MOISTURE.CRITICAL_HIGH) {
        alerts.push({
          id: `${fieldId}-moisture-critical-high`,
          severity: 'warning',
          category: 'irrigation',
          title: 'Excessive Soil Moisture',
          titleAr: 'رطوبة التربة مفرطة',
          message: `Soil moisture is too high at ${avgMoisture.toFixed(1)}%. Risk of waterlogging.`,
          messageAr: `رطوبة التربة عالية جداً عند ${avgMoisture.toFixed(1)}٪. خطر تشبع التربة بالماء.`,
          timestamp: now,
          currentValue: avgMoisture,
          threshold: THRESHOLDS.SOIL_MOISTURE.CRITICAL_HIGH,
        });
      }
    }
  }

  // Task attention alerts
  if (tasks && tasks.length > 0) {
    const now = new Date();
    const overdueTasks = tasks.filter(t => {
      const dueDate = t.due_date ? new Date(t.due_date) : null;
      return (t.status === 'open' || t.status === 'in_progress') && dueDate && dueDate < now;
    });

    if (overdueTasks.length >= THRESHOLDS.TASKS.OVERDUE_CRITICAL) {
      alerts.push({
        id: `${fieldId}-tasks-overdue-critical`,
        severity: 'critical',
        category: 'system',
        title: 'Multiple Overdue Tasks',
        titleAr: 'مهام متعددة متأخرة',
        message: `${overdueTasks.length} tasks are overdue. Field requires immediate attention.`,
        messageAr: `${overdueTasks.length} مهام متأخرة. الحقل يحتاج إلى اهتمام فوري.`,
        timestamp: now.toISOString(),
        currentValue: overdueTasks.length,
        threshold: THRESHOLDS.TASKS.OVERDUE_CRITICAL,
      });
    } else if (overdueTasks.length >= THRESHOLDS.TASKS.OVERDUE_WARNING) {
      alerts.push({
        id: `${fieldId}-tasks-overdue-warning`,
        severity: 'warning',
        category: 'system',
        title: 'Overdue Tasks',
        titleAr: 'مهام متأخرة',
        message: `${overdueTasks.length} tasks are overdue. Please review field activities.`,
        messageAr: `${overdueTasks.length} مهام متأخرة. يرجى مراجعة أنشطة الحقل.`,
        timestamp: now.toISOString(),
        currentValue: overdueTasks.length,
        threshold: THRESHOLDS.TASKS.OVERDUE_WARNING,
      });
    }
  }

  return alerts;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Recommendation Generation
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Generate recommendations based on field conditions
 */
function generateRecommendations(
  health: number,
  hydration: number,
  attention: number,
  _astral: number,
  _ndviData: any,
  weatherData: any,
  astronomicalData: any
): Recommendation[] {
  const recommendations: Recommendation[] = [];

  // Health recommendations
  if (health < 50) {
    recommendations.push({
      id: 'rec-health-improve',
      type: 'general',
      priority: health < 30 ? 'urgent' : 'high',
      title: 'Improve Crop Health',
      titleAr: 'تحسين صحة المحصول',
      description: 'Crop health indicators are below optimal levels. Consider soil testing and nutrient analysis.',
      descriptionAr: 'مؤشرات صحة المحصول أقل من المستويات المثالية. يُنصح بفحص التربة وتحليل المغذيات.',
      actionItems: [
        'Conduct soil nutrient analysis',
        'Check for pest or disease signs',
        'Review irrigation schedule',
        'Consider targeted fertilization',
      ],
      expectedBenefit: 'Improved crop vitality and yield potential',
      expectedBenefitAr: 'تحسين حيوية المحصول وإمكانات الإنتاج',
    });
  }

  // Hydration recommendations
  if (hydration < 40) {
    recommendations.push({
      id: 'rec-irrigation-increase',
      type: 'irrigation',
      priority: 'urgent',
      title: 'Increase Irrigation',
      titleAr: 'زيادة الري',
      description: 'Soil moisture levels are critically low. Immediate irrigation is recommended.',
      descriptionAr: 'مستويات رطوبة التربة منخفضة للغاية. يُوصى بالري الفوري.',
      actionItems: [
        'Schedule immediate irrigation',
        'Check irrigation system functionality',
        'Monitor soil moisture sensors',
        'Adjust irrigation frequency',
      ],
      expectedBenefit: 'Prevent crop stress and maintain healthy growth',
      expectedBenefitAr: 'منع إجهاد المحصول والحفاظ على نمو صحي',
    });
  } else if (hydration > 80) {
    recommendations.push({
      id: 'rec-irrigation-reduce',
      type: 'irrigation',
      priority: 'high',
      title: 'Reduce Irrigation',
      titleAr: 'تقليل الري',
      description: 'Soil moisture is too high. Reduce irrigation to prevent waterlogging and root diseases.',
      descriptionAr: 'رطوبة التربة عالية جداً. قلل الري لمنع تشبع التربة بالماء وأمراض الجذور.',
      actionItems: [
        'Pause irrigation temporarily',
        'Improve field drainage',
        'Monitor for signs of waterlogging',
        'Adjust irrigation schedule',
      ],
      expectedBenefit: 'Prevent root rot and optimize water usage',
      expectedBenefitAr: 'منع تعفن الجذور وتحسين استخدام المياه',
    });
  }

  // Task attention recommendations
  if (attention < 60) {
    recommendations.push({
      id: 'rec-tasks-complete',
      type: 'general',
      priority: 'high',
      title: 'Complete Pending Tasks',
      titleAr: 'إكمال المهام المعلقة',
      description: 'Several field tasks are pending or overdue. Completing them will improve field management.',
      descriptionAr: 'عدة مهام حقلية معلقة أو متأخرة. إكمالها سيحسن إدارة الحقل.',
      actionItems: [
        'Review overdue tasks',
        'Prioritize urgent activities',
        'Assign tasks to team members',
        'Update task completion status',
      ],
      expectedBenefit: 'Better field management and timely crop care',
      expectedBenefitAr: 'إدارة أفضل للحقل ورعاية المحصول في الوقت المناسب',
    });
  }

  // Astronomical recommendations
  if (astronomicalData?.recommendations && astronomicalData.recommendations.length > 0) {
    const astroRec = astronomicalData.recommendations[0]; // Take the top recommendation

    if (astroRec.suitability_score > 70) {
      recommendations.push({
        id: 'rec-astro-optimal',
        type: 'planting',
        priority: 'medium',
        title: `Optimal for ${astroRec.activity}`,
        titleAr: `مثالي لـ ${astroRec.activity}`,
        description: astroRec.reason || 'Current astronomical conditions are favorable for this activity.',
        descriptionAr: astroRec.reason || 'الظروف الفلكية الحالية مواتية لهذا النشاط.',
        actionItems: [
          `Plan ${astroRec.activity} activities`,
          'Check weather forecast',
          'Prepare necessary equipment',
        ],
        expectedBenefit: 'Take advantage of optimal astronomical timing',
        expectedBenefitAr: 'الاستفادة من التوقيت الفلكي المثالي',
      });
    }
  }

  // Weather-based recommendations
  if (weatherData) {
    const { temperature, humidity } = weatherData;

    if (temperature > 35 && humidity < 30) {
      recommendations.push({
        id: 'rec-heat-stress',
        type: 'irrigation',
        priority: 'high',
        title: 'Heat Stress Mitigation',
        titleAr: 'التخفيف من الإجهاد الحراري',
        description: 'High temperatures and low humidity increase water stress. Extra care needed.',
        descriptionAr: 'درجات الحرارة المرتفعة والرطوبة المنخفضة تزيد من إجهاد الماء. مطلوب عناية إضافية.',
        actionItems: [
          'Increase irrigation frequency',
          'Consider shade netting if available',
          'Monitor crops for stress signs',
          'Apply mulch to retain moisture',
        ],
        expectedBenefit: 'Protect crops from heat damage',
        expectedBenefitAr: 'حماية المحاصيل من أضرار الحرارة',
      });
    }
  }

  return recommendations;
}
