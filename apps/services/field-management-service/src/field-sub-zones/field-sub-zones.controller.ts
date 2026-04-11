/**
 * Field Sub-Zones Controller
 * REST endpoints for per-field sub-polygon management (terraced farms).
 *
 * Routes:
 *   GET    /api/v1/fields/:fieldId/sub-zones         — list
 *   POST   /api/v1/fields/:fieldId/sub-zones         — create
 *   GET    /api/v1/field-sub-zones/:id               — detail
 *   PATCH  /api/v1/field-sub-zones/:id               — partial update
 *   DELETE /api/v1/field-sub-zones/:id               — soft delete
 */

import {
  Controller,
  Get,
  Post,
  Patch,
  Delete,
  Body,
  Param,
  ParseUUIDPipe,
  ValidationPipe,
  HttpCode,
  HttpStatus,
  Req,
  UseInterceptors,
} from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse, ApiParam } from "@nestjs/swagger";
import { FieldSubZonesService } from "./field-sub-zones.service";
import {
  CreateFieldSubZoneDto,
  UpdateFieldSubZoneDto,
} from "./dto/field-sub-zone.dto";
import { getRequestTenantId } from "../auth/tenant.utils";
import { IdempotencyInterceptor } from "../idempotency/idempotency.interceptor";

@ApiTags("Field Sub-Zones - المناطق الفرعية للحقل")
@Controller("api/v1")
export class FieldSubZonesController {
  constructor(private readonly service: FieldSubZonesService) {}

  /**
   * List all sub-zones for a field, ordered by display_order then created_at.
   */
  @Get("fields/:fieldId/sub-zones")
  @ApiOperation({
    summary: "List sub-zones for a field",
    description: "قائمة المناطق الفرعية للحقل",
  })
  @ApiParam({ name: "fieldId", description: "Field UUID" })
  async listByField(
    @Req() req: any,
    @Param("fieldId", ParseUUIDPipe) fieldId: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const items = await this.service.listByField(fieldId, tenantId);
    return { success: true, items, total: items.length };
  }

  /**
   * Create a new sub-zone. Honors Idempotency-Key so clients can safely
   * retry after network errors.
   */
  @Post("fields/:fieldId/sub-zones")
  @HttpCode(HttpStatus.CREATED)
  @UseInterceptors(IdempotencyInterceptor)
  @ApiOperation({
    summary: "Create a new sub-zone",
    description: "إنشاء منطقة فرعية جديدة للحقل",
  })
  @ApiResponse({ status: 201, description: "Sub-zone created" })
  async create(
    @Req() req: any,
    @Param("fieldId", ParseUUIDPipe) fieldId: string,
    @Body(new ValidationPipe({ transform: true, whitelist: true }))
    dto: CreateFieldSubZoneDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const userId: string | undefined = req.user?.sub ?? req.user?.id;
    const row = await this.service.create(fieldId, tenantId, dto, userId);
    return {
      success: true,
      data: row,
      message: "تم إنشاء المنطقة الفرعية بنجاح",
    };
  }

  @Get("field-sub-zones/:id")
  @ApiOperation({ summary: "Get a sub-zone by id" })
  async getById(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const row = await this.service.getById(id, tenantId);
    return { success: true, data: row };
  }

  @Patch("field-sub-zones/:id")
  @ApiOperation({ summary: "Update a sub-zone" })
  async update(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true, whitelist: true }))
    dto: UpdateFieldSubZoneDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const row = await this.service.update(id, tenantId, dto);
    return { success: true, data: row };
  }

  @Delete("field-sub-zones/:id")
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: "Soft-delete a sub-zone" })
  async remove(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const userId: string | undefined = req.user?.sub ?? req.user?.id;
    await this.service.remove(id, tenantId, userId);
  }
}
