/**
 * Buyer Profile Controller
 * وحدة التحكم في ملفات المشترين
 *
 * Security hardening (2026-04-21): same model as SellerProfileController.
 * All endpoints require JwtAuthGuard, tenantId comes from the JWT only,
 * writes check ownership via JWT `sub` against the URL `:userId`.
 */

import {
  BadRequestException,
  Body,
  Controller,
  Delete,
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
  AddShippingAddressDto,
  CreateBuyerProfileDto,
  UpdateBuyerProfileDto,
  UpdateLoyaltyPointsDto,
} from "../dto/profiles.dto";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { ProfilesService } from "./profiles.service";

@ApiTags("Buyer Profiles")
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller("profiles/buyers")
export class BuyerProfileController {
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
    return roles.some(
      (r) => String(r).toLowerCase().replace(/[_-]/g, "") === "superadmin",
    );
  }

  private assertOwnsOrSuperAdmin(req: any, targetUserId: string): void {
    const callerId = req?.user?.id;
    if (!callerId) {
      throw new UnauthorizedException("user id missing from JWT");
    }
    if (callerId === targetUserId) return;
    if (this.isSuperAdmin(req)) return;
    throw new ForbiddenException(
      "You may only operate on your own buyer profile",
    );
  }

  // ─── endpoints ──────────────────────────────────────────────────────────

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: "Create a buyer profile for the authenticated user" })
  async createBuyerProfile(
    @Req() req: any,
    @Body(ValidationPipe) dto: CreateBuyerProfileDto,
  ) {
    const tenantId = this.requireTenantId(req);
    const callerId = req?.user?.id;
    if (!callerId) {
      throw new UnauthorizedException("user id missing from JWT");
    }
    // Force userId to the authenticated caller.
    const safeDto: CreateBuyerProfileDto = { ...dto, userId: callerId };
    return this.profilesService.createBuyerProfile(safeDto, tenantId);
  }

  @Get()
  @ApiOperation({ summary: "Get all buyers in caller's tenant" })
  @ApiQuery({ name: "minPurchases", required: false, type: Number })
  @ApiQuery({ name: "minLoyaltyPoints", required: false, type: Number })
  async getAllBuyers(
    @Req() req: any,
    @Query("minPurchases") minPurchases?: string,
    @Query("minLoyaltyPoints") minLoyaltyPoints?: string,
  ) {
    const tenantId = this.requireTenantId(req);
    return this.profilesService.getAllBuyers({
      // SECURITY: never from query-string / header.
      tenantId,
      minPurchases: minPurchases ? parseInt(minPurchases, 10) : undefined,
      minLoyaltyPoints: minLoyaltyPoints
        ? parseInt(minLoyaltyPoints, 10)
        : undefined,
      isAdmin: this.isSuperAdmin(req),
    });
  }

  @Get("me")
  @ApiOperation({ summary: "Get the caller's own buyer profile" })
  async getMyProfile(@Req() req: any) {
    const tenantId = this.requireTenantId(req);
    const callerId = req?.user?.id;
    return this.profilesService.getBuyerProfileByUserId(callerId, tenantId);
  }

  @Get("user/:userId")
  @ApiOperation({ summary: "Get buyer profile by user ID (tenant-scoped)" })
  async getBuyerProfileByUserId(
    @Req() req: any,
    @Param("userId") userId: string,
  ) {
    const tenantId = this.requireTenantId(req);
    return this.profilesService.getBuyerProfileByUserId(userId, tenantId);
  }

  @Get(":id")
  @ApiOperation({ summary: "Get buyer profile by ID (tenant-scoped)" })
  async getBuyerProfileById(@Req() req: any, @Param("id") id: string) {
    const tenantId = this.requireTenantId(req);
    return this.profilesService.getBuyerProfileById(id, tenantId);
  }

  @Put("user/:userId")
  @ApiOperation({ summary: "Update a buyer profile (owner or super-admin)" })
  async updateBuyerProfile(
    @Req() req: any,
    @Param("userId") userId: string,
    @Body(ValidationPipe) dto: UpdateBuyerProfileDto,
  ) {
    const tenantId = this.requireTenantId(req);
    this.assertOwnsOrSuperAdmin(req, userId);
    return this.profilesService.updateBuyerProfile(userId, dto, tenantId);
  }

  @Post("user/:userId/addresses")
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: "Add shipping address (owner only)" })
  async addShippingAddress(
    @Req() req: any,
    @Param("userId") userId: string,
    @Body(ValidationPipe) dto: AddShippingAddressDto,
  ) {
    const tenantId = this.requireTenantId(req);
    this.assertOwnsOrSuperAdmin(req, userId);
    return this.profilesService.addShippingAddress(userId, dto, tenantId);
  }

  @Delete("user/:userId/addresses/:label")
  @ApiOperation({ summary: "Remove shipping address (owner only)" })
  async removeShippingAddress(
    @Req() req: any,
    @Param("userId") userId: string,
    @Param("label") label: string,
  ) {
    const tenantId = this.requireTenantId(req);
    this.assertOwnsOrSuperAdmin(req, userId);
    return this.profilesService.removeShippingAddress(userId, label, tenantId);
  }

  @Patch("user/:userId/loyalty-points")
  @ApiOperation({ summary: "Update loyalty points (self or SUPER_ADMIN)" })
  async updateLoyaltyPoints(
    @Req() req: any,
    @Param("userId") userId: string,
    @Body(ValidationPipe) dto: UpdateLoyaltyPointsDto,
  ) {
    const tenantId = this.requireTenantId(req);
    // Crediting loyalty points is privileged — restrict to SUPER_ADMIN to
    // prevent self-issue abuse. Owner-initiated negative adjustments (e.g.
    // redemption) also go through SUPER_ADMIN-mediated flows in practice.
    if (!this.isSuperAdmin(req)) {
      throw new ForbiddenException(
        "SUPER_ADMIN role required to mutate loyalty points",
      );
    }
    return this.profilesService.updateLoyaltyPoints(userId, dto, tenantId);
  }

  @Patch("user/:userId/stats")
  @ApiOperation({ summary: "Update buyer statistics (self or SUPER_ADMIN)" })
  async updateBuyerStats(
    @Req() req: any,
    @Param("userId") userId: string,
    @Body() dto: { purchaseAmount: number; incrementPurchases?: number },
  ) {
    const tenantId = this.requireTenantId(req);
    this.assertOwnsOrSuperAdmin(req, userId);
    if (typeof dto?.purchaseAmount !== "number") {
      throw new BadRequestException("purchaseAmount is required");
    }
    return this.profilesService.updateBuyerStats(
      userId,
      dto.purchaseAmount,
      tenantId,
      dto.incrementPurchases,
    );
  }
}
