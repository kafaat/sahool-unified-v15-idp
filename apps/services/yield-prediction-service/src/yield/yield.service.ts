// ═══════════════════════════════════════════════════════════════════════════════
// Yield Service - خدمة الإنتاجية
// Field-First Architecture - Pre-Harvest Alerts
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from "@nestjs/common";
import { v4 as uuidv4 } from "uuid";

// ═══════════════════════════════════════════════════════════════════════════════
// Field-First Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface Badge {
  type: string;
  label_ar: string;
  label_en: string;
  color: string;
}

export interface ActionTemplate {
  action_id: string;
  action_type: string;
  what: string;
  what_ar: string;
  why: string;
  why_ar: string;
  when: {
    deadline: string;
    optimal_window: string;
    optimal_window_ar: string;
  };
  how: string[];
  how_ar: string[];
  fallback: string;
  fallback_ar: string;
  badge: Badge;
  confidence: number;
  source_service: string;
  field_id: string;
  farmer_id?: string;
  tenant_id?: string;
  data: Record<string, unknown>;
  created_at: string;
}

export interface PreHarvestAlertResponse {
  prediction: {
    yieldPerHectareKg: number;
    totalYieldKg: number;
    totalYieldTons: number;
    confidencePercent: number;
    harvestDate: string;
    daysUntilHarvest: number;
  };
  action_template: ActionTemplate;
  task_card: {
    id: string;
    type: string;
    title_ar: string;
    title_en: string;
    urgency: {
      level: string;
      label_ar: string;
      color: string;
    };
    field_id: string;
    confidence_percent: number;
    offline_ready: boolean;
    badge: Badge;
  };
  nats_topic: string;
}

// Crop data constants
const CROP_DATA: Record<
  string,
  {
    nameAr: string;
    avgYieldKgPerHectare: number;
    growthDays: number;
    stages: { name: string; nameAr: string; days: number }[];
  }
> = {
  wheat: {
    nameAr: "قمح",
    avgYieldKgPerHectare: 3500,
    growthDays: 120,
    stages: [
      { name: "germination", nameAr: "إنبات", days: 10 },
      { name: "tillering", nameAr: "تفرع", days: 25 },
      { name: "stem_extension", nameAr: "استطالة الساق", days: 30 },
      { name: "heading", nameAr: "طرد السنابل", days: 20 },
      { name: "flowering", nameAr: "إزهار", days: 10 },
      { name: "grain_filling", nameAr: "امتلاء الحبوب", days: 20 },
      { name: "maturity", nameAr: "نضج", days: 5 },
    ],
  },
  coffee: {
    nameAr: "بن",
    avgYieldKgPerHectare: 800,
    growthDays: 270,
    stages: [
      { name: "flowering", nameAr: "إزهار", days: 30 },
      { name: "fruit_set", nameAr: "عقد الثمار", days: 60 },
      { name: "green_fruit", nameAr: "ثمار خضراء", days: 90 },
      { name: "ripening", nameAr: "نضج", days: 60 },
      { name: "harvest_ready", nameAr: "جاهز للحصاد", days: 30 },
    ],
  },
  sorghum: {
    nameAr: "ذرة رفيعة",
    avgYieldKgPerHectare: 2500,
    growthDays: 100,
    stages: [
      { name: "emergence", nameAr: "بزوغ", days: 10 },
      { name: "vegetative", nameAr: "نمو خضري", days: 35 },
      { name: "boot", nameAr: "انتفاخ", days: 15 },
      { name: "heading", nameAr: "طرد السنابل", days: 10 },
      { name: "flowering", nameAr: "إزهار", days: 10 },
      { name: "grain_filling", nameAr: "امتلاء الحبوب", days: 15 },
      { name: "maturity", nameAr: "نضج", days: 5 },
    ],
  },
  tomato: {
    nameAr: "طماطم",
    avgYieldKgPerHectare: 45000,
    growthDays: 90,
    stages: [
      { name: "seedling", nameAr: "شتلة", days: 20 },
      { name: "vegetative", nameAr: "نمو خضري", days: 25 },
      { name: "flowering", nameAr: "إزهار", days: 15 },
      { name: "fruit_set", nameAr: "عقد الثمار", days: 15 },
      { name: "ripening", nameAr: "نضج", days: 15 },
    ],
  },
};

