"use client";

import React, { useState, useMemo } from "react";
import {
  Radio,
  Search,
  Wifi,
  WifiOff,
  Battery,
  Thermometer,
  Droplets,
  Wind,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import { useSensors, useSensorStats } from "@/features/iot";
import type { Sensor, SensorType, SensorStatus } from "@/features/iot";
import { useRouter } from "next/navigation";

const sensorTypeConfig: Record<string, { icon: React.ReactNode; label: string; labelAr: string }> = {
  soil_moisture: { icon: <Droplets className="w-5 h-5" />, label: "Soil Moisture", labelAr: "رطوبة التربة" },
  temperature: { icon: <Thermometer className="w-5 h-5" />, label: "Temperature", labelAr: "الحرارة" },
  humidity: { icon: <Droplets className="w-5 h-5" />, label: "Humidity", labelAr: "الرطوبة" },
  wind: { icon: <Wind className="w-5 h-5" />, label: "Wind", labelAr: "الرياح" },
  rain: { icon: <Droplets className="w-5 h-5" />, label: "Rain", labelAr: "الأمطار" },
  ph: { icon: <Radio className="w-5 h-5" />, label: "pH", labelAr: "الحموضة" },
  light: { icon: <Radio className="w-5 h-5" />, label: "Light", labelAr: "الإضاءة" },
  pressure: { icon: <Radio className="w-5 h-5" />, label: "Pressure", labelAr: "الضغط" },
};

export default function SensorsClient() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");

  const { data: sensors = [], isLoading, error } = useSensors();
  const { data: stats } = useSensorStats();

  const filteredSensors = useMemo(() => {
    return sensors.filter((sensor: Sensor) => {
      const matchesSearch =
        !searchTerm ||
        sensor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        sensor.nameAr.includes(searchTerm);
      const matchesStatus = statusFilter === "all" || sensor.status === statusFilter;
      const matchesType = typeFilter === "all" || sensor.type === typeFilter;
      return matchesSearch && matchesStatus && matchesType;
    });
  }, [sensors, searchTerm, statusFilter, typeFilter]);

  const getStatusBadge = (status: SensorStatus) => {
    const styles: Record<string, string> = {
      online: "bg-green-100 text-green-800",
      active: "bg-green-100 text-green-800",
      offline: "bg-red-100 text-red-800",
      inactive: "bg-red-100 text-red-800",
      error: "bg-red-100 text-red-800",
      maintenance: "bg-blue-100 text-blue-800",
    };
    const labels: Record<string, string> = {
      online: "متصل",
      active: "نشط",
      offline: "غير متصل",
      inactive: "غير نشط",
      error: "خطأ",
      maintenance: "صيانة",
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || "bg-gray-100 text-gray-800"}`}>
        {labels[status] || status}
      </span>
    );
  };

  const getStatusIcon = (status: SensorStatus) => {
    if (status === "online" || status === "active") return <Wifi className="w-4 h-4 text-green-500" />;
    if (status === "offline" || status === "inactive") return <WifiOff className="w-4 h-4 text-red-500" />;
    return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
  };

  const getBatteryColor = (level: number) => {
    if (level > 50) return "text-green-600";
    if (level > 20) return "text-yellow-600";
    return "text-red-600";
  };

  const onlineCount = stats?.online ?? sensors.filter((s: Sensor) => s.status === "online" || s.status === "active").length;
  const offlineCount = stats?.offline ?? sensors.filter((s: Sensor) => s.status === "offline" || s.status === "inactive").length;
  const warningCount = stats?.warning ?? sensors.filter((s: Sensor) => s.status === "error" || s.status === "maintenance").length;
  const lowBatteryCount = sensors.filter((s: Sensor) => (s.battery ?? 100) < 20).length;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-sahool-green-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">فشل في تحميل بيانات الحساسات</p>
          <p className="text-gray-500 text-sm">Failed to load sensor data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">مراقبة الحساسات</h1>
          <p className="text-gray-500 mt-1">Sensors Monitoring</p>
        </div>
      </div>

      {/* Alerts */}
      {(offlineCount > 0 || warningCount > 0) && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <span className="font-medium text-amber-800">
              تنبيه: {offlineCount} حساس غير متصل، {warningCount} يحتاج اهتمام
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Radio className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي الحساسات</div>
              <div className="text-xl font-bold text-gray-900">{stats?.total ?? sensors.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Wifi className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متصل</div>
              <div className="text-xl font-bold text-green-600">{onlineCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <WifiOff className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">غير متصل</div>
              <div className="text-xl font-bold text-red-600">{offlineCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Battery className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">بطارية منخفضة</div>
              <div className="text-xl font-bold text-yellow-600">{lowBatteryCount}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث عن حساس..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          <option value="all">جميع الحالات</option>
          <option value="online">متصل</option>
          <option value="offline">غير متصل</option>
          <option value="error">خطأ</option>
          <option value="maintenance">صيانة</option>
        </select>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          <option value="all">جميع الأنواع</option>
          <option value="soil_moisture">رطوبة التربة</option>
          <option value="temperature">الحرارة</option>
          <option value="humidity">الرطوبة</option>
          <option value="wind">الرياح</option>
        </select>
      </div>

      {/* Sensors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSensors.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">
            لا توجد حساسات
          </div>
        ) : (
          filteredSensors.map((sensor: Sensor) => (
            <div
              key={sensor.id}
              className={`bg-white rounded-lg border p-4 hover:shadow-md transition-shadow ${
                sensor.status === "offline" || sensor.status === "inactive" ? "border-red-200" : ""
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    sensor.status === "online" || sensor.status === "active" ? "bg-green-100 text-green-600" :
                    sensor.status === "offline" || sensor.status === "inactive" ? "bg-red-100 text-red-600" :
                    "bg-yellow-100 text-yellow-600"
                  }`}>
                    {sensorTypeConfig[sensor.type]?.icon ?? <Radio className="w-5 h-5" />}
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{sensor.nameAr}</h3>
                    <p className="text-sm text-gray-500">{sensor.location?.fieldName || sensor.name}</p>
                  </div>
                </div>
                {getStatusIcon(sensor.status)}
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">القراءة الأخيرة</span>
                  <span className="text-lg font-bold text-gray-900">
                    {sensor.lastReading ? `${sensor.lastReading.value}${sensor.lastReading.unit}` : "—"}
                  </span>
                </div>
                {sensor.battery != null && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">البطارية</span>
                    <span className={`text-sm font-medium ${getBatteryColor(sensor.battery)}`}>
                      {sensor.battery}%
                    </span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">الحالة</span>
                  {getStatusBadge(sensor.status)}
                </div>
              </div>

              <div className="mt-4 pt-4 border-t flex justify-between items-center">
                <span className="text-xs text-gray-400">
                  {sensor.lastReading?.timestamp
                    ? `آخر تحديث: ${new Date(sensor.lastReading.timestamp).toLocaleTimeString("ar-SA")}`
                    : ""}
                </span>
                <button
                  onClick={() => router.push(`/iot?sensor=${sensor.id}`)}
                  className="text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium"
                >
                  التفاصيل
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
