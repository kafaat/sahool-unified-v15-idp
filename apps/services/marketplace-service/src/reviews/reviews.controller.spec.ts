/**
 * Reviews Controller Tests
 * اختبارات وحدة التحكم في تقييمات المنتجات
 *
 * Rewritten for the 2026-04-21 security hardening:
 *   - Every endpoint requires JwtAuthGuard.
 *   - tenantId + userId come from `req.user` (JWT) only.
 *   - Ownership is resolved server-side; URL `:buyerId` / `:sellerId`
 *     parameters are gone. The spec asserts the new service signatures.
 */

import { Test, TestingModule } from "@nestjs/testing";
import { ReviewsController } from "./reviews.controller";
import { ReviewsService } from "./reviews.service";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import {
  CreateProductReviewDto,
  CreateReviewResponseDto,
  GetProductReviewsQueryDto,
  MarkReviewHelpfulDto,
  PaginationQueryDto,
  UpdateProductReviewDto,
  UpdateReviewResponseDto,
} from "../dto/reviews.dto";

const MOCK_TENANT = "tenant-1";
const MOCK_USER = "user-42";
const mockReq: any = { user: { id: MOCK_USER, tenantId: MOCK_TENANT } };

describe("ReviewsController", () => {
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

  const mockJwtAuthGuard = { canActivate: jest.fn(() => true) };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [ReviewsController],
      providers: [
        { provide: ReviewsService, useValue: mockReviewsService },
        { provide: JwtAuthGuard, useValue: mockJwtAuthGuard },
      ],
    }).compile();

    controller = module.get<ReviewsController>(ReviewsController);
    service = module.get<ReviewsService>(ReviewsService);
  });

  afterEach(() => jest.clearAllMocks());

  it("should be defined", () => {
    expect(controller).toBeDefined();
  });

  describe("createProductReview", () => {
    it("passes (dto, tenantId, userId) to the service", async () => {
      const dto: CreateProductReviewDto = {
        productId: "prod-123",
        buyerId: "buyer-456", // ignored by the service
        orderId: "order-789",
        rating: 5,
        title: "منتج ممتاز",
        comment: "جودة عالية",
      };
      mockReviewsService.createProductReview.mockResolvedValue({ id: "r1" });

      await controller.createProductReview(mockReq, dto);

      expect(service.createProductReview).toHaveBeenCalledWith(
        dto,
        MOCK_TENANT,
        MOCK_USER,
      );
    });
  });

  describe("getProductReviewStats", () => {
    it("threads tenantId from JWT", async () => {
      mockReviewsService.getProductReviewStats.mockResolvedValue({
        totalReviews: 0,
      });
      await controller.getProductReviewStats(mockReq, "prod-123");
      expect(service.getProductReviewStats).toHaveBeenCalledWith(
        "prod-123",
        MOCK_TENANT,
      );
    });
  });

  describe("getProductReviews", () => {
    it("threads tenantId from JWT + passes the query", async () => {
      const query: GetProductReviewsQueryDto = {
        minRating: 3,
        maxRating: 5,
        verified: true,
        limit: 20,
        offset: 0,
      };
      mockReviewsService.getProductReviews.mockResolvedValue({ reviews: [] });

      await controller.getProductReviews(mockReq, "prod-123", query);

      expect(service.getProductReviews).toHaveBeenCalledWith(
        "prod-123",
        MOCK_TENANT,
        query,
      );
    });
  });

  describe("getReviewById", () => {
    it("threads tenantId from JWT", async () => {
      mockReviewsService.getReviewById.mockResolvedValue({ id: "r1" });
      await controller.getReviewById(mockReq, "r1");
      expect(service.getReviewById).toHaveBeenCalledWith("r1", MOCK_TENANT);
    });
  });

  describe("getBuyerReviews", () => {
    it("threads tenantId + pagination", async () => {
      const query: PaginationQueryDto = { limit: 10, offset: 0 };
      mockReviewsService.getBuyerReviews.mockResolvedValue([]);

      await controller.getBuyerReviews(mockReq, "buyer-456", query);

      expect(service.getBuyerReviews).toHaveBeenCalledWith(
        "buyer-456",
        MOCK_TENANT,
        10,
        0,
      );
    });
  });

  describe("updateProductReview", () => {
    it("derives ownership from JWT (no URL :buyerId)", async () => {
      const dto: UpdateProductReviewDto = { rating: 5, title: "ممتاز" };
      mockReviewsService.updateProductReview.mockResolvedValue({ id: "r1" });

      await controller.updateProductReview(mockReq, "r1", dto);

      expect(service.updateProductReview).toHaveBeenCalledWith(
        "r1",
        dto,
        MOCK_TENANT,
        MOCK_USER,
      );
    });
  });

  describe("deleteProductReview", () => {
    it("derives ownership from JWT", async () => {
      mockReviewsService.deleteProductReview.mockResolvedValue({
        message: "ok",
      });
      await controller.deleteProductReview(mockReq, "r1");
      expect(service.deleteProductReview).toHaveBeenCalledWith(
        "r1",
        MOCK_TENANT,
        MOCK_USER,
      );
    });
  });

  describe("markReviewHelpful", () => {
    it("threads (id, helpful, tenantId, userId) — audit item #4 regression guard", async () => {
      const dto: MarkReviewHelpfulDto = { helpful: true };
      mockReviewsService.markReviewHelpful.mockResolvedValue({ id: "r1" });
      await controller.markReviewHelpful(mockReq, "r1", dto);
      expect(service.markReviewHelpful).toHaveBeenCalledWith(
        "r1",
        true,
        MOCK_TENANT,
        MOCK_USER,
      );
    });
  });

  describe("reportReview", () => {
    it("threads (id, reason, tenantId, userId) — audit item #5 regression guard", async () => {
      mockReviewsService.reportReview.mockResolvedValue({ id: "r1" });
      await controller.reportReview(mockReq, "r1", {
        reason: "spam",
      } as any);
      expect(service.reportReview).toHaveBeenCalledWith(
        "r1",
        "spam",
        MOCK_TENANT,
        MOCK_USER,
      );
    });
  });

  describe("createReviewResponse", () => {
    it("passes (dto, tenantId, userId) and ignores dto.sellerId", async () => {
      const dto: CreateReviewResponseDto = {
        reviewId: "r1",
        sellerId: "seller-999", // ignored by the service
        response: "شكراً",
      };
      mockReviewsService.createReviewResponse.mockResolvedValue({
        id: "resp1",
      });

      await controller.createReviewResponse(mockReq, dto);

      expect(service.createReviewResponse).toHaveBeenCalledWith(
        dto,
        MOCK_TENANT,
        MOCK_USER,
      );
    });
  });

  describe("getSellerResponses", () => {
    it("threads tenantId + pagination", async () => {
      const query: PaginationQueryDto = { limit: 20, offset: 0 };
      mockReviewsService.getSellerResponses.mockResolvedValue([]);
      await controller.getSellerResponses(mockReq, "seller-789", query);
      expect(service.getSellerResponses).toHaveBeenCalledWith(
        "seller-789",
        MOCK_TENANT,
        20,
        0,
      );
    });
  });

  describe("updateReviewResponse", () => {
    it("derives ownership from JWT", async () => {
      const dto: UpdateReviewResponseDto = { response: "شكراً مرة أخرى" };
      mockReviewsService.updateReviewResponse.mockResolvedValue({
        id: "resp1",
      });
      await controller.updateReviewResponse(mockReq, "resp1", dto);
      expect(service.updateReviewResponse).toHaveBeenCalledWith(
        "resp1",
        dto,
        MOCK_TENANT,
        MOCK_USER,
      );
    });
  });

  describe("deleteReviewResponse", () => {
    it("derives ownership from JWT", async () => {
      mockReviewsService.deleteReviewResponse.mockResolvedValue({
        message: "ok",
      });
      await controller.deleteReviewResponse(mockReq, "resp1");
      expect(service.deleteReviewResponse).toHaveBeenCalledWith(
        "resp1",
        MOCK_TENANT,
        MOCK_USER,
      );
    });
  });
});
