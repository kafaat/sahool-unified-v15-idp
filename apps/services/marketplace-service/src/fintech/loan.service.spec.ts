/**
 * SAHOOL Loan Service Tests
 * اختبارات خدمة القروض
 */

import { Test, TestingModule } from '@nestjs/testing';
import { LoanService } from './loan.service';
import { PrismaService } from '../prisma/prisma.service';
import { BadRequestException, NotFoundException } from '@nestjs/common';

describe('LoanService', () => {
  let service: LoanService;
  let prismaService: PrismaService;

  const mockPrismaService = {
    wallet: {
      findUnique: jest.fn(),
      update: jest.fn(),
    },
    loan: {
      create: jest.fn(),
      findUnique: jest.fn(),
      findMany: jest.fn(),
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
    scheduledPayment: {
      create: jest.fn(),
      findUnique: jest.fn(),
      findMany: jest.fn(),
      update: jest.fn(),
    },
    $transaction: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        LoanService,
        {
          provide: PrismaService,
          useValue: mockPrismaService,
        },
      ],
    }).compile();

    service = module.get<LoanService>(LoanService);
    prismaService = module.get<PrismaService>(PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('getLoanPurposeAr', () => {
    it('should translate loan purposes to Arabic', () => {
      expect(service.getLoanPurposeAr('SEEDS')).toBe('شراء بذور');
      expect(service.getLoanPurposeAr('FERTILIZER')).toBe('شراء أسمدة');
      expect(service.getLoanPurposeAr('EQUIPMENT')).toBe('شراء معدات');
      expect(service.getLoanPurposeAr('IRRIGATION')).toBe('نظام ري');
      expect(service.getLoanPurposeAr('EXPANSION')).toBe('توسيع المزرعة');
      expect(service.getLoanPurposeAr('EMERGENCY')).toBe('طوارئ');
      expect(service.getLoanPurposeAr('OTHER')).toBe('أخرى');
      expect(service.getLoanPurposeAr('CUSTOM')).toBe('CUSTOM');
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
        totalDue: 10200,
        status: 'PENDING',
        purpose: 'SEEDS',
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
      expect(result.nextSteps).toHaveLength(3);
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

    it('should throw error for non-existent wallet', async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);

      await expect(
        service.requestLoan({
          walletId: 'wallet-999',
          amount: 5000,
          termMonths: 12,
          purpose: 'SEEDS',
        }),
      ).rejects.toThrow(NotFoundException);
    });

    it('should calculate 2% admin fee correctly', async () => {
      const mockWallet = {
        id: 'wallet-1',
        loanLimit: 50000,
        currentLoan: 0,
      };

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);

      let capturedLoanData: any;
      mockPrismaService.loan.create.mockImplementation((args) => {
        capturedLoanData = args.data;
        return Promise.resolve({
          id: 'loan-1',
          ...args.data,
        });
      });

      await service.requestLoan({
        walletId: 'wallet-1',
        amount: 10000,
        termMonths: 12,
        purpose: 'SEEDS',
      });

      expect(capturedLoanData.totalDue).toBe(10200); // 10000 + 2% fee
      expect(capturedLoanData.interestRate).toBe(0); // Islamic finance
    });
  });

  describe('approveLoan', () => {
    it('should approve pending loan and credit wallet', async () => {
      const mockLoan = {
        id: 'loan-1',
        walletId: 'wallet-1',
        amount: 10000,
        totalDue: 10200,
        status: 'PENDING',
        purpose: 'SEEDS',
        wallet: { balance: 5000 },
      };

      mockPrismaService.loan.findUnique.mockResolvedValue(mockLoan);
      mockPrismaService.$transaction.mockResolvedValue([
        { ...mockLoan, status: 'ACTIVE' },
        { balance: 15000, currentLoan: 10200 },
        { id: 'tx-1', type: 'LOAN', amount: 10000 },
      ]);

      const result = await service.approveLoan('loan-1');

      expect(result.loan.status).toBe('ACTIVE');
      expect(result.wallet.balance).toBe(15000);
    });

    it('should reject non-pending loans', async () => {
      const mockLoan = {
        id: 'loan-1',
        status: 'ACTIVE',
      };

      mockPrismaService.loan.findUnique.mockResolvedValue(mockLoan);

      await expect(service.approveLoan('loan-1')).rejects.toThrow(BadRequestException);
    });

    it('should throw error for non-existent loan', async () => {
      mockPrismaService.loan.findUnique.mockResolvedValue(null);

      await expect(service.approveLoan('loan-999')).rejects.toThrow(NotFoundException);
    });
  });

  describe('repayLoan', () => {
    it('should throw error for zero or negative amount', async () => {
      await expect(service.repayLoan('loan-1', 0)).rejects.toThrow(BadRequestException);
      await expect(service.repayLoan('loan-1', -100)).rejects.toThrow(BadRequestException);
    });

    it('should return existing transaction for duplicate idempotency key', async () => {
      const existingTx = { id: 'tx-1', type: 'REPAYMENT', amount: -5000 };
      const mockLoan = {
        id: 'loan-1',
        wallet: { id: 'wallet-1', balance: 10000 },
      };

      mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
      mockPrismaService.loan.findUnique.mockResolvedValue(mockLoan);

      const result = await service.repayLoan('loan-1', 5000, 'idemp-key-1');

      expect(result.duplicate).toBe(true);
    });
  });

  describe('getUserLoans', () => {
    it('should return all loans for wallet', async () => {
      const mockLoans = [
        { id: 'loan-1', status: 'ACTIVE', amount: 10000 },
        { id: 'loan-2', status: 'PAID', amount: 5000 },
      ];

      mockPrismaService.loan.findMany.mockResolvedValue(mockLoans);

      const result = await service.getUserLoans('wallet-1');

      expect(mockPrismaService.loan.findMany).toHaveBeenCalledWith({
        where: { walletId: 'wallet-1' },
        orderBy: { createdAt: 'desc' },
      });
      expect(result).toEqual(mockLoans);
    });
  });

  describe('createScheduledPayment', () => {
    it('should create scheduled payment', async () => {
      const mockWallet = { id: 'wallet-1' };
      const nextPaymentDate = new Date('2024-02-01');

      mockPrismaService.wallet.findUnique.mockResolvedValue(mockWallet);
      mockPrismaService.scheduledPayment.create.mockResolvedValue({
        id: 'sp-1',
        walletId: 'wallet-1',
        amount: 1000,
        frequency: 'MONTHLY',
        nextPaymentDate,
        isActive: true,
      });

      const result = await service.createScheduledPayment(
        'wallet-1',
        1000,
        'MONTHLY',
        nextPaymentDate,
        'loan-1',
        'Monthly payment',
        'دفعة شهرية',
      );

      expect(result.scheduledPayment.amount).toBe(1000);
      expect(result.message).toContain('تم إنشاء الدفعة المجدولة بنجاح');
    });

    it('should throw error for non-existent wallet', async () => {
      mockPrismaService.wallet.findUnique.mockResolvedValue(null);

      await expect(
        service.createScheduledPayment('wallet-999', 1000, 'MONTHLY', new Date()),
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe('getScheduledPayments', () => {
    it('should return active scheduled payments', async () => {
      const mockPayments = [
        { id: 'sp-1', isActive: true, amount: 1000 },
        { id: 'sp-2', isActive: true, amount: 2000 },
      ];

      mockPrismaService.scheduledPayment.findMany.mockResolvedValue(mockPayments);

      const result = await service.getScheduledPayments('wallet-1', true);

      expect(mockPrismaService.scheduledPayment.findMany).toHaveBeenCalledWith({
        where: { walletId: 'wallet-1', isActive: true },
        orderBy: { nextPaymentDate: 'asc' },
      });
      expect(result).toEqual(mockPayments);
    });

    it('should return all scheduled payments when activeOnly is false', async () => {
      await service.getScheduledPayments('wallet-1', false);

      expect(mockPrismaService.scheduledPayment.findMany).toHaveBeenCalledWith({
        where: { walletId: 'wallet-1' },
        orderBy: { nextPaymentDate: 'asc' },
      });
    });
  });

  describe('cancelScheduledPayment', () => {
    it('should cancel scheduled payment', async () => {
      const mockPayment = { id: 'sp-1', isActive: true };

      mockPrismaService.scheduledPayment.findUnique.mockResolvedValue(mockPayment);
      mockPrismaService.scheduledPayment.update.mockResolvedValue({
        ...mockPayment,
        isActive: false,
      });

      const result = await service.cancelScheduledPayment('sp-1');

      expect(result.isActive).toBe(false);
    });

    it('should throw error for non-existent payment', async () => {
      mockPrismaService.scheduledPayment.findUnique.mockResolvedValue(null);

      await expect(service.cancelScheduledPayment('sp-999')).rejects.toThrow(NotFoundException);
    });
  });

  describe('executeScheduledPayment', () => {
    it('should execute scheduled payment successfully', async () => {
      const mockPayment = {
        id: 'sp-1',
        walletId: 'wallet-1',
        amount: 1000,
        frequency: 'MONTHLY',
        nextPaymentDate: new Date('2024-01-15'),
        isActive: true,
        wallet: { balance: 5000 },
      };

      mockPrismaService.scheduledPayment.findUnique.mockResolvedValue(mockPayment);
      mockPrismaService.$transaction.mockResolvedValue([
        { ...mockPayment, lastPaymentDate: new Date() },
        { balance: 4000 },
        { id: 'tx-1', type: 'SCHEDULED_PAYMENT' },
      ]);

      const result = await service.executeScheduledPayment('sp-1');

      expect(result.wallet.balance).toBe(4000);
    });

    it('should throw error for insufficient balance', async () => {
      const mockPayment = {
        id: 'sp-1',
        amount: 5000,
        isActive: true,
        wallet: { balance: 1000 },
      };

      mockPrismaService.scheduledPayment.findUnique.mockResolvedValue(mockPayment);
      mockPrismaService.scheduledPayment.update.mockResolvedValue({});

      await expect(service.executeScheduledPayment('sp-1')).rejects.toThrow(BadRequestException);
    });

    it('should throw error for inactive payment', async () => {
      const mockPayment = {
        id: 'sp-1',
        isActive: false,
        wallet: { balance: 5000 },
      };

      mockPrismaService.scheduledPayment.findUnique.mockResolvedValue(mockPayment);

      await expect(service.executeScheduledPayment('sp-1')).rejects.toThrow(BadRequestException);
    });

    it('should throw error for non-existent payment', async () => {
      mockPrismaService.scheduledPayment.findUnique.mockResolvedValue(null);

      await expect(service.executeScheduledPayment('sp-999')).rejects.toThrow(NotFoundException);
    });
  });
});
