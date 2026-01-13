/**
 * Seller Profile Controller
 * وحدة التحكم في ملفات البائعين
 */

import {
  Controller,
  Get,
  Post,
  Put,
  Patch,
  Body,
  Param,
  Query,
  HttpCode,
  HttpStatus,
  UseGuards,
  ValidationPipe,
} from "@nestjs/common";
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiParam,
  ApiQuery,
  ApiBearerAuth,
} from "@nestjs/swagger";
import { ProfilesService } from "./profiles.service";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import {
  CreateSellerProfileDto,
  UpdateSellerProfileDto,
  VerifySellerDto,
  BusinessType,
} from "../dto/profiles.dto";

@ApiTags("Seller Profiles")
@Controller("profiles/sellers")
export class SellerProfileController {
  constructor(private readonly profilesService: ProfilesService) {}

  /**
   * إنشاء ملف تعريف بائع جديد
   * POST /api/v1/profiles/sellers
   */
  @Post()
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: "Create a new seller profile" })
  @ApiResponse({
    status: 201,
    description: "Seller profile created successfully",
  })
  @ApiResponse({ status: 409, description: "Seller profile already exists" })
  async createSellerProfile(@Body(ValidationPipe) dto: CreateSellerProfileDto) {
    return this.profilesService.createSellerProfile(dto);
  }

  /**
   * جلب جميع البائعين
   * GET /api/v1/profiles/sellers
   */
  @Get()
  @ApiOperation({ summary: "Get all sellers with optional filters" })
  @ApiQuery({
    name: "businessType",
    required: false,
    enum: BusinessType,
    description: "Filter by business type",
  })
  @ApiQuery({
    name: "verified",
    required: false,
    type: Boolean,
    description: "Filter by verification status",
  })
  @ApiQuery({
    name: "tenantId",
    required: false,
    type: String,
    description: "Filter by tenant ID",
  })
  @ApiQuery({
    name: "minRating",
    required: false,
    type: Number,
    description: "Filter by minimum rating",
  })
  @ApiResponse({ status: 200, description: "List of sellers" })
  async getAllSellers(
    @Query("businessType") businessType?: BusinessType,
    @Query("verified") verified?: string,
    @Query("tenantId") tenantId?: string,
    @Query("minRating") minRating?: string,
  ) {
    return this.profilesService.getAllSellers({
      businessType,
      verified:
        verified === "true" ? true : verified === "false" ? false : undefined,
      tenantId,
      minRating: minRating ? parseFloat(minRating) : undefined,
    });
  }

  /**
   * جلب ملف تعريف البائع بواسطة معرف المستخدم
   * GET /api/v1/profiles/sellers/user/:userId
   */
  @Get("user/:userId")
  @ApiOperation({ summary: "Get seller profile by user ID" })
  @ApiParam({ name: "userId", description: "User ID" })
  @ApiResponse({ status: 200, description: "Seller profile found" })
  @ApiResponse({ status: 404, description: "Seller profile not found" })
  async getSellerProfileByUserId(@Param("userId") userId: string) {
    return this.profilesService.getSellerProfileByUserId(userId);
  }

  /**
   * جلب ملف تعريف البائع بواسطة المعرف
   * GET /api/v1/profiles/sellers/:id
   */
  @Get(":id")
  @ApiOperation({ summary: "Get seller profile by ID" })
  @ApiParam({ name: "id", description: "Seller profile ID" })
  @ApiResponse({ status: 200, description: "Seller profile found" })
  @ApiResponse({ status: 404, description: "Seller profile not found" })
  async getSellerProfileById(@Param("id") id: string) {
    return this.profilesService.getSellerProfileById(id);
  }

  /**
   * تحديث ملف تعريف البائع
   * PUT /api/v1/profiles/sellers/user/:userId
   */
  @Put("user/:userId")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: "Update seller profile" })
  @ApiParam({ name: "userId", description: "User ID" })
  @ApiResponse({ status: 200, description: "Seller profile updated" })
  @ApiResponse({ status: 404, description: "Seller profile not found" })
  async updateSellerProfile(
    @Param("userId") userId: string,
    @Body(ValidationPipe) dto: UpdateSellerProfileDto,
  ) {
    return this.profilesService.updateSellerProfile(userId, dto);
  }

  /**
   * التحقق من ملف تعريف البائع
   * PATCH /api/v1/profiles/sellers/user/:userId/verify
   */
  @Patch("user/:userId/verify")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: "Verify or unverify seller profile" })
  @ApiParam({ name: "userId", description: "User ID" })
  @ApiResponse({
    status: 200,
    description: "Seller verification status updated",
  })
  @ApiResponse({ status: 404, description: "Seller profile not found" })
  async verifySellerProfile(
    @Param("userId") userId: string,
    @Body(ValidationPipe) dto: VerifySellerDto,
  ) {
    return this.profilesService.verifySellerProfile(userId, dto.verified);
  }

  /**
   * تحديث إحصائيات البائع (للاستخدام الداخلي)
   * PATCH /api/v1/profiles/sellers/user/:userId/stats
   */
  @Patch("user/:userId/stats")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: "Update seller statistics (internal use)" })
  @ApiParam({ name: "userId", description: "User ID" })
  @ApiResponse({ status: 200, description: "Seller stats updated" })
  async updateSellerStats(
    @Param("userId") userId: string,
    @Body() dto: { saleAmount: number; incrementSales?: number },
  ) {
    return this.profilesService.updateSellerStats(
      userId,
      dto.saleAmount,
      dto.incrementSales,
    );
  }
}
