/**
 * SAHOOL Wallet Service Tests
 * اختبارات خدمة المحفظة
 */

import { Test, TestingModule } from '@nestjs/testing';
import { WalletService } from './wallet.service';
import { PrismaService } from '../prisma/prisma.service';
import { BadRequestException, NotFoundException } from '@nestjs/common';

describe('WalletService', () => {
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

  describe('getWallet', () => {
    it('should return existing wallet with Arabic tier translation', async () => {
      const mockWallet = {
        id: 'wallet-1',
        userId: 'user-123',
        balance: 5000,
        creditScore: 650,
        creditTier: 'GOLD',
        loanLimit: 22750,
        currentLoan: 0,
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      const result = await service.getWallet('user-123');

      expect(result).toEqual(expect.objectContaining({
        id: 'wallet-1',
        balance: 5000,
        creditTierAr: 'ذهبي',
        availableCredit: 22750,
      }));
    });

    it('should create new wallet if not exists', async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);

      const newWallet = {
        id: 'wallet-new',
        userId: 'user-new',
        balance: 0,
        creditScore: 300,
        creditTier: 'BRONZE',
        loanLimit: 0,
        currentLoan: 0,
      };

      mockPrismaService.wallet.create.mockResolvedValue(newWallet);

      const result = await service.getWallet('user-new', 'farmer');

      expect(mockPrismaService.wallet.create).toHaveBeenCalledWith({
        data: {
          userId: 'user-new',
          userType: 'farmer',
          balance: 0,
          creditScore: 300,
          creditTier: 'BRONZE',
        },
      });
      expect(result.creditTierAr).toBe('برونزي');
    });
  });

  describe('getCreditTierAr', () => {
    it('should translate credit tiers to Arabic', () => {
      expect(service.getCreditTierAr('BRONZE')).toBe('برونزي');
      expect(service.getCreditTierAr('SILVER')).toBe('فضي');
      expect(service.getCreditTierAr('GOLD')).toBe('ذهبي');
      expect(service.getCreditTierAr('PLATINUM')).toBe('بلاتيني');
      expect(service.getCreditTierAr('UNKNOWN')).toBe('UNKNOWN');
    });
  });

  describe('deposit', () => {
    it('should throw error for zero or negative amount', async () => {
      await expect(service.deposit('wallet-1', 0)).rejects.toThrow(BadRequestException);
      await expect(service.deposit('wallet-1', -100)).rejects.toThrow(BadRequestException);
    });

    it('should return existing transaction for duplicate idempotency key', async () => {
      const existingTx = { id: 'tx-1', type: 'DEPOSIT', amount: 500 };
      const existingWallet = { id: 'wallet-1', balance: 1500 };

      mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
      mockPrismaService.wallet.findUnique.mockResolvedValue(existingWallet);

      const result = await service.deposit('wallet-1', 500, 'Test', 'idemp-key-1');

      expect(result.duplicate).toBe(true);
      expect(result.transaction).toEqual(existingTx);
    });

    it('should deposit amount with audit logging', async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        $queryRaw: jest.fn().mockResolvedValue([{
          id: 'wallet-1',
          balance: 1000,
          version: 1,
        }]),
        wallet: {
          update: jest.fn().mockResolvedValue({
            id: 'wallet-1',
            balance: 1500,
            version: 2,
          }),
        },
        transaction: {
          create: jest.fn().mockResolvedValue({
            id: 'tx-1',
            type: 'DEPOSIT',
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

      const result = await service.deposit('wallet-1', 500, 'Test deposit');

      expect(result.duplicate).toBe(false);
      expect(result.wallet.balance).toBe(1500);
    });
  });

  describe('withdraw', () => {
    it('should throw error for zero or negative amount', async () => {
      await expect(service.withdraw('wallet-1', 0)).rejects.toThrow(BadRequestException);
      await expect(service.withdraw('wallet-1', -100)).rejects.toThrow(BadRequestException);
    });

    it('should throw error for insufficient balance', async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        $queryRaw: jest.fn().mockResolvedValue([{
          id: 'wallet-1',
          balance: 100,
          version: 1,
          singleTransactionLimit: 50000,
          dailyWithdrawLimit: 10000,
          dailyWithdrawnToday: 0,
        }]),
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      await expect(service.withdraw('wallet-1', 500)).rejects.toThrow(BadRequestException);
    });

    it('should return existing transaction for duplicate idempotency key', async () => {
      const existingTx = { id: 'tx-1', type: 'WITHDRAWAL', amount: -500 };
      const existingWallet = { id: 'wallet-1', balance: 500 };

      mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
      mockPrismaService.wallet.findUnique.mockResolvedValue(existingWallet);

      const result = await service.withdraw('wallet-1', 500, 'Test', 'idemp-key-1');

      expect(result.duplicate).toBe(true);
    });
  });

  describe('getTransactions', () => {
    it('should return wallet transactions', async () => {
      const mockTransactions = [
        { id: 'tx-1', type: 'DEPOSIT', amount: 500 },
        { id: 'tx-2', type: 'WITHDRAWAL', amount: -200 },
      ];

      mockPrismaService.transaction.findMany.mockResolvedValue(mockTransactions);

      const result = await service.getTransactions('wallet-1', 10);

      expect(mockPrismaService.transaction.findMany).toHaveBeenCalledWith({
        where: { walletId: 'wallet-1' },
        orderBy: { createdAt: 'desc' },
        take: 10,
      });
      expect(result).toEqual(mockTransactions);
    });
  });

  describe('getWalletLimits', () => {
    it('should return wallet limits', async () => {
      const mockWallet = {
        id: 'wallet-1',
        dailyWithdrawLimit: 10000,
        dailyWithdrawnToday: 2000,
        singleTransactionLimit: 50000,
        requiresPinForAmount: 5000,
        creditTier: 'SILVER',
        lastWithdrawReset: new Date(),
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      const result = await service.getWalletLimits('wallet-1');

      expect(result.dailyWithdrawLimit).toBe(10000);
      expect(result.singleTransactionLimit).toBe(50000);
    });

    it('should throw error for non-existent wallet', async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);

      await expect(service.getWalletLimits('wallet-999')).rejects.toThrow(NotFoundException);
    });
  });

  describe('updateWalletLimits', () => {
    it('should update limits based on credit tier', async () => {
      const testCases = [
        { tier: 'PLATINUM', daily: 100000, single: 500000, pin: 50000 },
        { tier: 'GOLD', daily: 50000, single: 200000, pin: 20000 },
        { tier: 'SILVER', daily: 20000, single: 100000, pin: 10000 },
        { tier: 'BRONZE', daily: 10000, single: 50000, pin: 5000 },
      ];

      for (const testCase of testCases) {
        mockPrismaService.wallet.findUnique.mockResolvedValue({
          id: 'wallet-1',
          creditTier: testCase.tier,
        });

        mockPrismaService.wallet.update.mockResolvedValue({
          id: 'wallet-1',
          dailyWithdrawLimit: testCase.daily,
          singleTransactionLimit: testCase.single,
          requiresPinForAmount: testCase.pin,
        });

        await service.updateWalletLimits('wallet-1');

        expect(mockPrismaService.wallet.update).toHaveBeenCalledWith({
          where: { id: 'wallet-1' },
          data: {
            dailyWithdrawLimit: testCase.daily,
            singleTransactionLimit: testCase.single,
            requiresPinForAmount: testCase.pin,
          },
        });
      }
    });
  });

  describe('getWalletDashboard', () => {
    it('should return complete wallet dashboard', async () => {
      const mockWallet = {
        id: 'wallet-1',
        balance: 5000,
        escrowBalance: 1000,
        creditScore: 650,
        creditTier: 'GOLD',
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

      const result = await service.getWalletDashboard('wallet-1');

      expect(result.wallet.id).toBe('wallet-1');
      expect(result.wallet.balance).toBe(5000);
      expect(result.wallet.creditTierAr).toBe('ذهبي');
      expect(result.summary.availableCredit).toBe(17750);
    });

    it('should throw error for non-existent wallet', async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);

      await expect(service.getWalletDashboard('wallet-999')).rejects.toThrow(NotFoundException);
    });
  });
});
