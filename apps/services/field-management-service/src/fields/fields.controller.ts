/**
 * Fields Controller - REST API Endpoints
 *
 * Features:
 * - CRUD operations with validation
 * - ETag-based optimistic locking
 * - Swagger documentation
 * - Rate limiting
 */

import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  Headers,
  HttpCode,
  HttpStatus,
  ParseUUIDPipe,
  ValidationPipe,
  Req,
} from "@nestjs/common";
import { Throttle } from "@nestjs/throttler";
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiParam,
  ApiQuery,
  ApiHeader,
} from "@nestjs/swagger";
import { FieldsService } from "./fields.service";
import { KpiSnapshotService, CreateKpiSnapshotDto } from "./kpi-snapshot.service";
import {
  CreateFieldDto,
  UpdateFieldDto,
  QueryFieldsDto,
  NearbyFieldsDto,
  UpdateBoundaryDto,
  RollbackBoundaryDto,
  FieldResponseDto,
  PaginatedFieldsResponseDto,
} from "./dto/field.dto";
import { getRequestTenantId, assertTenantOwnership } from "../auth/tenant.utils";

@ApiTags("Fields - الحقول")
@Controller("api/v1/fields")
export class FieldsController {
  constructor(
    private readonly fieldsService: FieldsService,
    private readonly kpiSnapshotService: KpiSnapshotService,
  ) {}

