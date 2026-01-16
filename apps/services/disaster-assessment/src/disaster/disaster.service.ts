// ═══════════════════════════════════════════════════════════════════════════════
// Disaster Service - خدمة الكوارث
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from "@nestjs/common";
import {
  CreateDisasterReportDto,
  DisasterAssessmentDto,
  DisasterType,
  Severity,
  DisasterStatus,
} from "./disaster.dto";

// Governorate translations
const GOVERNORATE_AR: Record<string, string> = {
  sanaa: "صنعاء",
  aden: "عدن",
  taiz: "تعز",
  hodeidah: "الحديدة",
  ibb: "إب",
  dhamar: "ذمار",
  hadramaut: "حضرموت",
  hajjah: "حجة",
  saadah: "صعدة",
  amran: "عمران",
  albayda: "البيضاء",
  lahj: "لحج",
  marib: "مأرب",
  shabwah: "شبوة",
  abyan: "أبين",
  aldali: "الضالع",
  almahrah: "المهرة",
  almahwit: "المحويت",
  raymah: "ريمة",
  socotra: "سقطرى",
};

const DISASTER_TYPE_AR: Record<DisasterType, string> = {
  [DisasterType.FLOOD]: "فيضان",
  [DisasterType.DROUGHT]: "جفاف",
  [DisasterType.FROST]: "صقيع",
  [DisasterType.HAIL]: "بَرَد",
  [DisasterType.STORM]: "عاصفة",
  [DisasterType.PEST]: "آفات",
  [DisasterType.DISEASE]: "أمراض نباتية",
  [DisasterType.LOCUST]: "جراد",
  [DisasterType.WILDFIRE]: "حرائق",
};

const DAMAGE_LEVELS = [
  { max: 10, level: "minimal", levelAr: "طفيف", color: "green" },
  { max: 25, level: "light", levelAr: "خفيف", color: "yellow" },
  { max: 50, level: "moderate", levelAr: "متوسط", color: "orange" },
  { max: 75, level: "severe", levelAr: "شديد", color: "red" },
  { max: 100, level: "catastrophic", levelAr: "كارثي", color: "darkred" },
];

@Injectable()
export class DisasterService {
  // Mock active disasters for demo
  private disasters: any[] = [
    {
      id: "disaster-001",
      type: DisasterType.FLOOD,
      title: "Hadramaut Valley Flood",
      titleAr: "فيضان وادي حضرموت",
      description: "Heavy rainfall caused flooding in agricultural areas",
      governorate: "hadramaut",
      location: { lat: 15.9, lng: 48.8 },
      affectedRadiusKm: 15,
      severity: Severity.HIGH,
      status: DisasterStatus.ACTIVE,
      affectedFieldsCount: 45,
      totalAffectedAreaHectares: 320,
      totalEstimatedLossYER: 15000000,
      startDate: "2024-12-15T00:00:00Z",
      createdAt: "2024-12-15T08:30:00Z",
      updatedAt: "2024-12-18T10:00:00Z",
    },
    {
      id: "disaster-002",
      type: DisasterType.DROUGHT,
      title: "Marib Drought",
      titleAr: "جفاف مأرب",
      description: "Extended dry period affecting crop growth",
      governorate: "marib",
      location: { lat: 15.4, lng: 45.3 },
      affectedRadiusKm: 30,
      severity: Severity.MEDIUM,
      status: DisasterStatus.MONITORING,
      affectedFieldsCount: 120,
      totalAffectedAreaHectares: 850,
      totalEstimatedLossYER: 8500000,
      startDate: "2024-11-01T00:00:00Z",
      createdAt: "2024-11-05T00:00:00Z",
      updatedAt: "2024-12-18T00:00:00Z",
    },
    {
      id: "disaster-003",
      type: DisasterType.LOCUST,
      title: "Desert Locust Swarm - Hodeidah",
      titleAr: "سرب جراد صحراوي - الحديدة",
      description:
        "Desert locust swarm detected moving towards agricultural areas",
      governorate: "hodeidah",
      location: { lat: 14.8, lng: 42.9 },
      affectedRadiusKm: 25,
      severity: Severity.CRITICAL,
      status: DisasterStatus.ACTIVE,
      affectedFieldsCount: 200,
      totalAffectedAreaHectares: 1500,
      totalEstimatedLossYER: 45000000,
      startDate: "2024-12-17T00:00:00Z",
      createdAt: "2024-12-17T06:00:00Z",
      updatedAt: "2024-12-18T12:00:00Z",
    },
  ];

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Active Disasters
  // ─────────────────────────────────────────────────────────────────────────────

