"use client";

// Seeds & Variety Catalog Page - P3 VRS
// صفحة كتالوج البذور والأصناف - إدارة أصناف المحاصيل

import React, { useState, useMemo } from "react";
import Header from "@/components/layout/Header";
import StatCard from "@/components/ui/StatCard";
import {
  Sprout,
  Search,
  Filter,
  X,
  Wheat,
  Coffee,
  Sun,
  Leaf,
  Cherry,
  Apple,
  MapPin,
  Clock,
  TrendingUp,
  Droplets,
  Thermometer,
  Shield,
  ChevronLeft,
  Info,
  Star,
  Globe,
  Package,
} from "lucide-react";
import { cn } from "@/lib/utils";

// ─── Types ───────────────────────────────────────────────────────────────────

type OriginType = "LOCAL" | "IMPROVED" | "INTRODUCED" | "HYBRID";
type MaturityType = "EARLY" | "MEDIUM" | "LATE";
type ToleranceLevel = "high" | "medium" | "low";
type CropType =
  | "WHEAT"
  | "COFFEE"
  | "SORGHUM"
  | "DATE"
  | "TOMATO"
  | "BARLEY"
  | "MANGO";

interface Variety {
  id: string;
  code: string;
  nameAr: string;
  nameEn: string;
  crop: CropType;
  origin: OriginType;
  maturity: MaturityType;
  daysToMaturity: number;
  yieldPotential_ton_ha: number;
  suitableRegions: string[];
  droughtTolerance: ToleranceLevel;
  heatTolerance: ToleranceLevel;
  diseaseResistance: ToleranceLevel;
  seedSource: string;
  description: string;
  plantingWindow: string;
  growthRequirements: string;
}

// ─── Mock Data ────────────────────────────────────────────────────────────────

