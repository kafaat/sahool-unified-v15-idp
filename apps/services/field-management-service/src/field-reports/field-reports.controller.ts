/**
 * Field Reports Controller
 *
 * Routes:
 *   POST   /api/v1/fields/:fieldId/reports       — enqueue a new report
 *   GET    /api/v1/fields/:fieldId/reports       — list reports for a field
 *   GET    /api/v1/field-reports/:id             — metadata (poll for status)
 *   GET    /api/v1/field-reports/:id/content     — rendered HTML content
 */

import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Query,
  ParseUUIDPipe,
  ValidationPipe,
  HttpCode,
  HttpStatus,
  Req,
  Res,
  UseInterceptors,
} from "@nestjs/common";
import type { Response } from "express";
import { ApiTags, ApiOperation, ApiResponse, ApiParam } from "@nestjs/swagger";
import { FieldReportsService } from "./field-reports.service";
import {
  CreateFieldReportDto,
  QueryFieldReportsDto,
} from "./dto/field-report.dto";
import { getRequestTenantId } from "../auth/tenant.utils";
import { IdempotencyInterceptor } from "../idempotency/idempotency.interceptor";
import { Public } from "../auth/public.decorator";

@ApiTags("Field Reports - تقارير الحقل")
@Controller("api/v1")
export class FieldReportsController {
  constructor(private readonly service: FieldReportsService) {}

  /**
   * Enqueue a new report. Returns immediately with status='pending';
   * client polls GET /field-reports/:id until status becomes 'ready'.
   */
  @Post("fields/:fieldId/reports")
  @HttpCode(HttpStatus.ACCEPTED)
  @UseInterceptors(IdempotencyInterceptor)
  @ApiOperation({
    summary: "Request a new field report (async)",
    description:
      "طلب توليد تقرير جديد للحقل — يتم التوليد في الخلفية",
  })
  @ApiResponse({
    status: 202,
    description: "Report queued — poll for status",
  })
  async request(
    @Req() req: any,
    @Param("fieldId", ParseUUIDPipe) fieldId: string,
    @Body(new ValidationPipe({ transform: true, whitelist: true }))
    dto: CreateFieldReportDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const userId: string | undefined = req.user?.sub ?? req.user?.id;
    const row = await this.service.requestReport(
      fieldId,
      tenantId,
      dto,
      userId,
    );
    return {
      success: true,
      data: row,
      message: "تم قبول طلب التقرير — جاري التوليد",
    };
  }

  @Get("fields/:fieldId/reports")
  @ApiOperation({ summary: "List reports for a field" })
  @ApiParam({ name: "fieldId", description: "Field UUID" })
  async listByField(
    @Req() req: any,
    @Param("fieldId", ParseUUIDPipe) fieldId: string,
    @Query(new ValidationPipe({ transform: true, whitelist: true }))
    q: QueryFieldReportsDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const items = await this.service.list(fieldId, tenantId, q);
    return { success: true, items, total: items.length };
  }

  @Get("field-reports/:id")
  @ApiOperation({ summary: "Get a report metadata (poll for status)" })
  async getById(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const row = await this.service.getById(id, tenantId);
    return { success: true, data: row };
  }

  /**
   * Serve the rendered HTML directly. Returns text/html content so
   * browsers can render it inline or download it. The URL is what the
   * InMemoryReportStorage emits.
   */
  @Get("field-reports/:id/content")
  @ApiOperation({ summary: "Fetch the rendered HTML content" })
  async getContent(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
    @Res() res: Response,
  ) {
    const tenantId = getRequestTenantId(req);
    const html = await this.service.getContent(id, tenantId);
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.setHeader(
      "Content-Disposition",
      `inline; filename="report-${id}.html"`,
    );
    res.send(html);
  }
}
