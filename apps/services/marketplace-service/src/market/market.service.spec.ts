/**
 * SAHOOL Market Service Tests
 * اختبارات خدمة السوق
 */

import { Test, TestingModule } from '@nestjs/testing';
import { MarketService } from './market.service';
import { PrismaService } from '../prisma/prisma.service';
import { EventsService } from '../events/events.service';

describe('MarketService', () => {
  let service: MarketService;
  let prismaService: PrismaService;

  const mockPrismaService = {
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
  };

  const mockEventsService = {
    publishOrderPlaced: jest.fn(),
    publishOrderCompleted: jest.fn(),
    publishOrderCancelled: jest.fn(),
    publishInventoryLowStock: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        MarketService,
        {
          provide: PrismaService,
          useValue: mockPrismaService,
        },
        {
          provide: EventsService,
          useValue: mockEventsService,
        },
      ],
    }).compile();

    service = module.get<MarketService>(MarketService);
    prismaService = module.get<PrismaService>(PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('findAllProducts', () => {
    it('should return all available products', async () => {
      const mockProducts = [
        { id: '1', name: 'Wheat', price: 1000, status: 'AVAILABLE' },
        { id: '2', name: 'Corn', price: 800, status: 'AVAILABLE' },
      ];

      mockPrismaService.product.findMany.mockResolvedValue(mockProducts);

      const result = await service.findAllProducts({});

      expect(result).toEqual(mockProducts);
      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith({
        where: { status: 'AVAILABLE' },
        orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
      });
    });

    it('should filter products by category', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([]);

      await service.findAllProducts({ category: 'HARVEST' });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith({
        where: { status: 'AVAILABLE', category: 'HARVEST' },
        orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
      });
    });

    it('should filter products by price range', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([]);

      await service.findAllProducts({ minPrice: 500, maxPrice: 2000 });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith({
        where: {
          status: 'AVAILABLE',
          price: { gte: 500, lte: 2000 },
        },
        orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
      });
    });
  });

  describe('findProductById', () => {
    it('should return a product by id', async () => {
      const mockProduct = { id: '1', name: 'Wheat', price: 1000 };
      mockPrismaService.product.findUnique.mockResolvedValue(mockProduct);

      const result = await service.findProductById('1');

      expect(result).toEqual(mockProduct);
      expect(mockPrismaService.product.findUnique).toHaveBeenCalledWith({
        where: { id: '1' },
      });
    });

    it('should throw NotFoundException when product not found', async () => {
      mockPrismaService.product.findUnique.mockResolvedValue(null);

      await expect(service.findProductById('999')).rejects.toThrow(
        'المنتج غير موجود',
      );
    });
  });

  describe('createProduct', () => {
    it('should create a new product', async () => {
      const productData = {
        name: 'Premium Wheat',
        nameAr: 'قمح ممتاز',
        category: 'HARVEST',
        price: 1500,
        stock: 100,
        unit: 'ton',
        sellerId: 'user-123',
        sellerType: 'FARMER',
      };

      const mockCreatedProduct = { id: '1', ...productData };
      mockPrismaService.product.create.mockResolvedValue(mockCreatedProduct);

      const result = await service.createProduct(productData);

      expect(result).toEqual(mockCreatedProduct);
      expect(mockPrismaService.product.create).toHaveBeenCalled();
    });
  });

  describe('convertYieldToProduct', () => {
    it('should convert yield data to a product listing', async () => {
      const yieldData = {
        crop: 'wheat',
        cropAr: 'قمح',
        predictedYieldTons: 50,
        pricePerTon: 2000,
        qualityGrade: 'A',
        governorate: 'Sana\'a',
      };

      const mockProduct = {
        id: '1',
        name: expect.stringContaining('Premium wheat Harvest'),
        nameAr: expect.stringContaining('قمح'),
        category: 'HARVEST',
        price: 2000,
        stock: 50,
      };

      mockPrismaService.product.create.mockResolvedValue(mockProduct);

      const result = await service.convertYieldToProduct('user-123', yieldData);

      expect(result).toEqual(mockProduct);
      expect(mockPrismaService.product.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            category: 'HARVEST',
            sellerId: 'user-123',
            sellerType: 'FARMER',
          }),
        }),
      );
    });
  });

  describe('getMarketStats', () => {
    it('should return market statistics', async () => {
      mockPrismaService.product.count.mockResolvedValueOnce(100);
      mockPrismaService.product.count.mockResolvedValueOnce(30);
      mockPrismaService.order.count.mockResolvedValue(50);
      mockPrismaService.product.findMany.mockResolvedValue([]);

      const result = await service.getMarketStats();

      expect(result).toEqual({
        totalProducts: 100,
        totalHarvests: 30,
        totalOrders: 50,
        recentProducts: [],
      });
    });
  });
});
