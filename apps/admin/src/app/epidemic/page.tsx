"use client";

// Epidemic Monitoring Center - مركز رصد الأوبئة
// Advanced disease outbreak monitoring with heatmap visualization

import { useEffect, useState, useMemo } from "react";
import Header from "@/components/layout/Header";
import StatCard from "@/components/ui/StatCard";
import DataTable from "@/components/ui/DataTable";
import { fetchDiagnoses, fetchDiagnosisStats } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { DiagnosisRecord } from "@/types";
import { logger } from "../../lib/logger";
import {
  Bug,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  MapPin,
  Activity,
  BarChart3,
  RefreshCw,
  Filter,
} from "lucide-react";

// Yemen Governorates with coordinates
const GOVERNORATES = [
  { id: "sanaa", name: "صنعاء", lat: 15.3694, lng: 44.191, color: "#ef4444" },
  { id: "aden", name: "عدن", lat: 12.7797, lng: 45.0187, color: "#f97316" },
  { id: "taiz", name: "تعز", lat: 13.5789, lng: 44.0219, color: "#eab308" },
  { id: "ibb", name: "إب", lat: 13.9759, lng: 44.1709, color: "#22c55e" },
  {
    id: "hodeidah",
    name: "الحديدة",
    lat: 14.7979,
    lng: 42.954,
    color: "#3b82f6",
  },
  {
    id: "hadramaut",
    name: "حضرموت",
    lat: 15.9329,
    lng: 49.3929,
    color: "#8b5cf6",
  },
  { id: "dhamar", name: "ذمار", lat: 14.5426, lng: 44.4051, color: "#ec4899" },
  { id: "marib", name: "مأرب", lat: 15.4542, lng: 45.3269, color: "#06b6d4" },
  { id: "hajjah", name: "حجة", lat: 15.6917, lng: 43.6028, color: "#14b8a6" },
  { id: "saadah", name: "صعدة", lat: 16.941, lng: 43.764, color: "#f43f5e" },
  { id: "shabwah", name: "شبوة", lat: 14.5333, lng: 47.0167, color: "#a855f7" },
  { id: "lahij", name: "لحج", lat: 13.0578, lng: 44.8831, color: "#84cc16" },
];

interface EpidemicStats {
  total: number;
  pending: number;
  confirmed: number;
  treated: number;
  criticalCount: number;
  highCount: number;
  byDisease: Record<string, number>;
  byGovernorate: Record<string, number>;
}

