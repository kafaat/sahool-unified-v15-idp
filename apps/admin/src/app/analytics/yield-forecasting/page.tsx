// Sahool Admin Dashboard - Yield Forecasting
// تنبؤ الإنتاجية

"use client";

import React, { useState, useMemo } from "react";
import Header from "@/components/layout/Header";
import StatCard from "@/components/ui/StatCard";
import {
  TrendingUp,
  BarChart3,
  Leaf,
  Calendar,
  CheckCircle2,
  ChevronDown,
  Droplets,
  Sun,
  FlaskConical,
  AlertTriangle,
  Target,
  Clock,
  MapPin,
  Activity,
} from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────────────────

type CropFilter = "all" | "wheat" | "barley" | "tomato" | "date_palm";
type YieldStatus = "above_average" | "average" | "below_average";

interface FieldPrediction {
  fieldId: string;
  fieldName: string;
  crop: string;
  cropKey: CropFilter;
  area_ha: number;
  predictedYield_kg_ha: number;
  confidence: number;
  growthStage: string;
  growthStageProgress: number; // 0-100
  harvestDate: string;
  ndviFactor: number;
  weatherFactor: number;
  soilFactor: number;
  status: YieldStatus;
  benchmarkYield_kg_ha: number;
  irrigationStatus: string;
  pestRisk: "low" | "medium" | "high";
}

// ─── Mock Data ───────────────────────────────────────────────────────────────

