/**
 * Analytics Feature - Mock Data (Development Fallback)
 * بيانات وهمية للتحليلات
 *
 * Separated from the API layer to reduce client bundle size.
 * This data is used as fallback when the API is unavailable.
 */

import type {
  AnalyticsSummary,
  YieldData,
  CostData,
  RevenueData,
  KPIMetric,
  ResourceUsage,
} from "./types";

export const MOCK_SUMMARY: AnalyticsSummary = {
  totalFields: 3,
  totalArea: 13.5,
  totalYield: 45000,
  totalRevenue: 135000,
  totalCost: 67500,
  totalProfit: 67500,
  averageYieldPerHectare: 3333.33,
  topPerformingField: {
    id: "1",
    name: "North Field",
    nameAr: "الحقل الشمالي",
    yieldPerHectare: 3636.36,
  },
  period: {
    start: new Date(
      new Date().setMonth(new Date().getMonth() - 6),
    ).toISOString(),
    end: new Date().toISOString(),
  },
};

export const MOCK_YIELD_DATA: YieldData[] = [
  {
    fieldId: "1",
    fieldName: "North Field",
    fieldNameAr: "الحقل الشمالي",
    cropType: "Wheat",
    cropTypeAr: "قمح",
    totalYield: 20000,
    expectedYield: 19000,
    yieldPerHectare: 3636.36,
    area: 5.5,
    season: "Winter 2025",
    harvestDate: new Date().toISOString(),
    variance: 5.26,
    timeSeries: [
      { date: "2025-01", value: 0, label: "Jan", labelAr: "يناير" },
      { date: "2025-02", value: 0, label: "Feb", labelAr: "فبراير" },
      { date: "2025-03", value: 5000, label: "Mar", labelAr: "مارس" },
      { date: "2025-04", value: 15000, label: "Apr", labelAr: "أبريل" },
      { date: "2025-05", value: 20000, label: "May", labelAr: "مايو" },
    ],
  },
  {
    fieldId: "2",
    fieldName: "South Field",
    fieldNameAr: "الحقل الجنوبي",
    cropType: "Corn",
    cropTypeAr: "ذرة",
    totalYield: 12000,
    expectedYield: 13000,
    yieldPerHectare: 3750,
    area: 3.2,
    season: "Summer 2025",
    harvestDate: new Date().toISOString(),
    variance: -7.69,
    timeSeries: [
      { date: "2025-03", value: 0, label: "Mar", labelAr: "مارس" },
      { date: "2025-04", value: 0, label: "Apr", labelAr: "أبريل" },
      { date: "2025-05", value: 3000, label: "May", labelAr: "مايو" },
      { date: "2025-06", value: 8000, label: "Jun", labelAr: "يونيو" },
      { date: "2025-07", value: 12000, label: "Jul", labelAr: "يوليو" },
    ],
  },
  {
    fieldId: "3",
    fieldName: "East Field",
    fieldNameAr: "الحقل الشرقي",
    cropType: "Barley",
    cropTypeAr: "شعير",
    totalYield: 13000,
    expectedYield: 12500,
    yieldPerHectare: 2708.33,
    area: 4.8,
    season: "Winter 2025",
    harvestDate: new Date().toISOString(),
    variance: 4.0,
    timeSeries: [
      { date: "2025-01", value: 0, label: "Jan", labelAr: "يناير" },
      { date: "2025-02", value: 0, label: "Feb", labelAr: "فبراير" },
      { date: "2025-03", value: 4000, label: "Mar", labelAr: "مارس" },
      { date: "2025-04", value: 9000, label: "Apr", labelAr: "أبريل" },
      { date: "2025-05", value: 13000, label: "May", labelAr: "مايو" },
    ],
  },
];

export const MOCK_COST_DATA: CostData[] = [
  {
    fieldId: "1",
    fieldName: "North Field",
    fieldNameAr: "الحقل الشمالي",
    totalCost: 27500,
    breakdown: {
      seeds: 5500,
      fertilizers: 8250,
      pesticides: 2750,
      irrigation: 5500,
      labor: 4125,
      equipment: 1100,
      other: 275,
    },
    costPerHectare: 5000,
    period: {
      start: new Date(
        new Date().setMonth(new Date().getMonth() - 6),
      ).toISOString(),
      end: new Date().toISOString(),
    },
  },
  {
    fieldId: "2",
    fieldName: "South Field",
    fieldNameAr: "الحقل الجنوبي",
    totalCost: 16000,
    breakdown: {
      seeds: 3200,
      fertilizers: 4800,
      pesticides: 1600,
      irrigation: 3200,
      labor: 2400,
      equipment: 640,
      other: 160,
    },
    costPerHectare: 5000,
    period: {
      start: new Date(
        new Date().setMonth(new Date().getMonth() - 6),
      ).toISOString(),
      end: new Date().toISOString(),
    },
  },
  {
    fieldId: "3",
    fieldName: "East Field",
    fieldNameAr: "الحقل الشرقي",
    totalCost: 24000,
    breakdown: {
      seeds: 4800,
      fertilizers: 7200,
      pesticides: 2400,
      irrigation: 4800,
      labor: 3600,
      equipment: 960,
      other: 240,
    },
    costPerHectare: 5000,
    period: {
      start: new Date(
        new Date().setMonth(new Date().getMonth() - 6),
      ).toISOString(),
      end: new Date().toISOString(),
    },
  },
];

