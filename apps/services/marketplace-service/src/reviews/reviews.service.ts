/**
 * Reviews Service
 * خدمة إدارة تقييمات المنتجات
 *
 * ─────────────────────────────────────────────────────────────────────────
 * SECURITY MODEL
 * ─────────────────────────────────────────────────────────────────────────
 * Product reviews are user-generated *content* about a product and are
 * therefore public-readable (stats, text, rating). The PII-sensitive
 * pieces are the embedded buyer/seller profile joins, so every read/write
 * is tenant-scoped via the `id_tenantId` composite unique so a foreign
 * tenant's review rows (and their buyer/seller PII) can never be
 * materialised.
 *
 * Ownership checks use the BuyerProfile.id / SellerProfile.id resolved
 * from the *authenticated caller's* JWT `sub` — never from a URL
 * parameter (URL params were trivially forgeable and let a user post
 * reviews as any buyer profile before this commit).
 */

import {
  BadRequestException,
  ConflictException,
  ForbiddenException,
  Injectable,
  NotFoundException,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import {
  CreateProductReviewDto,
  CreateReviewResponseDto,
  UpdateProductReviewDto,
  UpdateReviewResponseDto,
} from "../dto/reviews.dto";

@Injectable()
export class ReviewsService {
  constructor(private readonly prisma: PrismaService) {}

  // ═══════════════════════════════════════════════════════════════════════════
  // Internal helpers
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Resolve the caller's BuyerProfile.id from their JWT user id.
   * Forces buyerId to the authenticated caller so `dto.buyerId` from the
   * request body cannot be used to impersonate another buyer.
   */
  private async resolveCallerBuyerId(
    callerUserId: string,
    tenantId: string,
  ): Promise<string> {
    const profile = await this.prisma.buyerProfile.findFirst({
      where: { userId: callerUserId, tenantId },
      select: { id: true },
    });
    if (!profile) {
      throw new ForbiddenException(
        "You must have a buyer profile in this tenant to post a review",
      );
    }
    return profile.id;
  }

  /** Same as resolveCallerBuyerId but for sellers. */
  private async resolveCallerSellerId(
    callerUserId: string,
    tenantId: string,
  ): Promise<string> {
    const profile = await this.prisma.sellerProfile.findFirst({
      where: { userId: callerUserId, tenantId },
      select: { id: true },
    });
    if (!profile) {
      throw new ForbiddenException(
        "You must have a seller profile in this tenant to respond to a review",
      );
    }
    return profile.id;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Product Review Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء تقييم منتج جديد.
   *
   * SECURITY: `callerUserId` is derived from the JWT by the controller.
   * The service resolves the caller's BuyerProfile id from it and ignores
   * any `dto.buyerId` the request might carry.
   */
  async createProductReview(
    dto: CreateProductReviewDto,
    tenantId: string,
    callerUserId: string,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const buyerId = await this.resolveCallerBuyerId(callerUserId, tenantId);

    // Check if buyer has already reviewed this product for this order
    const existingReview = await this.prisma.productReview.findFirst({
      where: {
        tenantId,
        productId: dto.productId,
        buyerId,
        orderId: dto.orderId,
      },
    });

    if (existingReview) {
      throw new ConflictException(
        "You have already reviewed this product for this order",
      );
    }

    // Verify the order exists in this tenant AND contains the product AND
    // belongs to the caller's buyer profile.
    const order = await this.prisma.order.findUnique({
      where: { id_tenantId: { id: dto.orderId, tenantId } },
      include: { items: true },
    });

    if (!order) {
      throw new NotFoundException("Order not found");
    }

    if (order.buyerId !== buyerId) {
      throw new ForbiddenException(
        "You may only review orders you placed yourself",
      );
    }

    const orderContainsProduct = order.items.some(
      (item: { productId: string }) => item.productId === dto.productId,
    );

    if (!orderContainsProduct) {
      throw new BadRequestException("Product not found in this order");
    }

    // Create the review
    const review = await this.prisma.productReview.create({
      data: {
        tenantId,
        productId: dto.productId,
        buyerId,
        orderId: dto.orderId,
        rating: dto.rating,
        title: dto.title,
        comment: dto.comment,
        photos: dto.photos || [],
        verified: order.status === "DELIVERED",
      },
      include: { buyer: true },
    });

    // Update product seller's rating
    await this.updateProductSellerRating(dto.productId, tenantId);

    return review;
  }

  /**
   * جلب تقييم بالمعرف (tenant-scoped).
   */
  async getReviewById(id: string, tenantId: string) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const review = await this.prisma.productReview.findUnique({
      where: { id_tenantId: { id, tenantId } },
      include: {
        buyer: true,
        response: { include: { seller: true } },
      },
    });

    if (!review) {
      throw new NotFoundException("Review not found");
    }

    return review;
  }

  /**
   * جلب تقييمات منتج (tenant-scoped).
   */
  async getProductReviews(
    productId: string,
    tenantId: string,
    filters?: {
      minRating?: number;
      maxRating?: number;
      verified?: boolean;
      limit?: number;
      offset?: number;
    },
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const where: any = { productId, tenantId };

    if (filters?.minRating) {
      where.rating = { ...where.rating, gte: filters.minRating };
    }

    if (filters?.maxRating) {
      where.rating = { ...where.rating, lte: filters.maxRating };
    }

    if (filters?.verified !== undefined) {
      where.verified = filters.verified;
    }

    const reviews = await this.prisma.productReview.findMany({
      where,
      include: {
        buyer: true,
        response: { include: { seller: true } },
      },
      orderBy: { createdAt: "desc" },
      take: filters?.limit || 20,
      skip: filters?.offset || 0,
    });

    const stats = await this.getProductReviewStats(productId, tenantId);

    return {
      reviews,
      stats,
      pagination: {
        limit: filters?.limit || 20,
        offset: filters?.offset || 0,
      },
    };
  }

  async getProductReviewStats(productId: string, tenantId: string) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const reviews = await this.prisma.productReview.findMany({
      where: { productId, tenantId },
      select: { rating: true },
      take: 1000,
    });

    if (reviews.length === 0) {
      return {
        totalReviews: 0,
        averageRating: 0,
        ratingDistribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
      };
    }

    const totalReviews = reviews.length;
    const sumRatings = reviews.reduce(
      (sum: number, r: { rating: number }) => sum + r.rating,
      0,
    );
    const averageRating = sumRatings / totalReviews;

    const ratingDistribution = reviews.reduce(
      (dist: Record<number, number>, r: { rating: number }) => {
        dist[r.rating] = (dist[r.rating] || 0) + 1;
        return dist;
      },
      { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 } as Record<number, number>,
    );

    return {
      totalReviews,
      averageRating: Math.round(averageRating * 10) / 10,
      ratingDistribution,
    };
  }

  async getBuyerReviews(
    buyerId: string,
    tenantId: string,
    limit = 20,
    offset = 0,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    return this.prisma.productReview.findMany({
      where: { buyerId, tenantId },
      include: {
        response: { include: { seller: true } },
      },
      orderBy: { createdAt: "desc" },
      take: limit,
      skip: offset,
    });
  }

  /**
   * تحديث تقييم.
   *
   * SECURITY: resolves buyerId from caller's JWT (NOT from URL). Rejects
   * if the review's buyerId doesn't match, so a forged reviewId still
   * returns 403 rather than succeeding with a spoofed ownership claim.
   */
  async updateProductReview(
    id: string,
    dto: UpdateProductReviewDto,
    tenantId: string,
    callerUserId: string,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const callerBuyerId = await this.resolveCallerBuyerId(
      callerUserId,
      tenantId,
    );

    const review = await this.prisma.productReview.findUnique({
      where: { id_tenantId: { id, tenantId } },
    });

    if (!review) {
      throw new NotFoundException("Review not found");
    }

    if (review.buyerId !== callerBuyerId) {
      throw new ForbiddenException("You can only edit your own reviews");
    }

    const updatedReview = await this.prisma.productReview.update({
      where: { id_tenantId: { id, tenantId } },
      data: {
        ...(dto.rating && { rating: dto.rating }),
        ...(dto.title && { title: dto.title }),
        ...(dto.comment !== undefined && { comment: dto.comment }),
        ...(dto.photos !== undefined && { photos: dto.photos }),
      },
      include: {
        buyer: true,
        response: { include: { seller: true } },
      },
    });

    if (dto.rating) {
      await this.updateProductSellerRating(review.productId, tenantId);
    }

    return updatedReview;
  }

  async deleteProductReview(
    id: string,
    tenantId: string,
    callerUserId: string,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const callerBuyerId = await this.resolveCallerBuyerId(
      callerUserId,
      tenantId,
    );

    const review = await this.prisma.productReview.findUnique({
      where: { id_tenantId: { id, tenantId } },
    });

    if (!review) {
      throw new NotFoundException("Review not found");
    }

    if (review.buyerId !== callerBuyerId) {
      throw new ForbiddenException("You can only delete your own reviews");
    }

    const productId = review.productId;

    await this.prisma.productReview.delete({
      where: { id_tenantId: { id, tenantId } },
    });

    await this.updateProductSellerRating(productId, tenantId);

    return { message: "Review deleted successfully" };
  }

  async markReviewHelpful(id: string, helpful: boolean, tenantId: string) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const review = await this.prisma.productReview.findUnique({
      where: { id_tenantId: { id, tenantId } },
    });

    if (!review) {
      throw new NotFoundException("Review not found");
    }

    return this.prisma.productReview.update({
      where: { id_tenantId: { id, tenantId } },
      data: {
        helpful: helpful ? { increment: 1 } : { decrement: 1 },
      },
    });
  }

  async reportReview(id: string, _reason: string, tenantId: string) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const review = await this.prisma.productReview.findUnique({
      where: { id_tenantId: { id, tenantId } },
    });

    if (!review) {
      throw new NotFoundException("Review not found");
    }

    return this.prisma.productReview.update({
      where: { id_tenantId: { id, tenantId } },
      data: { reported: true },
    });
  }

  /**
   * تحديث تقييم البائع (داخلي) — tenant-scoped.
   */
  private async updateProductSellerRating(
    productId: string,
    tenantId: string,
  ) {
    const result = await this.prisma.$queryRaw<
      Array<{
        seller_id: string;
        seller_profile_id: string | null;
        avg_rating: number | null;
        review_count: number;
      }>
    >`
      SELECT
        p.seller_id,
        sp.id as seller_profile_id,
        AVG(pr.rating) as avg_rating,
        COUNT(pr.id)::int as review_count
      FROM products p
      LEFT JOIN seller_profiles sp ON sp.user_id = p.seller_id AND sp.tenant_id = ${tenantId}
      LEFT JOIN products seller_products ON seller_products.seller_id = p.seller_id AND seller_products.tenant_id = ${tenantId}
      LEFT JOIN product_reviews pr ON pr.product_id = seller_products.id AND pr.tenant_id = ${tenantId}
      WHERE p.id = ${productId}::uuid AND p.tenant_id = ${tenantId}
      GROUP BY p.seller_id, sp.id
    `;

    if (result.length === 0 || !result[0].seller_profile_id) {
      return;
    }

    const { seller_profile_id, avg_rating, review_count } = result[0];

    if (review_count > 0 && avg_rating !== null) {
      await this.prisma.sellerProfile.update({
        where: {
          id_tenantId: { id: seller_profile_id, tenantId },
        },
        data: { rating: Math.round(avg_rating * 10) / 10 },
      });
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Review Response Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء رد على تقييم.
   *
   * SECURITY: resolves sellerId from caller's JWT — `dto.sellerId` is
   * ignored. Verifies the target review is in the caller's tenant and
   * that the product's seller matches the caller.
   */
  async createReviewResponse(
    dto: CreateReviewResponseDto,
    tenantId: string,
    callerUserId: string,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const sellerId = await this.resolveCallerSellerId(callerUserId, tenantId);

    const review = await this.prisma.productReview.findUnique({
      where: { id_tenantId: { id: dto.reviewId, tenantId } },
      include: { product: true },
    });

    if (!review) {
      throw new NotFoundException("Review not found");
    }

    // Reject attempts to reply to a review on someone else's product.
    const product = (review as any).product;
    const sellerProfile = await this.prisma.sellerProfile.findFirst({
      where: { id: sellerId, tenantId },
      select: { userId: true },
    });
    if (!sellerProfile || product?.sellerId !== sellerProfile.userId) {
      throw new ForbiddenException(
        "You can only respond to reviews on your own products",
      );
    }

    const existingResponse = await this.prisma.reviewResponse.findUnique({
      where: { reviewId: dto.reviewId },
    });

    if (existingResponse) {
      throw new ConflictException("Response already exists for this review");
    }

    return this.prisma.reviewResponse.create({
      data: {
        reviewId: dto.reviewId,
        sellerId,
        response: dto.response,
      },
      include: {
        review: true,
        seller: true,
      },
    });
  }

  async updateReviewResponse(
    id: string,
    dto: UpdateReviewResponseDto,
    tenantId: string,
    callerUserId: string,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const callerSellerId = await this.resolveCallerSellerId(
      callerUserId,
      tenantId,
    );

    const response = await this.prisma.reviewResponse.findUnique({
      where: { id },
    });

    if (!response) {
      throw new NotFoundException("Review response not found");
    }

    if (response.sellerId !== callerSellerId) {
      throw new ForbiddenException("You can only edit your own responses");
    }

    return this.prisma.reviewResponse.update({
      where: { id },
      data: { response: dto.response },
      include: {
        review: true,
        seller: true,
      },
    });
  }

  async deleteReviewResponse(
    id: string,
    tenantId: string,
    callerUserId: string,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const callerSellerId = await this.resolveCallerSellerId(
      callerUserId,
      tenantId,
    );

    const response = await this.prisma.reviewResponse.findUnique({
      where: { id },
    });

    if (!response) {
      throw new NotFoundException("Review response not found");
    }

    if (response.sellerId !== callerSellerId) {
      throw new ForbiddenException("You can only delete your own responses");
    }

    await this.prisma.reviewResponse.delete({
      where: { id },
    });

    return { message: "Review response deleted successfully" };
  }

  async getSellerResponses(
    sellerId: string,
    tenantId: string,
    limit = 20,
    offset = 0,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    return this.prisma.reviewResponse.findMany({
      where: {
        sellerId,
        review: { tenantId },
      },
      include: {
        review: {
          include: { buyer: true },
        },
      },
      orderBy: { createdAt: "desc" },
      take: limit,
      skip: offset,
    });
  }
}
