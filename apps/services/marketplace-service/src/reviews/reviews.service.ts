/**
 * Reviews Service
 * خدمة إدارة تقييمات المنتجات
 */

import {
  Injectable,
  NotFoundException,
  ConflictException,
  BadRequestException,
  ForbiddenException,
} from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import {
  CreateProductReviewDto,
  UpdateProductReviewDto,
  CreateReviewResponseDto,
  UpdateReviewResponseDto,
} from '../dto/reviews.dto';

@Injectable()
export class ReviewsService {
  constructor(private readonly prisma: PrismaService) {}

  // ═══════════════════════════════════════════════════════════════════════════
  // Product Review Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء تقييم منتج جديد
   */
  async createProductReview(dto: CreateProductReviewDto) {
    // Verify the buyer profile exists
    const buyerProfile = await this.prisma.buyerProfile.findUnique({
      where: { id: dto.buyerId },
    });

    if (!buyerProfile) {
      throw new NotFoundException('Buyer profile not found');
    }

    // Check if buyer has already reviewed this product for this order
    const existingReview = await this.prisma.productReview.findFirst({
      where: {
        productId: dto.productId,
        buyerId: dto.buyerId,
        orderId: dto.orderId,
      },
    });

    if (existingReview) {
      throw new ConflictException(
        'You have already reviewed this product for this order',
      );
    }

    // Verify the order exists and contains the product
    const order = await this.prisma.order.findUnique({
      where: { id: dto.orderId },
      include: { items: true },
    });

    if (!order) {
      throw new NotFoundException('Order not found');
    }

    const orderContainsProduct = order.items.some(
      (item) => item.productId === dto.productId,
    );

    if (!orderContainsProduct) {
      throw new BadRequestException('Product not found in this order');
    }

    // Create the review
    const review = await this.prisma.productReview.create({
      data: {
        productId: dto.productId,
        buyerId: dto.buyerId,
        orderId: dto.orderId,
        rating: dto.rating,
        title: dto.title,
        comment: dto.comment,
        photos: dto.photos || [],
        verified: order.status === 'DELIVERED', // Verify if order is delivered
      },
      include: {
        buyer: true,
      },
    });

    // Update product seller's rating
    await this.updateProductSellerRating(dto.productId);

    return review;
  }

  /**
   * جلب تقييم بالمعرف
   */
  async getReviewById(id: string) {
    const review = await this.prisma.productReview.findUnique({
      where: { id },
      include: {
        buyer: true,
        response: {
          include: {
            seller: true,
          },
        },
      },
    });

    if (!review) {
      throw new NotFoundException('Review not found');
    }

    return review;
  }

