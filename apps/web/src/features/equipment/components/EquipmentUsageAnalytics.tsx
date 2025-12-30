/**
 * Equipment Usage Analytics Component
 * مكون تحليلات استخدام المعدات
 *
 * Similar to John Deere Operations Center - Provides comprehensive analytics
 * for equipment usage, fuel consumption, utilization, and maintenance tracking
 */

'use client';

import { useState, useMemo } from 'react';
import {
  Clock,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  Check,
  RefreshCw,
  Settings,
  MapPin,
} from 'lucide-react';

// ==================== TypeScript Interfaces ====================

export interface EquipmentUsage {
  equipmentId: string;
  equipmentName: string;
  equipmentNameAr: string;
  type: 'tractor' | 'harvester' | 'irrigation_system' | 'sprayer' | 'planter' | 'other';
  operatingHours: {
    daily: number[];
    weekly: number[];
    monthly: number[];
  };
  fuelConsumption: FuelMetrics;
  utilization: UtilizationData;
  costPerHour: number;
  downtime: DowntimeData;
  maintenanceStatus: MaintenanceStatus;
  location?: string;
  lastUpdated: string;
}

export interface FuelMetrics {
  currentLevel: number; // percentage
  consumption: {
    daily: number; // liters
    weekly: number;
    monthly: number;
  };
  efficiency: {
    litersPerHour: number;
    trend: 'up' | 'down' | 'stable';
    changePercentage: number;
  };
  totalCost: number;
  estimatedDaysRemaining: number;
}

export interface UtilizationData {
  rate: number; // percentage
  activeHours: number;
  totalAvailableHours: number;
  trend: 'up' | 'down' | 'stable';
  changePercentage: number;
}

export interface DowntimeData {
  totalHours: number;
  reasons: Array<{
    reason: string;
    reasonAr: string;
    hours: number;
    percentage: number;
  }>;
  lastIncident: {
    date: string;
    reason: string;
    reasonAr: string;
    duration: number;
  };
}

export type MaintenanceStatus = 'good' | 'warning' | 'critical';

export interface EquipmentComparisonData {
  equipmentId: string;
  name: string;
  nameAr: string;
  operatingHours: number;
  utilization: number;
  fuelEfficiency: number;
  costPerHour: number;
  maintenanceStatus: MaintenanceStatus;
}

type TimeRange = 'daily' | 'weekly' | 'monthly';

// ==================== Mock Data ====================

