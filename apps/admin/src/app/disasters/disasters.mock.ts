/**
 * Disasters Page - Mock Data (Development Fallback)
 * بيانات وهمية ثابتة للتطوير - صفحة تقارير الكوارث
 *
 * This file is separated from the page component to allow tree-shaking
 * in production builds. Mock data is only loaded as a fallback when the
 * API is unavailable during development.
 */

export interface DisasterReport {
  id: string;
  type: "flood" | "drought" | "frost" | "pest" | "disease" | "storm" | "fire";
  typeAr: string;
  location: string;
  locationAr: string;
  affectedFarms: number;
  affectedArea: number;
  severity: "minor" | "moderate" | "severe" | "catastrophic";
  status: "active" | "monitoring" | "resolved" | "closed";
  damageEstimate: number;
  currency: string;
  reportedBy: string;
  reportedByAr: string;
  reportedAt: string;
  resolvedAt?: string;
  description: string;
  descriptionAr: string;
}

export const MOCK_REPORTS: DisasterReport[] = [
  {
    id: "1",
    type: "drought",
    typeAr: "جفاف",
    location: "Northern Region",
    locationAr: "المنطقة الشمالية",
    affectedFarms: 12,
    affectedArea: 450,
    severity: "severe",
    status: "active",
    damageEstimate: 500000,
    currency: "SAR",
    reportedBy: "Regional Office",
    reportedByAr: "المكتب الإقليمي",
    reportedAt: "2026-01-20",
    description: "Severe drought affecting wheat crops",
    descriptionAr: "جفاف شديد يؤثر على محاصيل القمح",
  },
  {
    id: "2",
    type: "pest",
    typeAr: "آفات",
    location: "Eastern Province",
    locationAr: "المنطقة الشرقية",
    affectedFarms: 5,
    affectedArea: 120,
    severity: "moderate",
    status: "monitoring",
    damageEstimate: 75000,
    currency: "SAR",
    reportedBy: "Farm Inspector",
    reportedByAr: "مفتش المزارع",
    reportedAt: "2026-01-22",
    description: "Locust swarm detected",
    descriptionAr: "رصد سرب جراد",
  },
  {
    id: "3",
    type: "frost",
    typeAr: "صقيع",
    location: "Central Region",
    locationAr: "المنطقة الوسطى",
    affectedFarms: 8,
    affectedArea: 200,
    severity: "minor",
    status: "resolved",
    damageEstimate: 45000,
    currency: "SAR",
    reportedBy: "Weather Station",
    reportedByAr: "محطة الطقس",
    reportedAt: "2026-01-15",
    resolvedAt: "2026-01-18",
    description: "Early morning frost damage",
    descriptionAr: "أضرار صقيع الصباح الباكر",
  },
  {
    id: "4",
    type: "flood",
    typeAr: "فيضان",
    location: "Western Province",
    locationAr: "المنطقة الغربية",
    affectedFarms: 3,
    affectedArea: 80,
    severity: "moderate",
    status: "closed",
    damageEstimate: 120000,
    currency: "SAR",
    reportedBy: "Emergency Services",
    reportedByAr: "خدمات الطوارئ",
    reportedAt: "2026-01-10",
    resolvedAt: "2026-01-14",
    description: "Flash flood from heavy rain",
    descriptionAr: "فيضان مفاجئ من الأمطار الغزيرة",
  },
  {
    id: "5",
    type: "disease",
    typeAr: "مرض",
    location: "Southern Region",
    locationAr: "المنطقة الجنوبية",
    affectedFarms: 15,
    affectedArea: 350,
    severity: "catastrophic",
    status: "active",
    damageEstimate: 850000,
    currency: "SAR",
    reportedBy: "Agriculture Ministry",
    reportedByAr: "وزارة الزراعة",
    reportedAt: "2026-01-24",
    description: "Red Palm Weevil outbreak",
    descriptionAr: "انتشار سوسة النخيل الحمراء",
  },
];
