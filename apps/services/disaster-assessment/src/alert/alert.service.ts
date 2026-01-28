// ═══════════════════════════════════════════════════════════════════════════════
// Alert Service - خدمة التنبيهات
// Early Warning System for Agricultural Disasters
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from "@nestjs/common";

@Injectable()
export class AlertService {
  private alerts = [
    {
      id: "alert-001",
      type: "weather",
      title: "Heavy Rainfall Warning",
      titleAr: "تحذير من أمطار غزيرة",
      description: "Expected heavy rainfall in the next 48 hours",
      descriptionAr: "متوقع أمطار غزيرة خلال الـ 48 ساعة القادمة",
      severity: "high",
      governorate: "hadramaut",
      governorateAr: "حضرموت",
      startTime: new Date(Date.now() + 6 * 3600000).toISOString(),
      endTime: new Date(Date.now() + 54 * 3600000).toISOString(),
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
      createdAt: new Date().toISOString(),
    },
    {
      id: "alert-002",
      type: "pest",
      title: "Locust Swarm Alert",
      titleAr: "تنبيه سرب جراد",
      description: "Desert locust swarm detected 50km west, moving east",
      descriptionAr: "رصد سرب جراد صحراوي على بعد 50 كم غرباً، يتحرك شرقاً",
      severity: "critical",
      governorate: "hodeidah",
      governorateAr: "الحديدة",
      startTime: new Date().toISOString(),
      endTime: new Date(Date.now() + 72 * 3600000).toISOString(),
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
      createdAt: new Date().toISOString(),
    },
    {
      id: "alert-003",
      type: "disease",
      title: "Late Blight Risk - High",
      titleAr: "خطر اللفحة المتأخرة - مرتفع",
      description:
        "Weather conditions favor late blight development in tomatoes",
      descriptionAr: "الظروف الجوية تفضل انتشار اللفحة المتأخرة في الطماطم",
      severity: "medium",
      governorate: "ibb",
      governorateAr: "إب",
      startTime: new Date().toISOString(),
      endTime: new Date(Date.now() + 168 * 3600000).toISOString(),
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
      createdAt: new Date().toISOString(),
    },
    {
      id: "alert-004",
      type: "weather",
      title: "Frost Warning",
      titleAr: "تحذير من الصقيع",
      description: "Temperatures expected to drop below 0°C tonight",
      descriptionAr: "متوقع انخفاض درجات الحرارة إلى ما دون الصفر الليلة",
      severity: "high",
      governorate: "sanaa",
      governorateAr: "صنعاء",
      startTime: new Date(Date.now() + 12 * 3600000).toISOString(),
      endTime: new Date(Date.now() + 24 * 3600000).toISOString(),
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
      createdAt: new Date().toISOString(),
    },
  ];

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Active Alerts
  // ─────────────────────────────────────────────────────────────────────────────

  async getActiveAlerts(params: {
    governorate?: string;
    type?: string;
    severity?: string;
  }) {
    let filtered = this.alerts.filter((a) => a.isActive);

    if (params.governorate) {
      filtered = filtered.filter((a) => a.governorate === params.governorate);
    }
    if (params.type) {
      filtered = filtered.filter((a) => a.type === params.type);
    }
    if (params.severity) {
      filtered = filtered.filter((a) => a.severity === params.severity);
    }

    // Sort by severity (critical first)
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    filtered.sort(
      (a, b) =>
        severityOrder[a.severity as keyof typeof severityOrder] -
        severityOrder[b.severity as keyof typeof severityOrder],
    );

    return {
      total: filtered.length,
      criticalCount: filtered.filter((a) => a.severity === "critical").length,
      highCount: filtered.filter((a) => a.severity === "high").length,
      alerts: filtered,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Weather Alerts
  // ─────────────────────────────────────────────────────────────────────────────

  async getWeatherAlerts(governorate?: string) {
    let weatherAlerts = this.alerts.filter(
      (a) => a.type === "weather" && a.isActive,
    );

    if (governorate) {
      weatherAlerts = weatherAlerts.filter(
        (a) => a.governorate === governorate,
      );
    }

    // Add hourly forecast summary
    const hourlyForecast = Array.from({ length: 24 }, (_, i) => ({
      hour: i,
      temperature: Math.round(15 + Math.sin(i / 4) * 10),
      humidity: Math.round(50 + Math.cos(i / 6) * 20),
      precipitation: Math.random() > 0.7 ? Math.round(Math.random() * 10) : 0,
      windSpeed: Math.round(5 + Math.random() * 15),
    }));

    return {
      alerts: weatherAlerts,
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

  async getPestDiseaseAlerts(params: {
    governorate?: string;
    cropType?: string;
  }) {
    let alerts = this.alerts.filter(
      (a) => (a.type === "pest" || a.type === "disease") && a.isActive,
    );

    if (params.governorate) {
      alerts = alerts.filter((a) => a.governorate === params.governorate);
    }

    // Generate 10-day pest/disease risk forecast
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
      currentAlerts: alerts,
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

  async subscribeToAlerts(dto: {
    userId: string;
    governorate: string;
    types: string[];
  }) {
    return {
      success: true,
      message: "Subscribed successfully",
      messageAr: "تم الاشتراك بنجاح",
      subscription: {
        userId: dto.userId,
        governorate: dto.governorate,
        types: dto.types,
        channels: ["sms", "push", "email"],
        createdAt: new Date().toISOString(),
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Mark Alert as Read
  // ─────────────────────────────────────────────────────────────────────────────

  async markAsRead(id: string) {
    return {
      success: true,
      alertId: id,
      readAt: new Date().toISOString(),
    };
  }
}
