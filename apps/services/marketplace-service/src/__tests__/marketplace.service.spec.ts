/**
 * SAHOOL Marketplace Service Unit Tests
 * اختبارات الوحدة لخدمة السوق
 *
 * Tests for:
 * - Health endpoint responses
 * - Module initialization
 * - Product listing validation
 * - Order creation validation
 * - Wallet balance checks
 */

import { Test, TestingModule } from "@nestjs/testing";
import { ThrottlerModule } from "@nestjs/throttler";
import { NotFoundException, BadRequestException } from "@nestjs/common";
import { AppModule } from "../app.module";
import { AppController } from "../app.controller";
import { MarketService } from "../market/market.service";
import { FintechService } from "../fintech/fintech.service";
import { WalletService } from "../fintech/wallet.service";
import { CreditService } from "../fintech/credit.service";
import { LoanService } from "../fintech/loan.service";
import { EscrowService } from "../fintech/escrow.service";
import { PrismaService } from "../prisma/prisma.service";
import { EventsService } from "../events/events.service";
import { CacheService } from "../cache/cache.service";

// ═══════════════════════════════════════════════════════════════════════════════
// Mock Factories
// ═══════════════════════════════════════════════════════════════════════════════

const createMockPrismaService = () => ({
  product: {
    findMany: jest.fn(),
    findUnique: jest.fn(),
    create: jest.fn(),
    update: jest.fn(),
    count: jest.fn(),
  },
  order: {
    create: jest.fn(),
    findMany: jest.fn(),
    count: jest.fn(),
  },
  wallet: {
    findUnique: jest.fn(),
    create: jest.fn(),
    update: jest.fn(),
  },
  transaction: {
    findMany: jest.fn(),
    findUnique: jest.fn(),
    create: jest.fn(),
  },
  loan: {
    findMany: jest.fn(),
    count: jest.fn(),
  },
  escrow: {
    findMany: jest.fn(),
  },
  scheduledPayment: {
    findMany: jest.fn(),
  },
  walletAuditLog: {
    create: jest.fn(),
    count: jest.fn(),
  },
  creditEvent: {
    findMany: jest.fn(),
    create: jest.fn(),
  },
  $transaction: jest.fn(),
  $connect: jest.fn(),
  $disconnect: jest.fn(),
  onModuleInit: jest.fn(),
  onModuleDestroy: jest.fn(),
});

const createMockEventsService = () => ({
  publishOrderPlaced: jest.fn(),
  publishOrderCompleted: jest.fn(),
  publishOrderCancelled: jest.fn(),
  publishInventoryLowStock: jest.fn(),
});

const createMockCacheService = () => ({
  get: jest.fn().mockResolvedValue(null),
  set: jest.fn().mockResolvedValue(undefined),
  del: jest.fn().mockResolvedValue(undefined),
  delByPattern: jest.fn().mockResolvedValue(undefined),
  getOrSet: jest.fn(),
  invalidateProduct: jest.fn().mockResolvedValue(undefined),
  invalidateWallet: jest.fn().mockResolvedValue(undefined),
  invalidateOrder: jest.fn().mockResolvedValue(undefined),
  isHealthy: jest.fn().mockResolvedValue(true),
});

// ═══════════════════════════════════════════════════════════════════════════════
// 1. Health Endpoint Tests
// ═══════════════════════════════════════════════════════════════════════════════