  /**
   * Create a new field
   */
  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: "Create a new field",
    description: "إنشاء حقل جديد مع الحدود الجغرافية",
  })
  @ApiResponse({
    status: 201,
    description: "Field created successfully",
    type: FieldResponseDto,
  })
  @ApiResponse({ status: 400, description: "Invalid input data" })
  async create(
    @Req() req: any,
    @Body(new ValidationPipe({ transform: true })) dto: CreateFieldDto,
  ) {
    const tenantId = getRequestTenantId(req);
    // Override DTO tenantId with authenticated tenant to prevent spoofing
    dto.tenantId = tenantId;
    const field = await this.fieldsService.create(dto);
    return {
      success: true,
      data: field,
      etag: field.etag,
      message: "حقل جديد تم إنشاؤه بنجاح",
    };
  }

  /**
   * Get all fields with pagination
   */
  @Get()
  @ApiOperation({
    summary: "List all fields",
    description: "جلب قائمة الحقول مع الترقيم والفلترة",
  })
  @ApiResponse({
    status: 200,
    description: "Fields retrieved successfully",
    type: PaginatedFieldsResponseDto,
  })
  async findAll(
    @Req() req: any,
    @Query(new ValidationPipe({ transform: true })) query: QueryFieldsDto,
  ) {
    const tenantId = getRequestTenantId(req);
    // Always scope to authenticated tenant
    query.tenantId = tenantId;
    const result = await this.fieldsService.findAll(query);
    return {
      success: true,
      ...result,
    };
  }

  /**
   * Get nearby fields
   */
  @Get("nearby")
  @ApiOperation({
    summary: "Find nearby fields",
    description: "البحث عن الحقول القريبة باستخدام PostGIS",
  })
  @ApiQuery({ name: "lat", type: Number, required: true })
  @ApiQuery({ name: "lng", type: Number, required: true })
  @ApiQuery({ name: "radius", type: Number, required: false })
  @ApiResponse({ status: 200, description: "Nearby fields found" })
  async findNearby(
    @Req() req: any,
    @Query(new ValidationPipe({ transform: true })) query: NearbyFieldsDto,
  ) {
    const tenantId = getRequestTenantId(req);
    // Scope nearby search to authenticated tenant
    query.tenantId = tenantId;
    const fields = await this.fieldsService.findNearby(query);
    return {
      success: true,
      data: fields,
      query: { lat: query.lat, lng: query.lng, radius: query.radius },
    };
  }

  /**
   * Get field statistics for tenant
   *
   * NOTE: This route MUST be declared before `@Get(":id")` so that NestJS
   * matches the literal `stats/` prefix before the UUID route. Otherwise
   * `ParseUUIDPipe` on `:id` will reject the literal "stats" segment and
   * return HTTP 400 on every stats request.
   */
  @Get("stats/:tenantId")
  @Throttle({ default: { limit: 30, ttl: 60000 } })
  @ApiOperation({
    summary: "Get field statistics",
    description: "جلب إحصائيات الحقول للمستأجر",
  })
  @ApiParam({ name: "tenantId", type: String })
  @ApiResponse({ status: 200, description: "Statistics retrieved" })
  async getStats(
    @Req() req: any,
    @Param("tenantId") pathTenantId: string,
  ) {
    const tenantId = getRequestTenantId(req);
    // Reject if the path param doesn't match the authenticated tenant
    assertTenantOwnership(pathTenantId, tenantId, "stats");
    const stats = await this.fieldsService.getStats(tenantId);
    return {
      success: true,
      data: stats,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Get field by ID
   */
  @Get(":id")
  @ApiOperation({
    summary: "Get field by ID",
    description: "جلب بيانات حقل محدد",
  })
  @ApiParam({ name: "id", type: String, format: "uuid" })
  @ApiResponse({
    status: 200,
    description: "Field found",
    type: FieldResponseDto,
  })
  @ApiResponse({ status: 404, description: "Field not found" })
  async findOne(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const field = await this.fieldsService.findById(id, tenantId);
    return {
      success: true,
      data: field,
      etag: field.etag,
    };
  }

  /**
   * Update field with optimistic locking
   */
  @Put(":id")
  @ApiOperation({
    summary: "Update field",
    description: "تحديث بيانات الحقل مع دعم القفل المتفائل",
  })
  @ApiParam({ name: "id", type: String, format: "uuid" })
  @ApiHeader({
    name: "If-Match",
    description: "ETag for optimistic locking",
    required: false,
  })
  @ApiResponse({
    status: 200,
    description: "Field updated successfully",
    type: FieldResponseDto,
  })
  @ApiResponse({ status: 404, description: "Field not found" })
  @ApiResponse({ status: 409, description: "Conflict - field was modified" })
  async update(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true })) dto: UpdateFieldDto,
    @Headers("if-match") ifMatch?: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const field = await this.fieldsService.update(id, dto, tenantId, ifMatch);
    return {
      success: true,
      data: field,
      etag: field.etag,
      message: "تم تحديث الحقل بنجاح",
    };
  }

  /**
   * Delete field (soft delete)
   */
  @Delete(":id")
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: "Delete field",
    description: "حذف الحقل (حذف ناعم)",
  })
  @ApiParam({ name: "id", type: String, format: "uuid" })
  @ApiResponse({ status: 200, description: "Field deleted successfully" })
  @ApiResponse({ status: 404, description: "Field not found" })
  async delete(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    await this.fieldsService.delete(id, tenantId);
    return {
      success: true,
      message: "تم حذف الحقل بنجاح",
    };
  }

  /**
   * Get boundary history
   */
  @Get(":id/boundary-history")
  @ApiOperation({
    summary: "Get boundary change history",
    description: "جلب سجل تغييرات حدود الحقل",
  })
  @ApiParam({ name: "id", type: String, format: "uuid" })
  @ApiQuery({ name: "limit", type: Number, required: false })
  @ApiResponse({ status: 200, description: "Boundary history retrieved" })
  async getBoundaryHistory(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
    @Query("limit") limit?: number,
  ) {
    const tenantId = getRequestTenantId(req);
    const history = await this.fieldsService.getBoundaryHistory(id, tenantId, limit);
    return {
      success: true,
      data: history,
      count: history.length,
    };
  }

  /**
   * Update field boundary
   */
  @Put(":id/boundary")
  @ApiOperation({
    summary: "Update field boundary",
    description: "تحديث حدود الحقل مع تتبع التاريخ",
  })
  @ApiParam({ name: "id", type: String, format: "uuid" })
  @ApiResponse({ status: 200, description: "Boundary updated successfully" })
  @ApiResponse({ status: 404, description: "Field not found" })
  async updateBoundary(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true })) dto: UpdateBoundaryDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const field = await this.fieldsService.updateBoundary(id, dto, tenantId);
    return {
      success: true,
      data: field,
      etag: field.etag,
      message: "تم تحديث حدود الحقل بنجاح",
    };
  }

  /**
   * Rollback boundary to previous version
   */
  @Post(":id/boundary-history/rollback")
  @ApiOperation({
    summary: "Rollback boundary to previous version",
    description: "استعادة حدود الحقل من نسخة سابقة",
  })
  @ApiParam({ name: "id", type: String, format: "uuid" })
  @ApiResponse({ status: 200, description: "Boundary rollback successful" })
  @ApiResponse({ status: 404, description: "Field or history entry not found" })
  async rollbackBoundary(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true })) dto: RollbackBoundaryDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const field = await this.fieldsService.rollbackBoundary(id, dto, tenantId);
    return {
      success: true,
      data: field,
      etag: field.etag,
      message: "تم استرجاع الحدود السابقة بنجاح",
    };
  }

  /**
   * Get latest KPI snapshot for a field
   * جلب أحدث لقطة KPI للحقل
   */
  @Get(":id/kpi-snapshot")
  @ApiOperation({
    summary: "Get latest KPI snapshot",
    description: "جلب أحدث لقطة KPI من Sentinel Hub + OpenWeather",
  })
  @ApiParam({ name: "id", type: String, format: "uuid" })
  @ApiResponse({ status: 200, description: "KPI snapshot retrieved" })
  @ApiResponse({ status: 404, description: "Field not found" })
  async getKpiSnapshot(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const snapshot = await this.kpiSnapshotService.getLatest(id, tenantId);
    return {
      success: true,
      data: snapshot,
    };
  }

  /**
   * Save a new KPI snapshot for a field
   * حفظ لقطة KPI جديدة للحقل
   */
  @Post(":id/kpi-snapshot")
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: "Save KPI snapshot",
    description: "حفظ لقطة KPI جديدة وتحديث صحة الحقل",
  })
  @ApiParam({ name: "id", type: String, format: "uuid" })
  @ApiResponse({ status: 201, description: "KPI snapshot saved" })
  @ApiResponse({ status: 404, description: "Field not found" })
  async saveKpiSnapshot(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true })) dto: CreateKpiSnapshotDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const snapshot = await this.kpiSnapshotService.save(id, tenantId, dto);
    return {
      success: true,
      data: snapshot,
      message: "تم حفظ لقطة KPI بنجاح",
    };
  }

}
