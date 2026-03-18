// Sahool Admin Dashboard - Soil Nutrition Monitoring
// مراقبة تغذية التربة

"use client";

import { useState, useEffect, useMemo } from "react";
import { apiClient, API_URLS } from "@/lib/api";
import { API_PATHS } from "@/config/api";
import { logger } from "@/lib/logger";
import {
  Layers,
  Droplets,
  AlertTriangle,
  Loader2,
  MapPin,
  Calendar,
  Download,
  Activity,
  Gauge,
  Leaf,
  Zap,
  BarChart3,
} from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────────────────

interface SoilTest {
  id: string;
  field_id: string;
  field_name_ar: string;
  farm_name_ar: string;
  governorate_ar: string;
  test_date: string;
  depth_cm: number;
  ph: number;
  ec_ds_m: number;
  organic_matter_percent: number;
  nitrogen_ppm: number;
  phosphorus_ppm: number;
  potassium_ppm: number;
  calcium_ppm: number;
  magnesium_ppm: number;
  sulfur_ppm: number;
  iron_ppm: number;
  zinc_ppm: number;
  texture_ar: string;
  moisture_percent: number;
  salinity_level: "low" | "moderate" | "high" | "critical";
  status: "optimal" | "deficient" | "excess" | "critical";
  recommendations_ar: string[];
}

interface NutrientThreshold {
  name: string;
  name_ar: string;
  unit: string;
  low: number;
  optimal_min: number;
  optimal_max: number;
  high: number;
}

// ─── Constants ───────────────────────────────────────────────────────────────

const NUTRIENT_THRESHOLDS: NutrientThreshold[] = [
  { name: "nitrogen", name_ar: "النيتروجين (N)", unit: "ppm", low: 20, optimal_min: 25, optimal_max: 50, high: 60 },
  { name: "phosphorus", name_ar: "الفوسفور (P)", unit: "ppm", low: 10, optimal_min: 15, optimal_max: 40, high: 50 },
  { name: "potassium", name_ar: "البوتاسيوم (K)", unit: "ppm", low: 100, optimal_min: 150, optimal_max: 300, high: 400 },
  { name: "calcium", name_ar: "الكالسيوم (Ca)", unit: "ppm", low: 1000, optimal_min: 1500, optimal_max: 3000, high: 4000 },
  { name: "magnesium", name_ar: "المغنيسيوم (Mg)", unit: "ppm", low: 100, optimal_min: 150, optimal_max: 400, high: 500 },
];

// ─── Mock Data ───────────────────────────────────────────────────────────────

