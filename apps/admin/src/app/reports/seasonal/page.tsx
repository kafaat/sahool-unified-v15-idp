// Sahool Admin Dashboard - Seasonal Report Generator
// تقرير موسمي شامل بنقرة واحدة

"use client";

import { useState, useEffect } from "react";
import { apiClient, API_URLS } from "@/lib/api";
import { logger } from "@/lib/logger";
import {
  FileText,
  Download,
  Calendar,
  TrendingUp,
  Droplets,
  Bug,
  Loader2,
  Sprout,
  MapPin,
  DollarSign,
  BarChart3,
  CheckCircle2,
  Thermometer,
  Target,
  Printer,
} from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────────────────

interface SeasonSummary {
  season_id: string;
  season_name_ar: string;
  year: number;
  start_date: string;
  end_date: string;
  status: "active" | "completed" | "planned";
  total_farms: number;
  total_fields: number;
  total_area_hectares: number;
}

interface YieldSummary {
  crop_type: string;
  crop_name_ar: string;
  total_area_hectares: number;
  avg_yield_ton_per_ha: number;
  total_yield_tons: number;
  target_yield_ton_per_ha: number;
  achievement_percent: number;
  comparison_last_season: number; // positive = improvement
}

interface IrrigationSummary {
  total_water_m3: number;
  avg_efficiency_percent: number;
  irrigation_events: number;
  water_saved_m3: number;
  water_saved_percent: number;
  cost_yer: number;
}

interface DiseaseSummary {
  total_diagnoses: number;
  diseases_detected: number;
  pests_detected: number;
  treatments_applied: number;
  resolved_percent: number;
  top_diseases: Array<{
    name_ar: string;
    count: number;
    severity: string;
  }>;
}

interface FinancialSummary {
  total_revenue_yer: number;
  total_cost_yer: number;
  net_profit_yer: number;
  profit_margin_percent: number;
  cost_breakdown: Array<{
    category_ar: string;
    amount_yer: number;
    percent: number;
  }>;
}

interface WeatherSummary {
  avg_temperature: number;
  total_rainfall_mm: number;
  frost_events: number;
  heat_stress_days: number;
  gdd_total: number;
}

interface TaskSummary {
  total_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  completion_rate_percent: number;
}

interface SeasonalReport {
  season: SeasonSummary;
  yields: YieldSummary[];
  irrigation: IrrigationSummary;
  diseases: DiseaseSummary;
  financial: FinancialSummary;
  weather: WeatherSummary;
  tasks: TaskSummary;
  generated_at: string;
}

// ─── Mock Data ───────────────────────────────────────────────────────────────

