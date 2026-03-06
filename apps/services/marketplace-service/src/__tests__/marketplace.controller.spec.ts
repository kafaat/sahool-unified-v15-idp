/**
 * SAHOOL Marketplace Controller Tests
 * اختبارات وحدة التحكم في السوق
 *
 * Tests API endpoints for:
 * - Product CRUD operations
 * - Order management
 * - Market statistics
 * - Health checks
 */

import { Test, TestingModule } from "@nestjs/testing";
import { AppController } from "../app.controller";
import { MarketService } from "../market/market.service";
import { FintechService } from "../fintech/fintech.service";
import { ForbiddenException } from "@nestjs/common";

describe("AppController (Marketplace)", () => {
  let controller: AppController;
  let marketService: MarketService;
  let fintechService: FintechService;

  const mockMarketService = {
    findAllProducts: jest.fn(),
    findProductById: jest.fn(),
    createProduct: jest.fn(),
    convertYieldToProduct: jest.fn(),
    createOrder: jest.fn(),
    getUserOrders: jest.fn(),
    getMarketStats: jest.fn(),
  };

  const mockFintechService = {
    getWallet: jest.fn(),
    deposit: jest.fn(),
    withdraw: jest.fn(),
    getTransactions: jest.fn(),
    calculateCreditScore: jest.fn(),
    calculateAdvancedCreditScore: jest.fn(),
    getCreditFactors: jest.fn(),
    recordCreditEvent: jest.fn(),
    getCreditReport: jest.fn(),
    requestLoan: jest.fn(),
    approveLoan: jest.fn(),
    repayLoan: jest.fn(),
    getUserLoans: jest.fn(),
    getFinanceStats: jest.fn(),
    getWalletLimits: jest.fn(),
    updateWalletLimits: jest.fn(),
    getWalletById: jest.fn(),
    createEscrow: jest.fn(),
    releaseEscrow: jest.fn(),
    refundEscrow: jest.fn(),
    getEscrowByOrder: jest.fn(),
    getWalletEscrows: jest.fn(),
    createScheduledPayment: jest.fn(),
    getScheduledPayments: jest.fn(),
    cancelScheduledPayment: jest.fn(),
    executeScheduledPayment: jest.fn(),
    getWalletDashboard: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [
        {
          provide: MarketService,
          useValue: mockMarketService,
        },
        {
          provide: FintechService,
          useValue: mockFintechService,
        },
      ],
    }).compile();

    controller = module.get<AppController>(AppController);
    marketService = module.get<MarketService>(MarketService);
    fintechService = module.get<FintechService>(FintechService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Check Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe("GET /healthz", () => {
    it("should return health status", () => {
      const result = controller.healthCheck();

      expect(result).toHaveProperty("status", "ok");
      expect(result).toHaveProperty("service", "marketplace-service");
      expect(result).toHaveProperty("version");
      expect(result).toHaveProperty("timestamp");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Product API Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe("GET /market/products", () => {
    it("should return all products", async () => {
      const mockProducts = {
        data: [
          {
            id: "1",
            name: "Premium Wheat",
            nameAr: "قمح ممتاز",
            price: 1500,
            stock: 100,
            category: "HARVEST",
          },
          {
            id: "2",
            name: "Organic Corn",
            nameAr: "ذرة عضوية",
            price: 1200,
            stock: 80,
            category: "HARVEST",
          },
        ],
        total: 2,
        page: 1,
        pageSize: 10,
        totalPages: 1,
      };

      mockMarketService.findAllProducts.mockResolvedValue(mockProducts);

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      const result = await controller.getProducts(mockReq);

      expect(result).toEqual(mockProducts);
      expect(mockMarketService.findAllProducts).toHaveBeenCalledWith(
        expect.objectContaining({}),
      );
    });

    it("should filter products by category", async () => {
      const mockProducts = {
        data: [],
        total: 0,
        page: 1,
        pageSize: 10,
        totalPages: 0,
      };

      mockMarketService.findAllProducts.mockResolvedValue(mockProducts);

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      await controller.getProducts(mockReq, "HARVEST");

      expect(mockMarketService.findAllProducts).toHaveBeenCalledWith(
        expect.objectContaining({ category: "HARVEST" }),
      );
    });

    it("should filter products by governorate", async () => {
      const mockProducts = {
        data: [],
        total: 0,
        page: 1,
        pageSize: 10,
        totalPages: 0,
      };

      mockMarketService.findAllProducts.mockResolvedValue(mockProducts);

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      await controller.getProducts(mockReq, undefined, "Sana'a");

      expect(mockMarketService.findAllProducts).toHaveBeenCalledWith(
        expect.objectContaining({ governorate: "Sana'a" }),
      );
    });

    it("should filter products by seller ID", async () => {
      const mockProducts = {
        data: [],
        total: 0,
        page: 1,
        pageSize: 10,
        totalPages: 0,
      };

      mockMarketService.findAllProducts.mockResolvedValue(mockProducts);

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      await controller.getProducts(mockReq, undefined, undefined, "seller-123");

      expect(mockMarketService.findAllProducts).toHaveBeenCalledWith(
        expect.objectContaining({ sellerId: "seller-123" }),
      );
    });

    it("should filter products by price range", async () => {
      const mockProducts = {
        data: [],
        total: 0,
        page: 1,
        pageSize: 10,
        totalPages: 0,
      };

      mockMarketService.findAllProducts.mockResolvedValue(mockProducts);

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      await controller.getProducts(
        mockReq,
        undefined,
        undefined,
        undefined,
        "500",
        "2000",
      );

      expect(mockMarketService.findAllProducts).toHaveBeenCalledWith(
        expect.objectContaining({
          minPrice: 500,
          maxPrice: 2000,
        }),
      );
    });
  });

  describe("GET /market/products/:id", () => {
    it("should return a single product by ID", async () => {
      const mockProduct = {
        id: "1",
        name: "Premium Wheat",
        nameAr: "قمح ممتاز",
        price: 1500,
        stock: 100,
        category: "HARVEST",
      };

      mockMarketService.findProductById.mockResolvedValue(mockProduct);

      const result = await controller.getProduct("1");

      expect(result).toEqual(mockProduct);
      expect(mockMarketService.findProductById).toHaveBeenCalledWith("1");
    });

    it("should handle product not found", async () => {
      mockMarketService.findProductById.mockRejectedValue(
        new Error("المنتج غير موجود"),
      );

      await expect(controller.getProduct("999")).rejects.toThrow(
        "المنتج غير موجود",
      );
    });
  });

  describe("POST /market/products", () => {
    it("should create a new product", async () => {
      const createProductDto = {
        name: "Premium Wheat",
        nameAr: "قمح ممتاز",
        category: "HARVEST",
        price: 1500,
        stock: 100,
        unit: "ton",
        sellerId: "user-123",
        sellerType: "FARMER",
        description: "High quality wheat",
        descriptionAr: "قمح عالي الجودة",
      };

      const mockCreatedProduct = {
        id: "1",
        ...createProductDto,
        status: "AVAILABLE",
        featured: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      mockMarketService.createProduct.mockResolvedValue(mockCreatedProduct);

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      const result = await controller.createProduct(mockReq, createProductDto);

      expect(result).toEqual(mockCreatedProduct);
      expect(mockMarketService.createProduct).toHaveBeenCalledWith(
        createProductDto,
        "tenant-1",
      );
    });

    it("should validate product data", async () => {
      const invalidProductDto = {
        name: "",
        nameAr: "",
        category: "INVALID",
        price: -100,
        stock: -10,
        unit: "",
        sellerId: "",
        sellerType: "",
      };

      mockMarketService.createProduct.mockRejectedValue(
        new Error("Validation failed"),
      );

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      await expect(
        controller.createProduct(mockReq, invalidProductDto as any),
      ).rejects.toThrow();
    });
  });

  describe("POST /market/list-harvest", () => {
    it("should convert yield prediction to product", async () => {
      const listHarvestDto = {
        userId: "farmer-123",
        yieldData: {
          crop: "wheat",
          cropAr: "قمح",
          predictedYieldTons: 50,
          pricePerTon: 2000,
          harvestDate: "2024-06-15",
          qualityGrade: "A",
          governorate: "Sana'a",
          district: "Bani Harith",
        },
      };

      const mockProduct = {
        id: "1",
        name: "Premium wheat Harvest - 2024 Season",
        nameAr: "حصاد قمح عالي الجودة - موسم 2024",
        category: "HARVEST",
        price: 2000,
        stock: 50,
        unit: "ton",
        sellerId: "farmer-123",
        sellerType: "FARMER",
        cropType: "wheat",
        harvestDate: new Date("2024-06-15"),
        qualityGrade: "A",
        governorate: "Sana'a",
        district: "Bani Harith",
      };

      mockMarketService.convertYieldToProduct.mockResolvedValue(mockProduct);

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      const result = await controller.listHarvest(mockReq, listHarvestDto);

      expect(result).toEqual(mockProduct);
      expect(mockMarketService.convertYieldToProduct).toHaveBeenCalledWith(
        "farmer-123",
        listHarvestDto.yieldData,
        "tenant-1",
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Order API Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe("POST /market/orders", () => {
    it("should create a new order", async () => {
      const createOrderDto = {
        buyerId: "buyer-123",
        buyerName: "Ahmed Ali",
        buyerPhone: "+967771234567",
        items: [
          { productId: "product-1", quantity: 2 },
          { productId: "product-2", quantity: 5 },
        ],
        deliveryAddress: "Sana'a, Bani Harith Street",
        paymentMethod: "WALLET",
      };

      const mockOrder = {
        id: "order-1",
        orderNumber: "SAH-ABC123",
        buyerId: "buyer-123",
        buyerName: "Ahmed Ali",
        buyerPhone: "+967771234567",
        status: "PENDING",
        subtotal: 10000,
        serviceFee: 200,
        deliveryFee: 500,
        totalAmount: 10700,
        deliveryAddress: "Sana'a, Bani Harith Street",
        paymentMethod: "WALLET",
        items: [
          {
            id: "item-1",
            productId: "product-1",
            quantity: 2,
            unitPrice: 2000,
            totalPrice: 4000,
          },
          {
            id: "item-2",
            productId: "product-2",
            quantity: 5,
            unitPrice: 1200,
            totalPrice: 6000,
          },
        ],
        createdAt: new Date(),
      };

      mockMarketService.createOrder.mockResolvedValue(mockOrder);

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      const result = await controller.createOrder(mockReq, createOrderDto);

      expect(result).toEqual(mockOrder);
      expect(mockMarketService.createOrder).toHaveBeenCalledWith(
        createOrderDto,
        'tenant-1',
      );
    });

    it("should handle insufficient stock error", async () => {
      const createOrderDto = {
        buyerId: "buyer-123",
        items: [{ productId: "product-1", quantity: 1000 }],
      };

      mockMarketService.createOrder.mockRejectedValue(
        new Error("الكمية المطلوبة غير متوفرة للمنتج"),
      );

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      await expect(
        controller.createOrder(mockReq, createOrderDto as any),
      ).rejects.toThrow("الكمية المطلوبة غير متوفرة للمنتج");
    });

    it("should handle product not found error", async () => {
      const createOrderDto = {
        buyerId: "buyer-123",
        items: [{ productId: "non-existent", quantity: 1 }],
      };

      mockMarketService.createOrder.mockRejectedValue(
        new Error("المنتج غير موجود"),
      );

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      await expect(
        controller.createOrder(mockReq, createOrderDto as any),
      ).rejects.toThrow("المنتج غير موجود");
    });
  });

  describe("GET /market/orders/:userId", () => {
    it("should return buyer orders for authorized user", async () => {
      const userId = "buyer-123";
      const mockRequest = {
        user: { id: userId, roles: ["user"] },
      };

      const mockOrders = {
        data: [
          {
            id: "order-1",
            orderNumber: "SAH-ABC123",
            status: "PENDING",
            totalAmount: 10700,
            createdAt: new Date(),
          },
        ],
        total: 1,
        page: 1,
        pageSize: 10,
        totalPages: 1,
      };

      mockMarketService.getUserOrders.mockResolvedValue(mockOrders);

      const result = await controller.getUserOrders(
        mockRequest,
        userId,
        "buyer",
      );

      expect(result).toEqual(mockOrders);
      expect(mockMarketService.getUserOrders).toHaveBeenCalledWith(
        userId,
        "buyer",
      );
    });

    it("should return seller orders for authorized user", async () => {
      const userId = "seller-123";
      const mockRequest = {
        user: { id: userId, roles: ["user"] },
      };

      const mockOrders = {
        data: [
          {
            id: "order-2",
            orderNumber: "SAH-XYZ789",
            status: "COMPLETED",
            totalAmount: 5000,
            createdAt: new Date(),
          },
        ],
        total: 1,
        page: 1,
        pageSize: 10,
        totalPages: 1,
      };

      mockMarketService.getUserOrders.mockResolvedValue(mockOrders);

      const result = await controller.getUserOrders(
        mockRequest,
        userId,
        "seller",
      );

      expect(result).toEqual(mockOrders);
      expect(mockMarketService.getUserOrders).toHaveBeenCalledWith(
        userId,
        "seller",
      );
    });

    it("should allow admin to access any user orders", async () => {
      const userId = "buyer-123";
      const mockRequest = {
        user: { id: "admin-456", roles: ["admin"] },
      };

      const mockOrders = {
        data: [],
        total: 0,
        page: 1,
        pageSize: 10,
        totalPages: 0,
      };

      mockMarketService.getUserOrders.mockResolvedValue(mockOrders);

      const result = await controller.getUserOrders(
        mockRequest,
        userId,
        "buyer",
      );

      expect(result).toEqual(mockOrders);
      expect(mockMarketService.getUserOrders).toHaveBeenCalledWith(
        userId,
        "buyer",
      );
    });

    it("should throw ForbiddenException for unauthorized access", async () => {
      const userId = "buyer-123";
      const mockRequest = {
        user: { id: "other-user-456", roles: ["user"] },
      };

      await expect(
        controller.getUserOrders(mockRequest, userId, "buyer"),
      ).rejects.toThrow(ForbiddenException);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Statistics API Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe("GET /market/stats", () => {
    it("should return market statistics", async () => {
      const mockStats = {
        totalProducts: 150,
        totalHarvests: 45,
        totalOrders: 320,
        recentProducts: [
          {
            id: "1",
            name: "Premium Wheat",
            price: 1500,
            createdAt: new Date(),
          },
          {
            id: "2",
            name: "Organic Corn",
            price: 1200,
            createdAt: new Date(),
          },
        ],
      };

      mockMarketService.getMarketStats.mockResolvedValue(mockStats);

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      const result = await controller.getMarketStats(mockReq);

      expect(result).toEqual(expect.objectContaining(mockStats));
      expect(mockMarketService.getMarketStats).toHaveBeenCalled();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Integration Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe("Integration: Product to Order Flow", () => {
    it("should create product and then create order for it", async () => {
      // Step 1: Create product
      const createProductDto = {
        name: "Premium Wheat",
        nameAr: "قمح ممتاز",
        category: "HARVEST",
        price: 1500,
        stock: 100,
        unit: "ton",
        sellerId: "farmer-123",
        sellerType: "FARMER",
      };

      const mockProduct = {
        id: "product-1",
        ...createProductDto,
        status: "AVAILABLE",
        featured: false,
        createdAt: new Date(),
      };

      mockMarketService.createProduct.mockResolvedValue(mockProduct);

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      const product = await controller.createProduct(mockReq, createProductDto);
      expect(product.id).toBe("product-1");

      // Step 2: Create order for the product
      const createOrderDto = {
        buyerId: "buyer-123",
        items: [{ productId: "product-1", quantity: 10 }],
      };

      const mockOrder = {
        id: "order-1",
        orderNumber: "SAH-ABC123",
        buyerId: "buyer-123",
        totalAmount: 15000,
        items: [
          {
            productId: "product-1",
            quantity: 10,
            unitPrice: 1500,
            totalPrice: 15000,
          },
        ],
      };

      mockMarketService.createOrder.mockResolvedValue(mockOrder);

      const order = await controller.createOrder(mockReq, createOrderDto as any);
      expect(order.totalAmount).toBe(15000);
      expect(order.items[0].productId).toBe("product-1");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Error Handling Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe("Error Handling", () => {
    it("should handle database connection errors gracefully", async () => {
      mockMarketService.findAllProducts.mockRejectedValue(
        new Error("Database connection failed"),
      );

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      await expect(controller.getProducts(mockReq)).rejects.toThrow(
        "Database connection failed",
      );
    });

    it("should handle validation errors", async () => {
      const invalidDto = {
        name: "",
        price: -100,
      };

      mockMarketService.createProduct.mockRejectedValue(
        new Error("Validation failed"),
      );

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      await expect(controller.createProduct(mockReq, invalidDto as any)).rejects.toThrow(
        "Validation failed",
      );
    });

    it("should handle concurrent order creation", async () => {
      const createOrderDto = {
        buyerId: "buyer-123",
        items: [{ productId: "product-1", quantity: 5 }],
      };

      // Simulate concurrent order attempts causing stock issues
      mockMarketService.createOrder.mockRejectedValue(
        new Error("الكمية المطلوبة غير متوفرة للمنتج"),
      );

      const mockReq = { user: { tenantId: 'tenant-1' }, headers: {} };
      await expect(
        controller.createOrder(mockReq, createOrderDto as any),
      ).rejects.toThrow("الكمية المطلوبة غير متوفرة للمنتج");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Wallet Limits Authorization Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe("PUT /fintech/wallet/:walletId/limits", () => {
    it("should allow wallet owner to update limits", async () => {
      const walletId = "wallet-123";
      const userId = "user-123";
      const mockRequest = {
        user: { id: userId, roles: ["user"] },
      };

      const mockWallet = { id: walletId, userId: userId };
      const mockUpdatedLimits = {
        dailyWithdrawLimit: 20000,
        singleTransactionLimit: 100000,
        requiresPinForAmount: 10000,
      };

      mockFintechService.getWalletById.mockResolvedValue(mockWallet);
      mockFintechService.updateWalletLimits.mockResolvedValue(mockUpdatedLimits);

      const result = await controller.updateWalletLimits(mockRequest, walletId);

      expect(result).toEqual(mockUpdatedLimits);
      expect(mockFintechService.getWalletById).toHaveBeenCalledWith(walletId);
      expect(mockFintechService.updateWalletLimits).toHaveBeenCalledWith(
        walletId,
      );
    });

    it("should allow admin to update any wallet limits", async () => {
      const walletId = "wallet-123";
      const mockRequest = {
        user: { id: "admin-456", roles: ["admin"] },
      };

      const mockWallet = { id: walletId, userId: "user-123" };
      const mockUpdatedLimits = {
        dailyWithdrawLimit: 50000,
        singleTransactionLimit: 200000,
        requiresPinForAmount: 20000,
      };

      mockFintechService.getWalletById.mockResolvedValue(mockWallet);
      mockFintechService.updateWalletLimits.mockResolvedValue(mockUpdatedLimits);

      const result = await controller.updateWalletLimits(mockRequest, walletId);

      expect(result).toEqual(mockUpdatedLimits);
      expect(mockFintechService.updateWalletLimits).toHaveBeenCalledWith(
        walletId,
      );
    });

    it("should throw ForbiddenException for non-owner non-admin", async () => {
      const walletId = "wallet-123";
      const mockRequest = {
        user: { id: "other-user-456", roles: ["user"] },
      };

      const mockWallet = { id: walletId, userId: "user-123" };
      mockFintechService.getWalletById.mockResolvedValue(mockWallet);

      await expect(
        controller.updateWalletLimits(mockRequest, walletId),
      ).rejects.toThrow(ForbiddenException);
    });

    it("should throw ForbiddenException when wallet not found", async () => {
      const walletId = "non-existent-wallet";
      const mockRequest = {
        user: { id: "user-123", roles: ["user"] },
      };

      mockFintechService.getWalletById.mockResolvedValue(null);

      await expect(
        controller.updateWalletLimits(mockRequest, walletId),
      ).rejects.toThrow(ForbiddenException);
    });
  });
});