const MOCK_PREDICTIONS: FieldPrediction[] = [
  {
    fieldId: "FIELD-001",
    fieldName: "حقل الرشيد",
    crop: "قمح",
    cropKey: "wheat",
    area_ha: 5.2,
    predictedYield_kg_ha: 3800,
    confidence: 85,
    growthStage: "التفريع",
    growthStageProgress: 45,
    harvestDate: "2026-05-15",
    ndviFactor: 0.82,
    weatherFactor: 0.79,
    soilFactor: 0.88,
    status: "above_average",
    benchmarkYield_kg_ha: 3400,
    irrigationStatus: "مثالي",
    pestRisk: "low",
  },
  {
    fieldId: "FIELD-002",
    fieldName: "حقل الشمالي",
    crop: "شعير",
    cropKey: "barley",
    area_ha: 3.8,
    predictedYield_kg_ha: 2900,
    confidence: 82,
    growthStage: "الإسبال",
    growthStageProgress: 65,
    harvestDate: "2026-04-20",
    ndviFactor: 0.76,
    weatherFactor: 0.81,
    soilFactor: 0.74,
    status: "above_average",
    benchmarkYield_kg_ha: 2600,
    irrigationStatus: "جيد",
    pestRisk: "low",
  },
  {
    fieldId: "FIELD-003",
    fieldName: "حقل الشرقي",
    crop: "طماطم",
    cropKey: "tomato",
    area_ha: 2.1,
    predictedYield_kg_ha: 48000,
    confidence: 78,
    growthStage: "الإزهار",
    growthStageProgress: 40,
    harvestDate: "2026-06-10",
    ndviFactor: 0.71,
    weatherFactor: 0.68,
    soilFactor: 0.80,
    status: "average",
    benchmarkYield_kg_ha: 46000,
    irrigationStatus: "يحتاج متابعة",
    pestRisk: "medium",
  },
  {
    fieldId: "FIELD-004",
    fieldName: "بستان النخيل",
    crop: "تمر",
    cropKey: "date_palm",
    area_ha: 4.5,
    predictedYield_kg_ha: 8500,
    confidence: 90,
    growthStage: "عقد الثمار",
    growthStageProgress: 55,
    harvestDate: "2026-09-01",
    ndviFactor: 0.91,
    weatherFactor: 0.88,
    soilFactor: 0.85,
    status: "above_average",
    benchmarkYield_kg_ha: 7800,
    irrigationStatus: "مثالي",
    pestRisk: "low",
  },
  {
    fieldId: "FIELD-005",
    fieldName: "حقل الغربي",
    crop: "قمح",
    cropKey: "wheat",
    area_ha: 6.0,
    predictedYield_kg_ha: 3500,
    confidence: 80,
    growthStage: "التطاول",
    growthStageProgress: 55,
    harvestDate: "2026-05-25",
    ndviFactor: 0.74,
    weatherFactor: 0.72,
    soilFactor: 0.78,
    status: "average",
    benchmarkYield_kg_ha: 3400,
    irrigationStatus: "جيد",
    pestRisk: "medium",
  },
  {
    fieldId: "FIELD-006",
    fieldName: "مزارع إب للبن",
    crop: "بن",
    cropKey: "all",
    area_ha: 3.2,
    predictedYield_kg_ha: 850,
    confidence: 75,
    growthStage: "الثمار الخضراء",
    growthStageProgress: 70,
    harvestDate: "2026-11-15",
    ndviFactor: 0.69,
    weatherFactor: 0.77,
    soilFactor: 0.72,
    status: "below_average",
    benchmarkYield_kg_ha: 920,
    irrigationStatus: "يحتاج متابعة",
    pestRisk: "medium",
  },
  {
    fieldId: "FIELD-007",
    fieldName: "حقل صنعاء",
    crop: "ذرة رفيعة",
    cropKey: "all",
    area_ha: 4.8,
    predictedYield_kg_ha: 2600,
    confidence: 83,
    growthStage: "النمو الخضري",
    growthStageProgress: 30,
    harvestDate: "2026-08-20",
    ndviFactor: 0.78,
    weatherFactor: 0.74,
    soilFactor: 0.82,
    status: "average",
    benchmarkYield_kg_ha: 2550,
    irrigationStatus: "جيد",
    pestRisk: "low",
  },
  {
    fieldId: "FIELD-008",
    fieldName: "مزارع حضرموت",
    crop: "مانجو",
    cropKey: "all",
    area_ha: 2.5,
    predictedYield_kg_ha: 12000,
    confidence: 88,
    growthStage: "الإزهار",
    growthStageProgress: 35,
    harvestDate: "2026-07-10",
    ndviFactor: 0.86,
    weatherFactor: 0.83,
    soilFactor: 0.79,
    status: "above_average",
    benchmarkYield_kg_ha: 10500,
    irrigationStatus: "مثالي",
    pestRisk: "low",
  },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

const STATUS_CONFIG: Record<
  YieldStatus,
  { label: string; bg: string; text: string; border: string; dot: string }
> = {
  above_average: {
    label: "فوق المتوسط",
    bg: "bg-green-50 dark:bg-green-900/20",
    text: "text-green-700 dark:text-green-400",
    border: "border-green-200 dark:border-green-800",
    dot: "bg-green-500",
  },
  average: {
    label: "متوسط",
    bg: "bg-yellow-50 dark:bg-yellow-900/20",
    text: "text-yellow-700 dark:text-yellow-400",
    border: "border-yellow-200 dark:border-yellow-800",
    dot: "bg-yellow-500",
  },
  below_average: {
    label: "دون المتوسط",
    bg: "bg-red-50 dark:bg-red-900/20",
    text: "text-red-700 dark:text-red-400",
    border: "border-red-200 dark:border-red-800",
    dot: "bg-red-500",
  },
};

const CROP_FILTERS: { key: CropFilter; label: string }[] = [
  { key: "all", label: "الكل" },
  { key: "wheat", label: "قمح" },
  { key: "barley", label: "شعير" },
  { key: "tomato", label: "طماطم" },
  { key: "date_palm", label: "نخيل" },
];

const PEST_RISK_CONFIG = {
  low: { label: "منخفضة", color: "text-green-600 dark:text-green-400", bg: "bg-green-100 dark:bg-green-900/30" },
  medium: { label: "متوسطة", color: "text-yellow-600 dark:text-yellow-400", bg: "bg-yellow-100 dark:bg-yellow-900/30" },
  high: { label: "مرتفعة", color: "text-red-600 dark:text-red-400", bg: "bg-red-100 dark:bg-red-900/30" },
};

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("ar-SA", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatYield(kg_ha: number): string {
  if (kg_ha >= 1000) {
    return `${(kg_ha / 1000).toFixed(1)} طن/هك`;
  }
  return `${kg_ha} كجم/هك`;
}

function daysUntilHarvest(dateStr: string): number {
  const today = new Date("2026-03-18");
  const harvest = new Date(dateStr);
  const diff = harvest.getTime() - today.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

// ─── Sub-components ───────────────────────────────────────────────────────────

interface FactorBarProps {
  label: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}

function FactorBar({ label, value, icon, color }: FactorBarProps) {
  const pct = Math.round(value * 100);
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="flex items-center gap-1 text-gray-600 dark:text-gray-400">
          {icon}
          {label}
        </span>
        <span className={`font-semibold ${color}`}>{pct}%</span>
      </div>
      <div className="h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color.replace("text-", "bg-")}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

interface PredictionCardProps {
  prediction: FieldPrediction;
  isSelected: boolean;
  onClick: () => void;
}

function PredictionCard({ prediction: p, isSelected, onClick }: PredictionCardProps) {
  const status = STATUS_CONFIG[p.status];
  const days = daysUntilHarvest(p.harvestDate);
  const yieldDiff = p.predictedYield_kg_ha - p.benchmarkYield_kg_ha;
  const yieldDiffPct = ((yieldDiff / (p.benchmarkYield_kg_ha || 1)) * 100).toFixed(1);
  const pest = PEST_RISK_CONFIG[p.pestRisk];

  return (
    <div
      onClick={onClick}
      className={`bg-white dark:bg-gray-900 rounded-xl border-2 transition-all duration-200 cursor-pointer hover:shadow-md ${
        isSelected
          ? "border-sahool-500 dark:border-sahool-400 shadow-md"
          : `border-gray-200 dark:border-gray-700 hover:border-sahool-300 dark:hover:border-sahool-600`
      }`}
    >
      {/* Card Header */}
      <div className="p-4 border-b border-gray-100 dark:border-gray-800">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="font-bold text-gray-900 dark:text-gray-100 text-sm">{p.fieldName}</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                {p.fieldId}
              </span>
              <span className="text-xs text-gray-400 dark:text-gray-500">•</span>
              <span className="text-xs text-gray-500 dark:text-gray-400">{p.area_ha} هك</span>
            </div>
          </div>
          <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${status.bg} ${status.text} border ${status.border}`}>
            <div className={`w-1.5 h-1.5 rounded-full ${status.dot}`} />
            {status.label}
          </div>
        </div>

        {/* Crop badge */}
        <div className="mt-2 flex items-center gap-2">
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300 text-xs font-medium rounded-full border border-sahool-200 dark:border-sahool-700">
            <Leaf className="w-3 h-3" />
            {p.crop}
          </span>
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full ${pest.bg} ${pest.color}`}>
            <AlertTriangle className="w-3 h-3" />
            مخاطر آفات: {pest.label}
          </span>
        </div>
      </div>

      {/* Yield Prediction */}
      <div className="p-4">
        <div className="flex items-end justify-between mb-3">
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">الإنتاجية المتوقعة</p>
            <p className="text-xl font-bold text-gray-900 dark:text-gray-100">{formatYield(p.predictedYield_kg_ha)}</p>
            <p className={`text-xs font-medium mt-0.5 ${yieldDiff >= 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>
              {yieldDiff >= 0 ? "+" : ""}{yieldDiffPct}% من المعيار
            </p>
          </div>
          <div className="text-left">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">مستوى الثقة</p>
            <p className="text-xl font-bold text-sahool-600 dark:text-sahool-400">{p.confidence}%</p>
          </div>
        </div>

        {/* Confidence bar */}
        <div className="mb-3">
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
            <span>مستوى الثقة</span>
            <span>{p.confidence}%</span>
          </div>
          <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                p.confidence >= 85
                  ? "bg-green-500"
                  : p.confidence >= 75
                  ? "bg-yellow-500"
                  : "bg-orange-500"
              }`}
              style={{ width: `${p.confidence}%` }}
            />
          </div>
        </div>

        {/* Growth stage */}
        <div className="mb-3">
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
            <span className="flex items-center gap-1">
              <Activity className="w-3 h-3" />
              {p.growthStage}
            </span>
            <span>{p.growthStageProgress}%</span>
          </div>
          <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-l from-emerald-500 to-teal-400 transition-all duration-700"
              style={{ width: `${p.growthStageProgress}%` }}
            />
          </div>
        </div>

        {/* Contributing Factors */}
        <div className="space-y-2 pt-2 border-t border-gray-100 dark:border-gray-800">
          <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">العوامل المؤثرة</p>
          <FactorBar
            label="مؤشر NDVI"
            value={p.ndviFactor}
            icon={<Activity className="w-3 h-3" />}
            color={p.ndviFactor >= 0.8 ? "text-green-600" : p.ndviFactor >= 0.65 ? "text-yellow-600" : "text-red-600"}
          />
          <FactorBar
            label="الطقس"
            value={p.weatherFactor}
            icon={<Sun className="w-3 h-3" />}
            color={p.weatherFactor >= 0.8 ? "text-blue-600" : p.weatherFactor >= 0.65 ? "text-yellow-600" : "text-red-600"}
          />
          <FactorBar
            label="التربة"
            value={p.soilFactor}
            icon={<FlaskConical className="w-3 h-3" />}
            color={p.soilFactor >= 0.8 ? "text-amber-600" : p.soilFactor >= 0.65 ? "text-yellow-600" : "text-red-600"}
          />
        </div>

        {/* Harvest date */}
        <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
            <Calendar className="w-3.5 h-3.5" />
            <span>موعد الحصاد: {formatDate(p.harvestDate)}</span>
          </div>
          <div className={`flex items-center gap-1 text-xs font-medium ${days <= 30 ? "text-orange-600 dark:text-orange-400" : "text-gray-500 dark:text-gray-400"}`}>
            <Clock className="w-3 h-3" />
            <span>{days} يوم</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Detail Panel ─────────────────────────────────────────────────────────────

interface DetailPanelProps {
  prediction: FieldPrediction;
  onClose: () => void;
}

function DetailPanel({ prediction: p, onClose }: DetailPanelProps) {
  const status = STATUS_CONFIG[p.status];
  const days = daysUntilHarvest(p.harvestDate);
  const totalYield_kg = p.predictedYield_kg_ha * p.area_ha;
  const totalYield_tons = totalYield_kg / 1000;
  const yieldDiff = p.predictedYield_kg_ha - p.benchmarkYield_kg_ha;
  const yieldDiffPct = ((yieldDiff / (p.benchmarkYield_kg_ha || 1)) * 100).toFixed(1);
  const pest = PEST_RISK_CONFIG[p.pestRisk];

  const overallScore = Math.round(
    (p.ndviFactor * 0.4 + p.weatherFactor * 0.35 + p.soilFactor * 0.25) * 100
  );

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border-2 border-sahool-400 dark:border-sahool-500 shadow-lg overflow-hidden">
      {/* Panel Header */}
      <div className="bg-gradient-to-l from-sahool-600 to-sahool-700 p-5 text-white">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-bold">{p.fieldName}</h2>
            <p className="text-sahool-200 text-sm mt-0.5">{p.fieldId} • {p.area_ha} هكتار • {p.crop}</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-white/20 transition-colors text-white"
            aria-label="إغلاق"
          >
            <ChevronDown className="w-5 h-5" />
          </button>
        </div>

        {/* Score highlight */}
        <div className="mt-4 flex items-center gap-4">
          <div className="text-center">
            <p className="text-3xl font-black">{formatYield(p.predictedYield_kg_ha)}</p>
            <p className="text-sahool-200 text-xs mt-0.5">الإنتاجية المتوقعة</p>
          </div>
          <div className="w-px h-10 bg-white/30" />
          <div className="text-center">
            <p className="text-3xl font-black">{p.confidence}%</p>
            <p className="text-sahool-200 text-xs mt-0.5">مستوى الثقة</p>
          </div>
          <div className="w-px h-10 bg-white/30" />
          <div className="text-center">
            <p className="text-3xl font-black">{totalYield_tons.toFixed(1)}t</p>
            <p className="text-sahool-200 text-xs mt-0.5">الإجمالي المتوقع</p>
          </div>
        </div>
      </div>

      <div className="p-5 space-y-5">
        {/* Status row */}
        <div className="flex flex-wrap gap-3">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium ${status.bg} ${status.text} border ${status.border}`}>
            <div className={`w-2 h-2 rounded-full ${status.dot}`} />
            {status.label}
          </div>
          <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${pest.bg} ${pest.color}`}>
            <AlertTriangle className="w-4 h-4" />
            مخاطر آفات: {pest.label}
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
            <Droplets className="w-4 h-4" />
            الري: {p.irrigationStatus}
          </div>
        </div>

        {/* Yield comparison */}
        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4">
          <h4 className="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-3 flex items-center gap-2">
            <Target className="w-4 h-4 text-sahool-600 dark:text-sahool-400" />
            مقارنة بالمعيار
          </h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">المتوقع</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{formatYield(p.predictedYield_kg_ha)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">المعيار</p>
              <p className="text-2xl font-bold text-gray-500 dark:text-gray-400">{formatYield(p.benchmarkYield_kg_ha)}</p>
            </div>
          </div>
          <div className="mt-3">
            <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
              <span>المعيار</span>
              <span className={`font-bold text-sm ${yieldDiff >= 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>
                {yieldDiff >= 0 ? "+" : ""}{yieldDiffPct}%
              </span>
              <span>المتوقع</span>
            </div>
            <div className="relative h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              {/* benchmark marker at 70% */}
              <div className="absolute inset-0 flex">
                <div
                  className="h-full bg-sahool-500 rounded-full"
                  style={{ width: `${Math.min((p.predictedYield_kg_ha / (p.benchmarkYield_kg_ha * 1.4)) * 100, 100)}%` }}
                />
              </div>
              <div
                className="absolute top-0 h-full w-0.5 bg-white dark:bg-gray-900"
                style={{ left: `${(p.benchmarkYield_kg_ha / (p.benchmarkYield_kg_ha * 1.4)) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Growth stage */}
        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4">
          <h4 className="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-3 flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-600" />
            مرحلة النمو
          </h4>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{p.growthStage}</span>
            <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400">{p.growthStageProgress}%</span>
          </div>
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-l from-emerald-500 to-teal-400"
              style={{ width: `${p.growthStageProgress}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-400 dark:text-gray-500 mt-1">
            <span>الإنبات</span>
            <span>الحصاد</span>
          </div>
        </div>

        {/* Factors breakdown */}
        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4">
          <h4 className="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-4 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-purple-600" />
            تفصيل العوامل المؤثرة
          </h4>
          <div className="space-y-3">
            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                  <Activity className="w-4 h-4 text-green-600" />
                  مؤشر NDVI الفضائي
                  <span className="text-xs text-gray-400">(40%)</span>
                </span>
                <span className="font-bold text-gray-900 dark:text-gray-100">{Math.round(p.ndviFactor * 100)}%</span>
              </div>
              <div className="h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-green-500 rounded-full"
                  style={{ width: `${p.ndviFactor * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                  <Sun className="w-4 h-4 text-blue-600" />
                  الطقس والمناخ
                  <span className="text-xs text-gray-400">(35%)</span>
                </span>
                <span className="font-bold text-gray-900 dark:text-gray-100">{Math.round(p.weatherFactor * 100)}%</span>
              </div>
              <div className="h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500 rounded-full"
                  style={{ width: `${p.weatherFactor * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                  <FlaskConical className="w-4 h-4 text-amber-600" />
                  تحليل التربة
                  <span className="text-xs text-gray-400">(25%)</span>
                </span>
                <span className="font-bold text-gray-900 dark:text-gray-100">{Math.round(p.soilFactor * 100)}%</span>
              </div>
              <div className="h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-amber-500 rounded-full"
                  style={{ width: `${p.soilFactor * 100}%` }}
                />
              </div>
            </div>

            {/* Overall score */}
            <div className="mt-2 pt-3 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="font-semibold text-gray-900 dark:text-gray-100">النتيجة الإجمالية</span>
                <span className={`font-bold text-base ${overallScore >= 80 ? "text-green-600 dark:text-green-400" : overallScore >= 65 ? "text-yellow-600 dark:text-yellow-400" : "text-red-600 dark:text-red-400"}`}>
                  {overallScore}%
                </span>
              </div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${overallScore >= 80 ? "bg-green-500" : overallScore >= 65 ? "bg-yellow-500" : "bg-red-500"}`}
                  style={{ width: `${overallScore}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Harvest countdown */}
        <div className={`rounded-xl p-4 flex items-center justify-between ${
          days <= 30
            ? "bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800"
            : "bg-sahool-50 dark:bg-sahool-900/20 border border-sahool-200 dark:border-sahool-800"
        }`}>
          <div>
            <p className={`text-sm font-medium ${days <= 30 ? "text-orange-700 dark:text-orange-400" : "text-sahool-700 dark:text-sahool-300"}`}>
              موعد الحصاد المتوقع
            </p>
            <p className={`text-lg font-bold ${days <= 30 ? "text-orange-800 dark:text-orange-300" : "text-sahool-800 dark:text-sahool-200"}`}>
              {formatDate(p.harvestDate)}
            </p>
          </div>
          <div className="text-center">
            <p className={`text-3xl font-black ${days <= 30 ? "text-orange-600 dark:text-orange-400" : "text-sahool-600 dark:text-sahool-400"}`}>
              {days}
            </p>
            <p className={`text-xs ${days <= 30 ? "text-orange-500 dark:text-orange-500" : "text-sahool-500 dark:text-sahool-500"}`}>يوم</p>
          </div>
        </div>

        {/* Total yield */}
        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4">
          <h4 className="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-3 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-sahool-600 dark:text-sahool-400" />
            ملخص الإنتاج
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="text-center p-3 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">المساحة</p>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{p.area_ha} هك</p>
            </div>
            <div className="text-center p-3 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">الإنتاج الكلي</p>
              <p className="text-lg font-bold text-sahool-600 dark:text-sahool-400">{totalYield_tons.toFixed(1)} طن</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function YieldForecastingPage() {
  const [cropFilter, setCropFilter] = useState<CropFilter>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showDetail, setShowDetail] = useState(false);

  // Filtered predictions
  const filtered = useMemo(() => {
    if (cropFilter === "all") return MOCK_PREDICTIONS;
    return MOCK_PREDICTIONS.filter((p) => p.cropKey === cropFilter);
  }, [cropFilter]);

  // Stats
  const stats = useMemo(() => {
    const total = MOCK_PREDICTIONS.length;
    const avgYield = MOCK_PREDICTIONS.reduce((s, p) => s + p.predictedYield_kg_ha, 0) / total;
    const avgConfidence = Math.round(MOCK_PREDICTIONS.reduce((s, p) => s + p.confidence, 0) / total);
    const harvestReady = MOCK_PREDICTIONS.filter((p) => daysUntilHarvest(p.harvestDate) <= 60).length;
    return { total, avgYield, avgConfidence, harvestReady };
  }, []);

  const selectedPrediction = MOCK_PREDICTIONS.find((p) => p.fieldId === selectedId) ?? null;

  function handleCardClick(fieldId: string) {
    if (selectedId === fieldId && showDetail) {
      setShowDetail(false);
      setSelectedId(null);
    } else {
      setSelectedId(fieldId);
      setShowDetail(true);
    }
  }

  return (
    <div className="p-6 space-y-6" dir="rtl">
      {/* Page Header */}
      <Header
        title="تنبؤ الإنتاجية"
        subtitle="تحليل وتوقعات إنتاجية المحاصيل بناءً على بيانات الحقول"
      />

      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="متوسط الإنتاجية المتوقعة"
          value={`${(stats.avgYield / 1000).toFixed(1)} طن/هك`}
          icon={TrendingUp}
          iconColor="text-sahool-600"
          trend={{ value: 8.5, isPositive: true }}
        />
        <StatCard
          title="الحقول المرصودة"
          value={stats.total}
          icon={MapPin}
          iconColor="text-blue-600"
        />
        <StatCard
          title="متوسط مستوى الثقة"
          value={`${stats.avgConfidence}%`}
          icon={CheckCircle2}
          iconColor="text-green-600"
          trend={{ value: 3.2, isPositive: true }}
        />
        <StatCard
          title="قريب من الحصاد"
          value={stats.harvestReady}
          icon={Calendar}
          iconColor="text-orange-600"
          suffix="حقول"
        />
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">تصفية حسب المحصول:</span>
        {CROP_FILTERS.map((f) => {
          const count = f.key === "all"
            ? MOCK_PREDICTIONS.length
            : MOCK_PREDICTIONS.filter((p) => p.cropKey === f.key).length;
          return (
            <button
              key={f.key}
              onClick={() => setCropFilter(f.key)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 border ${
                cropFilter === f.key
                  ? "bg-sahool-600 text-white border-sahool-600 shadow-sm"
                  : "bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 border-gray-200 dark:border-gray-700 hover:border-sahool-400 dark:hover:border-sahool-500 hover:text-sahool-600 dark:hover:text-sahool-400"
              }`}
            >
              {f.label}
              <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                cropFilter === f.key
                  ? "bg-white/20 text-white"
                  : "bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400"
              }`}>
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Content: grid + optional detail panel */}
      <div className={`grid gap-6 ${showDetail && selectedPrediction ? "grid-cols-1 lg:grid-cols-3" : "grid-cols-1"}`}>
        {/* Prediction Cards Grid */}
        <div className={`${showDetail && selectedPrediction ? "lg:col-span-2" : ""}`}>
          {filtered.length === 0 ? (
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-12 text-center">
              <Leaf className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
              <p className="text-gray-500 dark:text-gray-400">لا توجد حقول مطابقة لهذا المحصول</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filtered.map((prediction) => (
                <PredictionCard
                  key={prediction.fieldId}
                  prediction={prediction}
                  isSelected={selectedId === prediction.fieldId}
                  onClick={() => handleCardClick(prediction.fieldId)}
                />
              ))}
            </div>
          )}

          {/* Result count */}
          <p className="text-xs text-gray-400 dark:text-gray-600 mt-3 text-left">
            عرض {filtered.length} من {MOCK_PREDICTIONS.length} حقول
          </p>
        </div>

        {/* Detail Panel */}
        {showDetail && selectedPrediction && (
          <div className="lg:col-span-1 sticky top-6 self-start">
            <DetailPanel
              prediction={selectedPrediction}
              onClose={() => {
                setShowDetail(false);
                setSelectedId(null);
              }}
            />
          </div>
        )}
      </div>

      {/* Summary insight row */}
      <div className="bg-gradient-to-l from-sahool-600 via-sahool-700 to-sahool-800 rounded-xl p-5 text-white">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-white/15 rounded-xl">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-lg">ملخص موسم 2026</h3>
            <p className="text-sahool-200 text-sm mt-1">
              بناءً على بيانات {MOCK_PREDICTIONS.length} حقول، يُتوقع موسم{" "}
              <span className="text-white font-semibold">فوق المتوسط</span> لمحاصيل القمح والنخيل،
              مع الحاجة لمتابعة مكثفة لحقول الطماطم والبن.
              {" "}الإنتاج الكلي المتوقع:{" "}
              <span className="text-white font-semibold">
                {(MOCK_PREDICTIONS.reduce((s, p) => s + p.predictedYield_kg_ha * p.area_ha, 0) / 1000).toFixed(0)} طن
              </span>.
            </p>
            <div className="flex flex-wrap gap-4 mt-3 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-400" />
                <span className="text-sahool-200">
                  فوق المتوسط: {MOCK_PREDICTIONS.filter((p) => p.status === "above_average").length} حقول
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-yellow-400" />
                <span className="text-sahool-200">
                  متوسط: {MOCK_PREDICTIONS.filter((p) => p.status === "average").length} حقول
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-red-400" />
                <span className="text-sahool-200">
                  دون المتوسط: {MOCK_PREDICTIONS.filter((p) => p.status === "below_average").length} حقول
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