const generateMockData = (): EquipmentUsage[] => {
  return [
    {
      equipmentId: 'eq-001',
      equipmentName: 'John Deere 8R Series Tractor',
      equipmentNameAr: 'جرار جون ديري سلسلة 8R',
      type: 'tractor',
      operatingHours: {
        daily: [8.5, 9.2, 7.8, 8.1, 9.5, 6.3, 8.9],
        weekly: [56.3, 58.1, 52.4, 55.7],
        monthly: [228, 235, 220, 242],
      },
      fuelConsumption: {
        currentLevel: 68,
        consumption: {
          daily: 45.2,
          weekly: 316.4,
          monthly: 1285.6,
        },
        efficiency: {
          litersPerHour: 5.3,
          trend: 'down',
          changePercentage: -3.2,
        },
        totalCost: 257120,
        estimatedDaysRemaining: 12,
      },
      utilization: {
        rate: 78.5,
        activeHours: 188,
        totalAvailableHours: 240,
        trend: 'up',
        changePercentage: 5.3,
      },
      costPerHour: 1250,
      downtime: {
        totalHours: 18.5,
        reasons: [
          { reason: 'Routine Maintenance', reasonAr: 'صيانة دورية', hours: 8.0, percentage: 43.2 },
          { reason: 'Fuel Refill', reasonAr: 'إعادة تعبئة الوقود', hours: 5.5, percentage: 29.7 },
          { reason: 'Repair', reasonAr: 'إصلاح', hours: 3.0, percentage: 16.2 },
          { reason: 'Weather', reasonAr: 'طقس', hours: 2.0, percentage: 10.8 },
        ],
        lastIncident: {
          date: '2025-12-28',
          reason: 'Routine Maintenance',
          reasonAr: 'صيانة دورية',
          duration: 3.5,
        },
      },
      maintenanceStatus: 'good',
      location: 'Field A - North Section',
      lastUpdated: '2025-12-30T10:30:00Z',
    },
    {
      equipmentId: 'eq-002',
      equipmentName: 'Case IH Axial-Flow Harvester',
      equipmentNameAr: 'حصادة كيس IH محورية',
      type: 'harvester',
      operatingHours: {
        daily: [7.2, 8.5, 6.9, 7.8, 8.2, 5.5, 7.9],
        weekly: [52.0, 50.3, 48.6, 51.2],
        monthly: [205, 198, 210, 215],
      },
      fuelConsumption: {
        currentLevel: 42,
        consumption: {
          daily: 62.8,
          weekly: 439.6,
          monthly: 1788.4,
        },
        efficiency: {
          litersPerHour: 7.8,
          trend: 'stable',
          changePercentage: 0.5,
        },
        totalCost: 357680,
        estimatedDaysRemaining: 5,
      },
      utilization: {
        rate: 65.2,
        activeHours: 156,
        totalAvailableHours: 240,
        trend: 'down',
        changePercentage: -2.8,
      },
      costPerHour: 1680,
      downtime: {
        totalHours: 32.0,
        reasons: [
          { reason: 'Belt Replacement', reasonAr: 'استبدال السير', hours: 12.0, percentage: 37.5 },
          { reason: 'Fuel Refill', reasonAr: 'إعادة تعبئة الوقود', hours: 8.0, percentage: 25.0 },
          { reason: 'Routine Maintenance', reasonAr: 'صيانة دورية', hours: 7.0, percentage: 21.9 },
          { reason: 'Operator Break', reasonAr: 'استراحة المشغل', hours: 5.0, percentage: 15.6 },
        ],
        lastIncident: {
          date: '2025-12-29',
          reason: 'Belt Replacement',
          reasonAr: 'استبدال السير',
          duration: 4.0,
        },
      },
      maintenanceStatus: 'warning',
      location: 'Field B - South Section',
      lastUpdated: '2025-12-30T09:15:00Z',
    },
    {
      equipmentId: 'eq-003',
      equipmentName: 'Valley Pivot Irrigation System',
      equipmentNameAr: 'نظام الري المحوري فالي',
      type: 'irrigation_system',
      operatingHours: {
        daily: [12.0, 14.5, 13.2, 15.0, 14.8, 16.0, 13.5],
        weekly: [98.8, 102.3, 95.6, 99.0],
        monthly: [398, 405, 388, 410],
      },
      fuelConsumption: {
        currentLevel: 25,
        consumption: {
          daily: 28.5,
          weekly: 199.5,
          monthly: 810.6,
        },
        efficiency: {
          litersPerHour: 2.1,
          trend: 'up',
          changePercentage: 4.8,
        },
        totalCost: 162120,
        estimatedDaysRemaining: 3,
      },
      utilization: {
        rate: 92.3,
        activeHours: 221,
        totalAvailableHours: 240,
        trend: 'up',
        changePercentage: 7.2,
      },
      costPerHour: 420,
      downtime: {
        totalHours: 8.5,
        reasons: [
          { reason: 'Filter Cleaning', reasonAr: 'تنظيف الفلتر', hours: 4.0, percentage: 47.1 },
          { reason: 'System Check', reasonAr: 'فحص النظام', hours: 2.5, percentage: 29.4 },
          { reason: 'Fuel Refill', reasonAr: 'إعادة تعبئة الوقود', hours: 2.0, percentage: 23.5 },
        ],
        lastIncident: {
          date: '2025-12-27',
          reason: 'Filter Cleaning',
          reasonAr: 'تنظيف الفلتر',
          duration: 2.0,
        },
      },
      maintenanceStatus: 'critical',
      location: 'Field C - Central',
      lastUpdated: '2025-12-30T11:00:00Z',
    },
  ];
};

// ==================== Component Props ====================

interface EquipmentUsageAnalyticsProps {
  equipmentId?: string;
  showComparison?: boolean;
  initialTimeRange?: TimeRange;
}

// ==================== Main Component ====================

