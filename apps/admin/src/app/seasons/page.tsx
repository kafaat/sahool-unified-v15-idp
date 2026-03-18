"use client";

/**
 * Agricultural Seasons Management Page
 * صفحة إدارة المواسم الزراعية
 *
 * Features:
 * - Season listing with filters
 * - Create season with crop selection
 * - Growth stages with plowing/seeding dates
 * - Fertilizer recommendations
 * - Preventive pesticide suggestions
 */

import { useState, useMemo, useCallback } from "react";
import Header from "@/components/layout/Header";
import { cn, formatDate, formatNumber } from "@/lib/utils";
import {
  Search,
  Plus,
  Calendar,
  Sprout,
  Bug,
  FlaskConical,
  ChevronDown,
  ChevronRight,
  X,
  Check,
  AlertTriangle,
  Leaf,
  Sun,
  Snowflake,
  TreeDeciduous,
} from "lucide-react";

// =============================================================================
// Types | الأنواع
// =============================================================================

type SeasonStatus = "planning" | "active" | "harvesting" | "completed" | "cancelled";
type SeasonType = "winter" | "summer" | "spring" | "fall";
type CropCategory = "cereals" | "vegetables" | "fruits" | "legumes" | "forage" | "industrial";

interface GrowthStage {
  id: string;
  name: string;
  nameAr: string;
  durationDays: number;
  description: string;
  descriptionAr: string;
  waterMultiplier: number;
  nutrientRequirements?: {
    nitrogen: number;
    phosphorus: number;
    potassium: number;
  };
}

interface FertilizerRecommendation {
  id: string;
  stage: string;
  stageAr: string;
  product: string;
  productAr: string;
  rateKgPerHa: number;
  method: string;
  methodAr: string;
  timing: string;
  timingAr: string;
  notes: string;
  notesAr: string;
}

interface PesticideRecommendation {
  id: string;
  pest: string;
  pestAr: string;
  type: "fungicide" | "insecticide" | "herbicide";
  product: string;
  productAr: string;
  activeIngredient: string;
  ratePerHa: string;
  timing: string;
  timingAr: string;
  phi: number;
  safetyNotes: string;
  safetyNotesAr: string;
}

interface SeasonCrop {
  id: string;
  name: string;
  nameAr: string;
  variety: string;
  varietyAr: string;
  category: CropCategory;
  areaHa: number;
  plantingDate: string;
  expectedHarvestDate: string;
  plowingDate: string;
  seedingDate: string;
  growthStages: GrowthStage[];
  fertilizerPlan: FertilizerRecommendation[];
  pesticidePlan: PesticideRecommendation[];
}

interface Season {
  id: string;
  name: string;
  nameAr: string;
  type: SeasonType;
  year: number;
  status: SeasonStatus;
  startDate: string;
  endDate: string;
  farmId: string;
  farmName: string;
  farmNameAr: string;
  crops: SeasonCrop[];
  totalAreaHa: number;
  targetYieldTons: number;
  actualYieldTons?: number;
  budgetSar: number;
  spentSar: number;
  progress: number;
  notes?: string;
}

// =============================================================================
// Constants | الثوابت
// =============================================================================