  async getActiveDisasters(params: {
    type?: DisasterType;
    governorate?: string;
    severity?: string;
  }) {
    let filtered = [...this.disasters];

    if (params.type) {
      filtered = filtered.filter((d) => d.type === params.type);
    }
    if (params.governorate) {
      filtered = filtered.filter((d) => d.governorate === params.governorate);
    }
    if (params.severity) {
      filtered = filtered.filter((d) => d.severity === params.severity);
    }

    return {
      total: filtered.length,
      disasters: filtered.map((d) => ({
        ...d,
        governorateAr: GOVERNORATE_AR[d.governorate] || d.governorate,
        typeAr: DISASTER_TYPE_AR[d.type as DisasterType],
      })),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Disaster by ID
  // ─────────────────────────────────────────────────────────────────────────────

  async getDisasterById(id: string) {
    const disaster = this.disasters.find((d) => d.id === id);
    if (!disaster) {
      return { error: "Disaster not found", errorAr: "الكارثة غير موجودة" };
    }

    return {
      ...disaster,
      governorateAr:
        GOVERNORATE_AR[disaster.governorate] || disaster.governorate,
      typeAr: DISASTER_TYPE_AR[disaster.type as DisasterType],
      // Add affected fields list (mock)
      affectedFields: this.generateAffectedFields(disaster.affectedFieldsCount),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Report New Disaster
  // ─────────────────────────────────────────────────────────────────────────────

  async reportDisaster(dto: CreateDisasterReportDto) {
    const id = `disaster-${Date.now()}`;
    const now = new Date().toISOString();

    const newDisaster = {
      id,
      ...dto,
      titleAr: dto.title, // In real implementation, translate or require Arabic title
      status: DisasterStatus.ACTIVE,
      affectedFieldsCount: 0,
      totalAffectedAreaHectares: 0,
      totalEstimatedLossYER: 0,
      createdAt: now,
      updatedAt: now,
    };

    this.disasters.push(newDisaster);

    return {
      success: true,
      message: "Disaster reported successfully",
      messageAr: "تم الإبلاغ عن الكارثة بنجاح",
      disaster: {
        ...newDisaster,
        governorateAr: GOVERNORATE_AR[dto.governorate] || dto.governorate,
        typeAr: DISASTER_TYPE_AR[dto.type],
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Assess Field Damage
  // ─────────────────────────────────────────────────────────────────────────────

  async assessFieldDamage(fieldId: string, dto: DisasterAssessmentDto) {
    const damagePercentage = dto.damagePercentage ?? Math.random() * 80 + 10;
    const affectedArea = dto.affectedAreaHectares ?? Math.random() * 20 + 5;

    // Determine damage level
    const damageLevel = DAMAGE_LEVELS.find((l) => damagePercentage <= l.max)!;

    // Calculate estimated loss (based on average crop value per hectare)
    const avgValuePerHectare = 200000; // YER
    const estimatedLoss =
      dto.estimatedLossYER ??
      Math.round(affectedArea * avgValuePerHectare * (damagePercentage / 100));

    // Generate recommendations based on disaster type and damage level
    const recommendations = this.generateRecommendations(
      dto.disasterId,
      damageLevel.level,
    );

    return {
      fieldId,
      disasterId: dto.disasterId,
      damagePercentage: Math.round(damagePercentage * 10) / 10,
      damageLevel: damageLevel.level,
      damageLevelAr: damageLevel.levelAr,
      damageColor: damageLevel.color,
      affectedAreaHectares: Math.round(affectedArea * 100) / 100,
      estimatedLossYER: estimatedLoss,
      affectedCropType: dto.affectedCropType || "wheat",
      recommendations: recommendations.en,
      recommendationsAr: recommendations.ar,
      insuranceEligible: damagePercentage >= 30,
      insuranceClaimAmount:
        damagePercentage >= 30 ? Math.round(estimatedLoss * 0.7) : 0,
      assessedAt: new Date().toISOString(),
      assessmentNotes: dto.assessmentNotes,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Flood Risk Map
  // ─────────────────────────────────────────────────────────────────────────────

  async getFloodRiskMap(governorate: string) {
    // Mock flood risk zones
    const riskZones = [
      { zone: "high", zoneAr: "عالي", percentage: 15, color: "#dc2626" },
      { zone: "medium", zoneAr: "متوسط", percentage: 25, color: "#f59e0b" },
      { zone: "low", zoneAr: "منخفض", percentage: 60, color: "#22c55e" },
    ];

    return {
      governorate,
      governorateAr: GOVERNORATE_AR[governorate] || governorate,
      lastUpdated: new Date().toISOString(),
      dataSource: "Satellite Remote Sensing + Historical Data",
      dataSourceAr: "الاستشعار عن بُعد + البيانات التاريخية",
      riskZones,
      totalAreaHectares: 50000,
      highRiskAreaHectares: 7500,
      recommendations: [
        "Install early warning systems in high-risk areas",
        "Improve drainage infrastructure",
        "Consider flood-resistant crop varieties",
      ],
      recommendationsAr: [
        "تركيب أنظمة إنذار مبكر في المناطق عالية الخطورة",
        "تحسين البنية التحتية للصرف",
        "النظر في أصناف المحاصيل المقاومة للفيضانات",
      ],
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Drought Index
  // ─────────────────────────────────────────────────────────────────────────────

  async getDroughtIndex(governorate: string) {
    // Mock drought indices
    const currentIndex = Math.random() * 3 - 1.5; // SPI typically ranges -3 to +3

    let status: string, statusAr: string, color: string;
    if (currentIndex <= -2) {
      status = "extreme_drought";
      statusAr = "جفاف شديد";
      color = "#7f1d1d";
    } else if (currentIndex <= -1.5) {
      status = "severe_drought";
      statusAr = "جفاف حاد";
      color = "#dc2626";
    } else if (currentIndex <= -1) {
      status = "moderate_drought";
      statusAr = "جفاف معتدل";
      color = "#f59e0b";
    } else if (currentIndex <= 1) {
      status = "normal";
      statusAr = "طبيعي";
      color = "#22c55e";
    } else {
      status = "wet";
      statusAr = "رطب";
      color = "#3b82f6";
    }

    return {
      governorate,
      governorateAr: GOVERNORATE_AR[governorate] || governorate,
      indexType: "SPI", // Standardized Precipitation Index
      indexValue: Math.round(currentIndex * 100) / 100,
      status,
      statusAr,
      color,
      lastUpdated: new Date().toISOString(),
      dataSource: "Satellite Precipitation Data",
      dataSourceAr: "بيانات الأقمار الصناعية للأمطار",
      historicalComparison: {
        lastMonth: Math.round((currentIndex - 0.3) * 100) / 100,
        lastYear: Math.round((currentIndex + 0.5) * 100) / 100,
        fiveYearAvg: Math.round((currentIndex + 0.2) * 100) / 100,
      },
      forecast: {
        nextMonth: status === "normal" ? "stable" : "improving",
        nextMonthAr: status === "normal" ? "مستقر" : "تحسن متوقع",
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Statistics
  // ─────────────────────────────────────────────────────────────────────────────

  async getStatistics(params: { year?: number; governorate?: string }) {
    const year = params.year || new Date().getFullYear();

    return {
      year,
      governorate: params.governorate || "all",
      governorateAr: params.governorate
        ? GOVERNORATE_AR[params.governorate]
        : "جميع المحافظات",
      summary: {
        totalDisasters: 45,
        activeDisasters: 3,
        resolvedDisasters: 42,
        totalAffectedAreaHectares: 12500,
        totalEstimatedLossYER: 850000000,
        totalFieldsAffected: 1250,
        farmersAffected: 890,
      },
      byType: [
        {
          type: DisasterType.FLOOD,
          typeAr: "فيضان",
          count: 12,
          lossYER: 250000000,
        },
        {
          type: DisasterType.DROUGHT,
          typeAr: "جفاف",
          count: 8,
          lossYER: 180000000,
        },
        {
          type: DisasterType.LOCUST,
          typeAr: "جراد",
          count: 5,
          lossYER: 320000000,
        },
        {
          type: DisasterType.PEST,
          typeAr: "آفات",
          count: 15,
          lossYER: 60000000,
        },
        {
          type: DisasterType.DISEASE,
          typeAr: "أمراض",
          count: 5,
          lossYER: 40000000,
        },
      ],
      byMonth: Array.from({ length: 12 }, (_, i) => ({
        month: i + 1,
        count: Math.floor(Math.random() * 8) + 1,
        lossYER: Math.floor(Math.random() * 100000000),
      })),
      trend: "decreasing",
      trendAr: "متناقص",
      comparedToLastYear: -15, // 15% decrease
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Helper Methods
  // ─────────────────────────────────────────────────────────────────────────────

  private generateAffectedFields(count: number) {
    return Array.from({ length: Math.min(count, 10) }, (_, i) => ({
      fieldId: `field-${i + 1}`,
      fieldName: `حقل ${i + 1}`,
      areaHectares: Math.round(Math.random() * 20 * 10) / 10,
      damagePercentage: Math.round(Math.random() * 80 + 10),
      cropType: ["wheat", "coffee", "qat", "sorghum"][
        Math.floor(Math.random() * 4)
      ],
    }));
  }

  private generateRecommendations(disasterId: string, damageLevel: string) {
    const disaster = this.disasters.find((d) => d.id === disasterId);
    const type = disaster?.type || DisasterType.FLOOD;

    const recommendationsByType: Record<
      string,
      { en: string[]; ar: string[] }
    > = {
      [DisasterType.FLOOD]: {
        en: [
          "Drain excess water from fields immediately",
          "Apply fungicides to prevent root rot",
          "Document damage for insurance claims",
          "Consider replanting if damage exceeds 50%",
        ],
        ar: [
          "تصريف المياه الزائدة من الحقول فوراً",
          "رش مبيدات الفطريات لمنع تعفن الجذور",
          "توثيق الأضرار لمطالبات التأمين",
          "النظر في إعادة الزراعة إذا تجاوز الضرر 50%",
        ],
      },
      [DisasterType.DROUGHT]: {
        en: [
          "Implement emergency irrigation if available",
          "Apply mulch to retain soil moisture",
          "Consider drought-resistant varieties for next season",
          "Reduce plant density to conserve water",
        ],
        ar: [
          "تطبيق الري الطارئ إن أمكن",
          "استخدام المهاد للحفاظ على رطوبة التربة",
          "النظر في الأصناف المقاومة للجفاف للموسم القادم",
          "تقليل كثافة النباتات للحفاظ على المياه",
        ],
      },
      [DisasterType.LOCUST]: {
        en: [
          "Apply approved insecticides immediately",
          "Coordinate with neighboring farms for area-wide treatment",
          "Report swarm movements to authorities",
          "Protect seed stores and harvested crops",
        ],
        ar: [
          "رش المبيدات المعتمدة فوراً",
          "التنسيق مع المزارع المجاورة للمعالجة الشاملة",
          "الإبلاغ عن تحركات الأسراب للسلطات",
          "حماية مخازن البذور والمحاصيل المحصودة",
        ],
      },
    };

    return (
      recommendationsByType[type] || {
        en: [
          "Document damage",
          "Contact agricultural extension services",
          "Apply for disaster relief",
        ],
        ar: [
          "توثيق الأضرار",
          "التواصل مع خدمات الإرشاد الزراعي",
          "التقدم للحصول على إغاثة الكوارث",
        ],
      }
    );
  }
}
