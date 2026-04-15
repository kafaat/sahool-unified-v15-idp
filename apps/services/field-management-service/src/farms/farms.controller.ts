/**
 * Farms Controller - REST API Endpoints
 * وحدة تحكم المزارع
 *
 * Exposes tenant-scoped CRUD + stats routes under /api/v1/farms.
 * The tenant ID is always extracted from the authenticated JWT
 * (via `req.tenantId`, set by TenantGuard) — NOT from request headers —
 * to prevent cross-tenant data leakage.
 */

import {
  Body,
  Controller,
  Delete,
  Get,
  HttpCode,
  HttpStatus,
  Param,
  ParseUUIDPipe,
  Post,
  Put,
  Query,
  Req,
  ValidationPipe,
} from "@nestjs/common";
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiParam,
  ApiQuery,
} from "@nestjs/swagger";
import { FarmsService } from "./farms.service";
import { CreateFarmDto } from "./dto/create-farm.dto";
import { UpdateFarmDto } from "./dto/update-farm.dto";
import { QueryFarmsDto } from "./dto/query-farms.dto";
import {
  assertTenantOwnership,
  getRequestTenantId,
} from "../auth/tenant.utils";

@ApiTags("Farms - المزارع")
@Controller("api/v1/farms")
export class FarmsController {
  constructor(private readonly farmsService: FarmsService) {}

  /**
   * List farms with pagination and filtering.
   */
  @Get()
  @ApiOperation({
    summary: "List farms",
    description: "جلب قائمة المزارع مع الترقيم والفلترة",
  })
  @ApiQuery({ name: "page", type: Number, required: false })
  @ApiQuery({ name: "limit", type: Number, required: false })
  @ApiQuery({ name: "status", type: String, required: false })
  @ApiQuery({ name: "region", type: String, required: false })
  @ApiQuery({ name: "search", type: String, required: false })
  @ApiResponse({ status: 200, description: "Farms retrieved successfully" })
  async findAll(
    @Req() req: any,
    @Query(new ValidationPipe({ transform: true, whitelist: true }))
    query: QueryFarmsDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const result = await this.farmsService.findAll(tenantId, query);
    return {
      success: true,
      ...result,
    };
  }

  /**
   * Get aggregate stats for the authenticated tenant.
   *
   * NOTE: Declared BEFORE `@Get(":id")` so that NestJS matches the literal
   * `stats/` prefix first (same route-ordering lesson as the Fields controller).
   */
  @Get("stats/:tenantId")
  @ApiOperation({
    summary: "Get farm statistics",
    description: "جلب إحصائيات المزارع للمستأجر",
  })
  @ApiParam({ name: "tenantId", type: String })
  @ApiResponse({ status: 200, description: "Statistics retrieved" })
  async getStats(
    @Req() req: any,
    @Param("tenantId") pathTenantId: string,
  ) {
    const tenantId = getRequestTenantId(req);
    // Reject if the path param doesn't match the authenticated tenant.
    assertTenantOwnership(pathTenantId, tenantId, "farm stats");
    const stats = await this.farmsService.getStats(tenantId);
    return {
      success: true,
      data: stats,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Get a single farm by ID.
   */
  @Get(":id")
  @ApiOperation({
    summary: "Get farm by ID",
    description: "جلب بيانات مزرعة محددة",
  })
  @ApiParam({ name: "id", type: String, format: "uuid" })
  @ApiResponse({ status: 200, description: "Farm found" })
  @ApiResponse({ status: 404, description: "Farm not found" })
  async findOne(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const farm = await this.farmsService.findById(id, tenantId);
    return {
      success: true,
      data: farm,
    };
  }

  /**
   * Create a new farm.
   */
  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: "Create a new farm",
    description: "إنشاء مزرعة جديدة",
  })
  @ApiResponse({ status: 201, description: "Farm created successfully" })
  @ApiResponse({ status: 400, description: "Invalid input data" })
  async create(
    @Req() req: any,
    @Body(new ValidationPipe({ transform: true, whitelist: true }))
    dto: CreateFarmDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const farm = await this.farmsService.create(tenantId, dto);
    return {
      success: true,
      data: farm,
      message: "تم إنشاء المزرعة بنجاح",
    };
  }

  /**
   * Update an existing farm.
   */
  @Put(":id")
  @ApiOperation({
    summary: "Update farm",
    description: "تحديث بيانات المزرعة",
  })
  @ApiParam({ name: "id", type: String, format: "uuid" })
  @ApiResponse({ status: 200, description: "Farm updated successfully" })
  @ApiResponse({ status: 404, description: "Farm not found" })
  async update(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true, whitelist: true }))
    dto: UpdateFarmDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const farm = await this.farmsService.update(id, tenantId, dto);
    return {
      success: true,
      data: farm,
      message: "تم تحديث المزرعة بنجاح",
    };
  }

  /**
   * Soft-delete a farm.
   */
  @Delete(":id")
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: "Delete farm (soft delete)",
    description: "حذف المزرعة (حذف ناعم)",
  })
  @ApiParam({ name: "id", type: String, format: "uuid" })
  @ApiResponse({ status: 200, description: "Farm deleted successfully" })
  @ApiResponse({ status: 404, description: "Farm not found" })
  async delete(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    await this.farmsService.delete(id, tenantId);
    return {
      success: true,
      message: "تم حذف المزرعة بنجاح",
    };
  }
}
