/**
 * SAHOOL FinTech Service Tests
 * اختبارات خدمة التمويل
 */

import { Test, TestingModule } from '@nestjs/testing';
import { FintechService } from './fintech.service';
import { PrismaService } from '../prisma/prisma.service';
import { BadRequestException, NotFoundException } from '@nestjs/common';

describe('FintechService', () => {
  let service: FintechService;
  let prismaService: PrismaService;

  const mockPrismaService = {
    wallet: {
      findUnique: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      upsert: jest.fn(),
      count: jest.fn(),
      aggregate: jest.fn(),
    },
    transaction: {
      create: jest.fn(),
      findMany: jest.fn(),
    },
    loan: {
      create: jest.fn(),
      findUnique: jest.fn(),
      update: jest.fn(),
      findMany: jest.fn(),
      count: jest.fn(),
    },
    $transaction: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        FintechService,
        {
          provide: PrismaService,
          useValue: mockPrismaService,
        },
      ],
    }).compile();

    service = module.get<FintechService>(FintechService);
    prismaService = module.get<PrismaService>(PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('getWallet', () => {
    it('should return existing wallet', async () => {
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

      expect(result).toEqual(expect.objectContaining({
        id: 'wallet-new',
        balance: 0,
        creditTierAr: 'برونزي',
      }));
    });
  });

  describe('deposit', () => {
    it('should deposit amount to wallet', async () => {
      const mockWallet = {
        id: 'wallet-1',
        balance: 1000,
      };

      const updatedWallet = { ...mockWallet, balance: 1500 };
      const mockTransaction = { id: 'tx-1', type: 'DEPOSIT', amount: 500 };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);
      mockPrismaService.$transaction.mockResolvedValue([updatedWallet, mockTransaction]);

      const result = await service.deposit('wallet-1', 500, 'Test deposit');

      expect(result.wallet.balance).toBe(1500);
      expect(result.transaction.amount).toBe(500);
    });

    it('should throw error for negative amount', async () => {
      await expect(service.deposit('wallet-1', -100)).rejects.toThrow(
        BadRequestException,
      );
    });

    it('should throw error for non-existent wallet', async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);

      await expect(service.deposit('wallet-999', 100)).rejects.toThrow(
        NotFoundException,
      );
    });
  });

  describe('withdraw', () => {
    it('should withdraw amount from wallet', async () => {
      const mockWallet = {
        id: 'wallet-1',
        balance: 1000,
      };

      const updatedWallet = { ...mockWallet, balance: 500 };
      const mockTransaction = { id: 'tx-1', type: 'WITHDRAWAL', amount: -500 };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);
      mockPrismaService.$transaction.mockResolvedValue([updatedWallet, mockTransaction]);

      const result = await service.withdraw('wallet-1', 500, 'Test withdrawal');

      expect(result.wallet.balance).toBe(500);
    });

    it('should throw error for insufficient balance', async () => {
      const mockWallet = {
        id: 'wallet-1',
        balance: 100,
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      await expect(service.withdraw('wallet-1', 500)).rejects.toThrow(
        BadRequestException,
      );
    });
  });

  describe('calculateCreditScore', () => {
    it('should calculate credit score for farmer with good data', async () => {
      const farmData = {
        totalArea: 10,
        activeSeasons: 5,
        fieldCount: 5,
        diseaseRisk: 'Low' as const,
        irrigationType: 'drip',
        avgYieldScore: 85,
        onTimePayments: 10,
        latePayments: 0,
      };

      const mockWallet = {
        id: 'wallet-1',
        userId: 'user-123',
        creditScore: 750,
        creditTier: 'PLATINUM',
        loanLimit: 37500,
        currentLoan: 0,
      };

      mockPrismaService.wallet.upsert.mockResolvedValue(mockWallet);

      const result = await service.calculateCreditScore('user-123', farmData);

      expect(result.wallet.creditTier).toBe('PLATINUM');
      expect(result.creditTierAr).toBe('بلاتيني');
      expect(result.message).toContain('تهانينا');
    });

    it('should calculate lower score for farmer with poor data', async () => {
      const farmData = {
        totalArea: 1,
        activeSeasons: 1,
        fieldCount: 1,
        diseaseRisk: 'High' as const,
        irrigationType: 'flood',
        avgYieldScore: 30,
        onTimePayments: 2,
        latePayments: 8,
      };

      const mockWallet = {
        id: 'wallet-1',
        userId: 'user-123',
        creditScore: 350,
        creditTier: 'BRONZE',
        loanLimit: 3500,
        currentLoan: 0,
      };

      mockPrismaService.wallet.upsert.mockResolvedValue(mockWallet);

      const result = await service.calculateCreditScore('user-123', farmData);

      expect(result.wallet.creditTier).toBe('BRONZE');
      expect(result.message).toContain('ننصحك');
    });
  });

  describe('requestLoan', () => {
    it('should create loan request within credit limit', async () => {
      const mockWallet = {
        id: 'wallet-1',
        loanLimit: 20000,
        currentLoan: 5000,
      };

      const mockLoan = {
        id: 'loan-1',
        walletId: 'wallet-1',
        amount: 10000,
        status: 'PENDING',
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);
      mockPrismaService.loan.create.mockResolvedValue(mockLoan);

      const result = await service.requestLoan({
        walletId: 'wallet-1',
        amount: 10000,
        termMonths: 12,
        purpose: 'SEEDS',
      });

      expect(result.loan.status).toBe('PENDING');
      expect(result.message).toContain('تم تقديم طلب القرض بنجاح');
    });

    it('should reject loan exceeding credit limit', async () => {
      const mockWallet = {
        id: 'wallet-1',
        loanLimit: 10000,
        currentLoan: 8000,
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      await expect(
        service.requestLoan({
          walletId: 'wallet-1',
          amount: 5000,
          termMonths: 12,
          purpose: 'SEEDS',
        }),
      ).rejects.toThrow(BadRequestException);
    });
  });

  describe('getFinanceStats', () => {
    it('should return finance statistics', async () => {
      mockPrismaService.wallet.count.mockResolvedValue(100);
      mockPrismaService.wallet.aggregate.mockResolvedValueOnce({ _sum: { balance: 500000 } });
      mockPrismaService.loan.count.mockResolvedValueOnce(20);
      mockPrismaService.loan.count.mockResolvedValueOnce(50);
      mockPrismaService.wallet.aggregate.mockResolvedValueOnce({ _avg: { creditScore: 550 } });

      const result = await service.getFinanceStats();

      expect(result).toEqual({
        totalWallets: 100,
        totalBalance: 500000,
        activeLoans: 20,
        paidLoans: 50,
        avgCreditScore: 550,
      });
    });
  });
});
