/**
 * SAHOOL Credit Service Tests
 * اختبارات خدمة التصنيف الائتماني
 */

import { Test, TestingModule } from "@nestjs/testing";
import { CreditService, FarmData, CreditFactors } from "./credit.service";
import { PrismaService } from "../prisma/prisma.service";
import { NotFoundException } from "@nestjs/common";

describe("CreditService", () => {
  let service: CreditService;
  let prismaService: PrismaService;

  const mockPrismaService = {
    wallet: {
      findUnique: jest.fn(),
      upsert: jest.fn(),
      update: jest.fn(),
    },
    creditEvent: {
      create: jest.fn(),
    },
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        CreditService,
        {
          provide: PrismaService,
          useValue: mockPrismaService,
        },
      ],
    }).compile();

    service = module.get<CreditService>(CreditService);
    prismaService = module.get<PrismaService>(PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe("getCreditTierAr", () => {
    it("should translate credit tiers to Arabic", () => {
      expect(service.getCreditTierAr("BRONZE")).toBe("برونزي");
      expect(service.getCreditTierAr("SILVER")).toBe("فضي");
      expect(service.getCreditTierAr("GOLD")).toBe("ذهبي");
      expect(service.getCreditTierAr("PLATINUM")).toBe("بلاتيني");
    });
  });

  describe("calculateCreditScore", () => {
    it("should calculate PLATINUM tier for excellent farm data", async () => {
      const farmData: FarmData = {
        totalArea: 15,
        activeSeasons: 6,
        fieldCount: 5,
        diseaseRisk: "Low",
        irrigationType: "drip",
        avgYieldScore: 90,
        onTimePayments: 20,
        latePayments: 0,
      };

      const mockWallet = {
        id: "wallet-1",
        userId: "user-123",
        creditScore: 800,
        creditTier: "PLATINUM",
        loanLimit: 40000,
        currentLoan: 0,
      };

      mockPrismaService.wallet.upsert.mockResolvedValue(mockWallet);

      const result = await service.calculateCreditScore("user-123", farmData);

      expect(result.wallet.creditTier).toBe("PLATINUM");
      expect(result.creditTierAr).toBe("بلاتيني");
      expect(result.message).toContain("تهانينا");
    });

    it("should calculate GOLD tier for good farm data", async () => {
      const farmData: FarmData = {
        totalArea: 8,
        activeSeasons: 4,
        fieldCount: 3,
        diseaseRisk: "Low",
        irrigationType: "sprinkler",
        avgYieldScore: 70,
        onTimePayments: 15,
        latePayments: 2,
      };

      const mockWallet = {
        id: "wallet-1",
        creditScore: 700,
        creditTier: "GOLD",
        loanLimit: 24500,
        currentLoan: 0,
      };

      mockPrismaService.wallet.upsert.mockResolvedValue(mockWallet);

      const result = await service.calculateCreditScore("user-123", farmData);

      expect(result.wallet.creditTier).toBe("GOLD");
      expect(result.message).toContain("تهانينا");
    });

    it("should calculate SILVER tier for average farm data", async () => {
      const farmData: FarmData = {
        totalArea: 3,
        activeSeasons: 2,
        fieldCount: 2,
        diseaseRisk: "Medium",
        irrigationType: "flood",
        avgYieldScore: 50,
        onTimePayments: 5,
        latePayments: 2,
      };

      const mockWallet = {
        id: "wallet-1",
        creditScore: 550,
        creditTier: "SILVER",
        loanLimit: 11000,
        currentLoan: 0,
      };

      mockPrismaService.wallet.upsert.mockResolvedValue(mockWallet);

      const result = await service.calculateCreditScore("user-123", farmData);

      expect(result.wallet.creditTier).toBe("SILVER");
      expect(result.message).toContain("جيد");
    });

    it("should calculate BRONZE tier for poor farm data", async () => {
      const farmData: FarmData = {
        totalArea: 1,
        activeSeasons: 1,
        fieldCount: 1,
        diseaseRisk: "High",
        irrigationType: "",
        avgYieldScore: 20,
        onTimePayments: 1,
        latePayments: 5,
      };

      const mockWallet = {
        id: "wallet-1",
        creditScore: 350,
        creditTier: "BRONZE",
        loanLimit: 3500,
        currentLoan: 0,
      };

      mockPrismaService.wallet.upsert.mockResolvedValue(mockWallet);

      const result = await service.calculateCreditScore("user-123", farmData);

      expect(result.wallet.creditTier).toBe("BRONZE");
      expect(result.message).toContain("ننصحك");
    });
  });

  describe("calculateAdvancedCreditScore", () => {
    it("should calculate advanced score with all factors", async () => {
      const factors: CreditFactors = {
        farmArea: 10,
        numberOfSeasons: 5,
        diseaseRiskScore: 90,
        irrigationType: "drip",
        yieldScore: 85,
        paymentHistory: 95,
        cropDiversity: 8,
        marketplaceHistory: 50,
        loanRepaymentRate: 100,
        verificationLevel: "premium",
        landOwnership: "owned",
        cooperativeMember: true,
        yearsOfExperience: 12,
        satelliteVerified: true,
      };

      const mockWallet = {
        id: "wallet-1",
        creditScore: 850,
        creditTier: "PLATINUM",
        loanLimit: 42500,
        currentLoan: 0,
      };

      mockPrismaService.wallet.upsert.mockResolvedValue(mockWallet);

      const result = await service.calculateAdvancedCreditScore(
        "user-123",
        factors,
      );

      expect(result.creditTier).toBe("PLATINUM");
      expect(result.breakdown).toBeDefined();
      expect(result.breakdown.farmDataScore).toBeGreaterThan(0);
      expect(result.breakdown.paymentHistoryScore).toBeGreaterThan(0);
      expect(result.breakdown.verificationScore).toBeGreaterThan(0);
      expect(result.breakdown.bonusScore).toBeGreaterThan(0);
    });
  });

  describe("getCreditFactors", () => {
    it("should return credit factors for user", async () => {
      const mockWallet = {
        id: "wallet-1",
        userId: "user-123",
        isVerified: true,
        loans: [{ status: "PAID" }, { status: "PAID" }, { status: "ACTIVE" }],
        creditEvents: [
          { eventType: "ORDER_COMPLETED" },
          { eventType: "ORDER_COMPLETED" },
          { eventType: "FARM_VERIFIED" },
        ],
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      const result = await service.getCreditFactors("user-123");

      expect(result.marketplaceHistory).toBe(2);
      expect(result.satelliteVerified).toBe(true);
      expect(result.loanRepaymentRate).toBeCloseTo(66.67, 1);
    });

    it("should throw error for non-existent wallet", async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);

      await expect(service.getCreditFactors("user-999")).rejects.toThrow(
        NotFoundException,
      );
    });
  });

  describe("recordCreditEvent", () => {
    it("should record positive credit event and update score", async () => {
      const mockWallet = {
        id: "wallet-1",
        creditScore: 600,
        creditTier: "SILVER",
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      const mockEvent = {
        id: "event-1",
        eventType: "LOAN_REPAID_ONTIME",
        impact: 15,
      };

      mockPrismaService.creditEvent.create.mockResolvedValue(mockEvent);

      const updatedWallet = {
        ...mockWallet,
        creditScore: 615,
        creditTier: "SILVER",
      };

      mockPrismaService.wallet.update.mockResolvedValue(updatedWallet);

      const result = await service.recordCreditEvent({
        walletId: "wallet-1",
        eventType: "LOAN_REPAID_ONTIME",
        amount: 5000,
        description: "قرض مسدد في الوقت",
      });

      expect(result.impact).toBe(15);
      expect(result.message).toContain("ارتفع");
    });

    it("should record negative credit event and update score", async () => {
      const mockWallet = {
        id: "wallet-1",
        creditScore: 500,
        creditTier: "SILVER",
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      const mockEvent = {
        id: "event-1",
        eventType: "LOAN_DEFAULTED",
        impact: -50,
      };

      mockPrismaService.creditEvent.create.mockResolvedValue(mockEvent);

      const updatedWallet = {
        ...mockWallet,
        creditScore: 450,
        creditTier: "BRONZE",
      };

      mockPrismaService.wallet.update.mockResolvedValue(updatedWallet);

      const result = await service.recordCreditEvent({
        walletId: "wallet-1",
        eventType: "LOAN_DEFAULTED",
        description: "قرض متعثر",
      });

      expect(result.impact).toBe(-50);
      expect(result.message).toContain("انخفض");
    });

    it("should throw error for non-existent wallet", async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);

      await expect(
        service.recordCreditEvent({
          walletId: "wallet-999",
          eventType: "ORDER_COMPLETED",
          description: "Test",
        }),
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe("getCreditReport", () => {
    it("should generate comprehensive credit report", async () => {
      const mockWallet = {
        id: "wallet-1",
        userId: "user-123",
        creditScore: 700,
        creditTier: "GOLD",
        loanLimit: 24500,
        currentLoan: 5000,
        isVerified: true,
        loans: [{ status: "PAID" }, { status: "ACTIVE" }],
        creditEvents: [
          { eventType: "ORDER_COMPLETED", createdAt: new Date() },
          { eventType: "FARM_VERIFIED", createdAt: new Date() },
        ],
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      const result = await service.getCreditReport("user-123");

      expect(result.currentScore).toBe(700);
      expect(result.creditTier).toBe("ذهبي");
      expect(result.riskLevel).toBe("low");
      expect(result.availableCredit).toBe(19500);
      expect(result.recommendations).toBeDefined();
      expect(Array.isArray(result.recommendations)).toBe(true);
    });

    it("should identify high risk level for low scores", async () => {
      const mockWallet = {
        id: "wallet-1",
        userId: "user-123",
        creditScore: 400,
        creditTier: "BRONZE",
        loanLimit: 4000,
        currentLoan: 0,
        isVerified: false,
        loans: [],
        creditEvents: [],
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      const result = await service.getCreditReport("user-123");

      expect(result.riskLevel).toBe("high");
    });

    it("should throw error for non-existent wallet", async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);

      await expect(service.getCreditReport("user-999")).rejects.toThrow(
        NotFoundException,
      );
    });
  });
});
