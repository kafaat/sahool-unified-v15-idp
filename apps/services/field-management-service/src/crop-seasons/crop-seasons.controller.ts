/**
 * Crop Seasons Controller
 * REST endpoints for per-field crop rotation archive.
 *
 * Routes:
 *   GET    /api/v1/fields/:fieldId/crop-seasons        — list seasons
 *   POST   /api/v1/fields/:fieldId/crop-seasons        — start new season
 *   GET    /api/v1/crop-seasons/:id                    — detail
 *   PATCH  /api/v1/crop-seasons/:id                    — partial update
 *   POST   /api/v1/crop-seasons/:id/end                — close the season
 *   DELETE /api/v1/crop-seasons/:id                    — hard delete
 *   GET    /api/v1/crop-seasons                         — tenant-wide query
 *
 * Tenant isolation: `req.tenantId` is injected by TenantGuard (JWT tid claim).
 * The service layer uses it for every read/write; the client CANNOT supply
 * a body-level tenantId (the DTOs do not expose one).
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
  UseInterceptors,
} from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse, ApiParam } from "@nestjs/swagger";
import { CropSeasonsService } from "./crop-seasons.service";
import {
  CreateCropSeasonDto,
  UpdateCropSeasonDto,
  EndCropSeasonDto,
  QueryCropSeasonsDto,
} from "./dto/crop-season.dto";
import { getRequestTenantId } from "../auth/tenant.utils";
import { IdempotencyInterceptor } from "../idempotency/idempotency.interceptor";

@ApiTags("Crop Seasons - مواسم المحاصيل")
@Controller("api/v1")
export class CropSeasonsController {
  constructor(private readonly service: CropSeasonsService) {}

  /**
   * Tenant-wide query (with fieldId filter) — used by dashboards that
   * show "all active seasons" across the tenant's fields.
   */
  @Get("crop-seasons")
  @ApiOperation({
    summary: "List crop seasons",
    description: "قائمة مواسم المحاصيل للمستأجر الحالي",
  })
  @ApiResponse({ status: 200, description: "List of crop seasons" })
  async listAll(
    @Req() req: any,
    @Query(new ValidationPipe({ transform: true, whitelist: true }))
    q: QueryCropSeasonsDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const result = await this.service.list(tenantId, q);
    return { success: true, ...result };
  }

  /**
   * List crop seasons for a single field (convenience — same as
   * /crop-seasons?fieldId=... but with a nicer URL).
   */
  @Get("fields/:fieldId/crop-seasons")
  @ApiOperation({
    summary: "List crop seasons for a field",
    description: "قائمة مواسم محصول لحقل معين",
  })
  @ApiParam({ name: "fieldId", description: "Field UUID" })
  async listByField(
    @Req() req: any,
    @Param("fieldId", ParseUUIDPipe) fieldId: string,
    @Query(new ValidationPipe({ transform: true, whitelist: true }))
    q: QueryCropSeasonsDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const result = await this.service.list(tenantId, { ...q, fieldId });
    return { success: true, ...result };
  }

  /**
   * Start a new crop season on a field. Automatically closes the
   * previously active season (if any) inside the same transaction.
   */
  @Post("fields/:fieldId/crop-seasons")
  @HttpCode(HttpStatus.CREATED)
  @UseInterceptors(IdempotencyInterceptor)
  @ApiOperation({
    summary: "Start a new crop season",
    description: "بدء موسم محصولي جديد على الحقل",
  })
  @ApiResponse({ status: 201, description: "Crop season created" })
  async create(
    @Req() req: any,
    @Param("fieldId", ParseUUIDPipe) fieldId: string,
    @Body(new ValidationPipe({ transform: true, whitelist: true }))
    dto: CreateCropSeasonDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const userId: string | undefined = req.user?.sub ?? req.user?.id;
    const row = await this.service.create(fieldId, tenantId, dto, userId);
    return {
      success: true,
      data: row,
      message: "تم بدء الموسم المحصولي بنجاح",
    };
  }

  /**
   * Fetch a crop season by id (tenant-scoped).
   */
  @Get("crop-seasons/:id")
  @ApiOperation({ summary: "Get a crop season by id" })
  async getById(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const row = await this.service.getById(id, tenantId);
    return { success: true, data: row };
  }

  /**
   * Partial update.
   */
  @Patch("crop-seasons/:id")
  @ApiOperation({ summary: "Update a crop season" })
  async update(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true, whitelist: true }))
    dto: UpdateCropSeasonDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const row = await this.service.update(id, tenantId, dto);
    return { success: true, data: row };
  }

  /**
   * Close the season (soft - row stays for history).
   */
  @Post("crop-seasons/:id/end")
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: "End an active crop season",
    description: "إنهاء الموسم الحالي (يحفظ البيانات للتاريخ)",
  })
  async end(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true, whitelist: true }))
    dto: EndCropSeasonDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const row = await this.service.end(id, tenantId, dto);
    return { success: true, data: row };
  }

  /**
   * Hard delete (rare).
   */
  @Delete("crop-seasons/:id")
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: "Soft-delete a crop season (audit-safe)" })
  async remove(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const userId: string | undefined = req.user?.sub ?? req.user?.id;
    await this.service.remove(id, tenantId, userId);
  }
}
