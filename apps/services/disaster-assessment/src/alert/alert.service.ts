// ═══════════════════════════════════════════════════════════════════════════════
// Alert Service - خدمة التنبيهات
// Early Warning System for Agricultural Disasters
// Database-backed with PostgreSQL persistence
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable, Logger } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import {
  DisasterAlertType,
  DisasterSeverity,
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

@Injectable()
export class AlertService {
  private readonly logger = new Logger(AlertService.name);

  constructor(private readonly prisma: PrismaService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Initialize seed data if empty
  // ─────────────────────────────────────────────────────────────────────────────

  async onModuleInit() {
    // Check if database is connected before attempting to seed
    const isHealthy = await this.prisma.isHealthy();
    if (!isHealthy) {
      this.logger.warn("Database not connected - skipping alert seed data initialization");
      return;
    }

    try {
      const count = await this.prisma.disasterAlert.count();
      if (count === 0) {
        await this.seedInitialAlerts();
      }
    } catch (error) {
      this.logger.warn("Could not seed initial alert data:", error);
    }
  }

  private async seedInitialAlerts() {
    this.logger.log("Seeding initial alert data...");

    const seedAlerts = [
      {
        alertType: DisasterAlertType.weather,
        severity: DisasterSeverity.high,
        title: "Heavy Rainfall Warning",
        titleAr: "تحذير من أمطار غزيرة",
        message: "Expected heavy rainfall in the next 48 hours",
        messageAr: "متوقع أمطار غزيرة خلال الـ 48 ساعة القادمة",
        description: "Expected heavy rainfall in the next 48 hours",
        descriptionAr: "متوقع أمطار غزيرة خلال الـ 48 ساعة القادمة",
        governorate: "hadramaut",
        governorateAr: "حضرموت",
        startTime: new Date(Date.now() + 6 * 3600000),
        endTime: new Date(Date.now() + 54 * 3600000),
        isActive: true,
        recommendations: [
          "Ensure proper drainage",
          "Protect harvested crops",
          "Postpone fertilizer application",
        ],
        recommendationsAr: [
          "ضمان الصرف الصحيح",
          "حماية المحاصيل المحصودة",
          "تأجيل تطبيق الأسمدة",
        ],
        tenantId: "default",
      },
      {
        alertType: DisasterAlertType.pest,
        severity: DisasterSeverity.critical,
        title: "Locust Swarm Alert",
        titleAr: "تنبيه سرب جراد",
        message: "Desert locust swarm detected 50km west, moving east",
        messageAr: "رصد سرب جراد صحراوي على بعد 50 كم غرباً، يتحرك شرقاً",
        description: "Desert locust swarm detected 50km west, moving east",
        descriptionAr: "رصد سرب جراد صحراوي على بعد 50 كم غرباً، يتحرك شرقاً",
        governorate: "hodeidah",
        governorateAr: "الحديدة",
        startTime: new Date(),
        endTime: new Date(Date.now() + 72 * 3600000),
        isActive: true,
        recommendations: [
          "Prepare insecticides",
          "Coordinate with neighbors",
          "Report sightings",
        ],
        recommendationsAr: [
          "تحضير المبيدات",
          "التنسيق مع الجيران",
          "الإبلاغ عن المشاهدات",
        ],
        tenantId: "default",
      },
      {
        alertType: DisasterAlertType.disease,
        severity: DisasterSeverity.medium,
        title: "Late Blight Risk - High",
        titleAr: "خطر اللفحة المتأخرة - مرتفع",
        message: "Weather conditions favor late blight development in tomatoes",
        messageAr: "الظروف الجوية تفضل انتشار اللفحة المتأخرة في الطماطم",
        description: "Weather conditions favor late blight development in tomatoes",
        descriptionAr: "الظروف الجوية تفضل انتشار اللفحة المتأخرة في الطماطم",
        governorate: "ibb",
        governorateAr: "إب",
        startTime: new Date(),
        endTime: new Date(Date.now() + 168 * 3600000),
        isActive: true,
        recommendations: [
          "Apply preventive fungicides",
          "Monitor plants daily",
          "Remove infected plants",
        ],
        recommendationsAr: [
          "رش مبيدات فطرية وقائية",
          "مراقبة النباتات يومياً",
          "إزالة النباتات المصابة",
        ],
        tenantId: "default",
      },
      {
        alertType: DisasterAlertType.frost,
        severity: DisasterSeverity.high,
        title: "Frost Warning",
        titleAr: "تحذير من الصقيع",
        message: "Temperatures expected to drop below 0 degrees C tonight",
        messageAr: "متوقع انخفاض درجات الحرارة إلى ما دون الصفر الليلة",
        description: "Temperatures expected to drop below 0 degrees C tonight",
        descriptionAr: "متوقع انخفاض درجات الحرارة إلى ما دون الصفر الليلة",
        governorate: "sanaa",
        governorateAr: "صنعاء",
        startTime: new Date(Date.now() + 12 * 3600000),
        endTime: new Date(Date.now() + 24 * 3600000),
        isActive: true,
        recommendations: [
          "Cover sensitive crops",
          "Irrigate before sunset",
          "Use anti-frost agents",
        ],
        recommendationsAr: [
          "تغطية المحاصيل الحساسة",
          "الري قبل غروب الشمس",
          "استخدام مواد مضادة للصقيع",
        ],
        tenantId: "default",
      },
    ];

    for (const alert of seedAlerts) {
      await this.prisma.disasterAlert.create({ data: alert });
    }

    this.logger.log("Initial alert data seeded successfully");
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Active Alerts
  // ─────────────────────────────────────────────────────────────────────────────

  async getActiveAlerts(tenantId: string, params: {
    governorate?: string;
    type?: string;
    severity?: string;
  }) {
    const where: any = {
      tenantId,
      isActive: true,
    };

    if (params.governorate) {
      where.governorate = params.governorate;
    }
    if (params.type) {
      where.alertType = params.type as DisasterAlertType;
    }
    if (params.severity) {
      where.severity = params.severity as DisasterSeverity;
    }

    const alerts = await this.prisma.disasterAlert.findMany({
      where,
      orderBy: [
        { severity: "desc" }, // Critical first
        { createdAt: "desc" },
      ],
    });

    // Sort by severity (critical first) - custom ordering since Prisma doesn't handle enum sorting well
    const severityOrder: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 };
    const sortedAlerts = [...alerts].sort(
      (a, b) => severityOrder[a.severity] - severityOrder[b.severity],
    );

    return {
      total: sortedAlerts.length,
      criticalCount: sortedAlerts.filter((a) => a.severity === "critical").length,
      highCount: sortedAlerts.filter((a) => a.severity === "high").length,
      alerts: sortedAlerts.map((a) => ({
        id: a.id,
        type: a.alertType,
        title: a.title,
        titleAr: a.titleAr,
        description: a.description || a.message,
        descriptionAr: a.descriptionAr || a.messageAr,
        severity: a.severity,
        governorate: a.governorate,
        governorateAr: a.governorateAr || GOVERNORATE_AR[a.governorate] || a.governorate,
        startTime: a.startTime.toISOString(),
        endTime: a.endTime?.toISOString(),
        isActive: a.isActive,
        recommendations: a.recommendations || [],
        recommendationsAr: a.recommendationsAr || [],
        createdAt: a.createdAt.toISOString(),
      })),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Weather Alerts
  // ─────────────────────────────────────────────────────────────────────────────

  async getWeatherAlerts(tenantId: string, governorate?: string) {
    const where: any = {
      tenantId,
      alertType: DisasterAlertType.weather,
      isActive: true,
    };

    if (governorate) {
      where.governorate = governorate;
    }

    const weatherAlerts = await this.prisma.disasterAlert.findMany({
      where,
      orderBy: { createdAt: "desc" },
    });

    // Add hourly forecast summary (mock data - could be integrated with weather service)
    const hourlyForecast = Array.from({ length: 24 }, (_, i) => ({
      hour: i,
      temperature: Math.round(15 + Math.sin(i / 4) * 10),
      humidity: Math.round(50 + Math.cos(i / 6) * 20),
      precipitation: Math.random() > 0.7 ? Math.round(Math.random() * 10) : 0,
      windSpeed: Math.round(5 + Math.random() * 15),
    }));

    return {
      alerts: weatherAlerts.map((a) => ({
        id: a.id,
        type: a.alertType,
        title: a.title,
        titleAr: a.titleAr,
        description: a.description || a.message,
        descriptionAr: a.descriptionAr || a.messageAr,
        severity: a.severity,
        governorate: a.governorate,
        governorateAr: a.governorateAr || GOVERNORATE_AR[a.governorate] || a.governorate,
        startTime: a.startTime.toISOString(),
        endTime: a.endTime?.toISOString(),
        isActive: a.isActive,
        recommendations: a.recommendations || [],
        recommendationsAr: a.recommendationsAr || [],
        createdAt: a.createdAt.toISOString(),
      })),
      hourlyForecast,
      summary: {
        maxTemp: Math.max(...hourlyForecast.map((h) => h.temperature)),
        minTemp: Math.min(...hourlyForecast.map((h) => h.temperature)),
        avgHumidity: Math.round(
          hourlyForecast.reduce((s, h) => s + h.humidity, 0) / 24,
        ),
        totalPrecipitation: hourlyForecast.reduce(
          (s, h) => s + h.precipitation,
          0,
        ),
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Pest & Disease Alerts (10-day forecast as per article)
  // ─────────────────────────────────────────────────────────────────────────────

  async getPestDiseaseAlerts(tenantId: string, params: {
    governorate?: string;
    cropType?: string;
  }) {
    const where: any = {
      tenantId,
      alertType: {
        in: [DisasterAlertType.pest, DisasterAlertType.disease],
      },
      isActive: true,
    };

    if (params.governorate) {
      where.governorate = params.governorate;
    }

    const alerts = await this.prisma.disasterAlert.findMany({
      where,
      orderBy: { createdAt: "desc" },
    });

    // Generate 10-day pest/disease risk forecast (mock data)
    const tenDayForecast = Array.from({ length: 10 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() + i);

      return {
        date: date.toISOString().split("T")[0],
        pestRisk: Math.round(Math.random() * 100),
        diseaseRisk: Math.round(Math.random() * 100),
        conditions: {
          humidity: Math.round(50 + Math.random() * 30),
          temperature: Math.round(20 + Math.random() * 15),
          leafWetness: Math.round(Math.random() * 12), // hours
        },
        riskLevel: ["low", "medium", "high"][Math.floor(Math.random() * 3)],
        recommendations:
          i < 3 ? ["Monitor closely", "Apply preventive measures"] : [],
        recommendationsAr:
          i < 3 ? ["المراقبة عن كثب", "تطبيق إجراءات وقائية"] : [],
      };
    });

    return {
      currentAlerts: alerts.map((a) => ({
        id: a.id,
        type: a.alertType,
        title: a.title,
        titleAr: a.titleAr,
        description: a.description || a.message,
        descriptionAr: a.descriptionAr || a.messageAr,
        severity: a.severity,
        governorate: a.governorate,
        governorateAr: a.governorateAr || GOVERNORATE_AR[a.governorate] || a.governorate,
        startTime: a.startTime.toISOString(),
        endTime: a.endTime?.toISOString(),
        isActive: a.isActive,
        recommendations: a.recommendations || [],
        recommendationsAr: a.recommendationsAr || [],
        createdAt: a.createdAt.toISOString(),
      })),
      tenDayForecast,
      highRiskDays: tenDayForecast.filter((d) => d.riskLevel === "high").length,
      summary: {
        overallPestRisk: Math.round(
          tenDayForecast.reduce((s, d) => s + d.pestRisk, 0) / 10,
        ),
        overallDiseaseRisk: Math.round(
          tenDayForecast.reduce((s, d) => s + d.diseaseRisk, 0) / 10,
        ),
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Subscribe to Alerts
  // ─────────────────────────────────────────────────────────────────────────────

  async subscribeToAlerts(tenantId: string, dto: {
    userId: string;
    governorate: string;
    types: string[];
  }) {
    // Upsert subscription
    const subscription = await this.prisma.alertSubscription.upsert({
      where: {
        idx_subscription_user_gov: {
          userId: dto.userId,
          governorate: dto.governorate,
        },
      },
      update: {
        types: dto.types,
        channels: ["sms", "push", "email"],
        isActive: true,
      },
      create: {
        userId: dto.userId,
        governorate: dto.governorate,
        types: dto.types,
        channels: ["sms", "push", "email"],
        isActive: true,
        tenantId,
      },
    });

    return {
      success: true,
      message: "Subscribed successfully",
      messageAr: "تم الاشتراك بنجاح",
      subscription: {
        id: subscription.id,
        userId: subscription.userId,
        governorate: subscription.governorate,
        types: subscription.types,
        channels: subscription.channels,
        createdAt: subscription.createdAt.toISOString(),
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Mark Alert as Read
  // ─────────────────────────────────────────────────────────────────────────────

  async markAsRead(id: string, tenantId: string) {
    // In a full implementation, this would update a user-alert read status table
    // For now, we just return success
    const alert = await this.prisma.disasterAlert.findFirst({
      where: { id, tenantId },
    });

    if (!alert) {
      return {
        success: false,
        error: "Alert not found",
        errorAr: "التنبيه غير موجود",
      };
    }

    return {
      success: true,
      alertId: id,
      readAt: new Date().toISOString(),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Create Alert (for internal use or admin)
  // ─────────────────────────────────────────────────────────────────────────────

  async createAlert(tenantId: string, data: {
    alertType: string;
    severity: string;
    title: string;
    titleAr?: string;
    message: string;
    messageAr?: string;
    governorate: string;
    startTime: Date;
    endTime?: Date;
    recommendations?: string[];
    recommendationsAr?: string[];
    reportId?: string;
  }) {
    const alert = await this.prisma.disasterAlert.create({
      data: {
        alertType: data.alertType as DisasterAlertType,
        severity: data.severity as DisasterSeverity,
        title: data.title,
        titleAr: data.titleAr,
        message: data.message,
        messageAr: data.messageAr,
        governorate: data.governorate,
        governorateAr: GOVERNORATE_AR[data.governorate] || data.governorate,
        startTime: data.startTime,
        endTime: data.endTime,
        isActive: true,
        recommendations: data.recommendations,
        recommendationsAr: data.recommendationsAr,
        reportId: data.reportId,
        tenantId,
      },
    });

    return {
      success: true,
      message: "Alert created successfully",
      messageAr: "تم إنشاء التنبيه بنجاح",
      alert: {
        id: alert.id,
        title: alert.title,
        titleAr: alert.titleAr,
        createdAt: alert.createdAt.toISOString(),
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Deactivate Alert
  // ─────────────────────────────────────────────────────────────────────────────

  async deactivateAlert(id: string, tenantId: string) {
    // Verify the alert belongs to this tenant
    const existing = await this.prisma.disasterAlert.findFirst({
      where: { id, tenantId },
    });

    if (!existing) {
      return {
        success: false,
        error: "Alert not found",
        errorAr: "التنبيه غير موجود",
      };
    }

    const alert = await this.prisma.disasterAlert.update({
      where: { id },
      data: { isActive: false },
    });

    return {
      success: true,
      message: "Alert deactivated",
      messageAr: "تم إلغاء تنشيط التنبيه",
      alertId: alert.id,
    };
  }
}
