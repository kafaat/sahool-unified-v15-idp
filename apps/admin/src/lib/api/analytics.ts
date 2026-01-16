// Analytics API Client
// عميل API للتحليلات

import { apiClient, API_URLS } from "../api";
import { logger } from "../logger";

// Profitability Analytics Types
export interface ProfitabilityData {
  summary: {
    totalRevenue: number;
    totalCosts: number;
    netProfit: number;
    profitMargin: number;
    roi: number;
  };
  byCrop: Array<{
    crop: string;
    cropAr: string;
    revenue: number;
    costs: number;
    profit: number;
    margin: number;
    area: number;
  }>;
  byMonth: Array<{
    month: string;
    revenue: number;
    costs: number;
    profit: number;
  }>;
  costBreakdown: Array<{
    category: string;
    categoryAr: string;
    amount: number;
    percentage: number;
  }>;
  seasons: Array<{
    season: string;
    seasonAr: string;
    revenue: number;
    costs: number;
    profit: number;
    crops: number;
  }>;
}

// Satellite Analytics Types
export interface SatelliteData {
  summary: {
    totalFields: number;
    lastUpdate: string;
    coverage: number;
    dataUsage: number;
  };
  fields: Array<{
    id: string;
    farmId: string;
    farmName: string;
    fieldName: string;
    area: number;
    location: { lat: number; lng: number };
    ndvi: {
      current: number;
      average: number;
      trend: "up" | "down" | "stable";
      change: number;
    };
    lastImageDate: string;
    alerts: Array<{
      type: "anomaly" | "stress" | "disease" | "pest";
      severity: "low" | "medium" | "high" | "critical";
      message: string;
      messageAr: string;
      detectedAt: string;
    }>;
  }>;
  ndviTrends: Array<{
    date: string;
    ndvi: number;
    fieldId: string;
    fieldName: string;
  }>;
}

