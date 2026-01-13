/**
 * SAHOOL FinTech Service (Facade) Tests
 * اختبارات خدمة التمويل - الواجهة الموحدة
 */

import { Test, TestingModule } from "@nestjs/testing";
import { FintechService } from "./fintech.service";
import { WalletService } from "./wallet.service";
import { CreditService } from "./credit.service";
import { LoanService } from "./loan.service";
import { EscrowService } from "./escrow.service";
import { PrismaService } from "../prisma/prisma.service";

describe("FintechService (Facade)", () => {
  let service: FintechService;
  let walletService: WalletService;
  let creditService: CreditService;
  let loanService: LoanService;
  let escrowService: EscrowService;

  const mockWalletService = {
    getWallet: jest.fn(),
    deposit: jest.fn(),
    withdraw: jest.fn(),
    getTransactions: jest.fn(),
    getWalletLimits: jest.fn(),
    updateWalletLimits: jest.fn(),
    getWalletDashboard: jest.fn(),
    getCreditTierAr: jest.fn(),
  };

  const mockCreditService = {
    calculateCreditScore: jest.fn(),
    calculateAdvancedCreditScore: jest.fn(),
    getCreditFactors: jest.fn(),
    recordCreditEvent: jest.fn(),
    getCreditReport: jest.fn(),
  };

  const mockLoanService = {
    requestLoan: jest.fn(),
    approveLoan: jest.fn(),
    repayLoan: jest.fn(),
    getUserLoans: jest.fn(),
    createScheduledPayment: jest.fn(),
    getScheduledPayments: jest.fn(),
    cancelScheduledPayment: jest.fn(),
    executeScheduledPayment: jest.fn(),
    getLoanPurposeAr: jest.fn(),
  };

  const mockEscrowService = {
    createEscrow: jest.fn(),
    releaseEscrow: jest.fn(),
    refundEscrow: jest.fn(),
    getEscrowByOrder: jest.fn(),
    getWalletEscrows: jest.fn(),
  };

  const mockPrismaService = {
    wallet: {
      count: jest.fn(),
      aggregate: jest.fn(),
    },
    loan: {
      count: jest.fn(),
    },
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        FintechService,
        { provide: WalletService, useValue: mockWalletService },
        { provide: CreditService, useValue: mockCreditService },
        { provide: LoanService, useValue: mockLoanService },
        { provide: EscrowService, useValue: mockEscrowService },
        { provide: PrismaService, useValue: mockPrismaService },
      ],
    }).compile();

    service = module.get<FintechService>(FintechService);
    walletService = module.get<WalletService>(WalletService);
    creditService = module.get<CreditService>(CreditService);
    loanService = module.get<LoanService>(LoanService);
    escrowService = module.get<EscrowService>(EscrowService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe("Wallet Operations (delegated)", () => {
    it("should delegate getWallet to WalletService", async () => {
      const mockResult = { id: "wallet-1", balance: 5000 };
      mockWalletService.getWallet.mockResolvedValue(mockResult);

      const result = await service.getWallet("user-123", "farmer");

      expect(mockWalletService.getWallet).toHaveBeenCalledWith(
        "user-123",
        "farmer",
      );
      expect(result).toEqual(mockResult);
    });

    it("should delegate deposit to WalletService", async () => {
      const mockResult = {
        wallet: { balance: 1500 },
        transaction: { id: "tx-1" },
      };
      mockWalletService.deposit.mockResolvedValue(mockResult);

      const result = await service.deposit(
        "wallet-1",
        500,
        "Test",
        "key-1",
        "user-1",
        "127.0.0.1",
      );

      expect(mockWalletService.deposit).toHaveBeenCalledWith(
        "wallet-1",
        500,
        "Test",
        "key-1",
        "user-1",
        "127.0.0.1",
      );
      expect(result).toEqual(mockResult);
    });

    it("should delegate withdraw to WalletService", async () => {
      const mockResult = {
        wallet: { balance: 500 },
        transaction: { id: "tx-1" },
      };
      mockWalletService.withdraw.mockResolvedValue(mockResult);

      const result = await service.withdraw("wallet-1", 500);

      expect(mockWalletService.withdraw).toHaveBeenCalledWith(
        "wallet-1",
        500,
        undefined,
        undefined,
        undefined,
        undefined,
      );
      expect(result).toEqual(mockResult);
    });

    it("should delegate getTransactions to WalletService", async () => {
      const mockResult = [{ id: "tx-1" }, { id: "tx-2" }];
      mockWalletService.getTransactions.mockResolvedValue(mockResult);

      const result = await service.getTransactions("wallet-1", 10);

      expect(mockWalletService.getTransactions).toHaveBeenCalledWith(
        "wallet-1",
        10,
      );
      expect(result).toEqual(mockResult);
    });

    it("should delegate getWalletDashboard to WalletService", async () => {
      const mockResult = { wallet: { id: "wallet-1" }, summary: {} };
      mockWalletService.getWalletDashboard.mockResolvedValue(mockResult);

      const result = await service.getWalletDashboard("wallet-1");

      expect(mockWalletService.getWalletDashboard).toHaveBeenCalledWith(
        "wallet-1",
      );
      expect(result).toEqual(mockResult);
    });
  });

  describe("Credit Operations (delegated)", () => {
    it("should delegate calculateCreditScore to CreditService", async () => {
      const farmData = { totalArea: 10, activeSeasons: 5 };
      const mockResult = { wallet: { creditScore: 700 } };
      mockCreditService.calculateCreditScore.mockResolvedValue(mockResult);

      const result = await service.calculateCreditScore(
        "user-123",
        farmData as any,
      );

      expect(mockCreditService.calculateCreditScore).toHaveBeenCalledWith(
        "user-123",
        farmData,
      );
      expect(result).toEqual(mockResult);
    });

    it("should delegate getCreditReport to CreditService", async () => {
      const mockResult = { currentScore: 700, recommendations: [] };
      mockCreditService.getCreditReport.mockResolvedValue(mockResult);

      const result = await service.getCreditReport("user-123");

      expect(mockCreditService.getCreditReport).toHaveBeenCalledWith(
        "user-123",
      );
      expect(result).toEqual(mockResult);
    });

    it("should delegate recordCreditEvent to CreditService", async () => {
      const eventData = {
        walletId: "wallet-1",
        eventType: "ORDER_COMPLETED",
        description: "Test",
      };
      const mockResult = { event: { id: "event-1" }, impact: 5 };
      mockCreditService.recordCreditEvent.mockResolvedValue(mockResult);

      const result = await service.recordCreditEvent(eventData);

      expect(mockCreditService.recordCreditEvent).toHaveBeenCalledWith(
        eventData,
      );
      expect(result).toEqual(mockResult);
    });
  });

  describe("Loan Operations (delegated)", () => {
    it("should delegate requestLoan to LoanService", async () => {
      const loanData = {
        walletId: "wallet-1",
        amount: 10000,
        termMonths: 12,
        purpose: "SEEDS",
      };
      const mockResult = { loan: { id: "loan-1" }, message: "Success" };
      mockLoanService.requestLoan.mockResolvedValue(mockResult);

      const result = await service.requestLoan(loanData);

      expect(mockLoanService.requestLoan).toHaveBeenCalledWith(loanData);
      expect(result).toEqual(mockResult);
    });

    it("should delegate approveLoan to LoanService", async () => {
      const mockResult = { loan: { status: "ACTIVE" } };
      mockLoanService.approveLoan.mockResolvedValue(mockResult);

      const result = await service.approveLoan("loan-1");

      expect(mockLoanService.approveLoan).toHaveBeenCalledWith("loan-1");
      expect(result).toEqual(mockResult);
    });

    it("should delegate repayLoan to LoanService", async () => {
      const mockResult = { loan: { paidAmount: 5000 }, remainingAmount: 5000 };
      mockLoanService.repayLoan.mockResolvedValue(mockResult);

      const result = await service.repayLoan(
        "loan-1",
        5000,
        "key-1",
        "user-1",
        "127.0.0.1",
      );

      expect(mockLoanService.repayLoan).toHaveBeenCalledWith(
        "loan-1",
        5000,
        "key-1",
        "user-1",
        "127.0.0.1",
      );
      expect(result).toEqual(mockResult);
    });

    it("should delegate scheduled payment operations to LoanService", async () => {
      const nextDate = new Date();
      mockLoanService.createScheduledPayment.mockResolvedValue({
        scheduledPayment: {},
      });
      mockLoanService.getScheduledPayments.mockResolvedValue([]);
      mockLoanService.cancelScheduledPayment.mockResolvedValue({
        isActive: false,
      });

      await service.createScheduledPayment(
        "wallet-1",
        1000,
        "MONTHLY",
        nextDate,
      );
      await service.getScheduledPayments("wallet-1", true);
      await service.cancelScheduledPayment("sp-1");

      expect(mockLoanService.createScheduledPayment).toHaveBeenCalled();
      expect(mockLoanService.getScheduledPayments).toHaveBeenCalledWith(
        "wallet-1",
        true,
      );
      expect(mockLoanService.cancelScheduledPayment).toHaveBeenCalledWith(
        "sp-1",
      );
    });
  });

  describe("Escrow Operations (delegated)", () => {
    it("should delegate createEscrow to EscrowService", async () => {
      const mockResult = { escrow: { id: "escrow-1", status: "HELD" } };
      mockEscrowService.createEscrow.mockResolvedValue(mockResult);

      const result = await service.createEscrow(
        "order-1",
        "buyer-wallet",
        "seller-wallet",
        1000,
        "Notes",
        "key-1",
        "user-1",
        "127.0.0.1",
      );

      expect(mockEscrowService.createEscrow).toHaveBeenCalledWith(
        "order-1",
        "buyer-wallet",
        "seller-wallet",
        1000,
        "Notes",
        "key-1",
        "user-1",
        "127.0.0.1",
      );
      expect(result).toEqual(mockResult);
    });

    it("should delegate releaseEscrow to EscrowService", async () => {
      const mockResult = { escrow: { status: "RELEASED" } };
      mockEscrowService.releaseEscrow.mockResolvedValue(mockResult);

      const result = await service.releaseEscrow(
        "escrow-1",
        "Notes",
        "key-1",
        "user-1",
        "127.0.0.1",
      );

      expect(mockEscrowService.releaseEscrow).toHaveBeenCalledWith(
        "escrow-1",
        "Notes",
        "key-1",
        "user-1",
        "127.0.0.1",
      );
      expect(result).toEqual(mockResult);
    });

    it("should delegate refundEscrow to EscrowService", async () => {
      const mockResult = { escrow: { status: "REFUNDED" } };
      mockEscrowService.refundEscrow.mockResolvedValue(mockResult);

      const result = await service.refundEscrow("escrow-1", "Cancelled");

      expect(mockEscrowService.refundEscrow).toHaveBeenCalledWith(
        "escrow-1",
        "Cancelled",
        undefined,
        undefined,
        undefined,
      );
      expect(result).toEqual(mockResult);
    });

    it("should delegate getWalletEscrows to EscrowService", async () => {
      const mockResult = { asBuyer: [], asSeller: [] };
      mockEscrowService.getWalletEscrows.mockResolvedValue(mockResult);

      const result = await service.getWalletEscrows("wallet-1");

      expect(mockEscrowService.getWalletEscrows).toHaveBeenCalledWith(
        "wallet-1",
      );
      expect(result).toEqual(mockResult);
    });
  });

  describe("Statistics", () => {
    it("should return finance statistics", async () => {
      mockPrismaService.wallet.count.mockResolvedValue(100);
      mockPrismaService.wallet.aggregate
        .mockResolvedValueOnce({ _sum: { balance: 500000 } })
        .mockResolvedValueOnce({ _avg: { creditScore: 550 } });
      mockPrismaService.loan.count
        .mockResolvedValueOnce(20)
        .mockResolvedValueOnce(50);

      const result = await service.getFinanceStats();

      expect(result).toEqual({
        totalWallets: 100,
        totalBalance: 500000,
        activeLoans: 20,
        paidLoans: 50,
        avgCreditScore: 550,
      });
    });

    it("should handle empty statistics gracefully", async () => {
      mockPrismaService.wallet.count.mockResolvedValue(0);
      mockPrismaService.wallet.aggregate
        .mockResolvedValueOnce({ _sum: { balance: null } })
        .mockResolvedValueOnce({ _avg: { creditScore: null } });
      mockPrismaService.loan.count
        .mockResolvedValueOnce(0)
        .mockResolvedValueOnce(0);

      const result = await service.getFinanceStats();

      expect(result).toEqual({
        totalWallets: 0,
        totalBalance: 0,
        activeLoans: 0,
        paidLoans: 0,
        avgCreditScore: 0,
      });
    });
  });

  describe("Helper Methods", () => {
    it("should delegate getCreditTierAr to WalletService", () => {
      mockWalletService.getCreditTierAr.mockReturnValue("ذهبي");

      const result = service.getCreditTierAr("GOLD");

      expect(mockWalletService.getCreditTierAr).toHaveBeenCalledWith("GOLD");
      expect(result).toBe("ذهبي");
    });

    it("should delegate getLoanPurposeAr to LoanService", () => {
      mockLoanService.getLoanPurposeAr.mockReturnValue("شراء بذور");

      const result = service.getLoanPurposeAr("SEEDS");

      expect(mockLoanService.getLoanPurposeAr).toHaveBeenCalledWith("SEEDS");
      expect(result).toBe("شراء بذور");
    });
  });
});