const VARIETIES: Variety[] = [
  {
    id: "WHEAT-001",
    code: "WHT-001",
    nameAr: "قمح محلي يمني",
    nameEn: "Yemeni Local Wheat",
    crop: "WHEAT",
    origin: "LOCAL",
    maturity: "MEDIUM",
    daysToMaturity: 130,
    yieldPotential_ton_ha: 3.5,
    suitableRegions: ["صنعاء", "إب"],
    droughtTolerance: "high",
    heatTolerance: "medium",
    diseaseResistance: "medium",
    seedSource: "مركز البحوث الزراعية اليمني",
    description:
      "صنف محلي متأقلم مع ظروف المرتفعات اليمنية، يتميز بمقاومته للجفاف وملاءمته للزراعة في الأراضي الجبلية. يُزرع منذ مئات السنين ويحتفظ بخصائص وراثية متميزة تجعله مناسباً للبيئة المحلية.",
    plantingWindow: "أكتوبر - نوفمبر (موسم الشتاء)",
    growthRequirements:
      "ارتفاع 1500-2500م، أمطار 400-600مم/سنة، درجة حرارة 10-25°م",
  },
  {
    id: "WHEAT-002",
    code: "WHT-002",
    nameAr: "ساخا 93",
    nameEn: "Sakha 93",
    crop: "WHEAT",
    origin: "IMPROVED",
    maturity: "MEDIUM",
    daysToMaturity: 145,
    yieldPotential_ton_ha: 5.0,
    suitableRegions: ["المرتفعات"],
    droughtTolerance: "medium",
    heatTolerance: "medium",
    diseaseResistance: "high",
    seedSource: "مركز البحث الزراعي الدولي (CIMMYT)",
    description:
      "صنف محسّن عالي الإنتاجية تم تطويره لمناطق المرتفعات. يتميز بمقاومته للأمراض الفطرية خاصة صدأ الأوراق، ويعطي إنتاجاً مرتفعاً في الظروف المُحسّنة مع توفر الري والتسميد الكافي.",
    plantingWindow: "نوفمبر - ديسمبر (موسم الشتاء)",
    growthRequirements:
      "ارتفاع 1800-2800م، ري منتظم، تسميد نيتروجيني 80-100 كغ/هـ",
  },
  {
    id: "COFFEE-001",
    code: "COF-001",
    nameAr: "موكا يمني",
    nameEn: "Yemeni Mocha Coffee",
    crop: "COFFEE",
    origin: "LOCAL",
    maturity: "LATE",
    daysToMaturity: 270,
    yieldPotential_ton_ha: 0.8,
    suitableRegions: ["إب", "حراز"],
    droughtTolerance: "high",
    heatTolerance: "medium",
    diseaseResistance: "high",
    seedSource: "مزارع الموكا التقليدية",
    description:
      "القهوة اليمنية الأصيلة المشهورة عالمياً بنكهتها الفريدة. يُعدّ من أقدم أصناف البن في العالم وأكثرها تميزاً، يزرع في المدرجات الجبلية على ارتفاعات 1500-2500م ويُصدَّر بأسعار مرتفعة.",
    plantingWindow: "مارس - أبريل (بعد الأمطار)",
    growthRequirements:
      "ارتفاع 1500-2500م، أمطار 600-800مم/سنة، تربة طينية جيدة الصرف",
  },
  {
    id: "COFFEE-002",
    code: "COF-002",
    nameAr: "ماطري",
    nameEn: "Matari Coffee",
    crop: "COFFEE",
    origin: "LOCAL",
    maturity: "LATE",
    daysToMaturity: 260,
    yieldPotential_ton_ha: 0.9,
    suitableRegions: ["بني مطر"],
    droughtTolerance: "high",
    heatTolerance: "low",
    diseaseResistance: "medium",
    seedSource: "مزارع بني مطر التقليدية",
    description:
      "صنف الماطري من أرقى أصناف البن اليمني، ينمو حصرياً في منطقة بني مطر غرب صنعاء. يتميز بنكهته الفاكهية المميزة ورائحته الزهرية، ويُحقق أعلى أسعار في أسواق البن المتخصصة العالمية.",
    plantingWindow: "أبريل - مايو",
    growthRequirements: "ارتفاع 1800-2200م، مناخ معتدل، تربة بازلتية",
  },
  {
    id: "SORGHUM-001",
    code: "SOR-001",
    nameAr: "ذرة تهامة البيضاء",
    nameEn: "Tihama White Sorghum",
    crop: "SORGHUM",
    origin: "LOCAL",
    maturity: "EARLY",
    daysToMaturity: 90,
    yieldPotential_ton_ha: 2.5,
    suitableRegions: ["تهامة"],
    droughtTolerance: "high",
    heatTolerance: "high",
    diseaseResistance: "medium",
    seedSource: "مزارعو تهامة المحليون",
    description:
      "صنف تهامي متأقلم مع حرارة السهل الساحلي الشديدة والرطوبة العالية. يُستخدم للغذاء البشري (العيش) والعلف الحيواني. دورة نمو قصيرة تسمح بزراعة موسمين في السنة في مناطق تهامة.",
    plantingWindow: "مارس - أبريل / يوليو - أغسطس",
    growthRequirements:
      "درجة حرارة 25-38°م، رطوبة عالية، تربة طمية خصبة، ري منتظم",
  },
  {
    id: "SORGHUM-002",
    code: "SOR-002",
    nameAr: "ذرة حمراء",
    nameEn: "Red Sorghum",
    crop: "SORGHUM",
    origin: "LOCAL",
    maturity: "MEDIUM",
    daysToMaturity: 100,
    yieldPotential_ton_ha: 2.8,
    suitableRegions: ["المرتفعات"],
    droughtTolerance: "medium",
    heatTolerance: "medium",
    diseaseResistance: "high",
    seedSource: "مركز البحوث الزراعية - إب",
    description:
      "صنف ذرة محلي يزرع في المرتفعات اليمنية، غني بالمغذيات ومناسب للاستهلاك البشري. يُستخدم في صنع الخبز التقليدي والعصيدة. يتميز بمقاومته للأمراض الفطرية الشائعة في المناطق الرطبة.",
    plantingWindow: "يوليو - أغسطس (موسم الصيف)",
    growthRequirements: "ارتفاع 1000-2000م، أمطار موسمية، تربة متوسطة",
  },
  {
    id: "DATE-001",
    code: "DAT-001",
    nameAr: "خلاص",
    nameEn: "Khalas Dates",
    crop: "DATE",
    origin: "LOCAL",
    maturity: "LATE",
    daysToMaturity: 180,
    yieldPotential_ton_ha: 10.0,
    suitableRegions: ["حضرموت", "الساحل"],
    droughtTolerance: "high",
    heatTolerance: "high",
    diseaseResistance: "medium",
    seedSource: "مزارع حضرموت التقليدية",
    description:
      "من أجود أصناف التمور اليمنية، يُعدّ من الأصناف التجارية الرئيسية في حضرموت. يتميز بطعمه الحلو المميز ولونه العسلي الجميل، ويُصدَّر لدول الخليج والعالم. يتحمل درجات الحرارة المرتفعة جداً.",
    plantingWindow: "فبراير - مارس (التلقيح)",
    growthRequirements: "حرارة 35-45°م، جفاف شديد، تربة رملية، مياه جوفية",
  },
  {
    id: "DATE-002",
    code: "DAT-002",
    nameAr: "بلحي",
    nameEn: "Balhi Dates",
    crop: "DATE",
    origin: "LOCAL",
    maturity: "LATE",
    daysToMaturity: 170,
    yieldPotential_ton_ha: 8.0,
    suitableRegions: ["حضرموت"],
    droughtTolerance: "high",
    heatTolerance: "high",
    diseaseResistance: "high",
    seedSource: "مشتل النخيل الحكومي - سيئون",
    description:
      "صنف حضرمي أصيل يتميز بمقاومته الفائقة للجفاف وملوحة التربة. يُنتج ثماراً كبيرة الحجم ذات لب وفير. يُعدّ من الأصناف الاقتصادية المهمة لمزارعي حضرموت نظراً لانخفاض احتياجاته المائية.",
    plantingWindow: "فبراير - مارس (التلقيح)",
    growthRequirements:
      "حرارة 30-45°م، تحمل ملوحة عالية، ري بالتنقيط مناسب",
  },
  {
    id: "TOMATO-001",
    code: "TOM-001",
    nameAr: "طماطم محلي",
    nameEn: "Local Tomato",
    crop: "TOMATO",
    origin: "LOCAL",
    maturity: "EARLY",
    daysToMaturity: 75,
    yieldPotential_ton_ha: 45.0,
    suitableRegions: ["تهامة", "الساحل"],
    droughtTolerance: "medium",
    heatTolerance: "medium",
    diseaseResistance: "low",
    seedSource: "تجار البذور المحليون",
    description:
      "صنف طماطم محلي سريع النضج يناسب الزراعة في السهول الساحلية. يتميز بنكهته القوية وتحمله لدرجات الحرارة المرتفعة نسبياً. يحتاج إلى مكافحة الآفات بشكل منتظم خاصة في الفترات الرطبة.",
    plantingWindow: "أكتوبر - ديسمبر (الشتاء) / فبراير - مارس (الربيع)",
    growthRequirements:
      "درجة حرارة 20-30°م، ري منتظم، تسميد كثيف، مكافحة آفات",
  },
  {
    id: "TOMATO-002",
    code: "TOM-002",
    nameAr: "بونتا روزا",
    nameEn: "Punta Rosa Tomato",
    crop: "TOMATO",
    origin: "INTRODUCED",
    maturity: "MEDIUM",
    daysToMaturity: 85,
    yieldPotential_ton_ha: 55.0,
    suitableRegions: ["المرتفعات"],
    droughtTolerance: "low",
    heatTolerance: "low",
    diseaseResistance: "high",
    seedSource: "شركة سينجنتا للبذور",
    description:
      "صنف هجين مُستورد عالي الإنتاجية مناسب لمناطق المرتفعات المعتدلة. يتميز بمقاومته للأمراض الفطرية والفيروسية وإعطائه إنتاجاً عالياً في الزراعة المحمية. يحتاج إلى ظروف مناخية معتدلة وري منتظم.",
    plantingWindow: "سبتمبر - أكتوبر (الخريف) / فبراير - مارس (الربيع)",
    growthRequirements:
      "درجة حرارة 15-25°م، ري بالتنقيط، زراعة محمية (بيوت بلاستيكية)",
  },
  {
    id: "BARLEY-001",
    code: "BAR-001",
    nameAr: "شعير بلدي",
    nameEn: "Local Barley",
    crop: "BARLEY",
    origin: "LOCAL",
    maturity: "EARLY",
    daysToMaturity: 100,
    yieldPotential_ton_ha: 2.0,
    suitableRegions: ["المرتفعات الشمالية"],
    droughtTolerance: "high",
    heatTolerance: "low",
    diseaseResistance: "medium",
    seedSource: "مزارعو المرتفعات الشمالية",
    description:
      "صنف شعير بلدي متكيف مع المناطق الجبلية الباردة والجافة، يُزرع بصفة رئيسية في محافظات صعدة وحجة والجوف. يُستخدم في صنع خبز المرتفعات التقليدي وعلف الحيوانات. يتحمل درجات الحرارة المنخفضة والصقيع.",
    plantingWindow: "نوفمبر - ديسمبر (الشتاء)",
    growthRequirements:
      "ارتفاع 2000-3000م، درجة حرارة 5-20°م، أمطار شتوية",
  },
  {
    id: "MANGO-001",
    code: "MNG-001",
    nameAr: "أويس",
    nameEn: "Owais Mango",
    crop: "MANGO",
    origin: "LOCAL",
    maturity: "MEDIUM",
    daysToMaturity: 150,
    yieldPotential_ton_ha: 12.0,
    suitableRegions: ["تهامة", "عدن"],
    droughtTolerance: "medium",
    heatTolerance: "high",
    diseaseResistance: "medium",
    seedSource: "مشتل وزارة الزراعة - الحديدة",
    description:
      "صنف مانجو يمني أصيل مشهور بحجمه الكبير ونكهته الاستثنائية. يُعدّ من أجود أصناف المانجو في المنطقة ويُصدَّر لدول الخليج. يتحمل الحرارة الشديدة ويزدهر في المناطق الساحلية الحارة مع توفر الري الكافي.",
    plantingWindow: "مارس - أبريل (الإزهار)",
    growthRequirements:
      "درجة حرارة 25-40°م، ري منتظم، رطوبة معتدلة، تسميد دوري",
  },
];

