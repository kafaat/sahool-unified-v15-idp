"use client";

// Spray Management - Optimal Application Windows
// إدارة الرش - نوافذ التطبيق المثلى

import { useEffect, useState } from "react";
import Header from "@/components/layout/Header";
import StatCard from "@/components/ui/StatCard";
import { fetchSprayWindows, fetchSprayHistory } from "@/lib/api/precision";
import {
  Droplet,
  Wind,
  CheckCircle,
  Clock,
  TrendingUp,
  Sun,
} from "lucide-react";
import { formatDate } from "@/lib/utils";
import { logger } from "../../../lib/logger";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

interface SprayWindow {
  id: string;
  farmId: string;
  farmName: string;
  fieldName: string;
  cropType: string;
  productType: "pesticide" | "herbicide" | "fungicide" | "fertilizer";
  productName: string;
  windowStart: string;
  windowEnd: string;
  optimalTime: string;
  status: "upcoming" | "optimal" | "missed" | "completed";
  conditions: {
    temperature: number;
    windSpeed: number;
    humidity: number;
    precipitation: number;
  };
  recommendations: string[];
  recommendationsAr: string[];
}

interface SprayHistory {
  id: string;
  farmName: string;
  fieldName: string;
  productType: string;
  productName: string;
  appliedAt: string;
  area: number;
  quantity: number;
  cost: number;
  effectiveness: number;
}

const CHART_COLORS = {
  primary: "#2E7D32",
  secondary: "#4CAF50",
  accent: "#81C784",
  warning: "#FF9800",
};

const PIE_COLORS = ["#2E7D32", "#4CAF50", "#81C784", "#A5D6A7"];