export function EquipmentUsageAnalytics({
  equipmentId,
  showComparison = true,
  initialTimeRange = 'daily',
}: EquipmentUsageAnalyticsProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>(initialTimeRange);
  const [selectedEquipmentId, setSelectedEquipmentId] = useState<string>(equipmentId || 'eq-001');
  const [isLoading, setIsLoading] = useState(false);
  const [_error, _setError] = useState<string | null>(null);
  void _error; void _setError; // Reserved for API error handling

  // Mock data - in production, this would come from an API
  const allEquipmentData = useMemo(() => generateMockData(), []);

  const selectedEquipment = useMemo(
    () => allEquipmentData.find((eq) => eq.equipmentId === selectedEquipmentId),
    [allEquipmentData, selectedEquipmentId]
  );

  const comparisonData: EquipmentComparisonData[] = useMemo(
    () =>
      allEquipmentData.map((eq) => ({
        equipmentId: eq.equipmentId,
        name: eq.equipmentName,
        nameAr: eq.equipmentNameAr,
        operatingHours:
          timeRange === 'daily'
            ? eq.operatingHours.daily.reduce((a, b) => a + b, 0)
            : timeRange === 'weekly'
            ? eq.operatingHours.weekly.reduce((a, b) => a + b, 0)
            : eq.operatingHours.monthly.reduce((a, b) => a + b, 0),
        utilization: eq.utilization.rate,
        fuelEfficiency: eq.fuelConsumption.efficiency.litersPerHour,
        costPerHour: eq.costPerHour,
        maintenanceStatus: eq.maintenanceStatus,
      })),
    [allEquipmentData, timeRange]
  );

  if (!selectedEquipment) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center" data-testid="analytics-error">
        <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-3" />
        <p className="text-red-800 font-semibold">معدات غير موجودة</p>
        <p className="text-red-600 text-sm mt-1">Equipment not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="equipment-usage-analytics">
      {/* Header Section */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900 mb-1" data-testid="analytics-title-ar">
              {selectedEquipment.equipmentNameAr}
            </h1>
            <p className="text-gray-600 mb-2" data-testid="analytics-title-en">
              {selectedEquipment.equipmentName}
            </p>
            {selectedEquipment.location && (
              <div className="flex items-center text-sm text-gray-500">
                <MapPin className="w-4 h-4 ml-1" />
                <span>{selectedEquipment.location}</span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-3">
            {/* Equipment Selector */}
            <select
              value={selectedEquipmentId}
              onChange={(e) => setSelectedEquipmentId(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              data-testid="equipment-selector"
            >
              {allEquipmentData.map((eq) => (
                <option key={eq.equipmentId} value={eq.equipmentId}>
                  {eq.equipmentNameAr}
                </option>
              ))}
            </select>

            {/* Time Range Selector */}
            <div className="flex bg-gray-100 rounded-lg p-1">
              {(['daily', 'weekly', 'monthly'] as TimeRange[]).map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    timeRange === range
                      ? 'bg-white text-green-600 shadow'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                  data-testid={`time-range-${range}`}
                >
                  {range === 'daily' ? 'يومي' : range === 'weekly' ? 'أسبوعي' : 'شهري'}
                </button>
              ))}
            </div>

            {/* Refresh Button */}
            <button
              onClick={() => {
                setIsLoading(true);
                setTimeout(() => setIsLoading(false), 1000);
              }}
              disabled={isLoading}
              className="p-2 text-gray-600 hover:text-green-600 transition-colors disabled:opacity-50"
              title="تحديث البيانات / Refresh"
              data-testid="refresh-button"
            >
              <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Last Updated */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            آخر تحديث: {new Date(selectedEquipment.lastUpdated).toLocaleString('ar-YE')} •
            Last updated: {new Date(selectedEquipment.lastUpdated).toLocaleString('en-US')}
          </p>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Utilization Rate */}
        <MetricCard
          title="معدل الاستخدام"
          titleEn="Utilization Rate"
          value={`${selectedEquipment.utilization.rate}%`}
          icon={<Clock className="w-6 h-6" />}
          trend={selectedEquipment.utilization.trend}
          trendValue={selectedEquipment.utilization.changePercentage}
          color="blue"
        />

        {/* Fuel Efficiency */}
        <MetricCard
          title="كفاءة الوقود"
          titleEn="Fuel Efficiency"
          value={`${selectedEquipment.fuelConsumption.efficiency.litersPerHour} L/h`}
          icon={<TrendingUp className="w-6 h-6" />}
          trend={selectedEquipment.fuelConsumption.efficiency.trend}
          trendValue={selectedEquipment.fuelConsumption.efficiency.changePercentage}
          color="green"
          inverted
        />

        {/* Cost Per Hour */}
        <MetricCard
          title="التكلفة في الساعة"
          titleEn="Cost Per Hour"
          value={`${selectedEquipment.costPerHour.toLocaleString('ar-YE')} ريال`}
          icon={<TrendingDown className="w-6 h-6" />}
          color="orange"
        />

        {/* Maintenance Status */}
        <MaintenanceStatusCard status={selectedEquipment.maintenanceStatus} />
      </div>

      {/* Operating Hours Chart */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">ساعات التشغيل</h2>
            <p className="text-sm text-gray-500">Operating Hours</p>
          </div>
          <Clock className="w-6 h-6 text-blue-600" />
        </div>
        <OperatingHoursChart
          data={selectedEquipment.operatingHours}
          timeRange={timeRange}
        />
      </div>

      {/* Fuel Consumption & Downtime */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fuel Consumption */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">استهلاك الوقود</h2>
          <p className="text-sm text-gray-500 mb-6">Fuel Consumption</p>
          <FuelConsumptionMetrics
            fuelMetrics={selectedEquipment.fuelConsumption}
            timeRange={timeRange}
          />
        </div>

        {/* Downtime Analysis */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">تحليل التوقف</h2>
          <p className="text-sm text-gray-500 mb-6">Downtime Analysis</p>
          <DowntimeAnalysis downtime={selectedEquipment.downtime} />
        </div>
      </div>

      {/* Equipment Comparison Table */}
      {showComparison && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">مقارنة المعدات</h2>
          <p className="text-sm text-gray-500 mb-6">Equipment Comparison</p>
          <EquipmentComparisonTable
            data={comparisonData}
            selectedEquipmentId={selectedEquipmentId}
          />
        </div>
      )}
    </div>
  );
}

// ==================== Sub-Components ====================

interface MetricCardProps {
  title: string;
  titleEn: string;
  value: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: number;
  color: 'blue' | 'green' | 'orange' | 'red';
  inverted?: boolean; // If true, down trend is good
}

function MetricCard({
  title,
  titleEn,
  value,
  icon,
  trend,
  trendValue,
  color,
  inverted = false,
}: MetricCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    orange: 'bg-orange-50 text-orange-600',
    red: 'bg-red-50 text-red-600',
  };

  const getTrendColor = () => {
    if (!trend || trend === 'stable') return 'text-gray-500';
    const isPositive = inverted ? trend === 'down' : trend === 'up';
    return isPositive ? 'text-green-600' : 'text-red-600';
  };

  const getTrendIcon = () => {
    if (!trend || trend === 'stable') return null;
    return trend === 'up' ? (
      <TrendingUp className="w-4 h-4" />
    ) : (
      <TrendingDown className="w-4 h-4" />
    );
  };

  return (
    <div className="bg-white rounded-lg shadow p-6" data-testid={`metric-card-${titleEn.toLowerCase().replace(/\s+/g, '-')}`}>
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>{icon}</div>
        {trend && trendValue !== undefined && (
          <div className={`flex items-center gap-1 text-sm font-medium ${getTrendColor()}`}>
            {getTrendIcon()}
            <span>{Math.abs(trendValue).toFixed(1)}%</span>
          </div>
        )}
      </div>
      <h3 className="text-2xl font-bold text-gray-900 mb-1">{value}</h3>
      <p className="text-sm font-medium text-gray-900">{title}</p>
      <p className="text-xs text-gray-500">{titleEn}</p>
    </div>
  );
}

interface MaintenanceStatusCardProps {
  status: MaintenanceStatus;
}

function MaintenanceStatusCard({ status }: MaintenanceStatusCardProps) {
  const statusConfig = {
    good: {
      icon: <Check className="w-6 h-6" />,
      color: 'bg-green-50 text-green-600',
      bgColor: 'bg-green-500',
      title: 'جيد',
      titleEn: 'Good',
      description: 'الصيانة محدثة',
      descriptionEn: 'Maintenance up to date',
    },
    warning: {
      icon: <Settings className="w-6 h-6" />,
      color: 'bg-yellow-50 text-yellow-600',
      bgColor: 'bg-yellow-500',
      title: 'تحذير',
      titleEn: 'Warning',
      description: 'صيانة قريبة',
      descriptionEn: 'Maintenance due soon',
    },
    critical: {
      icon: <AlertCircle className="w-6 h-6" />,
      color: 'bg-red-50 text-red-600',
      bgColor: 'bg-red-500',
      title: 'حرج',
      titleEn: 'Critical',
      description: 'صيانة عاجلة مطلوبة',
      descriptionEn: 'Urgent maintenance required',
    },
  };

  const config = statusConfig[status];

  return (
    <div className="bg-white rounded-lg shadow p-6" data-testid="maintenance-status-card">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-lg ${config.color}`}>{config.icon}</div>
        <div className={`w-3 h-3 rounded-full ${config.bgColor} animate-pulse`} />
      </div>
      <h3 className="text-2xl font-bold text-gray-900 mb-1">{config.title}</h3>
      <p className="text-sm font-medium text-gray-900">{config.description}</p>
      <p className="text-xs text-gray-500">{config.titleEn} - {config.descriptionEn}</p>
    </div>
  );
}

interface OperatingHoursChartProps {
  data: {
    daily: number[];
    weekly: number[];
    monthly: number[];
  };
  timeRange: TimeRange;
}

function OperatingHoursChart({ data, timeRange }: OperatingHoursChartProps) {
  const chartData = data[timeRange];
  const maxValue = Math.max(...chartData);

  const getLabel = (index: number) => {
    if (timeRange === 'daily') {
      const days = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'];
      return days[index];
    } else if (timeRange === 'weekly') {
      return `أسبوع ${index + 1}`;
    } else {
      const months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'];
      const currentMonth = new Date().getMonth();
      const monthIndex = (currentMonth - chartData.length + 1 + index + 12) % 12;
      return months[monthIndex];
    }
  };

  return (
    <div className="space-y-4" data-testid="operating-hours-chart">
      {/* Chart */}
      <div className="flex items-end justify-between gap-2 h-64">
        {chartData.map((value, index) => {
          const heightPercentage = (value / maxValue) * 100;
          return (
            <div key={index} className="flex-1 flex flex-col items-center gap-2">
              <div className="w-full flex flex-col items-center justify-end h-full">
                <span className="text-xs font-medium text-gray-600 mb-1">
                  {value.toFixed(1)}h
                </span>
                <div
                  className="w-full bg-blue-500 rounded-t-lg transition-all hover:bg-blue-600 relative group"
                  style={{ height: `${heightPercentage}%`, minHeight: '4px' }}
                >
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block bg-gray-900 text-white text-xs rounded py-1 px-2 whitespace-nowrap">
                    {value.toFixed(2)} ساعة
                  </div>
                </div>
              </div>
              <span className="text-xs text-gray-600 text-center">{getLabel(index)}</span>
            </div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-900">
            {chartData.reduce((a, b) => a + b, 0).toFixed(1)}
          </p>
          <p className="text-xs text-gray-500">إجمالي الساعات / Total Hours</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-900">
            {(chartData.reduce((a, b) => a + b, 0) / chartData.length).toFixed(1)}
          </p>
          <p className="text-xs text-gray-500">المتوسط / Average</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-900">{Math.max(...chartData).toFixed(1)}</p>
          <p className="text-xs text-gray-500">الأعلى / Peak</p>
        </div>
      </div>
    </div>
  );
}

interface FuelConsumptionMetricsProps {
  fuelMetrics: FuelMetrics;
  timeRange: TimeRange;
}

function FuelConsumptionMetrics({ fuelMetrics, timeRange }: FuelConsumptionMetricsProps) {
  const consumption =
    timeRange === 'daily'
      ? fuelMetrics.consumption.daily
      : timeRange === 'weekly'
      ? fuelMetrics.consumption.weekly
      : fuelMetrics.consumption.monthly;

  return (
    <div className="space-y-6" data-testid="fuel-consumption-metrics">
      {/* Fuel Level Gauge */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">مستوى الوقود الحالي</span>
          <span className="text-lg font-bold text-gray-900">{fuelMetrics.currentLevel}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              fuelMetrics.currentLevel > 50
                ? 'bg-green-500'
                : fuelMetrics.currentLevel > 25
                ? 'bg-yellow-500'
                : 'bg-red-500'
            }`}
            style={{ width: `${fuelMetrics.currentLevel}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-1">
          متبقي حوالي {fuelMetrics.estimatedDaysRemaining} أيام • {fuelMetrics.estimatedDaysRemaining} days remaining
        </p>
      </div>

      {/* Consumption Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">استهلاك {timeRange === 'daily' ? 'يومي' : timeRange === 'weekly' ? 'أسبوعي' : 'شهري'}</p>
          <p className="text-2xl font-bold text-blue-600">{consumption.toFixed(1)} L</p>
        </div>
        <div className="bg-green-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">لتر/ساعة</p>
          <p className="text-2xl font-bold text-green-600">
            {fuelMetrics.efficiency.litersPerHour.toFixed(1)}
          </p>
        </div>
      </div>

      {/* Efficiency Trend */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">اتجاه الكفاءة</p>
            <p className="text-xs text-gray-500">Efficiency Trend</p>
          </div>
          <div className={`flex items-center gap-2 ${
            fuelMetrics.efficiency.trend === 'down' ? 'text-green-600' :
            fuelMetrics.efficiency.trend === 'up' ? 'text-red-600' : 'text-gray-600'
          }`}>
            {fuelMetrics.efficiency.trend === 'down' ? (
              <>
                <TrendingDown className="w-5 h-5" />
                <span className="font-bold">{Math.abs(fuelMetrics.efficiency.changePercentage).toFixed(1)}%</span>
              </>
            ) : fuelMetrics.efficiency.trend === 'up' ? (
              <>
                <TrendingUp className="w-5 h-5" />
                <span className="font-bold">+{fuelMetrics.efficiency.changePercentage.toFixed(1)}%</span>
              </>
            ) : (
              <span className="font-bold">مستقر / Stable</span>
            )}
          </div>
        </div>
      </div>

      {/* Total Cost */}
      <div className="border-t border-gray-200 pt-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">إجمالي التكلفة / Total Cost</span>
          <span className="text-xl font-bold text-gray-900">
            {fuelMetrics.totalCost.toLocaleString('ar-YE')} ريال
          </span>
        </div>
      </div>
    </div>
  );
}

interface DowntimeAnalysisProps {
  downtime: DowntimeData;
}

function DowntimeAnalysis({ downtime }: DowntimeAnalysisProps) {
  const maxHours = Math.max(...downtime.reasons.map((r) => r.hours));

  return (
    <div className="space-y-6" data-testid="downtime-analysis">
      {/* Total Downtime */}
      <div className="bg-orange-50 rounded-lg p-4">
        <p className="text-sm text-gray-600 mb-1">إجمالي وقت التوقف</p>
        <p className="text-3xl font-bold text-orange-600">{downtime.totalHours.toFixed(1)}h</p>
      </div>

      {/* Downtime Reasons */}
      <div className="space-y-3">
        <p className="text-sm font-medium text-gray-700">أسباب التوقف / Downtime Reasons</p>
        {downtime.reasons.map((reason, index) => (
          <div key={index} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-gray-900">{reason.reasonAr}</span>
              <span className="text-gray-600">{reason.hours.toFixed(1)}h ({reason.percentage.toFixed(1)}%)</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-orange-500 h-2 rounded-full transition-all"
                style={{ width: `${(reason.hours / maxHours) * 100}%` }}
              />
            </div>
            <p className="text-xs text-gray-500">{reason.reason}</p>
          </div>
        ))}
      </div>

      {/* Last Incident */}
      <div className="border-t border-gray-200 pt-4">
        <p className="text-sm font-medium text-gray-700 mb-2">آخر حادثة / Last Incident</p>
        <div className="bg-gray-50 rounded-lg p-3 space-y-1">
          <p className="text-sm font-medium text-gray-900">{downtime.lastIncident.reasonAr}</p>
          <p className="text-xs text-gray-600">{downtime.lastIncident.reason}</p>
          <div className="flex items-center justify-between text-xs text-gray-500 pt-2">
            <span>{new Date(downtime.lastIncident.date).toLocaleDateString('ar-YE')}</span>
            <span>{downtime.lastIncident.duration.toFixed(1)} ساعة</span>
          </div>
        </div>
      </div>
    </div>
  );
}

interface EquipmentComparisonTableProps {
  data: EquipmentComparisonData[];
  selectedEquipmentId: string;
}

function EquipmentComparisonTable({ data, selectedEquipmentId }: EquipmentComparisonTableProps) {
  const maintenanceStatusColors = {
    good: 'text-green-600',
    warning: 'text-yellow-600',
    critical: 'text-red-600',
  };

  const maintenanceStatusIcons = {
    good: <Check className="w-5 h-5" />,
    warning: <Settings className="w-5 h-5" />,
    critical: <AlertCircle className="w-5 h-5" />,
  };

  return (
    <div className="overflow-x-auto" data-testid="equipment-comparison-table">
      <table className="w-full">
        <thead>
          <tr className="border-b-2 border-gray-200">
            <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">
              المعدة / Equipment
            </th>
            <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">
              ساعات التشغيل / Hours
            </th>
            <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">
              الاستخدام / Utilization
            </th>
            <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">
              كفاءة الوقود / Fuel Eff.
            </th>
            <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">
              التكلفة/ساعة / Cost/Hr
            </th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900">
              الصيانة / Status
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {data.map((equipment) => {
            const isSelected = equipment.equipmentId === selectedEquipmentId;
            return (
              <tr
                key={equipment.equipmentId}
                className={`hover:bg-gray-50 transition-colors ${
                  isSelected ? 'bg-green-50' : ''
                }`}
                data-testid={`comparison-row-${equipment.equipmentId}`}
              >
                <td className="py-3 px-4">
                  <p className={`text-sm font-medium ${isSelected ? 'text-green-700' : 'text-gray-900'}`}>
                    {equipment.nameAr}
                  </p>
                  <p className="text-xs text-gray-500">{equipment.name}</p>
                </td>
                <td className="py-3 px-4">
                  <span className="text-sm text-gray-900">{equipment.operatingHours.toFixed(1)}h</span>
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-900">{equipment.utilization.toFixed(1)}%</span>
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${equipment.utilization}%` }}
                      />
                    </div>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <span className="text-sm text-gray-900">{equipment.fuelEfficiency.toFixed(1)} L/h</span>
                </td>
                <td className="py-3 px-4">
                  <span className="text-sm font-medium text-gray-900">
                    {equipment.costPerHour.toLocaleString('ar-YE')} ريال
                  </span>
                </td>
                <td className="py-3 px-4">
                  <div className={`flex items-center justify-center ${maintenanceStatusColors[equipment.maintenanceStatus]}`}>
                    {maintenanceStatusIcons[equipment.maintenanceStatus]}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* Summary Footer */}
      <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <div>
          <p className="text-xs text-gray-500 mb-1">متوسط الاستخدام</p>
          <p className="text-lg font-bold text-gray-900">
            {(data.reduce((sum, eq) => sum + eq.utilization, 0) / data.length).toFixed(1)}%
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">متوسط الكفاءة</p>
          <p className="text-lg font-bold text-gray-900">
            {(data.reduce((sum, eq) => sum + eq.fuelEfficiency, 0) / data.length).toFixed(1)} L/h
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">متوسط التكلفة</p>
          <p className="text-lg font-bold text-gray-900">
            {Math.round(data.reduce((sum, eq) => sum + eq.costPerHour, 0) / data.length).toLocaleString('ar-YE')} ريال
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">حالة الصيانة الجيدة</p>
          <p className="text-lg font-bold text-green-600">
            {data.filter((eq) => eq.maintenanceStatus === 'good').length}/{data.length}
          </p>
        </div>
      </div>
    </div>
  );
}