// ─── Helper Maps ──────────────────────────────────────────────────────────────

const CROP_LABELS: Record<CropType, { ar: string; icon: React.ReactNode }> = {
  WHEAT: { ar: "قمح", icon: <Wheat className="w-4 h-4" /> },
  COFFEE: { ar: "قهوة", icon: <Coffee className="w-4 h-4" /> },
  SORGHUM: { ar: "ذرة", icon: <Sun className="w-4 h-4" /> },
  DATE: { ar: "نخيل تمر", icon: <Leaf className="w-4 h-4" /> },
  TOMATO: { ar: "طماطم", icon: <Cherry className="w-4 h-4" /> },
  BARLEY: { ar: "شعير", icon: <Sprout className="w-4 h-4" /> },
  MANGO: { ar: "مانجو", icon: <Apple className="w-4 h-4" /> },
};

const ORIGIN_CONFIG: Record<
  OriginType,
  { label: string; color: string; bg: string }
> = {
  LOCAL: {
    label: "محلي",
    color: "text-green-700 dark:text-green-400",
    bg: "bg-green-100 dark:bg-green-900/40",
  },
  IMPROVED: {
    label: "محسّن",
    color: "text-blue-700 dark:text-blue-400",
    bg: "bg-blue-100 dark:bg-blue-900/40",
  },
  INTRODUCED: {
    label: "مستورد",
    color: "text-purple-700 dark:text-purple-400",
    bg: "bg-purple-100 dark:bg-purple-900/40",
  },
  HYBRID: {
    label: "هجين",
    color: "text-orange-700 dark:text-orange-400",
    bg: "bg-orange-100 dark:bg-orange-900/40",
  },
};