export default function SprayPage() {
  const [windows, setWindows] = useState<SprayWindow[]>([]);
  const [history, setHistory] = useState<SprayHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"windows" | "history">("windows");

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setIsLoading(true);
    try {
      const [windowsData, historyData] = await Promise.all([
        fetchSprayWindows(),
        fetchSprayHistory({ limit: 20 }),
      ]);
      setWindows(windowsData);
      setHistory(historyData);
    } catch (error) {
      logger.error("Failed to load spray data:", error);
    } finally {
      setIsLoading(false);
    }
  }

  const stats = {
    upcoming: windows.filter((w) => w.status === "upcoming").length,
    optimal: windows.filter((w) => w.status === "optimal").length,
    completed: windows.filter((w) => w.status === "completed").length,
    totalCost: history.reduce((sum, h) => sum + h.cost, 0),
  };

  const productUsage = history.reduce(
    (acc, h) => {
      const type = h.productType;
      if (!acc[type]) {
        acc[type] = { type, quantity: 0, cost: 0 };
      }
      acc[type].quantity += h.quantity;
      acc[type].cost += h.cost;
      return acc;
    },
    {} as Record<string, { type: string; quantity: number; cost: number }>,
  );

  const productUsageData = Object.values(productUsage);

  const productTypeLabels: Record<string, string> = {
    pesticide: "مبيدات حشرية",
    herbicide: "مبيدات أعشاب",
    fungicide: "مبيدات فطرية",
    fertilizer: "أسمدة",
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      upcoming: "bg-blue-100 text-blue-700",
      optimal: "bg-green-100 text-green-700",
      missed: "bg-red-100 text-red-700",
      completed: "bg-gray-100 text-gray-700",
    };
    return colors[status] || "bg-gray-100 text-gray-700";
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      upcoming: "قادم",
      optimal: "مثالي الآن",
      missed: "فات الموعد",
      completed: "مكتمل",
    };
    return labels[status] || status;
  };

  return (
    <div className="p-6">
      <Header
        title="إدارة الرش الذكي"
        subtitle="Smart Spray Management - نوافذ التطبيق المثلى وتتبع الاستخدام"
      />

      {/* Statistics Cards */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="نوافذ قادمة"
          value={stats.upcoming}
          icon={Clock}
          iconColor="text-blue-600"
        />
        <StatCard
          title="مثالي الآن"
          value={stats.optimal}
          icon={CheckCircle}
          iconColor="text-green-600"
        />
        <StatCard
          title="تم الإكمال"
          value={stats.completed}
          icon={Droplet}
          iconColor="text-purple-600"
        />
        <StatCard
          title="التكلفة الإجمالية"
          value={`$${stats.totalCost.toFixed(2)}`}
          icon={TrendingUp}
          iconColor="text-yellow-600"
        />
      </div>

      {/* Tabs */}
      <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="border-b border-gray-100">
          <div className="flex">
            <button
              onClick={() => setActiveTab("windows")}
              className={`px-6 py-3 font-medium text-sm transition-colors ${
                activeTab === "windows"
                  ? "text-sahool-600 border-b-2 border-sahool-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              نوافذ الرش القادمة
            </button>
            <button
              onClick={() => setActiveTab("history")}
              className={`px-6 py-3 font-medium text-sm transition-colors ${
                activeTab === "history"
                  ? "text-sahool-600 border-b-2 border-sahool-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              سجل الرش
            </button>
          </div>
        </div>

        {/* Windows Tab Content */}
        {activeTab === "windows" && (
          <div className="p-6">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="w-8 h-8 border-4 border-sahool-600 border-t-transparent rounded-full animate-spin"></div>
              </div>
            ) : windows.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                لا توجد نوافذ رش متاحة
              </div>
            ) : (
              <div className="space-y-4">
                {windows.map((window) => (
                  <div
                    key={window.id}
                    className="border border-gray-100 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="font-bold text-gray-900">
                          {window.farmName}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {window.fieldName} - {window.cropType}
                        </p>
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(window.status)}`}
                      >
                        {getStatusLabel(window.status)}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <p className="text-xs text-gray-500 mb-1">المنتج</p>
                        <p className="font-medium text-gray-900 text-sm">
                          {window.productName}
                        </p>
                        <p className="text-xs text-gray-500">
                          {productTypeLabels[window.productType]}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 mb-1">
                          الوقت المثالي
                        </p>
                        <p className="font-medium text-gray-900 text-sm">
                          {formatDate(window.optimalTime)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 mb-1">الحرارة</p>
                        <div className="flex items-center gap-1">
                          <Sun className="w-4 h-4 text-yellow-500" />
                          <span className="font-medium text-gray-900 text-sm">
                            {window.conditions.temperature}°C
                          </span>
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 mb-1">الرياح</p>
                        <div className="flex items-center gap-1">
                          <Wind className="w-4 h-4 text-blue-500" />
                          <span className="font-medium text-gray-900 text-sm">
                            {window.conditions.windSpeed} km/h
                          </span>
                        </div>
                      </div>
                    </div>

                    {window.recommendationsAr.length > 0 && (
                      <div className="bg-blue-50 rounded-lg p-3">
                        <p className="text-xs font-medium text-blue-900 mb-2">
                          توصيات:
                        </p>
                        <ul className="text-xs text-blue-700 space-y-1">
                          {window.recommendationsAr.map((rec, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-blue-400">•</span>
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* History Tab Content */}
        {activeTab === "history" && (
          <div className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              {/* Product Usage Chart */}
              <div className="lg:col-span-2">
                <h3 className="font-bold text-gray-900 mb-4">
                  استخدام المنتجات
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={productUsageData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis
                        dataKey="type"
                        tick={{ fontSize: 11 }}
                        tickFormatter={(value) =>
                          productTypeLabels[value] || value
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
                      />
                      <Bar
                        dataKey="quantity"
                        fill={CHART_COLORS.primary}
                        radius={[4, 4, 0, 0]}
                        name="الكمية (لتر)"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Cost Distribution */}
              <div>
                <h3 className="font-bold text-gray-900 mb-4">توزيع التكاليف</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={productUsageData}
                        dataKey="cost"
                        nameKey="type"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        label={({ type, percent }) =>
                          `${productTypeLabels[type]} ${((percent || 0) * 100).toFixed(0)}%`
                        }
                        labelLine={false}
                      >
                        {productUsageData.map((_entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={PIE_COLORS[index % PIE_COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* History Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      المزرعة / الحقل
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      المنتج
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      المساحة
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      الكمية
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      التكلفة
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      الفعالية
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      التاريخ
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {history.map((record) => (
                    <tr
                      key={record.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-4 py-3">
                        <div>
                          <p className="font-medium text-gray-900 text-sm">
                            {record.farmName}
                          </p>
                          <p className="text-xs text-gray-500">
                            {record.fieldName}
                          </p>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div>
                          <p className="font-medium text-gray-900 text-sm">
                            {record.productName}
                          </p>
                          <p className="text-xs text-gray-500">
                            {productTypeLabels[record.productType]}
                          </p>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {record.area.toFixed(1)} هكتار
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {record.quantity.toFixed(1)} لتر
                      </td>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        ${record.cost.toFixed(2)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-green-500 rounded-full"
                              style={{ width: `${record.effectiveness}%` }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-600">
                            {record.effectiveness}%
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {formatDate(record.appliedAt)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
