/**
 * SAHOOL Marketplace Service Tests
 * اختبارات خدمة السوق الزراعي
 */

import { Test, TestingModule } from '@nestjs/testing';
import { NotFoundException } from '@nestjs/common';
import { MarketService } from '../src/market/market.service';
import { PrismaService } from '../src/prisma/prisma.service';

describe('MarketplaceService - خدمة السوق', () => {
  let service: MarketService;
  let prismaService: PrismaService;

  // Mock data
  const mockProduct = {
    id: 'prod-123',
    name: 'Premium Wheat Harvest',
    nameAr: 'حصاد قمح ممتاز',
    description: 'High-quality wheat harvest',
    descriptionAr: 'محصول قمح عالي الجودة',
    category: 'HARVEST',
    price: 1500,
    stock: 100,
    unit: 'ton',
    imageUrl: 'https://cdn.sahool.io/crops/wheat.jpg',
    sellerId: 'user-123',
    sellerType: 'FARMER',
    sellerName: 'Ahmed Al-Yamani',
    cropType: 'wheat',
    governorate: 'Sana\'a',
    district: 'Bani Matar',
    status: 'AVAILABLE',
    featured: false,
    harvestDate: new Date('2024-06-01'),
    qualityGrade: 'A',
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const mockOrder = {
    id: 'order-123',
    orderNumber: 'SAH-ABC123',
    buyerId: 'buyer-456',
    buyerName: 'Mohammed Ali',
    buyerPhone: '+967777123456',
    subtotal: 5000,
    serviceFee: 100,
    deliveryFee: 500,
    totalAmount: 5600,
    status: 'PENDING',
    deliveryAddress: 'Sana\'a, Yemen',
    paymentMethod: 'CASH_ON_DELIVERY',
    createdAt: new Date(),
    updatedAt: new Date(),
    items: [
      {
        id: 'item-1',
        orderId: 'order-123',
        productId: 'prod-123',
        quantity: 5,
        unitPrice: 1000,
        totalPrice: 5000,
        createdAt: new Date(),
      },
    ],
  };

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
    $transaction: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        MarketService,
        {
          provide: PrismaService,
          useValue: mockPrismaService,
        },
      ],
    }).compile();

    service = module.get<MarketService>(MarketService);
    prismaService = module.get<PrismaService>(PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // =========================================================================
  // Create Product Tests - اختبارات إنشاء منتج
  // =========================================================================

  describe('createProduct - إنشاء منتج', () => {
    it('should create a new product successfully', async () => {
      const productData = {
        name: 'Premium Wheat',
        nameAr: 'قمح ممتاز',
        category: 'HARVEST',
        price: 1500,
        stock: 100,
        unit: 'ton',
        description: 'High-quality wheat',
        descriptionAr: 'قمح عالي الجودة',
        imageUrl: 'https://cdn.sahool.io/crops/wheat.jpg',
        sellerId: 'user-123',
        sellerType: 'FARMER',
        sellerName: 'Ahmed Al-Yamani',
        cropType: 'wheat',
        governorate: 'Sana\'a',
      };

      mockPrismaService.product.create.mockResolvedValue({
        id: 'prod-123',
        ...productData,
      });

      const result = await service.createProduct(productData);

      expect(result).toBeDefined();
      expect(result.id).toBe('prod-123');
      expect(result.name).toBe('Premium Wheat');
      expect(mockPrismaService.product.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          name: 'Premium Wheat',
          category: 'HARVEST',
          price: 1500,
          stock: 100,
          sellerId: 'user-123',
        }),
      });
    });

    it('should create product with all required fields', async () => {
      const productData = {
        name: 'Coffee Beans',
        nameAr: 'بن يمني',
        category: 'HARVEST',
        price: 3000,
        stock: 50,
        unit: 'kg',
        sellerId: 'user-456',
        sellerType: 'COOPERATIVE',
      };

      mockPrismaService.product.create.mockResolvedValue({
        id: 'prod-456',
        ...productData,
      });

      const result = await service.createProduct(productData);

      expect(result.category).toBe('HARVEST');
      expect(result.sellerType).toBe('COOPERATIVE');
    });

    it('should create product with optional fields', async () => {
      const productData = {
        name: 'Tomatoes',
        nameAr: 'طماطم',
        category: 'VEGETABLES',
        price: 500,
        stock: 200,
        unit: 'kg',
        sellerId: 'user-789',
        sellerType: 'FARMER',
        description: 'Fresh organic tomatoes',
        descriptionAr: 'طماطم عضوية طازجة',
        imageUrl: 'https://cdn.sahool.io/crops/tomato.jpg',
      };

      mockPrismaService.product.create.mockResolvedValue({
        id: 'prod-789',
        ...productData,
      });

      const result = await service.createProduct(productData);

      expect(result.description).toBe('Fresh organic tomatoes');
      expect(result.imageUrl).toBe('https://cdn.sahool.io/crops/tomato.jpg');
    });
  });

  // =========================================================================
  // Search Products Tests - اختبارات البحث عن منتجات
  // =========================================================================

  describe('findAllProducts - البحث عن منتجات', () => {
    it('should return all available products', async () => {
      const mockProducts = [mockProduct, { ...mockProduct, id: 'prod-456' }];
      mockPrismaService.product.findMany.mockResolvedValue(mockProducts);

      const result = await service.findAllProducts({});

      expect(result).toHaveLength(2);
      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith({
        where: { status: 'AVAILABLE' },
        orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
      });
    });

    it('should filter products by category', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([mockProduct]);

      const result = await service.findAllProducts({ category: 'HARVEST' });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith({
        where: {
          status: 'AVAILABLE',
          category: 'HARVEST',
        },
        orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
      });
    });

    it('should filter products by governorate', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([mockProduct]);

      const result = await service.findAllProducts({ governorate: 'Sana\'a' });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith({
        where: {
          status: 'AVAILABLE',
          governorate: 'Sana\'a',
        },
        orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
      });
    });

    it('should filter products by sellerId', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([mockProduct]);

      const result = await service.findAllProducts({ sellerId: 'user-123' });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith({
        where: {
          status: 'AVAILABLE',
          sellerId: 'user-123',
        },
        orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
      });
    });

    it('should filter products by price range', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([mockProduct]);

      const result = await service.findAllProducts({
        minPrice: 1000,
        maxPrice: 2000,
      });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith({
        where: {
          status: 'AVAILABLE',
          price: { gte: 1000, lte: 2000 },
        },
        orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
      });
    });

    it('should filter products by minimum price only', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([mockProduct]);

      const result = await service.findAllProducts({ minPrice: 1000 });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith({
        where: {
          status: 'AVAILABLE',
          price: { gte: 1000 },
        },
        orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
      });
    });

    it('should filter products by maximum price only', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([mockProduct]);

      const result = await service.findAllProducts({ maxPrice: 2000 });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith({
        where: {
          status: 'AVAILABLE',
          price: { lte: 2000 },
        },
        orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
      });
    });

    it('should combine multiple filters', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([mockProduct]);

      const result = await service.findAllProducts({
        category: 'HARVEST',
        governorate: 'Sana\'a',
        minPrice: 1000,
        maxPrice: 2000,
      });

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith({
        where: {
          status: 'AVAILABLE',
          category: 'HARVEST',
          governorate: 'Sana\'a',
          price: { gte: 1000, lte: 2000 },
        },
        orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
      });
    });

    it('should return empty array when no products match filters', async () => {
      mockPrismaService.product.findMany.mockResolvedValue([]);

      const result = await service.findAllProducts({ category: 'UNKNOWN' });

      expect(result).toEqual([]);
    });
  });

  // =========================================================================
  // Get Product by ID Tests - اختبارات جلب منتج بالمعرف
  // =========================================================================

  describe('findProductById - جلب منتج بالمعرف', () => {
    it('should return product by ID', async () => {
      mockPrismaService.product.findUnique.mockResolvedValue(mockProduct);

      const result = await service.findProductById('prod-123');

      expect(result).toEqual(mockProduct);
      expect(mockPrismaService.product.findUnique).toHaveBeenCalledWith({
        where: { id: 'prod-123' },
      });
    });

    it('should throw NotFoundException when product not found', async () => {
      mockPrismaService.product.findUnique.mockResolvedValue(null);

      await expect(service.findProductById('prod-999')).rejects.toThrow(
        NotFoundException,
      );
      await expect(service.findProductById('prod-999')).rejects.toThrow(
        'المنتج غير موجود',
      );
    });
  });

  // =========================================================================
  // Create Order Tests - اختبارات إنشاء طلب
  // =========================================================================

  describe('createOrder - إنشاء طلب', () => {
    it('should create an order successfully', async () => {
      const orderData = {
        buyerId: 'buyer-456',
        buyerName: 'Mohammed Ali',
        buyerPhone: '+967777123456',
        items: [
          { productId: 'prod-123', quantity: 5 },
        ],
        deliveryAddress: 'Sana\'a, Yemen',
        paymentMethod: 'CASH_ON_DELIVERY',
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          product: {
            findUnique: jest.fn().mockResolvedValue({
              ...mockProduct,
              stock: 100,
            }),
            update: jest.fn().mockResolvedValue(mockProduct),
          },
          order: {
            create: jest.fn().mockResolvedValue(mockOrder),
          },
        });
      });

      const result = await service.createOrder(orderData);

      expect(result).toBeDefined();
      expect(result.orderNumber).toContain('SAH-');
    });

    it('should calculate order totals correctly', async () => {
      const orderData = {
        buyerId: 'buyer-456',
        items: [{ productId: 'prod-123', quantity: 10 }],
      };

      const expectedSubtotal = 1500 * 10; // 15000
      const expectedServiceFee = expectedSubtotal * 0.02; // 300
      const expectedDeliveryFee = 500;
      const expectedTotal = expectedSubtotal + expectedServiceFee + expectedDeliveryFee;

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          product: {
            findUnique: jest.fn().mockResolvedValue({
              ...mockProduct,
              price: 1500,
              stock: 100,
            }),
            update: jest.fn().mockResolvedValue(mockProduct),
          },
          order: {
            create: jest.fn().mockImplementation((args) => {
              expect(args.data.subtotal).toBe(expectedSubtotal);
              expect(args.data.serviceFee).toBe(expectedServiceFee);
              expect(args.data.deliveryFee).toBe(expectedDeliveryFee);
              expect(args.data.totalAmount).toBe(expectedTotal);
              return Promise.resolve({ ...mockOrder, ...args.data });
            }),
          },
        });
      });

      await service.createOrder(orderData);
    });

    it('should throw error when product not found', async () => {
      const orderData = {
        buyerId: 'buyer-456',
        items: [{ productId: 'prod-999', quantity: 5 }],
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          product: {
            findUnique: jest.fn().mockResolvedValue(null),
          },
        });
      });

      await expect(service.createOrder(orderData)).rejects.toThrow();
    });

    it('should throw error when stock is insufficient', async () => {
      const orderData = {
        buyerId: 'buyer-456',
        items: [{ productId: 'prod-123', quantity: 200 }],
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          product: {
            findUnique: jest.fn().mockResolvedValue({
              ...mockProduct,
              stock: 100,
            }),
          },
        });
      });

      await expect(service.createOrder(orderData)).rejects.toThrow(
        'الكمية المطلوبة غير متوفرة',
      );
    });

    it('should decrement product stock after order', async () => {
      const orderData = {
        buyerId: 'buyer-456',
        items: [{ productId: 'prod-123', quantity: 10 }],
      };

      const mockUpdate = jest.fn().mockResolvedValue(mockProduct);

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          product: {
            findUnique: jest.fn().mockResolvedValue({
              ...mockProduct,
              stock: 100,
            }),
            update: mockUpdate,
          },
          order: {
            create: jest.fn().mockResolvedValue(mockOrder),
          },
        });
      });

      await service.createOrder(orderData);

      expect(mockUpdate).toHaveBeenCalledWith({
        where: { id: 'prod-123' },
        data: { stock: { decrement: 10 } },
      });
    });

    it('should create order with multiple items', async () => {
      const orderData = {
        buyerId: 'buyer-456',
        items: [
          { productId: 'prod-123', quantity: 5 },
          { productId: 'prod-456', quantity: 3 },
        ],
      };

      let callCount = 0;
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          product: {
            findUnique: jest.fn().mockImplementation(() => {
              callCount++;
              return Promise.resolve({
                ...mockProduct,
                id: callCount === 1 ? 'prod-123' : 'prod-456',
                price: callCount === 1 ? 1500 : 2000,
                stock: 100,
              });
            }),
            update: jest.fn().mockResolvedValue(mockProduct),
          },
          order: {
            create: jest.fn().mockResolvedValue({
              ...mockOrder,
              items: [
                {
                  productId: 'prod-123',
                  quantity: 5,
                  unitPrice: 1500,
                  totalPrice: 7500,
                },
                {
                  productId: 'prod-456',
                  quantity: 3,
                  unitPrice: 2000,
                  totalPrice: 6000,
                },
              ],
            }),
          },
        });
      });

      const result = await service.createOrder(orderData);

      expect(result.items).toHaveLength(2);
    });

    it('should generate unique order number', async () => {
      const orderData = {
        buyerId: 'buyer-456',
        items: [{ productId: 'prod-123', quantity: 1 }],
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          product: {
            findUnique: jest.fn().mockResolvedValue({
              ...mockProduct,
              stock: 100,
            }),
            update: jest.fn().mockResolvedValue(mockProduct),
          },
          order: {
            create: jest.fn().mockImplementation((args) => {
              expect(args.data.orderNumber).toMatch(/^SAH-[A-Z0-9]+$/);
              return Promise.resolve({ ...mockOrder, ...args.data });
            }),
          },
        });
      });

      await service.createOrder(orderData);
    });
  });

  // =========================================================================
  // Get User Orders Tests - اختبارات جلب طلبات المستخدم
  // =========================================================================

  describe('getUserOrders - جلب طلبات المستخدم', () => {
    it('should return buyer orders', async () => {
      const mockOrders = [mockOrder];
      mockPrismaService.order.findMany.mockResolvedValue(mockOrders);

      const result = await service.getUserOrders('buyer-456', 'buyer');

      expect(result).toEqual(mockOrders);
      expect(mockPrismaService.order.findMany).toHaveBeenCalledWith({
        where: { buyerId: 'buyer-456' },
        include: { items: { include: { product: true } } },
        orderBy: { createdAt: 'desc' },
      });
    });

    it('should return seller orders', async () => {
      const mockOrders = [mockOrder];
      mockPrismaService.order.findMany.mockResolvedValue(mockOrders);

      const result = await service.getUserOrders('user-123', 'seller');

      expect(result).toEqual(mockOrders);
      expect(mockPrismaService.order.findMany).toHaveBeenCalledWith({
        where: {
          items: {
            some: {
              product: { sellerId: 'user-123' },
            },
          },
        },
        include: { items: { include: { product: true } } },
        orderBy: { createdAt: 'desc' },
      });
    });

    it('should return empty array when no orders found', async () => {
      mockPrismaService.order.findMany.mockResolvedValue([]);

      const result = await service.getUserOrders('user-999', 'buyer');

      expect(result).toEqual([]);
    });
  });

  // =========================================================================
  // Convert Yield to Product Tests - اختبارات تحويل التوقع لمنتج
  // =========================================================================

  describe('convertYieldToProduct - تحويل توقع الحصاد لمنتج', () => {
    it('should convert yield data to product listing', async () => {
      const yieldData = {
        crop: 'wheat',
        cropAr: 'قمح',
        predictedYieldTons: 50,
        pricePerTon: 2000,
        qualityGrade: 'A',
        governorate: 'Sana\'a',
        harvestDate: '2024-06-01',
      };

      mockPrismaService.product.create.mockResolvedValue({
        ...mockProduct,
        category: 'HARVEST',
        stock: 50,
        price: 2000,
      });

      const result = await service.convertYieldToProduct('user-123', yieldData);

      expect(result.category).toBe('HARVEST');
      expect(result.stock).toBe(50);
      expect(result.price).toBe(2000);
      expect(mockPrismaService.product.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            category: 'HARVEST',
            sellerId: 'user-123',
            sellerType: 'FARMER',
            stock: 50,
            price: 2000,
            unit: 'ton',
          }),
        }),
      );
    });

    it('should include harvest date in product', async () => {
      const yieldData = {
        crop: 'coffee',
        cropAr: 'بن',
        predictedYieldTons: 20,
        pricePerTon: 3000,
        harvestDate: '2024-07-15',
      };

      mockPrismaService.product.create.mockResolvedValue({
        ...mockProduct,
        harvestDate: new Date('2024-07-15'),
      });

      const result = await service.convertYieldToProduct('user-123', yieldData);

      expect(result.harvestDate).toBeDefined();
    });

    it('should set crop image URL correctly', async () => {
      const yieldData = {
        crop: 'coffee',
        cropAr: 'بن',
        predictedYieldTons: 20,
        pricePerTon: 3000,
      };

      mockPrismaService.product.create.mockResolvedValue({
        ...mockProduct,
        imageUrl: 'https://cdn.sahool.io/crops/coffee.jpg',
      });

      const result = await service.convertYieldToProduct('user-123', yieldData);

      expect(result.imageUrl).toContain('coffee.jpg');
    });
  });

  // =========================================================================
  // Market Stats Tests - اختبارات إحصائيات السوق
  // =========================================================================

  describe('getMarketStats - إحصائيات السوق', () => {
    it('should return market statistics', async () => {
      mockPrismaService.product.count.mockResolvedValueOnce(100);
      mockPrismaService.product.count.mockResolvedValueOnce(30);
      mockPrismaService.order.count.mockResolvedValue(50);
      mockPrismaService.product.findMany.mockResolvedValue([mockProduct]);

      const result = await service.getMarketStats();

      expect(result).toEqual({
        totalProducts: 100,
        totalHarvests: 30,
        totalOrders: 50,
        recentProducts: [mockProduct],
      });
    });

    it('should count only available products', async () => {
      mockPrismaService.product.count.mockResolvedValueOnce(100);
      mockPrismaService.product.count.mockResolvedValueOnce(30);
      mockPrismaService.order.count.mockResolvedValue(50);
      mockPrismaService.product.findMany.mockResolvedValue([]);

      await service.getMarketStats();

      expect(mockPrismaService.product.count).toHaveBeenNthCalledWith(1, {
        where: { status: 'AVAILABLE' },
      });
    });

    it('should count only harvest category for totalHarvests', async () => {
      mockPrismaService.product.count.mockResolvedValueOnce(100);
      mockPrismaService.product.count.mockResolvedValueOnce(30);
      mockPrismaService.order.count.mockResolvedValue(50);
      mockPrismaService.product.findMany.mockResolvedValue([]);

      await service.getMarketStats();

      expect(mockPrismaService.product.count).toHaveBeenNthCalledWith(2, {
        where: { category: 'HARVEST', status: 'AVAILABLE' },
      });
    });

    it('should return recent products limited to 5', async () => {
      const mockProducts = Array(10).fill(mockProduct).map((p, i) => ({
        ...p,
        id: `prod-${i}`,
      }));

      mockPrismaService.product.count.mockResolvedValue(100);
      mockPrismaService.order.count.mockResolvedValue(50);
      mockPrismaService.product.findMany.mockResolvedValue(mockProducts);

      await service.getMarketStats();

      expect(mockPrismaService.product.findMany).toHaveBeenCalledWith({
        where: { status: 'AVAILABLE' },
        orderBy: { createdAt: 'desc' },
        take: 5,
      });
    });
  });
});