export const MOCK_REVENUE_DATA: RevenueData[] = [
  {
    fieldId: "1",
    fieldName: "North Field",
    fieldNameAr: "الحقل الشمالي",
    revenue: 60000,
    cost: 27500,
    profit: 32500,
    profitMargin: 54.17,
    roi: 118.18,
    period: {
      start: new Date(
        new Date().setMonth(new Date().getMonth() - 6),
      ).toISOString(),
      end: new Date().toISOString(),
    },
  },
  {
    fieldId: "2",
    fieldName: "South Field",
    fieldNameAr: "الحقل الجنوبي",
    revenue: 36000,
    cost: 16000,
    profit: 20000,
    profitMargin: 55.56,
    roi: 125,
    period: {
      start: new Date(
        new Date().setMonth(new Date().getMonth() - 6),
      ).toISOString(),
      end: new Date().toISOString(),
    },
  },
  {
    fieldId: "3",
    fieldName: "East Field",
    fieldNameAr: "الحقل الشرقي",
    revenue: 39000,
    cost: 24000,
    profit: 15000,
    profitMargin: 38.46,
    roi: 62.5,
    period: {
      start: new Date(
        new Date().setMonth(new Date().getMonth() - 6),
      ).toISOString(),
      end: new Date().toISOString(),
    },
  },
];

export const MOCK_KPI_METRICS: KPIMetric[] = [
  {
    id: "total-yield",
    name: "Total Yield",
    nameAr: "إجمالي الإنتاج",
    value: 45000,
    unit: "kg",
    unitAr: "كجم",
    change: 12.5,
    trend: "up",
    status: "good",
    icon: "TrendingUp",
    description: "Total crop yield across all fields",
    descriptionAr: "إجمالي إنتاج المحاصيل في جميع الحقول",
  },
  {
    id: "total-revenue",
    name: "Total Revenue",
    nameAr: "إجمالي الإيرادات",
    value: 135000,
    unit: "SAR",
    unitAr: "ريال",
    change: 8.3,
    trend: "up",
    status: "good",
    icon: "DollarSign",
    description: "Total revenue from crop sales",
    descriptionAr: "إجمالي الإيرادات من بيع المحاصيل",
  },
  {
    id: "profit-margin",
    name: "Profit Margin",
    nameAr: "هامش الربح",
    value: 50,
    unit: "%",
    unitAr: "%",
    change: -2.1,
    trend: "down",
    status: "warning",
    icon: "Percent",
    description: "Average profit margin across all fields",
    descriptionAr: "متوسط هامش الربح في جميع الحقول",
  },
  {
    id: "water-efficiency",
    name: "Water Efficiency",
    nameAr: "كفاءة المياه",
    value: 0.85,
    unit: "m³/kg",
    unitAr: "م³/كجم",
    change: 5.6,
    trend: "up",
    status: "good",
    icon: "Droplet",
    description: "Water usage efficiency",
    descriptionAr: "كفاءة استهلاك المياه",
  },
];

export const MOCK_RESOURCE_USAGE: ResourceUsage[] = [
  {
    fieldId: "1",
    fieldName: "North Field",
    fieldNameAr: "الحقل الشمالي",
    waterUsage: 17000,
    fertilizerUsage: 825,
    pesticideUsage: 110,
    energyUsage: 2200,
    period: {
      start: new Date(
        new Date().setMonth(new Date().getMonth() - 6),
      ).toISOString(),
      end: new Date().toISOString(),
    },
    efficiency: {
      waterPerKg: 0.85,
      fertilizerPerKg: 0.041,
      energyPerKg: 0.11,
    },
  },
  {
    fieldId: "2",
    fieldName: "South Field",
    fieldNameAr: "الحقل الجنوبي",
    waterUsage: 10800,
    fertilizerUsage: 480,
    pesticideUsage: 64,
    energyUsage: 1320,
    period: {
      start: new Date(
        new Date().setMonth(new Date().getMonth() - 6),
      ).toISOString(),
      end: new Date().toISOString(),
    },
    efficiency: {
      waterPerKg: 0.9,
      fertilizerPerKg: 0.04,
      energyPerKg: 0.11,
    },
  },
  {
    fieldId: "3",
    fieldName: "East Field",
    fieldNameAr: "الحقل الشرقي",
    waterUsage: 11700,
    fertilizerUsage: 720,
    pesticideUsage: 96,
    energyUsage: 1560,
    period: {
      start: new Date(
        new Date().setMonth(new Date().getMonth() - 6),
      ).toISOString(),
      end: new Date().toISOString(),
    },
    efficiency: {
      waterPerKg: 0.9,
      fertilizerPerKg: 0.055,
      energyPerKg: 0.12,
    },
  },
];
