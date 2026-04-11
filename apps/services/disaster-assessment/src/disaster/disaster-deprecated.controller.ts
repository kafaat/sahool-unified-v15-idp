// ═══════════════════════════════════════════════════════════════════════════════
// Deprecated Disaster Alias Controller
// مراقب أليس المسارات المتوقفة
// ═══════════════════════════════════════════════════════════════════════════════
//
// Exposes the legacy singular `/api/v1/disaster/*` paths as deprecated aliases
// forwarding to the new plural `/api/v1/disasters/*` handlers. All responses
// include RFC 8594 deprecation headers (`Deprecation: true`, `Sunset`, `Link`).
//
// Sunset: 2026-09-01 (2 minor versions after deprecation).
// ═══════════════════════════════════════════════════════════════════════════════

import {
  Controller,
  Get,
  Query,
  Req,
  Res,
  UseGuards,
} from "@nestjs/common";
import type { Response } from "express";
import { ApiOperation, ApiTags } from "@nestjs/swagger";
import { DisasterService } from "./disaster.service";
import { EventsService } from "../events/events.service";
import { ListEventsQueryDto } from "../events/events.dto";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";

const DEPRECATION_SUNSET = "2026-09-01T00:00:00Z";
const DEPRECATION_HEADERS: Record<string, string> = {
  Deprecation: "true",
  Sunset: DEPRECATION_SUNSET,
  "X-API-Deprecated": "true",
  "X-API-Sunset": DEPRECATION_SUNSET,
};

function applyDeprecationHeaders(res: Response, replacedBy: string) {
  for (const [k, v] of Object.entries(DEPRECATION_HEADERS)) {
    res.setHeader(k, v);
  }
  res.setHeader(
    "Link",
    `<${replacedBy}>; rel="successor-version"; type="application/json"`,
  );
}

@ApiTags("disaster-deprecated")
@Controller("api/v1/disaster")
@UseGuards(JwtAuthGuard)
export class DisasterDeprecatedController {
  constructor(
    private readonly disasterService: DisasterService,
    private readonly eventsService: EventsService,
  ) {}

  private tenantId(req: any): string {
    return (
      req.user?.tenantId ||
      req.tenantId ||
      req.headers["x-tenant-id"] ||
      "unassigned"
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // GET /api/v1/disaster/events
  //   → /api/v1/disasters/events
  // ─────────────────────────────────────────────────────────────────────────

  @Get("events")
  @ApiOperation({
    summary: "[DEPRECATED] List disaster events",
    description: "Use /api/v1/disasters/events instead",
  })
  async events(
    @Req() req: any,
    @Res({ passthrough: true }) res: Response,
    @Query() query: ListEventsQueryDto,
  ) {
    applyDeprecationHeaders(res, "/api/v1/disasters/events");
    return this.eventsService.listEvents(this.tenantId(req), query);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // GET /api/v1/disaster/stats
  //   → /api/v1/disasters/stats/summary
  // ─────────────────────────────────────────────────────────────────────────

  @Get("stats")
  @ApiOperation({
    summary: "[DEPRECATED] Get disaster statistics",
    description: "Use /api/v1/disasters/stats/summary instead",
  })
  async stats(
    @Req() req: any,
    @Res({ passthrough: true }) res: Response,
    @Query("year") year?: number,
    @Query("governorate") governorate?: string,
  ) {
    applyDeprecationHeaders(res, "/api/v1/disasters/stats/summary");
    return this.disasterService.getStatistics(this.tenantId(req), {
      year,
      governorate,
    });
  }
}
