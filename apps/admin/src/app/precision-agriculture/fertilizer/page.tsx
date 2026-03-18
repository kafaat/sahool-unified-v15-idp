"use client";

// Enhanced VRA Fertilizer Prescription Management
// إدارة وصفات التسميد المتغير المحسّنة

import { useEffect, useState, useCallback } from "react";
import Header from "@/components/layout/Header";
import StatCard from "@/components/ui/StatCard";
import StatusBadge from "@/components/ui/StatusBadge";
import axios from "axios";
import { API_URLS, API_PATHS } from "@/config/api";
import {
  FlaskConical,
  MapPin,
  Layers,
  Plus,
  Save,
  Download,
  RefreshCw,
  Leaf,
  Droplets,
  Zap,
  AlertTriangle,
  CheckCircle,
  ArrowLeft,
  ArrowRight,
} from "lucide-react";
import { logger } from "../../../lib/logger";

// ═══════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════

interface NutrientLevel {
  current: number;
  target: number;
  unit: string;
  status: "deficient" | "low" | "optimal" | "high" | "excessive";
}

interface ZonePrescription {
  zoneId: string;
  zoneName: string;
  area: number; // hectares
  soilType: string;
  nitrogen: NutrientLevel;
  phosphorus: NutrientLevel;
  potassium: NutrientLevel;
  recommendedFertilizer: string;
  applicationRate: number; // kg/ha
  applicationMethod: string;
  estimatedCost: number;
  priority: "high" | "medium" | "low";
}

interface FertilizerPrescription {
  id: string;
  fieldId: string;
  fieldName: string;
  farmName: string;
  cropType: string;
  cropStage: string;
  totalArea: number;
  zones: ZonePrescription[];
  status: "draft" | "reviewed" | "approved" | "applied";
  createdAt: string;
  createdBy: string;
  soilTestDate: string;
  totalCost: number;
  fertilizerType: string;
}

interface FertilizerProduct {
  id: string;
  name: string;
  nameAr: string;
  type: string;
  nContent: number;
  pContent: number;
  kContent: number;
  unitPrice: number;
  unit: string;
}

// ═══════════════════════════════════════════════════════════════
// Mock Data
// ═══════════════════════════════════════════════════════════════

const MOCK_PRODUCTS: FertilizerProduct[] = [
  { id: "f1", name: "Urea 46%", nameAr: "يوريا 46%", type: "nitrogen", nContent: 46, pContent: 0, kContent: 0, unitPrice: 2.5, unit: "kg" },
  { id: "f2", name: "DAP 18-46-0", nameAr: "داب 18-46-0", type: "compound", nContent: 18, pContent: 46, kContent: 0, unitPrice: 3.8, unit: "kg" },
  { id: "f3", name: "NPK 20-20-20", nameAr: "سماد مركب 20-20-20", type: "compound", nContent: 20, pContent: 20, kContent: 20, unitPrice: 4.2, unit: "kg" },
  { id: "f4", name: "Potassium Chloride", nameAr: "كلوريد البوتاسيوم", type: "potassium", nContent: 0, pContent: 0, kContent: 60, unitPrice: 3.0, unit: "kg" },
  { id: "f5", name: "TSP 46%", nameAr: "سوبر فوسفات ثلاثي", type: "phosphorus", nContent: 0, pContent: 46, kContent: 0, unitPrice: 3.5, unit: "kg" },
];