export default function EpidemicCenterPage() {
  const [diagnoses, setDiagnoses] = useState<DiagnosisRecord[]>([]);
  const [stats, setStats] = useState<EpidemicStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedGovernorate, setSelectedGovernorate] = useState<string | null>(
    null,
  );
  const [timeRange, setTimeRange] = useState<"day" | "week" | "month">("week");

  useEffect(() => {
    loadData();
  }, [timeRange]);

  async function loadData() {
    setIsLoading(true);
    try {
      const [diagnosesData, statsData] = await Promise.all([
        fetchDiagnoses({ limit: 100 }),
        fetchDiagnosisStats(),
      ]);
      setDiagnoses(diagnosesData);
      setStats(statsData);
    } catch (error) {
      logger.error("Failed to load epidemic data:", error);
    } finally {
      setIsLoading(false);
    }
  }

  // Calculate governorate statistics
  const governorateStats = useMemo(() => {
    const statsMap: Record<
      string,
      { total: number; critical: number; high: number }
    > = {};

    GOVERNORATES.forEach((gov) => {
      statsMap[gov.id] = { total: 0, critical: 0, high: 0 };
    });

    diagnoses.forEach((d) => {
      // Try to match governorate from diagnosis
      // Type assertion needed as governorate might be optional in some diagnosis types
      const diagnosisWithGov = d as typeof d & { governorate?: string };
      const govName = diagnosisWithGov.governorate?.toLowerCase() || "";
      const gov = GOVERNORATES.find(
        (g) => g.id === govName || g.name.includes(govName),
      );

      const govStat = gov ? statsMap[gov.id] : undefined;
      if (govStat) {
        govStat.total++;
        if (d.severity === "critical") govStat.critical++;
        if (d.severity === "high") govStat.high++;
      }
    });

    return statsMap;
  }, [diagnoses]);

  // Top diseases
  const topDiseases = useMemo(() => {
    if (!stats?.byDisease) return [];
    return Object.entries(stats.byDisease)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5);
  }, [stats]);

  // Alert level calculation
  const getAlertLevel = (govId: string) => {
    const govStats = governorateStats[govId];
    if (!govStats) return "safe";
    if (govStats.critical > 0) return "critical";
    if (govStats.high > 2) return "high";
    if (govStats.total > 5) return "medium";
    return "safe";
  };

  const alertColors = {
    critical: "bg-red-500",
    high: "bg-orange-500",
    medium: "bg-yellow-500",
    safe: "bg-green-500",
  };

  return (
    <div className="p-6">
      <Header
        title="مركز رصد الأوبئة"
        subtitle="المراقبة المتقدمة لانتشار الأمراض في اليمن"
      />

      {/* Quick Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard
          title="إجمالي الحالات"
          value={stats?.total || 0}
          icon={Activity}
          iconColor="text-blue-600"
        />

        <StatCard
          title="حالات حرجة"
          value={stats?.criticalCount || 0}
          icon={AlertTriangle}
          iconColor="text-red-600"
        />

        <StatCard
          title="خطورة عالية"
          value={stats?.highCount || 0}
          icon={TrendingUp}
          iconColor="text-orange-600"
        />

        <StatCard
          title="قيد المراجعة"
          value={stats?.pending || 0}
          icon={Bug}
          iconColor="text-amber-600"
        />

        <StatCard
          title="تم العلاج"
          value={stats?.treated || 0}
          icon={TrendingDown}
          iconColor="text-green-600"
        />

        <StatCard
          title="محافظات متأثرة"
          value={
            Object.values(governorateStats).filter((g) => g.total > 0).length
          }
          icon={MapPin}
          iconColor="text-purple-600"
        />
      </div>

      {/* Time Range Filter */}
      <div className="mt-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <span className="text-sm text-gray-600">الفترة الزمنية:</span>
          <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
            {[
              { key: "day" as const, label: "اليوم" },
              { key: "week" as const, label: "الأسبوع" },
              { key: "month" as const, label: "الشهر" },
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setTimeRange(key)}
                className={cn(
                  "px-3 py-1 text-sm rounded-md transition-colors",
                  timeRange === key
                    ? "bg-white text-sahool-700 shadow-sm"
                    : "text-gray-600 hover:text-gray-900",
                )}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={loadData}
          className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <RefreshCw className={cn("w-4 h-4", isLoading && "animate-spin")} />
          تحديث
        </button>
      </div>

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Governorates Map (Simplified) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-100 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-sahool-600" />
            خريطة انتشار الأمراض
          </h3>

          {/* Simplified Governorate Grid */}
          <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
            {GOVERNORATES.map((gov) => {
              const govStats = governorateStats[gov.id];
              const alertLevel = getAlertLevel(gov.id);
              const isSelected = selectedGovernorate === gov.id;

              return (
                <button
                  key={gov.id}
                  onClick={() =>
                    setSelectedGovernorate(isSelected ? null : gov.id)
                  }
                  className={cn(
                    "relative p-4 rounded-xl border-2 transition-all text-right",
                    isSelected
                      ? "border-sahool-500 bg-sahool-50"
                      : "border-gray-100 hover:border-gray-200 bg-white",
                  )}
                >
                  {/* Alert Indicator */}
                  <div
                    className={cn(
                      "absolute top-2 left-2 w-3 h-3 rounded-full",
                      alertColors[alertLevel],
                    )}
                  />

                  <p className="font-bold text-gray-900">{gov.name}</p>
                  <p
                    className="text-2xl font-bold mt-1"
                    style={{ color: gov.color }}
                  >
                    {govStats?.total || 0}
                  </p>
                  <p className="text-xs text-gray-500">حالة</p>

                  {(govStats?.critical ?? 0) > 0 && (
                    <div className="mt-2 flex items-center gap-1 text-xs text-red-600">
                      <AlertTriangle className="w-3 h-3" />
                      {govStats?.critical ?? 0} حرج
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Legend */}
          <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span>حرج</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-orange-500" />
              <span>مرتفع</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <span>متوسط</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span>آمن</span>
            </div>
          </div>
        </div>

        {/* Top Diseases Sidebar */}
        <div className="bg-white rounded-xl border border-gray-100 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-sahool-600" />
            أكثر الأمراض انتشاراً
          </h3>

          <div className="space-y-4">
            {topDiseases.length > 0 ? (
              topDiseases.map(([disease, count], index) => {
                const maxCount = topDiseases[0]?.[1] ?? 1;
                const percentage = (count / maxCount) * 100;

                return (
                  <div key={disease}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">
                        {disease}
                      </span>
                      <span className="text-sm text-gray-500">{count}</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={cn(
                          "h-full rounded-full transition-all",
                          index === 0
                            ? "bg-red-500"
                            : index === 1
                              ? "bg-orange-500"
                              : index === 2
                                ? "bg-yellow-500"
                                : "bg-blue-500",
                        )}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Bug className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>لا توجد بيانات</p>
              </div>
            )}
          </div>

          {/* Selected Governorate Details */}
          {selectedGovernorate && (
            <div className="mt-6 pt-6 border-t border-gray-100">
              <h4 className="font-bold text-gray-900 mb-3">
                {GOVERNORATES.find((g) => g.id === selectedGovernorate)?.name}
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">إجمالي الحالات:</span>
                  <span className="font-medium">
                    {governorateStats[selectedGovernorate]?.total || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">حالات حرجة:</span>
                  <span className="font-medium text-red-600">
                    {governorateStats[selectedGovernorate]?.critical || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">خطورة عالية:</span>
                  <span className="font-medium text-orange-600">
                    {governorateStats[selectedGovernorate]?.high || 0}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recent Critical Cases */}
      <div className="mt-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          الحالات الحرجة الأخيرة
        </h3>

        <DataTable
          columns={[
            {
              key: "severity",
              header: "الحالة",
              render: (d: DiagnosisRecord) => (
                <div className="flex items-center gap-2">
                  <div
                    className={cn(
                      "w-3 h-3 rounded-full",
                      d.severity === "critical"
                        ? "bg-red-500"
                        : "bg-orange-500",
                    )}
                  />
                  <span className="font-medium">
                    {d.severity === "critical" ? "حرج" : "عالي"}
                  </span>
                </div>
              ),
            },
            {
              key: "diseaseNameAr",
              header: "المرض",
              render: (d: DiagnosisRecord) => (
                <div>
                  <p className="font-medium text-gray-900">{d.diseaseNameAr}</p>
                  <p className="text-xs text-gray-500">{d.diseaseName}</p>
                </div>
              ),
            },
            {
              key: "farmName",
              header: "المزرعة",
            },
            {
              key: "confidence",
              header: "دقة التشخيص",
              render: (d: DiagnosisRecord) => (
                <div className="flex items-center gap-2">
                  <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500 rounded-full"
                      style={{ width: `${d.confidence}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">
                    {d.confidence.toFixed(0)}%
                  </span>
                </div>
              ),
            },
            {
              key: "diagnosedAt",
              header: "التاريخ",
              render: (d: DiagnosisRecord) => (
                <span className="text-sm text-gray-500">
                  {new Date(d.diagnosedAt).toLocaleDateString("ar-YE")}
                </span>
              ),
            },
          ]}
          data={diagnoses
            .filter((d) => d.severity === "critical" || d.severity === "high")
            .slice(0, 10)}
          keyExtractor={(d) => d.id}
          isLoading={isLoading}
          emptyMessage="لا توجد حالات حرجة حالياً"
        />
      </div>
    </div>
  );
}
