/**
 * Research Page - Mock Data (Development Fallback)
 * بيانات وهمية ثابتة للتطوير - صفحة إدارة الأبحاث
 *
 * This file is separated from the page component to allow tree-shaking
 * in production builds. Mock data is only loaded as a fallback when the
 * API is unavailable during development.
 */

export interface ResearchTrial {
  id: string;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
  crop: string;
  cropAr: string;
  status: "planning" | "active" | "completed" | "on_hold" | "cancelled";
  startDate: string;
  endDate: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  researchers: number;
  progress: number;
  budget: number;
  spent: number;
  currency: string;
  findings?: string;
  findingsAr?: string;
}

export const MOCK_TRIALS: ResearchTrial[] = [
  {
    id: "1",
    name: "Wheat Drought Resistance Trial",
    nameAr: "تجربة مقاومة القمح للجفاف",
    description: "Testing new drought-resistant wheat varieties",
    descriptionAr: "اختبار أصناف قمح جديدة مقاومة للجفاف",
    crop: "Wheat",
    cropAr: "قمح",
    status: "active",
    startDate: "2025-10-01",
    endDate: "2026-04-30",
    fieldId: "F001",
    fieldName: "Research Field A",
    fieldNameAr: "حقل البحث أ",
    researchers: 4,
    progress: 65,
    budget: 150000,
    spent: 95000,
    currency: "SAR",
  },
  {
    id: "2",
    name: "Organic Fertilizer Effectiveness",
    nameAr: "فعالية السماد العضوي",
    description: "Comparing organic vs chemical fertilizers on tomatoes",
    descriptionAr: "مقارنة الأسمدة العضوية والكيميائية على الطماطم",
    crop: "Tomato",
    cropAr: "طماطم",
    status: "completed",
    startDate: "2025-06-01",
    endDate: "2025-12-15",
    fieldId: "F002",
    fieldName: "Greenhouse B",
    fieldNameAr: "الصوبة ب",
    researchers: 3,
    progress: 100,
    budget: 80000,
    spent: 72000,
    currency: "SAR",
    findings: "Organic fertilizer showed 15% yield improvement",
    findingsAr: "أظهر السماد العضوي تحسناً في المحصول بنسبة 15%",
  },
  {
    id: "3",
    name: "Date Palm Irrigation Optimization",
    nameAr: "تحسين ري النخيل",
    description: "Smart irrigation scheduling for date palms",
    descriptionAr: "جدولة الري الذكي لأشجار النخيل",
    crop: "Date Palm",
    cropAr: "نخيل",
    status: "active",
    startDate: "2025-11-15",
    endDate: "2026-11-15",
    fieldId: "F003",
    fieldName: "Palm Grove C",
    fieldNameAr: "بستان النخيل ج",
    researchers: 5,
    progress: 25,
    budget: 200000,
    spent: 45000,
    currency: "SAR",
  },
  {
    id: "4",
    name: "Pest Biocontrol Study",
    nameAr: "دراسة المكافحة الحيوية للآفات",
    description: "Natural predators for pest management",
    descriptionAr: "استخدام المفترسات الطبيعية لمكافحة الآفات",
    crop: "Multiple",
    cropAr: "متعدد",
    status: "planning",
    startDate: "2026-03-01",
    endDate: "2026-09-30",
    fieldId: "F004",
    fieldName: "Research Field D",
    fieldNameAr: "حقل البحث د",
    researchers: 2,
    progress: 0,
    budget: 120000,
    spent: 5000,
    currency: "SAR",
  },
  {
    id: "5",
    name: "Soil Health Monitoring",
    nameAr: "مراقبة صحة التربة",
    description: "Long-term soil quality assessment",
    descriptionAr: "تقييم جودة التربة على المدى الطويل",
    crop: "N/A",
    cropAr: "غير محدد",
    status: "on_hold",
    startDate: "2025-08-01",
    endDate: "2026-08-01",
    fieldId: "F005",
    fieldName: "Multiple Fields",
    fieldNameAr: "حقول متعددة",
    researchers: 3,
    progress: 35,
    budget: 90000,
    spent: 32000,
    currency: "SAR",
  },
];
