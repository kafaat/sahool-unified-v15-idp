/**
 * SAHOOL Payment Service Tests
 * اختبارات خدمة الدفع
 *
 * Tests for:
 * - Wallet operations (deposit, withdraw)
 * - Payment processing
 * - Escrow management
 * - Transaction history
 * - Wallet limits and security
 * - Idempotency protection
 * - Audit logging
 */

import { Test, TestingModule } from '@nestjs/testing';
import { WalletService } from '../fintech/wallet.service';
import { EscrowService } from '../fintech/escrow.service';
import { FintechService } from '../fintech/fintech.service';
import { PrismaService } from '../prisma/prisma.service';
import { CreditService } from '../fintech/credit.service';
import { LoanService } from '../fintech/loan.service';
import { NotFoundException, BadRequestException } from '@nestjs/common';

describe('Payment Service - Wallet Operations', () => {
  let walletService: WalletService;
  let escrowService: EscrowService;
  let fintechService: FintechService;
  let prismaService: PrismaService;

  const mockPrismaService = {
    wallet: {
      findUnique: jest.fn(),
      findMany: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      count: jest.fn(),
      aggregate: jest.fn(),
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
      findUnique: jest.fn(),
      findMany: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
    },
    scheduledPayment: {
      findMany: jest.fn(),
    },
    loan: {
      count: jest.fn(),
    },
    $transaction: jest.fn(),
    $queryRaw: jest.fn(),
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

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        WalletService,
        EscrowService,
        FintechService,
        {
          provide: PrismaService,
          useValue: mockPrismaService,
        },
        {
          provide: CreditService,
          useValue: mockCreditService,
        },
        {
          provide: LoanService,
          useValue: mockLoanService,
        },
      ],
    }).compile();

    walletService = module.get<WalletService>(WalletService);
    escrowService = module.get<EscrowService>(EscrowService);
    fintechService = module.get<FintechService>(FintechService);
    prismaService = module.get<PrismaService>(PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Wallet Management Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('getWallet', () => {
    it('should return existing wallet', async () => {
      const mockWallet = {
        id: 'wallet-1',
        userId: 'user-123',
        userType: 'farmer',
        balance: 10000,
        escrowBalance: 2000,
        creditScore: 650,
        creditTier: 'SILVER',
        loanLimit: 50000,
        currentLoan: 10000,
        dailyWithdrawLimit: 20000,
        singleTransactionLimit: 100000,
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      const result = await walletService.getWallet('user-123');

      expect(result).toMatchObject({
        id: 'wallet-1',
        balance: 10000,
        creditScore: 650,
        creditTier: 'SILVER',
      });
      expect(result.creditTierAr).toBe('فضي');
      expect(result.availableCredit).toBe(40000); // loanLimit - currentLoan
    });

    it('should create wallet if it does not exist', async () => {
      const mockNewWallet = {
        id: 'wallet-2',
        userId: 'new-user-456',
        userType: 'farmer',
        balance: 0,
        creditScore: 300,
        creditTier: 'BRONZE',
        loanLimit: 10000,
        currentLoan: 0,
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(null);
      mockPrismaService.wallet.create.mockResolvedValue(mockNewWallet);

      const result = await walletService.getWallet('new-user-456');

      expect(result.balance).toBe(0);
      expect(result.creditScore).toBe(300);
      expect(result.creditTier).toBe('BRONZE');
      expect(mockPrismaService.wallet.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            userId: 'new-user-456',
            userType: 'farmer',
            balance: 0,
            creditScore: 300,
            creditTier: 'BRONZE',
          }),
        })
      );
    });

    it('should support different user types', async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);
      mockPrismaService.wallet.create.mockResolvedValue({
        id: 'wallet-3',
        userId: 'company-789',
        userType: 'company',
      });

      await walletService.getWallet('company-789', 'company');

      expect(mockPrismaService.wallet.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            userType: 'company',
          }),
        })
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Deposit Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('deposit', () => {
    it('should deposit money to wallet', async () => {
      const walletData = {
        id: 'wallet-1',
        balance: 10000,
        version: 1,
      };

      const updatedWallet = {
        ...walletData,
        balance: 15000,
        version: 2,
      };

      const transaction = {
        id: 'tx-1',
        walletId: 'wallet-1',
        type: 'DEPOSIT',
        amount: 5000,
        balanceBefore: 10000,
        balanceAfter: 15000,
        status: 'COMPLETED',
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          $queryRaw: jest.fn().mockResolvedValue([walletData]),
          wallet: {
            update: jest.fn().mockResolvedValue(updatedWallet),
          },
          transaction: {
            create: jest.fn().mockResolvedValue(transaction),
          },
          walletAuditLog: {
            create: jest.fn().mockResolvedValue({}),
          },
        };
        return callback(tx);
      });

      const result = await walletService.deposit('wallet-1', 5000, 'Test deposit');

      expect(result.wallet.balance).toBe(15000);
      expect(result.transaction.amount).toBe(5000);
      expect(result.duplicate).toBe(false);
    });

    it('should prevent duplicate deposits with idempotency key', async () => {
      const existingTransaction = {
        id: 'tx-existing',
        idempotencyKey: 'key-123',
        amount: 5000,
      };

      const wallet = {
        id: 'wallet-1',
        balance: 15000,
      };

      mockPrismaService.transaction.findUnique.mockResolvedValue(existingTransaction);
      mockPrismaService.wallet.findUnique.mockResolvedValue(wallet);

      const result = await walletService.deposit(
        'wallet-1',
        5000,
        'Duplicate deposit',
        'key-123'
      );

      expect(result.duplicate).toBe(true);
      expect(result.transaction).toEqual(existingTransaction);
      expect(mockPrismaService.$transaction).not.toHaveBeenCalled();
    });

    it('should reject negative deposit amounts', async () => {
      await expect(walletService.deposit('wallet-1', -100)).rejects.toThrow(
        BadRequestException
      );
      await expect(walletService.deposit('wallet-1', -100)).rejects.toThrow(
        'المبلغ يجب أن يكون أكبر من صفر'
      );
    });

    it('should reject zero deposit amounts', async () => {
      await expect(walletService.deposit('wallet-1', 0)).rejects.toThrow(
        BadRequestException
      );
    });

    it('should create audit log for deposit', async () => {
      const walletData = {
        id: 'wallet-1',
        balance: 10000,
        version: 1,
      };

      const auditLogCreate = jest.fn().mockResolvedValue({});

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          $queryRaw: jest.fn().mockResolvedValue([walletData]),
          wallet: {
            update: jest.fn().mockResolvedValue({ ...walletData, balance: 15000 }),
          },
          transaction: {
            create: jest.fn().mockResolvedValue({ id: 'tx-1' }),
          },
          walletAuditLog: {
            create: auditLogCreate,
          },
        };
        return callback(tx);
      });

      await walletService.deposit('wallet-1', 5000, 'Test', 'key-1', 'user-1', '1.2.3.4');

      expect(auditLogCreate).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            walletId: 'wallet-1',
            userId: 'user-1',
            operation: 'DEPOSIT',
            amount: 5000,
            ipAddress: '1.2.3.4',
          }),
        })
      );
    });

    it('should use SERIALIZABLE isolation level for deposits', async () => {
      const walletData = {
        id: 'wallet-1',
        balance: 10000,
        version: 1,
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          $queryRaw: jest.fn().mockResolvedValue([walletData]),
          wallet: {
            update: jest.fn().mockResolvedValue({}),
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

      await walletService.deposit('wallet-1', 5000);

      expect(mockPrismaService.$transaction).toHaveBeenCalledWith(
        expect.any(Function),
        expect.objectContaining({
          isolationLevel: 'Serializable',
        })
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Withdrawal Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('withdraw', () => {
    it('should withdraw money from wallet', async () => {
      const walletData = {
        id: 'wallet-1',
        balance: 10000,
        version: 1,
        dailyWithdrawLimit: 20000,
        singleTransactionLimit: 100000,
        dailyWithdrawnToday: 0,
        lastWithdrawReset: new Date(),
      };

      const updatedWallet = {
        ...walletData,
        balance: 7000,
        version: 2,
        dailyWithdrawnToday: 3000,
      };

      const transaction = {
        id: 'tx-1',
        type: 'WITHDRAWAL',
        amount: -3000,
        balanceBefore: 10000,
        balanceAfter: 7000,
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          $queryRaw: jest.fn().mockResolvedValue([walletData]),
          wallet: {
            update: jest.fn().mockResolvedValue(updatedWallet),
          },
          transaction: {
            create: jest.fn().mockResolvedValue(transaction),
          },
          walletAuditLog: {
            create: jest.fn().mockResolvedValue({}),
          },
        };
        return callback(tx);
      });

      const result = await walletService.withdraw('wallet-1', 3000, 'Test withdrawal');

      expect(result.wallet.balance).toBe(7000);
      expect(result.transaction.amount).toBe(-3000);
      expect(result.duplicate).toBe(false);
    });

    it('should reject withdrawal when balance is insufficient', async () => {
      const walletData = {
        id: 'wallet-1',
        balance: 1000,
        version: 1,
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          $queryRaw: jest.fn().mockResolvedValue([walletData]),
        };
        return callback(tx);
      });

      await expect(
        walletService.withdraw('wallet-1', 5000)
      ).rejects.toThrow(BadRequestException);

      await expect(
        walletService.withdraw('wallet-1', 5000)
      ).rejects.toThrow('الرصيد غير كافي');
    });

    it('should reject negative withdrawal amounts', async () => {
      await expect(walletService.withdraw('wallet-1', -100)).rejects.toThrow(
        BadRequestException
      );
    });

    it('should enforce daily withdrawal limits', async () => {
      const walletData = {
        id: 'wallet-1',
        balance: 100000,
        version: 1,
        dailyWithdrawLimit: 20000,
        singleTransactionLimit: 100000,
        dailyWithdrawnToday: 15000,
        lastWithdrawReset: new Date(),
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          $queryRaw: jest.fn().mockResolvedValue([walletData]),
        };
        return callback(tx);
      });

      await expect(
        walletService.withdraw('wallet-1', 10000)
      ).rejects.toThrow('تجاوزت حد السحب اليومي');
    });

    it('should enforce single transaction limits', async () => {
      const walletData = {
        id: 'wallet-1',
        balance: 200000,
        version: 1,
        dailyWithdrawLimit: 100000,
        singleTransactionLimit: 50000,
        dailyWithdrawnToday: 0,
        lastWithdrawReset: new Date(),
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          $queryRaw: jest.fn().mockResolvedValue([walletData]),
        };
        return callback(tx);
      });

      await expect(
        walletService.withdraw('wallet-1', 60000)
      ).rejects.toThrow('المبلغ يتجاوز حد المعاملة الواحدة');
    });

    it('should reset daily withdrawal counter on new day', async () => {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);

      const walletData = {
        id: 'wallet-1',
        balance: 50000,
        version: 1,
        dailyWithdrawLimit: 20000,
        singleTransactionLimit: 100000,
        dailyWithdrawnToday: 19000,
        lastWithdrawReset: yesterday,
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          $queryRaw: jest.fn().mockResolvedValue([walletData]),
          wallet: {
            update: jest.fn().mockResolvedValue({
              ...walletData,
              balance: 40000,
              dailyWithdrawnToday: 10000,
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

      const result = await walletService.withdraw('wallet-1', 10000);

      expect(result.wallet.dailyWithdrawnToday).toBe(10000);
    });

    it('should prevent duplicate withdrawals with idempotency key', async () => {
      const existingTransaction = {
        id: 'tx-existing',
        idempotencyKey: 'key-456',
        amount: -3000,
      };

      const wallet = {
        id: 'wallet-1',
        balance: 7000,
      };

      mockPrismaService.transaction.findUnique.mockResolvedValue(existingTransaction);
      mockPrismaService.wallet.findUnique.mockResolvedValue(wallet);

      const result = await walletService.withdraw(
        'wallet-1',
        3000,
        'Duplicate withdrawal',
        'key-456'
      );

      expect(result.duplicate).toBe(true);
      expect(result.transaction).toEqual(existingTransaction);
    });

    it('should use optimistic locking to prevent race conditions', async () => {
      const walletData = {
        id: 'wallet-1',
        balance: 10000,
        version: 5,
        dailyWithdrawLimit: 20000,
        singleTransactionLimit: 100000,
        dailyWithdrawnToday: 0,
        lastWithdrawReset: new Date(),
      };

      const updateMock = jest.fn().mockResolvedValue({});

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          $queryRaw: jest.fn().mockResolvedValue([walletData]),
          wallet: {
            update: updateMock,
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

      await walletService.withdraw('wallet-1', 1000);

      expect(updateMock).toHaveBeenCalledWith(
        expect.objectContaining({
          where: {
            id: 'wallet-1',
            version: 5,
          },
        })
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Transaction History Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('getTransactions', () => {
    it('should return transaction history', async () => {
      const mockTransactions = [
        {
          id: 'tx-1',
          type: 'DEPOSIT',
          amount: 5000,
          balanceAfter: 15000,
          createdAt: new Date(),
        },
        {
          id: 'tx-2',
          type: 'WITHDRAWAL',
          amount: -2000,
          balanceAfter: 13000,
          createdAt: new Date(),
        },
      ];

      mockPrismaService.transaction.findMany.mockResolvedValue(mockTransactions);

      const result = await walletService.getTransactions('wallet-1');

      expect(result).toEqual(mockTransactions);
      expect(mockPrismaService.transaction.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { walletId: 'wallet-1' },
          orderBy: { createdAt: 'desc' },
          take: 20,
        })
      );
    });

    it('should support custom limit', async () => {
      mockPrismaService.transaction.findMany.mockResolvedValue([]);

      await walletService.getTransactions('wallet-1', 50);

      expect(mockPrismaService.transaction.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          take: 50,
        })
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Wallet Limits Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Wallet Limits', () => {
    it('should return wallet limits', async () => {
      const mockWallet = {
        id: 'wallet-1',
        dailyWithdrawLimit: 20000,
        singleTransactionLimit: 100000,
        requiresPinForAmount: 10000,
        creditTier: 'SILVER',
        dailyWithdrawnToday: 5000,
        lastWithdrawReset: new Date(),
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      const result = await walletService.getWalletLimits('wallet-1');

      expect(result).toEqual({
        dailyWithdrawLimit: 20000,
        dailyRemaining: 15000,
        singleTransactionLimit: 100000,
        requiresPinForAmount: 10000,
        creditTier: 'SILVER',
      });
    });

    it('should throw error for non-existent wallet', async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);

      await expect(walletService.getWalletLimits('non-existent')).rejects.toThrow(
        NotFoundException
      );
    });

    it('should update wallet limits based on credit tier - PLATINUM', async () => {
      const mockWallet = {
        id: 'wallet-1',
        creditTier: 'PLATINUM',
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);
      mockPrismaService.wallet.update.mockResolvedValue({
        ...mockWallet,
        dailyWithdrawLimit: 100000,
        singleTransactionLimit: 500000,
        requiresPinForAmount: 50000,
      });

      const result = await walletService.updateWalletLimits('wallet-1');

      expect(result.dailyWithdrawLimit).toBe(100000);
      expect(result.singleTransactionLimit).toBe(500000);
      expect(result.requiresPinForAmount).toBe(50000);
    });

    it('should update wallet limits based on credit tier - GOLD', async () => {
      const mockWallet = {
        id: 'wallet-1',
        creditTier: 'GOLD',
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);
      mockPrismaService.wallet.update.mockResolvedValue({
        ...mockWallet,
        dailyWithdrawLimit: 50000,
        singleTransactionLimit: 200000,
        requiresPinForAmount: 20000,
      });

      const result = await walletService.updateWalletLimits('wallet-1');

      expect(result.dailyWithdrawLimit).toBe(50000);
    });

    it('should update wallet limits based on credit tier - BRONZE (default)', async () => {
      const mockWallet = {
        id: 'wallet-1',
        creditTier: 'BRONZE',
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);
      mockPrismaService.wallet.update.mockResolvedValue({
        ...mockWallet,
        dailyWithdrawLimit: 10000,
        singleTransactionLimit: 50000,
        requiresPinForAmount: 5000,
      });

      const result = await walletService.updateWalletLimits('wallet-1');

      expect(result.dailyWithdrawLimit).toBe(10000);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Escrow Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Escrow Management', () => {
    it('should create escrow and hold funds', async () => {
      const mockEscrow = {
        id: 'escrow-1',
        orderId: 'order-1',
        buyerWalletId: 'wallet-buyer',
        sellerWalletId: 'wallet-seller',
        amount: 10000,
        status: 'HELD',
        createdAt: new Date(),
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          $queryRaw: jest.fn().mockResolvedValue([
            { id: 'wallet-buyer', balance: 50000, version: 1 },
          ]),
          wallet: {
            update: jest.fn().mockResolvedValue({}),
          },
          escrow: {
            create: jest.fn().mockResolvedValue(mockEscrow),
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

      const result = await escrowService.createEscrow(
        'order-1',
        'wallet-buyer',
        'wallet-seller',
        10000
      );

      expect(result.amount).toBe(10000);
      expect(result.status).toBe('HELD');
    });

    it('should get escrow by order ID', async () => {
      const mockEscrow = {
        id: 'escrow-1',
        orderId: 'order-1',
        amount: 10000,
        status: 'HELD',
      };

      mockPrismaService.escrow.findUnique.mockResolvedValue(mockEscrow);

      const result = await escrowService.getEscrowByOrder('order-1');

      expect(result).toEqual(mockEscrow);
    });

    it('should get wallet escrows', async () => {
      const mockEscrows = [
        {
          id: 'escrow-1',
          buyerWalletId: 'wallet-1',
          amount: 5000,
          status: 'HELD',
        },
        {
          id: 'escrow-2',
          sellerWalletId: 'wallet-1',
          amount: 3000,
          status: 'HELD',
        },
      ];

      mockPrismaService.escrow.findMany.mockResolvedValue(mockEscrows);

      const result = await escrowService.getWalletEscrows('wallet-1');

      expect(result).toHaveLength(2);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Wallet Dashboard Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Wallet Dashboard', () => {
    it('should return comprehensive wallet dashboard', async () => {
      const mockWallet = {
        id: 'wallet-1',
        balance: 50000,
        escrowBalance: 5000,
        creditScore: 700,
        creditTier: 'GOLD',
        loanLimit: 100000,
        currentLoan: 20000,
        dailyWithdrawLimit: 50000,
        singleTransactionLimit: 200000,
        dailyWithdrawnToday: 10000,
        lastWithdrawReset: new Date(),
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);
      mockPrismaService.escrow.findMany
        .mockResolvedValueOnce([]) // buyer escrows
        .mockResolvedValueOnce([]); // seller escrows
      mockPrismaService.scheduledPayment.findMany.mockResolvedValue([]);
      mockPrismaService.transaction.findMany.mockResolvedValue([]);

      const result = await walletService.getWalletDashboard('wallet-1');

      expect(result.wallet.balance).toBe(50000);
      expect(result.wallet.creditScore).toBe(700);
      expect(result.summary.availableCredit).toBe(80000);
      expect(result.limits.dailyRemaining).toBe(40000);
    });

    it('should calculate escrow balances correctly', async () => {
      const mockWallet = {
        id: 'wallet-1',
        balance: 50000,
        escrowBalance: 0,
        creditScore: 650,
        creditTier: 'SILVER',
        loanLimit: 50000,
        currentLoan: 0,
        dailyWithdrawLimit: 20000,
        singleTransactionLimit: 100000,
        dailyWithdrawnToday: 0,
        lastWithdrawReset: new Date(),
      };

      const buyerEscrows = [
        { amount: 5000 },
        { amount: 3000 },
      ];

      const sellerEscrows = [
        { amount: 10000 },
      ];

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);
      mockPrismaService.escrow.findMany
        .mockResolvedValueOnce(buyerEscrows)
        .mockResolvedValueOnce(sellerEscrows);
      mockPrismaService.scheduledPayment.findMany.mockResolvedValue([]);
      mockPrismaService.transaction.findMany.mockResolvedValue([]);

      const result = await walletService.getWalletDashboard('wallet-1');

      expect(result.summary.inEscrowAsBuyer).toBe(8000);
      expect(result.summary.inEscrowAsSeller).toBe(10000);
    });

    it('should include monthly transaction chart', async () => {
      const mockWallet = {
        id: 'wallet-1',
        balance: 50000,
        escrowBalance: 0,
        creditScore: 650,
        creditTier: 'SILVER',
        loanLimit: 50000,
        currentLoan: 0,
        dailyWithdrawLimit: 20000,
        singleTransactionLimit: 100000,
        dailyWithdrawnToday: 0,
        lastWithdrawReset: new Date(),
      };

      const mockTransactions = [
        {
          amount: 5000,
          createdAt: new Date('2024-01-15'),
        },
        {
          amount: -2000,
          createdAt: new Date('2024-01-15'),
        },
      ];

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);
      mockPrismaService.escrow.findMany
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce([]);
      mockPrismaService.scheduledPayment.findMany.mockResolvedValue([]);
      mockPrismaService.transaction.findMany.mockResolvedValue(mockTransactions);

      const result = await walletService.getWalletDashboard('wallet-1');

      expect(result.monthlyChart).toBeDefined();
      expect(Array.isArray(result.monthlyChart)).toBe(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FinTech Service Integration Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('FintechService Integration', () => {
    it('should delegate wallet operations to WalletService', async () => {
      const mockWallet = {
        id: 'wallet-1',
        balance: 10000,
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      const result = await fintechService.getWallet('user-123');

      expect(result).toBeDefined();
    });

    it('should return finance statistics', async () => {
      mockPrismaService.wallet.count.mockResolvedValue(100);
      mockPrismaService.wallet.aggregate.mockResolvedValue({
        _sum: { balance: 1000000 },
        _avg: { creditScore: 650 },
      });
      mockPrismaService.loan.count
        .mockResolvedValueOnce(20) // active loans
        .mockResolvedValueOnce(80); // paid loans

      const result = await fintechService.getFinanceStats();

      expect(result).toEqual({
        totalWallets: 100,
        totalBalance: 1000000,
        activeLoans: 20,
        paidLoans: 80,
        avgCreditScore: 650,
      });
    });
  });
});