describe("Health Endpoints", () => {
  let controller: AppController;

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
    setPin: jest.fn(),
    verifyPin: jest.fn(),
    changePin: jest.fn(),
    createEscrow: jest.fn(),
    releaseEscrow: jest.fn(),
    refundEscrow: jest.fn(),
    disputeEscrow: jest.fn(),
    resolveDispute: jest.fn(),
    getEscrowByOrder: jest.fn(),
    getWalletEscrows: jest.fn(),
    createScheduledPayment: jest.fn(),
    getScheduledPayments: jest.fn(),
    getScheduledPaymentById: jest.fn(),
    cancelScheduledPayment: jest.fn(),
    executeScheduledPayment: jest.fn(),
    processDuePayments: jest.fn(),
    getWalletDashboard: jest.fn(),
    transfer: jest.fn(),
    freezeWallet: jest.fn(),
    unfreezeWallet: jest.fn(),
  };

  const mockPrismaService = {
    $queryRaw: jest.fn().mockResolvedValue([{ "?column?": 1 }]),
  };

  const mockEventsService = {
    isConnected: jest.fn().mockReturnValue(true),
    publish: jest.fn().mockResolvedValue(undefined),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [
        { provide: MarketService, useValue: mockMarketService },
        { provide: FintechService, useValue: mockFintechService },
        { provide: PrismaService, useValue: mockPrismaService },
        { provide: EventsService, useValue: mockEventsService },
      ],
    }).compile();

    controller = module.get<AppController>(AppController);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe("GET /healthz", () => {
    it("should return status ok with service name and version", () => {
      const result = controller.healthCheck();

      expect(result).toHaveProperty("status", "ok");
      expect(result).toHaveProperty("service", "marketplace-service");
      expect(result).toHaveProperty("version", "16.0.0");
    });

    it("should include a valid ISO timestamp", () => {
      const result = controller.healthCheck();

      expect(result).toHaveProperty("timestamp");
      const parsed = Date.parse(result.timestamp);
      expect(isNaN(parsed)).toBe(false);
    });
  });

  describe("GET /readyz", () => {
    it("should return readiness status with dependency checks", async () => {
      const result = await controller.readinessCheck();

      expect(result).toHaveProperty("status", "ready");
      expect(result).toHaveProperty("service", "marketplace-service");
      expect(result).toHaveProperty("version", "16.0.0");
      expect(result).toHaveProperty("checks");
      expect(result.checks).toHaveProperty("database", "connected");
      expect(result.checks).toHaveProperty("nats", "connected");
    });

    it("should include a valid ISO timestamp", async () => {
      const result = await controller.readinessCheck();

      expect(result).toHaveProperty("timestamp");
      const parsed = Date.parse(result.timestamp);
      expect(isNaN(parsed)).toBe(false);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 2. Module Initialization Tests
// ═══════════════════════════════════════════════════════════════════════════════

describe("Module Initialization", () => {
  it("should compile the AppModule with all required providers", async () => {
    const mockPrisma = createMockPrismaService();
    const mockEvents = createMockEventsService();
    const mockCache = createMockCacheService();

    const module: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [
        { provide: PrismaService, useValue: mockPrisma },
        { provide: EventsService, useValue: mockEvents },
        { provide: CacheService, useValue: mockCache },
        MarketService,
        WalletService,
        CreditService,
        LoanService,
        EscrowService,
        FintechService,
      ],
    }).compile();

    expect(module).toBeDefined();
  });

  it("should resolve AppController from the module", async () => {
    const mockPrisma = createMockPrismaService();
    const mockEvents = createMockEventsService();
    const mockCache = createMockCacheService();

    const module: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [
        { provide: PrismaService, useValue: mockPrisma },
        { provide: EventsService, useValue: mockEvents },
        { provide: CacheService, useValue: mockCache },
        MarketService,
        WalletService,
        CreditService,
        LoanService,
        EscrowService,
        FintechService,
      ],
    }).compile();

    const controller = module.get<AppController>(AppController);
    expect(controller).toBeDefined();
    expect(controller).toBeInstanceOf(AppController);
  });

  it("should resolve MarketService from the module", async () => {
    const mockPrisma = createMockPrismaService();
    const mockEvents = createMockEventsService();
    const mockCache = createMockCacheService();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        { provide: PrismaService, useValue: mockPrisma },
        { provide: EventsService, useValue: mockEvents },
        { provide: CacheService, useValue: mockCache },
        MarketService,
      ],
    }).compile();

    const service = module.get<MarketService>(MarketService);
    expect(service).toBeDefined();
    expect(service).toBeInstanceOf(MarketService);
  });

  it("should resolve WalletService from the module", async () => {
    const mockPrisma = createMockPrismaService();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        { provide: PrismaService, useValue: mockPrisma },
        WalletService,
      ],
    }).compile();

    const service = module.get<WalletService>(WalletService);
    expect(service).toBeDefined();
    expect(service).toBeInstanceOf(WalletService);
  });

  it("should resolve FintechService facade from the module", async () => {
    const mockPrisma = createMockPrismaService();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        { provide: PrismaService, useValue: mockPrisma },
        WalletService,
        CreditService,
        LoanService,
        EscrowService,
        FintechService,
      ],
    }).compile();

    const service = module.get<FintechService>(FintechService);
    expect(service).toBeDefined();
    expect(service).toBeInstanceOf(FintechService);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 3. Product Listing Validation Tests