  /**
   * جلب تقييمات منتج
   */
  async getProductReviews(
    productId: string,
    filters?: {
      minRating?: number;
      maxRating?: number;
      verified?: boolean;
      limit?: number;
      offset?: number;
    },
  ) {
    const where: any = { productId };

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
        response: {
          include: {
            seller: true,
          },
        },
      },
      orderBy: { createdAt: 'desc' },
      take: filters?.limit || 20,
      skip: filters?.offset || 0,
    });

    // Calculate review statistics
    const stats = await this.getProductReviewStats(productId);

    return {
      reviews,
      stats,
      pagination: {
        limit: filters?.limit || 20,
        offset: filters?.offset || 0,
      },
    };
  }

  /**
   * جلب إحصائيات تقييمات المنتج
   */
  async getProductReviewStats(productId: string) {
    const reviews = await this.prisma.productReview.findMany({
      where: { productId },
      select: { rating: true },
    });

    if (reviews.length === 0) {
      return {
        totalReviews: 0,
        averageRating: 0,
        ratingDistribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
      };
    }

    const totalReviews = reviews.length;
    const sumRatings = reviews.reduce((sum, r) => sum + r.rating, 0);
    const averageRating = sumRatings / totalReviews;

    const ratingDistribution = reviews.reduce(
      (dist, r) => {
        dist[r.rating] = (dist[r.rating] || 0) + 1;
        return dist;
      },
      { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 } as Record<number, number>,
    );

    return {
      totalReviews,
      averageRating: Math.round(averageRating * 10) / 10, // Round to 1 decimal
      ratingDistribution,
    };
  }

  /**
   * جلب تقييمات المشتري
   */
  async getBuyerReviews(buyerId: string, limit = 20, offset = 0) {
    return this.prisma.productReview.findMany({
      where: { buyerId },
      include: {
        response: {
          include: {
            seller: true,
          },
        },
      },
      orderBy: { createdAt: 'desc' },
      take: limit,
      skip: offset,
    });
  }

  /**
   * تحديث تقييم
   */
  async updateProductReview(id: string, buyerId: string, dto: UpdateProductReviewDto) {
    const review = await this.prisma.productReview.findUnique({
      where: { id },
    });

    if (!review) {
      throw new NotFoundException('Review not found');
    }

    // Ensure the buyer owns this review
    if (review.buyerId !== buyerId) {
      throw new ForbiddenException('You can only edit your own reviews');
    }

    const updatedReview = await this.prisma.productReview.update({
      where: { id },
      data: {
        ...(dto.rating && { rating: dto.rating }),
        ...(dto.title && { title: dto.title }),
        ...(dto.comment !== undefined && { comment: dto.comment }),
        ...(dto.photos !== undefined && { photos: dto.photos }),
      },
      include: {
        buyer: true,
        response: {
          include: {
            seller: true,
          },
        },
      },
    });

    // Update product seller's rating if rating changed
    if (dto.rating) {
      await this.updateProductSellerRating(review.productId);
    }

    return updatedReview;
  }

  /**
   * حذف تقييم
   */
  async deleteProductReview(id: string, buyerId: string) {
    const review = await this.prisma.productReview.findUnique({
      where: { id },
    });

    if (!review) {
      throw new NotFoundException('Review not found');
    }

    // Ensure the buyer owns this review
    if (review.buyerId !== buyerId) {
      throw new ForbiddenException('You can only delete your own reviews');
    }

    const productId = review.productId;

    await this.prisma.productReview.delete({
      where: { id },
    });

    // Update product seller's rating
    await this.updateProductSellerRating(productId);

    return { message: 'Review deleted successfully' };
  }

  /**
   * وضع علامة على التقييم كمفيد
   */
  async markReviewHelpful(id: string, helpful: boolean) {
    const review = await this.prisma.productReview.findUnique({
      where: { id },
    });

    if (!review) {
      throw new NotFoundException('Review not found');
    }

    return this.prisma.productReview.update({
      where: { id },
      data: {
        helpful: helpful ? { increment: 1 } : { decrement: 1 },
      },
    });
  }

  /**
   * الإبلاغ عن تقييم
   */
  async reportReview(id: string, reason: string) {
    const review = await this.prisma.productReview.findUnique({
      where: { id },
    });

    if (!review) {
      throw new NotFoundException('Review not found');
    }

    return this.prisma.productReview.update({
      where: { id },
      data: { reported: true },
    });
  }

  /**
   * تحديث تقييم البائع (داخلي)
   * Optimized to prevent N+1 queries using a single aggregation query
   */
  private async updateProductSellerRating(productId: string) {
    // Use raw SQL for optimal performance with a single query
    // This query:
    // 1. Joins product to find seller
    // 2. Gets all products by this seller
    // 3. Aggregates all reviews for those products
    // 4. Returns seller info and average rating
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
      LEFT JOIN seller_profiles sp ON sp.user_id = p.seller_id
      LEFT JOIN products seller_products ON seller_products.seller_id = p.seller_id
      LEFT JOIN product_reviews pr ON pr.product_id = seller_products.id
      WHERE p.id = ${productId}::uuid
      GROUP BY p.seller_id, sp.id
    `;

    if (result.length === 0 || !result[0].seller_profile_id) {
      return;
    }

    const { seller_profile_id, avg_rating, review_count } = result[0];

    // Only update if there are reviews
    if (review_count > 0 && avg_rating !== null) {
      await this.prisma.sellerProfile.update({
        where: { id: seller_profile_id },
        data: { rating: Math.round(avg_rating * 10) / 10 },
      });
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Review Response Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء رد على تقييم
   */
  async createReviewResponse(dto: CreateReviewResponseDto) {
    // Verify the review exists
    const review = await this.prisma.productReview.findUnique({
      where: { id: dto.reviewId },
    });

    if (!review) {
      throw new NotFoundException('Review not found');
    }

    // Check if response already exists
    const existingResponse = await this.prisma.reviewResponse.findUnique({
      where: { reviewId: dto.reviewId },
    });

    if (existingResponse) {
      throw new ConflictException('Response already exists for this review');
    }

    // Verify seller profile exists
    const sellerProfile = await this.prisma.sellerProfile.findUnique({
      where: { id: dto.sellerId },
    });

    if (!sellerProfile) {
      throw new NotFoundException('Seller profile not found');
    }

    return this.prisma.reviewResponse.create({
      data: {
        reviewId: dto.reviewId,
        sellerId: dto.sellerId,
        response: dto.response,
      },
      include: {
        review: true,
        seller: true,
      },
    });
  }

  /**
   * تحديث رد على تقييم
   */
  async updateReviewResponse(id: string, sellerId: string, dto: UpdateReviewResponseDto) {
    const response = await this.prisma.reviewResponse.findUnique({
      where: { id },
    });

    if (!response) {
      throw new NotFoundException('Review response not found');
    }

    // Ensure the seller owns this response
    if (response.sellerId !== sellerId) {
      throw new ForbiddenException('You can only edit your own responses');
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

  /**
   * حذف رد على تقييم
   */
  async deleteReviewResponse(id: string, sellerId: string) {
    const response = await this.prisma.reviewResponse.findUnique({
      where: { id },
    });

    if (!response) {
      throw new NotFoundException('Review response not found');
    }

    // Ensure the seller owns this response
    if (response.sellerId !== sellerId) {
      throw new ForbiddenException('You can only delete your own responses');
    }

    await this.prisma.reviewResponse.delete({
      where: { id },
    });

    return { message: 'Review response deleted successfully' };
  }

  /**
   * جلب ردود البائع
   */
  async getSellerResponses(sellerId: string, limit = 20, offset = 0) {
    return this.prisma.reviewResponse.findMany({
      where: { sellerId },
      include: {
        review: {
          include: {
            buyer: true,
          },
        },
      },
      orderBy: { createdAt: 'desc' },
      take: limit,
      skip: offset,
    });
  }
}
