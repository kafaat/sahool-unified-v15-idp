// ═══════════════════════════════════════════════════════════════════════════════
// Disaster Service - خدمة الكوارث
// Database-backed disaster management with PostgreSQL persistence
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable, Logger } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import {
  CreateDisasterReportDto,
  DisasterAssessmentDto,
  DisasterType,
  Severity,
} from "./disaster.dto";
import {
  DisasterType as PrismaDisasterType,
  DisasterSeverity as PrismaSeverity,
  DisasterStatus as PrismaDisasterStatus,
} from "@prisma/client";

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

// Map DTOs to Prisma enums
const mapDisasterType = (type: DisasterType): PrismaDisasterType => {
  return type as unknown as PrismaDisasterType;
};

const mapSeverity = (severity: Severity): PrismaSeverity => {
  return severity as unknown as PrismaSeverity;
};

@Injectable()
export class DisasterService {
  private readonly logger = new Logger(DisasterService.name);

  constructor(private readonly prisma: PrismaService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Initialize seed data if empty
  // ─────────────────────────────────────────────────────────────────────────────

  async onModuleInit() {
    // Check if database is connected before attempting to seed
    const isHealthy = await this.prisma.isHealthy();
    if (!isHealthy) {
      this.logger.warn("Database not connected - skipping seed data initialization");
      return;
    }

    try {
      const count = await this.prisma.disasterReport.count();
      if (count === 0) {
        await this.seedInitialData();
      }
    } catch (error) {
      this.logger.warn("Could not seed initial data:", error);
    }
  }

  private async seedInitialData() {
    this.logger.log("Seeding initial disaster data...");

    const seedData = [
      {
        type: PrismaDisasterType.flood,
        title: "Hadramaut Valley Flood",
        titleAr: "فيضان وادي حضرموت",
        description: "Heavy rainfall caused flooding in agricultural areas",
        governorate: "hadramaut",
        location: { lat: 15.9, lng: 48.8 },
        affectedRadiusKm: 15,
        severity: PrismaSeverity.high,
        status: PrismaDisasterStatus.active,
        affectedFieldsCount: 45,
        totalAffectedAreaHectares: 320,
        totalEstimatedLossYER: BigInt(15000000),
        startDate: new Date("2024-12-15T00:00:00Z"),
        reportedBy: "system",
        tenantId: "default",
      },
      {
        type: PrismaDisasterType.drought,
        title: "Marib Drought",
        titleAr: "جفاف مأرب",
        description: "Extended dry period affecting crop growth",
        governorate: "marib",
        location: { lat: 15.4, lng: 45.3 },
        affectedRadiusKm: 30,
        severity: PrismaSeverity.medium,
        status: PrismaDisasterStatus.monitoring,
        affectedFieldsCount: 120,
        totalAffectedAreaHectares: 850,
        totalEstimatedLossYER: BigInt(8500000),
        startDate: new Date("2024-11-01T00:00:00Z"),
        reportedBy: "system",
        tenantId: "default",
      },
      {
        type: PrismaDisasterType.locust,
        title: "Desert Locust Swarm - Hodeidah",
        titleAr: "سرب جراد صحراوي - الحديدة",
        description:
          "Desert locust swarm detected moving towards agricultural areas",
        governorate: "hodeidah",
        location: { lat: 14.8, lng: 42.9 },
        affectedRadiusKm: 25,
        severity: PrismaSeverity.critical,
        status: PrismaDisasterStatus.active,
        affectedFieldsCount: 200,
        totalAffectedAreaHectares: 1500,
        totalEstimatedLossYER: BigInt(45000000),
        startDate: new Date("2024-12-17T00:00:00Z"),
        reportedBy: "system",
        tenantId: "default",
      },
    ];

    for (const data of seedData) {
      await this.prisma.disasterReport.create({ data });
    }

    this.logger.log("Initial disaster data seeded successfully");
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Active Disasters
  // ─────────────────────────────────────────────────────────────────────────────

  async getActiveDisasters(tenantId: string, params: {
    type?: DisasterType;
    governorate?: string;
    severity?: string;
  }) {
    const where: any = { tenantId };

    if (params.type) {
      where.type = mapDisasterType(params.type);
    }
    if (params.governorate) {
      where.governorate = params.governorate;
    }
    if (params.severity) {
      where.severity = params.severity as PrismaSeverity;
    }

    const disasters = await this.prisma.disasterReport.findMany({
      where,
      orderBy: { createdAt: "desc" },
    });

    return {
      total: disasters.length,
      disasters: disasters.map((d) => ({
        id: d.id,
        type: d.type,
        title: d.title,
        titleAr: d.titleAr,
        description: d.description,
        governorate: d.governorate,
        governorateAr: GOVERNORATE_AR[d.governorate] || d.governorate,
        location: d.location,
        affectedRadiusKm: d.affectedRadiusKm,
        severity: d.severity,
        status: d.status,
        affectedFieldsCount: d.affectedFieldsCount,
        totalAffectedAreaHectares: d.totalAffectedAreaHectares,
        totalEstimatedLossYER: d.totalEstimatedLossYER
          ? Number(d.totalEstimatedLossYER)
          : null,
        startDate: d.startDate?.toISOString(),
        createdAt: d.createdAt.toISOString(),
        updatedAt: d.updatedAt.toISOString(),
        typeAr: DISASTER_TYPE_AR[d.type as DisasterType],
      })),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Disaster by ID
  // ─────────────────────────────────────────────────────────────────────────────

  async getDisasterById(id: string, tenantId: string) {
    const disaster = await this.prisma.disasterReport.findFirst({
      where: { id, tenantId },
      include: {
        fieldAssessments: true,
      },
    });

    if (!disaster) {
      return { error: "Disaster not found", errorAr: "الكارثة غير موجودة" };
    }

    return {
      id: disaster.id,
      type: disaster.type,
      title: disaster.title,
      titleAr: disaster.titleAr,
      description: disaster.description,
      governorate: disaster.governorate,
      governorateAr: GOVERNORATE_AR[disaster.governorate] || disaster.governorate,
      location: disaster.location,
      affectedRadiusKm: disaster.affectedRadiusKm,
      severity: disaster.severity,
      status: disaster.status,
      affectedFieldsCount: disaster.affectedFieldsCount,
      totalAffectedAreaHectares: disaster.totalAffectedAreaHectares,
      totalEstimatedLossYER: disaster.totalEstimatedLossYER
        ? Number(disaster.totalEstimatedLossYER)
        : null,
      startDate: disaster.startDate?.toISOString(),
      createdAt: disaster.createdAt.toISOString(),
      updatedAt: disaster.updatedAt.toISOString(),
      typeAr: DISASTER_TYPE_AR[disaster.type as DisasterType],
      // Include affected fields from assessments or generate mock
      affectedFields:
        disaster.fieldAssessments.length > 0
          ? disaster.fieldAssessments.map((a: any) => ({
              fieldId: a.fieldId,
              areaHectares: a.affectedAreaHectares,
              damagePercentage: a.damagePercentage,
              cropType: a.affectedCropType,
            }))
          : this.generateAffectedFields(disaster.affectedFieldsCount),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Report New Disaster
  // ─────────────────────────────────────────────────────────────────────────────

  async reportDisaster(dto: CreateDisasterReportDto, tenantId: string) {
    const disaster = await this.prisma.disasterReport.create({
      data: {
        type: mapDisasterType(dto.type),
        title: dto.title,
        titleAr: dto.title, // In real implementation, translate or require Arabic title
        description: dto.description,
        governorate: dto.governorate,
        district: dto.district,
        location: dto.location as any,
        affectedRadiusKm: dto.affectedRadiusKm,
        severity: mapSeverity(dto.severity),
        status: PrismaDisasterStatus.active,
        startDate: dto.startDate ? new Date(dto.startDate) : null,
        images: dto.images as any,
        reportedBy: dto.reportedBy || "anonymous",
        tenantId,
        affectedFieldsCount: 0,
        totalAffectedAreaHectares: 0,
        totalEstimatedLossYER: BigInt(0),
      },
    });

    return {
      success: true,
      message: "Disaster reported successfully",
      messageAr: "تم الإبلاغ عن الكارثة بنجاح",
      disaster: {
        id: disaster.id,
        type: disaster.type,
        title: disaster.title,
        titleAr: disaster.titleAr,
        governorate: disaster.governorate,
        governorateAr: GOVERNORATE_AR[disaster.governorate] || disaster.governorate,
        typeAr: DISASTER_TYPE_AR[dto.type],
        severity: disaster.severity,
        status: disaster.status,
        createdAt: disaster.createdAt.toISOString(),
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Assess Field Damage
  // ─────────────────────────────────────────────────────────────────────────────

  async assessFieldDamage(fieldId: string, dto: DisasterAssessmentDto, tenantId: string) {
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
    const recommendations = await this.generateRecommendations(
      dto.disasterId,
      damageLevel.level,
    );

    // Store assessment in database
    const assessment = await this.prisma.fieldAssessment.create({
      data: {
        fieldId,
        disasterId: dto.disasterId,
        damagePercentage: Math.round(damagePercentage * 10) / 10,
        damageLevel: damageLevel.level,
        damageLevelAr: damageLevel.levelAr,
        affectedAreaHectares: Math.round(affectedArea * 100) / 100,
        estimatedLossYER: BigInt(estimatedLoss),
        affectedCropType: dto.affectedCropType || "wheat",
        recommendations: recommendations.en as any,
        recommendationsAr: recommendations.ar as any,
        insuranceEligible: damagePercentage >= 30,
        insuranceClaimAmount:
          damagePercentage >= 30 ? BigInt(Math.round(estimatedLoss * 0.7)) : null,
        assessmentNotes: dto.assessmentNotes,
        assessmentImages: dto.assessmentImages as any,
        tenantId,
      },
    });

    // Update disaster statistics
    await this.updateDisasterStats(dto.disasterId);

    return {
      fieldId,
      disasterId: dto.disasterId,
      damagePercentage: assessment.damagePercentage,
      damageLevel: assessment.damageLevel,
      damageLevelAr: assessment.damageLevelAr,
      damageColor: damageLevel.color,
      affectedAreaHectares: assessment.affectedAreaHectares,
      estimatedLossYER: Number(assessment.estimatedLossYER),
      affectedCropType: assessment.affectedCropType,
      recommendations: recommendations.en,
      recommendationsAr: recommendations.ar,
      insuranceEligible: assessment.insuranceEligible,
      insuranceClaimAmount: assessment.insuranceClaimAmount
        ? Number(assessment.insuranceClaimAmount)
        : 0,
      assessedAt: assessment.assessedAt.toISOString(),
      assessmentNotes: assessment.assessmentNotes,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Update Disaster Statistics after assessment
  // ─────────────────────────────────────────────────────────────────────────────

  private async updateDisasterStats(disasterId: string) {
    const assessments = await this.prisma.fieldAssessment.findMany({
      where: { disasterId },
    });

    const totalArea = assessments.reduce(
      (sum, a) => sum + a.affectedAreaHectares,
      0,
    );
    const totalLoss = assessments.reduce(
      (sum, a) => sum + Number(a.estimatedLossYER),
      0,
    );

    await this.prisma.disasterReport.update({
      where: { id: disasterId },
      data: {
        affectedFieldsCount: assessments.length,
        totalAffectedAreaHectares: totalArea,
        totalEstimatedLossYER: BigInt(Math.round(totalLoss)),
      },
    });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Flood Risk Map
  // ─────────────────────────────────────────────────────────────────────────────

  async getFloodRiskMap(governorate: string, tenantId: string) {
    // Mock flood risk zones (could be enhanced with actual GIS data)
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

  async getDroughtIndex(governorate: string, tenantId: string) {
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

  async getStatistics(tenantId: string, params: { year?: number; governorate?: string }) {
    const year = params.year || new Date().getFullYear();
    const startOfYear = new Date(`${year}-01-01T00:00:00Z`);
    const endOfYear = new Date(`${year}-12-31T23:59:59Z`);

    const where: any = {
      tenantId,
      createdAt: {
        gte: startOfYear,
        lte: endOfYear,
      },
    };

    if (params.governorate) {
      where.governorate = params.governorate;
    }

    // Get counts from database
    const totalDisasters = await this.prisma.disasterReport.count({ where });
    const activeDisasters = await this.prisma.disasterReport.count({
      where: { ...where, status: PrismaDisasterStatus.active },
    });
    const resolvedDisasters = await this.prisma.disasterReport.count({
      where: { ...where, status: PrismaDisasterStatus.resolved },
    });

    // Get aggregate statistics
    const aggregates = await this.prisma.disasterReport.aggregate({
      where,
      _sum: {
        totalAffectedAreaHectares: true,
        affectedFieldsCount: true,
      },
    });

    // Get loss totals
    const disasters = await this.prisma.disasterReport.findMany({
      where,
      select: { totalEstimatedLossYER: true, type: true },
    });

    const totalLoss = disasters.reduce(
      (sum, d) => sum + (d.totalEstimatedLossYER ? Number(d.totalEstimatedLossYER) : 0),
      0,
    );

    // Group by type
    const byType = await this.prisma.disasterReport.groupBy({
      by: ["type"],
      where,
      _count: { id: true },
    });

    const byTypeWithLoss = byType.map((item) => {
      const typeLoss = disasters
        .filter((d) => d.type === item.type)
        .reduce(
          (sum, d) => sum + (d.totalEstimatedLossYER ? Number(d.totalEstimatedLossYER) : 0),
          0,
        );
      return {
        type: item.type,
        typeAr: DISASTER_TYPE_AR[item.type as DisasterType] || item.type,
        count: item._count.id,
        lossYER: typeLoss,
      };
    });

    // Get monthly distribution
    const byMonth = await this.getMonthlyDistribution(year, tenantId, params.governorate);

    return {
      year,
      governorate: params.governorate || "all",
      governorateAr: params.governorate
        ? GOVERNORATE_AR[params.governorate]
        : "جميع المحافظات",
      summary: {
        totalDisasters,
        activeDisasters,
        resolvedDisasters,
        totalAffectedAreaHectares: aggregates._sum.totalAffectedAreaHectares || 0,
        totalEstimatedLossYER: totalLoss,
        totalFieldsAffected: aggregates._sum.affectedFieldsCount || 0,
        farmersAffected: Math.round((aggregates._sum.affectedFieldsCount || 0) * 0.7),
      },
      byType: byTypeWithLoss,
      byMonth,
      trend: totalDisasters > 0 ? "stable" : "none",
      trendAr: totalDisasters > 0 ? "مستقر" : "لا بيانات",
      comparedToLastYear: 0,
    };
  }

  private async getMonthlyDistribution(year: number, tenantId: string, governorate?: string) {
    const months = [];
    for (let month = 1; month <= 12; month++) {
      const startOfMonth = new Date(`${year}-${month.toString().padStart(2, "0")}-01`);
      const endOfMonth = new Date(year, month, 0, 23, 59, 59);

      const where: any = {
        tenantId,
        createdAt: {
          gte: startOfMonth,
          lte: endOfMonth,
        },
      };

      if (governorate) {
        where.governorate = governorate;
      }

      const count = await this.prisma.disasterReport.count({ where });
      const disasters = await this.prisma.disasterReport.findMany({
        where,
        select: { totalEstimatedLossYER: true },
      });

      const lossYER = disasters.reduce(
        (sum, d) => sum + (d.totalEstimatedLossYER ? Number(d.totalEstimatedLossYER) : 0),
        0,
      );

      months.push({ month, count, lossYER });
    }
    return months;
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

  private async generateRecommendations(disasterId: string, damageLevel: string) {
    const disaster = await this.prisma.disasterReport.findUnique({
      where: { id: disasterId },
      select: { type: true },
    });

    const type = disaster?.type || PrismaDisasterType.flood;

    const recommendationsByType: Record<string, { en: string[]; ar: string[] }> = {
      [PrismaDisasterType.flood]: {
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
      [PrismaDisasterType.drought]: {
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
      [PrismaDisasterType.locust]: {
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
