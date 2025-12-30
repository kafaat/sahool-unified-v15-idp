/**
 * Yield Historical Trends Component
 * مكون اتجاهات المحصول التاريخية
 *
 * Advanced multi-year historical yield analysis component with:
 * - 5-10 year historical data visualization
 * - Year-over-year comparison
 * - Trend analysis with moving averages
 * - Seasonal patterns identification
 * - Crop type comparison
 * - Field performance ranking
 * - Climate impact correlation
 */

'use client';

import React, { useState, useMemo } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  ScatterChart,
  Scatter,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Download,
  Filter,
  BarChart3,
  LineChart as LineChartIcon,
  Activity,
  Award,
  Cloud,
  CheckCircle2,
  Info,
  X,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

// ===== Type Definitions =====

export interface YearlyYieldData {
  year: number;
  month?: number;
  season?: string;
  seasonAr?: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  cropTypeAr: string;
  totalYield: number; // kg
  yieldPerHectare: number;
  area: number; // hectares
  quality: number; // 0-100 score
  revenue: number;
  cost: number;
  profit: number;
  weatherConditions: WeatherConditions;
}

export interface WeatherConditions {
  avgTemperature: number; // Celsius
  totalRainfall: number; // mm
  avgHumidity: number; // percentage
  extremeEvents: number; // count of extreme weather events
  favorabilityScore: number; // 0-100 score
}

export interface HistoricalTrendSummary {
  avgYieldPerHectare: number;
  totalYield: number;
  growthRate: number; // percentage
  bestYear: {
    year: number;
    yield: number;
  };
  worstYear: {
    year: number;
    yield: number;
  };
  volatility: number; // standard deviation
  consistency: number; // 0-100 score
}

export interface FieldPerformanceRanking {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  avgYieldPerHectare: number;
  totalYield: number;
  consistency: number;
  trend: 'improving' | 'declining' | 'stable';
  rank: number;
  change: number; // percentage change vs previous period
}

export interface CropComparison {
  cropType: string;
  cropTypeAr: string;
  avgYield: number;
  growthRate: number;
  years: number;
  revenue: number;
}

export interface MovingAverageData {
  year: number;
  actual: number;
  ma3: number; // 3-year moving average
  ma5: number; // 5-year moving average
}

export type ChartView = 'line' | 'area' | 'bar' | 'composed' | 'comparison';
export type TimeGranularity = 'yearly' | 'seasonal' | 'monthly';

interface YieldHistoricalTrendsProps {
  farmId?: string;
  initialYears?: number;
  className?: string;
}

// ===== Mock Data Generator =====

const generateMockHistoricalData = (): YearlyYieldData[] => {
  const currentYear = new Date().getFullYear();
  const fields = [
    { id: 'field-001', name: 'North Field', nameAr: 'الحقل الشمالي' },
    { id: 'field-002', name: 'South Field', nameAr: 'الحقل الجنوبي' },
    { id: 'field-003', name: 'East Field', nameAr: 'الحقل الشرقي' },
    { id: 'field-004', name: 'West Field', nameAr: 'الحقل الغربي' },
  ];

  const crops = [
    { type: 'Wheat', typeAr: 'قمح', baseYield: 4000 },
    { type: 'Corn', typeAr: 'ذرة', baseYield: 8000 },
    { type: 'Barley', typeAr: 'شعير', baseYield: 3500 },
    { type: 'Rice', typeAr: 'أرز', baseYield: 6000 },
  ];

  const seasons = [
    { name: 'Winter', nameAr: 'شتاء', month: 1 },
    { name: 'Spring', nameAr: 'ربيع', month: 4 },
    { name: 'Summer', nameAr: 'صيف', month: 7 },
    { name: 'Fall', nameAr: 'خريف', month: 10 },
  ];

  const data: YearlyYieldData[] = [];

  // Generate 10 years of historical data
  for (let yearOffset = 9; yearOffset >= 0; yearOffset--) {
    const year = currentYear - yearOffset;

    fields.forEach((field, fieldIndex) => {
      seasons.forEach((season, seasonIndex) => {
        const crop = crops[fieldIndex % crops.length] ?? crops[0];
        if (!crop) return;
        const area = 20 + fieldIndex * 5;

        // Add trend (improving over years)
        const trendFactor = 1 + (9 - yearOffset) * 0.03;

        // Add seasonal variation
        const seasonalFactor = 1 + (seasonIndex === 1 ? 0.15 : seasonIndex === 2 ? -0.1 : 0);

        // Add random variation
        const randomFactor = 0.85 + Math.random() * 0.3;

        // Weather impact
        const weatherScore = 60 + Math.random() * 35;
        const weatherFactor = 0.7 + (weatherScore / 100) * 0.6;

        const yieldPerHectare = crop.baseYield * trendFactor * seasonalFactor * randomFactor * weatherFactor;
        const totalYield = yieldPerHectare * area;
        const quality = 70 + Math.random() * 25;
        const pricePerKg = 0.5 + Math.random() * 0.3;
        const revenue = totalYield * pricePerKg;
        const cost = totalYield * (0.3 + Math.random() * 0.15);

        data.push({
          year,
          month: season.month,
          season: season.name,
          seasonAr: season.nameAr,
          fieldId: field.id,
          fieldName: field.name,
          fieldNameAr: field.nameAr,
          cropType: crop.type,
          cropTypeAr: crop.typeAr,
          totalYield: Math.round(totalYield),
          yieldPerHectare: Math.round(yieldPerHectare),
          area,
          quality: Math.round(quality),
          revenue: Math.round(revenue),
          cost: Math.round(cost),
          profit: Math.round(revenue - cost),
          weatherConditions: {
            avgTemperature: 20 + Math.random() * 15,
            totalRainfall: 50 + Math.random() * 200,
            avgHumidity: 40 + Math.random() * 40,
            extremeEvents: Math.floor(Math.random() * 4),
            favorabilityScore: Math.round(weatherScore),
          },
        });
      });
    });
  }

  return data;
};

