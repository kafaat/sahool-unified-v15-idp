/**
 * Reviews Controller Tests
 * اختبارات وحدة التحكم في تقييمات المنتجات
 */

import { Test, TestingModule } from '@nestjs/testing';
import { ReviewsController } from './reviews.controller';
import { ReviewsService } from './reviews.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import {
  CreateProductReviewDto,
  UpdateProductReviewDto,
  MarkReviewHelpfulDto,
  GetProductReviewsQueryDto,
  PaginationQueryDto,
} from '../dto/reviews.dto';

describe('ReviewsController', () => {
  let controller: ReviewsController;
  let service: ReviewsService;

  const mockReviewsService = {
    createProductReview: jest.fn(),
    getReviewById: jest.fn(),
    getProductReviews: jest.fn(),
    getProductReviewStats: jest.fn(),
    getBuyerReviews: jest.fn(),
    updateProductReview: jest.fn(),
    deleteProductReview: jest.fn(),
    markReviewHelpful: jest.fn(),
    reportReview: jest.fn(),
    createReviewResponse: jest.fn(),
    updateReviewResponse: jest.fn(),
    deleteReviewResponse: jest.fn(),
    getSellerResponses: jest.fn(),
  };

  const mockJwtAuthGuard = {
    canActivate: jest.fn(() => true),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [ReviewsController],
      providers: [
        {
          provide: ReviewsService,
          useValue: mockReviewsService,
        },
        {
          provide: JwtAuthGuard,
          useValue: mockJwtAuthGuard,
        },
      ],
    }).compile();

    controller = module.get<ReviewsController>(ReviewsController);
    service = module.get<ReviewsService>(ReviewsService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });

  describe('createProductReview', () => {
    it('should create a new review', async () => {
      const dto: CreateProductReviewDto = {
        productId: 'prod-123',
        buyerId: 'buyer-456',
        orderId: 'order-789',
        rating: 5,
        title: 'منتج ممتاز',
        comment: 'جودة عالية',
      };

      const expectedResult = {
        id: 'review-123',
        ...dto,
        createdAt: new Date(),
      };

      mockReviewsService.createProductReview.mockResolvedValue(expectedResult);

      const result = await controller.createProductReview(dto);

      expect(result).toEqual(expectedResult);
      expect(service.createProductReview).toHaveBeenCalledWith(dto);
    });
  });

  describe('getProductReviewStats', () => {
    it('should return review statistics before getting reviews', async () => {
      const productId = 'prod-123';
      const expectedStats = {
        totalReviews: 10,
        averageRating: 4.5,
        ratingDistribution: { 1: 0, 2: 1, 3: 2, 4: 3, 5: 4 },
      };

      mockReviewsService.getProductReviewStats.mockResolvedValue(expectedStats);

      const result = await controller.getProductReviewStats(productId);

      expect(result).toEqual(expectedStats);
      expect(service.getProductReviewStats).toHaveBeenCalledWith(productId);
    });
  });

  describe('getProductReviews', () => {
    it('should return product reviews with filters', async () => {
      const productId = 'prod-123';
      const query: GetProductReviewsQueryDto = {
        minRating: 3,
        maxRating: 5,
        verified: true,
        limit: 20,
        offset: 0,
      };

      const expectedResult = {
        reviews: [
          {
            id: 'review-123',
            productId,
            rating: 4,
            title: 'جيد',
            verified: true,
          },
        ],
        stats: {
          totalReviews: 1,
          averageRating: 4.0,
        },
        pagination: {
          limit: 20,
          offset: 0,
        },
      };

      mockReviewsService.getProductReviews.mockResolvedValue(expectedResult);

      const result = await controller.getProductReviews(productId, query);

      expect(result).toEqual(expectedResult);
      expect(service.getProductReviews).toHaveBeenCalledWith(productId, query);
    });
  });

  describe('getReviewById', () => {
    it('should return a single review by ID', async () => {
      const reviewId = 'review-123';
      const expectedReview = {
        id: reviewId,
        productId: 'prod-123',
        rating: 5,
        title: 'ممتاز',
      };

      mockReviewsService.getReviewById.mockResolvedValue(expectedReview);

      const result = await controller.getReviewById(reviewId);

      expect(result).toEqual(expectedReview);
      expect(service.getReviewById).toHaveBeenCalledWith(reviewId);
    });
  });

  describe('getBuyerReviews', () => {
    it('should return buyer reviews with pagination', async () => {
      const buyerId = 'buyer-456';
      const query: PaginationQueryDto = {
        limit: 10,
        offset: 0,
      };

      const expectedReviews = [
        {
          id: 'review-123',
          buyerId,
          rating: 4,
        },
      ];

      mockReviewsService.getBuyerReviews.mockResolvedValue(expectedReviews);

      const result = await controller.getBuyerReviews(buyerId, query);

      expect(result).toEqual(expectedReviews);
      expect(service.getBuyerReviews).toHaveBeenCalledWith(
        buyerId,
        query.limit,
        query.offset,
      );
    });
  });

  describe('updateProductReview', () => {
    it('should update a review', async () => {
      const reviewId = 'review-123';
      const buyerId = 'buyer-456';
      const dto: UpdateProductReviewDto = {
        rating: 5,
        title: 'ممتاز جداً',
      };

      const expectedResult = {
        id: reviewId,
        buyerId,
        ...dto,
        updatedAt: new Date(),
      };

      mockReviewsService.updateProductReview.mockResolvedValue(expectedResult);

      const result = await controller.updateProductReview(reviewId, buyerId, dto);

      expect(result).toEqual(expectedResult);
      expect(service.updateProductReview).toHaveBeenCalledWith(
        reviewId,
        buyerId,
        dto,
      );
    });
  });

  describe('deleteProductReview', () => {
    it('should delete a review', async () => {
      const reviewId = 'review-123';
      const buyerId = 'buyer-456';
      const expectedResult = { message: 'Review deleted successfully' };

      mockReviewsService.deleteProductReview.mockResolvedValue(expectedResult);

      const result = await controller.deleteProductReview(reviewId, buyerId);

      expect(result).toEqual(expectedResult);
      expect(service.deleteProductReview).toHaveBeenCalledWith(reviewId, buyerId);
    });
  });

  describe('markReviewHelpful', () => {
    it('should mark review as helpful', async () => {
      const reviewId = 'review-123';
      const dto: MarkReviewHelpfulDto = {
        helpful: true,
      };

      const expectedResult = {
        id: reviewId,
        helpful: 5,
      };

      mockReviewsService.markReviewHelpful.mockResolvedValue(expectedResult);

      const result = await controller.markReviewHelpful(reviewId, dto);

      expect(result).toEqual(expectedResult);
      expect(service.markReviewHelpful).toHaveBeenCalledWith(
        reviewId,
        dto.helpful,
      );
    });
  });

  describe('reportReview', () => {
    it('should report a review', async () => {
      const reviewId = 'review-123';
      const dto = {
        reason: 'محتوى غير مناسب',
      };

      const expectedResult = {
        id: reviewId,
        reported: true,
      };

      mockReviewsService.reportReview.mockResolvedValue(expectedResult);

      const result = await controller.reportReview(reviewId, dto);

      expect(result).toEqual(expectedResult);
      expect(service.reportReview).toHaveBeenCalledWith(reviewId, dto.reason);
    });
  });

  describe('getSellerResponses', () => {
    it('should return seller responses with pagination', async () => {
      const sellerId = 'seller-789';
      const query: PaginationQueryDto = {
        limit: 20,
        offset: 0,
      };

      const expectedResponses = [
        {
          id: 'response-123',
          sellerId,
          response: 'شكراً لتقييمك',
        },
      ];

      mockReviewsService.getSellerResponses.mockResolvedValue(expectedResponses);

      const result = await controller.getSellerResponses(sellerId, query);

      expect(result).toEqual(expectedResponses);
      expect(service.getSellerResponses).toHaveBeenCalledWith(
        sellerId,
        query.limit,
        query.offset,
      );
    });
  });
});