const MOCK_REPORT: SeasonalReport = {
  season: {
    season_id: "season-2025-winter",
    season_name_ar: "الموسم الشتوي 2025/2026",
    year: 2025,
    start_date: "2025-10-01",
    end_date: "2026-03-31",
    status: "active",
    total_farms: 12,
    total_fields: 47,
    total_area_hectares: 324.5,
  },
  yields: [
    { crop_type: "wheat", crop_name_ar: "قمح", total_area_hectares: 120, avg_yield_ton_per_ha: 3.2, total_yield_tons: 384, target_yield_ton_per_ha: 3.5, achievement_percent: 91, comparison_last_season: 8 },
    { crop_type: "barley", crop_name_ar: "شعير", total_area_hectares: 85, avg_yield_ton_per_ha: 2.8, total_yield_tons: 238, target_yield_ton_per_ha: 3.0, achievement_percent: 93, comparison_last_season: 12 },
    { crop_type: "tomato", crop_name_ar: "طماطم", total_area_hectares: 35, avg_yield_ton_per_ha: 25.0, total_yield_tons: 875, target_yield_ton_per_ha: 28.0, achievement_percent: 89, comparison_last_season: 5 },
    { crop_type: "potato", crop_name_ar: "بطاطس", total_area_hectares: 45, avg_yield_ton_per_ha: 18.5, total_yield_tons: 832.5, target_yield_ton_per_ha: 20.0, achievement_percent: 92, comparison_last_season: -3 },
    { crop_type: "coffee", crop_name_ar: "بن يمني", total_area_hectares: 39.5, avg_yield_ton_per_ha: 0.8, total_yield_tons: 31.6, target_yield_ton_per_ha: 0.9, achievement_percent: 88, comparison_last_season: 15 },
  ],
  irrigation: {
    total_water_m3: 486000,
    avg_efficiency_percent: 78,
    irrigation_events: 892,
    water_saved_m3: 54000,
    water_saved_percent: 10,
    cost_yer: 2450000,
  },
  diseases: {
    total_diagnoses: 156,
    diseases_detected: 23,
    pests_detected: 12,
    treatments_applied: 89,
    resolved_percent: 82,
    top_diseases: [
      { name_ar: "صدأ الأوراق - القمح", count: 18, severity: "moderate" },
      { name_ar: "البياض الدقيقي - الطماطم", count: 14, severity: "high" },
      { name_ar: "المن الأخضر", count: 11, severity: "low" },
      { name_ar: "لفحة متأخرة - بطاطس", count: 9, severity: "high" },
      { name_ar: "سوسة النخيل الحمراء", count: 5, severity: "critical" },
    ],
  },
  financial: {
    total_revenue_yer: 185000000,
    total_cost_yer: 124000000,
    net_profit_yer: 61000000,
    profit_margin_percent: 33,
    cost_breakdown: [
      { category_ar: "مدخلات زراعية (بذور + أسمدة)", amount_yer: 42000000, percent: 34 },
      { category_ar: "عمالة ومعدات", amount_yer: 35000000, percent: 28 },
      { category_ar: "ري ومياه", amount_yer: 24500000, percent: 20 },
      { category_ar: "مبيدات ومكافحة", amount_yer: 15000000, percent: 12 },
      { category_ar: "نقل وتسويق", amount_yer: 7500000, percent: 6 },
    ],
  },
  weather: {
    avg_temperature: 18,
    total_rainfall_mm: 285,
    frost_events: 3,
    heat_stress_days: 0,
    gdd_total: 1850,
  },
  tasks: {
    total_tasks: 342,
    completed_tasks: 298,
    overdue_tasks: 12,
    completion_rate_percent: 87,
  },
  generated_at: new Date().toISOString(),
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatNumber(n: number): string {
  return n.toLocaleString("ar-YE");
}

function formatMoney(n: number): string {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)} مليون ر.ي`;
  if (n >= 1000) return `${(n / 1000).toFixed(0)} ألف ر.ي`;
  return `${n} ر.ي`;
}

function getSeverityBadge(severity: string) {
  const colors: Record<string, string> = {
    critical: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300",
    high: "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300",
    moderate: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300",
    low: "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300",
  };
  const labels: Record<string, string> = {
    critical: "حرج",
    high: "مرتفع",
    moderate: "متوسط",
    low: "منخفض",
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[severity] || colors.low}`}>
      {labels[severity] || severity}
    </span>
  );
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function SeasonalReportPage() {
  const [report, setReport] = useState<SeasonalReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [selectedSeason, setSelectedSeason] = useState("2025-winter");

  const SEASONS = [
    { id: "2025-winter", label: "الموسم الشتوي 2025/2026" },
    { id: "2025-summer", label: "الموسم الصيفي 2025" },
    { id: "2024-winter", label: "الموسم الشتوي 2024/2025" },
  ];

  useEffect(() => {
    loadReport();
  }, [selectedSeason]);

  const loadReport = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.get(
        `${API_URLS.indicators}/api/v1/reports/seasonal`,
        { params: { season_id: selectedSeason } },
      );
      setReport(response.data);
    } catch (err) {
      logger.warn("Report API unavailable, using demo data", err);
      setReport(MOCK_REPORT);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (format: "pdf" | "csv") => {
    setIsExporting(true);
    try {
      // In production, this would call the report generation API
      await new Promise((resolve) => setTimeout(resolve, 1500));
      logger.info(`Seasonal report exported as ${format}`);
      // Placeholder for actual download
    } catch (err) {
      logger.error("Export failed", err);
    } finally {
      setIsExporting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-sahool-600" />
        <span className="mr-3 text-gray-500 dark:text-gray-400">جاري إعداد التقرير الموسمي...</span>
      </div>
    );
  }

  if (!report) return null;

  const { season, yields, irrigation, diseases, financial, weather, tasks } = report;

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <FileText className="w-7 h-7 text-sahool-600" />
            التقرير الموسمي الشامل
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            ملخص شامل لأداء الموسم — الإنتاجية، الري، الأمراض، المالية
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedSeason}
            onChange={(e) => setSelectedSeason(e.target.value)}
            className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-4 py-2 text-sm text-gray-900 dark:text-gray-100"
          >
            {SEASONS.map((s) => (
              <option key={s.id} value={s.id}>{s.label}</option>
            ))}
          </select>
          <button
            onClick={() => handleExport("pdf")}
            disabled={isExporting}
            className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg text-sm hover:bg-sahool-700 transition-colors disabled:opacity-50"
          >
            {isExporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
            تصدير PDF
          </button>
          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <Printer className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Season Overview Cards */}
      <div className="bg-gradient-to-br from-sahool-600 to-sahool-800 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-2 mb-4">
          <Calendar className="w-5 h-5 opacity-80" />
          <h2 className="text-lg font-bold">{season.season_name_ar}</h2>
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
            season.status === "active" ? "bg-green-500/20 text-green-200" :
            season.status === "completed" ? "bg-blue-500/20 text-blue-200" :
            "bg-yellow-500/20 text-yellow-200"
          }`}>
            {season.status === "active" ? "نشط" : season.status === "completed" ? "مكتمل" : "مخطط"}
          </span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { icon: MapPin, label: "المزارع", value: season.total_farms },
            { icon: Target, label: "الحقول", value: season.total_fields },
            { icon: Sprout, label: "المساحة الكلية", value: `${formatNumber(season.total_area_hectares)} هكتار` },
            { icon: Calendar, label: "الفترة", value: `${season.start_date.slice(5)} — ${season.end_date.slice(5)}` },
          ].map((s) => (
            <div key={s.label} className="bg-white/10 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <s.icon className="w-4 h-4 opacity-70" />
                <span className="text-xs opacity-70">{s.label}</span>
              </div>
              <p className="text-lg font-bold">{s.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Yield Analysis */}
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-sahool-600" />
          أداء الإنتاجية حسب المحصول
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400">
                <th className="text-right py-3 px-2 font-medium">المحصول</th>
                <th className="text-right py-3 px-2 font-medium">المساحة (هكتار)</th>
                <th className="text-right py-3 px-2 font-medium">الغلة (طن/هكتار)</th>
                <th className="text-right py-3 px-2 font-medium">المستهدف</th>
                <th className="text-right py-3 px-2 font-medium">الإنجاز</th>
                <th className="text-right py-3 px-2 font-medium">الإجمالي (طن)</th>
                <th className="text-right py-3 px-2 font-medium">مقارنة بالموسم السابق</th>
              </tr>
            </thead>
            <tbody>
              {yields.map((y) => (
                <tr key={y.crop_type} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                  <td className="py-3 px-2 font-medium text-gray-900 dark:text-gray-100">{y.crop_name_ar}</td>
                  <td className="py-3 px-2 text-gray-600 dark:text-gray-400">{formatNumber(y.total_area_hectares)}</td>
                  <td className="py-3 px-2 font-bold text-gray-900 dark:text-gray-100">{y.avg_yield_ton_per_ha}</td>
                  <td className="py-3 px-2 text-gray-500 dark:text-gray-400">{y.target_yield_ton_per_ha}</td>
                  <td className="py-3 px-2">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                        <div
                          className={`h-full rounded-full ${y.achievement_percent >= 90 ? "bg-green-500" : y.achievement_percent >= 75 ? "bg-yellow-500" : "bg-red-500"}`}
                          style={{ width: `${Math.min(y.achievement_percent, 100)}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium">{y.achievement_percent}%</span>
                    </div>
                  </td>
                  <td className="py-3 px-2 font-bold text-gray-900 dark:text-gray-100">{formatNumber(y.total_yield_tons)}</td>
                  <td className="py-3 px-2">
                    <span className={`flex items-center gap-1 text-sm font-medium ${y.comparison_last_season >= 0
                      ? "text-green-600 dark:text-green-400"
                      : "text-red-600 dark:text-red-400"
                    }`}>
                      {y.comparison_last_season >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingUp className="w-4 h-4 rotate-180" />}
                      {y.comparison_last_season >= 0 ? "+" : ""}{y.comparison_last_season}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Irrigation Summary */}
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
            <Droplets className="w-5 h-5 text-blue-600" />
            ملخص الري
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "إجمالي المياه", value: `${formatNumber(irrigation.total_water_m3)} م³`, color: "text-blue-600 dark:text-blue-400" },
              { label: "كفاءة الري", value: `${irrigation.avg_efficiency_percent}%`, color: "text-green-600 dark:text-green-400" },
              { label: "عمليات الري", value: formatNumber(irrigation.irrigation_events), color: "text-gray-900 dark:text-gray-100" },
              { label: "المياه الموفرة", value: `${formatNumber(irrigation.water_saved_m3)} م³ (${irrigation.water_saved_percent}%)`, color: "text-cyan-600 dark:text-cyan-400" },
            ].map((item) => (
              <div key={item.label} className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{item.label}</p>
                <p className={`text-lg font-bold ${item.color}`}>{item.value}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/10 rounded-lg">
            <p className="text-xs text-gray-500 dark:text-gray-400">تكلفة الري الإجمالية</p>
            <p className="text-lg font-bold text-blue-700 dark:text-blue-400">{formatMoney(irrigation.cost_yer)}</p>
          </div>
        </div>

        {/* Disease Summary */}
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
            <Bug className="w-5 h-5 text-red-600" />
            ملخص الأمراض والآفات
          </h3>
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{diseases.total_diagnoses}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">تشخيص</p>
            </div>
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">{diseases.resolved_percent}%</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">تم حلها</p>
            </div>
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">{diseases.treatments_applied}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">علاج مُطبَّق</p>
            </div>
          </div>
          <div className="space-y-2">
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400">أكثر الأمراض انتشاراً</p>
            {diseases.top_diseases.map((d, i) => (
              <div key={i} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800/50 rounded">
                <span className="text-sm text-gray-700 dark:text-gray-300">{d.name_ar}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{d.count}</span>
                  {getSeverityBadge(d.severity)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Financial Summary */}
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-green-600" />
            الملخص المالي
          </h3>
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="p-3 bg-green-50 dark:bg-green-900/10 rounded-lg text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400">الإيرادات</p>
              <p className="text-base font-bold text-green-700 dark:text-green-400">{formatMoney(financial.total_revenue_yer)}</p>
            </div>
            <div className="p-3 bg-red-50 dark:bg-red-900/10 rounded-lg text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400">التكاليف</p>
              <p className="text-base font-bold text-red-700 dark:text-red-400">{formatMoney(financial.total_cost_yer)}</p>
            </div>
            <div className="p-3 bg-blue-50 dark:bg-blue-900/10 rounded-lg text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400">صافي الربح</p>
              <p className="text-base font-bold text-blue-700 dark:text-blue-400">{formatMoney(financial.net_profit_yer)}</p>
            </div>
          </div>
          <div className="space-y-2">
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">توزيع التكاليف</p>
            {financial.cost_breakdown.map((c, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-xs text-gray-600 dark:text-gray-400 w-40 flex-shrink-0">{c.category_ar}</span>
                <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                  <div className="h-full bg-sahool-500 rounded-full" style={{ width: `${c.percent}%` }} />
                </div>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300 w-10 text-left">{c.percent}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Weather & Tasks Summary */}
        <div className="space-y-6">
          {/* Weather */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <Thermometer className="w-5 h-5 text-orange-600" />
              ملخص الطقس الموسمي
            </h3>
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: "متوسط الحرارة", value: `${weather.avg_temperature}°م`, icon: Thermometer },
                { label: "إجمالي الأمطار", value: `${weather.total_rainfall_mm} ملم`, icon: Droplets },
                { label: "GDD المتراكمة", value: formatNumber(weather.gdd_total), icon: TrendingUp },
              ].map((item) => (
                <div key={item.label} className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg text-center">
                  <item.icon className="w-5 h-5 mx-auto mb-1 text-gray-400" />
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{item.value}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{item.label}</p>
                </div>
              ))}
            </div>
            <div className="flex gap-3 mt-3">
              <div className="flex-1 p-2 bg-blue-50 dark:bg-blue-900/10 rounded text-center">
                <span className="text-sm font-bold text-blue-700 dark:text-blue-400">{weather.frost_events}</span>
                <p className="text-xs text-gray-500 dark:text-gray-400">حدث صقيع</p>
              </div>
              <div className="flex-1 p-2 bg-orange-50 dark:bg-orange-900/10 rounded text-center">
                <span className="text-sm font-bold text-orange-700 dark:text-orange-400">{weather.heat_stress_days}</span>
                <p className="text-xs text-gray-500 dark:text-gray-400">يوم إجهاد حراري</p>
              </div>
            </div>
          </div>

          {/* Tasks */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-sahool-600" />
              ملخص المهام
            </h3>
            <div className="flex items-center gap-4 mb-3">
              <div className="flex-1">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500 dark:text-gray-400">معدل الإنجاز</span>
                  <span className="font-bold text-sahool-600">{tasks.completion_rate_percent}%</span>
                </div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full">
                  <div className="h-full bg-sahool-500 rounded-full" style={{ width: `${tasks.completion_rate_percent}%` }} />
                </div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="text-center p-2 bg-gray-50 dark:bg-gray-800/50 rounded">
                <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{tasks.total_tasks}</p>
                <p className="text-xs text-gray-500">إجمالي</p>
              </div>
              <div className="text-center p-2 bg-green-50 dark:bg-green-900/10 rounded">
                <p className="text-lg font-bold text-green-600 dark:text-green-400">{tasks.completed_tasks}</p>
                <p className="text-xs text-gray-500">مكتمل</p>
              </div>
              <div className="text-center p-2 bg-red-50 dark:bg-red-900/10 rounded">
                <p className="text-lg font-bold text-red-600 dark:text-red-400">{tasks.overdue_tasks}</p>
                <p className="text-xs text-gray-500">متأخر</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