const MOCK_TESTS: SoilTest[] = [
  { id: "s1", field_id: "f1", field_name_ar: "حقل القمح الشمالي", farm_name_ar: "مزرعة الرشيد", governorate_ar: "صنعاء", test_date: "2026-02-15", depth_cm: 30, ph: 7.2, ec_ds_m: 1.8, organic_matter_percent: 2.1, nitrogen_ppm: 18, phosphorus_ppm: 25, potassium_ppm: 180, calcium_ppm: 2200, magnesium_ppm: 250, sulfur_ppm: 12, iron_ppm: 8, zinc_ppm: 2.5, texture_ar: "طينية", moisture_percent: 38, salinity_level: "low", status: "deficient", recommendations_ar: ["إضافة سماد يوريا 46% بمعدل 46 كجم/هكتار", "النيتروجين أقل من الحد الأمثل (18 < 25 ppm)"] },
  { id: "s2", field_id: "f2", field_name_ar: "حقل القمح الجنوبي", farm_name_ar: "مزرعة الرشيد", governorate_ar: "صنعاء", test_date: "2026-02-15", depth_cm: 30, ph: 7.8, ec_ds_m: 3.2, organic_matter_percent: 1.5, nitrogen_ppm: 32, phosphorus_ppm: 12, potassium_ppm: 120, calcium_ppm: 1800, magnesium_ppm: 180, sulfur_ppm: 8, iron_ppm: 5, zinc_ppm: 1.8, texture_ar: "رملية طينية", moisture_percent: 28, salinity_level: "moderate", status: "deficient", recommendations_ar: ["إضافة سوبر فوسفات (P أقل من الحد)", "معالجة ملوحة التربة (EC = 3.2)"] },
  { id: "s3", field_id: "f3", field_name_ar: "حقل الشعير", farm_name_ar: "مزرعة النور", governorate_ar: "إب", test_date: "2026-01-20", depth_cm: 30, ph: 6.8, ec_ds_m: 0.9, organic_matter_percent: 3.2, nitrogen_ppm: 42, phosphorus_ppm: 35, potassium_ppm: 220, calcium_ppm: 2500, magnesium_ppm: 300, sulfur_ppm: 15, iron_ppm: 12, zinc_ppm: 3.5, texture_ar: "طينية", moisture_percent: 45, salinity_level: "low", status: "optimal", recommendations_ar: ["التربة في حالة جيدة — استمر في البرنامج الحالي"] },
  { id: "s4", field_id: "f4", field_name_ar: "حقل الطماطم A", farm_name_ar: "مزرعة الخير", governorate_ar: "تعز", test_date: "2026-02-01", depth_cm: 20, ph: 6.5, ec_ds_m: 1.2, organic_matter_percent: 2.8, nitrogen_ppm: 55, phosphorus_ppm: 40, potassium_ppm: 350, calcium_ppm: 2800, magnesium_ppm: 350, sulfur_ppm: 18, iron_ppm: 15, zinc_ppm: 4.2, texture_ar: "طينية ثقيلة", moisture_percent: 52, salinity_level: "low", status: "optimal", recommendations_ar: ["التغذية ممتازة — خفض النيتروجين قليلاً لتجنب الإفراط"] },
  { id: "s5", field_id: "f5", field_name_ar: "حقل البطاطس", farm_name_ar: "مزرعة السلام", governorate_ar: "الحديدة", test_date: "2026-02-10", depth_cm: 25, ph: 8.2, ec_ds_m: 4.5, organic_matter_percent: 0.8, nitrogen_ppm: 15, phosphorus_ppm: 8, potassium_ppm: 90, calcium_ppm: 3500, magnesium_ppm: 450, sulfur_ppm: 6, iron_ppm: 3, zinc_ppm: 1.0, texture_ar: "رملية", moisture_percent: 18, salinity_level: "high", status: "critical", recommendations_ar: ["معالجة ملوحة عاجلة (EC = 4.5)", "إضافة NPK كامل — جميع العناصر ناقصة", "إضافة مادة عضوية لتحسين بنية التربة", "غسيل ملحي بـ 200 ملم مياه نظيفة"] },
  { id: "s6", field_id: "f6", field_name_ar: "حقل البن", farm_name_ar: "مزرعة الجبل", governorate_ar: "إب", test_date: "2026-01-10", depth_cm: 40, ph: 5.8, ec_ds_m: 0.5, organic_matter_percent: 4.5, nitrogen_ppm: 38, phosphorus_ppm: 22, potassium_ppm: 200, calcium_ppm: 1500, magnesium_ppm: 200, sulfur_ppm: 20, iron_ppm: 18, zinc_ppm: 5.0, texture_ar: "بركانية", moisture_percent: 55, salinity_level: "low", status: "optimal", recommendations_ar: ["تربة بركانية ممتازة للبن — حافظ على المادة العضوية"] },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

function getNutrientStatus(value: number, threshold: NutrientThreshold): { label: string; color: string } {
  if (value < threshold.low) return { label: "ناقص", color: "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20" };
  if (value < threshold.optimal_min) return { label: "منخفض", color: "text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20" };
  if (value <= threshold.optimal_max) return { label: "مثالي", color: "text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20" };
  if (value <= threshold.high) return { label: "مرتفع", color: "text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20" };
  return { label: "مفرط", color: "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20" };
}

function getSalinityColor(level: string) {
  switch (level) {
    case "low": return "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400";
    case "moderate": return "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400";
    case "high": return "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400";
    case "critical": return "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400";
    default: return "bg-gray-100 text-gray-700";
  }
}

const SALINITY_LABELS: Record<string, string> = {
  low: "منخفضة",
  moderate: "متوسطة",
  high: "مرتفعة",
  critical: "حرجة",
};

// ─── Component ───────────────────────────────────────────────────────────────

export default function SoilMonitoringPage() {
  const [tests, setTests] = useState<SoilTest[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTest, setSelectedTest] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>("all");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.get(`${API_URLS.soilAnalysis}${API_PATHS.soilAnalysis.tests}`);
      setTests(response.data);
    } catch (err) {
      logger.warn("Soil API unavailable, using demo data", err);
      setTests(MOCK_TESTS);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredTests = useMemo(() => {
    if (filterStatus === "all") return tests;
    return tests.filter((t) => t.status === filterStatus);
  }, [tests, filterStatus]);

  const stats = useMemo(() => {
    const optimal = tests.filter((t) => t.status === "optimal").length;
    const deficient = tests.filter((t) => t.status === "deficient").length;
    const critical = tests.filter((t) => t.status === "critical").length;
    const avgPh = tests.reduce((s, t) => s + t.ph, 0) / (tests.length || 1);
    const avgEC = tests.reduce((s, t) => s + t.ec_ds_m, 0) / (tests.length || 1);
    const highSalinity = tests.filter((t) => t.salinity_level === "high" || t.salinity_level === "critical").length;
    return { total: tests.length, optimal, deficient, critical, avgPh, avgEC, highSalinity };
  }, [tests]);

  const selectedData = tests.find((t) => t.id === selectedTest);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-sahool-600" />
        <span className="mr-3 text-gray-500 dark:text-gray-400">جاري تحميل بيانات التربة...</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <Layers className="w-7 h-7 text-sahool-600" />
            مراقبة تغذية التربة
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            تحليل NPK والملوحة والعناصر الغذائية — لكل حقل بالتفصيل
          </p>
        </div>
        <div className="flex gap-3">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-4 py-2 text-sm"
          >
            <option value="all">كل الحالات</option>
            <option value="optimal">مثالي</option>
            <option value="deficient">ناقص</option>
            <option value="critical">حرج</option>
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

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-4">
        {[
          { label: "إجمالي الاختبارات", value: stats.total, icon: Layers, color: "text-blue-600 dark:text-blue-400" },
          { label: "مثالي", value: stats.optimal, icon: Leaf, color: "text-green-600 dark:text-green-400" },
          { label: "ناقص", value: stats.deficient, icon: AlertTriangle, color: "text-yellow-600 dark:text-yellow-400" },
          { label: "حرج", value: stats.critical, icon: Zap, color: "text-red-600 dark:text-red-400" },
          { label: "متوسط pH", value: stats.avgPh.toFixed(1), icon: Gauge, color: "text-purple-600 dark:text-purple-400" },
          { label: "متوسط EC", value: `${stats.avgEC.toFixed(1)} dS/m`, icon: Activity, color: "text-cyan-600 dark:text-cyan-400" },
          { label: "ملوحة عالية", value: stats.highSalinity, icon: Droplets, color: "text-orange-600 dark:text-orange-400" },
        ].map((s) => (
          <div key={s.label} className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-3">
            <div className="flex items-center gap-2 mb-1">
              <s.icon className={`w-4 h-4 ${s.color}`} />
              <span className="text-xs text-gray-500 dark:text-gray-400">{s.label}</span>
            </div>
            <p className={`text-lg font-bold ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Test List */}
        <div className="lg:col-span-2 space-y-3">
          {filteredTests.map((test) => {
            const isSelected = selectedTest === test.id;
            return (
              <div
                key={test.id}
                onClick={() => setSelectedTest(isSelected ? null : test.id)}
                className={`bg-white dark:bg-gray-900 rounded-xl border p-4 cursor-pointer transition-all ${
                  isSelected ? "border-sahool-500 ring-1 ring-sahool-200 dark:ring-sahool-800" : "border-gray-200 dark:border-gray-800 hover:border-gray-300"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-bold text-gray-900 dark:text-gray-100">{test.field_name_ar}</h3>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        test.status === "optimal" ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400" :
                        test.status === "deficient" ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400" :
                        "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400"
                      }`}>
                        {test.status === "optimal" ? "مثالي" : test.status === "deficient" ? "ناقص" : "حرج"}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getSalinityColor(test.salinity_level)}`}>
                        ملوحة {SALINITY_LABELS[test.salinity_level]}
                      </span>
                    </div>
                    <div className="flex gap-3 text-xs text-gray-500 dark:text-gray-400">
                      <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{test.farm_name_ar}</span>
                      <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{test.test_date}</span>
                      <span>{test.texture_ar}</span>
                    </div>
                    {/* NPK Quick Bar */}
                    <div className="flex gap-4 mt-3">
                      {[
                        { label: "N", value: test.nitrogen_ppm, threshold: NUTRIENT_THRESHOLDS[0]! },
                        { label: "P", value: test.phosphorus_ppm, threshold: NUTRIENT_THRESHOLDS[1]! },
                        { label: "K", value: test.potassium_ppm, threshold: NUTRIENT_THRESHOLDS[2]! },
                      ].map((n) => {
                        const ns = getNutrientStatus(n.value, n.threshold);
                        return (
                          <div key={n.label} className="flex items-center gap-2">
                            <span className="text-xs font-bold text-gray-500 w-3">{n.label}</span>
                            <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                              <div
                                className={`h-full rounded-full ${
                                  ns.label === "مثالي" ? "bg-green-500" :
                                  ns.label === "منخفض" || ns.label === "ناقص" ? "bg-orange-500" :
                                  "bg-red-500"
                                }`}
                                style={{ width: `${Math.min((n.value / n.threshold.high) * 100, 100)}%` }}
                              />
                            </div>
                            <span className="text-xs font-medium text-gray-600 dark:text-gray-400">{n.value}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  <div className="text-left flex-shrink-0">
                    <p className="text-sm text-gray-500">pH</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-gray-100">{test.ph}</p>
                    <p className="text-xs text-gray-400">EC: {test.ec_ds_m}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Detail Panel */}
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-sahool-600" />
            تفاصيل العناصر الغذائية
          </h3>
          {!selectedData ? (
            <div className="text-center py-12 text-gray-400">
              <Layers className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">اختر اختبار تربة لعرض التفاصيل</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="p-3 bg-sahool-50 dark:bg-sahool-900/20 rounded-lg">
                <p className="text-sm font-bold text-sahool-700 dark:text-sahool-300">{selectedData.field_name_ar}</p>
                <p className="text-xs text-sahool-600 dark:text-sahool-400">{selectedData.farm_name_ar} — {selectedData.governorate_ar}</p>
              </div>

              {/* All nutrients */}
              <div className="space-y-3">
                {NUTRIENT_THRESHOLDS.map((threshold) => {
                  const key = threshold.name as keyof SoilTest;
                  const value = selectedData[key] as number;
                  const ns = getNutrientStatus(value, threshold);
                  const percent = Math.min((value / threshold.high) * 100, 100);
                  return (
                    <div key={threshold.name}>
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-gray-700 dark:text-gray-300">{threshold.name_ar}</span>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-gray-900 dark:text-gray-100">{value} {threshold.unit}</span>
                          <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${ns.color}`}>{ns.label}</span>
                        </div>
                      </div>
                      <div className="w-full h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full relative">
                        {/* Optimal zone indicator */}
                        <div
                          className="absolute h-full bg-green-200 dark:bg-green-900/30 rounded-full"
                          style={{
                            left: `${(threshold.optimal_min / threshold.high) * 100}%`,
                            width: `${((threshold.optimal_max - threshold.optimal_min) / threshold.high) * 100}%`,
                          }}
                        />
                        <div
                          className={`absolute h-full rounded-full ${
                            ns.label === "مثالي" ? "bg-green-500" :
                            ns.label === "منخفض" || ns.label === "ناقص" ? "bg-orange-500" :
                            ns.label === "مرتفع" ? "bg-yellow-500" :
                            "bg-red-500"
                          }`}
                          style={{ width: `${Math.max(percent, 3)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Extra metrics */}
              <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                {[
                  { label: "المادة العضوية", value: `${selectedData.organic_matter_percent}%` },
                  { label: "الرطوبة", value: `${selectedData.moisture_percent}%` },
                  { label: "الحديد (Fe)", value: `${selectedData.iron_ppm} ppm` },
                  { label: "الزنك (Zn)", value: `${selectedData.zinc_ppm} ppm` },
                  { label: "الكبريت (S)", value: `${selectedData.sulfur_ppm} ppm` },
                  { label: "العمق", value: `${selectedData.depth_cm} سم` },
                ].map((m) => (
                  <div key={m.label} className="p-2 bg-gray-50 dark:bg-gray-800/50 rounded">
                    <p className="text-xs text-gray-500 dark:text-gray-400">{m.label}</p>
                    <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{m.value}</p>
                  </div>
                ))}
              </div>

              {/* Recommendations */}
              {selectedData.recommendations_ar.length > 0 && (
                <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-xs font-bold text-gray-500 dark:text-gray-400 mb-2">التوصيات</p>
                  <div className="space-y-2">
                    {selectedData.recommendations_ar.map((rec, i) => (
                      <div key={i} className="flex gap-2 p-2 bg-amber-50 dark:bg-amber-900/10 rounded text-sm text-amber-800 dark:text-amber-300">
                        <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                        <span>{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