const MATURITY_CONFIG: Record<MaturityType, { label: string; color: string }> =
  {
    EARLY: { label: "مبكر", color: "text-green-600 dark:text-green-400" },
    MEDIUM: { label: "متوسط", color: "text-amber-600 dark:text-amber-400" },
    LATE: { label: "متأخر", color: "text-red-600 dark:text-red-400" },
  };

const TOLERANCE_DOT: Record<ToleranceLevel, string> = {
  high: "bg-green-500",
  medium: "bg-amber-400",
  low: "bg-red-400",
};

const TOLERANCE_LABEL: Record<ToleranceLevel, string> = {
  high: "عالي",
  medium: "متوسط",
  low: "منخفض",
};

// ─── Filter Options ───────────────────────────────────────────────────────────

const CROP_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "كل المحاصيل" },
  { value: "WHEAT", label: "قمح" },
  { value: "COFFEE", label: "قهوة" },
  { value: "SORGHUM", label: "ذرة" },
  { value: "DATE", label: "نخيل تمر" },
  { value: "TOMATO", label: "طماطم" },
  { value: "BARLEY", label: "شعير" },
  { value: "MANGO", label: "مانجو" },
];

const ORIGIN_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "كل الأصول" },
  { value: "LOCAL", label: "محلي" },
  { value: "IMPROVED", label: "محسّن" },
  { value: "INTRODUCED", label: "مستورد" },
  { value: "HYBRID", label: "هجين" },
];

