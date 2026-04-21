/**
 * Reviews Controller
 * وحدة التحكم في تقييمات المنتجات
 *
 * Security hardening (2026-04-21):
 * - All endpoints require JwtAuthGuard (read endpoints expose PII-joined
 *   buyer/seller profiles, so anonymous access is blocked).
 * - tenantId from JWT only (no `x-tenant-id` header, no `?tenantId=`).
 * - Write endpoints derive buyerId/sellerId from the caller's JWT via
 *   the service helpers; the previous URL-param ownership checks were
 *   trivially forgeable.
 */

import {
  Body,
  Controller,
  Delete,
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
import { Throttle } from "@nestjs/throttler";
import {
  ApiBearerAuth,
  ApiOperation,
  ApiParam,
  ApiResponse,
  ApiTags,
} from "@nestjs/swagger";
import {
  CreateProductReviewDto,
  CreateReviewResponseDto,
  GetProductReviewsQueryDto,
  MarkReviewHelpfulDto,
  PaginationQueryDto,
  ReportReviewDto,
  UpdateProductReviewDto,
  UpdateReviewResponseDto,
} from "../dto/reviews.dto";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { ReviewsService } from "./reviews.service";

@ApiTags("Product Reviews")
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller("reviews")
export class ReviewsController {
  constructor(private readonly reviewsService: ReviewsService) {}

  // ─── auth helpers ───────────────────────────────────────────────────────

  private requireTenantId(req: any): string {
    const tenantId = req?.user?.tenantId ?? req?.user?.tid;
    if (!tenantId) {
      throw new UnauthorizedException("tenantId missing from JWT");
    }
    return String(tenantId);
  }

  private requireUserId(req: any): string {
    const userId = req?.user?.id;
    if (!userId) {
      throw new UnauthorizedException("user id missing from JWT");
    }
    return String(userId);
  }

  // ─── product review endpoints ───────────────────────────────────────────

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: "Create a new product review" })
  @ApiResponse({ status: 201, description: "Review created successfully" })
  async createProductReview(
    @Req() req: any,
    @Body(ValidationPipe) dto: CreateProductReviewDto,
  ) {
    const tenantId = this.requireTenantId(req);
    const userId = this.requireUserId(req);
    return this.reviewsService.createProductReview(dto, tenantId, userId);
  }

  @Get("product/:productId/stats")
  @ApiOperation({ summary: "Get review statistics for a product (tenant-scoped)" })
  @ApiParam({ name: "productId", description: "Product ID" })
  async getProductReviewStats(
    @Req() req: any,
    @Param("productId") productId: string,
  ) {
    const tenantId = this.requireTenantId(req);
    return this.reviewsService.getProductReviewStats(productId, tenantId);
  }

  @Get("product/:productId")
  @ApiOperation({ summary: "Get all reviews for a product (tenant-scoped)" })
  @ApiParam({ name: "productId", description: "Product ID" })
  async getProductReviews(
    @Req() req: any,
    @Param("productId") productId: string,
    @Query() query: GetProductReviewsQueryDto,
  ) {
    const tenantId = this.requireTenantId(req);
    return this.reviewsService.getProductReviews(productId, tenantId, query);
  }

  @Get(":id")
  @ApiOperation({ summary: "Get review by ID (tenant-scoped)" })
  @ApiParam({ name: "id", description: "Review ID" })
  async getReviewById(@Req() req: any, @Param("id") id: string) {
    const tenantId = this.requireTenantId(req);
    return this.reviewsService.getReviewById(id, tenantId);
  }

  @Get("buyer/:buyerId")
  @ApiOperation({ summary: "Get all reviews by a buyer (tenant-scoped)" })
  @ApiParam({ name: "buyerId", description: "Buyer profile ID" })
  async getBuyerReviews(
    @Req() req: any,
    @Param("buyerId") buyerId: string,
    @Query() query: PaginationQueryDto,
  ) {
    const tenantId = this.requireTenantId(req);
    return this.reviewsService.getBuyerReviews(
      buyerId,
      tenantId,
      query.limit,
      query.offset,
    );
  }

  /**
   * تحديث تقييم. Route simplified to PUT /:id — ownership is derived
   * from the JWT (no URL :buyerId to forge).
   */
  @Put(":id")
  @ApiOperation({ summary: "Update a product review (owner only)" })
  @ApiParam({ name: "id", description: "Review ID" })
  async updateProductReview(
    @Req() req: any,
    @Param("id") id: string,
    @Body(ValidationPipe) dto: UpdateProductReviewDto,
  ) {
    const tenantId = this.requireTenantId(req);
    const userId = this.requireUserId(req);
    return this.reviewsService.updateProductReview(id, dto, tenantId, userId);
  }

  @Delete(":id")
  @ApiOperation({ summary: "Delete a product review (owner only)" })
  @ApiParam({ name: "id", description: "Review ID" })
  async deleteProductReview(@Req() req: any, @Param("id") id: string) {
    const tenantId = this.requireTenantId(req);
    const userId = this.requireUserId(req);
    return this.reviewsService.deleteProductReview(id, tenantId, userId);
  }

  @Patch(":id/helpful")
  // Tight per-user throttle — 10 helpful-toggles per minute is plenty for
  // humans and blocks automated vote-stuffing. The service additionally
  // enforces the one-vote-per-(tenant,review,user) invariant at the DB
  // layer via `review_helpful_votes.uq_helpful_vote_tenant_review_user`.
  @Throttle({ default: { limit: 10, ttl: 60_000 } })
  @ApiOperation({ summary: "Mark a review as helpful or not helpful" })
  @ApiParam({ name: "id", description: "Review ID" })
  async markReviewHelpful(
    @Req() req: any,
    @Param("id") id: string,
    @Body(ValidationPipe) dto: MarkReviewHelpfulDto,
  ) {
    const tenantId = this.requireTenantId(req);
    const userId = this.requireUserId(req);
    return this.reviewsService.markReviewHelpful(id, dto.helpful, tenantId, userId);
  }

  @Post(":id/report")
  // Looser but still protective throttle for abuse-reports — 5 per minute
  // is enough for a concerned buyer reporting a cluster of spam reviews
  // while blocking mass-report denial-of-reputation attacks. A second
  // line of defence is `review_reports.uq_report_tenant_review_reporter`
  // — a single reporter can't inflate the counter past +1 no matter how
  // often they POST.
  @Throttle({ default: { limit: 5, ttl: 60_000 } })
  @ApiOperation({ summary: "Report a review for inappropriate content" })
  @ApiParam({ name: "id", description: "Review ID" })
  async reportReview(
    @Req() req: any,
    @Param("id") id: string,
    @Body(ValidationPipe) dto: ReportReviewDto,
  ) {
    const tenantId = this.requireTenantId(req);
    const userId = this.requireUserId(req);
    return this.reviewsService.reportReview(id, dto.reason, tenantId, userId);
  }

  // ─── review response endpoints ──────────────────────────────────────────

  @Post("responses")
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: "Create a response to a review (seller only)" })
  async createReviewResponse(
    @Req() req: any,
    @Body(ValidationPipe) dto: CreateReviewResponseDto,
  ) {
    const tenantId = this.requireTenantId(req);
    const userId = this.requireUserId(req);
    return this.reviewsService.createReviewResponse(dto, tenantId, userId);
  }

  @Get("responses/seller/:sellerId")
  @ApiOperation({ summary: "Get all responses by a seller (tenant-scoped)" })
  async getSellerResponses(
    @Req() req: any,
    @Param("sellerId") sellerId: string,
    @Query() query: PaginationQueryDto,
  ) {
    const tenantId = this.requireTenantId(req);
    return this.reviewsService.getSellerResponses(
      sellerId,
      tenantId,
      query.limit,
      query.offset,
    );
  }

  @Put("responses/:id")
  @ApiOperation({ summary: "Update a review response (owner only)" })
  async updateReviewResponse(
    @Req() req: any,
    @Param("id") id: string,
    @Body(ValidationPipe) dto: UpdateReviewResponseDto,
  ) {
    const tenantId = this.requireTenantId(req);
    const userId = this.requireUserId(req);
    return this.reviewsService.updateReviewResponse(id, dto, tenantId, userId);
  }

  @Delete("responses/:id")
  @ApiOperation({ summary: "Delete a review response (owner only)" })
  async deleteReviewResponse(@Req() req: any, @Param("id") id: string) {
    const tenantId = this.requireTenantId(req);
    const userId = this.requireUserId(req);
    return this.reviewsService.deleteReviewResponse(id, tenantId, userId);
  }
}