const MOCK_PRESCRIPTIONS: FertilizerPrescription[] = [
  {
    id: "fp-001",
    fieldId: "FLD-003",
    fieldName: "حقل القمح الشرقي",
    farmName: "مزرعة الوادي",
    cropType: "قمح",
    cropStage: "التفريع",
    totalArea: 8.5,
    status: "draft",
    createdAt: "2026-03-15",
    createdBy: "م. أحمد",
    soilTestDate: "2026-03-10",
    totalCost: 4250,
    fertilizerType: "Urea 46%",
    zones: [
      {
        zoneId: "z1",
        zoneName: "المنطقة الشمالية",
        area: 2.8,
        soilType: "طيني",
        nitrogen: { current: 15, target: 30, unit: "ppm", status: "deficient" },
        phosphorus: { current: 22, target: 25, unit: "ppm", status: "low" },
        potassium: { current: 180, target: 150, unit: "ppm", status: "optimal" },
        recommendedFertilizer: "Urea 46%",
        applicationRate: 55,
        applicationMethod: "بث سطحي",
        estimatedCost: 1540,
        priority: "high",
      },
      {
        zoneId: "z2",
        zoneName: "المنطقة الوسطى",
        area: 3.2,
        soilType: "طيني رملي",
        nitrogen: { current: 20, target: 30, unit: "ppm", status: "low" },
        phosphorus: { current: 28, target: 25, unit: "ppm", status: "optimal" },
        potassium: { current: 140, target: 150, unit: "ppm", status: "low" },
        recommendedFertilizer: "Urea 46%",
        applicationRate: 40,
        applicationMethod: "بث سطحي",
        estimatedCost: 1280,
        priority: "medium",
      },
      {
        zoneId: "z3",
        zoneName: "المنطقة الجنوبية",
        area: 2.5,
        soilType: "رملي",
        nitrogen: { current: 12, target: 30, unit: "ppm", status: "deficient" },
        phosphorus: { current: 18, target: 25, unit: "ppm", status: "low" },
        potassium: { current: 120, target: 150, unit: "ppm", status: "low" },
        recommendedFertilizer: "NPK 20-20-20",
        applicationRate: 65,
        applicationMethod: "حقن مع الري",
        estimatedCost: 1430,
        priority: "high",
      },
    ],
  },
  {
    id: "fp-002",
    fieldId: "FLD-007",
    fieldName: "حقل الطماطم",
    farmName: "مزرعة السهل",
    cropType: "طماطم",
    cropStage: "الإزهار",
    totalArea: 3.2,
    status: "approved",
    createdAt: "2026-03-12",
    createdBy: "م. خالد",
    soilTestDate: "2026-03-08",
    totalCost: 2890,
    fertilizerType: "NPK 20-20-20",
    zones: [
      {
        zoneId: "z1",
        zoneName: "القسم أ",
        area: 1.6,
        soilType: "طيني",
        nitrogen: { current: 25, target: 35, unit: "ppm", status: "low" },
        phosphorus: { current: 30, target: 35, unit: "ppm", status: "low" },
        potassium: { current: 200, target: 180, unit: "ppm", status: "high" },
        recommendedFertilizer: "DAP 18-46-0",
        applicationRate: 45,
        applicationMethod: "حقن مع الري",
        estimatedCost: 1445,
        priority: "medium",
      },
      {
        zoneId: "z2",
        zoneName: "القسم ب",
        area: 1.6,
        soilType: "طيني رملي",
        nitrogen: { current: 22, target: 35, unit: "ppm", status: "low" },
        phosphorus: { current: 20, target: 35, unit: "ppm", status: "deficient" },
        potassium: { current: 160, target: 180, unit: "ppm", status: "low" },
        recommendedFertilizer: "NPK 20-20-20",
        applicationRate: 50,
        applicationMethod: "حقن مع الري",
        estimatedCost: 1445,
        priority: "high",
      },
    ],
  },
];

// ═══════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════

function getNutrientColor(status: NutrientLevel["status"]): string {
  const colors: Record<NutrientLevel["status"], string> = {
    deficient: "text-red-600 dark:text-red-400",
    low: "text-orange-600 dark:text-orange-400",
    optimal: "text-green-600 dark:text-green-400",
    high: "text-blue-600 dark:text-blue-400",
    excessive: "text-purple-600 dark:text-purple-400",
  };
  return colors[status];
}

function getNutrientBgColor(status: NutrientLevel["status"]): string {
  const colors: Record<NutrientLevel["status"], string> = {
    deficient: "bg-red-100 dark:bg-red-900/30",
    low: "bg-orange-100 dark:bg-orange-900/30",
    optimal: "bg-green-100 dark:bg-green-900/30",
    high: "bg-blue-100 dark:bg-blue-900/30",
    excessive: "bg-purple-100 dark:bg-purple-900/30",
  };
  return colors[status];
}

