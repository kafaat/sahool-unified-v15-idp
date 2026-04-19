/**
 * Dashboard Controller — GET endpoints consumed by the web home screen
 * (apps/web/src/features/home/api.ts, DASHBOARD_ENDPOINTS in
 * packages/shared-types/src/contracts/api-endpoints.ts).
 *
 * These endpoints previously had no backend — every call 404'd and the
 * dashboard widget fell back to cached/mock data. This module aggregates
 * tenant-scoped counts directly from Prisma (Field, Task) and returns
 * the `DashboardData` shape the web expects.
 *
 * Weather + recent-activity blocks intentionally return sensible empty
 * defaults — aggregating those requires cross-service calls (weather-
 * service, notification-service) which belong in a dedicated BFF, not
 * here. The UI renders empty-state gracefully when arrays/objects are
 * empty.
 */

import { Controller, Get, Query, Req } from "@nestjs/common";
import { ApiOperation, ApiTags } from "@nestjs/swagger";
import { PrismaService } from "../prisma/prisma.service";
import { getRequestTenantId } from "../auth/tenant.utils";

@ApiTags("Dashboard - لوحة التحكم")
@Controller("api/v1/dashboard")
export class DashboardController {
  constructor(private readonly prisma: PrismaService) {}

  private async statsFor(tenantId: string) {
    // Four counts tracked by web DashboardData.stats:
    //   totalFields, activeTasks, activeAlerts, completedTasks
    // activeAlerts is served from this service's view of task urgency
    // (Task with priority='urgent' AND status='pending') since the
    // alert-service lives behind a different DB and a cross-service
    // join in a dashboard widget is overkill.
    const [totalFields, activeTasks, completedTasks, activeAlerts] = await Promise.all([
      // Field model has no soft-delete column; "total fields" means
      // non-inactive rows for this tenant.
      this.prisma.field.count({ where: { tenantId, NOT: { status: "inactive" } } }),
      this.prisma.task.count({ where: { tenantId, status: "pending" } }),
      this.prisma.task.count({ where: { tenantId, status: "completed" } }),
      this.prisma.task.count({
        where: { tenantId, status: "pending", priority: "urgent" },
      }),
    ]);
    return { totalFields, activeTasks, activeAlerts, completedTasks };
  }

  @Get("stats")
  @ApiOperation({ summary: "Dashboard counters (DASHBOARD_ENDPOINTS.STATS)" })
  async stats(@Req() req: any) {
    const tenantId = getRequestTenantId(req);
    const data = await this.statsFor(tenantId);
    return { success: true, data };
  }

  @Get("summary")
  @ApiOperation({
    summary: "Aggregated dashboard payload (DASHBOARD_ENDPOINTS.SUMMARY)",
    description:
      "Returns the DashboardData shape consumed by apps/web/src/features/home/api.ts. " +
      "weather/recentActivity default to null/[] until a BFF aggregator wires those services.",
  })
  async summary(@Req() req: any) {
    const tenantId = getRequestTenantId(req);
    const stats = await this.statsFor(tenantId);
    const upcomingTaskRows = await this.prisma.task.findMany({
      where: { tenantId, status: "pending" },
      orderBy: { dueDate: "asc" },
      take: 5,
      select: {
        id: true,
        title: true,
        titleAr: true,
        dueDate: true,
        priority: true,
        status: true,
      },
    });
    const upcomingTasks = upcomingTaskRows.map((t) => ({
      id: t.id,
      title: t.title,
      titleAr: t.titleAr ?? t.title,
      dueDate: t.dueDate ? t.dueDate.toISOString() : "",
      priority: t.priority as "high" | "medium" | "low",
      status: String(t.status),
    }));
    return {
      success: true,
      data: {
        stats,
        weather: null,
        recentActivity: [],
        upcomingTasks,
      },
    };
  }

  @Get("recent-activity")
  @ApiOperation({ summary: "Recent activity feed (DASHBOARD_ENDPOINTS.RECENT_ACTIVITY)" })
  async recentActivity(@Req() req: any, @Query("limit") limitRaw?: string) {
    const tenantId = getRequestTenantId(req);
    const limit = Math.min(Math.max(parseInt(limitRaw ?? "10", 10) || 10, 1), 50);
    // Pull recently completed or updated tasks as the activity stream.
    const rows = await this.prisma.task.findMany({
      where: { tenantId },
      orderBy: [{ completedAt: "desc" }, { updatedAt: "desc" }],
      take: limit,
      select: {
        id: true,
        title: true,
        titleAr: true,
        description: true,
        status: true,
        completedAt: true,
        updatedAt: true,
      },
    });
    const items = rows.map((r) => ({
      id: r.id,
      type: "task" as const,
      title: r.title,
      titleAr: r.titleAr ?? r.title,
      description: r.description ?? "",
      descriptionAr: r.description ?? "",
      timestamp: (r.completedAt ?? r.updatedAt).toISOString(),
    }));
    return { success: true, data: items };
  }

  @Get("weather")
  @ApiOperation({ summary: "Dashboard weather widget (DASHBOARD_ENDPOINTS.WEATHER_WIDGET)" })
  async weather() {
    // Weather aggregation needs a location from the tenant profile AND
    // a call to weather-service. Until the BFF exists, return null so
    // the web widget renders its "no data" state gracefully instead of
    // 404-ing.
    return { success: true, data: null };
  }

  @Get("alerts")
  @ApiOperation({ summary: "Dashboard alerts widget (DASHBOARD_ENDPOINTS.ALERTS_WIDGET)" })
  async alerts(@Req() req: any) {
    const tenantId = getRequestTenantId(req);
    // Surface the urgent open tasks as "alerts" — same data the stats
    // endpoint counts. Keeps the dashboard consistent without a
    // separate alert store.
    const rows = await this.prisma.task.findMany({
      where: { tenantId, status: "pending", priority: "urgent" },
      orderBy: { dueDate: "asc" },
      take: 10,
      select: { id: true, title: true, titleAr: true, dueDate: true },
    });
    const items = rows.map((r) => ({
      id: r.id,
      severity: "high" as const,
      title: r.title,
      titleAr: r.titleAr ?? r.title,
      timestamp: (r.dueDate ?? new Date()).toISOString(),
    }));
    return { success: true, data: items };
  }
}
