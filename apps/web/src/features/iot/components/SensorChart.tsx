/**
 * SensorChart Component
 * مخطط قراءات المستشعر
 */

"use client";

import React, { useMemo } from "react";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { TrendingUp, TrendingDown, Activity } from "lucide-react";
import type { SensorReading } from "../types";

interface SensorChartProps {
  readings: SensorReading[];
  sensorType: string;
  sensorUnit: string;
  sensorUnitAr: string;
  chartType?: "line" | "area";
  showStats?: boolean;
}

export const SensorChart: React.FC<SensorChartProps> = ({
  readings,
  sensorType,
  sensorUnit,
  sensorUnitAr,
  chartType = "area",
  showStats = true,
}) => {
  // Prepare chart data
  const chartData = useMemo(() => {
    return readings
      .map((reading) => ({
        time: new Date(reading.timestamp).toLocaleTimeString("ar-SA", {
          hour: "2-digit",
          minute: "2-digit",
        }),
        value: reading.value,
        timestamp: reading.timestamp,
      }))
      .reverse(); // Most recent first in readings, but chart should show chronologically
  }, [readings]);

  // Calculate statistics
  const stats = useMemo(() => {
    if (readings.length === 0) {
      return { current: 0, average: 0, min: 0, max: 0, trend: 0 };
    }

    const values = readings.map((r) => r.value);
    const current = values[0]; // Most recent reading
    const average = values.reduce((sum, v) => sum + v, 0) / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);

    // Calculate trend (comparing first half vs second half)
    const mid = Math.floor(values.length / 2);
    const firstHalf = values.slice(0, mid);
    const secondHalf = values.slice(mid);
    const firstAvg =
      firstHalf.reduce((sum, v) => sum + v, 0) / firstHalf.length;
    const secondAvg =
      secondHalf.reduce((sum, v) => sum + v, 0) / secondHalf.length;
    const trend = ((secondAvg - firstAvg) / firstAvg) * 100;

    return { current, average, min, max, trend };
  }, [readings]);

  // Get color based on sensor type
  const getColor = () => {
    switch (sensorType) {
      case "temperature":
        return "#ef4444"; // red
      case "humidity":
        return "#3b82f6"; // blue
      case "soil_moisture":
        return "#10b981"; // green
      case "ph":
        return "#8b5cf6"; // purple
      case "light":
        return "#f59e0b"; // amber
      default:
        return "#6366f1"; // indigo
    }
  };

  const color = getColor();

  if (readings.length === 0) {
    return (
      <div className="bg-white rounded-xl border-2 border-gray-200 p-8">
        <div className="text-center py-8">
          <Activity className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="text-gray-500">
            لا توجد قراءات متاحة | No readings available
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-6 space-y-6">
      {/* Statistics */}
      {showStats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {/* Current */}
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-600 mb-1">الحالي | Current</p>
            <p className="text-xl font-bold" style={{ color }}>
              {stats.current!.toFixed(2)}
              <span className="text-sm text-gray-600 mr-1">{sensorUnitAr}</span>
            </p>
          </div>

          {/* Average */}
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-600 mb-1">المتوسط | Average</p>
            <p className="text-xl font-bold text-gray-900">
              {stats.average.toFixed(2)}
              <span className="text-sm text-gray-600 mr-1">{sensorUnitAr}</span>
            </p>
          </div>

          {/* Min */}
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-600 mb-1">الأدنى | Min</p>
            <p className="text-xl font-bold text-blue-600">
              {stats.min.toFixed(2)}
              <span className="text-sm text-gray-600 mr-1">{sensorUnitAr}</span>
            </p>
          </div>

          {/* Max */}
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-600 mb-1">الأعلى | Max</p>
            <p className="text-xl font-bold text-red-600">
              {stats.max.toFixed(2)}
              <span className="text-sm text-gray-600 mr-1">{sensorUnitAr}</span>
            </p>
          </div>

          {/* Trend */}
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-600 mb-1">الاتجاه | Trend</p>
            <div className="flex items-center gap-1">
              {stats.trend > 0 ? (
                <TrendingUp className="w-5 h-5 text-green-600" />
              ) : stats.trend < 0 ? (
                <TrendingDown className="w-5 h-5 text-red-600" />
              ) : (
                <Activity className="w-5 h-5 text-gray-400" />
              )}
              <p
                className={`text-xl font-bold ${
                  stats.trend > 0
                    ? "text-green-600"
                    : stats.trend < 0
                      ? "text-red-600"
                      : "text-gray-600"
                }`}
              >
                {stats.trend > 0 ? "+" : ""}
                {stats.trend.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === "area" ? (
            <AreaChart data={chartData}>
              <defs>
                <linearGradient
                  id={`gradient-${sensorType}`}
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={color} stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="time"
                stroke="#6b7280"
                style={{ fontSize: "12px" }}
                tickLine={false}
              />
              <YAxis
                stroke="#6b7280"
                style={{ fontSize: "12px" }}
                tickLine={false}
                label={{
                  value: `${sensorUnitAr} (${sensorUnit})`,
                  angle: -90,
                  position: "insideLeft",
                  style: { fontSize: "12px", fill: "#6b7280" },
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "white",
                  border: "2px solid #e5e7eb",
                  borderRadius: "8px",
                  fontSize: "14px",
                }}
                labelStyle={{ fontWeight: "bold", marginBottom: "4px" }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={2}
                fill={`url(#gradient-${sensorType})`}
                name={`${sensorUnitAr} (${sensorUnit})`}
              />
            </AreaChart>
          ) : (
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="time"
                stroke="#6b7280"
                style={{ fontSize: "12px" }}
                tickLine={false}
              />
              <YAxis
                stroke="#6b7280"
                style={{ fontSize: "12px" }}
                tickLine={false}
                label={{
                  value: `${sensorUnitAr} (${sensorUnit})`,
                  angle: -90,
                  position: "insideLeft",
                  style: { fontSize: "12px", fill: "#6b7280" },
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "white",
                  border: "2px solid #e5e7eb",
                  borderRadius: "8px",
                  fontSize: "14px",
                }}
                labelStyle={{ fontWeight: "bold", marginBottom: "4px" }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={2}
                dot={{ fill: color, r: 4 }}
                activeDot={{ r: 6 }}
                name={`${sensorUnitAr} (${sensorUnit})`}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Time Range Info */}
      {chartData.length > 0 && (
        <div className="text-center text-sm text-gray-500">
          {chartData.length} قراءة من {chartData[0]!.time} إلى{" "}
          {chartData[chartData.length - 1]!.time}
        </div>
      )}
    </div>
  );
};

export default SensorChart;
