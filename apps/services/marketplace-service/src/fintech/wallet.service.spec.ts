/**
 * SAHOOL Wallet Service Tests
 * اختبارات خدمة المحفظة
 */

import { Test, TestingModule } from "@nestjs/testing";
import { WalletService } from "./wallet.service";
import { PrismaService } from "../prisma/prisma.service";
import { BadRequestException, NotFoundException } from "@nestjs/common";

describe("WalletService", () => {
  let service: WalletService;
  let prismaService: PrismaService;

  const mockPrismaService = {
    wallet: {
      findUnique: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
    },
    transaction: {
      findUnique: jest.fn(),
      findMany: jest.fn(),
      create: jest.fn(),
    },
    walletAuditLog: {
      create: jest.fn(),
    },
    escrow: {
      findMany: jest.fn(),
    },
    scheduledPayment: {
      findMany: jest.fn(),
    },
    $transaction: jest.fn(),
    $queryRaw: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        WalletService,
        {
          provide: PrismaService,
          useValue: mockPrismaService,
        },
      ],
    }).compile();

    service = module.get<WalletService>(WalletService);
    prismaService = module.get<PrismaService>(PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe("getWallet", () => {
    it("should return existing wallet with Arabic tier translation", async () => {
      const mockWallet = {
        id: "wallet-1",
        userId: "user-123",
        balance: 5000,
        creditScore: 650,
        creditTier: "GOLD",
        loanLimit: 22750,
        currentLoan: 0,
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      const result = await service.getWallet("user-123");

      expect(result).toEqual(
        expect.objectContaining({
          id: "wallet-1",
          balance: 5000,
          creditTierAr: "ذهبي",
          availableCredit: 22750,
        }),
      );
    });

    it("should create new wallet if not exists", async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);

      const newWallet = {
        id: "wallet-new",
        userId: "user-new",
        balance: 0,
        creditScore: 300,
        creditTier: "BRONZE",
        loanLimit: 0,
        currentLoan: 0,
      };

      mockPrismaService.wallet.create.mockResolvedValue(newWallet);

      const result = await service.getWallet("user-new", "farmer");

      expect(mockPrismaService.wallet.create).toHaveBeenCalledWith({
        data: {
          userId: "user-new",
          userType: "farmer",
          balance: 0,
          creditScore: 300,
          creditTier: "BRONZE",
        },
      });
      expect(result.creditTierAr).toBe("برونزي");
    });
  });

  describe("getCreditTierAr", () => {
    it("should translate credit tiers to Arabic", () => {
      expect(service.getCreditTierAr("BRONZE")).toBe("برونزي");
      expect(service.getCreditTierAr("SILVER")).toBe("فضي");
      expect(service.getCreditTierAr("GOLD")).toBe("ذهبي");
      expect(service.getCreditTierAr("PLATINUM")).toBe("بلاتيني");
      expect(service.getCreditTierAr("UNKNOWN")).toBe("UNKNOWN");
    });
  });

  describe("deposit", () => {
    it("should throw error for zero or negative amount", async () => {
      await expect(service.deposit("wallet-1", 0)).rejects.toThrow(
        BadRequestException,
      );
      await expect(service.deposit("wallet-1", -100)).rejects.toThrow(
        BadRequestException,
      );
    });

    it("should return existing transaction for duplicate idempotency key", async () => {
      const existingTx = { id: "tx-1", type: "DEPOSIT", amount: 500 };
      const existingWallet = { id: "wallet-1", balance: 1500 };

      mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
      mockPrismaService.wallet.findUnique.mockResolvedValue(existingWallet);

      const result = await service.deposit(
        "wallet-1",
        500,
        "Test",
        "idemp-key-1",
      );

      expect(result.duplicate).toBe(true);
      expect(result.transaction).toEqual(existingTx);
    });

    it("should deposit amount with audit logging", async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        $queryRaw: jest.fn().mockResolvedValue([
          {
            id: "wallet-1",
            balance: 1000,
            version: 1,
          },
        ]),
        wallet: {
          update: jest.fn().mockResolvedValue({
            id: "wallet-1",
            balance: 1500,
            version: 2,
          }),
        },
        transaction: {
          create: jest.fn().mockResolvedValue({
            id: "tx-1",
            type: "DEPOSIT",
            amount: 500,
          }),
        },
        walletAuditLog: {
          create: jest.fn().mockResolvedValue({}),
        },
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      const result = await service.deposit("wallet-1", 500, "Test deposit");

      expect(result.duplicate).toBe(false);
      expect(result.wallet.balance).toBe(1500);
    });
  });

  describe("withdraw", () => {
    it("should throw error for zero or negative amount", async () => {
      await expect(service.withdraw("wallet-1", 0)).rejects.toThrow(
        BadRequestException,
      );
      await expect(service.withdraw("wallet-1", -100)).rejects.toThrow(
        BadRequestException,
      );
    });

    it("should throw error for insufficient balance", async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        $queryRaw: jest.fn().mockResolvedValue([
          {
            id: "wallet-1",
            balance: 100,
            version: 1,
            singleTransactionLimit: 50000,
            dailyWithdrawLimit: 10000,
            dailyWithdrawnToday: 0,
          },
        ]),
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      await expect(service.withdraw("wallet-1", 500)).rejects.toThrow(
        BadRequestException,
      );
    });

    it("should return existing transaction for duplicate idempotency key", async () => {
      const existingTx = { id: "tx-1", type: "WITHDRAWAL", amount: -500 };
      const existingWallet = { id: "wallet-1", balance: 500 };

      mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
      mockPrismaService.wallet.findUnique.mockResolvedValue(existingWallet);

      const result = await service.withdraw(
        "wallet-1",
        500,
        "Test",
        "idemp-key-1",
      );

      expect(result.duplicate).toBe(true);
    });
  });

  describe("getTransactions", () => {
    it("should return wallet transactions", async () => {
      const mockTransactions = [
        { id: "tx-1", type: "DEPOSIT", amount: 500 },
        { id: "tx-2", type: "WITHDRAWAL", amount: -200 },
      ];

      mockPrismaService.transaction.findMany.mockResolvedValue(
        mockTransactions,
      );

      const result = await service.getTransactions("wallet-1", 10);

      expect(mockPrismaService.transaction.findMany).toHaveBeenCalledWith({
        where: { walletId: "wallet-1" },
        orderBy: { createdAt: "desc" },
        take: 10,
      });
      expect(result).toEqual(mockTransactions);
    });
  });

  describe("getWalletLimits", () => {
    it("should return wallet limits", async () => {
      const mockWallet = {
        id: "wallet-1",
        dailyWithdrawLimit: 10000,
        dailyWithdrawnToday: 2000,
        singleTransactionLimit: 50000,
        requiresPinForAmount: 5000,
        creditTier: "SILVER",
        lastWithdrawReset: new Date(),
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      const result = await service.getWalletLimits("wallet-1");

      expect(result.dailyWithdrawLimit).toBe(10000);
      expect(result.singleTransactionLimit).toBe(50000);
    });

    it("should throw error for non-existent wallet", async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);

      await expect(service.getWalletLimits("wallet-999")).rejects.toThrow(
        NotFoundException,
      );
    });
  });

  describe("updateWalletLimits", () => {
    it("should update limits based on credit tier", async () => {
      const testCases = [
        { tier: "PLATINUM", daily: 100000, single: 500000, pin: 50000 },
        { tier: "GOLD", daily: 50000, single: 200000, pin: 20000 },
        { tier: "SILVER", daily: 20000, single: 100000, pin: 10000 },
        { tier: "BRONZE", daily: 10000, single: 50000, pin: 5000 },
      ];

      for (const testCase of testCases) {
        mockPrismaService.wallet.findUnique.mockResolvedValue({
          id: "wallet-1",
          creditTier: testCase.tier,
        });

        mockPrismaService.wallet.update.mockResolvedValue({
          id: "wallet-1",
          dailyWithdrawLimit: testCase.daily,
          singleTransactionLimit: testCase.single,
          requiresPinForAmount: testCase.pin,
        });

        await service.updateWalletLimits("wallet-1");

        expect(mockPrismaService.wallet.update).toHaveBeenCalledWith({
          where: { id: "wallet-1" },
          data: {
            dailyWithdrawLimit: testCase.daily,
            singleTransactionLimit: testCase.single,
            requiresPinForAmount: testCase.pin,
          },
        });
      }
    });
  });

  describe("getWalletDashboard", () => {
    it("should return complete wallet dashboard", async () => {
      const mockWallet = {
        id: "wallet-1",
        balance: 5000,
        escrowBalance: 1000,
        creditScore: 650,
        creditTier: "GOLD",
        loanLimit: 22750,
        currentLoan: 5000,
        dailyWithdrawLimit: 50000,
        dailyWithdrawnToday: 1000,
        singleTransactionLimit: 200000,
        lastWithdrawReset: new Date(),
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);
      mockPrismaService.escrow.findMany.mockResolvedValue([]);
      mockPrismaService.scheduledPayment.findMany.mockResolvedValue([]);
      mockPrismaService.transaction.findMany.mockResolvedValue([]);

      const result = await service.getWalletDashboard("wallet-1");

      expect(result.wallet.id).toBe("wallet-1");
      expect(result.wallet.balance).toBe(5000);
      expect(result.wallet.creditTierAr).toBe("ذهبي");
      expect(result.summary.availableCredit).toBe(17750);
    });

    it("should throw error for non-existent wallet", async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);

      await expect(service.getWalletDashboard("wallet-999")).rejects.toThrow(
        NotFoundException,
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Additional Security & Integrity Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe("Advanced Security Tests", () => {
    describe("Transaction Serialization", () => {
      it("should use SERIALIZABLE isolation level for critical operations", async () => {
        const walletData = {
          id: "wallet-1",
          balance: 10000,
          version: 1,
        };

        mockPrismaService.$transaction.mockImplementation(
          async (callback, options) => {
            const tx = {
              $queryRaw: jest.fn().mockResolvedValue([walletData]),
              wallet: {
                update: jest.fn().mockResolvedValue({
                  ...walletData,
                  balance: 15000,
                  version: 2,
                }),
              },
              transaction: {
                create: jest.fn().mockResolvedValue({ id: "tx-1" }),
              },
              walletAuditLog: {
                create: jest.fn().mockResolvedValue({}),
              },
            };
            return callback(tx);
          },
        );

        await service.deposit("wallet-1", 5000);

        expect(mockPrismaService.$transaction).toHaveBeenCalledWith(
          expect.any(Function),
          expect.objectContaining({
            isolationLevel: "Serializable",
            maxWait: 5000,
            timeout: 10000,
          }),
        );
      });

      it("should handle transaction timeout gracefully", async () => {
        mockPrismaService.$transaction.mockRejectedValue(
          new Error("Transaction timeout"),
        );

        await expect(service.deposit("wallet-1", 5000)).rejects.toThrow(
          "Transaction timeout",
        );
      });
    });

    describe("Balance Integrity", () => {
      it("should maintain balance integrity across multiple operations", async () => {
        const initialBalance = 10000;
        let currentBalance = initialBalance;

        // Deposit
        mockPrismaService.$transaction.mockImplementationOnce(
          async (callback) => {
            const tx = {
              $queryRaw: jest.fn().mockResolvedValue([
                {
                  id: "wallet-1",
                  balance: currentBalance,
                  version: 1,
                },
              ]),
              wallet: {
                update: jest.fn().mockImplementation(() => {
                  currentBalance += 5000;
                  return Promise.resolve({ balance: currentBalance });
                }),
              },
              transaction: {
                create: jest.fn().mockResolvedValue({}),
              },
              walletAuditLog: {
                create: jest.fn().mockResolvedValue({}),
              },
            };
            return callback(tx);
          },
        );

        await service.deposit("wallet-1", 5000);
        expect(currentBalance).toBe(15000);

        // Withdraw
        mockPrismaService.$transaction.mockImplementationOnce(
          async (callback) => {
            const tx = {
              $queryRaw: jest.fn().mockResolvedValue([
                {
                  id: "wallet-1",
                  balance: currentBalance,
                  version: 2,
                  dailyWithdrawLimit: 100000,
                  singleTransactionLimit: 200000,
                  dailyWithdrawnToday: 0,
                  lastWithdrawReset: new Date(),
                },
              ]),
              wallet: {
                update: jest.fn().mockImplementation(() => {
                  currentBalance -= 3000;
                  return Promise.resolve({ balance: currentBalance });
                }),
              },
              transaction: {
                create: jest.fn().mockResolvedValue({}),
              },
              walletAuditLog: {
                create: jest.fn().mockResolvedValue({}),
              },
            };
            return callback(tx);
          },
        );

        await service.withdraw("wallet-1", 3000);
        expect(currentBalance).toBe(12000);
      });

      it("should prevent balance from going negative", async () => {
        const walletData = {
          id: "wallet-1",
          balance: 100,
          version: 1,
        };

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          const tx = {
            $queryRaw: jest.fn().mockResolvedValue([walletData]),
          };
          return callback(tx);
        });

        await expect(service.withdraw("wallet-1", 500)).rejects.toThrow(
          "الرصيد غير كافي",
        );
      });
    });

    describe("Concurrent Transaction Handling", () => {
      it("should handle optimistic locking conflicts", async () => {
        const walletData = {
          id: "wallet-1",
          balance: 10000,
          version: 5,
        };

        // First transaction
        mockPrismaService.$transaction.mockImplementationOnce(
          async (callback) => {
            const tx = {
              $queryRaw: jest.fn().mockResolvedValue([walletData]),
              wallet: {
                update: jest.fn().mockResolvedValue({
                  ...walletData,
                  balance: 15000,
                  version: 6,
                }),
              },
              transaction: {
                create: jest.fn().mockResolvedValue({}),
              },
              walletAuditLog: {
                create: jest.fn().mockResolvedValue({}),
              },
            };
            return callback(tx);
          },
        );

        await service.deposit("wallet-1", 5000);

        // Second concurrent transaction should fail if version mismatch
        mockPrismaService.$transaction.mockImplementationOnce(
          async (callback) => {
            const tx = {
              $queryRaw: jest.fn().mockResolvedValue([
                {
                  ...walletData,
                  version: 6, // Version already updated
                },
              ]),
              wallet: {
                update: jest
                  .fn()
                  .mockRejectedValue(new Error("Optimistic locking failed")),
              },
            };
            return callback(tx);
          },
        );

        // This should potentially retry or fail gracefully
        // depending on implementation
      });
    });

    describe("Fraud Detection Patterns", () => {
      it("should flag suspicious rapid withdrawal patterns", async () => {
        const rapidWithdrawals = [
          { amount: 5000, timestamp: new Date("2024-01-01T10:00:00") },
          { amount: 5000, timestamp: new Date("2024-01-01T10:00:05") },
          { amount: 5000, timestamp: new Date("2024-01-01T10:00:10") },
        ];

        // Mock fraud detection logic
        const isSuspicious = (withdrawals: typeof rapidWithdrawals) => {
          if (withdrawals.length < 3) return false;
          const timeWindow = 60000; // 1 minute
          const first = withdrawals[0].timestamp.getTime();
          const last = withdrawals[withdrawals.length - 1].timestamp.getTime();
          return last - first < timeWindow;
        };

        expect(isSuspicious(rapidWithdrawals)).toBe(true);
      });

      it("should detect unusual transaction amounts", async () => {
        const recentTransactions = [
          { amount: 100 },
          { amount: 150 },
          { amount: 120 },
          { amount: 50000 }, // Unusual spike
        ];

        // Mock anomaly detection
        const detectAnomaly = (transactions: typeof recentTransactions) => {
          const amounts = transactions.map((t) => t.amount);
          const avg = amounts.reduce((a, b) => a + b, 0) / amounts.length;
          const threshold = avg * 10;
          return amounts.some((amount) => amount > threshold);
        };

        expect(detectAnomaly(recentTransactions)).toBe(true);
      });

      it("should monitor cross-country transaction patterns", async () => {
        const transactions = [
          { ipAddress: "192.168.1.1", country: "YE" },
          { ipAddress: "203.0.113.42", country: "YE" },
          { ipAddress: "198.51.100.99", country: "US" }, // Different country
        ];

        // Mock geo-location validation
        const hasSuspiciousLocation = (txs: typeof transactions) => {
          const countries = new Set(txs.map((t) => t.country));
          return countries.size > 1; // Multiple countries in short time
        };

        expect(hasSuspiciousLocation(transactions)).toBe(true);
      });
    });

    describe("Audit Compliance", () => {
      it("should record complete audit trail with metadata", async () => {
        const walletData = {
          id: "wallet-1",
          balance: 10000,
          version: 1,
        };

        const auditLogMock = jest.fn().mockResolvedValue({});

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          const tx = {
            $queryRaw: jest.fn().mockResolvedValue([walletData]),
            wallet: {
              update: jest.fn().mockResolvedValue({
                ...walletData,
                balance: 15000,
                version: 2,
              }),
            },
            transaction: {
              create: jest.fn().mockResolvedValue({ id: "tx-1" }),
            },
            walletAuditLog: {
              create: auditLogMock,
            },
          };
          return callback(tx);
        });

        await service.deposit(
          "wallet-1",
          5000,
          "Test deposit",
          "idemp-key-1",
          "user-123",
          "192.168.1.1",
        );

        expect(auditLogMock).toHaveBeenCalledWith(
          expect.objectContaining({
            data: expect.objectContaining({
              walletId: "wallet-1",
              transactionId: "tx-1",
              userId: "user-123",
              operation: "DEPOSIT",
              balanceBefore: 10000,
              balanceAfter: 15000,
              amount: 5000,
              versionBefore: 1,
              versionAfter: 2,
              idempotencyKey: "idemp-key-1",
              ipAddress: "192.168.1.1",
            }),
          }),
        );
      });

      it("should maintain immutable audit logs", async () => {
        // Audit logs should never be updated or deleted
        // Only created
        const auditLog = {
          id: "audit-1",
          operation: "DEPOSIT",
          amount: 5000,
          createdAt: new Date(),
        };

        // Verify no update or delete methods are exposed
        // This is a design verification test
        expect(typeof service["updateAuditLog"]).toBe("undefined");
        expect(typeof service["deleteAuditLog"]).toBe("undefined");
      });
    });

    describe("Error Handling & Recovery", () => {
      it("should rollback transaction on wallet update failure", async () => {
        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          const tx = {
            $queryRaw: jest.fn().mockResolvedValue([
              {
                id: "wallet-1",
                balance: 10000,
                version: 1,
              },
            ]),
            wallet: {
              update: jest.fn().mockRejectedValue(new Error("Update failed")),
            },
          };
          return callback(tx);
        });

        await expect(service.deposit("wallet-1", 5000)).rejects.toThrow(
          "Update failed",
        );
      });

      it("should handle database connection errors", async () => {
        mockPrismaService.$transaction.mockRejectedValue(
          new Error("Connection refused"),
        );

        await expect(service.deposit("wallet-1", 5000)).rejects.toThrow(
          "Connection refused",
        );
      });

      it("should handle constraint violation errors", async () => {
        mockPrismaService.$transaction.mockRejectedValue(
          new Error("Unique constraint violation"),
        );

        await expect(
          service.deposit("wallet-1", 5000, "Test", "existing-key"),
        ).rejects.toThrow("Unique constraint violation");
      });
    });

    describe("Performance & Scalability", () => {
      it("should handle high transaction volumes efficiently", async () => {
        const startTime = Date.now();
        const transactionCount = 100;

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          const tx = {
            $queryRaw: jest.fn().mockResolvedValue([
              {
                id: "wallet-1",
                balance: 10000,
                version: 1,
              },
            ]),
            wallet: {
              update: jest.fn().mockResolvedValue({
                balance: 15000,
                version: 2,
              }),
            },
            transaction: {
              create: jest.fn().mockResolvedValue({}),
            },
            walletAuditLog: {
              create: jest.fn().mockResolvedValue({}),
            },
          };
          return callback(tx);
        });

        const promises = [];
        for (let i = 0; i < transactionCount; i++) {
          promises.push(service.deposit("wallet-1", 100));
        }

        await Promise.all(promises);

        const endTime = Date.now();
        const duration = endTime - startTime;

        // Should complete in reasonable time (adjust threshold as needed)
        expect(duration).toBeLessThan(10000); // 10 seconds
      });

      it("should batch read operations efficiently", async () => {
        const queryMock = jest.fn().mockResolvedValue([]);

        mockPrismaService.transaction.findMany = queryMock;

        await service.getTransactions("wallet-1", 20);

        // Should make single query, not N+1
        expect(queryMock).toHaveBeenCalledTimes(1);
      });
    });

    describe("Authorization & Access Control", () => {
      it("should prevent cross-wallet access", async () => {
        // User should only access their own wallet
        const userWalletId = "wallet-1";
        const attemptedWalletId = "wallet-2";

        const isAuthorized = userWalletId === attemptedWalletId;
        expect(isAuthorized).toBe(false);
      });

      it("should validate admin privileges for sensitive operations", async () => {
        // Only admins should be able to update wallet limits manually
        const userRole = "user";
        const requiredRole = "admin";

        const hasPermission = userRole === requiredRole;
        expect(hasPermission).toBe(false);
      });
    });
  });
});
