/**
 * Field Operations Controller
 * REST endpoints for the per-field operation log.
 *
 * Routes:
 *   GET    /api/v1/fields/:fieldId/operations             — list ops
 *   POST   /api/v1/fields/:fieldId/operations             — record op
 *   GET    /api/v1/field-operations/:id                   — detail
 *   PATCH  /api/v1/field-operations/:id                   — update
 *   DELETE /api/v1/field-operations/:id                   — hard delete
 *   GET    /api/v1/field-operations                        — tenant query
 *   GET    /api/v1/crop-seasons/:cropSeasonId/rollup      — per-season totals
 */

import {
  Controller,
  Get,
  Post,
  Patch,
  Delete,
  Body,
  Param,
  Query,
  ParseUUIDPipe,
  ValidationPipe,
  HttpCode,
  HttpStatus,
  Req,
} from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse, ApiParam } from "@nestjs/swagger";
import { FieldOperationsService } from "./field-operations.service";
import {
  CreateFieldOperationDto,
  UpdateFieldOperationDto,
  QueryFieldOperationsDto,
} from "./dto/field-operation.dto";
import { getRequestTenantId } from "../auth/tenant.utils";

@ApiTags("Field Operations - عمليات الحقل")
@Controller("api/v1")
export class FieldOperationsController {
  constructor(private readonly service: FieldOperationsService) {}

  /**
   * Tenant-wide query.
   */
  @Get("field-operations")
  @ApiOperation({ summary: "List field operations" })
  async listAll(
    @Req() req: any,
    @Query(new ValidationPipe({ transform: true, whitelist: true }))
    q: QueryFieldOperationsDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const result = await this.service.list(tenantId, q);
    return { success: true, ...result };
  }

  /**
   * Per-field list (convenience URL).
   */
  @Get("fields/:fieldId/operations")
  @ApiOperation({ summary: "List operations for a single field" })
  @ApiParam({ name: "fieldId", description: "Field UUID" })
  async listByField(
    @Req() req: any,
    @Param("fieldId", ParseUUIDPipe) fieldId: string,
    @Query(new ValidationPipe({ transform: true, whitelist: true }))
    q: QueryFieldOperationsDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const result = await this.service.list(tenantId, { ...q, fieldId });
    return { success: true, ...result };
  }

  /**
   * Record a new operation against a field.
   */
  @Post("fields/:fieldId/operations")
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: "Record a new field operation" })
  @ApiResponse({ status: 201, description: "Operation recorded" })
  async create(
    @Req() req: any,
    @Param("fieldId", ParseUUIDPipe) fieldId: string,
    @Body(new ValidationPipe({ transform: true, whitelist: true }))
    dto: CreateFieldOperationDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const userId: string | undefined = req.user?.sub ?? req.user?.id;
    const row = await this.service.create(fieldId, tenantId, dto, userId);
    return {
      success: true,
      data: row,
      message: "تم تسجيل العملية بنجاح",
    };
  }

  /**
   * Per-season rollup: total hours + cost + breakdown by operation type.
   * Used by yield-prediction + advisory-service + the web timeline.
   */
  @Get("crop-seasons/:cropSeasonId/rollup")
  @ApiOperation({ summary: "Rollup operations for a crop season" })
  async rollupForSeason(
    @Req() req: any,
    @Param("cropSeasonId", ParseUUIDPipe) cropSeasonId: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const data = await this.service.rollupForCropSeason(cropSeasonId, tenantId);
    return { success: true, data };
  }

  @Get("field-operations/:id")
  @ApiOperation({ summary: "Get field operation by id" })
  async getById(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const row = await this.service.getById(id, tenantId);
    return { success: true, data: row };
  }

  @Patch("field-operations/:id")
  @ApiOperation({ summary: "Update a field operation" })
  async update(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true, whitelist: true }))
    dto: UpdateFieldOperationDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const row = await this.service.update(id, tenantId, dto);
    return { success: true, data: row };
  }

  @Delete("field-operations/:id")
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: "Delete a field operation" })
  async remove(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    await this.service.remove(id, tenantId);
  }
}
