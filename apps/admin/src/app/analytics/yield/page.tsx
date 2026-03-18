// Sahool Admin Dashboard - Deep Yield Analysis
// تحليل الغلة العميق

"use client";

import { useState, useEffect, useMemo } from "react";
import { apiClient, API_URLS } from "@/lib/api";
import { logger } from "@/lib/logger";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Download,
  Loader2,
  MapPin,
  Layers,
  ArrowLeftRight,
  Scale,
} from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────────────────

interface FieldYield {
  field_id: string;
  field_name_ar: string;
  farm_name_ar: string;
  governorate_ar: string;
  crop_type: string;
  crop_name_ar: string;
  area_hectares: number;
  yield_ton_per_ha: number;
  total_yield_tons: number;
  season: string;
  soil_type_ar: string;
  irrigation_type_ar: string;
  seed_variety_ar: string;
  planting_date: string;
  harvest_date: string;
  rainfall_mm: number;
  avg_temperature: number;
  ndvi_avg: number;
  fertilizer_applied_kg_per_ha: number;
}

interface YieldComparison {
  dimension: string;
  dimension_ar: string;
  groups: Array<{
    name: string;
    name_ar: string;
    avg_yield: number;
    total_area: number;
    field_count: number;
    min_yield: number;
    max_yield: number;
  }>;
}

interface SeasonTrend {
  season: string;
  season_ar: string;
  crop_type: string;
  avg_yield: number;
  total_area: number;
  total_yield: number;
}

// ─── Mock Data ───────────────────────────────────────────────────────────────

const MOCK_FIELDS: FieldYield[] = [
  { field_id: "f1", field_name_ar: "حقل القمح الشمالي", farm_name_ar: "مزرعة الرشيد", governorate_ar: "صنعاء", crop_type: "wheat", crop_name_ar: "قمح", area_hectares: 12, yield_ton_per_ha: 3.8, total_yield_tons: 45.6, season: "2025-winter", soil_type_ar: "طينية", irrigation_type_ar: "ري بالتنقيط", seed_variety_ar: "سخا 95", planting_date: "2025-10-15", harvest_date: "2026-03-20", rainfall_mm: 180, avg_temperature: 17, ndvi_avg: 0.72, fertilizer_applied_kg_per_ha: 150 },
  { field_id: "f2", field_name_ar: "حقل القمح الجنوبي", farm_name_ar: "مزرعة الرشيد", governorate_ar: "صنعاء", crop_type: "wheat", crop_name_ar: "قمح", area_hectares: 8, yield_ton_per_ha: 3.2, total_yield_tons: 25.6, season: "2025-winter", soil_type_ar: "رملية طينية", irrigation_type_ar: "ري غمر", seed_variety_ar: "مصر 3", planting_date: "2025-10-20", harvest_date: "2026-03-25", rainfall_mm: 180, avg_temperature: 17, ndvi_avg: 0.65, fertilizer_applied_kg_per_ha: 120 },
  { field_id: "f3", field_name_ar: "حقل الشعير", farm_name_ar: "مزرعة النور", governorate_ar: "إب", crop_type: "barley", crop_name_ar: "شعير", area_hectares: 15, yield_ton_per_ha: 3.1, total_yield_tons: 46.5, season: "2025-winter", soil_type_ar: "طينية", irrigation_type_ar: "ري رشاش", seed_variety_ar: "جيزة 136", planting_date: "2025-10-10", harvest_date: "2026-03-15", rainfall_mm: 220, avg_temperature: 16, ndvi_avg: 0.68, fertilizer_applied_kg_per_ha: 110 },
  { field_id: "f4", field_name_ar: "حقل الطماطم A", farm_name_ar: "مزرعة الخير", governorate_ar: "تعز", crop_type: "tomato", crop_name_ar: "طماطم", area_hectares: 5, yield_ton_per_ha: 28.0, total_yield_tons: 140, season: "2025-winter", soil_type_ar: "طينية ثقيلة", irrigation_type_ar: "ري بالتنقيط", seed_variety_ar: "هجين 1023", planting_date: "2025-11-01", harvest_date: "2026-02-28", rainfall_mm: 250, avg_temperature: 20, ndvi_avg: 0.78, fertilizer_applied_kg_per_ha: 200 },
  { field_id: "f5", field_name_ar: "حقل الطماطم B", farm_name_ar: "مزرعة الخير", governorate_ar: "تعز", crop_type: "tomato", crop_name_ar: "طماطم", area_hectares: 4, yield_ton_per_ha: 22.5, total_yield_tons: 90, season: "2025-winter", soil_type_ar: "رملية", irrigation_type_ar: "ري غمر", seed_variety_ar: "محلي", planting_date: "2025-11-10", harvest_date: "2026-03-05", rainfall_mm: 250, avg_temperature: 20, ndvi_avg: 0.62, fertilizer_applied_kg_per_ha: 130 },
  { field_id: "f6", field_name_ar: "حقل البطاطس", farm_name_ar: "مزرعة السلام", governorate_ar: "الحديدة", crop_type: "potato", crop_name_ar: "بطاطس", area_hectares: 10, yield_ton_per_ha: 19.0, total_yield_tons: 190, season: "2025-winter", soil_type_ar: "رملية طينية", irrigation_type_ar: "ري ذكي", seed_variety_ar: "سبونتا", planting_date: "2025-10-25", harvest_date: "2026-02-20", rainfall_mm: 80, avg_temperature: 24, ndvi_avg: 0.70, fertilizer_applied_kg_per_ha: 180 },
  { field_id: "f7", field_name_ar: "حقل البن", farm_name_ar: "مزرعة الجبل", governorate_ar: "إب", crop_type: "coffee", crop_name_ar: "بن يمني", area_hectares: 20, yield_ton_per_ha: 0.85, total_yield_tons: 17, season: "2025-winter", soil_type_ar: "بركانية", irrigation_type_ar: "أمطار", seed_variety_ar: "بن مخا", planting_date: "2020-01-01", harvest_date: "2025-12-15", rainfall_mm: 350, avg_temperature: 18, ndvi_avg: 0.75, fertilizer_applied_kg_per_ha: 60 },
  { field_id: "f8", field_name_ar: "حقل القمح المرتفعات", farm_name_ar: "مزرعة الجبل", governorate_ar: "إب", crop_type: "wheat", crop_name_ar: "قمح", area_hectares: 6, yield_ton_per_ha: 4.1, total_yield_tons: 24.6, season: "2025-winter", soil_type_ar: "بركانية", irrigation_type_ar: "أمطار + تكميلي", seed_variety_ar: "سخا 95", planting_date: "2025-10-05", harvest_date: "2026-03-10", rainfall_mm: 350, avg_temperature: 15, ndvi_avg: 0.76, fertilizer_applied_kg_per_ha: 140 },
];