const GOVERNORATE_AR: Record<string, string> = {
  sanaa: "صنعاء",
  aden: "عدن",
  taiz: "تعز",
  hodeidah: "الحديدة",
  ibb: "إب",
  dhamar: "ذمار",
  hadramaut: "حضرموت",
  marib: "مأرب",
};

@Injectable()
export class YieldService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Predict Field Yield
  // ─────────────────────────────────────────────────────────────────────────────

  async predictFieldYield(fieldId: string) {
    // Mock field data
    const cropType = "wheat";
    const areaHectares = 15.5;
    const plantingDate = new Date("2024-10-15");
    const currentNDVI = 0.72;

    const cropData = CROP_DATA[cropType];
    const baseYield = cropData.avgYieldKgPerHectare;

    // Calculate yield factors
    const ndviFactor = this.calculateNDVIFactor(currentNDVI);
    const weatherFactor = 0.95; // Based on weather conditions
    const soilFactor = 0.92; // Based on soil health

    const predictedYieldPerHectare = Math.round(
      baseYield * ndviFactor * weatherFactor * soilFactor,
    );
    const totalPredictedYield = Math.round(
      predictedYieldPerHectare * areaHectares,
    );

    // Compare with regional average
    const regionalAvg = baseYield;
    const comparisonPercent = Math.round(
      ((predictedYieldPerHectare - regionalAvg) / regionalAvg) * 100,
    );

    return {
      fieldId,
      cropType,
      cropTypeAr: cropData.nameAr,
      areaHectares,
      plantingDate: plantingDate.toISOString().split("T")[0],
      prediction: {
        yieldPerHectareKg: predictedYieldPerHectare,
        totalYieldKg: totalPredictedYield,
        totalYieldTons: Math.round(totalPredictedYield / 100) / 10,
        confidencePercent: 85,
      },
      factors: {
        ndvi: {
          value: currentNDVI,
          factor: ndviFactor,
          status: ndviFactor >= 1 ? "good" : "below_average",
        },
        weather: {
          factor: weatherFactor,
          status: weatherFactor >= 0.9 ? "favorable" : "challenging",
        },
        soil: {
          factor: soilFactor,
          status: soilFactor >= 0.9 ? "healthy" : "needs_attention",
        },
      },
      comparison: {
        regionalAverageKg: regionalAvg,
        differencePercent: comparisonPercent,
        status: comparisonPercent >= 0 ? "above_average" : "below_average",
        statusAr: comparisonPercent >= 0 ? "فوق المتوسط" : "تحت المتوسط",
      },
      recommendations: this.generateYieldRecommendations(
        ndviFactor,
        weatherFactor,
        soilFactor,
      ),
      predictedAt: new Date().toISOString(),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Growth Stage
  // ─────────────────────────────────────────────────────────────────────────────

  async getGrowthStage(fieldId: string) {
    const cropType = "wheat";
    const plantingDate = new Date("2024-10-15");
    const daysSincePlanting = Math.floor(
      (Date.now() - plantingDate.getTime()) / (1000 * 60 * 60 * 24),
    );

    const cropData = CROP_DATA[cropType];
    let cumulativeDays = 0;
    let currentStage = cropData.stages[0];
    let stageProgress = 0;

    for (const stage of cropData.stages) {
      if (daysSincePlanting <= cumulativeDays + stage.days) {
        currentStage = stage;
        stageProgress = Math.round(
          ((daysSincePlanting - cumulativeDays) / stage.days) * 100,
        );
        break;
      }
      cumulativeDays += stage.days;
    }

    const overallProgress = Math.min(
      100,
      Math.round((daysSincePlanting / cropData.growthDays) * 100),
    );

    return {
      fieldId,
      cropType,
      cropTypeAr: cropData.nameAr,
      plantingDate: plantingDate.toISOString().split("T")[0],
      daysSincePlanting,
      totalGrowthDays: cropData.growthDays,
      currentStage: {
        name: currentStage.name,
        nameAr: currentStage.nameAr,
        progress: stageProgress,
        daysInStage: daysSincePlanting - cumulativeDays,
        totalDaysInStage: currentStage.days,
      },
      overallProgress,
      allStages: cropData.stages.map((s, i) => {
        const stageStart = cropData.stages
          .slice(0, i)
          .reduce((sum, st) => sum + st.days, 0);
        const stageEnd = stageStart + s.days;
        let status: string;

        if (daysSincePlanting >= stageEnd) {
          status = "completed";
        } else if (daysSincePlanting >= stageStart) {
          status = "current";
        } else {
          status = "upcoming";
        }

        return {
          ...s,
          status,
          statusAr:
            status === "completed"
              ? "مكتمل"
              : status === "current"
                ? "حالي"
                : "قادم",
        };
      }),
      nextMilestone: {
        name: currentStage.name,
        nameAr: currentStage.nameAr,
        daysRemaining: currentStage.days - (daysSincePlanting - cumulativeDays),
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Predict Harvest Date
  // ─────────────────────────────────────────────────────────────────────────────

  async predictHarvestDate(fieldId: string) {
    const cropType = "wheat";
    const plantingDate = new Date("2024-10-15");
    const cropData = CROP_DATA[cropType];

    const baseHarvestDate = new Date(plantingDate);
    baseHarvestDate.setDate(baseHarvestDate.getDate() + cropData.growthDays);

    // Adjust based on conditions
    const weatherAdjustment = -3; // Days earlier due to warm weather
    const ndviAdjustment = 2; // Days later due to slower growth

    const predictedHarvestDate = new Date(baseHarvestDate);
    predictedHarvestDate.setDate(
      predictedHarvestDate.getDate() + weatherAdjustment + ndviAdjustment,
    );

    const daysUntilHarvest = Math.floor(
      (predictedHarvestDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24),
    );

    // Optimal harvest window (typically 5-7 days)
    const windowStart = new Date(predictedHarvestDate);
    windowStart.setDate(windowStart.getDate() - 2);
    const windowEnd = new Date(predictedHarvestDate);
    windowEnd.setDate(windowEnd.getDate() + 5);

    return {
      fieldId,
      cropType,
      cropTypeAr: cropData.nameAr,
      plantingDate: plantingDate.toISOString().split("T")[0],
      prediction: {
        predictedDate: predictedHarvestDate.toISOString().split("T")[0],
        daysUntilHarvest,
        confidencePercent: 82,
      },
      harvestWindow: {
        start: windowStart.toISOString().split("T")[0],
        end: windowEnd.toISOString().split("T")[0],
        optimalDay: predictedHarvestDate.toISOString().split("T")[0],
      },
      adjustments: {
        weather: {
          days: weatherAdjustment,
          reason: "Warm conditions accelerating maturity",
          reasonAr: "ظروف دافئة تسرع النضج",
        },
        ndvi: {
          days: ndviAdjustment,
          reason: "Slightly below average growth rate",
          reasonAr: "معدل نمو أقل قليلاً من المتوسط",
        },
      },
      recommendations: [
        "Monitor grain moisture content starting 7 days before harvest",
        "Prepare harvesting equipment",
        "Check weather forecast for harvest window",
      ],
      recommendationsAr: [
        "مراقبة محتوى رطوبة الحبوب قبل 7 أيام من الحصاد",
        "تجهيز معدات الحصاد",
        "مراجعة توقعات الطقس لفترة الحصاد",
      ],
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Regional Statistics
  // ─────────────────────────────────────────────────────────────────────────────

  async getRegionalStats(params: {
    governorate: string;
    cropType?: string;
    year?: number;
  }) {
    const year = params.year || new Date().getFullYear();
    const cropType = params.cropType || "wheat";
    const cropData = CROP_DATA[cropType];

    // Mock regional statistics
    const totalFields = Math.floor(Math.random() * 500) + 200;
    const totalAreaHectares = Math.floor(Math.random() * 10000) + 5000;
    const avgYield =
      cropData.avgYieldKgPerHectare * (0.85 + Math.random() * 0.3);

    return {
      governorate: params.governorate,
      governorateAr: GOVERNORATE_AR[params.governorate] || params.governorate,
      year,
      cropType,
      cropTypeAr: cropData.nameAr,
      statistics: {
        totalFields,
        totalAreaHectares,
        averageYieldKgPerHectare: Math.round(avgYield),
        totalProductionTons: Math.round((avgYield * totalAreaHectares) / 1000),
        topPerformingFields: 15,
        belowAverageFields: Math.floor(totalFields * 0.2),
      },
      comparison: {
        nationalAverage: cropData.avgYieldKgPerHectare,
        percentOfNational: Math.round(
          (avgYield / cropData.avgYieldKgPerHectare) * 100,
        ),
        rankAmongGovernorates: Math.floor(Math.random() * 10) + 1,
      },
      trends: {
        vsLastYear: Math.round((Math.random() - 0.3) * 20),
        vsFiveYearAvg: Math.round((Math.random() - 0.2) * 15),
      },
      forecast: {
        expectedChangeNextYear: Math.round((Math.random() - 0.5) * 10),
        confidence: 75,
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Historical Yields
  // ─────────────────────────────────────────────────────────────────────────────

  async getHistoricalYields(fieldId: string, years: number) {
    const cropType = "wheat";
    const cropData = CROP_DATA[cropType];
    const currentYear = new Date().getFullYear();

    const history = Array.from({ length: years }, (_, i) => {
      const year = currentYear - years + i + 1;
      const yieldVariation = 0.7 + Math.random() * 0.5; // 70-120% of average
      const yieldKg = Math.round(
        cropData.avgYieldKgPerHectare * yieldVariation,
      );

      return {
        year,
        season: year < currentYear ? "completed" : "in_progress",
        seasonAr: year < currentYear ? "مكتمل" : "جاري",
        yieldKgPerHectare: yieldKg,
        areaHectares: 15 + Math.random() * 5,
        totalYieldTons:
          Math.round((yieldKg * (15 + Math.random() * 5)) / 100) / 10,
        weatherConditions: ["excellent", "good", "moderate", "challenging"][
          Math.floor(Math.random() * 4)
        ],
        notes:
          year === currentYear - 1 && yieldVariation < 0.85
            ? "Drought affected yield"
            : null,
        notesAr:
          year === currentYear - 1 && yieldVariation < 0.85
            ? "الجفاف أثر على الإنتاجية"
            : null,
      };
    });

    const avgYield = Math.round(
      history.reduce((sum, h) => sum + h.yieldKgPerHectare, 0) / history.length,
    );
    const maxYield = Math.max(...history.map((h) => h.yieldKgPerHectare));
    const minYield = Math.min(...history.map((h) => h.yieldKgPerHectare));

    return {
      fieldId,
      cropType,
      cropTypeAr: cropData.nameAr,
      periodYears: years,
      history,
      summary: {
        averageYieldKgPerHectare: avgYield,
        maxYieldKgPerHectare: maxYield,
        minYieldKgPerHectare: minYield,
        variabilityPercent: Math.round(
          ((maxYield - minYield) / avgYield) * 100,
        ),
        trend:
          history[history.length - 1].yieldKgPerHectare >
          history[0].yieldKgPerHectare
            ? "improving"
            : "declining",
        trendAr:
          history[history.length - 1].yieldKgPerHectare >
          history[0].yieldKgPerHectare
            ? "تحسن"
            : "انخفاض",
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Maturity Monitoring
  // ─────────────────────────────────────────────────────────────────────────────

  async getMaturityMonitoring(fieldId: string) {
    const cropType = "wheat";
    const cropData = CROP_DATA[cropType];

    // Mock maturity indicators
    const grainMoisture = 18 + Math.random() * 10; // Target: 13-14% for harvest
    const ndvi = 0.35 + Math.random() * 0.3; // Declining as crop matures
    const canopyTemperature = 28 + Math.random() * 8;

    let maturityStatus: string, maturityStatusAr: string;
    if (grainMoisture > 25) {
      maturityStatus = "green";
      maturityStatusAr = "أخضر";
    } else if (grainMoisture > 18) {
      maturityStatus = "yellowing";
      maturityStatusAr = "اصفرار";
    } else if (grainMoisture > 14) {
      maturityStatus = "mature";
      maturityStatusAr = "ناضج";
    } else {
      maturityStatus = "ready_for_harvest";
      maturityStatusAr = "جاهز للحصاد";
    }

    return {
      fieldId,
      cropType,
      cropTypeAr: cropData.nameAr,
      maturity: {
        status: maturityStatus,
        statusAr: maturityStatusAr,
        progress: Math.round((1 - (grainMoisture - 13) / 20) * 100),
      },
      indicators: {
        grainMoisture: {
          current: Math.round(grainMoisture * 10) / 10,
          target: 13,
          unit: "%",
          status: grainMoisture <= 14 ? "optimal" : "drying",
        },
        ndvi: {
          current: Math.round(ndvi * 100) / 100,
          trend: "declining",
          status: ndvi < 0.4 ? "senescence" : "active",
        },
        canopyTemperature: {
          current: Math.round(canopyTemperature * 10) / 10,
          unit: "°C",
          status: canopyTemperature > 32 ? "stress" : "normal",
        },
      },
      timeline: [
        {
          date: this.addDays(new Date(), -14).toISOString().split("T")[0],
          moisture: 28,
          status: "green",
        },
        {
          date: this.addDays(new Date(), -7).toISOString().split("T")[0],
          moisture: 22,
          status: "yellowing",
        },
        {
          date: new Date().toISOString().split("T")[0],
          moisture: Math.round(grainMoisture),
          status: maturityStatus,
        },
        {
          date: this.addDays(new Date(), 7).toISOString().split("T")[0],
          moisture: 15,
          status: "mature",
          predicted: true,
        },
        {
          date: this.addDays(new Date(), 12).toISOString().split("T")[0],
          moisture: 13,
          status: "ready_for_harvest",
          predicted: true,
        },
      ],
      recommendations:
        grainMoisture > 18
          ? ["Continue monitoring daily", "Prepare harvesting equipment"]
          : ["Begin harvest within 3-5 days", "Check weather forecast"],
      recommendationsAr:
        grainMoisture > 18
          ? ["استمر في المراقبة اليومية", "جهز معدات الحصاد"]
          : ["ابدأ الحصاد خلال 3-5 أيام", "راجع توقعات الطقس"],
      lastUpdated: new Date().toISOString(),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Helper Methods
  // ─────────────────────────────────────────────────────────────────────────────

  private calculateNDVIFactor(ndvi: number): number {
    // NDVI to yield factor mapping
    if (ndvi >= 0.8) return 1.15;
    if (ndvi >= 0.7) return 1.05;
    if (ndvi >= 0.6) return 1.0;
    if (ndvi >= 0.5) return 0.9;
    if (ndvi >= 0.4) return 0.8;
    return 0.7;
  }

  private generateYieldRecommendations(
    ndviFactor: number,
    weatherFactor: number,
    soilFactor: number,
  ) {
    const recommendations: { en: string[]; ar: string[] } = { en: [], ar: [] };

    if (ndviFactor < 1) {
      recommendations.en.push(
        "Consider foliar fertilization to boost plant health",
      );
      recommendations.ar.push("النظر في التسميد الورقي لتعزيز صحة النبات");
    }
    if (weatherFactor < 0.9) {
      recommendations.en.push(
        "Implement protective measures for weather stress",
      );
      recommendations.ar.push("تطبيق إجراءات وقائية للإجهاد الجوي");
    }
    if (soilFactor < 0.9) {
      recommendations.en.push("Conduct soil testing and amend as needed");
      recommendations.ar.push("إجراء اختبار التربة وتعديلها حسب الحاجة");
    }
    if (ndviFactor >= 1 && weatherFactor >= 0.9 && soilFactor >= 0.9) {
      recommendations.en.push(
        "Maintain current practices - conditions are optimal",
      );
      recommendations.ar.push("الحفاظ على الممارسات الحالية - الظروف مثالية");
    }

    return recommendations;
  }

  private addDays(date: Date, days: number): Date {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Field-First: ActionTemplate Methods
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * Predict yield with ActionTemplate for pre-harvest alerts
   * التنبؤ بالإنتاجية مع قالب إجراء ما قبل الحصاد
   */
  async predictWithAction(
    fieldId: string,
    farmerId?: string,
    tenantId?: string,
  ): Promise<PreHarvestAlertResponse> {
    // Get prediction and harvest data
    const prediction = await this.predictFieldYield(fieldId);
    const harvestData = await this.predictHarvestDate(fieldId);
    const maturity = await this.getMaturityMonitoring(fieldId);

    const daysUntilHarvest = harvestData.prediction.daysUntilHarvest;
    const actionId = uuidv4();

    // Determine urgency based on days until harvest
    let urgencyLevel: string;
    let urgencyLabelAr: string;
    let urgencyColor: string;

    if (daysUntilHarvest <= 3) {
      urgencyLevel = "critical";
      urgencyLabelAr = "حرج";
      urgencyColor = "#EF4444";
    } else if (daysUntilHarvest <= 7) {
      urgencyLevel = "high";
      urgencyLabelAr = "عالي";
      urgencyColor = "#F97316";
    } else if (daysUntilHarvest <= 14) {
      urgencyLevel = "medium";
      urgencyLabelAr = "متوسط";
      urgencyColor = "#EAB308";
    } else {
      urgencyLevel = "low";
      urgencyLabelAr = "منخفض";
      urgencyColor = "#22C55E";
    }

    // Create ActionTemplate
    const actionTemplate: ActionTemplate = {
      action_id: actionId,
      action_type: "pre_harvest_alert",
      what: "Prepare for harvest",
      what_ar: "استعداد للحصاد",
      why: `Crop will be ready in ${daysUntilHarvest} days - Expected yield: ${prediction.prediction.totalYieldTons} tons/hectare`,
      why_ar: `المحصول سيكون جاهزاً خلال ${daysUntilHarvest} يوم - الإنتاج المتوقع: ${prediction.prediction.totalYieldTons} طن/هكتار`,
      when: {
        deadline: harvestData.prediction.predictedDate,
        optimal_window:
          harvestData.harvestWindow.start +
          " to " +
          harvestData.harvestWindow.end,
        optimal_window_ar: `من ${harvestData.harvestWindow.start} إلى ${harvestData.harvestWindow.end}`,
      },
      how: [
        "Prepare harvesting equipment",
        "Ensure labor availability",
        "Arrange storage space",
        "Contact potential buyers",
        "Check weather forecast for harvest window",
      ],
      how_ar: [
        "جهّز معدات الحصاد",
        "تأكد من توفر العمالة",
        "رتّب مكان التخزين",
        "تواصل مع المشترين المحتملين",
        "راجع توقعات الطقس لفترة الحصاد",
      ],
      fallback:
        "If harvest is delayed: Monitor for signs of over-drying or grain shatter",
      fallback_ar: "إذا تأخر الحصاد: راقب علامات الجفاف الزائد أو تساقط الحبوب",
      badge: {
        type: "yield_model",
        label_ar: "نموذج إنتاجية",
        label_en: "Yield Model",
        color: "#10B981",
      },
      confidence: prediction.prediction.confidencePercent / 100,
      source_service: "yield-prediction",
      field_id: fieldId,
      farmer_id: farmerId,
      tenant_id: tenantId,
      data: {
        predicted_yield_kg_ha: prediction.prediction.yieldPerHectareKg,
        total_yield_tons: prediction.prediction.totalYieldTons,
        harvest_date: harvestData.prediction.predictedDate,
        days_until_harvest: daysUntilHarvest,
        maturity_status: maturity.maturity.status,
        grain_moisture: maturity.indicators.grainMoisture.current,
        ndvi_factor: prediction.factors.ndvi.factor,
        weather_factor: prediction.factors.weather.factor,
      },
      created_at: new Date().toISOString(),
    };

    // Create task card for mobile app
    const taskCard = {
      id: actionId,
      type: "pre_harvest_alert",
      title_ar: `تنبيه حصاد - ${daysUntilHarvest} يوم`,
      title_en: `Harvest Alert - ${daysUntilHarvest} days`,
      urgency: {
        level: urgencyLevel,
        label_ar: urgencyLabelAr,
        color: urgencyColor,
      },
      field_id: fieldId,
      confidence_percent: prediction.prediction.confidencePercent,
      offline_ready: true,
      badge: actionTemplate.badge,
    };

    return {
      prediction: {
        yieldPerHectareKg: prediction.prediction.yieldPerHectareKg,
        totalYieldKg: prediction.prediction.totalYieldKg,
        totalYieldTons: prediction.prediction.totalYieldTons,
        confidencePercent: prediction.prediction.confidencePercent,
        harvestDate: harvestData.prediction.predictedDate,
        daysUntilHarvest,
      },
      action_template: actionTemplate,
      task_card: taskCard,
      nats_topic: "sahool.alerts.pre_harvest",
    };
  }

  /**
   * Get harvest readiness with ActionTemplate
   * فحص جاهزية الحصاد مع قالب إجراء
   */
  async getHarvestReadiness(fieldId: string, farmerId?: string) {
    const maturity = await this.getMaturityMonitoring(fieldId);
    const actionId = uuidv4();

    const isReady =
      maturity.maturity.status === "ready_for_harvest" ||
      maturity.maturity.status === "mature";
    const grainMoisture = maturity.indicators.grainMoisture.current;

    // Determine action type and urgency
    let actionType: string;
    let urgencyLevel: string;
    let whatAr: string;
    let whyAr: string;

    if (maturity.maturity.status === "ready_for_harvest") {
      actionType = "harvest_now";
      urgencyLevel = "critical";
      whatAr = "ابدأ الحصاد الآن";
      whyAr = `المحصول جاهز للحصاد - رطوبة الحبوب: ${grainMoisture}%`;
    } else if (maturity.maturity.status === "mature") {
      actionType = "harvest_soon";
      urgencyLevel = "high";
      whatAr = "الحصاد خلال 3-5 أيام";
      whyAr = `المحصول ناضج - رطوبة الحبوب: ${grainMoisture}%`;
    } else if (maturity.maturity.status === "yellowing") {
      actionType = "prepare_harvest";
      urgencyLevel = "medium";
      whatAr = "جهّز للحصاد";
      whyAr = `المحصول في مرحلة الاصفرار - رطوبة الحبوب: ${grainMoisture}%`;
    } else {
      actionType = "monitor";
      urgencyLevel = "low";
      whatAr = "استمر في المراقبة";
      whyAr = `المحصول لا يزال أخضر - رطوبة الحبوب: ${grainMoisture}%`;
    }

    const actionTemplate: ActionTemplate = {
      action_id: actionId,
      action_type: actionType,
      what: isReady ? "Begin harvest" : "Continue monitoring",
      what_ar: whatAr,
      why: `Grain moisture at ${grainMoisture}% - ${maturity.maturity.status}`,
      why_ar: whyAr,
      when: {
        deadline: isReady ? "Within 3-5 days" : "Monitor daily",
        optimal_window: isReady
          ? "Early morning when moisture is lower"
          : "Check daily at 8 AM",
        optimal_window_ar: isReady
          ? "الصباح الباكر عندما تكون الرطوبة أقل"
          : "فحص يومي الساعة 8 صباحاً",
      },
      how: isReady
        ? [
            "Check grain moisture with meter",
            "Start harvest in dry weather",
            "Monitor for grain shatter",
          ]
        : [
            "Monitor grain color change",
            "Check moisture content",
            "Prepare equipment",
          ],
      how_ar: isReady
        ? [
            "افحص رطوبة الحبوب بالمقياس",
            "ابدأ الحصاد في طقس جاف",
            "راقب تساقط الحبوب",
          ]
        : ["راقب تغير لون الحبوب", "افحص محتوى الرطوبة", "جهّز المعدات"],
      fallback: "If weather delays harvest: Consider early harvest with drying",
      fallback_ar: "إذا أخّر الطقس الحصاد: فكر في حصاد مبكر مع التجفيف",
      badge: {
        type: "maturity_model",
        label_ar: "نموذج النضج",
        label_en: "Maturity Model",
        color: "#8B5CF6",
      },
      confidence: 0.85,
      source_service: "yield-prediction",
      field_id: fieldId,
      farmer_id: farmerId,
      data: {
        maturity_status: maturity.maturity.status,
        maturity_progress: maturity.maturity.progress,
        grain_moisture: grainMoisture,
        target_moisture: maturity.indicators.grainMoisture.target,
        ndvi: maturity.indicators.ndvi.current,
        is_ready: isReady,
      },
      created_at: new Date().toISOString(),
    };

    return {
      maturity,
      action_template: actionTemplate,
      is_ready: isReady,
      nats_topic: "sahool.alerts.harvest_readiness",
    };
  }
}