// ===== Main Component =====

export const YieldHistoricalTrends: React.FC<YieldHistoricalTrendsProps> = ({
  farmId: _farmId,
  initialYears: _initialYears = 10,
  className = '',
}) => {
  void _farmId;
  void _initialYears;
  // State management
  const [chartView, setChartView] = useState<ChartView>('line');
  const [timeGranularity, setTimeGranularity] = useState<TimeGranularity>('yearly');
  const [selectedYears, setSelectedYears] = useState<number[]>([]);
  const [selectedFields, setSelectedFields] = useState<string[]>([]);
  const [selectedCrops, setSelectedCrops] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [isLoading, _setIsLoading] = useState(false);
  void _setIsLoading;
  const [showMovingAverage, setShowMovingAverage] = useState(true);
  const [showWeatherCorrelation, setShowWeatherCorrelation] = useState(false);

  // Mock data
  const historicalData = useMemo(() => generateMockHistoricalData(), []);

  // Filtered data
  const filteredData = useMemo(() => {
    let data = historicalData;

    if (selectedYears.length > 0) {
      data = data.filter((d) => selectedYears.includes(d.year));
    }

    if (selectedFields.length > 0) {
      data = data.filter((d) => selectedFields.includes(d.fieldId));
    }

    if (selectedCrops.length > 0) {
      data = data.filter((d) => selectedCrops.includes(d.cropType));
    }

    return data;
  }, [historicalData, selectedYears, selectedFields, selectedCrops]);

  // Get unique values for filters
  const availableYears = useMemo(
    () => Array.from(new Set(historicalData.map((d) => d.year))).sort((a, b) => b - a),
    [historicalData]
  );

  const availableFields = useMemo(
    () =>
      Array.from(
        new Map(
          historicalData.map((d) => [d.fieldId, { id: d.fieldId, name: d.fieldName, nameAr: d.fieldNameAr }])
        ).values()
      ),
    [historicalData]
  );

  const availableCrops = useMemo(
    () =>
      Array.from(
        new Set(historicalData.map((d) => JSON.stringify({ type: d.cropType, typeAr: d.cropTypeAr })))
      ).map((s) => JSON.parse(s)),
    [historicalData]
  );

  // Aggregate data by year
  const yearlyAggregatedData = useMemo(() => {
    const grouped = filteredData.reduce((acc, item) => {
      const key = timeGranularity === 'yearly' ? item.year : `${item.year}-${item.season}`;

      if (!acc[key]) {
        acc[key] = {
          year: item.year,
          season: item.season,
          seasonAr: item.seasonAr,
          totalYield: 0,
          totalArea: 0,
          totalRevenue: 0,
          totalCost: 0,
          weatherScore: 0,
          count: 0,
        };
      }

      acc[key].totalYield += item.totalYield;
      acc[key].totalArea += item.area;
      acc[key].totalRevenue += item.revenue;
      acc[key].totalCost += item.cost;
      acc[key].weatherScore += item.weatherConditions.favorabilityScore;
      acc[key].count += 1;

      return acc;
    }, {} as Record<string, any>);

    return Object.values(grouped)
      .map((g: any) => ({
        label: timeGranularity === 'yearly' ? `${g.year}` : `${g.seasonAr} ${g.year}`,
        year: g.year,
        season: g.season,
        yieldPerHectare: Math.round(g.totalYield / g.totalArea),
        totalYield: Math.round(g.totalYield),
        revenue: Math.round(g.totalRevenue),
        profit: Math.round(g.totalRevenue - g.totalCost),
        weatherScore: Math.round(g.weatherScore / g.count),
      }))
      .sort((a, b) => {
        if (a.year !== b.year) return a.year - b.year;
        return (a.season || '').localeCompare(b.season || '');
      });
  }, [filteredData, timeGranularity]);

  // Calculate moving averages
  const movingAverageData = useMemo(() => {
    if (timeGranularity !== 'yearly') return [];

    const yearlyData = yearlyAggregatedData.filter((d) => !d.season);

    return yearlyData.map((item, index, arr) => {
      const current = arr[index]?.yieldPerHectare ?? 0;
      const prev1 = arr[index - 1]?.yieldPerHectare ?? 0;
      const prev2 = arr[index - 2]?.yieldPerHectare ?? 0;
      const prev3 = arr[index - 3]?.yieldPerHectare ?? 0;
      const prev4 = arr[index - 4]?.yieldPerHectare ?? 0;

      const ma3 =
        index >= 2
          ? Math.round((current + prev1 + prev2) / 3)
          : null;

      const ma5 =
        index >= 4
          ? Math.round((current + prev1 + prev2 + prev3 + prev4) / 5)
          : null;

      return {
        label: item.label,
        year: item.year,
        actual: item.yieldPerHectare,
        ma3,
        ma5,
      };
    });
  }, [yearlyAggregatedData, timeGranularity]);

  // Field performance ranking
  const fieldRankings = useMemo(() => {
    const fieldStats = filteredData.reduce((acc, item) => {
      if (!acc[item.fieldId]) {
        acc[item.fieldId] = {
          fieldId: item.fieldId,
          fieldName: item.fieldName,
          fieldNameAr: item.fieldNameAr,
          yields: [],
          totalYield: 0,
        };
      }

      acc[item.fieldId].yields.push(item.yieldPerHectare);
      acc[item.fieldId].totalYield += item.totalYield;

      return acc;
    }, {} as Record<string, any>);

    const rankings: FieldPerformanceRanking[] = Object.values(fieldStats).map((field: any) => {
      const avgYield = field.yields.reduce((sum: number, y: number) => sum + y, 0) / field.yields.length;
      const variance = field.yields.reduce((sum: number, y: number) => sum + Math.pow(y - avgYield, 2), 0) / field.yields.length;
      const consistency = Math.max(0, 100 - (Math.sqrt(variance) / avgYield) * 100);

      // Calculate trend
      const firstHalf = field.yields.slice(0, Math.floor(field.yields.length / 2));
      const secondHalf = field.yields.slice(Math.floor(field.yields.length / 2));
      const avgFirstHalf = firstHalf.reduce((sum: number, y: number) => sum + y, 0) / firstHalf.length;
      const avgSecondHalf = secondHalf.reduce((sum: number, y: number) => sum + y, 0) / secondHalf.length;
      const change = ((avgSecondHalf - avgFirstHalf) / avgFirstHalf) * 100;
      const trend = change > 5 ? 'improving' : change < -5 ? 'declining' : 'stable';

      return {
        fieldId: field.fieldId,
        fieldName: field.fieldName,
        fieldNameAr: field.fieldNameAr,
        avgYieldPerHectare: Math.round(avgYield),
        totalYield: Math.round(field.totalYield),
        consistency: Math.round(consistency),
        trend,
        rank: 0,
        change: Math.round(change * 10) / 10,
      };
    });

    // Assign ranks
    rankings.sort((a, b) => b.avgYieldPerHectare - a.avgYieldPerHectare);
    rankings.forEach((r, index) => {
      r.rank = index + 1;
    });

    return rankings;
  }, [filteredData]);

  // Crop comparison
  const cropComparison = useMemo(() => {
    const cropStats = filteredData.reduce((acc, item) => {
      if (!acc[item.cropType]) {
        acc[item.cropType] = {
          cropType: item.cropType,
          cropTypeAr: item.cropTypeAr,
          yields: [],
          years: new Set<number>(),
          revenue: 0,
        };
      }

      acc[item.cropType].yields.push(item.yieldPerHectare);
      acc[item.cropType].years.add(item.year);
      acc[item.cropType].revenue += item.revenue;

      return acc;
    }, {} as Record<string, any>);

    const comparisons: CropComparison[] = Object.values(cropStats).map((crop: any) => {
      const avgYield = crop.yields.reduce((sum: number, y: number) => sum + y, 0) / crop.yields.length;

      // Calculate growth rate (compare first year to last year)
      const yearlyAvgs: Record<number, number[]> = {};
      filteredData
        .filter((d) => d.cropType === crop.cropType)
        .forEach((d) => {
          if (!yearlyAvgs[d.year]) yearlyAvgs[d.year] = [];
          yearlyAvgs[d.year]?.push(d.yieldPerHectare);
        });

      const years = Object.keys(yearlyAvgs).map(Number).sort();
      const firstYear = years[0];
      const lastYear = years[years.length - 1];
      const firstYearData = firstYear !== undefined ? yearlyAvgs[firstYear] ?? [] : [];
      const lastYearData = lastYear !== undefined ? yearlyAvgs[lastYear] ?? [] : [];
      const firstYearAvg = firstYearData.length > 0
        ? firstYearData.reduce((sum, y) => sum + y, 0) / firstYearData.length
        : 0;
      const lastYearAvg = lastYearData.length > 0
        ? lastYearData.reduce((sum, y) => sum + y, 0) / lastYearData.length
        : 0;
      const growthRate = firstYearAvg > 0 ? ((lastYearAvg - firstYearAvg) / firstYearAvg) * 100 : 0;

      return {
        cropType: crop.cropType,
        cropTypeAr: crop.cropTypeAr,
        avgYield: Math.round(avgYield),
        growthRate: Math.round(growthRate * 10) / 10,
        years: crop.years.size,
        revenue: Math.round(crop.revenue),
      };
    });

    return comparisons.sort((a, b) => b.avgYield - a.avgYield);
  }, [filteredData]);

  // Historical summary
  const summary: HistoricalTrendSummary = useMemo(() => {
    const yearlyYields = yearlyAggregatedData.filter((d) => !d.season).map((d) => d.yieldPerHectare);
    const avgYield = yearlyYields.reduce((sum, y) => sum + y, 0) / yearlyYields.length;
    const variance = yearlyYields.reduce((sum, y) => sum + Math.pow(y - avgYield, 2), 0) / yearlyYields.length;
    const volatility = Math.sqrt(variance);

    const defaultData = yearlyAggregatedData[0] ?? { year: 0, yieldPerHectare: 0, totalYield: 0 };
    const bestYearData = yearlyAggregatedData.reduce(
      (max, d) => (!d.season && max && d.yieldPerHectare > max.yieldPerHectare ? d : max),
      defaultData
    );

    const worstYearData = yearlyAggregatedData.reduce(
      (min, d) => (!d.season && min && d.yieldPerHectare < min.yieldPerHectare ? d : min),
      defaultData
    );

    const firstYearYield = yearlyYields[0] ?? 0;
    const lastYearYield = yearlyYields[yearlyYields.length - 1] ?? 0;
    const growthRate = firstYearYield > 0 ? ((lastYearYield - firstYearYield) / firstYearYield) * 100 : 0;

    return {
      avgYieldPerHectare: Math.round(avgYield),
      totalYield: Math.round(yearlyAggregatedData.reduce((sum, d) => sum + d.totalYield, 0)),
      growthRate: Math.round(growthRate * 10) / 10,
      bestYear: {
        year: bestYearData.year,
        yield: bestYearData.yieldPerHectare,
      },
      worstYear: {
        year: worstYearData.year,
        yield: worstYearData.yieldPerHectare,
      },
      volatility: Math.round(volatility),
      consistency: Math.max(0, Math.round(100 - (volatility / avgYield) * 100)),
    };
  }, [yearlyAggregatedData]);

  // Export handlers
  const handleExportCSV = () => {
    const headers = ['السنة,Year,المحصول (كجم/هكتار),Yield (kg/ha),الإيرادات,Revenue,الأرباح,Profit'];
    const rows = yearlyAggregatedData.map(
      (d) => `${d.year},${d.year},${d.yieldPerHectare},${d.yieldPerHectare},${d.revenue},${d.revenue},${d.profit},${d.profit}`
    );
    const csv = [headers, ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `yield-historical-trends-${Date.now()}.csv`;
    link.click();
  };

  const handleExportPDF = () => {
    // In a real implementation, this would generate a PDF
    alert('تصدير PDF سيتم قريباً / PDF export coming soon');
  };

  // Empty state
  if (filteredData.length === 0) {
    return (
      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 text-center" data-testid="yield-trends-empty">
        <Info className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 text-lg font-semibold">لا توجد بيانات تاريخية</p>
        <p className="text-sm text-gray-500 mt-1">No historical data available</p>
        <p className="text-sm text-gray-500 mt-2">الرجاء ضبط الفلاتر للعرض البيانات</p>
        <p className="text-xs text-gray-400 mt-1">Please adjust filters to view data</p>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="bg-white p-12 rounded-xl shadow-sm border border-gray-200" data-testid="yield-trends-loading">
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
          <p className="text-gray-600 font-semibold">جاري تحميل البيانات التاريخية...</p>
          <p className="text-sm text-gray-500">Loading historical data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`} data-testid="yield-historical-trends">
      {/* Header with Actions */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900" data-testid="trends-title">
              اتجاهات المحصول التاريخية
            </h2>
            <p className="text-sm text-gray-600 mt-1">Historical Yield Trends Analysis</p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Time Granularity */}
            <div className="flex gap-2" data-testid="time-granularity-selector">
              <button
                onClick={() => setTimeGranularity('yearly')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  timeGranularity === 'yearly'
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
                data-testid="granularity-yearly"
              >
                سنوي
              </button>
              <button
                onClick={() => setTimeGranularity('seasonal')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  timeGranularity === 'seasonal'
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
                data-testid="granularity-seasonal"
              >
                موسمي
              </button>
            </div>

            {/* Filter Toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
              data-testid="toggle-filters"
            >
              <Filter className="w-4 h-4" />
              <span className="text-sm font-medium">فلاتر</span>
              {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {/* Export Buttons */}
            <div className="flex gap-2">
              <button
                onClick={handleExportCSV}
                className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
                data-testid="export-csv"
              >
                <Download className="w-4 h-4" />
                <span className="text-sm font-medium">CSV</span>
              </button>
              <button
                onClick={handleExportPDF}
                className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                data-testid="export-pdf"
              >
                <Download className="w-4 h-4" />
                <span className="text-sm font-medium">PDF</span>
              </button>
            </div>
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mt-6 pt-6 border-t border-gray-200" data-testid="filters-panel">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Year Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  السنوات / Years
                </label>
                <div className="space-y-2 max-h-40 overflow-y-auto p-2 border border-gray-200 rounded-lg" data-testid="year-filter">
                  {availableYears.map((year) => (
                    <label key={year} className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
                      <input
                        type="checkbox"
                        checked={selectedYears.includes(year)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedYears([...selectedYears, year]);
                          } else {
                            setSelectedYears(selectedYears.filter((y) => y !== year));
                          }
                        }}
                        className="rounded border-gray-300 text-green-500 focus:ring-green-500"
                      />
                      <span className="text-sm text-gray-700">{year}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Field Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  الحقول / Fields
                </label>
                <div className="space-y-2 max-h-40 overflow-y-auto p-2 border border-gray-200 rounded-lg" data-testid="field-filter">
                  {availableFields.map((field) => (
                    <label key={field.id} className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
                      <input
                        type="checkbox"
                        checked={selectedFields.includes(field.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedFields([...selectedFields, field.id]);
                          } else {
                            setSelectedFields(selectedFields.filter((f) => f !== field.id));
                          }
                        }}
                        className="rounded border-gray-300 text-green-500 focus:ring-green-500"
                      />
                      <span className="text-sm text-gray-700">{field.nameAr}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Crop Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  المحاصيل / Crops
                </label>
                <div className="space-y-2 max-h-40 overflow-y-auto p-2 border border-gray-200 rounded-lg" data-testid="crop-filter">
                  {availableCrops.map((crop) => (
                    <label key={crop.type} className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
                      <input
                        type="checkbox"
                        checked={selectedCrops.includes(crop.type)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedCrops([...selectedCrops, crop.type]);
                          } else {
                            setSelectedCrops(selectedCrops.filter((c) => c !== crop.type));
                          }
                        }}
                        className="rounded border-gray-300 text-green-500 focus:ring-green-500"
                      />
                      <span className="text-sm text-gray-700">{crop.typeAr}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {/* Clear Filters */}
            {(selectedYears.length > 0 || selectedFields.length > 0 || selectedCrops.length > 0) && (
              <button
                onClick={() => {
                  setSelectedYears([]);
                  setSelectedFields([]);
                  setSelectedCrops([]);
                }}
                className="mt-4 flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                data-testid="clear-filters"
              >
                <X className="w-4 h-4" />
                <span>مسح جميع الفلاتر / Clear All Filters</span>
              </button>
            )}
          </div>
        )}
      </div>

      {/* Summary KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" data-testid="summary-kpis">
        <div className="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-xl text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">متوسط الإنتاجية</p>
              <p className="text-xs opacity-75 mt-0.5">Avg Yield/Hectare</p>
            </div>
            <TrendingUp className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-3xl font-bold mt-3">{summary.avgYieldPerHectare.toLocaleString('ar-SA')}</p>
          <p className="text-sm opacity-90 mt-1">كجم/هكتار</p>
          <div className="flex items-center gap-2 mt-2">
            <div className={`flex items-center gap-1 text-xs px-2 py-1 rounded ${
              summary.growthRate >= 0 ? 'bg-green-700' : 'bg-red-500'
            }`}>
              {summary.growthRate >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              <span>{Math.abs(summary.growthRate)}%</span>
            </div>
            <span className="text-xs opacity-75">معدل النمو</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-xl text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">أفضل سنة</p>
              <p className="text-xs opacity-75 mt-0.5">Best Year</p>
            </div>
            <Award className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-3xl font-bold mt-3">{summary.bestYear.year}</p>
          <p className="text-sm opacity-90 mt-1">{summary.bestYear.yield.toLocaleString('ar-SA')} كجم/هكتار</p>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 p-6 rounded-xl text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">الاستقرار</p>
              <p className="text-xs opacity-75 mt-0.5">Consistency</p>
            </div>
            <Activity className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-3xl font-bold mt-3">{summary.consistency}%</p>
          <p className="text-sm opacity-90 mt-1">التذبذب: {summary.volatility.toLocaleString('ar-SA')}</p>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-6 rounded-xl text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">إجمالي الإنتاج</p>
              <p className="text-xs opacity-75 mt-0.5">Total Production</p>
            </div>
            <BarChart3 className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-3xl font-bold mt-3">{(summary.totalYield / 1000).toFixed(1)}</p>
          <p className="text-sm opacity-90 mt-1">طن (جميع السنوات)</p>
        </div>
      </div>

      {/* Chart Type Selector */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            التحليل البياني / Chart Analysis
          </h3>
          <div className="flex gap-2" data-testid="chart-type-selector">
            <button
              onClick={() => setChartView('line')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                chartView === 'line' ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              data-testid="chart-type-line"
            >
              <LineChartIcon className="w-4 h-4" />
            </button>
            <button
              onClick={() => setChartView('area')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                chartView === 'area' ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              data-testid="chart-type-area"
            >
              خطوط منطقة
            </button>
            <button
              onClick={() => setChartView('bar')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                chartView === 'bar' ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              data-testid="chart-type-bar"
            >
              <BarChart3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setChartView('composed')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                chartView === 'composed' ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              data-testid="chart-type-composed"
            >
              مركب
            </button>
          </div>
        </div>

        {/* Chart Options */}
        <div className="flex flex-wrap gap-4 mt-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showMovingAverage}
              onChange={(e) => setShowMovingAverage(e.target.checked)}
              className="rounded border-gray-300 text-green-500 focus:ring-green-500"
              data-testid="toggle-moving-average"
            />
            <span className="text-sm text-gray-700">عرض المتوسط المتحرك / Show Moving Average</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showWeatherCorrelation}
              onChange={(e) => setShowWeatherCorrelation(e.target.checked)}
              className="rounded border-gray-300 text-green-500 focus:ring-green-500"
              data-testid="toggle-weather-correlation"
            />
            <span className="text-sm text-gray-700">ارتباط الطقس / Weather Correlation</span>
          </label>
        </div>

        {/* Main Chart */}
        <div className="mt-6" style={{ height: '500px' }} data-testid="main-chart">
          <ResponsiveContainer width="100%" height="100%">
            {chartView === 'line' && (
              <LineChart data={showMovingAverage && timeGranularity === 'yearly' ? movingAverageData : yearlyAggregatedData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="label"
                  tick={{ fontSize: 12, fill: '#6b7280' }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} label={{ value: 'كجم/هكتار', angle: -90, position: 'insideLeft' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '8px 12px',
                  }}
                />
                <Legend />
                {showMovingAverage && timeGranularity === 'yearly' ? (
                  <>
                    <Line type="monotone" dataKey="actual" stroke="#10b981" strokeWidth={2} name="الإنتاجية الفعلية" dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="ma3" stroke="#3b82f6" strokeWidth={2} strokeDasharray="5 5" name="المتوسط المتحرك 3 سنوات" />
                    <Line type="monotone" dataKey="ma5" stroke="#8b5cf6" strokeWidth={2} strokeDasharray="5 5" name="المتوسط المتحرك 5 سنوات" />
                  </>
                ) : (
                  <Line type="monotone" dataKey="yieldPerHectare" stroke="#10b981" strokeWidth={3} name="الإنتاجية" dot={{ r: 5 }} activeDot={{ r: 8 }} />
                )}
              </LineChart>
            )}

            {chartView === 'area' && (
              <AreaChart data={yearlyAggregatedData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="label" tick={{ fontSize: 12, fill: '#6b7280' }} angle={-45} textAnchor="end" height={80} />
                <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} />
                <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }} />
                <Legend />
                <Area type="monotone" dataKey="yieldPerHectare" stroke="#10b981" fill="#10b981" fillOpacity={0.3} name="الإنتاجية" />
              </AreaChart>
            )}

            {chartView === 'bar' && (
              <BarChart data={yearlyAggregatedData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="label" tick={{ fontSize: 12, fill: '#6b7280' }} angle={-45} textAnchor="end" height={80} />
                <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} />
                <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }} />
                <Legend />
                <Bar dataKey="yieldPerHectare" fill="#10b981" name="الإنتاجية" radius={[8, 8, 0, 0]} />
              </BarChart>
            )}

            {chartView === 'composed' && (
              <ComposedChart data={yearlyAggregatedData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="label" tick={{ fontSize: 12, fill: '#6b7280' }} angle={-45} textAnchor="end" height={80} />
                <YAxis yAxisId="left" tick={{ fontSize: 12, fill: '#6b7280' }} label={{ value: 'كجم/هكتار', angle: -90, position: 'insideLeft' }} />
                <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12, fill: '#6b7280' }} label={{ value: 'ريال', angle: 90, position: 'insideRight' }} />
                <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }} />
                <Legend />
                <Bar yAxisId="left" dataKey="yieldPerHectare" fill="#10b981" name="الإنتاجية" radius={[8, 8, 0, 0]} />
                <Line yAxisId="right" type="monotone" dataKey="profit" stroke="#3b82f6" strokeWidth={2} name="الأرباح" dot={{ r: 4 }} />
              </ComposedChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>

      {/* Weather Correlation Chart */}
      {showWeatherCorrelation && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200" data-testid="weather-correlation">
          <div className="flex items-center gap-3 mb-4">
            <Cloud className="w-6 h-6 text-blue-500" />
            <h3 className="text-lg font-semibold text-gray-900">
              ارتباط الطقس بالإنتاجية / Weather-Yield Correlation
            </h3>
          </div>
          <div style={{ height: '400px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" dataKey="weatherScore" name="نقاط الطقس" tick={{ fontSize: 12 }} label={{ value: 'Weather Score', position: 'bottom' }} />
                <YAxis type="number" dataKey="yieldPerHectare" name="الإنتاجية" tick={{ fontSize: 12 }} label={{ value: 'Yield (kg/ha)', angle: -90, position: 'insideLeft' }} />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }} />
                <Legend />
                <Scatter name="الإنتاجية مقابل الطقس" data={yearlyAggregatedData} fill="#10b981" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-900">
              <Info className="w-4 h-4 inline mr-2" />
              تظهر هذه الرسمة العلاقة بين ظروف الطقس والإنتاجية. نقاط أعلى تشير إلى ارتباط إيجابي قوي.
            </p>
            <p className="text-xs text-blue-700 mt-1">
              This chart shows the relationship between weather conditions and yield. Higher scores indicate a strong positive correlation.
            </p>
          </div>
        </div>
      )}

      {/* Crop Comparison */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200" data-testid="crop-comparison">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          مقارنة المحاصيل / Crop Comparison
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {cropComparison.map((crop) => (
            <div key={crop.cropType} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-gray-900">{crop.cropTypeAr}</h4>
                {crop.growthRate >= 0 ? (
                  <TrendingUp className="w-5 h-5 text-green-500" />
                ) : (
                  <TrendingDown className="w-5 h-5 text-red-500" />
                )}
              </div>
              <div className="space-y-2">
                <div>
                  <p className="text-xs text-gray-600">متوسط الإنتاجية</p>
                  <p className="text-xl font-bold text-gray-900">{crop.avgYield.toLocaleString('ar-SA')}</p>
                  <p className="text-xs text-gray-500">كجم/هكتار</p>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                  <span className="text-xs text-gray-600">معدل النمو</span>
                  <span className={`text-sm font-semibold ${crop.growthRate >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {crop.growthRate >= 0 ? '+' : ''}{crop.growthRate}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-600">عدد السنوات</span>
                  <span className="text-sm font-semibold text-gray-700">{crop.years}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Field Performance Rankings */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200" data-testid="field-rankings">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          تصنيف أداء الحقول / Field Performance Rankings
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase">الترتيب</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase">الحقل</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase">متوسط الإنتاجية</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase">الاستقرار</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase">الاتجاه</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase">التغيير</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {fieldRankings.map((field) => (
                <tr key={field.fieldId} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {field.rank === 1 && <Award className="w-5 h-5 text-yellow-500" />}
                      <span className="font-semibold text-gray-900">#{field.rank}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-900">{field.fieldNameAr}</p>
                    <p className="text-xs text-gray-500">{field.fieldName}</p>
                  </td>
                  <td className="px-4 py-3">
                    <p className="font-semibold text-gray-900">{field.avgYieldPerHectare.toLocaleString('ar-SA')}</p>
                    <p className="text-xs text-gray-500">كجم/هكتار</p>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-full bg-gray-200 rounded-full h-2 max-w-[100px]">
                        <div
                          className="bg-green-500 h-2 rounded-full transition-all"
                          style={{ width: `${field.consistency}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-700">{field.consistency}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {field.trend === 'improving' && (
                        <>
                          <TrendingUp className="w-4 h-4 text-green-500" />
                          <span className="text-sm text-green-700">تحسن</span>
                        </>
                      )}
                      {field.trend === 'declining' && (
                        <>
                          <TrendingDown className="w-4 h-4 text-red-500" />
                          <span className="text-sm text-red-700">تراجع</span>
                        </>
                      )}
                      {field.trend === 'stable' && (
                        <>
                          <Activity className="w-4 h-4 text-gray-500" />
                          <span className="text-sm text-gray-700">مستقر</span>
                        </>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-sm font-semibold ${
                      field.change >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {field.change >= 0 ? '+' : ''}{field.change}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Insights and Recommendations */}
      <div className="bg-gradient-to-br from-green-50 to-blue-50 p-6 rounded-xl border border-green-200" data-testid="insights">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              رؤى وتوصيات / Insights & Recommendations
            </h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">•</span>
                <span>
                  <strong>معدل النمو الإجمالي:</strong> {summary.growthRate >= 0 ? 'إيجابي' : 'سلبي'} بنسبة {Math.abs(summary.growthRate)}% خلال السنوات {availableYears.length}
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">•</span>
                <span>
                  <strong>أفضل أداء:</strong> حقل {fieldRankings[0]?.fieldNameAr} بمتوسط {fieldRankings[0]?.avgYieldPerHectare.toLocaleString('ar-SA')} كجم/هكتار
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">•</span>
                <span>
                  <strong>محصول موصى به:</strong> {cropComparison[0]?.cropTypeAr} أظهر أعلى إنتاجية متوسطة
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">•</span>
                <span>
                  <strong>استقرار الإنتاج:</strong> {summary.consistency}% - {summary.consistency >= 75 ? 'ممتاز' : summary.consistency >= 50 ? 'جيد' : 'يحتاج تحسين'}
                </span>
              </li>
              {showWeatherCorrelation && (
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 font-bold">•</span>
                  <span>
                    <strong>تأثير الطقس:</strong> ظروف الطقس المواتية تحسن الإنتاجية بشكل ملحوظ - استخدم توقعات الطقس للتخطيط الأمثل
                  </span>
                </li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default YieldHistoricalTrends;