const MOCK_TRENDS: SeasonTrend[] = [
  { season: "2023-winter", season_ar: "شتاء 2023", crop_type: "wheat", avg_yield: 2.8, total_area: 100, total_yield: 280 },
  { season: "2024-summer", season_ar: "صيف 2024", crop_type: "wheat", avg_yield: 2.5, total_area: 60, total_yield: 150 },
  { season: "2024-winter", season_ar: "شتاء 2024", crop_type: "wheat", avg_yield: 3.0, total_area: 110, total_yield: 330 },
  { season: "2025-winter", season_ar: "شتاء 2025", crop_type: "wheat", avg_yield: 3.5, total_area: 126, total_yield: 441 },
];

// ─── Component ───────────────────────────────────────────────────────────────

type ComparisonDimension = "crop" | "soil" | "irrigation" | "governorate" | "seed" | "farm";

const DIMENSIONS: Array<{ id: ComparisonDimension; label: string }> = [
  { id: "crop", label: "المحصول" },
  { id: "soil", label: "نوع التربة" },
  { id: "irrigation", label: "نوع الري" },
  { id: "governorate", label: "المحافظة" },
  { id: "seed", label: "الصنف" },
  { id: "farm", label: "المزرعة" },
];

export default function YieldAnalysisPage() {
  const [fields, setFields] = useState<FieldYield[]>([]);
  const [trends, setTrends] = useState<SeasonTrend[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [dimension, setDimension] = useState<ComparisonDimension>("crop");
  const [cropFilter, setCropFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<"yield" | "area" | "total">("yield");
  const [sortDesc, setSortDesc] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [fieldsRes, trendsRes] = await Promise.allSettled([
        apiClient.get(`${API_URLS.yieldPrediction}/api/v1/yield/analysis`, { params: { season: "2025-winter" } }),
        apiClient.get(`${API_URLS.yieldPrediction}/api/v1/yield/trends`),
      ]);
      setFields(fieldsRes.status === "fulfilled" ? fieldsRes.value.data : MOCK_FIELDS);
      setTrends(trendsRes.status === "fulfilled" ? trendsRes.value.data : MOCK_TRENDS);
    } catch (err) {
      logger.warn("Yield API unavailable, using demo data", err);
      setFields(MOCK_FIELDS);
      setTrends(MOCK_TRENDS);
    } finally {
      setIsLoading(false);
    }
  };

  // Available crop types
  const cropTypes = useMemo(() => {
    const types = new Set(fields.map((f) => f.crop_type));
    return Array.from(types).map((t) => ({
      value: t,
      label: fields.find((f) => f.crop_type === t)?.crop_name_ar || t,
    }));
  }, [fields]);

  // Filtered fields
  const filteredFields = useMemo(() => {
    let result = cropFilter === "all" ? fields : fields.filter((f) => f.crop_type === cropFilter);
    result = [...result].sort((a, b) => {
      const va = sortBy === "yield" ? a.yield_ton_per_ha : sortBy === "area" ? a.area_hectares : a.total_yield_tons;
      const vb = sortBy === "yield" ? b.yield_ton_per_ha : sortBy === "area" ? b.area_hectares : b.total_yield_tons;
      return sortDesc ? vb - va : va - vb;
    });
    return result;
  }, [fields, cropFilter, sortBy, sortDesc]);

  // Comparison data
  const comparison = useMemo((): YieldComparison => {
    const dimensionKey = (f: FieldYield) => {
      switch (dimension) {
        case "crop": return f.crop_name_ar;
        case "soil": return f.soil_type_ar;
        case "irrigation": return f.irrigation_type_ar;
        case "governorate": return f.governorate_ar;
        case "seed": return f.seed_variety_ar;
        case "farm": return f.farm_name_ar;
      }
    };

    const grouped = new Map<string, FieldYield[]>();
    for (const f of filteredFields) {
      const key = dimensionKey(f);
      if (!grouped.has(key)) grouped.set(key, []);
      grouped.get(key)!.push(f);
    }

    const groups = Array.from(grouped.entries()).map(([name, items]) => ({
      name,
      name_ar: name,
      avg_yield: items.reduce((s, f) => s + f.yield_ton_per_ha, 0) / items.length,
      total_area: items.reduce((s, f) => s + f.area_hectares, 0),
      field_count: items.length,
      min_yield: Math.min(...items.map((f) => f.yield_ton_per_ha)),
      max_yield: Math.max(...items.map((f) => f.yield_ton_per_ha)),
    })).sort((a, b) => b.avg_yield - a.avg_yield);

    return {
      dimension,
      dimension_ar: DIMENSIONS.find((d) => d.id === dimension)?.label || "",
      groups,
    };
  }, [filteredFields, dimension]);

  // Stats
  const stats = useMemo(() => {
    if (filteredFields.length === 0) return null;
    const totalArea = filteredFields.reduce((s, f) => s + f.area_hectares, 0);
    const totalYield = filteredFields.reduce((s, f) => s + f.total_yield_tons, 0);
    const avgYield = filteredFields.reduce((s, f) => s + f.yield_ton_per_ha, 0) / filteredFields.length;
    const maxYield = Math.max(...filteredFields.map((f) => f.yield_ton_per_ha));
    const minYield = Math.min(...filteredFields.map((f) => f.yield_ton_per_ha));
    const bestField = filteredFields.find((f) => f.yield_ton_per_ha === maxYield);
    return { totalArea, totalYield, avgYield, maxYield, minYield, bestField, fieldCount: filteredFields.length };
  }, [filteredFields]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-sahool-600" />
        <span className="mr-3 text-gray-500 dark:text-gray-400">جاري تحميل بيانات الغلة...</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <BarChart3 className="w-7 h-7 text-sahool-600" />
            تحليل الغلة العميق
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            مقارنة الغلة حسب الحقل، التربة، الصنف، نوع الري — مع تتبع الاتجاهات
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={cropFilter}
            onChange={(e) => setCropFilter(e.target.value)}
            className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-4 py-2 text-sm"
          >
            <option value="all">كل المحاصيل</option>
            {cropTypes.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
          <button
            disabled
            className="flex items-center gap-2 px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-300 disabled:opacity-40 disabled:cursor-not-allowed"
            title="تصدير (قريبًا)"
          >
            <Download className="w-4 h-4" />
            تصدير
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { label: "عدد الحقول", value: stats.fieldCount, icon: Layers, color: "text-blue-600 dark:text-blue-400" },
            { label: "المساحة الكلية", value: `${stats.totalArea.toFixed(0)} هكتار`, icon: MapPin, color: "text-green-600 dark:text-green-400" },
            { label: "إجمالي الغلة", value: `${stats.totalYield.toFixed(0)} طن`, icon: Scale, color: "text-purple-600 dark:text-purple-400" },
            { label: "متوسط الغلة", value: `${stats.avgYield.toFixed(1)} طن/هك`, icon: BarChart3, color: "text-sahool-600 dark:text-sahool-400" },
            { label: "أعلى غلة", value: `${stats.maxYield.toFixed(1)} طن/هك`, icon: TrendingUp, color: "text-green-600 dark:text-green-400" },
            { label: "أدنى غلة", value: `${stats.minYield.toFixed(1)} طن/هك`, icon: TrendingDown, color: "text-red-600 dark:text-red-400" },
          ].map((s) => (
            <div key={s.label} className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
              <div className="flex items-center gap-2 mb-2">
                <s.icon className={`w-4 h-4 ${s.color}`} />
                <span className="text-xs text-gray-500 dark:text-gray-400">{s.label}</span>
              </div>
              <p className={`text-lg font-bold ${s.color}`}>{s.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Comparison Section */}
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <ArrowLeftRight className="w-5 h-5 text-sahool-600" />
            مقارنة الغلة حسب: {comparison.dimension_ar}
          </h3>
          <div className="flex gap-2 flex-wrap">
            {DIMENSIONS.map((d) => (
              <button
                key={d.id}
                onClick={() => setDimension(d.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${dimension === d.id
                  ? "bg-sahool-100 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300 border border-sahool-300 dark:border-sahool-700"
                  : "bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700"
                }`}
              >
                {d.label}
              </button>
            ))}
          </div>
        </div>

        {/* Visual comparison bars */}
        <div className="space-y-3">
          {comparison.groups.map((g, i) => {
            const maxYield = Math.max(...comparison.groups.map((x) => x.max_yield), 1);
            const barWidth = (g.avg_yield / maxYield) * 100;
            return (
              <div key={i} className="flex items-center gap-4 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                <div className="w-32 flex-shrink-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{g.name_ar}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{g.field_count} حقل — {g.total_area.toFixed(0)} هكتار</p>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-6 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-l from-sahool-500 to-sahool-400 flex items-center justify-end px-2"
                        style={{ width: `${Math.max(barWidth, 8)}%` }}
                      >
                        {barWidth > 20 && (
                          <span className="text-xs font-bold text-white">{g.avg_yield.toFixed(1)}</span>
                        )}
                      </div>
                    </div>
                    {barWidth <= 20 && (
                      <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{g.avg_yield.toFixed(1)}</span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 mt-1 text-xs text-gray-500 dark:text-gray-400">
                    <span>الحد الأدنى: {g.min_yield.toFixed(1)}</span>
                    <span>—</span>
                    <span>الحد الأعلى: {g.max_yield.toFixed(1)}</span>
                    <span className="text-gray-400 dark:text-gray-500">طن/هكتار</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Season Trends */}
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-sahool-600" />
          اتجاه الغلة عبر المواسم (القمح)
        </h3>
        <div className="flex items-end gap-6 h-40">
          {trends.map((t, i) => {
            const maxYield = Math.max(...trends.map((x) => x.avg_yield), 1);
            const height = (t.avg_yield / maxYield) * 100;
            const prevYield = i > 0 ? trends[i - 1]!.avg_yield : t.avg_yield;
            const change = ((t.avg_yield - prevYield) / prevYield) * 100;
            return (
              <div key={t.season} className="flex-1 flex flex-col items-center gap-1">
                <span className="text-sm font-bold text-sahool-600 dark:text-sahool-400">{t.avg_yield.toFixed(1)}</span>
                {i > 0 && (
                  <span className={`text-xs font-medium ${change >= 0 ? "text-green-500" : "text-red-500"}`}>
                    {change >= 0 ? "+" : ""}{change.toFixed(0)}%
                  </span>
                )}
                <div
                  className="w-full rounded-t-md bg-gradient-to-t from-sahool-600 to-sahool-400"
                  style={{ height: `${Math.max(height, 10)}%` }}
                />
                <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">{t.season_ar}</span>
                <span className="text-xs text-gray-400">{t.total_area} هك</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Detailed Table */}
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <Layers className="w-5 h-5 text-sahool-600" />
            بيانات الحقول التفصيلية
          </h3>
          <div className="flex gap-2">
            {[
              { id: "yield" as const, label: "الغلة" },
              { id: "area" as const, label: "المساحة" },
              { id: "total" as const, label: "الإنتاج الكلي" },
            ].map((s) => (
              <button
                key={s.id}
                onClick={() => { setSortBy(s.id); setSortDesc(sortBy === s.id ? !sortDesc : true); }}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${sortBy === s.id
                  ? "bg-sahool-100 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300"
                  : "bg-gray-50 dark:bg-gray-800 text-gray-500 dark:text-gray-400"
                }`}
              >
                {s.label} {sortBy === s.id && (sortDesc ? "↓" : "↑")}
              </button>
            ))}
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400">
                <th className="text-right py-3 px-2 font-medium">الحقل</th>
                <th className="text-right py-3 px-2 font-medium">المزرعة</th>
                <th className="text-right py-3 px-2 font-medium">المحصول</th>
                <th className="text-right py-3 px-2 font-medium">الصنف</th>
                <th className="text-right py-3 px-2 font-medium">المساحة</th>
                <th className="text-right py-3 px-2 font-medium">الغلة (طن/هك)</th>
                <th className="text-right py-3 px-2 font-medium">الإجمالي</th>
                <th className="text-right py-3 px-2 font-medium">التربة</th>
                <th className="text-right py-3 px-2 font-medium">الري</th>
                <th className="text-right py-3 px-2 font-medium">NDVI</th>
                <th className="text-right py-3 px-2 font-medium">أسمدة (كجم/هك)</th>
              </tr>
            </thead>
            <tbody>
              {filteredFields.map((f) => {
                const avgForCrop = filteredFields.filter((x) => x.crop_type === f.crop_type).reduce((s, x) => s + x.yield_ton_per_ha, 0) / filteredFields.filter((x) => x.crop_type === f.crop_type).length;
                const aboveAvg = f.yield_ton_per_ha >= avgForCrop;
                return (
                  <tr key={f.field_id} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="py-3 px-2 font-medium text-gray-900 dark:text-gray-100">{f.field_name_ar}</td>
                    <td className="py-3 px-2 text-gray-600 dark:text-gray-400">{f.farm_name_ar}</td>
                    <td className="py-3 px-2 text-gray-600 dark:text-gray-400">{f.crop_name_ar}</td>
                    <td className="py-3 px-2 text-gray-500 dark:text-gray-400 text-xs">{f.seed_variety_ar}</td>
                    <td className="py-3 px-2 text-gray-600 dark:text-gray-400">{f.area_hectares}</td>
                    <td className="py-3 px-2">
                      <span className={`font-bold ${aboveAvg ? "text-green-600 dark:text-green-400" : "text-orange-600 dark:text-orange-400"}`}>
                        {f.yield_ton_per_ha.toFixed(1)}
                      </span>
                      {aboveAvg ? (
                        <TrendingUp className="inline w-3 h-3 mr-1 text-green-500" />
                      ) : (
                        <TrendingDown className="inline w-3 h-3 mr-1 text-orange-500" />
                      )}
                    </td>
                    <td className="py-3 px-2 font-medium text-gray-900 dark:text-gray-100">{f.total_yield_tons.toFixed(1)}</td>
                    <td className="py-3 px-2 text-xs text-gray-500 dark:text-gray-400">{f.soil_type_ar}</td>
                    <td className="py-3 px-2 text-xs text-gray-500 dark:text-gray-400">{f.irrigation_type_ar}</td>
                    <td className="py-3 px-2">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                        f.ndvi_avg >= 0.7 ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400" :
                        f.ndvi_avg >= 0.5 ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400" :
                        "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400"
                      }`}>
                        {f.ndvi_avg.toFixed(2)}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-gray-600 dark:text-gray-400">{f.fertilizer_applied_kg_per_ha}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