// Profitability API Functions
export async function fetchProfitabilityData(params?: {
  period?: "month" | "quarter" | "year";
  farmId?: string;
}): Promise<ProfitabilityData> {
  try {
    const response = await apiClient.get(
      `${API_URLS.yieldEngine}/v1/profitability`,
      { params },
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch profitability data:", error);
    return generateMockProfitabilityData();
  }
}

// Satellite Analytics API Functions
export async function fetchSatelliteData(params?: {
  range?: "week" | "month" | "season";
  farmId?: string;
}): Promise<SatelliteData> {
  try {
    const response = await apiClient.get(`${API_URLS.satellite}/v1/analysis`, {
      params,
    });
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch satellite data:", error);
    return generateMockSatelliteData();
  }
}

export async function fetchNDVITrends(params?: {
  fieldId?: string;
  startDate?: string;
  endDate?: string;
}): Promise<Array<{ date: string; ndvi: number; fieldId: string }>> {
  try {
    const response = await apiClient.get(
      `${API_URLS.satellite}/v1/ndvi-trends`,
      { params },
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch NDVI trends:", error);
    return [];
  }
}

// Mock Data Generators
function generateMockProfitabilityData(): ProfitabilityData {
  const crops = [
    { crop: "wheat", cropAr: "قمح", area: 120 },
    { crop: "coffee", cropAr: "بن", area: 85 },
    { crop: "qat", cropAr: "قات", area: 95 },
    { crop: "corn", cropAr: "ذرة", area: 60 },
    { crop: "vegetables", cropAr: "خضروات", area: 40 },
  ];

  const months = [
    "يناير",
    "فبراير",
    "مارس",
    "أبريل",
    "مايو",
    "يونيو",
    "يوليو",
    "أغسطس",
    "سبتمبر",
    "أكتوبر",
    "نوفمبر",
    "ديسمبر",
  ];

  const byCrop = crops.map((crop) => {
    const revenue = crop.area * (1000 + Math.random() * 2000);
    const costs = revenue * (0.5 + Math.random() * 0.3);
    const profit = revenue - costs;
    return {
      ...crop,
      revenue,
      costs,
      profit,
      margin: (profit / revenue) * 100,
    };
  });

  const byMonth = months.map((month) => {
    const revenue = 50000 + Math.random() * 100000;
    const costs = revenue * (0.55 + Math.random() * 0.2);
    return {
      month,
      revenue,
      costs,
      profit: revenue - costs,
    };
  });

  const totalRevenue = byCrop.reduce((sum, c) => sum + c.revenue, 0);
  const totalCosts = byCrop.reduce((sum, c) => sum + c.costs, 0);
  const netProfit = totalRevenue - totalCosts;

  const costCategories = [
    { category: "seeds", categoryAr: "بذور", percentage: 15 },
    { category: "fertilizer", categoryAr: "أسمدة", percentage: 25 },
    { category: "pesticides", categoryAr: "مبيدات", percentage: 18 },
    { category: "labor", categoryAr: "عمالة", percentage: 30 },
    { category: "equipment", categoryAr: "معدات", percentage: 12 },
  ];

  const costBreakdown = costCategories.map((cat) => ({
    ...cat,
    amount: (totalCosts * cat.percentage) / 100,
  }));

  const seasons = [
    { season: "spring", seasonAr: "ربيع", crops: 8 },
    { season: "summer", seasonAr: "صيف", crops: 12 },
    { season: "fall", seasonAr: "خريف", crops: 10 },
    { season: "winter", seasonAr: "شتاء", crops: 6 },
  ].map((season) => {
    const revenue = 150000 + Math.random() * 100000;
    const costs = revenue * (0.6 + Math.random() * 0.1);
    return {
      ...season,
      revenue,
      costs,
      profit: revenue - costs,
    };
  });

  return {
    summary: {
      totalRevenue,
      totalCosts,
      netProfit,
      profitMargin: (netProfit / totalRevenue) * 100,
      roi: (netProfit / totalCosts) * 100,
    },
    byCrop,
    byMonth,
    costBreakdown,
    seasons,
  };
}

function generateMockSatelliteData(): SatelliteData {
  const fields = Array.from({ length: 15 }, (_, i) => {
    const ndviCurrent = 0.3 + Math.random() * 0.5;
    const ndviAverage = 0.4 + Math.random() * 0.3;
    const change = (ndviCurrent - ndviAverage) / ndviAverage;

    // Generate NDVI trends for the last 30 days
    const trends = Array.from({ length: 30 }, (_, j) => ({
      date: new Date(Date.now() - (29 - j) * 24 * 60 * 60 * 1000).toISOString(),
      ndvi: Math.max(
        0.2,
        Math.min(0.9, ndviCurrent + (Math.random() - 0.5) * 0.2),
      ),
      fieldId: `field-${i + 1}`,
      fieldName: `حقل ${String.fromCharCode(65 + i)}`,
    }));

    const hasAlerts = Math.random() > 0.6;
    const alerts = hasAlerts
      ? [
          {
            type: ["anomaly", "stress", "disease", "pest"][
              Math.floor(Math.random() * 4)
            ] as "anomaly" | "stress" | "disease" | "pest",
            severity: ["low", "medium", "high", "critical"][
              Math.floor(Math.random() * 4)
            ] as "low" | "medium" | "high" | "critical",
            message: "Anomaly detected in vegetation index",
            messageAr: "تم اكتشاف شذوذ في مؤشر النباتات",
            detectedAt: new Date(
              Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000,
            ).toISOString(),
          },
        ]
      : [];

    return {
      id: `field-${i + 1}`,
      farmId: `farm-${Math.floor(Math.random() * 10) + 1}`,
      farmName: `مزرعة ${Math.floor(Math.random() * 10) + 1}`,
      fieldName: `حقل ${String.fromCharCode(65 + i)}`,
      area: 10 + Math.random() * 40,
      location: {
        lat: 15.5 + Math.random() * 2,
        lng: 44.0 + Math.random() * 4,
      },
      ndvi: {
        current: ndviCurrent,
        average: ndviAverage,
        trend:
          change > 0.05
            ? ("up" as const)
            : change < -0.05
              ? ("down" as const)
              : ("stable" as const),
        change,
      },
      lastImageDate: new Date(
        Date.now() - Math.random() * 5 * 24 * 60 * 60 * 1000,
      ).toISOString(),
      alerts,
      trends,
    };
  });

  // Flatten all trends
  const ndviTrends = fields.flatMap((f) => f.trends || []);

  return {
    summary: {
      totalFields: fields.length,
      lastUpdate: new Date().toISOString(),
      coverage: 85 + Math.random() * 15,
      dataUsage: 45 + Math.random() * 30,
    },
    fields: fields.map(({ trends, ...field }) => field), // Remove trends from fields
    ndviTrends,
  };
}
