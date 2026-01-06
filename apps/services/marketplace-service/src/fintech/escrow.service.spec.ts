/**
 * SAHOOL Escrow Service Tests
 * اختبارات خدمة الإسكرو (الضمان)
 */

import { Test, TestingModule } from '@nestjs/testing';
import { EscrowService } from './escrow.service';
import { PrismaService } from '../prisma/prisma.service';
import { BadRequestException, NotFoundException } from '@nestjs/common';

describe('EscrowService', () => {
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

  describe('createEscrow', () => {
    it('should throw error for zero or negative amount', async () => {
      await expect(
        service.createEscrow('order-1', 'buyer-wallet', 'seller-wallet', 0),
      ).rejects.toThrow(BadRequestException);

      await expect(
        service.createEscrow('order-1', 'buyer-wallet', 'seller-wallet', -100),
      ).rejects.toThrow(BadRequestException);
    });

    it('should return existing escrow for duplicate idempotency key', async () => {
      const existingTx = { id: 'tx-1', type: 'ESCROW_HOLD' };
      const existingEscrow = { id: 'escrow-1', orderId: 'order-1' };

      mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
      mockPrismaService.escrow.findUnique.mockResolvedValue(existingEscrow);

      const result = await service.createEscrow(
        'order-1',
        'buyer-wallet',
        'seller-wallet',
        1000,
        'Notes',
        'idemp-key-1',
      );

      expect(result.duplicate).toBe(true);
      expect(result.escrow).toEqual(existingEscrow);
    });

    it('should create escrow with locked buyer balance', async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue(null),
          create: jest.fn().mockResolvedValue({
            id: 'escrow-1',
            orderId: 'order-1',
            amount: 1000,
            status: 'HELD',
          }),
        },
        wallet: {
          findUnique: jest.fn().mockResolvedValue({ id: 'seller-wallet' }),
          update: jest.fn().mockResolvedValue({
            id: 'buyer-wallet',
            balance: 4000,
            escrowBalance: 1000,
          }),
        },
        transaction: {
          create: jest.fn().mockResolvedValue({
            id: 'tx-1',
            type: 'ESCROW_HOLD',
            amount: -1000,
          }),
        },
        walletAuditLog: {
          create: jest.fn().mockResolvedValue({}),
        },
        $queryRaw: jest.fn().mockResolvedValue([{
          id: 'buyer-wallet',
          balance: 5000,
          escrowBalance: 0,
          version: 1,
        }]),
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      const result = await service.createEscrow(
        'order-1',
        'buyer-wallet',
        'seller-wallet',
        1000,
        'Order payment',
      );

      expect(result.duplicate).toBe(false);
      expect(result.escrow.status).toBe('HELD');
      expect(result.wallet.balance).toBe(4000);
    });

    it('should throw error if escrow already exists for order', async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue({ id: 'existing-escrow' }),
        },
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      await expect(
        service.createEscrow('order-1', 'buyer-wallet', 'seller-wallet', 1000),
      ).rejects.toThrow(BadRequestException);
    });
  });

  describe('releaseEscrow', () => {
    it('should return existing transaction for duplicate idempotency key', async () => {
      const existingTx = { id: 'tx-1', type: 'ESCROW_RELEASE' };
      const existingEscrow = {
        id: 'escrow-1',
        status: 'RELEASED',
        buyerWallet: {},
        sellerWallet: {},
      };

      mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
      mockPrismaService.escrow.findUnique.mockResolvedValue(existingEscrow);

      const result = await service.releaseEscrow('escrow-1', 'Notes', 'idemp-key-1');

      expect(result.duplicate).toBe(true);
    });

    it('should throw error for non-held escrow', async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue({
            id: 'escrow-1',
            status: 'RELEASED',
          }),
        },
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      await expect(service.releaseEscrow('escrow-1')).rejects.toThrow(BadRequestException);
    });

    it('should throw error for non-existent escrow', async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue(null),
        },
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      await expect(service.releaseEscrow('escrow-999')).rejects.toThrow(NotFoundException);
    });
  });

  describe('refundEscrow', () => {
    it('should return existing transaction for duplicate idempotency key', async () => {
      const existingTx = { id: 'tx-1', type: 'ESCROW_REFUND' };
      const existingEscrow = {
        id: 'escrow-1',
        status: 'REFUNDED',
        buyerWallet: {},
      };

      mockPrismaService.transaction.findUnique.mockResolvedValue(existingTx);
      mockPrismaService.escrow.findUnique.mockResolvedValue(existingEscrow);

      const result = await service.refundEscrow('escrow-1', 'Cancelled', 'idemp-key-1');

      expect(result.duplicate).toBe(true);
    });

    it('should throw error for already released escrow', async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue({
            id: 'escrow-1',
            status: 'RELEASED',
          }),
        },
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      await expect(service.refundEscrow('escrow-1', 'Cancelled')).rejects.toThrow(
        BadRequestException,
      );
    });

    it('should refund held escrow to buyer', async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue({
            id: 'escrow-1',
            orderId: 'order-1',
            buyerWalletId: 'buyer-wallet',
            sellerWalletId: 'seller-wallet',
            amount: 1000,
            status: 'HELD',
          }),
          update: jest.fn().mockResolvedValue({
            id: 'escrow-1',
            status: 'REFUNDED',
          }),
        },
        wallet: {
          update: jest.fn().mockResolvedValue({
            id: 'buyer-wallet',
            balance: 6000,
            escrowBalance: 0,
          }),
        },
        transaction: {
          create: jest.fn().mockResolvedValue({
            id: 'tx-1',
            type: 'ESCROW_REFUND',
            amount: 1000,
          }),
        },
        walletAuditLog: {
          create: jest.fn().mockResolvedValue({}),
        },
        creditEvent: {
          create: jest.fn().mockResolvedValue({}),
        },
        $queryRaw: jest.fn().mockResolvedValue([{
          id: 'buyer-wallet',
          balance: 5000,
          escrowBalance: 1000,
          version: 1,
        }]),
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      const result = await service.refundEscrow('escrow-1', 'Order cancelled');

      expect(result.duplicate).toBe(false);
      expect(result.escrow.status).toBe('REFUNDED');
      expect(result.wallet.balance).toBe(6000);
    });

    it('should allow refund of disputed escrow', async () => {
      mockPrismaService.transaction.findUnique.mockResolvedValue(null);

      const mockTxContext = {
        escrow: {
          findUnique: jest.fn().mockResolvedValue({
            id: 'escrow-1',
            orderId: 'order-1',
            buyerWalletId: 'buyer-wallet',
            sellerWalletId: 'seller-wallet',
            amount: 1000,
            status: 'DISPUTED',
          }),
          update: jest.fn().mockResolvedValue({ status: 'REFUNDED' }),
        },
        wallet: {
          update: jest.fn().mockResolvedValue({ balance: 6000, escrowBalance: 0 }),
        },
        transaction: {
          create: jest.fn().mockResolvedValue({ id: 'tx-1' }),
        },
        walletAuditLog: {
          create: jest.fn().mockResolvedValue({}),
        },
        creditEvent: {
          create: jest.fn().mockResolvedValue({}),
        },
        $queryRaw: jest.fn().mockResolvedValue([{
          id: 'buyer-wallet',
          balance: 5000,
          escrowBalance: 1000,
          version: 1,
        }]),
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback(mockTxContext);
      });

      const result = await service.refundEscrow('escrow-1', 'Dispute resolved');

      expect(result.escrow.status).toBe('REFUNDED');
    });
  });

  describe('getEscrowByOrder', () => {
    it('should return escrow with wallets for order', async () => {
      const mockEscrow = {
        id: 'escrow-1',
        orderId: 'order-1',
        amount: 1000,
        buyerWallet: { id: 'buyer-wallet' },
        sellerWallet: { id: 'seller-wallet' },
      };

      mockPrismaService.escrow.findUnique.mockResolvedValue(mockEscrow);

      const result = await service.getEscrowByOrder('order-1');

      expect(mockPrismaService.escrow.findUnique).toHaveBeenCalledWith({
        where: { orderId: 'order-1' },
        include: {
          buyerWallet: true,
          sellerWallet: true,
        },
      });
      expect(result).toEqual(mockEscrow);
    });

    it('should return null for non-existent order', async () => {
      mockPrismaService.escrow.findUnique.mockResolvedValue(null);

      const result = await service.getEscrowByOrder('order-999');

      expect(result).toBeNull();
    });
  });

  describe('getWalletEscrows', () => {
    it('should return escrows as buyer and seller', async () => {
      const buyerEscrows = [
        { id: 'escrow-1', amount: 1000 },
        { id: 'escrow-2', amount: 2000 },
      ];

      const sellerEscrows = [
        { id: 'escrow-3', amount: 500 },
      ];

      mockPrismaService.escrow.findMany
        .mockResolvedValueOnce(buyerEscrows)
        .mockResolvedValueOnce(sellerEscrows);

      const result = await service.getWalletEscrows('wallet-1');

      expect(result.asBuyer).toEqual(buyerEscrows);
      expect(result.asSeller).toEqual(sellerEscrows);
      expect(mockPrismaService.escrow.findMany).toHaveBeenCalledTimes(2);
    });
  });
});
