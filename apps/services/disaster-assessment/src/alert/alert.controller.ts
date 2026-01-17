// ═══════════════════════════════════════════════════════════════════════════════
// Alert Controller - مراقب التنبيهات
// Early Warning System for Agricultural Disasters
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from "@nestjs/swagger";
import { AlertService } from "./alert.service";

@ApiTags("alerts")
@Controller("api/v1/alerts")
export class AlertController {
  constructor(private readonly alertService: AlertService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Active Alerts - التنبيهات النشطة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get()
  @ApiOperation({
    summary: "Get active alerts",
    description: "الحصول على التنبيهات النشطة والإنذارات المبكرة",
  })
  @ApiQuery({ name: "governorate", required: false })
  @ApiQuery({ name: "type", required: false })
  @ApiQuery({
    name: "severity",
    enum: ["low", "medium", "high", "critical"],
    required: false,
  })
  @ApiResponse({ status: 200, description: "List of active alerts" })
  async getActiveAlerts(
    @Query("governorate") governorate?: string,
    @Query("type") type?: string,
    @Query("severity") severity?: string,
  ) {
    return this.alertService.getActiveAlerts({ governorate, type, severity });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Weather Alerts - تنبيهات الطقس
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("weather")
  @ApiOperation({
    summary: "Get weather alerts",
    description: "الحصول على تنبيهات الطقس الزراعي",
  })
  @ApiQuery({ name: "governorate", required: false })
  async getWeatherAlerts(@Query("governorate") governorate?: string) {
    return this.alertService.getWeatherAlerts(governorate);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Pest & Disease Alerts - تنبيهات الآفات والأمراض
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("pest-disease")
  @ApiOperation({
    summary: "Get pest and disease alerts",
    description: "الحصول على تنبيهات الآفات والأمراض للأيام العشرة القادمة",
  })
  @ApiQuery({ name: "governorate", required: false })
  @ApiQuery({ name: "cropType", required: false })
  async getPestDiseaseAlerts(
    @Query("governorate") governorate?: string,
    @Query("cropType") cropType?: string,
  ) {
    return this.alertService.getPestDiseaseAlerts({ governorate, cropType });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Subscribe to Alerts - الاشتراك في التنبيهات
  // ─────────────────────────────────────────────────────────────────────────────

  @Post("subscribe")
  @ApiOperation({
    summary: "Subscribe to alerts",
    description: "الاشتراك في تنبيهات منطقة معينة",
  })
  async subscribeToAlerts(
    @Body() dto: { userId: string; governorate: string; types: string[] },
  ) {
    return this.alertService.subscribeToAlerts(dto);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Mark Alert as Read - تحديد التنبيه كمقروء
  // ─────────────────────────────────────────────────────────────────────────────

  @Post(":id/read")
  @ApiOperation({
    summary: "Mark alert as read",
    description: "تحديد التنبيه كمقروء",
  })
  async markAsRead(@Param("id") id: string) {
    return this.alertService.markAsRead(id);
  }
}
