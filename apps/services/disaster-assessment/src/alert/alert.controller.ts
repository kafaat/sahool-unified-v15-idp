// ═══════════════════════════════════════════════════════════════════════════════
// Alert Controller - مراقب التنبيهات
// Early Warning System for Agricultural Disasters
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query, UseGuards, Req } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from "@nestjs/swagger";
import { AlertService } from "./alert.service";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";

@ApiTags("alerts")
@Controller("api/v1/alerts")
@UseGuards(JwtAuthGuard)
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
    @Req() req: any,
    @Query("governorate") governorate?: string,
    @Query("type") type?: string,
    @Query("severity") severity?: string,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.alertService.getActiveAlerts(tenantId, { governorate, type, severity });
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
  async getWeatherAlerts(@Req() req: any, @Query("governorate") governorate?: string) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.alertService.getWeatherAlerts(tenantId, governorate);
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
    @Req() req: any,
    @Query("governorate") governorate?: string,
    @Query("cropType") cropType?: string,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.alertService.getPestDiseaseAlerts(tenantId, { governorate, cropType });
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
    @Req() req: any,
    @Body() dto: { userId: string; governorate: string; types: string[] },
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.alertService.subscribeToAlerts(tenantId, dto);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Mark Alert as Read - تحديد التنبيه كمقروء
  // ─────────────────────────────────────────────────────────────────────────────

  @Post(":id/read")
  @ApiOperation({
    summary: "Mark alert as read",
    description: "تحديد التنبيه كمقروء",
  })
  async markAsRead(@Param("id") id: string, @Req() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.alertService.markAsRead(id, tenantId);
  }
}