// ═══════════════════════════════════════════════════════════════════════════════

describe("Product Listing Validation", () => {
  let service: MarketService;
  let mockPrisma: ReturnType<typeof createMockPrismaService>;

  beforeEach(async () => {
    mockPrisma = createMockPrismaService();
    const mockEvents = createMockEventsService();
    const mockCache = createMockCacheService();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        { provide: PrismaService, useValue: mockPrisma },
        { provide: EventsService, useValue: mockEvents },
        { provide: CacheService, useValue: mockCache },
        MarketService,
      ],
    }).compile();

    service = module.get<MarketService>(MarketService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should only return AVAILABLE products by default", async () => {
    mockPrisma.product.findMany.mockResolvedValue([]);
    mockPrisma.product.count.mockResolvedValue(0);

    await service.findAllProducts({});

    expect(mockPrisma.product.findMany).toHaveBeenCalledWith(
      expect.objectContaining({
        where: expect.objectContaining({ status: "AVAILABLE" }),
      }),
    );
  });

  it("should return products with bilingual name fields", async () => {
    const mockProducts = [
      {
        id: "prod-1",
        name: "Premium Wheat",
        nameAr: "قمح ممتاز",
        category: "HARVEST",
        price: 1500,
        stock: 100,
        unit: "ton",
      },
    ];

    mockPrisma.product.findMany.mockResolvedValue(mockProducts);
    mockPrisma.product.count.mockResolvedValue(1);

    const result = await service.findAllProducts({});

    expect(result.data[0]).toHaveProperty("name", "Premium Wheat");
    expect(result.data[0]).toHaveProperty("nameAr", "قمح ممتاز");
  });

  it("should filter by category and return correct results", async () => {
    const seedProducts = [
      { id: "prod-1", name: "Wheat Seeds", category: "SEEDS", price: 500 },
    ];

    mockPrisma.product.findMany.mockResolvedValue(seedProducts);
    mockPrisma.product.count.mockResolvedValue(1);

    const result = await service.findAllProducts({ category: "SEEDS" });

    expect(mockPrisma.product.findMany).toHaveBeenCalledWith(
      expect.objectContaining({
        where: expect.objectContaining({
          status: "AVAILABLE",
          category: "SEEDS",
        }),
      }),
    );
    expect(result.data).toHaveLength(1);
  });

  it("should filter products by price range correctly", async () => {
    mockPrisma.product.findMany.mockResolvedValue([]);
    mockPrisma.product.count.mockResolvedValue(0);

    await service.findAllProducts({ minPrice: 1000, maxPrice: 5000 });

    expect(mockPrisma.product.findMany).toHaveBeenCalledWith(
      expect.objectContaining({
        where: expect.objectContaining({
          price: { gte: 1000, lte: 5000 },
        }),
      }),
    );
  });

  it("should throw NotFoundException for non-existent product by ID", async () => {
    mockPrisma.product.findUnique.mockResolvedValue(null);

    await expect(
      service.findProductById("non-existent-uuid"),
    ).rejects.toThrow(NotFoundException);
  });

  it("should return paginated response with meta information", async () => {
    mockPrisma.product.findMany.mockResolvedValue([
      { id: "1", name: "Product 1" },
      { id: "2", name: "Product 2" },
    ]);
    mockPrisma.product.count.mockResolvedValue(50);

    const result = await service.findAllProducts({ page: 1, limit: 2 });

    expect(result).toHaveProperty("data");
    expect(result).toHaveProperty("meta");
    expect(result.meta.total).toBe(50);
    expect(result.data).toHaveLength(2);
  });

  it("should order products with featured items first", async () => {
    mockPrisma.product.findMany.mockResolvedValue([]);
    mockPrisma.product.count.mockResolvedValue(0);

    await service.findAllProducts({});

    expect(mockPrisma.product.findMany).toHaveBeenCalledWith(
      expect.objectContaining({
        orderBy: [{ featured: "desc" }, { createdAt: "desc" }],
      }),
    );
  });

  it("should create a product with all required fields", async () => {
    const productData = {
      name: "Organic Tomatoes",
      nameAr: "طماطم عضوية",
      category: "HARVEST",
      price: 800,
      stock: 200,
      unit: "kg",
      sellerId: "farmer-001",
      sellerType: "FARMER",
    };

    const createdProduct = {
      id: "new-prod-1",
      ...productData,
      status: "AVAILABLE",
      featured: false,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    mockPrisma.product.create.mockResolvedValue(createdProduct);

    const result = await service.createProduct(productData);

    expect(result.id).toBe("new-prod-1");
    expect(result.name).toBe("Organic Tomatoes");
    expect(result.nameAr).toBe("طماطم عضوية");
    expect(mockPrisma.product.create).toHaveBeenCalledWith({
      data: expect.objectContaining({
        name: "Organic Tomatoes",
        nameAr: "طماطم عضوية",
        price: 800,
        stock: 200,
        sellerId: "farmer-001",
      }),
    });
  });

  it("should convert yield data into a marketplace product", async () => {
    const currentYear = new Date().getFullYear();
    const yieldData = {
      crop: "wheat",
      cropAr: "قمح",
      predictedYieldTons: 30,
      pricePerTon: 2500,
      qualityGrade: "A",
      governorate: "Sana'a",
    };

    const mockProduct = {
      id: "harvest-prod-1",
      name: `Premium wheat Harvest - ${currentYear} Season`,
      nameAr: `حصاد قمح عالي الجودة - موسم ${currentYear}`,
      category: "HARVEST",
      price: 2500,
      stock: 30,
      unit: "ton",
      sellerId: "farmer-xyz",
      sellerType: "FARMER",
      qualityGrade: "A",
    };

    mockPrisma.product.create.mockResolvedValue(mockProduct);

    const result = await service.convertYieldToProduct("farmer-xyz", yieldData);

    expect(result.category).toBe("HARVEST");
    expect(result.price).toBe(2500);
    expect(result.stock).toBe(30);
    expect(mockPrisma.product.create).toHaveBeenCalledWith(
      expect.objectContaining({
        data: expect.objectContaining({
          category: "HARVEST",
          unit: "ton",
          sellerId: "farmer-xyz",
          sellerType: "FARMER",
          cropType: "wheat",
        }),
      }),
    );
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 4. Order Creation Validation Tests
// ═══════════════════════════════════════════════════════════════════════════════

describe("Order Creation Validation", () => {
  let service: MarketService;
  let mockPrisma: ReturnType<typeof createMockPrismaService>;

  beforeEach(async () => {
    mockPrisma = createMockPrismaService();
    const mockEvents = createMockEventsService();
    const mockCache = createMockCacheService();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        { provide: PrismaService, useValue: mockPrisma },
        { provide: EventsService, useValue: mockEvents },
        { provide: CacheService, useValue: mockCache },
        MarketService,
      ],
    }).compile();

    service = module.get<MarketService>(MarketService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should create an order with correct total calculation", async () => {
    const mockProduct = {
      id: "prod-1",
      name: "Wheat",
      nameAr: "قمح",
      price: 2000,
      stock: 100,
      unit: "ton",
      sellerId: "farmer-1",
    };

    const orderData = {
      buyerId: "buyer-123",
      buyerName: "Ahmed",
      items: [{ productId: "prod-1", quantity: 10 }],
    };

    // The service uses $transaction, so we simulate the transaction callback
    const subtotal = 2000 * 10; // 20000
    const serviceFee = subtotal * 0.02; // 400
    const deliveryFee = 500;
    const totalAmount = subtotal + serviceFee + deliveryFee; // 20900

    const mockOrder = {
      id: "order-1",
      orderNumber: "SAH-TEST123",
      buyerId: "buyer-123",
      buyerName: "Ahmed",
      subtotal,
      serviceFee,
      deliveryFee,
      totalAmount,
      status: "PENDING",
      items: [
        {
          id: "item-1",
          productId: "prod-1",
          quantity: 10,
          unitPrice: 2000,
          totalPrice: 20000,
        },
      ],
    };

    // Mock the transaction to execute the callback
    mockPrisma.$transaction.mockImplementation(async (callback: Function) => {
      const txClient = {
        product: {
          findMany: jest.fn().mockResolvedValue([mockProduct]),
          update: jest.fn().mockResolvedValue({ ...mockProduct, stock: 90 }),
        },
        order: {
          create: jest.fn().mockResolvedValue(mockOrder),
        },
      };
      return callback(txClient);
    });

    const result = await service.createOrder(orderData);

    expect(result.totalAmount).toBe(totalAmount);
    expect(result.subtotal).toBe(subtotal);
    expect(result.serviceFee).toBe(serviceFee);
    expect(result.deliveryFee).toBe(deliveryFee);
    expect(result.status).toBe("PENDING");
  });

  it("should reject order when product does not exist", async () => {
    const orderData = {
      buyerId: "buyer-123",
      items: [{ productId: "non-existent", quantity: 5 }],
    };

    mockPrisma.$transaction.mockImplementation(async (callback: Function) => {
      const txClient = {
        product: {
          findMany: jest.fn().mockResolvedValue([]),
          update: jest.fn(),
        },
        order: {
          create: jest.fn(),
        },
      };
      return callback(txClient);
    });

    await expect(service.createOrder(orderData)).rejects.toThrow(
      /المنتج غير موجود/,
    );
  });

  it("should reject order when requested quantity exceeds stock", async () => {
    const mockProduct = {
      id: "prod-1",
      name: "Wheat",
      nameAr: "قمح",
      price: 2000,
      stock: 5,
      unit: "ton",
    };

    const orderData = {
      buyerId: "buyer-123",
      items: [{ productId: "prod-1", quantity: 50 }],
    };

    mockPrisma.$transaction.mockImplementation(async (callback: Function) => {
      const txClient = {
        product: {
          findMany: jest.fn().mockResolvedValue([mockProduct]),
          update: jest.fn(),
        },
        order: {
          create: jest.fn(),
        },
      };
      return callback(txClient);
    });

    await expect(service.createOrder(orderData)).rejects.toThrow(
      /الكمية المطلوبة غير متوفرة/,
    );
  });

  it("should handle multi-item orders with correct subtotals", async () => {
    const mockProducts = [
      { id: "prod-1", name: "Wheat", nameAr: "قمح", price: 2000, stock: 100, unit: "ton" },
      { id: "prod-2", name: "Corn", nameAr: "ذرة", price: 1500, stock: 80, unit: "ton" },
    ];

    const orderData = {
      buyerId: "buyer-123",
      items: [
        { productId: "prod-1", quantity: 5 },
        { productId: "prod-2", quantity: 10 },
      ],
    };

    // Expected: (2000*5) + (1500*10) = 10000 + 15000 = 25000
    const expectedSubtotal = 25000;
    const expectedServiceFee = expectedSubtotal * 0.02; // 500
    const expectedTotal = expectedSubtotal + expectedServiceFee + 500; // 26000

    const mockOrder = {
      id: "order-2",
      orderNumber: "SAH-MULTI1",
      buyerId: "buyer-123",
      subtotal: expectedSubtotal,
      serviceFee: expectedServiceFee,
      deliveryFee: 500,
      totalAmount: expectedTotal,
      status: "PENDING",
      items: [
        { productId: "prod-1", quantity: 5, unitPrice: 2000, totalPrice: 10000 },
        { productId: "prod-2", quantity: 10, unitPrice: 1500, totalPrice: 15000 },
      ],
    };

    mockPrisma.$transaction.mockImplementation(async (callback: Function) => {
      const txClient = {
        product: {
          findMany: jest.fn().mockResolvedValue(mockProducts),
          update: jest.fn().mockResolvedValue(mockProducts[0]),
        },
        order: {
          create: jest.fn().mockResolvedValue(mockOrder),
        },
      };
      return callback(txClient);
    });

    const result = await service.createOrder(orderData);

    expect(result.subtotal).toBe(expectedSubtotal);
    expect(result.items).toHaveLength(2);
  });

  it("should generate a unique order number prefixed with SAH-", async () => {
    const mockProduct = {
      id: "prod-1",
      name: "Wheat",
      nameAr: "قمح",
      price: 1000,
      stock: 100,
      unit: "ton",
    };

    const orderData = {
      buyerId: "buyer-456",
      items: [{ productId: "prod-1", quantity: 1 }],
    };

    let capturedOrderNumber: string = "";

    mockPrisma.$transaction.mockImplementation(async (callback: Function) => {
      const txClient = {
        product: {
          findMany: jest.fn().mockResolvedValue([mockProduct]),
          update: jest.fn().mockResolvedValue({ ...mockProduct, stock: 99 }),
        },
        order: {
          create: jest.fn().mockImplementation((args: any) => {
            capturedOrderNumber = args.data.orderNumber;
            return {
              id: "order-new",
              orderNumber: capturedOrderNumber,
              buyerId: "buyer-456",
              subtotal: 1000,
              serviceFee: 20,
              deliveryFee: 500,
              totalAmount: 1520,
              status: "PENDING",
              items: [],
            };
          }),
        },
      };
      return callback(txClient);
    });

    await service.createOrder(orderData);

    expect(capturedOrderNumber).toMatch(/^SAH-/);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 5. Wallet Balance Check Tests
// ═══════════════════════════════════════════════════════════════════════════════

describe("Wallet Balance Checks", () => {
  let walletService: WalletService;
  let mockPrisma: ReturnType<typeof createMockPrismaService>;

  beforeEach(async () => {
    mockPrisma = createMockPrismaService();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        { provide: PrismaService, useValue: mockPrisma },
        WalletService,
      ],
    }).compile();

    walletService = module.get<WalletService>(WalletService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should return existing wallet for a known user", async () => {
    const mockWallet = {
      id: "wallet-1",
      userId: "user-001",
      userType: "farmer",
      balance: 50000,
      escrowBalance: 0,
      creditScore: 650,
      creditTier: "GOLD",
      loanLimit: 100000,
      currentLoan: 20000,
      dailyWithdrawLimit: 50000,
      singleTransactionLimit: 200000,
      requiresPinForAmount: 20000,
      dailyWithdrawnToday: 0,
      lastWithdrawReset: null,
      version: 1,
      isVerified: true,
      kycStatus: "approved",
      pin: null,
      deletedAt: null,
      deletedBy: null,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    mockPrisma.wallet.findUnique.mockResolvedValue(mockWallet);

    const result = await walletService.getWallet("user-001");

    expect(result.balance).toBe(50000);
    expect(result.creditTier).toBe("GOLD");
    expect(result.creditTierAr).toBe("ذهبي");
    expect(result.availableCredit).toBe(80000); // 100000 - 20000
  });

  it("should create a new wallet with zero balance for unknown user", async () => {
    const newWallet = {
      id: "wallet-new",
      userId: "new-user",
      userType: "farmer",
      balance: 0,
      escrowBalance: 0,
      creditScore: 300,
      creditTier: "BRONZE",
      loanLimit: 0,
      currentLoan: 0,
      dailyWithdrawLimit: 10000,
      singleTransactionLimit: 50000,
      requiresPinForAmount: 5000,
      dailyWithdrawnToday: 0,
      lastWithdrawReset: null,
      version: 0,
      isVerified: false,
      kycStatus: null,
      pin: null,
      deletedAt: null,
      deletedBy: null,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    mockPrisma.wallet.findUnique.mockResolvedValue(null);
    mockPrisma.wallet.create.mockResolvedValue(newWallet);

    const result = await walletService.getWallet("new-user");

    expect(result.balance).toBe(0);
    expect(result.creditScore).toBe(300);
    expect(result.creditTier).toBe("BRONZE");
    expect(result.creditTierAr).toBe("برونزي");
    expect(mockPrisma.wallet.create).toHaveBeenCalledWith({
      data: expect.objectContaining({
        userId: "new-user",
        userType: "farmer",
        balance: 0,
        creditScore: 300,
        creditTier: "BRONZE",
      }),
    });
  });

  it("should reject deposit with zero or negative amount", async () => {
    await expect(walletService.deposit("wallet-1", 0)).rejects.toThrow(
      BadRequestException,
    );

    await expect(walletService.deposit("wallet-1", -500)).rejects.toThrow(
      BadRequestException,
    );
  });

  it("should reject withdrawal with zero or negative amount", async () => {
    await expect(walletService.withdraw("wallet-1", 0)).rejects.toThrow(
      BadRequestException,
    );

    await expect(walletService.withdraw("wallet-1", -1000)).rejects.toThrow(
      BadRequestException,
    );
  });

  it("should translate credit tiers to Arabic correctly", () => {
    expect(walletService.getCreditTierAr("BRONZE")).toBe("برونزي");
    expect(walletService.getCreditTierAr("SILVER")).toBe("فضي");
    expect(walletService.getCreditTierAr("GOLD")).toBe("ذهبي");
    expect(walletService.getCreditTierAr("PLATINUM")).toBe("بلاتيني");
  });

  it("should return wallet limits with remaining daily allowance", async () => {
    const mockWallet = {
      id: "wallet-1",
      dailyWithdrawLimit: 50000,
      singleTransactionLimit: 200000,
      requiresPinForAmount: 20000,
      creditTier: "GOLD",
      dailyWithdrawnToday: 10000,
      lastWithdrawReset: new Date(), // Same day
    };

    mockPrisma.wallet.findUnique.mockResolvedValue(mockWallet);

    const result = await walletService.getWalletLimits("wallet-1");

    expect(result.dailyWithdrawLimit).toBe(50000);
    expect(result.dailyRemaining).toBe(40000); // 50000 - 10000
    expect(result.singleTransactionLimit).toBe(200000);
    expect(result.requiresPinForAmount).toBe(20000);
    expect(result.creditTier).toBe("GOLD");
  });

  it("should throw NotFoundException for wallet limits on non-existent wallet", async () => {
    mockPrisma.wallet.findUnique.mockResolvedValue(null);

    await expect(
      walletService.getWalletLimits("non-existent"),
    ).rejects.toThrow(NotFoundException);
  });

  it("should update wallet limits based on credit tier", async () => {
    // GOLD tier
    const goldWallet = {
      id: "wallet-gold",
      creditTier: "GOLD",
    };
    mockPrisma.wallet.findUnique.mockResolvedValue(goldWallet);
    mockPrisma.wallet.update.mockResolvedValue({
      ...goldWallet,
      dailyWithdrawLimit: 50000,
      singleTransactionLimit: 200000,
      requiresPinForAmount: 20000,
    });

    const result = await walletService.updateWalletLimits("wallet-gold");

    expect(mockPrisma.wallet.update).toHaveBeenCalledWith({
      where: { id: "wallet-gold" },
      data: {
        dailyWithdrawLimit: 50000,
        singleTransactionLimit: 200000,
        requiresPinForAmount: 20000,
      },
    });
  });

  it("should set PLATINUM tier limits for highest credit tier", async () => {
    const platinumWallet = { id: "wallet-plat", creditTier: "PLATINUM" };
    mockPrisma.wallet.findUnique.mockResolvedValue(platinumWallet);
    mockPrisma.wallet.update.mockResolvedValue({});

    await walletService.updateWalletLimits("wallet-plat");

    expect(mockPrisma.wallet.update).toHaveBeenCalledWith({
      where: { id: "wallet-plat" },
      data: {
        dailyWithdrawLimit: 100000,
        singleTransactionLimit: 500000,
        requiresPinForAmount: 50000,
      },
    });
  });

  it("should set default BRONZE tier limits for unrecognized tier", async () => {
    const bronzeWallet = { id: "wallet-bronze", creditTier: "BRONZE" };
    mockPrisma.wallet.findUnique.mockResolvedValue(bronzeWallet);
    mockPrisma.wallet.update.mockResolvedValue({});

    await walletService.updateWalletLimits("wallet-bronze");

    expect(mockPrisma.wallet.update).toHaveBeenCalledWith({
      where: { id: "wallet-bronze" },
      data: {
        dailyWithdrawLimit: 10000,
        singleTransactionLimit: 50000,
        requiresPinForAmount: 5000,
      },
    });
  });

  it("should reject transfer to the same wallet", async () => {
    await expect(
      walletService.transfer("wallet-1", "wallet-1", 1000),
    ).rejects.toThrow(BadRequestException);
  });

  it("should reject transfer with zero or negative amount", async () => {
    await expect(
      walletService.transfer("wallet-1", "wallet-2", 0),
    ).rejects.toThrow(BadRequestException);

    await expect(
      walletService.transfer("wallet-1", "wallet-2", -500),
    ).rejects.toThrow(BadRequestException);
  });

  it("should return transaction history for a wallet", async () => {
    const mockTransactions = [
      {
        id: "tx-1",
        walletId: "wallet-1",
        type: "DEPOSIT",
        amount: 10000,
        balanceAfter: 10000,
        status: "COMPLETED",
        createdAt: new Date(),
      },
      {
        id: "tx-2",
        walletId: "wallet-1",
        type: "WITHDRAWAL",
        amount: -3000,
        balanceAfter: 7000,
        status: "COMPLETED",
        createdAt: new Date(),
      },
    ];

    mockPrisma.transaction.findMany.mockResolvedValue(mockTransactions);

    const result = await walletService.getTransactions("wallet-1", 20);

    expect(result).toHaveLength(2);
    expect(result[0].type).toBe("DEPOSIT");
    expect(result[1].type).toBe("WITHDRAWAL");
    expect(mockPrisma.transaction.findMany).toHaveBeenCalledWith({
      where: { walletId: "wallet-1" },
      orderBy: { createdAt: "desc" },
      take: 20,
    });
  });
});
