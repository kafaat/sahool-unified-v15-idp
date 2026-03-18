"use client";

// Fleet GPS Tracking Page
// صفحة تتبع الأسطول بنظام GPS

import React, { useState, useMemo, useCallback } from "react";
import Header from "@/components/layout/Header";
import StatCard from "@/components/ui/StatCard";
import { cn } from "@/lib/utils";
import {
  Tractor,
  Plane,
  Droplets,
  SprayCan,
  Truck,
  Wrench,
  MapPin,
  Gauge,
  Fuel,
  Clock,
  Activity,
  ChevronRight,
  X,
  RefreshCw,
  Filter,
  AlertTriangle,
  CheckCircle2,
  PauseCircle,
  WifiOff,
  Navigation,
  Thermometer,
  Battery,
  Shield,
  Calendar,
  BarChart3,
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// أنواع البيانات
// ═══════════════════════════════════════════════════════════════════════════

type EquipmentType = "tractor" | "drone" | "harvester" | "sprayer" | "pump" | "vehicle";
type FleetStatus = "active" | "idle" | "maintenance" | "offline";

interface GpsPosition {
  lat: number;
  lon: number;
  timestamp: string;
  speed_kmh: number;
}

interface MaintenanceItem {
  task: string;
  taskAr: string;
  dueDate: string;
  priority: "high" | "medium" | "low";
}

interface GeofenceAlert {
  id: string;
  message: string;
  messageAr: string;
  timestamp: string;
  type: "entry" | "exit" | "speed";
}

interface FleetItem {
  id: string;
  name: string;
  nameAr: string;
  type: EquipmentType;
  status: FleetStatus;
  lat: number;
  lon: number;
  speed_kmh: number;
  fuel_pct: number;
  fuelType: "diesel" | "electric" | "gasoline";
  lastUpdate: string;
  assignedField: string | null;
  currentTask: string | null;
  currentTaskAr: string | null;
  engineTemp?: number;
  engineHours: number;
  locationHistory: GpsPosition[];
  maintenanceSchedule: MaintenanceItem[];
  geofenceAlerts: GeofenceAlert[];
}

// ═══════════════════════════════════════════════════════════════════════════
// Mock Fleet Data
// بيانات الأسطول التجريبية
// ═══════════════════════════════════════════════════════════════════════════

const MOCK_FLEET: FleetItem[] = [
  {
    id: "EQ-001",
    name: "Al-Rashid Field Tractor",
    nameAr: "جرار حقل الرشيد",
    type: "tractor",
    status: "active",
    lat: 24.7123,
    lon: 46.6745,
    speed_kmh: 8,
    fuel_pct: 75,
    fuelType: "diesel",
    lastUpdate: "منذ دقيقتين",
    assignedField: "Field-001",
    currentTask: "Plowing",
    currentTaskAr: "حراثة الأرض",
    engineTemp: 87,
    engineHours: 1240,
    locationHistory: [
      { lat: 24.7120, lon: 46.6742, timestamp: "09:00", speed_kmh: 7 },
      { lat: 24.7121, lon: 46.6743, timestamp: "09:15", speed_kmh: 8 },
      { lat: 24.7122, lon: 46.6744, timestamp: "09:30", speed_kmh: 9 },
      { lat: 24.7122, lon: 46.6744, timestamp: "09:45", speed_kmh: 8 },
      { lat: 24.7123, lon: 46.6745, timestamp: "10:00", speed_kmh: 8 },
    ],
    maintenanceSchedule: [
      { task: "Oil Change", taskAr: "تغيير الزيت", dueDate: "2026-04-01", priority: "medium" },
      { task: "Filter Replacement", taskAr: "تغيير الفلتر", dueDate: "2026-05-15", priority: "low" },
    ],
    geofenceAlerts: [
      { id: "gf-1", message: "Entered Field-001 zone", messageAr: "دخول منطقة الحقل-001", timestamp: "08:30", type: "entry" },
    ],
  },
  {
    id: "EQ-002",
    name: "North Drone",
    nameAr: "طائرة مسيّرة الشمال",
    type: "drone",
    status: "active",
    lat: 24.7890,
    lon: 46.7012,
    speed_kmh: 35,
    fuel_pct: 45,
    fuelType: "electric",
    lastUpdate: "منذ 30 ثانية",
    assignedField: "Field-003",
    currentTask: "NDVI Scan",
    currentTaskAr: "مسح NDVI",
    engineTemp: 42,
    engineHours: 320,
    locationHistory: [
      { lat: 24.7870, lon: 46.6990, timestamp: "09:10", speed_kmh: 30 },
      { lat: 24.7875, lon: 46.6995, timestamp: "09:15", speed_kmh: 32 },
      { lat: 24.7880, lon: 46.7000, timestamp: "09:20", speed_kmh: 35 },
      { lat: 24.7885, lon: 46.7005, timestamp: "09:25", speed_kmh: 36 },
      { lat: 24.7890, lon: 46.7012, timestamp: "09:30", speed_kmh: 35 },
    ],
    maintenanceSchedule: [
      { task: "Battery Check", taskAr: "فحص البطارية", dueDate: "2026-03-25", priority: "high" },
      { task: "Propeller Inspection", taskAr: "فحص المروحة", dueDate: "2026-04-10", priority: "medium" },
    ],
    geofenceAlerts: [
      { id: "gf-2", message: "Entered Field-003 airspace", messageAr: "دخول مجال الحقل-003 الجوي", timestamp: "09:05", type: "entry" },
    ],
  },
  {
    id: "EQ-003",
    name: "East Farm Harvester",
    nameAr: "حصّادة المزرعة الشرقية",
    type: "harvester",
    status: "idle",
    lat: 24.6543,
    lon: 46.6234,
    speed_kmh: 0,
    fuel_pct: 90,
    fuelType: "diesel",
    lastUpdate: "منذ 45 دقيقة",
    assignedField: null,
    currentTask: null,
    currentTaskAr: null,
    engineTemp: 35,
    engineHours: 2850,
    locationHistory: [
      { lat: 24.6543, lon: 46.6234, timestamp: "08:00", speed_kmh: 0 },
      { lat: 24.6543, lon: 46.6234, timestamp: "08:15", speed_kmh: 0 },
      { lat: 24.6543, lon: 46.6234, timestamp: "08:30", speed_kmh: 0 },
      { lat: 24.6543, lon: 46.6234, timestamp: "08:45", speed_kmh: 0 },
      { lat: 24.6543, lon: 46.6234, timestamp: "09:00", speed_kmh: 0 },
    ],
    maintenanceSchedule: [
      { task: "Blade Sharpening", taskAr: "شحذ الشفرات", dueDate: "2026-04-20", priority: "medium" },
    ],
    geofenceAlerts: [],
  },
  {
    id: "EQ-004",
    name: "Pesticide Sprayer",
    nameAr: "مرش المبيدات",
    type: "sprayer",
    status: "active",
    lat: 24.7234,
    lon: 46.6890,
    speed_kmh: 5,
    fuel_pct: 60,
    fuelType: "diesel",
    lastUpdate: "منذ دقيقة",
    assignedField: "Field-002",
    currentTask: "Pesticide Application",
    currentTaskAr: "رش المبيدات",
    engineTemp: 75,
    engineHours: 680,
    locationHistory: [
      { lat: 24.7230, lon: 46.6886, timestamp: "09:00", speed_kmh: 5 },
      { lat: 24.7231, lon: 46.6887, timestamp: "09:15", speed_kmh: 5 },
      { lat: 24.7232, lon: 46.6888, timestamp: "09:30", speed_kmh: 4 },
      { lat: 24.7233, lon: 46.6889, timestamp: "09:45", speed_kmh: 5 },
      { lat: 24.7234, lon: 46.6890, timestamp: "10:00", speed_kmh: 5 },
    ],
    maintenanceSchedule: [
      { task: "Nozzle Cleaning", taskAr: "تنظيف الفوهات", dueDate: "2026-03-30", priority: "high" },
      { task: "Tank Inspection", taskAr: "فحص الخزان", dueDate: "2026-04-15", priority: "medium" },
    ],
    geofenceAlerts: [
      { id: "gf-3", message: "Speed limit exceeded briefly", messageAr: "تجاوز حد السرعة مؤقتاً", timestamp: "09:20", type: "speed" },
    ],
  },
  {
    id: "EQ-005",
    name: "Main Irrigation Pump",
    nameAr: "مضخة الري الرئيسية",
    type: "pump",
    status: "active",
    lat: 24.7456,
    lon: 46.7123,
    speed_kmh: 0,
    fuel_pct: 100,
    fuelType: "electric",
    lastUpdate: "منذ 5 دقائق",
    assignedField: "Field-001",
    currentTask: "Irrigation",
    currentTaskAr: "ري الحقول",
    engineTemp: 55,
    engineHours: 4200,
    locationHistory: [
      { lat: 24.7456, lon: 46.7123, timestamp: "06:00", speed_kmh: 0 },
      { lat: 24.7456, lon: 46.7123, timestamp: "07:00", speed_kmh: 0 },
      { lat: 24.7456, lon: 46.7123, timestamp: "08:00", speed_kmh: 0 },
      { lat: 24.7456, lon: 46.7123, timestamp: "09:00", speed_kmh: 0 },
      { lat: 24.7456, lon: 46.7123, timestamp: "10:00", speed_kmh: 0 },
    ],
    maintenanceSchedule: [
      { task: "Bearing Replacement", taskAr: "تغيير المحامل", dueDate: "2026-06-01", priority: "low" },
    ],
    geofenceAlerts: [],
  },
  {
    id: "EQ-006",
    name: "Transport Truck",
    nameAr: "شاحنة النقل",
    type: "vehicle",
    status: "maintenance",
    lat: 24.7000,
    lon: 46.6500,
    speed_kmh: 0,
    fuel_pct: 30,
    fuelType: "diesel",
    lastUpdate: "منذ 3 ساعات",
    assignedField: null,
    currentTask: null,
    currentTaskAr: null,
    engineTemp: 25,
    engineHours: 87500,
    locationHistory: [
      { lat: 24.7000, lon: 46.6500, timestamp: "07:00", speed_kmh: 0 },
      { lat: 24.7000, lon: 46.6500, timestamp: "07:30", speed_kmh: 0 },
      { lat: 24.7000, lon: 46.6500, timestamp: "08:00", speed_kmh: 0 },
      { lat: 24.7000, lon: 46.6500, timestamp: "08:30", speed_kmh: 0 },
      { lat: 24.7000, lon: 46.6500, timestamp: "09:00", speed_kmh: 0 },
    ],
    maintenanceSchedule: [
      { task: "Brake System Repair", taskAr: "إصلاح نظام الفرامل", dueDate: "2026-03-20", priority: "high" },
      { task: "Tire Replacement", taskAr: "تغيير الإطارات", dueDate: "2026-03-22", priority: "high" },
      { task: "Engine Tune-up", taskAr: "ضبط المحرك", dueDate: "2026-03-25", priority: "medium" },
    ],
    geofenceAlerts: [],
  },
  {
    id: "EQ-007",
    name: "Plowing Tractor",
    nameAr: "جرار الحراثة",
    type: "tractor",
    status: "offline",
    lat: 24.6800,
    lon: 46.6300,
    speed_kmh: 0,
    fuel_pct: 15,
    fuelType: "diesel",
    lastUpdate: "منذ يوم",
    assignedField: null,
    currentTask: null,
    currentTaskAr: null,
    engineTemp: 22,
    engineHours: 3100,
    locationHistory: [
      { lat: 24.6800, lon: 46.6300, timestamp: "يوم أمس 10:00", speed_kmh: 0 },
      { lat: 24.6800, lon: 46.6300, timestamp: "يوم أمس 12:00", speed_kmh: 0 },
      { lat: 24.6800, lon: 46.6300, timestamp: "يوم أمس 14:00", speed_kmh: 0 },
      { lat: 24.6800, lon: 46.6300, timestamp: "يوم أمس 16:00", speed_kmh: 0 },
      { lat: 24.6800, lon: 46.6300, timestamp: "يوم أمس 18:00", speed_kmh: 0 },
    ],
    maintenanceSchedule: [
      { task: "Full Service", taskAr: "صيانة شاملة", dueDate: "2026-04-05", priority: "medium" },
      { task: "Fuel Refill", taskAr: "تعبئة وقود", dueDate: "2026-03-19", priority: "high" },
    ],
    geofenceAlerts: [],
  },
  {
    id: "EQ-008",
    name: "Pivot Sprinkler",
    nameAr: "رشاش محوري",
    type: "sprayer",
    status: "active",
    lat: 24.7600,
    lon: 46.7200,
    speed_kmh: 2,
    fuel_pct: 80,
    fuelType: "electric",
    lastUpdate: "منذ دقيقة",
    assignedField: "Field-004",
    currentTask: "Pivot Irrigation",
    currentTaskAr: "ري محوري",
    engineTemp: 48,
    engineHours: 950,
    locationHistory: [
      { lat: 24.7592, lon: 46.7192, timestamp: "08:00", speed_kmh: 2 },
      { lat: 24.7594, lon: 46.7195, timestamp: "08:30", speed_kmh: 2 },
      { lat: 24.7596, lon: 46.7197, timestamp: "09:00", speed_kmh: 2 },
      { lat: 24.7598, lon: 46.7199, timestamp: "09:30", speed_kmh: 2 },
      { lat: 24.7600, lon: 46.7200, timestamp: "10:00", speed_kmh: 2 },
    ],
    maintenanceSchedule: [
      { task: "Pivot Arm Lubrication", taskAr: "تزييت ذراع المحور", dueDate: "2026-04-30", priority: "low" },
    ],
    geofenceAlerts: [
      { id: "gf-4", message: "Operating within Field-004 boundary", messageAr: "تشغيل داخل حدود الحقل-004", timestamp: "07:55", type: "entry" },
    ],
  },
];

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// دوال مساعدة
// ═══════════════════════════════════════════════════════════════════════════

function getTypeIcon(type: EquipmentType, className = "w-5 h-5") {
  switch (type) {
    case "tractor":
      return <Tractor className={className} />;
    case "drone":
      return <Plane className={className} />;
    case "harvester":
      return <Tractor className={className} />;
    case "sprayer":
      return <SprayCan className={className} />;
    case "pump":
      return <Droplets className={className} />;
    case "vehicle":
      return <Truck className={className} />;
    default:
      return <Wrench className={className} />;
  }
}

function getTypeLabel(type: EquipmentType): string {
  const labels: Record<EquipmentType, string> = {
    tractor: "جرار",
    drone: "طائرة مسيّرة",
    harvester: "حصّادة",
    sprayer: "رشاش",
    pump: "مضخة",
    vehicle: "مركبة",
  };
  return labels[type] ?? type;
}

function getTypeColors(type: EquipmentType): { bg: string; text: string; iconBg: string } {
  const map: Record<EquipmentType, { bg: string; text: string; iconBg: string }> = {
    tractor:   { bg: "bg-blue-50 dark:bg-blue-900/20",   text: "text-blue-700 dark:text-blue-300",   iconBg: "bg-blue-100 dark:bg-blue-800/50 text-blue-600 dark:text-blue-300" },
    drone:     { bg: "bg-emerald-50 dark:bg-emerald-900/20", text: "text-emerald-700 dark:text-emerald-300", iconBg: "bg-emerald-100 dark:bg-emerald-800/50 text-emerald-600 dark:text-emerald-300" },
    harvester: { bg: "bg-amber-50 dark:bg-amber-900/20",  text: "text-amber-700 dark:text-amber-300",  iconBg: "bg-amber-100 dark:bg-amber-800/50 text-amber-600 dark:text-amber-300" },
    sprayer:   { bg: "bg-purple-50 dark:bg-purple-900/20", text: "text-purple-700 dark:text-purple-300", iconBg: "bg-purple-100 dark:bg-purple-800/50 text-purple-600 dark:text-purple-300" },
    pump:      { bg: "bg-cyan-50 dark:bg-cyan-900/20",    text: "text-cyan-700 dark:text-cyan-300",    iconBg: "bg-cyan-100 dark:bg-cyan-800/50 text-cyan-600 dark:text-cyan-300" },
    vehicle:   { bg: "bg-gray-50 dark:bg-gray-800/50",   text: "text-gray-700 dark:text-gray-300",   iconBg: "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300" },
  };
  return map[type] ?? map.vehicle;
}

interface StatusConfig {
  label: string;
  dotClass: string;
  badgeClass: string;
  icon: React.ReactNode;
}

function getStatusConfig(status: FleetStatus): StatusConfig {
  switch (status) {
    case "active":
      return {
        label: "نشط",
        dotClass: "bg-green-500 animate-pulse",
        badgeClass: "text-green-700 dark:text-green-300 bg-green-100 dark:bg-green-900/40",
        icon: <CheckCircle2 className="w-3 h-3" />,
      };
    case "idle":
      return {
        label: "خامل",
        dotClass: "bg-yellow-400",
        badgeClass: "text-yellow-700 dark:text-yellow-300 bg-yellow-100 dark:bg-yellow-900/40",
        icon: <PauseCircle className="w-3 h-3" />,
      };
    case "maintenance":
      return {
        label: "صيانة",
        dotClass: "bg-orange-500",
        badgeClass: "text-orange-700 dark:text-orange-300 bg-orange-100 dark:bg-orange-900/40",
        icon: <AlertTriangle className="w-3 h-3" />,
      };
    case "offline":
      return {
        label: "غير متصل",
        dotClass: "bg-red-500",
        badgeClass: "text-red-700 dark:text-red-300 bg-red-100 dark:bg-red-900/40",
        icon: <WifiOff className="w-3 h-3" />,
      };
    default:
      return {
        label: status,
        dotClass: "bg-gray-400",
        badgeClass: "text-gray-700 bg-gray-100",
        icon: null,
      };
  }
}

function getFuelBarColor(pct: number, type: "diesel" | "electric" | "gasoline"): string {
  if (type === "electric") return "bg-cyan-500";
  if (pct >= 60) return "bg-green-500";
  if (pct >= 30) return "bg-yellow-500";
  return "bg-red-500";
}

function getPriorityConfig(priority: "high" | "medium" | "low") {
  switch (priority) {
    case "high":
      return { label: "عاجل", class: "text-red-700 dark:text-red-300 bg-red-100 dark:bg-red-900/40" };
    case "medium":
      return { label: "متوسط", class: "text-yellow-700 dark:text-yellow-300 bg-yellow-100 dark:bg-yellow-900/40" };
    case "low":
      return { label: "منخفض", class: "text-green-700 dark:text-green-300 bg-green-100 dark:bg-green-900/40" };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Sub-components
// المكونات الفرعية
// ═══════════════════════════════════════════════════════════════════════════

interface FleetCardProps {
  item: FleetItem;
  isSelected: boolean;
  onClick: () => void;
}

function FleetCard({ item, isSelected, onClick }: FleetCardProps) {
  const status = getStatusConfig(item.status);
  const colors = getTypeColors(item.type);
  const fuelColor = getFuelBarColor(item.fuel_pct, item.fuelType);

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "w-full text-right rounded-xl border p-4 transition-all hover:shadow-md cursor-pointer",
        isSelected
          ? "border-sahool-500 ring-2 ring-sahool-500/30 bg-sahool-50 dark:bg-sahool-900/20"
          : "border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-200 dark:hover:border-gray-600"
      )}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-3 min-w-0 flex-1">
          {/* Type icon */}
          <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0", colors.iconBg)}>
            {getTypeIcon(item.type)}
          </div>
          {/* Name & type */}
          <div className="min-w-0 text-right">
            <p className="font-semibold text-gray-900 dark:text-gray-100 text-sm truncate">{item.nameAr}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">{item.id} · {getTypeLabel(item.type)}</p>
          </div>
        </div>

        {/* Status badge */}
        <div className="flex items-center gap-1.5 flex-shrink-0">
          <span
            className={cn(
              "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium",
              status.badgeClass
            )}
          >
            <span className={cn("w-1.5 h-1.5 rounded-full flex-shrink-0", status.dotClass)} />
            {status.label}
          </span>
        </div>
      </div>

      {/* Location row */}
      <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400 mb-2">
        <MapPin className="w-3 h-3 flex-shrink-0" />
        <span dir="ltr" className="font-mono">
          {item.lat.toFixed(4)}, {item.lon.toFixed(4)}
        </span>
        {item.assignedField && (
          <>
            <span>·</span>
            <span className="text-sahool-600 dark:text-sahool-400">{item.assignedField}</span>
          </>
        )}
      </div>

      {/* Telemetry row */}
      <div className="flex items-center gap-4 mb-3">
        {/* Speed */}
        <div className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-300">
          <Gauge className="w-3 h-3" />
          <span>{item.speed_kmh} كم/س</span>
        </div>
        {/* Last update */}
        <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
          <Clock className="w-3 h-3" />
          <span>{item.lastUpdate}</span>
        </div>
        {/* Task */}
        {item.currentTaskAr && (
          <div className="flex items-center gap-1 text-xs text-sahool-600 dark:text-sahool-400">
            <Activity className="w-3 h-3" />
            <span className="truncate">{item.currentTaskAr}</span>
          </div>
        )}
      </div>

      {/* Fuel gauge */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
            {item.fuelType === "electric" ? (
              <Battery className="w-3 h-3" />
            ) : (
              <Fuel className="w-3 h-3" />
            )}
            {item.fuelType === "electric" ? "شحن" : "وقود"}
          </span>
          <span
            className={cn(
              "text-xs font-medium",
              item.fuel_pct >= 60
                ? "text-green-600 dark:text-green-400"
                : item.fuel_pct >= 30
                  ? "text-yellow-600 dark:text-yellow-400"
                  : "text-red-600 dark:text-red-400"
            )}
          >
            {item.fuel_pct}%
          </span>
        </div>
        <div className="h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className={cn("h-full rounded-full transition-all", fuelColor)}
            style={{ width: `${item.fuel_pct}%` }}
          />
        </div>
      </div>
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────
// Detail Panel
// لوحة التفاصيل
// ─────────────────────────────────────────────────────────────────

interface DetailPanelProps {
  item: FleetItem;
  onClose: () => void;
}

function DetailPanel({ item, onClose }: DetailPanelProps) {
  const status = getStatusConfig(item.status);
  const colors = getTypeColors(item.type);
  const fuelColor = getFuelBarColor(item.fuel_pct, item.fuelType);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 flex flex-col h-full overflow-hidden">
      {/* Panel header */}
      <div className="flex items-start justify-between p-4 border-b border-gray-100 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0", colors.iconBg)}>
            {getTypeIcon(item.type, "w-6 h-6")}
          </div>
          <div>
            <h3 className="font-bold text-gray-900 dark:text-gray-100">{item.nameAr}</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">{item.id} · {item.name}</p>
          </div>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          aria-label="إغلاق"
        >
          <X className="w-4 h-4 text-gray-500 dark:text-gray-400" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Status & Task */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">الحالة</p>
            <span className={cn("inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium", status.badgeClass)}>
              {status.icon}
              {status.label}
            </span>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">المهمة الحالية</p>
            <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
              {item.currentTaskAr ?? "لا توجد مهمة"}
            </p>
          </div>
        </div>

        {/* Live Telemetry */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-sahool-600 dark:text-sahool-400" />
            بيانات حية
          </h4>
          <div className="grid grid-cols-2 gap-2">
            {/* Speed */}
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
              <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400 mb-1">
                <Gauge className="w-3 h-3" />
                <span className="text-xs">السرعة</span>
              </div>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                {item.speed_kmh}
                <span className="text-xs font-normal text-gray-500 dark:text-gray-400 mr-1">كم/س</span>
              </p>
            </div>
            {/* Engine temp */}
            {item.engineTemp != null && (
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
                <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400 mb-1">
                  <Thermometer className="w-3 h-3" />
                  <span className="text-xs">حرارة المحرك</span>
                </div>
                <p className={cn(
                  "text-lg font-bold",
                  item.engineTemp > 100 ? "text-red-600 dark:text-red-400" : "text-gray-900 dark:text-gray-100"
                )}>
                  {item.engineTemp}
                  <span className="text-xs font-normal text-gray-500 dark:text-gray-400 mr-1">°م</span>
                </p>
              </div>
            )}
            {/* Engine hours */}
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
              <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400 mb-1">
                <Clock className="w-3 h-3" />
                <span className="text-xs">ساعات التشغيل</span>
              </div>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                {item.engineHours.toLocaleString("ar-SA")}
                <span className="text-xs font-normal text-gray-500 dark:text-gray-400 mr-1">س</span>
              </p>
            </div>
            {/* Last update */}
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
              <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400 mb-1">
                <Navigation className="w-3 h-3" />
                <span className="text-xs">آخر تحديث</span>
              </div>
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{item.lastUpdate}</p>
            </div>
          </div>

          {/* Fuel */}
          <div className="mt-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400">
                {item.fuelType === "electric" ? (
                  <Battery className="w-3 h-3" />
                ) : (
                  <Fuel className="w-3 h-3" />
                )}
                <span className="text-xs">
                  {item.fuelType === "electric" ? "مستوى الشحن" : "مستوى الوقود"}
                </span>
              </div>
              <span
                className={cn(
                  "text-sm font-bold",
                  item.fuel_pct >= 60
                    ? "text-green-600 dark:text-green-400"
                    : item.fuel_pct >= 30
                      ? "text-yellow-600 dark:text-yellow-400"
                      : "text-red-600 dark:text-red-400"
                )}
              >
                {item.fuel_pct}%
              </span>
            </div>
            <div className="h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
              <div
                className={cn("h-full rounded-full transition-all", fuelColor)}
                style={{ width: `${item.fuel_pct}%` }}
              />
            </div>
          </div>
        </div>

        {/* Location History */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-1.5">
            <MapPin className="w-4 h-4 text-sahool-600 dark:text-sahool-400" />
            سجل المواقع (آخر 5 نقاط)
          </h4>
          <div className="space-y-1.5">
            {item.locationHistory.map((pos, idx) => (
              <div
                key={idx}
                className={cn(
                  "flex items-center justify-between rounded-lg px-3 py-2 text-xs",
                  idx === item.locationHistory.length - 1
                    ? "bg-sahool-50 dark:bg-sahool-900/20 border border-sahool-200 dark:border-sahool-700"
                    : "bg-gray-50 dark:bg-gray-700/40"
                )}
              >
                <div className="flex items-center gap-2">
                  <span
                    className={cn(
                      "w-2 h-2 rounded-full flex-shrink-0",
                      idx === item.locationHistory.length - 1
                        ? "bg-sahool-500"
                        : "bg-gray-300 dark:bg-gray-600"
                    )}
                  />
                  <span className="text-gray-600 dark:text-gray-400">{pos.timestamp}</span>
                </div>
                <span dir="ltr" className="font-mono text-gray-700 dark:text-gray-300">
                  {pos.lat.toFixed(4)}, {pos.lon.toFixed(4)}
                </span>
                <span className="text-gray-500 dark:text-gray-400">{pos.speed_kmh} كم/س</span>
              </div>
            ))}
          </div>
        </div>

        {/* Maintenance Schedule */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-1.5">
            <Calendar className="w-4 h-4 text-sahool-600 dark:text-sahool-400" />
            جدول الصيانة
          </h4>
          {item.maintenanceSchedule.length === 0 ? (
            <p className="text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/40 rounded-lg px-3 py-2">
              لا توجد مهام صيانة مجدولة
            </p>
          ) : (
            <div className="space-y-1.5">
              {item.maintenanceSchedule.map((task, idx) => {
                const priority = getPriorityConfig(task.priority);
                return (
                  <div
                    key={idx}
                    className="flex items-center justify-between bg-gray-50 dark:bg-gray-700/40 rounded-lg px-3 py-2"
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      <Wrench className="w-3 h-3 text-gray-400 flex-shrink-0" />
                      <span className="text-xs text-gray-700 dark:text-gray-300 truncate">{task.taskAr}</span>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="text-xs text-gray-500 dark:text-gray-400">{task.dueDate}</span>
                      <span className={cn("px-1.5 py-0.5 rounded text-xs font-medium", priority.class)}>
                        {priority.label}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Geofence Alerts */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-1.5">
            <Shield className="w-4 h-4 text-sahool-600 dark:text-sahool-400" />
            تنبيهات السياج الجغرافي
          </h4>
          {item.geofenceAlerts.length === 0 ? (
            <p className="text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/40 rounded-lg px-3 py-2">
              لا توجد تنبيهات
            </p>
          ) : (
            <div className="space-y-1.5">
              {item.geofenceAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={cn(
                    "flex items-start justify-between rounded-lg px-3 py-2 text-xs",
                    alert.type === "speed"
                      ? "bg-orange-50 dark:bg-orange-900/20"
                      : "bg-blue-50 dark:bg-blue-900/20"
                  )}
                >
                  <div className="flex items-start gap-2 min-w-0">
                    <AlertTriangle
                      className={cn(
                        "w-3 h-3 mt-0.5 flex-shrink-0",
                        alert.type === "speed"
                          ? "text-orange-500"
                          : "text-blue-500"
                      )}
                    />
                    <span
                      className={cn(
                        "truncate",
                        alert.type === "speed"
                          ? "text-orange-700 dark:text-orange-300"
                          : "text-blue-700 dark:text-blue-300"
                      )}
                    >
                      {alert.messageAr}
                    </span>
                  </div>
                  <span className="text-gray-500 dark:text-gray-400 flex-shrink-0 mr-2">{alert.timestamp}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Main Page Component
// المكون الرئيسي للصفحة
// ═══════════════════════════════════════════════════════════════════════════

export default function FleetTrackingPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Derived data
  const stats = useMemo(() => {
    const total = MOCK_FLEET.length;
    const active = MOCK_FLEET.filter((e) => e.status === "active").length;
    const maintenance = MOCK_FLEET.filter((e) => e.status === "maintenance").length;
    const avgUtil = Math.round(
      (MOCK_FLEET.filter((e) => e.status === "active").length / MOCK_FLEET.length) * 100
    );
    return { total, active, maintenance, avgUtil };
  }, []);

  const filteredFleet = useMemo(() => {
    return MOCK_FLEET.filter((item) => {
      if (typeFilter && item.type !== typeFilter) return false;
      if (statusFilter && item.status !== statusFilter) return false;
      return true;
    });
  }, [typeFilter, statusFilter]);

  const selectedItem = useMemo(
    () => MOCK_FLEET.find((e) => e.id === selectedId) ?? null,
    [selectedId]
  );

  const handleRefresh = useCallback(() => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  }, []);

  const handleSelect = useCallback((id: string) => {
    setSelectedId((prev) => (prev === id ? null : id));
  }, []);

  const EQUIPMENT_TYPES: { value: EquipmentType; label: string }[] = [
    { value: "tractor", label: "جرار" },
    { value: "drone", label: "طائرة مسيّرة" },
    { value: "harvester", label: "حصّادة" },
    { value: "sprayer", label: "رشاش" },
    { value: "pump", label: "مضخة" },
    { value: "vehicle", label: "مركبة" },
  ];

  const STATUS_OPTIONS: { value: FleetStatus; label: string }[] = [
    { value: "active", label: "نشط" },
    { value: "idle", label: "خامل" },
    { value: "maintenance", label: "صيانة" },
    { value: "offline", label: "غير متصل" },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900" dir="rtl">
      <Header
        title="تتبع الأسطول"
        subtitle="مراقبة وتتبع مواقع المعدات والمركبات في الوقت الفعلي"
      />

      <div className="p-6 space-y-6">

        {/* Stats Row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="إجمالي المعدات المتتبعة"
            value={stats.total}
            icon={Navigation}
            iconColor="text-sahool-600"
          />
          <StatCard
            title="نشطة حالياً"
            value={stats.active}
            icon={Activity}
            iconColor="text-green-600"
            trend={{ value: 12, isPositive: true }}
          />
          <StatCard
            title="تحتاج صيانة"
            value={stats.maintenance}
            icon={Wrench}
            iconColor="text-orange-600"
          />
          <StatCard
            title="متوسط الاستخدام"
            value={stats.avgUtil}
            icon={BarChart3}
            iconColor="text-blue-600"
            suffix="%"
            trend={{ value: 5, isPositive: true }}
          />
        </div>

        {/* Filters Bar */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-1.5 text-sm font-medium text-gray-600 dark:text-gray-300">
              <Filter className="w-4 h-4" />
              <span>تصفية:</span>
            </div>

            {/* Type filter */}
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-sahool-500"
            >
              <option value="">كل الأنواع</option>
              {EQUIPMENT_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>

            {/* Status filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-sahool-500"
            >
              <option value="">كل الحالات</option>
              {STATUS_OPTIONS.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>

            {/* Quick status filters */}
            {STATUS_OPTIONS.map((s) => {
              const cfg = getStatusConfig(s.value);
              const count = MOCK_FLEET.filter((e) => e.status === s.value).length;
              return (
                <button
                  key={s.value}
                  type="button"
                  onClick={() => setStatusFilter((prev) => (prev === s.value ? "" : s.value))}
                  className={cn(
                    "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all",
                    statusFilter === s.value
                      ? cn(cfg.badgeClass, "border-current")
                      : "border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                  )}
                >
                  <span className={cn("w-2 h-2 rounded-full", cfg.dotClass)} />
                  {s.label}
                  <span className="text-gray-400 dark:text-gray-500">({count})</span>
                </button>
              );
            })}

            {/* Refresh */}
            <button
              type="button"
              onClick={handleRefresh}
              className="mr-auto p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              title="تحديث"
            >
              <RefreshCw
                className={cn("w-4 h-4 text-gray-500 dark:text-gray-400", isRefreshing && "animate-spin")}
              />
            </button>
          </div>
        </div>

        {/* Main Content: List + Detail Panel */}
        <div className={cn("grid gap-6", selectedItem ? "grid-cols-1 lg:grid-cols-5" : "grid-cols-1")}>

          {/* Fleet List */}
          <div className={cn(selectedItem ? "lg:col-span-3" : "col-span-1")}>
            {/* Results count */}
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
              يُعرض{" "}
              <span className="font-semibold text-gray-700 dark:text-gray-200">{filteredFleet.length}</span>
              {" "}من{" "}
              <span className="font-semibold text-gray-700 dark:text-gray-200">{MOCK_FLEET.length}</span>
              {" "}معدة
            </p>

            {filteredFleet.length === 0 ? (
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-12 text-center">
                <MapPin className="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                <p className="text-gray-500 dark:text-gray-400">لا توجد معدات تطابق المعايير المحددة</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {filteredFleet.map((item) => (
                  <FleetCard
                    key={item.id}
                    item={item}
                    isSelected={selectedId === item.id}
                    onClick={() => handleSelect(item.id)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Detail Panel */}
          {selectedItem && (
            <div className="lg:col-span-2">
              <div className="sticky top-20">
                {/* Panel header label */}
                <div className="flex items-center justify-between mb-3">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-300 flex items-center gap-1.5">
                    <ChevronRight className="w-4 h-4" />
                    تفاصيل المعدة
                  </p>
                </div>
                <DetailPanel item={selectedItem} onClose={() => setSelectedId(null)} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
