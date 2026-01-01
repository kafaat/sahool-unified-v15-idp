/**
 * Reviews Controller
 * وحدة التحكم في تقييمات المنتجات
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
import { ReviewsService } from './reviews.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import {
  CreateProductReviewDto,
  UpdateProductReviewDto,
  MarkReviewHelpfulDto,
  ReportReviewDto,
  CreateReviewResponseDto,
  UpdateReviewResponseDto,
} from '../dto/reviews.dto';

@ApiTags('Product Reviews')
@Controller('reviews')
export class ReviewsController {
  constructor(private readonly reviewsService: ReviewsService) {}

  // ═══════════════════════════════════════════════════════════════════════════
  // Product Review Endpoints
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء تقييم منتج جديد
   * POST /api/v1/reviews
   */
  @Post()
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Create a new product review' })
  @ApiResponse({ status: 201, description: 'Review created successfully' })
  @ApiResponse({ status: 404, description: 'Buyer profile or order not found' })
  @ApiResponse({ status: 409, description: 'Review already exists for this product and order' })
  async createProductReview(@Body(ValidationPipe) dto: CreateProductReviewDto) {
    return this.reviewsService.createProductReview(dto);
  }

  /**
   * جلب تقييم بالمعرف
   * GET /api/v1/reviews/:id
   */
  @Get(':id')
  @ApiOperation({ summary: 'Get review by ID' })
  @ApiParam({ name: 'id', description: 'Review ID' })
  @ApiResponse({ status: 200, description: 'Review found' })
  @ApiResponse({ status: 404, description: 'Review not found' })
  async getReviewById(@Param('id') id: string) {
    return this.reviewsService.getReviewById(id);
  }

  /**
   * جلب تقييمات منتج
   * GET /api/v1/reviews/product/:productId
   */
  @Get('product/:productId')
  @ApiOperation({ summary: 'Get all reviews for a product' })
  @ApiParam({ name: 'productId', description: 'Product ID' })
  @ApiQuery({
    name: 'minRating',
    required: false,
    type: Number,
    description: 'Filter by minimum rating',
  })
  @ApiQuery({
    name: 'maxRating',
    required: false,
    type: Number,
    description: 'Filter by maximum rating',
  })
  @ApiQuery({
    name: 'verified',
    required: false,
    type: Boolean,
    description: 'Filter by verified purchases',
  })
  @ApiQuery({
    name: 'limit',
    required: false,
    type: Number,
    description: 'Number of reviews to return',
  })
  @ApiQuery({
    name: 'offset',
    required: false,
    type: Number,
    description: 'Number of reviews to skip',
  })
  @ApiResponse({ status: 200, description: 'List of reviews' })
  async getProductReviews(
    @Param('productId') productId: string,
    @Query('minRating') minRating?: string,
    @Query('maxRating') maxRating?: string,
    @Query('verified') verified?: string,
    @Query('limit') limit?: string,
    @Query('offset') offset?: string,
  ) {
    return this.reviewsService.getProductReviews(productId, {
      minRating: minRating ? parseInt(minRating) : undefined,
      maxRating: maxRating ? parseInt(maxRating) : undefined,
      verified: verified === 'true' ? true : verified === 'false' ? false : undefined,
      limit: limit ? parseInt(limit) : undefined,
      offset: offset ? parseInt(offset) : undefined,
    });
  }

  /**
   * جلب إحصائيات تقييمات المنتج
   * GET /api/v1/reviews/product/:productId/stats
   */
  @Get('product/:productId/stats')
  @ApiOperation({ summary: 'Get review statistics for a product' })
  @ApiParam({ name: 'productId', description: 'Product ID' })
  @ApiResponse({ status: 200, description: 'Review statistics' })
  async getProductReviewStats(@Param('productId') productId: string) {
    return this.reviewsService.getProductReviewStats(productId);
  }

  /**
   * جلب تقييمات المشتري
   * GET /api/v1/reviews/buyer/:buyerId
   */
  @Get('buyer/:buyerId')
  @ApiOperation({ summary: 'Get all reviews by a buyer' })
  @ApiParam({ name: 'buyerId', description: 'Buyer profile ID' })
  @ApiQuery({
    name: 'limit',
    required: false,
    type: Number,
    description: 'Number of reviews to return',
  })
  @ApiQuery({
    name: 'offset',
    required: false,
    type: Number,
    description: 'Number of reviews to skip',
  })
  @ApiResponse({ status: 200, description: 'List of buyer reviews' })
  async getBuyerReviews(
    @Param('buyerId') buyerId: string,
    @Query('limit') limit?: string,
    @Query('offset') offset?: string,
  ) {
    return this.reviewsService.getBuyerReviews(
      buyerId,
      limit ? parseInt(limit) : undefined,
      offset ? parseInt(offset) : undefined,
    );
  }

  /**
   * تحديث تقييم
   * PUT /api/v1/reviews/:id/buyer/:buyerId
   */
  @Put(':id/buyer/:buyerId')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Update a product review' })
  @ApiParam({ name: 'id', description: 'Review ID' })
  @ApiParam({ name: 'buyerId', description: 'Buyer profile ID' })
  @ApiResponse({ status: 200, description: 'Review updated successfully' })
  @ApiResponse({ status: 404, description: 'Review not found' })
  @ApiResponse({ status: 403, description: 'You can only edit your own reviews' })
  async updateProductReview(
    @Param('id') id: string,
    @Param('buyerId') buyerId: string,
    @Body(ValidationPipe) dto: UpdateProductReviewDto,
  ) {
    return this.reviewsService.updateProductReview(id, buyerId, dto);
  }

  /**
   * حذف تقييم
   * DELETE /api/v1/reviews/:id/buyer/:buyerId
   */
  @Delete(':id/buyer/:buyerId')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Delete a product review' })
  @ApiParam({ name: 'id', description: 'Review ID' })
  @ApiParam({ name: 'buyerId', description: 'Buyer profile ID' })
  @ApiResponse({ status: 200, description: 'Review deleted successfully' })
  @ApiResponse({ status: 404, description: 'Review not found' })
  @ApiResponse({ status: 403, description: 'You can only delete your own reviews' })
  async deleteProductReview(
    @Param('id') id: string,
    @Param('buyerId') buyerId: string,
  ) {
    return this.reviewsService.deleteProductReview(id, buyerId);
  }

  /**
   * وضع علامة على التقييم كمفيد
   * PATCH /api/v1/reviews/:id/helpful
   */
  @Patch(':id/helpful')
  @ApiOperation({ summary: 'Mark a review as helpful or not helpful' })
  @ApiParam({ name: 'id', description: 'Review ID' })
  @ApiResponse({ status: 200, description: 'Review helpfulness updated' })
  @ApiResponse({ status: 404, description: 'Review not found' })
  async markReviewHelpful(
    @Param('id') id: string,
    @Body(ValidationPipe) dto: MarkReviewHelpfulDto,
  ) {
    return this.reviewsService.markReviewHelpful(id, dto.helpful);
  }

  /**
   * الإبلاغ عن تقييم
   * POST /api/v1/reviews/:id/report
   */
  @Post(':id/report')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Report a review for inappropriate content' })
  @ApiParam({ name: 'id', description: 'Review ID' })
  @ApiResponse({ status: 200, description: 'Review reported successfully' })
  @ApiResponse({ status: 404, description: 'Review not found' })
  async reportReview(
    @Param('id') id: string,
    @Body(ValidationPipe) dto: ReportReviewDto,
  ) {
    return this.reviewsService.reportReview(id, dto.reason);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Review Response Endpoints
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء رد على تقييم
   * POST /api/v1/reviews/responses
   */
  @Post('responses')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Create a response to a review (seller only)' })
  @ApiResponse({ status: 201, description: 'Response created successfully' })
  @ApiResponse({ status: 404, description: 'Review or seller profile not found' })
  @ApiResponse({ status: 409, description: 'Response already exists for this review' })
  async createReviewResponse(@Body(ValidationPipe) dto: CreateReviewResponseDto) {
    return this.reviewsService.createReviewResponse(dto);
  }

  /**
   * جلب ردود البائع
   * GET /api/v1/reviews/responses/seller/:sellerId
   */
  @Get('responses/seller/:sellerId')
  @ApiOperation({ summary: 'Get all responses by a seller' })
  @ApiParam({ name: 'sellerId', description: 'Seller profile ID' })
  @ApiQuery({
    name: 'limit',
    required: false,
    type: Number,
    description: 'Number of responses to return',
  })
  @ApiQuery({
    name: 'offset',
    required: false,
    type: Number,
    description: 'Number of responses to skip',
  })
  @ApiResponse({ status: 200, description: 'List of seller responses' })
  async getSellerResponses(
    @Param('sellerId') sellerId: string,
    @Query('limit') limit?: string,
    @Query('offset') offset?: string,
  ) {
    return this.reviewsService.getSellerResponses(
      sellerId,
      limit ? parseInt(limit) : undefined,
      offset ? parseInt(offset) : undefined,
    );
  }

  /**
   * تحديث رد على تقييم
   * PUT /api/v1/reviews/responses/:id/seller/:sellerId
   */
  @Put('responses/:id/seller/:sellerId')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Update a review response' })
  @ApiParam({ name: 'id', description: 'Response ID' })
  @ApiParam({ name: 'sellerId', description: 'Seller profile ID' })
  @ApiResponse({ status: 200, description: 'Response updated successfully' })
  @ApiResponse({ status: 404, description: 'Response not found' })
  @ApiResponse({ status: 403, description: 'You can only edit your own responses' })
  async updateReviewResponse(
    @Param('id') id: string,
    @Param('sellerId') sellerId: string,
    @Body(ValidationPipe) dto: UpdateReviewResponseDto,
  ) {
    return this.reviewsService.updateReviewResponse(id, sellerId, dto);
  }

  /**
   * حذف رد على تقييم
   * DELETE /api/v1/reviews/responses/:id/seller/:sellerId
   */
  @Delete('responses/:id/seller/:sellerId')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Delete a review response' })
  @ApiParam({ name: 'id', description: 'Response ID' })
  @ApiParam({ name: 'sellerId', description: 'Seller profile ID' })
  @ApiResponse({ status: 200, description: 'Response deleted successfully' })
  @ApiResponse({ status: 404, description: 'Response not found' })
  @ApiResponse({ status: 403, description: 'You can only delete your own responses' })
  async deleteReviewResponse(
    @Param('id') id: string,
    @Param('sellerId') sellerId: string,
  ) {
    return this.reviewsService.deleteReviewResponse(id, sellerId);
  }
}
