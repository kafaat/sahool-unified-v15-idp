/**
 * SAHOOL Product Service Tests
 * اختبارات خدمة المنتجات
 *
 * Tests for:
 * - Product CRUD operations
 * - Product filtering and search
 * - Harvest to product conversion
 * - Stock management
 * - Pagination
 */

import { Test, TestingModule } from '@nestjs/testing';
import { MarketService } from '../market/market.service';
import { PrismaService } from '../prisma/prisma.service';
import { EventsService } from '../events/events.service';
import { NotFoundException } from '@nestjs/common';

describe('MarketService - Product Operations', () => {
  let service: MarketService;
  let prismaService: PrismaService;
  let eventsService: EventsService;

  const mockPrismaService = {
    product: {
      findMany: jest.fn(),
      findUnique: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
      count: jest.fn(),
    },
    order: {
      create: jest.fn(),
      findMany: jest.fn(),
      count: jest.fn(),
    },
    $transaction: jest.fn(),
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
    eventsService = module.get<EventsService>(EventsService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Product Retrieval Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('findAllProducts', () => {
    it('should return paginated list of available products', async () => {
      const mockProducts = [
        {
          id: '1',
          name: 'Premium Wheat',
          nameAr: 'قمح ممتاز',
          category: 'HARVEST',
          price: 1500,
          stock: 100,
          unit: 'ton',
          status: 'AVAILABLE',
          sellerId: 'farmer-1',
          sellerType: 'FARMER',
          featured: true,
          createdAt: new Date(),
        },
        {
          id: '2',
          name: 'Organic Corn',
          nameAr: 'ذرة عضوية',
          category: 'HARVEST',
          price: 1200,
          stock: 80,
          unit: 'ton',
          status: 'AVAILABLE',
          sellerId: 'farmer-2',
          sellerType: 'FARMER',
          featured: false,
          createdAt: new Date(),
        },
      ];

      mockPrismaService.product.findMany.mockResolvedValue(mockProducts);
      mockPrismaService.product.count.mockResolvedValue(2);

      const result = await service.findAllProducts({});

      expect(result.data).toEqual(mockProducts);
      expect(result.total).toBe(2);
      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { status: 'AVAILABLE' },
          orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
        })
      );
    });

    it('should filter products by category', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([]);
      mockPrismaService.product.count.mockResolvedValue(0);

      await service.findAllProducts({ category: 'HARVEST' });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { status: 'AVAILABLE', category: 'HARVEST' },
        })
      );
    });

    it('should filter products by governorate', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([]);
      mockPrismaService.product.count.mockResolvedValue(0);

      await service.findAllProducts({ governorate: 'Sana\'a' });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { status: 'AVAILABLE', governorate: 'Sana\'a' },
        })
      );
    });

    it('should filter products by seller ID', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([]);
      mockPrismaService.product.count.mockResolvedValue(0);

      await service.findAllProducts({ sellerId: 'farmer-123' });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { status: 'AVAILABLE', sellerId: 'farmer-123' },
        })
      );
    });

    it('should filter products by price range', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([]);
      mockPrismaService.product.count.mockResolvedValue(0);

      await service.findAllProducts({ minPrice: 500, maxPrice: 2000 });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: {
            status: 'AVAILABLE',
            price: { gte: 500, lte: 2000 },
          },
        })
      );
    });

    it('should apply multiple filters simultaneously', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([]);
      mockPrismaService.product.count.mockResolvedValue(0);

      await service.findAllProducts({
        category: 'HARVEST',
        governorate: 'Sana\'a',
        minPrice: 1000,
        maxPrice: 2000,
      });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: {
            status: 'AVAILABLE',
            category: 'HARVEST',
            governorate: 'Sana\'a',
            price: { gte: 1000, lte: 2000 },
          },
        })
      );
    });

    it('should handle pagination parameters', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([]);
      mockPrismaService.product.count.mockResolvedValue(100);

      await service.findAllProducts({ page: 2, pageSize: 20 });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          skip: expect.any(Number),
          take: expect.any(Number),
        })
      );
    });

    it('should return featured products first', async () => {
      const mockProducts = [
        {
          id: '1',
          name: 'Featured Wheat',
          featured: true,
          createdAt: new Date('2024-01-01'),
        },
        {
          id: '2',
          name: 'Regular Corn',
          featured: false,
          createdAt: new Date('2024-01-02'),
        },
      ];

      mockPrismaService.product.findMany.mockResolvedValue(mockProducts);
      mockPrismaService.product.count.mockResolvedValue(2);

      const result = await service.findAllProducts({});

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
        })
      );
    });
  });

  describe('findProductById', () => {
    it('should return a product by ID', async () => {
      const mockProduct = {
        id: '1',
        name: 'Premium Wheat',
        nameAr: 'قمح ممتاز',
        category: 'HARVEST',
        price: 1500,
        stock: 100,
        unit: 'ton',
        status: 'AVAILABLE',
      };

      mockPrismaService.product.findUnique.mockResolvedValue(mockProduct);

      const result = await service.findProductById('1');

      expect(result).toEqual(mockProduct);
      expect(mockPrismaService.product.findUnique).toHaveBeenCalledWith({
        where: { id: '1' },
      });
    });

    it('should throw NotFoundException when product does not exist', async () => {
      mockPrismaService.product.findUnique.mockResolvedValue(null);

      await expect(service.findProductById('non-existent')).rejects.toThrow(
        NotFoundException
      );
      await expect(service.findProductById('non-existent')).rejects.toThrow(
        'المنتج غير موجود'
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Product Creation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('createProduct', () => {
    it('should create a new product with all fields', async () => {
      const productData = {
        name: 'Premium Wheat',
        nameAr: 'قمح ممتاز',
        category: 'HARVEST',
        price: 1500,
        stock: 100,
        unit: 'ton',
        description: 'High quality wheat from Yemen',
        descriptionAr: 'قمح عالي الجودة من اليمن',
        imageUrl: 'https://cdn.sahool.io/wheat.jpg',
        sellerId: 'farmer-123',
        sellerType: 'FARMER',
        sellerName: 'Ahmed Ali',
        cropType: 'wheat',
        governorate: 'Sana\'a',
      };

      const mockCreatedProduct = {
        id: '1',
        ...productData,
        status: 'AVAILABLE',
        featured: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      mockPrismaService.product.create.mockResolvedValue(mockCreatedProduct);

      const result = await service.createProduct(productData);

      expect(result).toEqual(mockCreatedProduct);
      expect(mockPrismaService.product.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          name: productData.name,
          nameAr: productData.nameAr,
          category: productData.category,
          price: productData.price,
          stock: productData.stock,
          unit: productData.unit,
        }),
      });
    });

    it('should create a product with minimal required fields', async () => {
      const minimalProductData = {
        name: 'Basic Product',
        nameAr: 'منتج أساسي',
        category: 'HARVEST',
        price: 1000,
        stock: 50,
        unit: 'kg',
        sellerId: 'seller-123',
        sellerType: 'FARMER',
      };

      const mockCreatedProduct = {
        id: '2',
        ...minimalProductData,
        description: null,
        descriptionAr: null,
        imageUrl: null,
        status: 'AVAILABLE',
        featured: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      mockPrismaService.product.create.mockResolvedValue(mockCreatedProduct);

      const result = await service.createProduct(minimalProductData);

      expect(result.id).toBe('2');
      expect(result.name).toBe('Basic Product');
    });

    it('should handle different seller types', async () => {
      const companyProduct = {
        name: 'Company Seeds',
        nameAr: 'بذور الشركة',
        category: 'SEEDS',
        price: 500,
        stock: 1000,
        unit: 'kg',
        sellerId: 'company-123',
        sellerType: 'COMPANY',
        sellerName: 'Agricultural Company Ltd',
      };

      mockPrismaService.product.create.mockResolvedValue({
        id: '3',
        ...companyProduct,
      });

      const result = await service.createProduct(companyProduct);

      expect(result.sellerType).toBe('COMPANY');
      expect(result.sellerName).toBe('Agricultural Company Ltd');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Harvest to Product Conversion Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('convertYieldToProduct', () => {
    it('should convert yield data to a product listing', async () => {
      const yieldData = {
        crop: 'wheat',
        cropAr: 'قمح',
        predictedYieldTons: 50,
        pricePerTon: 2000,
        harvestDate: '2024-06-15',
        qualityGrade: 'A',
        governorate: 'Sana\'a',
        district: 'Bani Harith',
      };

      const mockProduct = {
        id: '1',
        name: expect.stringContaining('Premium wheat Harvest'),
        nameAr: expect.stringContaining('حصاد قمح عالي الجودة'),
        category: 'HARVEST',
        price: 2000,
        stock: 50,
        unit: 'ton',
        sellerId: 'farmer-123',
        sellerType: 'FARMER',
        cropType: 'wheat',
        harvestDate: new Date('2024-06-15'),
        qualityGrade: 'A',
        governorate: 'Sana\'a',
        district: 'Bani Harith',
      };

      mockPrismaService.product.create.mockResolvedValue(mockProduct);

      const result = await service.convertYieldToProduct('farmer-123', yieldData);

      expect(result).toMatchObject({
        category: 'HARVEST',
        sellerId: 'farmer-123',
        sellerType: 'FARMER',
        cropType: 'wheat',
        price: 2000,
        stock: 50,
        qualityGrade: 'A',
      });

      expect(mockPrismaService.product.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            category: 'HARVEST',
            price: 2000,
            stock: 50,
            unit: 'ton',
            sellerId: 'farmer-123',
            sellerType: 'FARMER',
            cropType: 'wheat',
            qualityGrade: 'A',
          }),
        })
      );
    });

    it('should use default quality grade if not provided', async () => {
      const yieldData = {
        crop: 'corn',
        cropAr: 'ذرة',
        predictedYieldTons: 30,
        pricePerTon: 1500,
      };

      const mockProduct = {
        id: '2',
        qualityGrade: 'A',
      };

      mockPrismaService.product.create.mockResolvedValue(mockProduct);

      await service.convertYieldToProduct('farmer-456', yieldData);

      expect(mockPrismaService.product.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            qualityGrade: 'A',
          }),
        })
      );
    });

    it('should generate proper crop image URLs', async () => {
      const yieldData = {
        crop: 'coffee',
        cropAr: 'قهوة',
        predictedYieldTons: 20,
        pricePerTon: 5000,
      };

      mockPrismaService.product.create.mockResolvedValue({
        id: '3',
        imageUrl: 'https://cdn.sahool.io/crops/coffee.jpg',
      });

      const result = await service.convertYieldToProduct('farmer-789', yieldData);

      expect(mockPrismaService.product.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            imageUrl: expect.stringContaining('coffee'),
          }),
        })
      );
    });

    it('should use default image for unknown crops', async () => {
      const yieldData = {
        crop: 'unknown-crop',
        cropAr: 'محصول غير معروف',
        predictedYieldTons: 10,
        pricePerTon: 1000,
      };

      mockPrismaService.product.create.mockResolvedValue({
        id: '4',
        imageUrl: 'https://cdn.sahool.io/crops/default.jpg',
      });

      await service.convertYieldToProduct('farmer-999', yieldData);

      expect(mockPrismaService.product.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            imageUrl: expect.stringContaining('default'),
          }),
        })
      );
    });

    it('should include current year in product name', async () => {
      const currentYear = new Date().getFullYear();
      const yieldData = {
        crop: 'wheat',
        cropAr: 'قمح',
        predictedYieldTons: 50,
        pricePerTon: 2000,
      };

      mockPrismaService.product.create.mockResolvedValue({
        id: '5',
        name: `Premium wheat Harvest - ${currentYear} Season`,
      });

      await service.convertYieldToProduct('farmer-123', yieldData);

      expect(mockPrismaService.product.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            name: expect.stringContaining(currentYear.toString()),
            nameAr: expect.stringContaining(currentYear.toString()),
          }),
        })
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Stock Management Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Stock Management', () => {
    it('should track product stock correctly', async () => {
      const product = {
        id: '1',
        name: 'Test Product',
        stock: 100,
      };

      mockPrismaService.product.findUnique.mockResolvedValue(product);

      const result = await service.findProductById('1');

      expect(result.stock).toBe(100);
    });

    it('should handle zero stock products', async () => {
      const product = {
        id: '2',
        name: 'Out of Stock Product',
        stock: 0,
        status: 'SOLD_OUT',
      };

      mockPrismaService.product.findUnique.mockResolvedValue(product);

      const result = await service.findProductById('2');

      expect(result.stock).toBe(0);
      expect(result.status).toBe('SOLD_OUT');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Market Statistics Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('getMarketStats', () => {
    it('should return comprehensive market statistics', async () => {
      mockPrismaService.product.count
        .mockResolvedValueOnce(150) // totalProducts
        .mockResolvedValueOnce(45); // totalHarvests

      mockPrismaService.order.count.mockResolvedValue(320);

      const recentProducts = [
        { id: '1', name: 'Product 1', createdAt: new Date() },
        { id: '2', name: 'Product 2', createdAt: new Date() },
      ];

      mockPrismaService.product.findMany.mockResolvedValue(recentProducts);

      const result = await service.getMarketStats();

      expect(result).toEqual({
        totalProducts: 150,
        totalHarvests: 45,
        totalOrders: 320,
        recentProducts: recentProducts,
      });
    });

    it('should handle empty marketplace', async () => {
      mockPrismaService.product.count
        .mockResolvedValueOnce(0)
        .mockResolvedValueOnce(0);

      mockPrismaService.order.count.mockResolvedValue(0);
      mockPrismaService.product.findMany.mockResolvedValue([]);

      const result = await service.getMarketStats();

      expect(result).toEqual({
        totalProducts: 0,
        totalHarvests: 0,
        totalOrders: 0,
        recentProducts: [],
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Edge Cases and Error Handling
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Edge Cases', () => {
    it('should handle database errors gracefully', async () => {
      mockPrismaService.product.findMany.mockRejectedValue(
        new Error('Database connection failed')
      );

      await expect(service.findAllProducts({})).rejects.toThrow(
        'Database connection failed'
      );
    });

    it('should handle large product catalogs with pagination', async () => {
      const largeProductList = Array.from({ length: 1000 }, (_, i) => ({
        id: `product-${i}`,
        name: `Product ${i}`,
        price: 1000 + i,
      }));

      mockPrismaService.product.findMany.mockResolvedValue(
        largeProductList.slice(0, 20)
      );
      mockPrismaService.product.count.mockResolvedValue(1000);

      const result = await service.findAllProducts({ page: 1, pageSize: 20 });

      expect(result.data).toHaveLength(20);
      expect(result.total).toBe(1000);
    });

    it('should handle products with special characters in names', async () => {
      const productData = {
        name: 'Product with "quotes" & symbols',
        nameAr: 'منتج مع "علامات" & رموز',
        category: 'HARVEST',
        price: 1500,
        stock: 100,
        unit: 'ton',
        sellerId: 'farmer-123',
        sellerType: 'FARMER',
      };

      mockPrismaService.product.create.mockResolvedValue({
        id: '1',
        ...productData,
      });

      const result = await service.createProduct(productData);

      expect(result.name).toBe('Product with "quotes" & symbols');
    });

    it('should handle concurrent read operations', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([]);
      mockPrismaService.product.count.mockResolvedValue(0);

      const promises = Array.from({ length: 10 }, () =>
        service.findAllProducts({})
      );

      const results = await Promise.all(promises);

      expect(results).toHaveLength(10);
      expect(mockPrismaService.product.findMany).toHaveBeenCalledTimes(10);
    });
  });
});