const MATURITY_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "كل مواعيد النضج" },
  { value: "EARLY", label: "مبكر" },
  { value: "MEDIUM", label: "متوسط" },
  { value: "LATE", label: "متأخر" },
];

const ALL_REGIONS = Array.from(
  new Set(VARIETIES.flatMap((v) => v.suitableRegions)),
).sort();

// ─── Sub-components ───────────────────────────────────────────────────────────

function ToleranceDot({
  level,
  label,
}: {
  level: ToleranceLevel;
  label: string;
}) {
  return (
    <span className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
      <span
        className={cn("inline-block w-2 h-2 rounded-full", TOLERANCE_DOT[level])}
        title={`${label}: ${TOLERANCE_LABEL[level]}`}
      />
      {label}
    </span>
  );
}

function VarietyCard({
  variety,
  isSelected,
  onClick,
}: {
  variety: Variety;
  isSelected: boolean;
  onClick: () => void;
}) {
  const crop = CROP_LABELS[variety.crop];
  const origin = ORIGIN_CONFIG[variety.origin];
  const maturity = MATURITY_CONFIG[variety.maturity];

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "w-full text-right bg-white dark:bg-gray-800 rounded-xl border transition-all hover:shadow-md focus:outline-none focus:ring-2 focus:ring-sahool-500 p-5",
        isSelected
          ? "border-sahool-500 dark:border-sahool-400 shadow-md ring-2 ring-sahool-200 dark:ring-sahool-800"
          : "border-gray-100 dark:border-gray-700",
      )}
    >
      {/* Header Row */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "px-2 py-0.5 rounded-full text-xs font-semibold",
              origin.bg,
              origin.color,
            )}
          >
            {origin.label}
          </span>
          <span className={cn("text-xs font-medium", maturity.color)}>
            {maturity.label} النضج
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-gray-400 dark:text-gray-500 text-xs">
          {crop.icon}
          <span>{crop.ar}</span>
        </div>
      </div>

      {/* Name */}
      <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-0.5">
        {variety.nameAr}
      </h3>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
        {variety.nameEn}
      </p>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="flex items-center gap-1.5 text-xs text-gray-600 dark:text-gray-400">
          <Clock className="w-3.5 h-3.5 flex-shrink-0 text-gray-400" />
          <span>{variety.daysToMaturity} يوم</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-gray-600 dark:text-gray-400">
          <TrendingUp className="w-3.5 h-3.5 flex-shrink-0 text-sahool-500" />
          <span>{variety.yieldPotential_ton_ha} طن/هـ</span>
        </div>
      </div>

      {/* Suitable Regions */}
      <div className="flex flex-wrap gap-1 mb-3">
        {variety.suitableRegions.map((region) => (
          <span
            key={region}
            className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded text-xs"
          >
            <MapPin className="w-2.5 h-2.5" />
            {region}
          </span>
        ))}
      </div>

      {/* Tolerance Indicators */}
      <div className="flex items-center gap-3 pt-2 border-t border-gray-100 dark:border-gray-700">
        <ToleranceDot level={variety.droughtTolerance} label="جفاف" />
        <ToleranceDot level={variety.heatTolerance} label="حرارة" />
        <ToleranceDot level={variety.diseaseResistance} label="مرض" />
      </div>
    </button>
  );
}

