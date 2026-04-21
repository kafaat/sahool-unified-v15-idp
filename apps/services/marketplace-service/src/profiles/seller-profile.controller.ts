/**
 * Seller Profile Controller
 * وحدة التحكم في ملفات البائعين
 *
 * ─────────────────────────────────────────────────────────────────────────
 * SECURITY NOTES (2026-04-21 hardening)
 * ─────────────────────────────────────────────────────────────────────────
 * 1. ALL endpoints require JwtAuthGuard. The previous version left
 *    `getAllSellers`, `getSellerProfileByUserId`, and `getSellerProfileById`
 *    unauthenticated, exposing PII (taxId, bankAccount, payoutPreferences).
 * 2. tenantId is sourced exclusively from the JWT (`req.user.tenantId`).
 *    The `x-tenant-id` header and `?tenantId=` query-string were honored
 *    previously — both were client-forgeable and have been removed.
 * 3. Ownership-scoped writes (updateSellerProfile, updateSellerStats,
 *    verifySellerProfile) now reject requests where the URL `:userId`
 *    param does not match `req.user.id` unless the caller holds the
 *    SUPER_ADMIN role (platform-level verification / stats backfill).
 */

import {
  BadRequestException,
  Body,
  Controller,
  ForbiddenException,
  Get,
  HttpCode,
  HttpStatus,
  Param,
  Patch,
  Post,
  Put,
  Query,
  Req,
  UnauthorizedException,
  UseGuards,
  ValidationPipe,
} from "@nestjs/common";
import {
  ApiBearerAuth,
  ApiOperation,
  ApiParam,
  ApiQuery,
  ApiResponse,
  ApiTags,
} from "@nestjs/swagger";
import {
  BusinessType,
  CreateSellerProfileDto,
  UpdateSellerProfileDto,
  VerifySellerDto,
} from "../dto/profiles.dto";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { ProfilesService } from "./profiles.service";

@ApiTags("Seller Profiles")
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller("profiles/sellers")
export class SellerProfileController {
  constructor(private readonly profilesService: ProfilesService) {}

  // ─── shared auth helpers ────────────────────────────────────────────────

  private requireTenantId(req: any): string {
    const tenantId = req?.user?.tenantId ?? req?.user?.tid;
    if (!tenantId) {
      throw new UnauthorizedException("tenantId missing from JWT");
    }
    return String(tenantId);
  }

  private isSuperAdmin(req: any): boolean {
    const roles: string[] = Array.isArray(req?.user?.roles)
      ? req.user.roles
      : [];
    return roles.some((r) => String(r).toLowerCase().replace(/[_-]/g, "") === "superadmin");
  }

  private assertOwnsOrSuperAdmin(req: any, targetUserId: string): void {
    const callerId = req?.user?.id;
    if (!callerId) {
      throw new UnauthorizedException("user id missing from JWT");
    }
    if (callerId === targetUserId) return;
    if (this.isSuperAdmin(req)) return;
    throw new ForbiddenException(
      "You may only operate on your own seller profile",
    );
  }

  // ─── endpoints ──────────────────────────────────────────────────────────

