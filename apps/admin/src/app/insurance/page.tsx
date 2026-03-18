"use client";

// Crop Insurance Management Page
// صفحة إدارة التأمين الزراعي

import React, { useState, useMemo } from "react";
import Header from "@/components/layout/Header";
import StatCard from "@/components/ui/StatCard";
import { cn } from "@/lib/utils";
import {
  Shield,
  FileText,
  AlertCircle,
  TrendingUp,
  CloudRain,
  Bug,
  CloudSnow,
  Waves,
  CheckCircle,
  Clock,
  XCircle,
  ChevronRight,
  Calendar,
  MapPin,
  DollarSign,
  BarChart2,
  Leaf,
  Info,
} from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────────────────

type PolicyType = "traditional" | "parametric" | "weather_index";
type PolicyStatus = "active" | "pending" | "expired" | "claimed";
type RiskLevel = "low" | "moderate" | "high";
type ClaimType = "drought" | "pest" | "hail" | "flood";
type ClaimStatus = "submitted" | "under_review" | "approved" | "rejected";
type ActiveTab = "policies" | "claims" | "risk";

interface InsurancePolicy {
  id: string;
  policyNumber: string;
  farmerName: string;
  crop: string;
  cropAr: string;
  fieldArea_ha: number;
  coverageAmount_SAR: number;
  premium_SAR: number;
  type: PolicyType;
  status: PolicyStatus;
  startDate: string;
  endDate: string;
  riskLevel: RiskLevel;
}

interface InsuranceClaim {
  id: string;
  claimNumber: string;
  policyId: string;
  type: ClaimType;
  amount_SAR: number;
  status: ClaimStatus;
  filedDate: string;
  description: string;
  descriptionAr: string;
}

// ─── Mock Data ───────────────────────────────────────────────────────────────

const MOCK_POLICIES: InsurancePolicy[] = [
  {
    id: "pol-001",
    policyNumber: "POL-001",
    farmerName: "أحمد الراشدي",
    crop: "Wheat",
    cropAr: "قمح",
    fieldArea_ha: 5.2,
    coverageAmount_SAR: 150000,
    premium_SAR: 4500,
    type: "traditional",
    status: "active",
    startDate: "2025-10-01",
    endDate: "2026-06-30",
    riskLevel: "low",
  },
  {
    id: "pol-002",
    policyNumber: "POL-002",
    farmerName: "محمد الحميري",
    crop: "Barley",
    cropAr: "شعير",
    fieldArea_ha: 3.8,
    coverageAmount_SAR: 95000,
    premium_SAR: 3200,
    type: "parametric",
    status: "active",
    startDate: "2025-11-01",
    endDate: "2026-05-31",
    riskLevel: "moderate",
  },
  {
    id: "pol-003",
    policyNumber: "POL-003",
    farmerName: "علي المقبلي",
    crop: "Tomato",
    cropAr: "طماطم",
    fieldArea_ha: 2.1,
    coverageAmount_SAR: 200000,
    premium_SAR: 8000,
    type: "weather_index",
    status: "active",
    startDate: "2025-09-15",
    endDate: "2026-03-15",
    riskLevel: "high",
  },
  {
    id: "pol-004",
    policyNumber: "POL-004",
    farmerName: "خالد الزبيدي",
    crop: "Dates",
    cropAr: "تمر",
    fieldArea_ha: 4.5,
    coverageAmount_SAR: 300000,
    premium_SAR: 6000,
    type: "traditional",
    status: "active",
    startDate: "2025-08-01",
    endDate: "2026-09-30",
    riskLevel: "low",
  },
  {
    id: "pol-005",
    policyNumber: "POL-005",
    farmerName: "سالم العمري",
    crop: "Coffee",
    cropAr: "قهوة",
    fieldArea_ha: 3.2,
    coverageAmount_SAR: 180000,
    premium_SAR: 7500,
    type: "parametric",
    status: "pending",
    startDate: "2026-01-01",
    endDate: "2026-12-31",
    riskLevel: "moderate",
  },
  {
    id: "pol-006",
    policyNumber: "POL-006",
    farmerName: "يوسف الشرعبي",
    crop: "Sorghum",
    cropAr: "ذرة رفيعة",
    fieldArea_ha: 4.8,
    coverageAmount_SAR: 120000,
    premium_SAR: 3800,
    type: "weather_index",
    status: "expired",
    startDate: "2024-06-01",
    endDate: "2025-02-28",
    riskLevel: "high",
  },
];

