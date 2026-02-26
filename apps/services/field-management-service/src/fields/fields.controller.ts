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

@ApiTags("Fields - الحقول")
@Controller("api/v1/fields")
export class FieldsController {
  constructor(private readonly fieldsService: FieldsService) {}

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
    @Body(new ValidationPipe({ transform: true })) dto: CreateFieldDto,
  ) {
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
    @Query(new ValidationPipe({ transform: true })) query: QueryFieldsDto,
  ) {
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
    @Query(new ValidationPipe({ transform: true })) query: NearbyFieldsDto,
  ) {
    const fields = await this.fieldsService.findNearby(query);
    return {
      success: true,
      data: fields,
      query: { lat: query.lat, lng: query.lng, radius: query.radius },
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
  async findOne(@Param("id", ParseUUIDPipe) id: string) {
    const field = await this.fieldsService.findById(id);
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
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true })) dto: UpdateFieldDto,
    @Headers("if-match") ifMatch?: string,
  ) {
    const field = await this.fieldsService.update(id, dto, ifMatch);
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
  async delete(@Param("id", ParseUUIDPipe) id: string) {
    await this.fieldsService.delete(id);
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
    @Param("id", ParseUUIDPipe) id: string,
    @Query("limit") limit?: number,
  ) {
    const history = await this.fieldsService.getBoundaryHistory(id, limit);
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
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true })) dto: UpdateBoundaryDto,
  ) {
    const field = await this.fieldsService.updateBoundary(id, dto);
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
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true })) dto: RollbackBoundaryDto,
  ) {
    const field = await this.fieldsService.rollbackBoundary(id, dto);
    return {
      success: true,
      data: field,
      etag: field.etag,
      message: "تم استرجاع الحدود السابقة بنجاح",
    };
  }

  /**
   * Get field statistics for tenant
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
    @Param("tenantId") paramTenantId: string,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'] || paramTenantId;
    const stats = await this.fieldsService.getStats(tenantId);
    return {
      success: true,
      data: stats,
      timestamp: new Date().toISOString(),
    };
  }
}