  /**
   * إنشاء ملف تعريف بائع جديد. The dto.userId is OVERRIDDEN with the
   * authenticated caller's id to prevent impersonation.
   */
  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: "Create a seller profile for the authenticated user" })
  @ApiResponse({ status: 201, description: "Seller profile created" })
  @ApiResponse({ status: 409, description: "Seller profile already exists" })
  async createSellerProfile(
    @Req() req: any,
    @Body(ValidationPipe) dto: CreateSellerProfileDto,
  ) {
    const tenantId = this.requireTenantId(req);
    const callerId = req?.user?.id;
    if (!callerId) {
      throw new UnauthorizedException("user id missing from JWT");
    }
    // Force userId to the authenticated caller — attackers MUST NOT be
    // able to create a profile on someone else's behalf via dto.userId.
    const safeDto: CreateSellerProfileDto = { ...dto, userId: callerId };
    return this.profilesService.createSellerProfile(safeDto, tenantId);
  }

  /**
   * جلب جميع البائعين (مع الفلترة). Tenant is taken from JWT; the query
   * string tenantId is ignored.
   */
  @Get()
  @ApiOperation({ summary: "Get all sellers in caller's tenant" })
  @ApiQuery({ name: "businessType", required: false, enum: BusinessType })
  @ApiQuery({ name: "verified", required: false, type: Boolean })
  @ApiQuery({ name: "minRating", required: false, type: Number })
  async getAllSellers(
    @Req() req: any,
    @Query("businessType") businessType?: BusinessType,
    @Query("verified") verified?: string,
    @Query("minRating") minRating?: string,
  ) {
    const tenantId = this.requireTenantId(req);
    return this.profilesService.getAllSellers({
      businessType,
      verified:
        verified === "true" ? true : verified === "false" ? false : undefined,
      // SECURITY: NEVER trust a query-string tenantId.
      tenantId,
      minRating: minRating ? parseFloat(minRating) : undefined,
      // SECURITY: isAdmin flag is set from JWT role, not from the request.
      isAdmin: this.isSuperAdmin(req),
    });
  }

  /**
   * جلب ملف تعريف المستخدم الحالي.
   * GET /profiles/sellers/me
   */
  @Get("me")
  @ApiOperation({ summary: "Get the caller's own seller profile" })
  async getMyProfile(@Req() req: any) {
    const tenantId = this.requireTenantId(req);
    const callerId = req?.user?.id;
    return this.profilesService.getSellerProfileByUserId(callerId, tenantId);
  }

  /**
   * جلب ملف تعريف البائع بواسطة معرف المستخدم — scoped by caller's tenant.
   */
  @Get("user/:userId")
  @ApiOperation({ summary: "Get seller profile by user id (tenant-scoped)" })
  @ApiParam({ name: "userId", description: "User ID" })
  async getSellerProfileByUserId(
    @Req() req: any,
    @Param("userId") userId: string,
  ) {
    const tenantId = this.requireTenantId(req);
    return this.profilesService.getSellerProfileByUserId(userId, tenantId);
  }

  /**
   * جلب ملف تعريف البائع بواسطة المعرف — scoped via id_tenantId composite.
   */
  @Get(":id")
  @ApiOperation({ summary: "Get seller profile by id (tenant-scoped)" })
  @ApiParam({ name: "id", description: "Seller profile ID" })
  async getSellerProfileById(@Req() req: any, @Param("id") id: string) {
    const tenantId = this.requireTenantId(req);
    return this.profilesService.getSellerProfileById(id, tenantId);
  }

  /**
   * تحديث ملف تعريف البائع. Caller may only update their own profile
   * unless they are SUPER_ADMIN.
   */
  @Put("user/:userId")
  @ApiOperation({ summary: "Update a seller profile (owner or super-admin)" })
  async updateSellerProfile(
    @Req() req: any,
    @Param("userId") userId: string,
    @Body(ValidationPipe) dto: UpdateSellerProfileDto,
  ) {
    const tenantId = this.requireTenantId(req);
    this.assertOwnsOrSuperAdmin(req, userId);
    return this.profilesService.updateSellerProfile(userId, dto, tenantId);
  }

  /**
   * التحقق من ملف تعريف البائع — SUPER_ADMIN / KYC officer only.
   */
  @Patch("user/:userId/verify")
  @ApiOperation({ summary: "Verify or unverify a seller (SUPER_ADMIN only)" })
  async verifySellerProfile(
    @Req() req: any,
    @Param("userId") userId: string,
    @Body(ValidationPipe) dto: VerifySellerDto,
  ) {
    const tenantId = this.requireTenantId(req);
    if (!this.isSuperAdmin(req)) {
      throw new ForbiddenException("SUPER_ADMIN role required to verify sellers");
    }
    return this.profilesService.verifySellerProfile(userId, dto.verified, tenantId);
  }

  /**
   * تحديث إحصائيات البائع. Used by server-to-server callers (order flow);
   * humans cannot hit it directly — restricted to SUPER_ADMIN or when the
   * caller is updating their own stats.
   */
  @Patch("user/:userId/stats")
  @ApiOperation({ summary: "Update seller statistics (self or SUPER_ADMIN)" })
  async updateSellerStats(
    @Req() req: any,
    @Param("userId") userId: string,
    @Body() dto: { saleAmount: number; incrementSales?: number },
  ) {
    const tenantId = this.requireTenantId(req);
    this.assertOwnsOrSuperAdmin(req, userId);
    if (typeof dto?.saleAmount !== "number") {
      throw new BadRequestException("saleAmount is required");
    }
    return this.profilesService.updateSellerStats(
      userId,
      dto.saleAmount,
      tenantId,
      dto.incrementSales,
    );
  }
}
