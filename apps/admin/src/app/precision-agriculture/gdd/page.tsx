"use client";

// GDD (Growing Degree Days) Monitoring
// مراقبة درجات النمو الحرارية

import { useEffect, useState } from "react";
import Header from "@/components/layout/Header";
import StatCard from "@/components/ui/StatCard";
import { fetchGDDData } from "@/lib/api/precision";
import {
  Thermometer,
  Sprout,
  AlertTriangle,
  TrendingUp,
  Calendar,
  MapPin,
  Clock,
} from "lucide-react";
import { formatDate } from "@/lib/utils";
import { logger } from "../../../lib/logger";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

interface GDDField {
  id: string;
  farmId: string;
  farmName: string;
  fieldName: string;
  cropType: string;
  plantingDate: string;
  currentGDD: number;
  targetGDD: number;
  currentStage: string;
  currentStageAr: string;
  nextStage: string;
  nextStageAr: string;
  daysToNextStage: number;
  gddToNextStage: number;
  alerts: Array<{
    type: "info" | "warning" | "critical";
    message: string;
    messageAr: string;
  }>;
  history: Array<{
    date: string;
    gdd: number;
    temp_min: number;
    temp_max: number;
  }>;
}

const CHART_COLORS = {
  primary: "#2E7D32",
  secondary: "#4CAF50",
  accent: "#81C784",
  warning: "#FF9800",
};

export default function GDDPage() {
  const [fields, setFields] = useState<GDDField[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedField, setSelectedField] = useState<GDDField | null>(null);

  useEffect(() => {
    loadGDDData();
  }, []);

  async function loadGDDData() {
    setIsLoading(true);
    try {
      const data = await fetchGDDData();
      setFields(data);
      if (data.length > 0) {
        const firstField = data[0];
        if (firstField) {
          setSelectedField(firstField);
        }
      }
    } catch (error) {
      logger.error("Failed to load GDD data:", error);
    } finally {
      setIsLoading(false);
    }
  }

  const stats = {
    totalFields: fields.length,
    activeMonitoring: fields.length,
    criticalAlerts: fields.filter((f) =>
      f.alerts.some((a) => a.type === "critical"),
    ).length,
    nearTransition: fields.filter((f) => f.daysToNextStage <= 7).length,
  };

  const stageDistribution = fields.reduce(
    (acc, field) => {
      const stage = field.currentStageAr;
      acc[stage] = (acc[stage] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>,
  );

  const stageData = Object.entries(stageDistribution).map(([stage, count]) => ({
    stage,
    count,
  }));

  return (
    <div className="p-6">
      <Header
        title="مراقبة درجات النمو الحرارية (GDD)"
        subtitle="Growing Degree Days Monitoring - تتبع مراحل نمو المحاصيل"
      />

      {/* Statistics Cards */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="إجمالي الحقول"
          value={stats.totalFields}
          icon={MapPin}
          iconColor="text-blue-600"
        />
        <StatCard
          title="قيد المراقبة"
          value={stats.activeMonitoring}
          icon={Thermometer}
          iconColor="text-green-600"
        />
        <StatCard
          title="تنبيهات حرجة"
          value={stats.criticalAlerts}
          icon={AlertTriangle}
          iconColor="text-red-600"
        />
        <StatCard
          title="قرب الانتقال"
          value={stats.nearTransition}
          icon={Clock}
          iconColor="text-yellow-600"
        />
      </div>

      {/* Stage Distribution Chart */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="font-bold text-gray-900 mb-4">توزيع مراحل النمو</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stageData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis
                  dataKey="stage"
                  type="category"
                  tick={{ fontSize: 11 }}
                  width={80}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#fff",
                    border: "1px solid #e0e0e0",
                    borderRadius: "8px",
                    direction: "rtl",
                  }}
                />
                <Bar
                  dataKey="count"
                  fill={CHART_COLORS.primary}
                  radius={[0, 4, 4, 0]}
                  name="عدد الحقول"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* GDD History Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900">تاريخ GDD</h3>
            {selectedField && (
              <select
                value={selectedField.id}
                onChange={(e) => {
                  const field = fields.find((f) => f.id === e.target.value);
                  if (field) setSelectedField(field);
                }}
                className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sahool-500"
              >
                {fields.map((field) => (
                  <option key={field.id} value={field.id}>
                    {field.farmName} - {field.fieldName}
                  </option>
                ))}
              </select>
            )}
          </div>
          {selectedField && (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={selectedField.history}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 11 }}
                    tickFormatter={(value) =>
                      new Date(value).toLocaleDateString("ar-YE", {
                        month: "short",
                        day: "numeric",
                      })
                    }
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#fff",
                      border: "1px solid #e0e0e0",
                      borderRadius: "8px",
                      direction: "rtl",
                    }}
                    labelFormatter={(value) => formatDate(value)}
                  />
                  <Line
                    type="monotone"
                    dataKey="gdd"
                    stroke={CHART_COLORS.primary}
                    strokeWidth={2}
                    dot={{ fill: CHART_COLORS.primary }}
                    name="GDD التراكمي"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Fields List */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {isLoading ? (
          <div className="col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
            <div className="flex items-center justify-center">
              <div className="w-8 h-8 border-4 border-sahool-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
          </div>
        ) : fields.length === 0 ? (
          <div className="col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center text-gray-500">
            لا توجد حقول قيد المراقبة
          </div>
        ) : (
          fields.map((field) => (
            <div
              key={field.id}
              className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow"
            >
              {/* Field Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-bold text-gray-900">{field.farmName}</h3>
                  <p className="text-sm text-gray-500">
                    {field.fieldName} - {field.cropType}
                  </p>
                </div>
                <Sprout className="w-6 h-6 text-sahool-600" />
              </div>

              {/* GDD Progress */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">تقدم GDD</span>
                  <span className="text-sm font-bold text-gray-900">
                    {field.currentGDD.toFixed(0)} / {field.targetGDD.toFixed(0)}
                  </span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-sahool-600 rounded-full transition-all"
                    style={{
                      width: `${Math.min((field.currentGDD / field.targetGDD) * 100, 100)}%`,
                    }}
                  ></div>
                </div>
              </div>

              {/* Current Stage */}
              <div className="grid grid-cols-2 gap-4 mb-4 p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-xs text-gray-500 mb-1">المرحلة الحالية</p>
                  <p className="font-medium text-gray-900">
                    {field.currentStageAr}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">المرحلة القادمة</p>
                  <p className="font-medium text-gray-900">
                    {field.nextStageAr}
                  </p>
                </div>
              </div>

              {/* Next Stage Info */}
              <div className="flex items-center gap-4 text-sm mb-4">
                <div className="flex items-center gap-1 text-gray-600">
                  <Calendar className="w-4 h-4" />
                  <span>{field.daysToNextStage} يوم متبقي</span>
                </div>
                <div className="flex items-center gap-1 text-gray-600">
                  <TrendingUp className="w-4 h-4" />
                  <span>{field.gddToNextStage.toFixed(0)} GDD متبقي</span>
                </div>
              </div>

              {/* Alerts */}
              {field.alerts.length > 0 && (
                <div className="space-y-2">
                  {field.alerts.map((alert, index) => (
                    <div
                      key={index}
                      className={`flex items-start gap-2 p-2 rounded-lg text-sm ${
                        alert.type === "critical"
                          ? "bg-red-50 text-red-700"
                          : alert.type === "warning"
                            ? "bg-yellow-50 text-yellow-700"
                            : "bg-blue-50 text-blue-700"
                      }`}
                    >
                      <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>{alert.messageAr}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