const MOCK_CLAIMS: InsuranceClaim[] = [
  {
    id: "clm-001",
    claimNumber: "CLM-001",
    policyId: "pol-003",
    type: "drought",
    amount_SAR: 85000,
    status: "under_review",
    filedDate: "2026-02-10",
    description: "Severe drought caused crop loss in tomato field",
    descriptionAr: "أدى الجفاف الشديد إلى خسارة محصول الطماطم",
  },
  {
    id: "clm-002",
    claimNumber: "CLM-002",
    policyId: "pol-002",
    type: "hail",
    amount_SAR: 45000,
    status: "approved",
    filedDate: "2026-01-22",
    description: "Hailstorm damaged barley crop",
    descriptionAr: "تسببت عاصفة البرد في إتلاف محصول الشعير",
  },
  {
    id: "clm-003",
    claimNumber: "CLM-003",
    policyId: "pol-006",
    type: "pest",
    amount_SAR: 60000,
    status: "submitted",
    filedDate: "2026-03-01",
    description: "Pest infestation caused significant damage to sorghum",
    descriptionAr: "تسبب تفشي الآفات في أضرار جسيمة لمحصول الذرة الرفيعة",
  },
  {
    id: "clm-004",
    claimNumber: "CLM-004",
    policyId: "pol-001",
    type: "flood",
    amount_SAR: 30000,
    status: "rejected",
    filedDate: "2025-12-15",
    description: "Flash flood affected wheat field boundary areas",
    descriptionAr: "أثر السيل على مناطق حدود حقل القمح",
  },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────

const POLICY_TYPE_LABELS: Record<PolicyType, string> = {
  traditional: "تقليدي",
  parametric: "بارامتري",
  weather_index: "مؤشر الطقس",
};

const POLICY_TYPE_COLORS: Record<PolicyType, string> = {
  traditional: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
  parametric: "bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300",
  weather_index: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/40 dark:text-cyan-300",
};

const POLICY_STATUS_LABELS: Record<PolicyStatus, string> = {
  active: "نشط",
  pending: "معلق",
  expired: "منتهي",
  claimed: "مطالب به",
};

const POLICY_STATUS_COLORS: Record<PolicyStatus, string> = {
  active: "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300",
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300",
  expired: "bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400",
  claimed: "bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300",
};

const RISK_LEVEL_LABELS: Record<RiskLevel, string> = {
  low: "منخفض",
  moderate: "متوسط",
  high: "مرتفع",
};

const RISK_LEVEL_COLORS: Record<RiskLevel, string> = {
  low: "text-green-600 dark:text-green-400",
  moderate: "text-yellow-600 dark:text-yellow-400",
  high: "text-red-600 dark:text-red-400",
};

const RISK_BAR_COLORS: Record<RiskLevel, string> = {
  low: "bg-green-500",
  moderate: "bg-yellow-500",
  high: "bg-red-500",
};

const RISK_LEVEL_SCORES: Record<RiskLevel, number> = {
  low: 25,
  moderate: 55,
  high: 82,
};

const CLAIM_TYPE_LABELS: Record<ClaimType, string> = {
  drought: "جفاف",
  pest: "آفات",
  hail: "برد",
  flood: "فيضان",
};

const CLAIM_STATUS_LABELS: Record<ClaimStatus, string> = {
  submitted: "مقدمة",
  under_review: "قيد المراجعة",
  approved: "موافق عليها",
  rejected: "مرفوضة",
};

const CLAIM_STATUS_COLORS: Record<ClaimStatus, string> = {
  submitted: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
  under_review: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300",
  approved: "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300",
};

function getClaimTypeIcon(type: ClaimType) {
  const icons: Record<ClaimType, React.ReactNode> = {
    drought: <CloudRain className="w-5 h-5" />,
    pest: <Bug className="w-5 h-5" />,
    hail: <CloudSnow className="w-5 h-5" />,
    flood: <Waves className="w-5 h-5" />,
  };
  return icons[type];
}

function getClaimStatusIcon(status: ClaimStatus) {
  const icons: Record<ClaimStatus, React.ReactNode> = {
    submitted: <Clock className="w-4 h-4" />,
    under_review: <Info className="w-4 h-4" />,
    approved: <CheckCircle className="w-4 h-4" />,
    rejected: <XCircle className="w-4 h-4" />,
  };
  return icons[status];
}

function formatSAR(amount: number) {
  return amount.toLocaleString("ar-SA") + " ريال";
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("ar-SA", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

// ─── Sub-components ───────────────────────────────────────────────────────────

interface PolicyCardProps {
  policy: InsurancePolicy;
  isSelected: boolean;
  onSelect: (policy: InsurancePolicy) => void;
}

function PolicyCard({ policy, isSelected, onSelect }: PolicyCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(policy)}
      className={cn(
        "w-full text-right p-4 rounded-xl border transition-all hover:shadow-md",
        isSelected
          ? "border-sahool-500 bg-sahool-50 dark:bg-sahool-900/20 dark:border-sahool-400"
          : "border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-200 dark:hover:border-gray-600",
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-gray-900 dark:text-gray-100 truncate">
            {policy.farmerName}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
            {policy.policyNumber} • {policy.cropAr}
          </p>
        </div>
        <ChevronRight
          className={cn(
            "w-4 h-4 flex-shrink-0 mt-0.5 transition-transform",
            isSelected ? "text-sahool-600 rotate-90" : "text-gray-400",
          )}
        />
      </div>

      <div className="flex flex-wrap gap-1.5 mb-3">
        <span
          className={cn(
            "px-2 py-0.5 rounded-full text-xs font-medium",
            POLICY_TYPE_COLORS[policy.type],
          )}
        >
          {POLICY_TYPE_LABELS[policy.type]}
        </span>
        <span
          className={cn(
            "px-2 py-0.5 rounded-full text-xs font-medium",
            POLICY_STATUS_COLORS[policy.status],
          )}
        >
          {POLICY_STATUS_LABELS[policy.status]}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <p className="text-gray-400 dark:text-gray-500 text-xs">التغطية</p>
          <p className="font-medium text-gray-900 dark:text-gray-100">
            {(policy.coverageAmount_SAR / 1000).toFixed(0)}K ريال
          </p>
        </div>
        <div>
          <p className="text-gray-400 dark:text-gray-500 text-xs">القسط</p>
          <p className="font-medium text-gray-900 dark:text-gray-100">
            {policy.premium_SAR.toLocaleString()} ريال
          </p>
        </div>
      </div>

      <div className="mt-3 flex items-center gap-1.5">
        <div
          className={cn(
            "w-2 h-2 rounded-full flex-shrink-0",
            policy.riskLevel === "low"
              ? "bg-green-500"
              : policy.riskLevel === "moderate"
                ? "bg-yellow-500"
                : "bg-red-500",
          )}
        />
        <span
          className={cn(
            "text-xs font-medium",
            RISK_LEVEL_COLORS[policy.riskLevel],
          )}
        >
          مستوى المخاطر: {RISK_LEVEL_LABELS[policy.riskLevel]}
        </span>
      </div>
    </button>
  );
}

interface ClaimCardProps {
  claim: InsuranceClaim;
  policy: InsurancePolicy | undefined;
}

function ClaimCard({ claim, policy }: ClaimCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4 transition-all hover:shadow-md">
      <div className="flex items-start gap-3">
        <div
          className={cn(
            "w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0",
            claim.type === "drought"
              ? "bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400"
              : claim.type === "pest"
                ? "bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400"
                : claim.type === "hail"
                  ? "bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400"
                  : "bg-cyan-100 dark:bg-cyan-900/30 text-cyan-600 dark:text-cyan-400",
          )}
        >
          {getClaimTypeIcon(claim.type)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <p className="font-semibold text-gray-900 dark:text-gray-100">
              {claim.claimNumber}
            </p>
            <span
              className={cn(
                "flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium",
                CLAIM_STATUS_COLORS[claim.status],
              )}
            >
              {getClaimStatusIcon(claim.status)}
              {CLAIM_STATUS_LABELS[claim.status]}
            </span>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
            {CLAIM_TYPE_LABELS[claim.type]}
            {policy && (
              <span className="mr-1.5">
                • {policy.farmerName} ({policy.cropAr})
              </span>
            )}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-300 mt-1.5 leading-relaxed">
            {claim.descriptionAr}
          </p>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-gray-50 dark:border-gray-700 flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400">
          <Calendar className="w-3.5 h-3.5" />
          {formatDate(claim.filedDate)}
        </div>
        <p className="font-bold text-gray-900 dark:text-gray-100">
          {formatSAR(claim.amount_SAR)}
        </p>
      </div>
    </div>
  );
}

interface PolicyDetailPanelProps {
  policy: InsurancePolicy;
}

function PolicyDetailPanel({ policy }: PolicyDetailPanelProps) {
  const riskFactors = [
    { label: "مخاطر الطقس", labelEn: "Weather Risk", weight: 30, value: 30 },
    { label: "تقلب الإنتاجية", labelEn: "Yield Volatility", weight: 25, value: 25 },
    { label: "جودة التربة", labelEn: "Soil Quality", weight: 20, value: 20 },
    { label: "الموقع الجغرافي", labelEn: "Location", weight: 25, value: 25 },
  ];

  const score = RISK_LEVEL_SCORES[policy.riskLevel];

  return (
    <div className="space-y-5">
      {/* Policy Info */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-5">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <FileText className="w-4 h-4 text-sahool-600" />
          تفاصيل الوثيقة
        </h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b border-gray-50 dark:border-gray-700">
            <span className="text-sm text-gray-500 dark:text-gray-400">رقم الوثيقة</span>
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {policy.policyNumber}
            </span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-gray-50 dark:border-gray-700">
            <span className="text-sm text-gray-500 dark:text-gray-400">المزارع</span>
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {policy.farmerName}
            </span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-gray-50 dark:border-gray-700">
            <span className="text-sm text-gray-500 dark:text-gray-400">المحصول</span>
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {policy.cropAr}
            </span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-gray-50 dark:border-gray-700">
            <span className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5" />
              مساحة الحقل
            </span>
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {policy.fieldArea_ha} هكتار
            </span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-gray-50 dark:border-gray-700">
            <span className="text-sm text-gray-500 dark:text-gray-400">نوع التأمين</span>
            <span
              className={cn(
                "px-2 py-0.5 rounded-full text-xs font-medium",
                POLICY_TYPE_COLORS[policy.type],
              )}
            >
              {POLICY_TYPE_LABELS[policy.type]}
            </span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-gray-50 dark:border-gray-700">
            <span className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              تاريخ البداية
            </span>
            <span className="text-sm text-gray-900 dark:text-gray-100">
              {formatDate(policy.startDate)}
            </span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              تاريخ الانتهاء
            </span>
            <span className="text-sm text-gray-900 dark:text-gray-100">
              {formatDate(policy.endDate)}
            </span>
          </div>
        </div>
      </div>

      {/* Coverage & Premium */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-5">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <DollarSign className="w-4 h-4 text-sahool-600" />
          حساب القسط
        </h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500 dark:text-gray-400">قيمة التغطية</span>
            <span className="font-bold text-lg text-gray-900 dark:text-gray-100">
              {formatSAR(policy.coverageAmount_SAR)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500 dark:text-gray-400">القسط السنوي</span>
            <span className="font-bold text-lg text-sahool-700 dark:text-sahool-400">
              {formatSAR(policy.premium_SAR)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500 dark:text-gray-400">نسبة القسط</span>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {((policy.premium_SAR / policy.coverageAmount_SAR) * 100).toFixed(2)}%
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500 dark:text-gray-400">قسط الهكتار الواحد</span>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {Math.round(policy.premium_SAR / policy.fieldArea_ha).toLocaleString()} ريال/هـ
            </span>
          </div>
        </div>
      </div>

      {/* Risk Assessment Breakdown */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-5">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1 flex items-center gap-2">
          <BarChart2 className="w-4 h-4 text-sahool-600" />
          تقييم المخاطر
        </h3>
        <div className="flex items-center gap-2 mb-4">
          <div
            className={cn(
              "text-3xl font-bold",
              RISK_LEVEL_COLORS[policy.riskLevel],
            )}
          >
            {score}
          </div>
          <div>
            <p
              className={cn(
                "text-sm font-semibold",
                RISK_LEVEL_COLORS[policy.riskLevel],
              )}
            >
              {RISK_LEVEL_LABELS[policy.riskLevel]}
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500">من 100</p>
          </div>
          <div className="flex-1 mr-2">
            <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full rounded-full transition-all",
                  RISK_BAR_COLORS[policy.riskLevel],
                )}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>
        </div>

        <div className="space-y-3">
          {riskFactors.map((factor) => (
            <div key={factor.labelEn}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {factor.label}
                </span>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {factor.weight}%
                </span>
              </div>
              <div className="h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-sahool-400 dark:bg-sahool-500 rounded-full"
                  style={{ width: `${factor.weight}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Main Page Component ──────────────────────────────────────────────────────

export default function InsurancePage() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("policies");
  const [selectedPolicy, setSelectedPolicy] = useState<InsurancePolicy | null>(
    MOCK_POLICIES[0] ?? null,
  );

  const stats = useMemo(() => {
    const activePolicies = MOCK_POLICIES.filter((p) => p.status === "active").length;
    const pendingClaims = MOCK_CLAIMS.filter(
      (c) => c.status === "submitted" || c.status === "under_review",
    ).length;
    const totalCoverage = MOCK_POLICIES.filter((p) => p.status === "active").reduce(
      (acc, p) => acc + p.coverageAmount_SAR,
      0,
    );
    const avgRiskScore =
      MOCK_POLICIES.reduce((acc, p) => acc + RISK_LEVEL_SCORES[p.riskLevel], 0) /
      MOCK_POLICIES.length;
    return { activePolicies, pendingClaims, totalCoverage, avgRiskScore };
  }, []);

  const tabs: { key: ActiveTab; label: string; count?: number }[] = [
    { key: "policies", label: "وثائق التأمين", count: MOCK_POLICIES.length },
    { key: "claims", label: "المطالبات", count: MOCK_CLAIMS.length },
    { key: "risk", label: "تقييم المخاطر" },
  ];

  return (
    <div className="p-6 min-h-screen bg-gray-50 dark:bg-gray-950">
      <Header
        title="التأمين الزراعي"
        subtitle="إدارة وثائق التأمين على المحاصيل وتقييم المخاطر ومعالجة المطالبات"
      />

      {/* Stats Row */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          title="وثائق نشطة"
          value={stats.activePolicies}
          icon={Shield}
          iconColor="text-green-600"
          trend={{ value: 12, isPositive: true }}
        />
        <StatCard
          title="مطالبات معلقة"
          value={stats.pendingClaims}
          icon={AlertCircle}
          iconColor="text-yellow-600"
          trend={{ value: 5, isPositive: false }}
        />
        <StatCard
          title="إجمالي التغطية (ريال)"
          value={stats.totalCoverage}
          icon={DollarSign}
          iconColor="text-sahool-600"
          trend={{ value: 8, isPositive: true }}
        />
        <StatCard
          title="متوسط درجة المخاطر"
          value={Math.round(stats.avgRiskScore)}
          icon={TrendingUp}
          iconColor="text-orange-600"
          suffix="/100"
        />
      </div>

      {/* Tab Navigation */}
      <div className="mt-6 flex items-center gap-1 bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-xl p-1 w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setActiveTab(tab.key)}
            className={cn(
              "flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all",
              activeTab === tab.key
                ? "bg-sahool-600 text-white shadow-sm"
                : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700",
            )}
          >
            {tab.label}
            {tab.count !== undefined && (
              <span
                className={cn(
                  "px-1.5 py-0.5 rounded-full text-xs",
                  activeTab === tab.key
                    ? "bg-white/20 text-white"
                    : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400",
                )}
              >
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Policies Tab */}
      {activeTab === "policies" && (
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Policy List */}
          <div className="lg:col-span-1 space-y-3">
            <div className="flex items-center justify-between mb-1">
              <h2 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                <FileText className="w-4 h-4 text-sahool-600" />
                الوثائق ({MOCK_POLICIES.length})
              </h2>
            </div>
            {MOCK_POLICIES.map((policy) => (
              <PolicyCard
                key={policy.id}
                policy={policy}
                isSelected={selectedPolicy?.id === policy.id}
                onSelect={setSelectedPolicy}
              />
            ))}
          </div>

          {/* Policy Detail Panel */}
          <div className="lg:col-span-2">
            {selectedPolicy ? (
              <PolicyDetailPanel policy={selectedPolicy} />
            ) : (
              <div className="flex flex-col items-center justify-center h-64 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 text-gray-400 dark:text-gray-600">
                <Shield className="w-12 h-12 mb-3 opacity-30" />
                <p>اختر وثيقة لعرض التفاصيل</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Claims Tab */}
      {activeTab === "claims" && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-sahool-600" />
              المطالبات ({MOCK_CLAIMS.length})
            </h2>
            <div className="flex items-center gap-3 text-sm">
              {(["submitted", "under_review", "approved", "rejected"] as ClaimStatus[]).map(
                (status) => (
                  <div key={status} className="flex items-center gap-1.5">
                    <span
                      className={cn(
                        "px-2 py-0.5 rounded-full text-xs font-medium",
                        CLAIM_STATUS_COLORS[status],
                      )}
                    >
                      {CLAIM_STATUS_LABELS[status]}
                    </span>
                    <span className="text-gray-500 dark:text-gray-400">
                      ({MOCK_CLAIMS.filter((c) => c.status === status).length})
                    </span>
                  </div>
                ),
              )}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {MOCK_CLAIMS.map((claim) => (
              <ClaimCard
                key={claim.id}
                claim={claim}
                policy={MOCK_POLICIES.find((p) => p.id === claim.policyId)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Risk Assessment Tab */}
      {activeTab === "risk" && (
        <div className="mt-6 space-y-6">
          <h2 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-sahool-600" />
            تقييم المخاطر الشامل
          </h2>

          {/* Risk Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {(["low", "moderate", "high"] as RiskLevel[]).map((level) => {
              const count = MOCK_POLICIES.filter((p) => p.riskLevel === level).length;
              const colorMap = {
                low: "bg-green-50 dark:bg-green-900/20 border-green-100 dark:border-green-800/40",
                moderate:
                  "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-100 dark:border-yellow-800/40",
                high: "bg-red-50 dark:bg-red-900/20 border-red-100 dark:border-red-800/40",
              };
              return (
                <div
                  key={level}
                  className={cn(
                    "rounded-xl border p-5 flex items-center gap-4",
                    colorMap[level],
                  )}
                >
                  <div
                    className={cn(
                      "w-12 h-12 rounded-xl flex items-center justify-center",
                      level === "low"
                        ? "bg-green-100 dark:bg-green-800/40"
                        : level === "moderate"
                          ? "bg-yellow-100 dark:bg-yellow-800/40"
                          : "bg-red-100 dark:bg-red-800/40",
                    )}
                  >
                    <Shield
                      className={cn("w-6 h-6", RISK_LEVEL_COLORS[level])}
                    />
                  </div>
                  <div>
                    <p
                      className={cn(
                        "text-2xl font-bold",
                        RISK_LEVEL_COLORS[level],
                      )}
                    >
                      {count}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      مخاطر {RISK_LEVEL_LABELS[level]}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Risk Factor Breakdown */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-5">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-5">
              توزيع عوامل المخاطر
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {[
                {
                  label: "مخاطر الطقس",
                  weight: 30,
                  icon: CloudRain,
                  color: "bg-blue-500",
                  desc: "درجات الحرارة، الأمطار، الرياح",
                },
                {
                  label: "تقلب الإنتاجية",
                  weight: 25,
                  icon: TrendingUp,
                  color: "bg-purple-500",
                  desc: "البيانات التاريخية للمحصول",
                },
                {
                  label: "جودة التربة",
                  weight: 20,
                  icon: Leaf,
                  color: "bg-green-500",
                  desc: "خصائص التربة والملوحة",
                },
                {
                  label: "الموقع الجغرافي",
                  weight: 25,
                  icon: MapPin,
                  color: "bg-orange-500",
                  desc: "التضاريس ومصادر المياه",
                },
              ].map((factor) => (
                <div
                  key={factor.label}
                  className="flex items-start gap-3 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl"
                >
                  <div className="w-10 h-10 rounded-lg bg-white dark:bg-gray-800 shadow-sm flex items-center justify-center flex-shrink-0">
                    <factor.icon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium text-gray-900 dark:text-gray-100 text-sm">
                        {factor.label}
                      </p>
                      <span className="text-sm font-bold text-gray-700 dark:text-gray-300">
                        {factor.weight}%
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                      {factor.desc}
                    </p>
                    <div className="h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                      <div
                        className={cn(
                          "h-full rounded-full",
                          factor.color,
                        )}
                        style={{ width: `${factor.weight}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Per-policy Risk Table */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-50 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                تفصيل المخاطر لكل وثيقة
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700/50">
                  <tr>
                    {["المزارع", "المحصول", "المساحة", "التغطية", "درجة المخاطر", "المستوى"].map(
                      (header) => (
                        <th
                          key={header}
                          className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase"
                        >
                          {header}
                        </th>
                      ),
                    )}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50 dark:divide-gray-700">
                  {MOCK_POLICIES.map((policy) => {
                    const score = RISK_LEVEL_SCORES[policy.riskLevel];
                    return (
                      <tr
                        key={policy.id}
                        className="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors"
                      >
                        <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100">
                          {policy.farmerName}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                          {policy.cropAr}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                          {policy.fieldArea_ha} هـ
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">
                          {(policy.coverageAmount_SAR / 1000).toFixed(0)}K ريال
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden max-w-[80px]">
                              <div
                                className={cn(
                                  "h-full rounded-full",
                                  RISK_BAR_COLORS[policy.riskLevel],
                                )}
                                style={{ width: `${score}%` }}
                              />
                            </div>
                            <span
                              className={cn(
                                "text-xs font-semibold",
                                RISK_LEVEL_COLORS[policy.riskLevel],
                              )}
                            >
                              {score}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1.5">
                            <div
                              className={cn(
                                "w-2 h-2 rounded-full",
                                policy.riskLevel === "low"
                                  ? "bg-green-500"
                                  : policy.riskLevel === "moderate"
                                    ? "bg-yellow-500"
                                    : "bg-red-500",
                              )}
                            />
                            <span
                              className={cn(
                                "text-xs font-medium",
                                RISK_LEVEL_COLORS[policy.riskLevel],
                              )}
                            >
                              {RISK_LEVEL_LABELS[policy.riskLevel]}
                            </span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