function getNutrientStatusAr(status: NutrientLevel["status"]): string {
  const labels: Record<NutrientLevel["status"], string> = {
    deficient: "ناقص",
    low: "منخفض",
    optimal: "مثالي",
    high: "مرتفع",
    excessive: "مفرط",
  };
  return labels[status];
}

function getPriorityBadge(priority: "high" | "medium" | "low"): { color: string; label: string } {
  const map: Record<string, { color: string; label: string }> = {
    high: { color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400", label: "عالية" },
    medium: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400", label: "متوسطة" },
    low: { color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400", label: "منخفضة" },
  };
  return map[priority] ?? { color: "bg-gray-100 text-gray-700", label: priority };
}

function getNutrientBarWidth(current: number, target: number): number {
  if (target === 0) return 0;
  return Math.min((current / target) * 100, 150);
}

// ═══════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════

export default function FertilizerPrescriptionPage() {
  const [prescriptions, setPrescriptions] = useState<FertilizerPrescription[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPrescription, setSelectedPrescription] = useState<FertilizerPrescription | null>(null);
  const [selectedZone, setSelectedZone] = useState<ZonePrescription | null>(null);
  const [viewMode, setViewMode] = useState<"list" | "detail">("list");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  const loadPrescriptions = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(
        `${API_URLS.advisory}${API_PATHS.advisory.fertilizer}`
      );
      setPrescriptions(response.data?.data ?? response.data ?? []);
    } catch {
      logger.info("Using mock fertilizer prescriptions");
      setPrescriptions(MOCK_PRESCRIPTIONS);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPrescriptions();
  }, [loadPrescriptions]);

  const filteredPrescriptions = filterStatus === "all"
    ? prescriptions
    : prescriptions.filter((p) => p.status === filterStatus);

  const totalZones = prescriptions.reduce((sum, p) => sum + p.zones.length, 0);
  const totalArea = prescriptions.reduce((sum, p) => sum + p.totalArea, 0);
  const totalCost = prescriptions.reduce((sum, p) => sum + p.totalCost, 0);
  const highPriorityZones = prescriptions.reduce(
    (sum, p) => sum + p.zones.filter((z) => z.priority === "high").length,
    0
  );

  function handleSelectPrescription(p: FertilizerPrescription) {
    setSelectedPrescription(p);
    setSelectedZone(p.zones[0] ?? null);
    setViewMode("detail");
  }

  function handleBackToList() {
    setViewMode("list");
    setSelectedPrescription(null);
    setSelectedZone(null);
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Header
        title="وصفات التسميد المتغير"
        subtitle="إدارة وصفات NPK على مستوى المناطق مع توصيات مخصصة لكل منطقة"
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            title="إجمالي الوصفات"
            value={prescriptions.length}
            icon={FlaskConical}
          />
          <StatCard
            title="المناطق"
            value={totalZones}
            icon={Layers}
          />
          <StatCard
            title="المساحة الكلية"
            value={`${totalArea.toFixed(1)} هـ`}
            icon={MapPin}
          />
          <StatCard
            title="التكلفة الإجمالية"
            value={`${totalCost.toLocaleString()} ر.س`}
            icon={Zap}
          />
        </div>

        {highPriorityZones > 0 && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0" />
            <p className="text-sm text-red-700 dark:text-red-300">
              يوجد <strong>{highPriorityZones}</strong> منطقة ذات أولوية عالية تحتاج تسميد عاجل
            </p>
          </div>
        )}

        {viewMode === "list" ? (
          <>
            {/* Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200"
                >
                  <option value="all">جميع الحالات</option>
                  <option value="draft">مسودة</option>
                  <option value="reviewed">مراجَع</option>
                  <option value="approved">معتمد</option>
                  <option value="applied">مطبّق</option>
                </select>
                <button
                  onClick={loadPrescriptions}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  title="تحديث"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
              <button
                disabled
                className="flex items-center gap-2 bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                title="وصفة جديدة (قريبًا)"
              >
                <Plus className="w-4 h-4" />
                وصفة جديدة
              </button>
            </div>

            {/* Prescriptions List */}
            {isLoading ? (
              <div className="flex justify-center py-20">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-600" />
              </div>
            ) : filteredPrescriptions.length === 0 ? (
              <div className="text-center py-16 text-gray-500 dark:text-gray-400">
                <FlaskConical className="w-12 h-12 mx-auto mb-3 opacity-40" />
                <p>لا توجد وصفات تسميد</p>
              </div>
            ) : (
              <div className="grid gap-4">
                {filteredPrescriptions.map((p) => {
                  const deficientZones = p.zones.filter(
                    (z) => z.nitrogen.status === "deficient" || z.phosphorus.status === "deficient" || z.potassium.status === "deficient"
                  ).length;

                  return (
                    <div
                      key={p.id}
                      onClick={() => handleSelectPrescription(p)}
                      className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 hover:shadow-md transition-shadow cursor-pointer"
                    >
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                              {p.fieldName}
                            </h3>
                            <StatusBadge status={p.status} />
                          </div>
                          <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-500 dark:text-gray-400">
                            <span>{p.farmName}</span>
                            <span>المحصول: {p.cropType}</span>
                            <span>المرحلة: {p.cropStage}</span>
                            <span>{p.totalArea} هـ</span>
                            <span>{p.zones.length} مناطق</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-4 text-sm">
                          {deficientZones > 0 && (
                            <span className="flex items-center gap-1 text-red-600 dark:text-red-400 font-medium">
                              <AlertTriangle className="w-4 h-4" />
                              {deficientZones} نقص حاد
                            </span>
                          )}
                          <span className="font-semibold text-gray-900 dark:text-gray-100">
                            {p.totalCost.toLocaleString()} ر.س
                          </span>
                          <ArrowLeft className="w-4 h-4 text-gray-400" />
                        </div>
                      </div>

                      {/* Zone NPK Mini Summary */}
                      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                        {p.zones.map((z) => (
                          <div
                            key={z.zoneId}
                            className="flex items-center gap-2 text-xs bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2"
                          >
                            <span className="font-medium text-gray-700 dark:text-gray-300 truncate">
                              {z.zoneName}
                            </span>
                            <span className={getNutrientColor(z.nitrogen.status)}>N:{z.nitrogen.current}</span>
                            <span className={getNutrientColor(z.phosphorus.status)}>P:{z.phosphorus.current}</span>
                            <span className={getNutrientColor(z.potassium.status)}>K:{z.potassium.current}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        ) : selectedPrescription ? (
          /* Detail View */
          <div className="space-y-6">
            {/* Back + Header */}
            <div className="flex items-center justify-between">
              <button
                onClick={handleBackToList}
                className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
              >
                <ArrowRight className="w-4 h-4" />
                العودة للقائمة
              </button>
              <div className="flex items-center gap-2">
                <button
                  disabled
                  className="flex items-center gap-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 px-3 py-2 rounded-lg text-sm disabled:opacity-40 disabled:cursor-not-allowed"
                  title="تصدير (قريبًا)"
                >
                  <Download className="w-4 h-4" />
                  تصدير
                </button>
                <button
                  disabled
                  className="flex items-center gap-2 bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                  title="حفظ التعديلات (قريبًا)"
                >
                  <Save className="w-4 h-4" />
                  حفظ التعديلات
                </button>
              </div>
            </div>

            {/* Prescription Info */}
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                    {selectedPrescription.fieldName}
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {selectedPrescription.farmName} | {selectedPrescription.cropType} - {selectedPrescription.cropStage}
                  </p>
                </div>
                <StatusBadge status={selectedPrescription.status} />
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-500 dark:text-gray-400">المساحة</span>
                  <p className="font-semibold text-gray-900 dark:text-gray-100">{selectedPrescription.totalArea} هـ</p>
                </div>
                <div>
                  <span className="text-gray-500 dark:text-gray-400">تاريخ فحص التربة</span>
                  <p className="font-semibold text-gray-900 dark:text-gray-100">{selectedPrescription.soilTestDate}</p>
                </div>
                <div>
                  <span className="text-gray-500 dark:text-gray-400">التكلفة الإجمالية</span>
                  <p className="font-semibold text-gray-900 dark:text-gray-100">{selectedPrescription.totalCost.toLocaleString()} ر.س</p>
                </div>
                <div>
                  <span className="text-gray-500 dark:text-gray-400">أنشأها</span>
                  <p className="font-semibold text-gray-900 dark:text-gray-100">{selectedPrescription.createdBy}</p>
                </div>
              </div>
            </div>

            {/* Zone Selector Tabs */}
            <div className="flex gap-2 overflow-x-auto pb-1">
              {selectedPrescription.zones.map((z) => {
                const priorityBadge = getPriorityBadge(z.priority);
                return (
                  <button
                    key={z.zoneId}
                    onClick={() => setSelectedZone(z)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium border whitespace-nowrap transition-colors ${
                      selectedZone?.zoneId === z.zoneId
                        ? "bg-emerald-50 dark:bg-emerald-900/20 border-emerald-300 dark:border-emerald-700 text-emerald-700 dark:text-emerald-300"
                        : "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700"
                    }`}
                  >
                    <Layers className="w-4 h-4" />
                    {z.zoneName}
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${priorityBadge.color}`}>
                      {priorityBadge.label}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* Selected Zone Detail */}
            {selectedZone && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* NPK Analysis Panel */}
                <div className="lg:col-span-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 space-y-5">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    تحليل NPK — {selectedZone.zoneName}
                  </h3>

                  {/* Nutrient Bars */}
                  {([
                    { key: "nitrogen" as const, label: "النيتروجين (N)", icon: <Leaf className="w-4 h-4" />, barColor: "bg-blue-500" },
                    { key: "phosphorus" as const, label: "الفوسفور (P)", icon: <Zap className="w-4 h-4" />, barColor: "bg-orange-500" },
                    { key: "potassium" as const, label: "البوتاسيوم (K)", icon: <Droplets className="w-4 h-4" />, barColor: "bg-purple-500" },
                  ]).map(({ key, label, icon, barColor }) => {
                    const nutrient = selectedZone[key];
                    const barWidth = getNutrientBarWidth(nutrient.current, nutrient.target);
                    return (
                      <div key={key} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {icon}
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</span>
                          </div>
                          <div className="flex items-center gap-3 text-sm">
                            <span className={`font-semibold ${getNutrientColor(nutrient.status)}`}>
                              {nutrient.current} {nutrient.unit}
                            </span>
                            <span className="text-gray-400">/</span>
                            <span className="text-gray-500 dark:text-gray-400">
                              الهدف: {nutrient.target} {nutrient.unit}
                            </span>
                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getNutrientBgColor(nutrient.status)} ${getNutrientColor(nutrient.status)}`}>
                              {getNutrientStatusAr(nutrient.status)}
                            </span>
                          </div>
                        </div>
                        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden relative">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${barColor}`}
                            style={{ width: `${Math.min(barWidth, 100)}%` }}
                          />
                          {/* Target marker */}
                          <div
                            className="absolute top-0 bottom-0 w-0.5 bg-gray-800 dark:bg-gray-200"
                            style={{ left: "66.7%" }}
                            title={`الهدف: ${nutrient.target} ${nutrient.unit}`}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Zone Info Panel */}
                <div className="space-y-4">
                  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 space-y-3">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">معلومات المنطقة</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">المساحة</span>
                        <span className="font-medium text-gray-900 dark:text-gray-100">{selectedZone.area} هـ</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">نوع التربة</span>
                        <span className="font-medium text-gray-900 dark:text-gray-100">{selectedZone.soilType}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">طريقة التطبيق</span>
                        <span className="font-medium text-gray-900 dark:text-gray-100">{selectedZone.applicationMethod}</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 space-y-3">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">الوصفة الموصى بها</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">السماد</span>
                        <span className="font-medium text-gray-900 dark:text-gray-100">{selectedZone.recommendedFertilizer}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">معدل التطبيق</span>
                        <span className="font-medium text-gray-900 dark:text-gray-100">{selectedZone.applicationRate} كجم/هـ</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">الكمية الإجمالية</span>
                        <span className="font-medium text-gray-900 dark:text-gray-100">
                          {(selectedZone.applicationRate * selectedZone.area).toFixed(0)} كجم
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">التكلفة التقديرية</span>
                        <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                          {selectedZone.estimatedCost.toLocaleString()} ر.س
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Fertilizer Selector */}
                  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 space-y-3">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">تغيير السماد</h4>
                    <select className="w-full text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200">
                      {MOCK_PRODUCTS.map((prod) => (
                        <option key={prod.id} value={prod.id}>
                          {prod.nameAr} (N:{prod.nContent} P:{prod.pContent} K:{prod.kContent})
                        </option>
                      ))}
                    </select>
                    <div className="flex gap-2">
                      <label className="flex-1 text-sm">
                        <span className="text-gray-500 dark:text-gray-400">معدل (كجم/هـ)</span>
                        <input
                          type="number"
                          defaultValue={selectedZone.applicationRate}
                          className="mt-1 w-full text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                        />
                      </label>
                    </div>
                    <button
                      disabled
                      className="w-full flex items-center justify-center gap-2 bg-emerald-600 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                      title="تحديث الوصفة (قريبًا)"
                    >
                      <CheckCircle className="w-4 h-4" />
                      تحديث الوصفة
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* All Zones Summary Table */}
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-gray-200 dark:border-gray-800">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">ملخص جميع المناطق</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th className="text-right px-4 py-3 font-medium text-gray-600 dark:text-gray-400">المنطقة</th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600 dark:text-gray-400">المساحة</th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600 dark:text-gray-400">N</th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600 dark:text-gray-400">P</th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600 dark:text-gray-400">K</th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600 dark:text-gray-400">السماد</th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600 dark:text-gray-400">المعدل</th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600 dark:text-gray-400">التكلفة</th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600 dark:text-gray-400">الأولوية</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                    {selectedPrescription.zones.map((z) => {
                      const priorityBadge = getPriorityBadge(z.priority);
                      return (
                        <tr
                          key={z.zoneId}
                          onClick={() => setSelectedZone(z)}
                          className={`cursor-pointer transition-colors ${
                            selectedZone?.zoneId === z.zoneId
                              ? "bg-emerald-50 dark:bg-emerald-900/10"
                              : "hover:bg-gray-50 dark:hover:bg-gray-800/50"
                          }`}
                        >
                          <td className="px-4 py-3 font-medium text-gray-900 dark:text-gray-100">{z.zoneName}</td>
                          <td className="px-4 py-3 text-gray-600 dark:text-gray-400">{z.area} هـ</td>
                          <td className={`px-4 py-3 font-medium ${getNutrientColor(z.nitrogen.status)}`}>
                            {z.nitrogen.current}
                          </td>
                          <td className={`px-4 py-3 font-medium ${getNutrientColor(z.phosphorus.status)}`}>
                            {z.phosphorus.current}
                          </td>
                          <td className={`px-4 py-3 font-medium ${getNutrientColor(z.potassium.status)}`}>
                            {z.potassium.current}
                          </td>
                          <td className="px-4 py-3 text-gray-600 dark:text-gray-400">{z.recommendedFertilizer}</td>
                          <td className="px-4 py-3 text-gray-600 dark:text-gray-400">{z.applicationRate} كجم/هـ</td>
                          <td className="px-4 py-3 font-medium text-gray-900 dark:text-gray-100">
                            {z.estimatedCost.toLocaleString()} ر.س
                          </td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${priorityBadge.color}`}>
                              {priorityBadge.label}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : null}
      </main>
    </div>
  );
}
