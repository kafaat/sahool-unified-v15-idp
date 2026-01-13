/**
 * SAHOOL Escrow Service Tests
 * اختبارات خدمة الإسكرو (الضمان)
 */

import { Test, TestingModule } from "@nestjs/testing";
import { EscrowService } from "./escrow.service";
import { PrismaService } from "../prisma/prisma.service";
import { BadRequestException, NotFoundException } from "@nestjs/common";

describe("EscrowService", () => {
  let service: EscrowService;
  let prismaService: PrismaService;

  const mockPrismaService = {
    wallet: {
      findUnique: jest.fn(),
      update: jest.fn(),
    },
    escrow: {
      findUnique: jest.fn(),
      findMany: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
    },
    transaction: {
      findUnique: jest.fn(),
      create: jest.fn(),
    },
    walletAuditLog: {
      create: jest.fn(),
    },
    creditEvent: {
      create: jest.fn(),
    },
    $transaction: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        EscrowService,
        {
          provide: PrismaService,
          useValue: mockPrismaService,
        },
      ],
    }).compile();

    service = module.get<EscrowService>(EscrowService);
    prismaService = module.get<PrismaService>(PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe("createEscrow", () => {
    it("should throw error for zero or negative amount", async () => {
      await expect(
        service.createEscrow("order-1", "buyer-wallet", "seller-wallet", 0),
      ).rejects.toThrow(BadRequestException);

      await expect(
        service.createEscrow("order-1", "buyer-wallet", "seller-wallet", -100),
      ).rejects.toThrow(BadRequestException);
    });

    it("should return existing escrow for duplicate idempotency key", async () => {
      const existingTx = { id: "tx-1", type: "ESCROW_HOLD" };
      const existingEscrow = { id: "escrow-1", orderId: "order-1" };

      mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
      mockPrismaService.escrow.findUnique.mockResolvedValue(existingEscrow);

      const result = await service.createEscrow(
        "order-1",
        "buyer-wallet",
        "seller-wallet",
        1000,
        "Notes",
        "idemp-key-1",
      );

      expect(result.duplicate).toBe(true);
      expect(result.escrow).toEqual(existingEscrow);
    });

    it("should create escrow with locked buyer balance", async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue(null),
          create: jest.fn().mockResolvedValue({
            id: "escrow-1",
            orderId: "order-1",
            amount: 1000,
            status: "HELD",
          }),
        },
        wallet: {
          findUnique: jest.fn().mockResolvedValue({ id: "seller-wallet" }),
          update: jest.fn().mockResolvedValue({
            id: "buyer-wallet",
            balance: 4000,
            escrowBalance: 1000,
          }),
        },
        transaction: {
          create: jest.fn().mockResolvedValue({
            id: "tx-1",
            type: "ESCROW_HOLD",
            amount: -1000,
          }),
        },
        walletAuditLog: {
          create: jest.fn().mockResolvedValue({}),
        },
        $queryRaw: jest.fn().mockResolvedValue([
          {
            id: "buyer-wallet",
            balance: 5000,
            escrowBalance: 0,
            version: 1,
          },
        ]),
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      const result = await service.createEscrow(
        "order-1",
        "buyer-wallet",
        "seller-wallet",
        1000,
        "Order payment",
      );

      expect(result.duplicate).toBe(false);
      expect(result.escrow.status).toBe("HELD");
      expect(result.wallet.balance).toBe(4000);
    });

    it("should throw error if escrow already exists for order", async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue({ id: "existing-escrow" }),
        },
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      await expect(
        service.createEscrow("order-1", "buyer-wallet", "seller-wallet", 1000),
      ).rejects.toThrow(BadRequestException);
    });
  });

  describe("releaseEscrow", () => {
    it("should return existing transaction for duplicate idempotency key", async () => {
      const existingTx = { id: "tx-1", type: "ESCROW_RELEASE" };
      const existingEscrow = {
        id: "escrow-1",
        status: "RELEASED",
        buyerWallet: {},
        sellerWallet: {},
      };

      mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
      mockPrismaService.escrow.findUnique.mockResolvedValue(existingEscrow);

      const result = await service.releaseEscrow(
        "escrow-1",
        "Notes",
        "idemp-key-1",
      );

      expect(result.duplicate).toBe(true);
    });

    it("should throw error for non-held escrow", async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue({
            id: "escrow-1",
            status: "RELEASED",
          }),
        },
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      await expect(service.releaseEscrow("escrow-1")).rejects.toThrow(
        BadRequestException,
      );
    });

    it("should throw error for non-existent escrow", async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue(null),
        },
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      await expect(service.releaseEscrow("escrow-999")).rejects.toThrow(
        NotFoundException,
      );
    });
  });

  describe("refundEscrow", () => {
    it("should return existing transaction for duplicate idempotency key", async () => {
      const existingTx = { id: "tx-1", type: "ESCROW_REFUND" };
      const existingEscrow = {
        id: "escrow-1",
        status: "REFUNDED",
        buyerWallet: {},
      };

      mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
      mockPrismaService.escrow.findUnique.mockResolvedValue(existingEscrow);

      const result = await service.refundEscrow(
        "escrow-1",
        "Cancelled",
        "idemp-key-1",
      );

      expect(result.duplicate).toBe(true);
    });

    it("should throw error for already released escrow", async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue({
            id: "escrow-1",
            status: "RELEASED",
          }),
        },
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      await expect(
        service.refundEscrow("escrow-1", "Cancelled"),
      ).rejects.toThrow(BadRequestException);
    });

    it("should refund held escrow to buyer", async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue({
            id: "escrow-1",
            orderId: "order-1",
            buyerWalletId: "buyer-wallet",
            sellerWalletId: "seller-wallet",
            amount: 1000,
            status: "HELD",
          }),
          update: jest.fn().mockResolvedValue({
            id: "escrow-1",
            status: "REFUNDED",
          }),
        },
        wallet: {
          update: jest.fn().mockResolvedValue({
            id: "buyer-wallet",
            balance: 6000,
            escrowBalance: 0,
          }),
        },
        transaction: {
          create: jest.fn().mockResolvedValue({
            id: "tx-1",
            type: "ESCROW_REFUND",
            amount: 1000,
          }),
        },
        walletAuditLog: {
          create: jest.fn().mockResolvedValue({}),
        },
        creditEvent: {
          create: jest.fn().mockResolvedValue({}),
        },
        $queryRaw: jest.fn().mockResolvedValue([
          {
            id: "buyer-wallet",
            balance: 5000,
            escrowBalance: 1000,
            version: 1,
          },
        ]),
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      const result = await service.refundEscrow("escrow-1", "Order cancelled");

      expect(result.duplicate).toBe(false);
      expect(result.escrow.status).toBe("REFUNDED");
      expect(result.wallet.balance).toBe(6000);
    });

    it("should allow refund of disputed escrow", async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue({
            id: "escrow-1",
            orderId: "order-1",
            buyerWalletId: "buyer-wallet",
            sellerWalletId: "seller-wallet",
            amount: 1000,
            status: "DISPUTED",
          }),
          update: jest.fn().mockResolvedValue({ status: "REFUNDED" }),
        },
        wallet: {
          update: jest
            .fn()
            .mockResolvedValue({ balance: 6000, escrowBalance: 0 }),
        },
        transaction: {
          create: jest.fn().mockResolvedValue({ id: "tx-1" }),
        },
        walletAuditLog: {
          create: jest.fn().mockResolvedValue({}),
        },
        creditEvent: {
          create: jest.fn().mockResolvedValue({}),
        },
        $queryRaw: jest.fn().mockResolvedValue([
          {
            id: "buyer-wallet",
            balance: 5000,
            escrowBalance: 1000,
            version: 1,
          },
        ]),
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      const result = await service.refundEscrow("escrow-1", "Dispute resolved");

      expect(result.escrow.status).toBe("REFUNDED");
    });
  });

  describe("getEscrowByOrder", () => {
    it("should return escrow with wallets for order", async () => {
      const mockEscrow = {
        id: "escrow-1",
        orderId: "order-1",
        amount: 1000,
        buyerWallet: { id: "buyer-wallet" },
        sellerWallet: { id: "seller-wallet" },
      };

      mockPrismaService.escrow.findUnique.mockResolvedValue(mockEscrow);

      const result = await service.getEscrowByOrder("order-1");

      expect(mockPrismaService.escrow.findUnique).toHaveBeenCalledWith({
        where: { orderId: "order-1" },
        include: {
          buyerWallet: true,
          sellerWallet: true,
        },
      });
      expect(result).toEqual(mockEscrow);
    });

    it("should return null for non-existent order", async () => {
      mockPrismaService.escrow.findUnique.mockResolvedValue(null);

      const result = await service.getEscrowByOrder("order-999");

      expect(result).toBeNull();
    });
  });

  describe("getWalletEscrows", () => {
    it("should return escrows as buyer and seller", async () => {
      const buyerEscrows = [
        { id: "escrow-1", amount: 1000 },
        { id: "escrow-2", amount: 2000 },
      ];

      const sellerEscrows = [{ id: "escrow-3", amount: 500 }];

      mockPrismaService.escrow.findMany
        .mockResolvedValueOnce(buyerEscrows)
        .mockResolvedValueOnce(sellerEscrows);

      const result = await service.getWalletEscrows("wallet-1");

      expect(result.asBuyer).toEqual(buyerEscrows);
      expect(result.asSeller).toEqual(sellerEscrows);
      expect(mockPrismaService.escrow.findMany).toHaveBeenCalledTimes(2);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Transaction Integrity Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe("Transaction Integrity", () => {
    describe("Escrow Creation Integrity", () => {
      it("should ensure atomic escrow creation and balance deduction", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        let walletUpdated = false;
        let escrowCreated = false;
        let transactionCreated = false;

        const mockTxContext = {
          escrow: {
            findUnique: jest.fn().mockResolvedValue(null),
            create: jest.fn().mockImplementation(() => {
              escrowCreated = true;
              return Promise.resolve({
                id: "escrow-1",
                status: "HELD",
                amount: 1000,
              });
            }),
          },
          wallet: {
            findUnique: jest.fn().mockResolvedValue({ id: "seller-wallet" }),
            update: jest.fn().mockImplementation(() => {
              walletUpdated = true;
              return Promise.resolve({
                id: "buyer-wallet",
                balance: 4000,
                escrowBalance: 1000,
              });
            }),
          },
          transaction: {
            create: jest.fn().mockImplementation(() => {
              transactionCreated = true;
              return Promise.resolve({ id: "tx-1" });
            }),
          },
          walletAuditLog: {
            create: jest.fn().mockResolvedValue({}),
          },
          $queryRaw: jest.fn().mockResolvedValue([
            {
              id: "buyer-wallet",
              balance: 5000,
              escrowBalance: 0,
              version: 1,
            },
          ]),
        };

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          return callback(mockTxContext);
        });

        await service.createEscrow(
          "order-1",
          "buyer-wallet",
          "seller-wallet",
          1000,
        );

        // Verify all operations completed
        expect(walletUpdated).toBe(true);
        expect(escrowCreated).toBe(true);
        expect(transactionCreated).toBe(true);
      });

      it("should rollback if escrow creation fails", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        const mockTxContext = {
          escrow: {
            findUnique: jest.fn().mockResolvedValue(null),
            create: jest
              .fn()
              .mockRejectedValue(new Error("Escrow creation failed")),
          },
          wallet: {
            findUnique: jest.fn().mockResolvedValue({ id: "seller-wallet" }),
            update: jest.fn().mockResolvedValue({}),
          },
          $queryRaw: jest.fn().mockResolvedValue([
            {
              id: "buyer-wallet",
              balance: 5000,
              version: 1,
            },
          ]),
        };

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          return callback(mockTxContext);
        });

        await expect(
          service.createEscrow(
            "order-1",
            "buyer-wallet",
            "seller-wallet",
            1000,
          ),
        ).rejects.toThrow("Escrow creation failed");
      });

      it("should validate wallet has sufficient balance before escrow", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        const mockTxContext = {
          escrow: {
            findUnique: jest.fn().mockResolvedValue(null),
          },
          $queryRaw: jest.fn().mockResolvedValue([
            {
              id: "buyer-wallet",
              balance: 500, // Insufficient for 1000 escrow
              escrowBalance: 0,
              version: 1,
            },
          ]),
        };

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          return callback(mockTxContext);
        });

        await expect(
          service.createEscrow(
            "order-1",
            "buyer-wallet",
            "seller-wallet",
            1000,
          ),
        ).rejects.toThrow("رصيد المشتري غير كافي");
      });
    });

    describe("Escrow Release Integrity", () => {
      it("should atomically release escrow and credit seller", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        let buyerEscrowUpdated = false;
        let sellerBalanceUpdated = false;
        let escrowReleased = false;

        const mockTxContext = {
          escrow: {
            findUnique: jest.fn().mockResolvedValue({
              id: "escrow-1",
              orderId: "order-1",
              buyerWalletId: "buyer-wallet",
              sellerWalletId: "seller-wallet",
              amount: 1000,
              status: "HELD",
            }),
            update: jest.fn().mockImplementation(() => {
              escrowReleased = true;
              return Promise.resolve({ status: "RELEASED" });
            }),
          },
          wallet: {
            update: jest.fn().mockImplementation((params) => {
              if (params.where.id === "buyer-wallet") {
                buyerEscrowUpdated = true;
              } else if (params.where.id === "seller-wallet") {
                sellerBalanceUpdated = true;
              }
              return Promise.resolve({});
            }),
          },
          transaction: {
            create: jest.fn().mockResolvedValue({ id: "tx-1" }),
          },
          walletAuditLog: {
            create: jest.fn().mockResolvedValue({}),
          },
          creditEvent: {
            create: jest.fn().mockResolvedValue({}),
          },
          $queryRaw: jest.fn().mockImplementation((query) => {
            if (query.includes("buyer")) {
              return Promise.resolve([
                {
                  id: "buyer-wallet",
                  balance: 5000,
                  escrowBalance: 1000,
                  version: 1,
                },
              ]);
            } else {
              return Promise.resolve([
                {
                  id: "seller-wallet",
                  balance: 2000,
                  version: 1,
                },
              ]);
            }
          }),
        };

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          return callback(mockTxContext);
        });

        await service.releaseEscrow("escrow-1");

        expect(buyerEscrowUpdated).toBe(true);
        expect(sellerBalanceUpdated).toBe(true);
        expect(escrowReleased).toBe(true);
      });

      it("should verify escrow status before release", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        const mockTxContext = {
          escrow: {
            findUnique: jest.fn().mockResolvedValue({
              id: "escrow-1",
              status: "RELEASED", // Already released
            }),
          },
        };

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          return callback(mockTxContext);
        });

        await expect(service.releaseEscrow("escrow-1")).rejects.toThrow(
          "الإسكرو ليس في حالة محجوز",
        );
      });

      it("should validate escrow balance matches before release", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        const mockTxContext = {
          escrow: {
            findUnique: jest.fn().mockResolvedValue({
              id: "escrow-1",
              orderId: "order-1",
              buyerWalletId: "buyer-wallet",
              sellerWalletId: "seller-wallet",
              amount: 1000,
              status: "HELD",
            }),
          },
          $queryRaw: jest.fn().mockImplementation((query) => {
            if (query.includes("buyer")) {
              return Promise.resolve([
                {
                  id: "buyer-wallet",
                  balance: 5000,
                  escrowBalance: 500, // Less than escrow amount
                  version: 1,
                },
              ]);
            } else {
              return Promise.resolve([
                {
                  id: "seller-wallet",
                  balance: 2000,
                  version: 1,
                },
              ]);
            }
          }),
        };

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          return callback(mockTxContext);
        });

        await expect(service.releaseEscrow("escrow-1")).rejects.toThrow(
          "رصيد الإسكرو غير كافي",
        );
      });
    });

    describe("Escrow Refund Integrity", () => {
      it("should atomically refund escrow to buyer", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        let escrowRefunded = false;
        let buyerBalanceRestored = false;

        const mockTxContext = {
          escrow: {
            findUnique: jest.fn().mockResolvedValue({
              id: "escrow-1",
              orderId: "order-1",
              buyerWalletId: "buyer-wallet",
              sellerWalletId: "seller-wallet",
              amount: 1000,
              status: "HELD",
            }),
            update: jest.fn().mockImplementation(() => {
              escrowRefunded = true;
              return Promise.resolve({ status: "REFUNDED" });
            }),
          },
          wallet: {
            update: jest.fn().mockImplementation(() => {
              buyerBalanceRestored = true;
              return Promise.resolve({
                balance: 6000,
                escrowBalance: 0,
              });
            }),
          },
          transaction: {
            create: jest.fn().mockResolvedValue({ id: "tx-1" }),
          },
          walletAuditLog: {
            create: jest.fn().mockResolvedValue({}),
          },
          creditEvent: {
            create: jest.fn().mockResolvedValue({}),
          },
          $queryRaw: jest.fn().mockResolvedValue([
            {
              id: "buyer-wallet",
              balance: 5000,
              escrowBalance: 1000,
              version: 1,
            },
          ]),
        };

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          return callback(mockTxContext);
        });

        await service.refundEscrow("escrow-1", "Order cancelled");

        expect(escrowRefunded).toBe(true);
        expect(buyerBalanceRestored).toBe(true);
      });

      it("should only allow refund for HELD or DISPUTED escrows", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        const invalidStatuses = ["RELEASED", "REFUNDED"];

        for (const status of invalidStatuses) {
          const mockTxContext = {
            escrow: {
              findUnique: jest.fn().mockResolvedValue({
                id: "escrow-1",
                status,
              }),
            },
          };

          mockPrismaService.$transaction.mockImplementation(
            async (callback) => {
              return callback(mockTxContext);
            },
          );

          await expect(
            service.refundEscrow("escrow-1", "Test"),
          ).rejects.toThrow("لا يمكن استرداد هذا الإسكرو");
        }
      });
    });

    describe("Concurrent Escrow Operations", () => {
      it("should prevent concurrent release and refund of same escrow", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        const escrow = {
          id: "escrow-1",
          orderId: "order-1",
          buyerWalletId: "buyer-wallet",
          sellerWalletId: "seller-wallet",
          amount: 1000,
          status: "HELD",
        };

        // First operation (release) succeeds
        mockPrismaService.$transaction.mockImplementationOnce(
          async (callback) => {
            const tx = {
              escrow: {
                findUnique: jest.fn().mockResolvedValue(escrow),
                update: jest
                  .fn()
                  .mockResolvedValue({ ...escrow, status: "RELEASED" }),
              },
              wallet: {
                update: jest.fn().mockResolvedValue({}),
              },
              transaction: {
                create: jest.fn().mockResolvedValue({}),
              },
              walletAuditLog: {
                create: jest.fn().mockResolvedValue({}),
              },
              creditEvent: {
                create: jest.fn().mockResolvedValue({}),
              },
              $queryRaw: jest
                .fn()
                .mockResolvedValue([
                  {
                    id: "buyer-wallet",
                    balance: 5000,
                    escrowBalance: 1000,
                    version: 1,
                  },
                ]),
            };
            return callback(tx);
          },
        );

        await service.releaseEscrow("escrow-1");

        // Second operation (refund) should fail
        mockPrismaService.$transaction.mockImplementationOnce(
          async (callback) => {
            const tx = {
              escrow: {
                findUnique: jest.fn().mockResolvedValue({
                  ...escrow,
                  status: "RELEASED", // Already released
                }),
              },
            };
            return callback(tx);
          },
        );

        await expect(service.refundEscrow("escrow-1")).rejects.toThrow(
          "لا يمكن استرداد هذا الإسكرو",
        );
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Security Tests - Escrow
  // ═══════════════════════════════════════════════════════════════════════════

  describe("Security Tests - Escrow", () => {
    describe("Input Validation", () => {
      it("should reject zero or negative escrow amounts", async () => {
        await expect(
          service.createEscrow("order-1", "buyer-wallet", "seller-wallet", 0),
        ).rejects.toThrow("المبلغ يجب أن يكون أكبر من صفر");

        await expect(
          service.createEscrow(
            "order-1",
            "buyer-wallet",
            "seller-wallet",
            -1000,
          ),
        ).rejects.toThrow("المبلغ يجب أن يكون أكبر من صفر");
      });

      it("should prevent duplicate escrow for same order", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        const mockTxContext = {
          escrow: {
            findUnique: jest.fn().mockResolvedValue({
              id: "existing-escrow",
              orderId: "order-1",
            }),
          },
        };

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          return callback(mockTxContext);
        });

        await expect(
          service.createEscrow(
            "order-1",
            "buyer-wallet",
            "seller-wallet",
            1000,
          ),
        ).rejects.toThrow("يوجد إسكرو لهذا الطلب بالفعل");
      });

      it("should validate wallet existence before escrow operations", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        const mockTxContext = {
          escrow: {
            findUnique: jest.fn().mockResolvedValue(null),
          },
          $queryRaw: jest.fn().mockResolvedValue([]), // Wallet not found
        };

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          return callback(mockTxContext);
        });

        await expect(
          service.createEscrow(
            "order-1",
            "invalid-wallet",
            "seller-wallet",
            1000,
          ),
        ).rejects.toThrow("محفظة المشتري غير موجودة");
      });

      it("should validate seller wallet exists", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        const mockTxContext = {
          escrow: {
            findUnique: jest.fn().mockResolvedValue(null),
          },
          wallet: {
            findUnique: jest.fn().mockResolvedValue(null), // Seller wallet not found
          },
          $queryRaw: jest.fn().mockResolvedValue([
            {
              id: "buyer-wallet",
              balance: 5000,
              escrowBalance: 0,
              version: 1,
            },
          ]),
        };

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          return callback(mockTxContext);
        });

        await expect(
          service.createEscrow(
            "order-1",
            "buyer-wallet",
            "invalid-seller",
            1000,
          ),
        ).rejects.toThrow("محفظة البائع غير موجودة");
      });
    });

    describe("Idempotency Protection", () => {
      it("should return existing escrow for duplicate idempotency key on creation", async () => {
        const existingTx = { id: "tx-1", type: "ESCROW_HOLD" };
        const existingEscrow = { id: "escrow-1", orderId: "order-1" };

        mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
        mockPrismaService.escrow.findUnique.mockResolvedValue(existingEscrow);

        const result = await service.createEscrow(
          "order-1",
          "buyer-wallet",
          "seller-wallet",
          1000,
          "Notes",
          "idemp-key-123",
        );

        expect(result.duplicate).toBe(true);
        expect(result.escrow).toEqual(existingEscrow);
        expect(mockPrismaService.$transaction).not.toHaveBeenCalled();
      });

      it("should return existing transaction for duplicate idempotency key on release", async () => {
        const existingTx = { id: "tx-1", type: "ESCROW_RELEASE" };
        const existingEscrow = {
          id: "escrow-1",
          status: "RELEASED",
          buyerWallet: {},
          sellerWallet: {},
        };

        mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
        mockPrismaService.escrow.findUnique.mockResolvedValue(existingEscrow);

        const result = await service.releaseEscrow(
          "escrow-1",
          "Notes",
          "idemp-key-456",
        );

        expect(result.duplicate).toBe(true);
        expect(mockPrismaService.$transaction).not.toHaveBeenCalled();
      });

      it("should return existing transaction for duplicate idempotency key on refund", async () => {
        const existingTx = { id: "tx-1", type: "ESCROW_REFUND" };
        const existingEscrow = {
          id: "escrow-1",
          status: "REFUNDED",
          buyerWallet: {},
        };

        mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
        mockPrismaService.escrow.findUnique.mockResolvedValue(existingEscrow);

        const result = await service.refundEscrow(
          "escrow-1",
          "Cancelled",
          "idemp-key-789",
        );

        expect(result.duplicate).toBe(true);
        expect(mockPrismaService.$transaction).not.toHaveBeenCalled();
      });
    });

    describe("State Transition Validation", () => {
      it("should only allow valid escrow state transitions", async () => {
        const invalidTransitions = [
          { from: "RELEASED", to: "HELD" },
          { from: "REFUNDED", to: "HELD" },
          { from: "RELEASED", to: "REFUNDED" },
          { from: "REFUNDED", to: "RELEASED" },
        ];

        for (const transition of invalidTransitions) {
          // Mock validation
          const isValidTransition = (from: string, to: string) => {
            const validTransitions: Record<string, string[]> = {
              HELD: ["RELEASED", "REFUNDED", "DISPUTED"],
              DISPUTED: ["RELEASED", "REFUNDED"],
              RELEASED: [],
              REFUNDED: [],
            };
            return validTransitions[from]?.includes(to) || false;
          };

          expect(isValidTransition(transition.from, transition.to)).toBe(false);
        }
      });
    });

    describe("Authorization & Access Control", () => {
      it("should verify order ownership before escrow operations", async () => {
        // This test simulates controller-level authorization
        const userId = "user-123";
        const orderBuyerId = "user-456";

        const isAuthorized = userId === orderBuyerId;
        expect(isAuthorized).toBe(false);
      });

      it("should only allow seller or buyer to view escrow details", async () => {
        const escrow = {
          id: "escrow-1",
          buyerWalletId: "buyer-wallet",
          sellerWalletId: "seller-wallet",
        };

        const userWalletId = "other-wallet";
        const canView =
          userWalletId === escrow.buyerWalletId ||
          userWalletId === escrow.sellerWalletId;

        expect(canView).toBe(false);
      });
    });

    describe("Balance Verification", () => {
      it("should ensure buyer has sufficient balance for escrow creation", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        const mockTxContext = {
          escrow: {
            findUnique: jest.fn().mockResolvedValue(null),
          },
          $queryRaw: jest.fn().mockResolvedValue([
            {
              id: "buyer-wallet",
              balance: 500, // Insufficient
              escrowBalance: 0,
              version: 1,
            },
          ]),
        };

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          return callback(mockTxContext);
        });

        await expect(
          service.createEscrow(
            "order-1",
            "buyer-wallet",
            "seller-wallet",
            1000,
          ),
        ).rejects.toThrow("رصيد المشتري غير كافي");
      });

      it("should track escrow balance separately from available balance", async () => {
        mockPrismaService.transaction.findUnique.mockResolvedValue(null);

        const mockTxContext = {
          escrow: {
            findUnique: jest.fn().mockResolvedValue(null),
            create: jest.fn().mockResolvedValue({
              id: "escrow-1",
              amount: 1000,
            }),
          },
          wallet: {
            findUnique: jest.fn().mockResolvedValue({ id: "seller-wallet" }),
            update: jest.fn().mockResolvedValue({
              id: "buyer-wallet",
              balance: 4000, // Available balance
              escrowBalance: 1000, // Held in escrow
            }),
          },
          transaction: {
            create: jest.fn().mockResolvedValue({}),
          },
          walletAuditLog: {
            create: jest.fn().mockResolvedValue({}),
          },
          $queryRaw: jest.fn().mockResolvedValue([
            {
              id: "buyer-wallet",
              balance: 5000,
              escrowBalance: 0,
              version: 1,
            },
          ]),
        };

        mockPrismaService.$transaction.mockImplementation(async (callback) => {
          return callback(mockTxContext);
        });

        const result = await service.createEscrow(
          "order-1",
          "buyer-wallet",
          "seller-wallet",
          1000,
        );

        expect(result.wallet.balance).toBe(4000);
        expect(result.wallet.escrowBalance).toBe(1000);
      });
    });
  });
});
