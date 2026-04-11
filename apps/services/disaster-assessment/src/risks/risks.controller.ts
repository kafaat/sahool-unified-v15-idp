// ═══════════════════════════════════════════════════════════════════════════════
// Disaster Risks Controller - مراقب مخاطر الكوارث
// ═══════════════════════════════════════════════════════════════════════════════

import {
  Controller,
  Get,
  Param,
  Query,
  Req,
  UseGuards,
} from "@nestjs/common";
import { ApiOperation, ApiResponse, ApiTags } from "@nestjs/swagger";
import { RisksService } from "./risks.service";
import { ListRisksQueryDto } from "./risks.dto";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";

@ApiTags("disaster-risks")
@Controller("api/v1/disasters/risks")
@UseGuards(JwtAuthGuard)
export class RisksController {
  constructor(private readonly risks: RisksService) {}

  private tenantId(req: any): string {
    return (
      req.user?.tenantId ||
      req.tenantId ||
      req.headers["x-tenant-id"] ||
      "unassigned"
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // GET /api/v1/disasters/risks
  // ─────────────────────────────────────────────────────────────────────────

  @Get()
  @ApiOperation({
    summary: "List risk records",
    description:
      "قائمة سجلات المخاطر (مجمعة من التقارير والتقييمات الحقلية)",
  })
  @ApiResponse({ status: 200, description: "Aggregated risk records" })
  async list(@Req() req: any, @Query() query: ListRisksQueryDto) {
    return this.risks.listRisks(this.tenantId(req), query);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // GET /api/v1/disasters/risks/:id
  // ─────────────────────────────────────────────────────────────────────────

  @Get(":id")
  @ApiOperation({
    summary: "Get risk record",
    description: "الحصول على سجل مخاطرة محدد",
  })
  @ApiResponse({ status: 200, description: "Risk record" })
  @ApiResponse({ status: 404, description: "Risk not found" })
  async get(@Req() req: any, @Param("id") id: string) {
    return this.risks.getRisk(id, this.tenantId(req));
  }
}
