/**
 * Buyer Profile Controller
 * وحدة التحكم في ملفات المشترين
 */

import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Patch,
  Body,
  Param,
  Query,
  HttpCode,
  HttpStatus,
  UseGuards,
  ValidationPipe,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiParam,
  ApiQuery,
  ApiBearerAuth,
} from '@nestjs/swagger';
import { ProfilesService } from './profiles.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import {
  CreateBuyerProfileDto,
  UpdateBuyerProfileDto,
  AddShippingAddressDto,
  UpdateLoyaltyPointsDto,
} from '../dto/profiles.dto';

@ApiTags('Buyer Profiles')
@Controller('profiles/buyers')
export class BuyerProfileController {
  constructor(private readonly profilesService: ProfilesService) {}

  /**
   * إنشاء ملف تعريف مشتري جديد
   * POST /api/v1/profiles/buyers
   */
  @Post()
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Create a new buyer profile' })
  @ApiResponse({
    status: 201,
    description: 'Buyer profile created successfully',
  })
  @ApiResponse({ status: 409, description: 'Buyer profile already exists' })
  async createBuyerProfile(@Body(ValidationPipe) dto: CreateBuyerProfileDto) {
    return this.profilesService.createBuyerProfile(dto);
  }

  /**
   * جلب جميع المشترين
   * GET /api/v1/profiles/buyers
   */
  @Get()
  @ApiOperation({ summary: 'Get all buyers with optional filters' })
  @ApiQuery({
    name: 'tenantId',
    required: false,
    type: String,
    description: 'Filter by tenant ID',
  })
  @ApiQuery({
    name: 'minPurchases',
    required: false,
    type: Number,
    description: 'Filter by minimum purchases',
  })
  @ApiQuery({
    name: 'minLoyaltyPoints',
    required: false,
    type: Number,
    description: 'Filter by minimum loyalty points',
  })
  @ApiResponse({ status: 200, description: 'List of buyers' })
  async getAllBuyers(
    @Query('tenantId') tenantId?: string,
    @Query('minPurchases') minPurchases?: string,
    @Query('minLoyaltyPoints') minLoyaltyPoints?: string,
  ) {
    return this.profilesService.getAllBuyers({
      tenantId,
      minPurchases: minPurchases ? parseInt(minPurchases) : undefined,
      minLoyaltyPoints: minLoyaltyPoints ? parseInt(minLoyaltyPoints) : undefined,
    });
  }

  /**
   * جلب ملف تعريف المشتري بواسطة معرف المستخدم
   * GET /api/v1/profiles/buyers/user/:userId
   */
  @Get('user/:userId')
  @ApiOperation({ summary: 'Get buyer profile by user ID' })
  @ApiParam({ name: 'userId', description: 'User ID' })
  @ApiResponse({ status: 200, description: 'Buyer profile found' })
  @ApiResponse({ status: 404, description: 'Buyer profile not found' })
  async getBuyerProfileByUserId(@Param('userId') userId: string) {
    return this.profilesService.getBuyerProfileByUserId(userId);
  }

  /**
   * جلب ملف تعريف المشتري بواسطة المعرف
   * GET /api/v1/profiles/buyers/:id
   */
  @Get(':id')
  @ApiOperation({ summary: 'Get buyer profile by ID' })
  @ApiParam({ name: 'id', description: 'Buyer profile ID' })
  @ApiResponse({ status: 200, description: 'Buyer profile found' })
  @ApiResponse({ status: 404, description: 'Buyer profile not found' })
  async getBuyerProfileById(@Param('id') id: string) {
    return this.profilesService.getBuyerProfileById(id);
  }

  /**
   * تحديث ملف تعريف المشتري
   * PUT /api/v1/profiles/buyers/user/:userId
   */
  @Put('user/:userId')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Update buyer profile' })
  @ApiParam({ name: 'userId', description: 'User ID' })
  @ApiResponse({ status: 200, description: 'Buyer profile updated' })
  @ApiResponse({ status: 404, description: 'Buyer profile not found' })
  async updateBuyerProfile(
    @Param('userId') userId: string,
    @Body(ValidationPipe) dto: UpdateBuyerProfileDto,
  ) {
    return this.profilesService.updateBuyerProfile(userId, dto);
  }

  /**
   * إضافة عنوان شحن
   * POST /api/v1/profiles/buyers/user/:userId/addresses
   */
  @Post('user/:userId/addresses')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Add shipping address to buyer profile' })
  @ApiParam({ name: 'userId', description: 'User ID' })
  @ApiResponse({ status: 201, description: 'Shipping address added' })
  @ApiResponse({ status: 404, description: 'Buyer profile not found' })
  async addShippingAddress(
    @Param('userId') userId: string,
    @Body(ValidationPipe) dto: AddShippingAddressDto,
  ) {
    return this.profilesService.addShippingAddress(userId, dto);
  }

  /**
   * حذف عنوان شحن
   * DELETE /api/v1/profiles/buyers/user/:userId/addresses/:label
   */
  @Delete('user/:userId/addresses/:label')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Remove shipping address from buyer profile' })
  @ApiParam({ name: 'userId', description: 'User ID' })
  @ApiParam({ name: 'label', description: 'Address label to remove' })
  @ApiResponse({ status: 200, description: 'Shipping address removed' })
  @ApiResponse({ status: 404, description: 'Buyer profile not found' })
  async removeShippingAddress(
    @Param('userId') userId: string,
    @Param('label') label: string,
  ) {
    return this.profilesService.removeShippingAddress(userId, label);
  }

  /**
   * تحديث نقاط الولاء
   * PATCH /api/v1/profiles/buyers/user/:userId/loyalty-points
   */
  @Patch('user/:userId/loyalty-points')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Update loyalty points (add or subtract)' })
  @ApiParam({ name: 'userId', description: 'User ID' })
  @ApiResponse({ status: 200, description: 'Loyalty points updated' })
  @ApiResponse({ status: 404, description: 'Buyer profile not found' })
  @ApiResponse({ status: 400, description: 'Insufficient loyalty points' })
  async updateLoyaltyPoints(
    @Param('userId') userId: string,
    @Body(ValidationPipe) dto: UpdateLoyaltyPointsDto,
  ) {
    return this.profilesService.updateLoyaltyPoints(userId, dto);
  }

  /**
   * تحديث إحصائيات المشتري (للاستخدام الداخلي)
   * PATCH /api/v1/profiles/buyers/user/:userId/stats
   */
  @Patch('user/:userId/stats')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Update buyer statistics (internal use)' })
  @ApiParam({ name: 'userId', description: 'User ID' })
  @ApiResponse({ status: 200, description: 'Buyer stats updated' })
  async updateBuyerStats(
    @Param('userId') userId: string,
    @Body() dto: { purchaseAmount: number; incrementPurchases?: number },
  ) {
    return this.profilesService.updateBuyerStats(
      userId,
      dto.purchaseAmount,
      dto.incrementPurchases,
    );
  }
}