const SEASON_TYPE_CONFIG: Record<SeasonType, { label: string; labelAr: string; icon: typeof Sun; color: string }> = {
  winter: { label: "Winter", labelAr: "شتاء", icon: Snowflake, color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300" },
  summer: { label: "Summer", labelAr: "صيف", icon: Sun, color: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300" },
  spring: { label: "Spring", labelAr: "ربيع", icon: Sprout, color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300" },
  fall: { label: "Fall", labelAr: "خريف", icon: TreeDeciduous, color: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300" },
};

const STATUS_CONFIG: Record<SeasonStatus, { labelAr: string; color: string }> = {
  planning: { labelAr: "تخطيط", color: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300" },
  active: { labelAr: "نشط", color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300" },
  harvesting: { labelAr: "حصاد", color: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300" },
  completed: { labelAr: "مكتمل", color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300" },
  cancelled: { labelAr: "ملغي", color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300" },
};

const CATEGORY_LABELS: Record<CropCategory, string> = {
  cereals: "حبوب",
  vegetables: "خضروات",
  fruits: "فواكه",
  legumes: "بقوليات",
  forage: "أعلاف",
  industrial: "محاصيل صناعية",
};

// =============================================================================
// Mock Data | بيانات تجريبية
// =============================================================================

const WHEAT_GROWTH_STAGES: GrowthStage[] = [
  { id: "gs-1", name: "Germination", nameAr: "الإنبات", durationDays: 10, description: "Seed absorbs water and sprouts", descriptionAr: "امتصاص البذرة للماء والإنبات", waterMultiplier: 0.4, nutrientRequirements: { nitrogen: 0, phosphorus: 20, potassium: 10 } },
  { id: "gs-2", name: "Seedling", nameAr: "البادرة", durationDays: 15, description: "First leaves emerge", descriptionAr: "ظهور الأوراق الأولى", waterMultiplier: 0.5, nutrientRequirements: { nitrogen: 15, phosphorus: 15, potassium: 10 } },
  { id: "gs-3", name: "Tillering", nameAr: "التفريع", durationDays: 25, description: "Side shoots develop", descriptionAr: "نمو الأشطاء الجانبية", waterMultiplier: 0.7, nutrientRequirements: { nitrogen: 40, phosphorus: 10, potassium: 15 } },
  { id: "gs-4", name: "Stem Elongation", nameAr: "استطالة الساق", durationDays: 20, description: "Stem grows rapidly", descriptionAr: "نمو سريع للساق", waterMultiplier: 0.9, nutrientRequirements: { nitrogen: 30, phosphorus: 5, potassium: 20 } },
  { id: "gs-5", name: "Heading", nameAr: "طرد السنابل", durationDays: 15, description: "Ear emerges from flag leaf", descriptionAr: "خروج السنبلة من ورقة العلم", waterMultiplier: 1.0, nutrientRequirements: { nitrogen: 20, phosphorus: 5, potassium: 15 } },
  { id: "gs-6", name: "Flowering", nameAr: "الإزهار", durationDays: 10, description: "Pollination occurs", descriptionAr: "حدوث التلقيح", waterMultiplier: 1.0, nutrientRequirements: { nitrogen: 10, phosphorus: 5, potassium: 10 } },
  { id: "gs-7", name: "Grain Fill", nameAr: "امتلاء الحبوب", durationDays: 25, description: "Grain develops and fills", descriptionAr: "تطور وامتلاء الحبوب", waterMultiplier: 0.8, nutrientRequirements: { nitrogen: 5, phosphorus: 5, potassium: 10 } },
  { id: "gs-8", name: "Maturity", nameAr: "النضج", durationDays: 15, description: "Grain dries and hardens", descriptionAr: "جفاف وتصلب الحبوب", waterMultiplier: 0.3, nutrientRequirements: { nitrogen: 0, phosphorus: 0, potassium: 5 } },
];

const WHEAT_FERTILIZER_PLAN: FertilizerRecommendation[] = [
  { id: "f-1", stage: "Pre-planting", stageAr: "قبل الزراعة", product: "DAP (18-46-0)", productAr: "داب (18-46-0)", rateKgPerHa: 100, method: "Broadcast", methodAr: "نثر", timing: "During soil preparation", timingAr: "أثناء تحضير التربة", notes: "Apply before last plowing", notesAr: "يضاف قبل الحرثة الأخيرة" },
  { id: "f-2", stage: "Tillering", stageAr: "التفريع", product: "Urea 46%", productAr: "يوريا 46%", rateKgPerHa: 65, method: "Top dressing", methodAr: "تسميد سطحي", timing: "30-35 days after planting", timingAr: "30-35 يوم بعد الزراعة", notes: "Apply early morning with dew", notesAr: "يضاف في الصباح الباكر مع الندى" },
  { id: "f-3", stage: "Stem Elongation", stageAr: "استطالة الساق", product: "Urea 46%", productAr: "يوريا 46%", rateKgPerHa: 45, method: "Top dressing", methodAr: "تسميد سطحي", timing: "55-60 days after planting", timingAr: "55-60 يوم بعد الزراعة", notes: "Second nitrogen dose", notesAr: "الجرعة الثانية من النيتروجين" },
  { id: "f-4", stage: "Heading", stageAr: "طرد السنابل", product: "Potassium Sulfate", productAr: "سلفات البوتاسيوم", rateKgPerHa: 30, method: "Foliar spray", methodAr: "رش ورقي", timing: "At heading stage", timingAr: "عند طرد السنابل", notes: "Improves grain quality", notesAr: "يحسن جودة الحبوب" },
];

const WHEAT_PESTICIDE_PLAN: PesticideRecommendation[] = [
  { id: "p-1", pest: "Wheat Rust", pestAr: "صدأ القمح", type: "fungicide", product: "Propiconazole 25% EC", productAr: "بروبيكونازول 25% مركز", activeIngredient: "Propiconazole", ratePerHa: "0.5 L/ha", timing: "Preventive at tillering, repeat at heading if needed", timingAr: "وقائياً عند التفريع، يكرر عند طرد السنابل إذا لزم", phi: 35, safetyNotes: "Wear protective gloves and mask", safetyNotesAr: "ارتداء قفازات واقية وكمامة" },
  { id: "p-2", pest: "Aphids", pestAr: "المن", type: "insecticide", product: "Imidacloprid 20% SL", productAr: "إيميداكلوبريد 20%", activeIngredient: "Imidacloprid", ratePerHa: "0.25 L/ha", timing: "When 10+ aphids per tiller observed", timingAr: "عند ملاحظة 10+ حشرات من لكل إشطاء", phi: 21, safetyNotes: "Toxic to bees - do not apply during flowering", safetyNotesAr: "سام للنحل - لا يرش أثناء الإزهار" },
  { id: "p-3", pest: "Broadleaf Weeds", pestAr: "الأعشاب عريضة الأوراق", type: "herbicide", product: "2,4-D Amine 72%", productAr: "2,4-دي أمين 72%", activeIngredient: "2,4-Dichlorophenoxyacetic acid", ratePerHa: "1.0 L/ha", timing: "At 3-5 leaf stage of weeds", timingAr: "عند مرحلة 3-5 أوراق للأعشاب", phi: 30, safetyNotes: "Do not spray near other crops - drift risk", safetyNotesAr: "لا يرش بالقرب من محاصيل أخرى - خطر الانجراف" },
  { id: "p-4", pest: "Sunn Pest", pestAr: "حشرة السونة", type: "insecticide", product: "Deltamethrin 2.5% EC", productAr: "دلتاميثرين 2.5% مركز", activeIngredient: "Deltamethrin", ratePerHa: "0.5 L/ha", timing: "At grain fill stage when density exceeds threshold", timingAr: "عند مرحلة امتلاء الحبوب عند تجاوز الكثافة للعتبة", phi: 14, safetyNotes: "Apply in early morning or late evening", safetyNotesAr: "يرش في الصباح الباكر أو المساء المتأخر" },
];

const MOCK_SEASONS: Season[] = [
  {
    id: "s-001",
    name: "Winter 2025/2026",
    nameAr: "شتاء 2025/2026",
    type: "winter",
    year: 2026,
    status: "active",
    startDate: "2025-11-01",
    endDate: "2026-04-30",
    farmId: "farm-001",
    farmName: "Al-Rashid Farm",
    farmNameAr: "مزرعة الراشد",
    totalAreaHa: 22.5,
    targetYieldTons: 45,
    actualYieldTons: undefined,
    budgetSar: 150000,
    spentSar: 85000,
    progress: 65,
    crops: [
      {
        id: "sc-001",
        name: "Winter Wheat",
        nameAr: "قمح شتوي",
        variety: "Sakha 95",
        varietyAr: "سخا 95",
        category: "cereals",
        areaHa: 12.0,
        plantingDate: "2025-11-15",
        expectedHarvestDate: "2026-04-20",
        plowingDate: "2025-10-20",
        seedingDate: "2025-11-15",
        growthStages: WHEAT_GROWTH_STAGES,
        fertilizerPlan: WHEAT_FERTILIZER_PLAN,
        pesticidePlan: WHEAT_PESTICIDE_PLAN,
      },
      {
        id: "sc-002",
        name: "Barley",
        nameAr: "شعير",
        variety: "Giza 138",
        varietyAr: "جيزة 138",
        category: "cereals",
        areaHa: 6.5,
        plantingDate: "2025-11-20",
        expectedHarvestDate: "2026-04-10",
        plowingDate: "2025-10-25",
        seedingDate: "2025-11-20",
        growthStages: WHEAT_GROWTH_STAGES.map(gs => ({ ...gs, id: `gs-b-${gs.id}` })),
        fertilizerPlan: WHEAT_FERTILIZER_PLAN.map(f => ({ ...f, id: `f-b-${f.id}`, rateKgPerHa: Math.round(f.rateKgPerHa * 0.8) })),
        pesticidePlan: WHEAT_PESTICIDE_PLAN.slice(0, 3).map(p => ({ ...p, id: `p-b-${p.id}` })),
      },
      {
        id: "sc-003",
        name: "Alfalfa",
        nameAr: "برسيم حجازي",
        variety: "Local",
        varietyAr: "محلي",
        category: "forage",
        areaHa: 4.0,
        plantingDate: "2025-11-01",
        expectedHarvestDate: "2026-04-30",
        plowingDate: "2025-10-15",
        seedingDate: "2025-11-01",
        growthStages: [
          { id: "gs-a-1", name: "Germination", nameAr: "الإنبات", durationDays: 7, description: "Seed emergence", descriptionAr: "ظهور البادرة", waterMultiplier: 0.5, nutrientRequirements: { nitrogen: 0, phosphorus: 25, potassium: 15 } },
          { id: "gs-a-2", name: "Vegetative", nameAr: "النمو الخضري", durationDays: 30, description: "Leaf and stem growth", descriptionAr: "نمو الأوراق والسيقان", waterMultiplier: 0.8, nutrientRequirements: { nitrogen: 10, phosphorus: 10, potassium: 20 } },
          { id: "gs-a-3", name: "Flowering", nameAr: "الإزهار", durationDays: 15, description: "Flowers appear", descriptionAr: "ظهور الأزهار", waterMultiplier: 1.0, nutrientRequirements: { nitrogen: 5, phosphorus: 5, potassium: 10 } },
          { id: "gs-a-4", name: "Harvest", nameAr: "الحصاد", durationDays: 5, description: "Cut at 10% bloom", descriptionAr: "الحش عند 10% إزهار", waterMultiplier: 0.3 },
        ],
        fertilizerPlan: [
          { id: "f-a-1", stage: "Pre-planting", stageAr: "قبل الزراعة", product: "SSP (0-18-0)", productAr: "سوبر فوسفات (0-18-0)", rateKgPerHa: 150, method: "Broadcast", methodAr: "نثر", timing: "Before plowing", timingAr: "قبل الحراثة", notes: "Essential for root development", notesAr: "ضروري لتطور الجذور" },
          { id: "f-a-2", stage: "After each cut", stageAr: "بعد كل حشة", product: "NPK 20-20-20", productAr: "مركب 20-20-20", rateKgPerHa: 50, method: "Fertigation", methodAr: "تسميد مع الري", timing: "1-2 days after cutting", timingAr: "1-2 يوم بعد الحش", notes: "Promotes regrowth", notesAr: "يعزز النمو الجديد" },
        ],
        pesticidePlan: [
          { id: "p-a-1", pest: "Alfalfa Weevil", pestAr: "سوسة البرسيم", type: "insecticide", product: "Lambda-cyhalothrin", productAr: "لامبدا سيهالوثرين", activeIngredient: "Lambda-cyhalothrin", ratePerHa: "0.3 L/ha", timing: "When 30%+ tips show damage", timingAr: "عند تضرر 30% من القمم", phi: 7, safetyNotes: "Short PHI - safe for frequent harvest", safetyNotesAr: "فترة أمان قصيرة - آمن للحصاد المتكرر" },
        ],
      },
    ],
  },
  {
    id: "s-002",
    name: "Summer 2025",
    nameAr: "صيف 2025",
    type: "summer",
    year: 2025,
    status: "completed",
    startDate: "2025-05-01",
    endDate: "2025-09-30",
    farmId: "farm-001",
    farmName: "Al-Rashid Farm",
    farmNameAr: "مزرعة الراشد",
    totalAreaHa: 28.0,
    targetYieldTons: 55,
    actualYieldTons: 52,
    budgetSar: 180000,
    spentSar: 165000,
    progress: 100,
    crops: [
      {
        id: "sc-004",
        name: "Tomato",
        nameAr: "طماطم",
        variety: "Heinz 1370",
        varietyAr: "هاينز 1370",
        category: "vegetables",
        areaHa: 8.0,
        plantingDate: "2025-05-10",
        expectedHarvestDate: "2025-09-15",
        plowingDate: "2025-04-20",
        seedingDate: "2025-05-10",
        growthStages: [
          { id: "gs-t-1", name: "Transplanting", nameAr: "الشتل", durationDays: 10, description: "Seedling establishment", descriptionAr: "تثبيت الشتلات", waterMultiplier: 0.6 },
          { id: "gs-t-2", name: "Vegetative", nameAr: "النمو الخضري", durationDays: 30, description: "Vine growth", descriptionAr: "نمو العرش", waterMultiplier: 0.8 },
          { id: "gs-t-3", name: "Flowering", nameAr: "الإزهار", durationDays: 20, description: "Flower clusters form", descriptionAr: "تكون العناقيد الزهرية", waterMultiplier: 1.0 },
          { id: "gs-t-4", name: "Fruiting", nameAr: "الإثمار", durationDays: 30, description: "Fruit development", descriptionAr: "تطور الثمار", waterMultiplier: 1.1 },
          { id: "gs-t-5", name: "Ripening", nameAr: "النضج", durationDays: 20, description: "Fruit ripening and harvest", descriptionAr: "نضج الثمار والحصاد", waterMultiplier: 0.7 },
        ],
        fertilizerPlan: [
          { id: "f-t-1", stage: "Pre-planting", stageAr: "قبل الزراعة", product: "Compost + DAP", productAr: "كمبوست + داب", rateKgPerHa: 200, method: "Band", methodAr: "سطور", timing: "Before transplanting", timingAr: "قبل الشتل", notes: "Mix organic with mineral", notesAr: "خلط عضوي مع معدني" },
          { id: "f-t-2", stage: "Fruiting", stageAr: "الإثمار", product: "Calcium Nitrate", productAr: "نترات الكالسيوم", rateKgPerHa: 80, method: "Fertigation", methodAr: "تسميد مع الري", timing: "Weekly during fruiting", timingAr: "أسبوعياً أثناء الإثمار", notes: "Prevents blossom end rot", notesAr: "يمنع تعفن الطرف الزهري" },
        ],
        pesticidePlan: [
          { id: "p-t-1", pest: "Tomato Leaf Miner", pestAr: "حافرة أوراق الطماطم", type: "insecticide", product: "Abamectin 1.8% EC", productAr: "أبامكتين 1.8%", activeIngredient: "Abamectin", ratePerHa: "0.5 L/ha", timing: "At first mines observed", timingAr: "عند أول ظهور لأنفاق", phi: 3, safetyNotes: "Avoid spraying in high temperatures", safetyNotesAr: "تجنب الرش في درجات الحرارة المرتفعة" },
          { id: "p-t-2", pest: "Late Blight", pestAr: "اللفحة المتأخرة", type: "fungicide", product: "Mancozeb 80% WP", productAr: "مانكوزيب 80%", activeIngredient: "Mancozeb", ratePerHa: "2.0 kg/ha", timing: "Preventive every 7-10 days in humid conditions", timingAr: "وقائياً كل 7-10 أيام في الظروف الرطبة", phi: 7, safetyNotes: "Wear full protective equipment", safetyNotesAr: "ارتداء معدات الوقاية الكاملة" },
        ],
      },
    ],
  },
  {
    id: "s-003",
    name: "Spring 2026",
    nameAr: "ربيع 2026",
    type: "spring",
    year: 2026,
    status: "planning",
    startDate: "2026-03-01",
    endDate: "2026-06-30",
    farmId: "farm-002",
    farmName: "Green Valley Farm",
    farmNameAr: "مزرعة الوادي الأخضر",
    totalAreaHa: 0,
    targetYieldTons: 80,
    budgetSar: 250000,
    spentSar: 0,
    progress: 0,
    notes: "في مرحلة التخطيط - بانتظار اعتماد الميزانية",
    crops: [],
  },
];

// =============================================================================
// Sub-Components | المكونات الفرعية
// =============================================================================

function GrowthStageTimeline({ stages }: { stages: GrowthStage[] }) {
  const totalDays = stages.reduce((sum, s) => sum + s.durationDays, 0);
  let _cumulativeDays = 0;

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
        <Sprout className="w-4 h-4 text-green-600" />
        مراحل النمو ({totalDays} يوم)
      </h4>
      <div className="relative">
        {/* Progress bar background */}
        <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden flex">
          {stages.map((stage, i) => {
            const width = (stage.durationDays / totalDays) * 100;
            const colors = [
              "bg-emerald-300", "bg-green-400", "bg-lime-400", "bg-yellow-400",
              "bg-amber-400", "bg-orange-400", "bg-red-300", "bg-rose-300",
            ];
            return (
              <div
                key={stage.id}
                className={cn(colors[i % colors.length], "h-full transition-all")}
                style={{ width: `${width}%` }}
                title={`${stage.nameAr} - ${stage.durationDays} يوم`}
              />
            );
          })}
        </div>
        {/* Stage labels */}
        <div className="mt-2 grid gap-2" style={{ gridTemplateColumns: `repeat(${Math.min(stages.length, 4)}, 1fr)` }}>
          {stages.map((stage) => {
            _cumulativeDays += stage.durationDays;
            return (
              <div key={stage.id} className="text-center">
                <p className="text-xs font-medium text-gray-800 dark:text-gray-200">{stage.nameAr}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{stage.durationDays} يوم</p>
                {stage.nutrientRequirements && (
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                    N:{stage.nutrientRequirements.nitrogen} P:{stage.nutrientRequirements.phosphorus} K:{stage.nutrientRequirements.potassium}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function FertilizerPlanTable({ plan }: { plan: FertilizerRecommendation[] }) {
  if (plan.length === 0) return null;
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
        <FlaskConical className="w-4 h-4 text-purple-600" />
        توصيات التسميد
      </h4>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="text-right py-2 px-3 text-gray-500 dark:text-gray-400 font-medium">المرحلة</th>
              <th className="text-right py-2 px-3 text-gray-500 dark:text-gray-400 font-medium">المنتج</th>
              <th className="text-right py-2 px-3 text-gray-500 dark:text-gray-400 font-medium">المعدل (كغ/هـ)</th>
              <th className="text-right py-2 px-3 text-gray-500 dark:text-gray-400 font-medium">الطريقة</th>
              <th className="text-right py-2 px-3 text-gray-500 dark:text-gray-400 font-medium">التوقيت</th>
            </tr>
          </thead>
          <tbody>
            {plan.map((rec) => (
              <tr key={rec.id} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td className="py-2 px-3 font-medium text-gray-800 dark:text-gray-200">{rec.stageAr}</td>
                <td className="py-2 px-3 text-gray-700 dark:text-gray-300">{rec.productAr}</td>
                <td className="py-2 px-3 text-gray-700 dark:text-gray-300">{rec.rateKgPerHa}</td>
                <td className="py-2 px-3 text-gray-600 dark:text-gray-400">{rec.methodAr}</td>
                <td className="py-2 px-3 text-gray-600 dark:text-gray-400">{rec.timingAr}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PesticidePlanTable({ plan }: { plan: PesticideRecommendation[] }) {
  if (plan.length === 0) return null;
  const typeLabels: Record<string, { label: string; color: string }> = {
    fungicide: { label: "مبيد فطري", color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300" },
    insecticide: { label: "مبيد حشري", color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300" },
    herbicide: { label: "مبيد أعشاب", color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300" },
  };

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
        <Bug className="w-4 h-4 text-red-600" />
        المبيدات الوقائية
      </h4>
      <div className="space-y-3">
        {plan.map((rec) => {
          const typeConfig = typeLabels[rec.type] ?? typeLabels.insecticide ?? { label: rec.type, color: "bg-gray-100 text-gray-700" };
          return (
            <div key={rec.id} className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3 border border-gray-100 dark:border-gray-700">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={cn("text-xs px-2 py-0.5 rounded-full font-medium", typeConfig.color)}>
                      {typeConfig.label}
                    </span>
                    <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">{rec.pestAr}</span>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    <span className="font-medium">المنتج:</span> {rec.productAr} ({rec.ratePerHa})
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    <span className="font-medium">التوقيت:</span> {rec.timingAr}
                  </p>
                </div>
                <div className="text-left shrink-0">
                  <span className="text-xs bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300 px-2 py-1 rounded-full">
                    PHI: {rec.phi} يوم
                  </span>
                </div>
              </div>
              <div className="mt-2 flex items-start gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-500 mt-0.5 shrink-0" />
                <p className="text-xs text-amber-700 dark:text-amber-400">{rec.safetyNotesAr}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function CropDetailPanel({ crop, onClose }: { crop: SeasonCrop; onClose: () => void }) {
  const [activeTab, setActiveTab] = useState<"stages" | "fertilizer" | "pesticide">("stages");
  const tabs = [
    { key: "stages" as const, label: "مراحل النمو", icon: Sprout },
    { key: "fertilizer" as const, label: "التسميد", icon: FlaskConical },
    { key: "pesticide" as const, label: "المبيدات", icon: Bug },
  ];

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-l from-sahool-600 to-sahool-700 p-4 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold">{crop.nameAr}</h3>
            <p className="text-sahool-100 text-sm">{crop.varietyAr} • {CATEGORY_LABELS[crop.category]} • {crop.areaHa} هكتار</p>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-white/20 rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        {/* Dates */}
        <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-white/10 rounded-lg p-2">
            <p className="text-xs text-sahool-200">تاريخ الحراثة</p>
            <p className="text-sm font-medium">{formatDate(crop.plowingDate)}</p>
          </div>
          <div className="bg-white/10 rounded-lg p-2">
            <p className="text-xs text-sahool-200">تاريخ البذر</p>
            <p className="text-sm font-medium">{formatDate(crop.seedingDate)}</p>
          </div>
          <div className="bg-white/10 rounded-lg p-2">
            <p className="text-xs text-sahool-200">تاريخ الزراعة</p>
            <p className="text-sm font-medium">{formatDate(crop.plantingDate)}</p>
          </div>
          <div className="bg-white/10 rounded-lg p-2">
            <p className="text-xs text-sahool-200">الحصاد المتوقع</p>
            <p className="text-sm font-medium">{formatDate(crop.expectedHarvestDate)}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={cn(
              "flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors",
              activeTab === tab.key
                ? "text-sahool-700 dark:text-sahool-400 border-b-2 border-sahool-600"
                : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
            )}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-4">
        {activeTab === "stages" && <GrowthStageTimeline stages={crop.growthStages} />}
        {activeTab === "fertilizer" && <FertilizerPlanTable plan={crop.fertilizerPlan} />}
        {activeTab === "pesticide" && <PesticidePlanTable plan={crop.pesticidePlan} />}
      </div>
    </div>
  );
}

function CreateSeasonModal({ onClose, onSubmit }: { onClose: () => void; onSubmit: (data: Partial<Season>) => void }) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    nameAr: "",
    type: "winter" as SeasonType,
    year: 2026,
    startDate: "",
    endDate: "",
    farmNameAr: "",
    targetYieldTons: 0,
    budgetSar: 0,
    notes: "",
    selectedCrop: "",
    cropVariety: "",
    cropArea: 0,
    plowingDate: "",
    seedingDate: "",
  });

  const AVAILABLE_CROPS = [
    { value: "wheat", label: "قمح", category: "cereals" },
    { value: "barley", label: "شعير", category: "cereals" },
    { value: "corn", label: "ذرة", category: "cereals" },
    { value: "sorghum", label: "ذرة رفيعة", category: "cereals" },
    { value: "tomato", label: "طماطم", category: "vegetables" },
    { value: "onion", label: "بصل", category: "vegetables" },
    { value: "potato", label: "بطاطس", category: "vegetables" },
    { value: "pepper", label: "فلفل", category: "vegetables" },
    { value: "alfalfa", label: "برسيم حجازي", category: "forage" },
    { value: "date_palm", label: "نخيل تمر", category: "fruits" },
    { value: "mango", label: "مانجو", category: "fruits" },
    { value: "citrus", label: "حمضيات", category: "fruits" },
    { value: "coffee", label: "بن", category: "industrial" },
    { value: "sesame", label: "سمسم", category: "industrial" },
    { value: "lentil", label: "عدس", category: "legumes" },
    { value: "chickpea", label: "حمص", category: "legumes" },
  ];

  const handleSubmit = () => {
    onSubmit({
      nameAr: formData.nameAr,
      type: formData.type,
      year: formData.year,
      startDate: formData.startDate,
      endDate: formData.endDate,
      farmNameAr: formData.farmNameAr,
      targetYieldTons: formData.targetYieldTons,
      budgetSar: formData.budgetSar,
      notes: formData.notes,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div
        className="bg-white dark:bg-gray-900 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 p-5 flex items-center justify-between z-10">
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">إنشاء موسم زراعي جديد</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">الخطوة {step} من 3</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Step indicators */}
        <div className="px-5 pt-4">
          <div className="flex items-center gap-2">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex-1 flex items-center gap-2">
                <div className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors",
                  s <= step ? "bg-sahool-600 text-white" : "bg-gray-200 dark:bg-gray-700 text-gray-500"
                )}>
                  {s < step ? <Check className="w-4 h-4" /> : s}
                </div>
                <span className={cn("text-xs", s <= step ? "text-sahool-700 dark:text-sahool-400 font-medium" : "text-gray-400")}>
                  {s === 1 ? "بيانات الموسم" : s === 2 ? "اختيار المحصول" : "التواريخ والملاحظات"}
                </span>
                {s < 3 && <div className={cn("flex-1 h-0.5", s < step ? "bg-sahool-600" : "bg-gray-200 dark:bg-gray-700")} />}
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="p-5 space-y-5">
          {step === 1 && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">اسم الموسم</label>
                <input
                  type="text"
                  value={formData.nameAr}
                  onChange={(e) => setFormData({ ...formData, nameAr: e.target.value })}
                  placeholder="مثال: شتاء 2026/2027"
                  className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">نوع الموسم</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value as SeasonType })}
                    className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  >
                    {(Object.entries(SEASON_TYPE_CONFIG) as [SeasonType, typeof SEASON_TYPE_CONFIG[SeasonType]][]).map(([key, val]) => (
                      <option key={key} value={key}>{val.labelAr}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">السنة</label>
                  <input
                    type="number"
                    value={formData.year}
                    onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) })}
                    className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">اسم المزرعة</label>
                <input
                  type="text"
                  value={formData.farmNameAr}
                  onChange={(e) => setFormData({ ...formData, farmNameAr: e.target.value })}
                  placeholder="مثال: مزرعة الراشد"
                  className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">الإنتاج المستهدف (طن)</label>
                  <input
                    type="number"
                    value={formData.targetYieldTons || ""}
                    onChange={(e) => setFormData({ ...formData, targetYieldTons: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">الميزانية (ريال)</label>
                  <input
                    type="number"
                    value={formData.budgetSar || ""}
                    onChange={(e) => setFormData({ ...formData, budgetSar: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  />
                </div>
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">اختر المحصول</label>
                <select
                  value={formData.selectedCrop}
                  onChange={(e) => setFormData({ ...formData, selectedCrop: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                >
                  <option value="">-- اختر محصول --</option>
                  {Object.entries(
                    AVAILABLE_CROPS.reduce((acc, crop) => {
                      const cat = CATEGORY_LABELS[crop.category as CropCategory] || crop.category;
                      if (!acc[cat]) acc[cat] = [];
                      acc[cat].push(crop);
                      return acc;
                    }, {} as Record<string, typeof AVAILABLE_CROPS>)
                  ).map(([cat, crops]) => (
                    <optgroup key={cat} label={cat}>
                      {crops.map((c) => (
                        <option key={c.value} value={c.value}>{c.label}</option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">الصنف</label>
                  <input
                    type="text"
                    value={formData.cropVariety}
                    onChange={(e) => setFormData({ ...formData, cropVariety: e.target.value })}
                    placeholder="مثال: سخا 95"
                    className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">المساحة (هكتار)</label>
                  <input
                    type="number"
                    value={formData.cropArea || ""}
                    onChange={(e) => setFormData({ ...formData, cropArea: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  />
                </div>
              </div>
              {formData.selectedCrop && (
                <div className="bg-sahool-50 dark:bg-sahool-900/20 rounded-xl p-4 border border-sahool-200 dark:border-sahool-800">
                  <p className="text-sm text-sahool-700 dark:text-sahool-300 font-medium flex items-center gap-2">
                    <Leaf className="w-4 h-4" />
                    سيتم تحميل مراحل النمو وتوصيات التسميد والمبيدات تلقائياً بناءً على المحصول المختار
                  </p>
                </div>
              )}
            </>
          )}

          {step === 3 && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">تاريخ بداية الموسم</label>
                  <input
                    type="date"
                    value={formData.startDate}
                    onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">تاريخ نهاية الموسم</label>
                  <input
                    type="date"
                    value={formData.endDate}
                    onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">تاريخ الحراثة</label>
                  <input
                    type="date"
                    value={formData.plowingDate}
                    onChange={(e) => setFormData({ ...formData, plowingDate: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">تاريخ البذر</label>
                  <input
                    type="date"
                    value={formData.seedingDate}
                    onChange={(e) => setFormData({ ...formData, seedingDate: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">ملاحظات</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows={3}
                  placeholder="أي ملاحظات إضافية..."
                  className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 resize-none"
                />
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 p-5 flex items-center justify-between">
          <button
            onClick={() => step > 1 ? setStep(step - 1) : onClose()}
            className="px-5 py-2.5 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            {step > 1 ? "السابق" : "إلغاء"}
          </button>
          <button
            onClick={() => step < 3 ? setStep(step + 1) : handleSubmit()}
            className="px-5 py-2.5 bg-sahool-600 text-white rounded-xl hover:bg-sahool-700 transition-colors font-medium"
          >
            {step < 3 ? "التالي" : "إنشاء الموسم"}
          </button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Main Page Component | المكون الرئيسي
// =============================================================================

export default function SeasonsPage() {
  const [seasons] = useState<Season[]>(MOCK_SEASONS);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [expandedSeason, setExpandedSeason] = useState<string | null>("s-001");
  const [selectedCrop, setSelectedCrop] = useState<SeasonCrop | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const filteredSeasons = useMemo(() => {
    return seasons.filter((s) => {
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        if (!s.nameAr.includes(q) && !s.name.toLowerCase().includes(q) && !s.farmNameAr.includes(q)) return false;
      }
      if (statusFilter && s.status !== statusFilter) return false;
      if (typeFilter && s.type !== typeFilter) return false;
      return true;
    });
  }, [seasons, searchQuery, statusFilter, typeFilter]);

  const stats = useMemo(() => ({
    total: seasons.length,
    active: seasons.filter(s => s.status === "active").length,
    completed: seasons.filter(s => s.status === "completed").length,
    totalArea: seasons.reduce((sum, s) => sum + s.totalAreaHa, 0),
    totalBudget: seasons.reduce((sum, s) => sum + s.budgetSar, 0),
    totalCrops: seasons.reduce((sum, s) => sum + s.crops.length, 0),
  }), [seasons]);

  const handleCreateSeason = useCallback((_data: Partial<Season>) => {
    // In production, this would call the API
    // For now, just close the modal
  }, []);

  return (
    <div className="p-6">
      <Header
        title="المواسم الزراعية"
        subtitle={`${seasons.length} موسم • ${stats.totalCrops} محصول • ${stats.totalArea} هكتار`}
      />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي المواسم</p>
        </div>
        <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
          <p className="text-2xl font-bold text-green-600">{stats.active}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">مواسم نشطة</p>
        </div>
        <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
          <p className="text-2xl font-bold text-blue-600">{stats.completed}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">مكتملة</p>
        </div>
        <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.totalCrops}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">المحاصيل</p>
        </div>
        <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.totalArea}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">هكتار</p>
        </div>
        <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{formatNumber(stats.totalBudget)}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">الميزانية (ريال)</p>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-6 bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث بالاسم أو المزرعة..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value="">كل الحالات</option>
            {Object.entries(STATUS_CONFIG).map(([key, val]) => (
              <option key={key} value={key}>{val.labelAr}</option>
            ))}
          </select>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value="">كل الأنواع</option>
            {(Object.entries(SEASON_TYPE_CONFIG) as [SeasonType, typeof SEASON_TYPE_CONFIG[SeasonType]][]).map(([key, val]) => (
              <option key={key} value={key}>{val.labelAr}</option>
            ))}
          </select>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            إنشاء موسم
          </button>
        </div>
      </div>

      {/* Seasons List */}
      <div className="mt-6 space-y-4">
        {filteredSeasons.length === 0 ? (
          <div className="bg-white dark:bg-gray-900 rounded-xl p-12 text-center border border-gray-100 dark:border-gray-800">
            <Calendar className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">لا توجد مواسم مطابقة للبحث</p>
          </div>
        ) : (
          filteredSeasons.map((season) => {
            const isExpanded = expandedSeason === season.id;
            const typeConfig = SEASON_TYPE_CONFIG[season.type];
            const statusConfig = STATUS_CONFIG[season.status];
            const TypeIcon = typeConfig.icon;
            const budgetPercent = season.budgetSar > 0 ? Math.round((season.spentSar / season.budgetSar) * 100) : 0;

            return (
              <div key={season.id} className="bg-white dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-800 overflow-hidden">
                {/* Season Header */}
                <div
                  className="p-5 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                  onClick={() => setExpandedSeason(isExpanded ? null : season.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center", typeConfig.color)}>
                        <TypeIcon className="w-6 h-6" />
                      </div>
                      <div>
                        <div className="flex items-center gap-3">
                          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">{season.nameAr}</h3>
                          <span className={cn("text-xs px-2.5 py-1 rounded-full font-medium", statusConfig.color)}>
                            {statusConfig.labelAr}
                          </span>
                        </div>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                          {season.farmNameAr} • {formatDate(season.startDate)} - {formatDate(season.endDate)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="hidden md:flex items-center gap-6 text-center">
                        <div>
                          <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{season.crops.length}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">محاصيل</p>
                        </div>
                        <div>
                          <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{season.totalAreaHa}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">هكتار</p>
                        </div>
                        <div>
                          <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{season.progress}%</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">التقدم</p>
                        </div>
                      </div>
                      {isExpanded ? (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                  </div>

                  {/* Progress bar */}
                  {season.progress > 0 && (
                    <div className="mt-3 flex items-center gap-3">
                      <div className="flex-1 h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-sahool-500 rounded-full transition-all"
                          style={{ width: `${season.progress}%` }}
                        />
                      </div>
                      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                        <span>الميزانية: {formatNumber(season.spentSar)} / {formatNumber(season.budgetSar)} ريال ({budgetPercent}%)</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Expanded Content - Crops */}
                {isExpanded && (
                  <div className="border-t border-gray-100 dark:border-gray-800 p-5">
                    {season.crops.length === 0 ? (
                      <div className="text-center py-8">
                        <Sprout className="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                        <p className="text-gray-500 dark:text-gray-400">لم تتم إضافة محاصيل لهذا الموسم بعد</p>
                        <button disabled className="mt-3 text-sm text-sahool-600 font-medium disabled:opacity-40 disabled:cursor-not-allowed" title="إضافة محصول (قريبًا)">
                          + إضافة محصول
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <h4 className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                          المحاصيل ({season.crops.length})
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                          {season.crops.map((crop) => (
                            <div
                              key={crop.id}
                              onClick={() => setSelectedCrop(selectedCrop?.id === crop.id ? null : crop)}
                              className={cn(
                                "p-4 rounded-xl border cursor-pointer transition-all",
                                selectedCrop?.id === crop.id
                                  ? "border-sahool-500 bg-sahool-50 dark:bg-sahool-900/20 ring-1 ring-sahool-500"
                                  : "border-gray-200 dark:border-gray-700 hover:border-sahool-300 dark:hover:border-sahool-700 hover:shadow-sm"
                              )}
                            >
                              <div className="flex items-start justify-between">
                                <div>
                                  <h5 className="font-bold text-gray-900 dark:text-gray-100">{crop.nameAr}</h5>
                                  <p className="text-sm text-gray-500 dark:text-gray-400">{crop.varietyAr}</p>
                                </div>
                                <span className="text-xs bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 px-2 py-1 rounded-full">
                                  {CATEGORY_LABELS[crop.category]}
                                </span>
                              </div>
                              <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                                <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
                                  <Leaf className="w-3.5 h-3.5 text-green-500" />
                                  {crop.areaHa} هكتار
                                </div>
                                <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
                                  <Calendar className="w-3.5 h-3.5 text-blue-500" />
                                  {formatDate(crop.plantingDate)}
                                </div>
                                <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
                                  <Sprout className="w-3.5 h-3.5 text-emerald-500" />
                                  {crop.growthStages.length} مراحل
                                </div>
                                <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
                                  <FlaskConical className="w-3.5 h-3.5 text-purple-500" />
                                  {crop.fertilizerPlan.length} توصيات
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>

                        {/* Selected Crop Detail */}
                        {selectedCrop && season.crops.find(c => c.id === selectedCrop.id) && (
                          <CropDetailPanel
                            crop={selectedCrop}
                            onClose={() => setSelectedCrop(null)}
                          />
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Create Season Modal */}
      {showCreateModal && (
        <CreateSeasonModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateSeason}
        />
      )}
    </div>
  );
}