function DetailPanel({
  variety,
  onClose,
}: {
  variety: Variety;
  onClose: () => void;
}) {
  const crop = CROP_LABELS[variety.crop];
  const origin = ORIGIN_CONFIG[variety.origin];
  const maturity = MATURITY_CONFIG[variety.maturity];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-lg overflow-hidden flex flex-col h-full">
      {/* Panel Header */}
      <div className="flex items-start justify-between p-5 border-b border-gray-100 dark:border-gray-700">
        <div className="flex items-center gap-2 text-gray-400 dark:text-gray-500">
          {crop.icon}
          <span className="text-sm">{crop.ar}</span>
          <span className="text-gray-300 dark:text-gray-600">·</span>
          <span className="text-sm font-mono text-gray-400 dark:text-gray-500">
            {variety.code}
          </span>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          aria-label="إغلاق"
        >
          <X className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      <div className="overflow-y-auto flex-1 p-5 space-y-5">
        {/* Title */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            {variety.nameAr}
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {variety.nameEn}
          </p>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2">
          <span
            className={cn(
              "px-3 py-1 rounded-full text-sm font-semibold",
              origin.bg,
              origin.color,
            )}
          >
            {origin.label}
          </span>
          <span
            className={cn(
              "px-3 py-1 rounded-full text-sm font-medium bg-gray-100 dark:bg-gray-700",
              maturity.color,
            )}
          >
            {maturity.label} النضج
          </span>
        </div>

        {/* Key Stats Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
            <div className="flex items-center gap-1.5 text-gray-500 dark:text-gray-400 text-xs mb-1">
              <Clock className="w-3.5 h-3.5" />
              أيام النضج
            </div>
            <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
              {variety.daysToMaturity}
              <span className="text-sm font-normal text-gray-500 mr-1">يوم</span>
            </p>
          </div>
          <div className="bg-sahool-50 dark:bg-sahool-900/30 rounded-lg p-3">
            <div className="flex items-center gap-1.5 text-sahool-600 dark:text-sahool-400 text-xs mb-1">
              <TrendingUp className="w-3.5 h-3.5" />
              إمكانية الإنتاج
            </div>
            <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
              {variety.yieldPotential_ton_ha}
              <span className="text-sm font-normal text-gray-500 mr-1">
                طن/هـ
              </span>
            </p>
          </div>
        </div>

        {/* Tolerances */}
        <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            مؤشرات التحمل والمقاومة
          </h4>
          <div className="space-y-2">
            {(
              [
                {
                  icon: <Droplets className="w-4 h-4 text-blue-500" />,
                  label: "تحمل الجفاف",
                  level: variety.droughtTolerance,
                },
                {
                  icon: <Thermometer className="w-4 h-4 text-red-500" />,
                  label: "تحمل الحرارة",
                  level: variety.heatTolerance,
                },
                {
                  icon: <Shield className="w-4 h-4 text-green-500" />,
                  label: "مقاومة الأمراض",
                  level: variety.diseaseResistance,
                },
              ] as {
                icon: React.ReactNode;
                label: string;
                level: ToleranceLevel;
              }[]
            ).map((item) => (
              <div
                key={item.label}
                className="flex items-center justify-between"
              >
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  {item.icon}
                  {item.label}
                </div>
                <div className="flex items-center gap-1.5">
                  <span
                    className={cn(
                      "inline-block w-2.5 h-2.5 rounded-full",
                      TOLERANCE_DOT[item.level],
                    )}
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {TOLERANCE_LABEL[item.level]}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Suitable Regions */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-1.5">
            <MapPin className="w-4 h-4 text-gray-400" />
            المناطق المناسبة
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {variety.suitableRegions.map((region) => (
              <span
                key={region}
                className="px-2.5 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full text-sm"
              >
                {region}
              </span>
            ))}
          </div>
        </div>

        {/* Planting Window */}
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-800/40 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-green-800 dark:text-green-400 mb-1.5 flex items-center gap-1.5">
            <Star className="w-4 h-4" />
            موسم الزراعة الموصى به
          </h4>
          <p className="text-sm text-green-700 dark:text-green-300">
            {variety.plantingWindow}
          </p>
        </div>

        {/* Growth Requirements */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800/40 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-400 mb-1.5 flex items-center gap-1.5">
            <Info className="w-4 h-4" />
            متطلبات النمو
          </h4>
          <p className="text-sm text-blue-700 dark:text-blue-300">
            {variety.growthRequirements}
          </p>
        </div>

        {/* Description */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            الوصف
          </h4>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            {variety.description}
          </p>
        </div>

        {/* Seed Source */}
        <div className="flex items-start gap-2 pt-2 border-t border-gray-100 dark:border-gray-700">
          <Globe className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-500 mb-0.5">
              مصدر البذور
            </p>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              {variety.seedSource}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function SeedsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [cropFilter, setCropFilter] = useState("");
  const [originFilter, setOriginFilter] = useState("");
  const [maturityFilter, setMaturityFilter] = useState("");
  const [regionFilter, setRegionFilter] = useState("");
  const [selectedVariety, setSelectedVariety] = useState<Variety | null>(null);

  // ── Derived Stats ──
  const stats = useMemo(() => {
    const total = VARIETIES.length;
    const crops = new Set(VARIETIES.map((v) => v.crop)).size;
    const local = VARIETIES.filter((v) => v.origin === "LOCAL").length;
    const improved = VARIETIES.filter(
      (v) => v.origin === "IMPROVED" || v.origin === "HYBRID",
    ).length;
    return { total, crops, local, improved };
  }, []);

  // ── Filtered Varieties ──
  const filteredVarieties = useMemo(() => {
    return VARIETIES.filter((v) => {
      if (cropFilter && v.crop !== cropFilter) return false;
      if (originFilter && v.origin !== originFilter) return false;
      if (maturityFilter && v.maturity !== maturityFilter) return false;
      if (regionFilter && !v.suitableRegions.includes(regionFilter))
        return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        if (
          !v.nameAr.toLowerCase().includes(q) &&
          !v.nameEn.toLowerCase().includes(q) &&
          !v.code.toLowerCase().includes(q)
        )
          return false;
      }
      return true;
    });
  }, [cropFilter, originFilter, maturityFilter, regionFilter, searchQuery]);

  const hasFilters =
    !!searchQuery ||
    !!cropFilter ||
    !!originFilter ||
    !!maturityFilter ||
    !!regionFilter;

  const clearFilters = () => {
    setSearchQuery("");
    setCropFilter("");
    setOriginFilter("");
    setMaturityFilter("");
    setRegionFilter("");
  };

  const handleSelectVariety = (variety: Variety) => {
    setSelectedVariety((prev) =>
      prev?.id === variety.id ? null : variety,
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950" dir="rtl">
      {/* ── Header ── */}
      <Header
        title="كتالوج البذور والأصناف"
        subtitle="إدارة أصناف المحاصيل والتوصيات الصنفية حسب المنطقة والمناخ"
      />

      <div className="p-6 space-y-6">
        {/* ── Stats Row ── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="إجمالي الأصناف"
            value={stats.total}
            icon={Package}
            iconColor="text-sahool-600"
          />
          <StatCard
            title="المحاصيل المغطاة"
            value={stats.crops}
            icon={Sprout}
            iconColor="text-green-600"
          />
          <StatCard
            title="الأصناف المحلية"
            value={stats.local}
            icon={Leaf}
            iconColor="text-emerald-600"
            trend={{ value: 8, isPositive: true }}
          />
          <StatCard
            title="الأصناف الموصى بها"
            value={stats.improved}
            icon={Star}
            iconColor="text-amber-500"
          />
        </div>

        {/* ── Filters Bar ── */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4">
          <div className="flex flex-wrap items-center gap-3">
            {/* Search */}
            <div className="relative flex-1 min-w-[200px]">
              <input
                type="text"
                placeholder="بحث باسم الصنف أو الكود..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pr-10 pl-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
              />
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            </div>

            {/* Crop Filter */}
            <select
              value={cropFilter}
              onChange={(e) => setCropFilter(e.target.value)}
              className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-200"
            >
              {CROP_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>

            {/* Origin Filter */}
            <select
              value={originFilter}
              onChange={(e) => setOriginFilter(e.target.value)}
              className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-200"
            >
              {ORIGIN_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>

            {/* Maturity Filter */}
            <select
              value={maturityFilter}
              onChange={(e) => setMaturityFilter(e.target.value)}
              className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-200"
            >
              {MATURITY_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>

            {/* Region Filter */}
            <select
              value={regionFilter}
              onChange={(e) => setRegionFilter(e.target.value)}
              className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-200"
            >
              <option value="">كل المناطق</option>
              {ALL_REGIONS.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>

            {/* Clear Filters */}
            {hasFilters && (
              <button
                type="button"
                onClick={clearFilters}
                className="flex items-center gap-1.5 px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <X className="w-4 h-4" />
                مسح الفلاتر
              </button>
            )}

            {/* Results count */}
            <div className="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 mr-auto">
              <Filter className="w-4 h-4" />
              <span>
                {filteredVarieties.length} صنف
              </span>
            </div>
          </div>
        </div>

        {/* ── Main Content: Grid + Detail Panel ── */}
        <div
          className={cn(
            "grid gap-6",
            selectedVariety
              ? "grid-cols-1 lg:grid-cols-3"
              : "grid-cols-1",
          )}
        >
          {/* Variety Cards Grid */}
          <div
            className={cn(
              selectedVariety ? "lg:col-span-2" : "col-span-full",
            )}
          >
            {filteredVarieties.length === 0 ? (
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-16 text-center">
                <Sprout className="w-14 h-14 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400 text-lg font-medium mb-1">
                  لا توجد أصناف مطابقة
                </p>
                <p className="text-sm text-gray-400 dark:text-gray-500">
                  جرّب تغيير معايير البحث أو الفلترة
                </p>
                {hasFilters && (
                  <button
                    type="button"
                    onClick={clearFilters}
                    className="mt-4 px-4 py-2 bg-sahool-600 text-white rounded-lg text-sm hover:bg-sahool-700 transition-colors"
                  >
                    مسح جميع الفلاتر
                  </button>
                )}
              </div>
            ) : (
              <div
                className={cn(
                  "grid gap-4",
                  selectedVariety
                    ? "grid-cols-1 sm:grid-cols-2"
                    : "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4",
                )}
              >
                {filteredVarieties.map((variety) => (
                  <VarietyCard
                    key={variety.id}
                    variety={variety}
                    isSelected={selectedVariety?.id === variety.id}
                    onClick={() => handleSelectVariety(variety)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Detail Panel */}
          {selectedVariety && (
            <div className="lg:col-span-1">
              <div className="sticky top-20 max-h-[calc(100vh-6rem)]">
                <div className="flex items-center gap-2 mb-3 text-sm text-gray-500 dark:text-gray-400">
                  <ChevronLeft className="w-4 h-4" />
                  <span>تفاصيل الصنف</span>
                </div>
                <DetailPanel
                  variety={selectedVariety}
                  onClose={() => setSelectedVariety(null)}
                />
              </div>
            </div>
          )}
        </div>

        {/* ── Legend ── */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            دليل الرموز والألوان
          </h3>
          <div className="flex flex-wrap gap-x-8 gap-y-3">
            <div className="space-y-1">
              <p className="text-xs font-medium text-gray-500 dark:text-gray-500 uppercase">
                أصل الصنف
              </p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(ORIGIN_CONFIG).map(([key, cfg]) => (
                  <span
                    key={key}
                    className={cn(
                      "px-2 py-0.5 rounded-full text-xs font-semibold",
                      cfg.bg,
                      cfg.color,
                    )}
                  >
                    {cfg.label}
                  </span>
                ))}
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-xs font-medium text-gray-500 dark:text-gray-500 uppercase">
                مستوى التحمل
              </p>
              <div className="flex items-center gap-4">
                {(
                  [
                    { level: "high" as ToleranceLevel, label: "عالي" },
                    { level: "medium" as ToleranceLevel, label: "متوسط" },
                    { level: "low" as ToleranceLevel, label: "منخفض" },
                  ]
                ).map((item) => (
                  <span
                    key={item.level}
                    className="flex items-center gap-1.5 text-xs text-gray-600 dark:text-gray-400"
                  >
                    <span
                      className={cn(
                        "inline-block w-2.5 h-2.5 rounded-full",
                        TOLERANCE_DOT[item.level],
                      )}
                    />
                    {item.label}
                  </span>
                ))}
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-xs font-medium text-gray-500 dark:text-gray-500 uppercase">
                موعد النضج
              </p>
              <div className="flex items-center gap-4">
                {Object.entries(MATURITY_CONFIG).map(([key, cfg]) => (
                  <span
                    key={key}
                    className={cn("text-xs font-medium", cfg.color)}
                  >
                    {cfg.label}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
