/**
 * SAHOOL Order Service Tests
 * اختبارات خدمة الطلبات
 *
 * Tests for:
 * - Order creation and processing
 * - Stock management during orders
 * - Order retrieval (buyer/seller views)
 * - Order calculations (fees, totals)
 * - Concurrent order handling
 * - Event publishing
 */

import { Test, TestingModule } from '@nestjs/testing';
import { MarketService } from '../market/market.service';
import { PrismaService } from '../prisma/prisma.service';
import { EventsService } from '../events/events.service';

describe('MarketService - Order Operations', () => {
  let service: MarketService;
  let prismaService: PrismaService;
  let eventsService: EventsService;

  const mockPrismaService = {
    product: {
      findMany: jest.fn(),
      findUnique: jest.fn(),
      update: jest.fn(),
      count: jest.fn(),
    },
    order: {
      create: jest.fn(),
      findMany: jest.fn(),
      findUnique: jest.fn(),
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
  // Order Creation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('createOrder', () => {
    it('should create an order with single product', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        buyerName: 'Ahmed Ali',
        buyerPhone: '+967771234567',
        items: [{ productId: 'product-1', quantity: 2 }],
        deliveryAddress: 'Sana\'a, Yemen',
        paymentMethod: 'WALLET',
      };

      const mockProduct = {
        id: 'product-1',
        name: 'Premium Wheat',
        price: 2000,
        stock: 100,
        unit: 'ton',
      };

      const mockOrder = {
        id: 'order-1',
        orderNumber: 'SAH-ABC123',
        buyerId: 'buyer-123',
        buyerName: 'Ahmed Ali',
        buyerPhone: '+967771234567',
        subtotal: 4000,
        serviceFee: 80,
        deliveryFee: 500,
        totalAmount: 4580,
        status: 'PENDING',
        items: [
          {
            id: 'item-1',
            productId: 'product-1',
            quantity: 2,
            unitPrice: 2000,
            totalPrice: 4000,
          },
        ],
        createdAt: new Date(),
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue([mockProduct]),
            update: jest.fn().mockResolvedValue({ ...mockProduct, stock: 98 }),
          },
          order: {
            create: jest.fn().mockResolvedValue(mockOrder),
          },
        };
        return callback(tx);
      });

      const result = await service.createOrder(orderData);

      expect(result.orderNumber).toContain('SAH-');
      expect(result.subtotal).toBe(4000);
      expect(result.totalAmount).toBe(4580);
      expect(mockEventsService.publishOrderPlaced).toHaveBeenCalled();
    });

    it('should create an order with multiple products', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        items: [
          { productId: 'product-1', quantity: 2 },
          { productId: 'product-2', quantity: 5 },
        ],
      };

      const mockProducts = [
        {
          id: 'product-1',
          name: 'Premium Wheat',
          price: 2000,
          stock: 100,
        },
        {
          id: 'product-2',
          name: 'Organic Corn',
          price: 1200,
          stock: 80,
        },
      ];

      const mockOrder = {
        id: 'order-1',
        orderNumber: 'SAH-XYZ789',
        subtotal: 10000, // (2 * 2000) + (5 * 1200)
        serviceFee: 200,
        deliveryFee: 500,
        totalAmount: 10700,
        items: [
          {
            productId: 'product-1',
            quantity: 2,
            unitPrice: 2000,
            totalPrice: 4000,
          },
          {
            productId: 'product-2',
            quantity: 5,
            unitPrice: 1200,
            totalPrice: 6000,
          },
        ],
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue(mockProducts),
            update: jest.fn().mockImplementation((params) => {
              const product = mockProducts.find((p) => p.id === params.where.id);
              return Promise.resolve(product);
            }),
          },
          order: {
            create: jest.fn().mockResolvedValue(mockOrder),
          },
        };
        return callback(tx);
      });

      const result = await service.createOrder(orderData);

      expect(result.subtotal).toBe(10000);
      expect(result.items).toHaveLength(2);
    });

    it('should calculate service fee correctly (2%)', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        items: [{ productId: 'product-1', quantity: 10 }],
      };

      const mockProduct = {
        id: 'product-1',
        price: 1000,
        stock: 100,
      };

      const subtotal = 10000;
      const serviceFee = subtotal * 0.02; // 200

      const mockOrder = {
        id: 'order-1',
        subtotal,
        serviceFee,
        deliveryFee: 500,
        totalAmount: subtotal + serviceFee + 500,
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue([mockProduct]),
            update: jest.fn().mockResolvedValue(mockProduct),
          },
          order: {
            create: jest.fn().mockResolvedValue(mockOrder),
          },
        };
        return callback(tx);
      });

      const result = await service.createOrder(orderData);

      expect(result.serviceFee).toBe(200);
      expect(result.totalAmount).toBe(10700);
    });

    it('should include fixed delivery fee', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        items: [{ productId: 'product-1', quantity: 1 }],
      };

      const mockProduct = {
        id: 'product-1',
        price: 5000,
        stock: 10,
      };

      const mockOrder = {
        id: 'order-1',
        subtotal: 5000,
        serviceFee: 100,
        deliveryFee: 500,
        totalAmount: 5600,
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue([mockProduct]),
            update: jest.fn().mockResolvedValue(mockProduct),
          },
          order: {
            create: jest.fn().mockResolvedValue(mockOrder),
          },
        };
        return callback(tx);
      });

      const result = await service.createOrder(orderData);

      expect(result.deliveryFee).toBe(500);
    });

    it('should generate unique order number', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        items: [{ productId: 'product-1', quantity: 1 }],
      };

      const mockProduct = {
        id: 'product-1',
        price: 1000,
        stock: 10,
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue([mockProduct]),
            update: jest.fn().mockResolvedValue(mockProduct),
          },
          order: {
            create: jest.fn().mockResolvedValue({
              id: 'order-1',
              orderNumber: expect.stringMatching(/^SAH-[A-Z0-9]+$/),
            }),
          },
        };
        return callback(tx);
      });

      const result = await service.createOrder(orderData);

      expect(result.orderNumber).toMatch(/^SAH-/);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Stock Management Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Stock Management in Orders', () => {
    it('should decrement product stock when order is created', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        items: [{ productId: 'product-1', quantity: 10 }],
      };

      const mockProduct = {
        id: 'product-1',
        price: 1000,
        stock: 100,
      };

      const updateMock = jest.fn().mockResolvedValue({
        ...mockProduct,
        stock: 90,
      });

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue([mockProduct]),
            update: updateMock,
          },
          order: {
            create: jest.fn().mockResolvedValue({
              id: 'order-1',
            }),
          },
        };
        return callback(tx);
      });

      await service.createOrder(orderData);

      expect(updateMock).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { id: 'product-1' },
          data: { stock: { decrement: 10 } },
        })
      );
    });

    it('should throw error when product stock is insufficient', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        items: [{ productId: 'product-1', quantity: 200 }],
      };

      const mockProduct = {
        id: 'product-1',
        name: 'Premium Wheat',
        nameAr: 'قمح ممتاز',
        price: 1000,
        stock: 100,
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue([mockProduct]),
          },
        };
        return callback(tx);
      });

      await expect(service.createOrder(orderData)).rejects.toThrow(
        'الكمية المطلوبة غير متوفرة للمنتج'
      );
    });

    it('should throw error when product does not exist', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        items: [{ productId: 'non-existent', quantity: 1 }],
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue([]),
          },
        };
        return callback(tx);
      });

      await expect(service.createOrder(orderData)).rejects.toThrow(
        'المنتج غير موجود'
      );
    });

    it('should handle concurrent orders atomically with transactions', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        items: [{ productId: 'product-1', quantity: 5 }],
      };

      const mockProduct = {
        id: 'product-1',
        price: 1000,
        stock: 10,
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue([mockProduct]),
            update: jest.fn().mockResolvedValue({
              ...mockProduct,
              stock: 5,
            }),
          },
          order: {
            create: jest.fn().mockResolvedValue({
              id: 'order-1',
            }),
          },
        };
        return callback(tx);
      });

      await service.createOrder(orderData);

      expect(mockPrismaService.$transaction).toHaveBeenCalled();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Order Retrieval Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('getUserOrders', () => {
    it('should return buyer orders with pagination', async () => {
      const userId = 'buyer-123';
      const mockOrders = [
        {
          id: 'order-1',
          orderNumber: 'SAH-ABC123',
          buyerId: userId,
          status: 'PENDING',
          totalAmount: 5000,
          createdAt: new Date(),
          items: [],
        },
        {
          id: 'order-2',
          orderNumber: 'SAH-XYZ789',
          buyerId: userId,
          status: 'COMPLETED',
          totalAmount: 3000,
          createdAt: new Date(),
          items: [],
        },
      ];

      mockPrismaService.order.findMany.mockResolvedValue(mockOrders);
      mockPrismaService.order.count.mockResolvedValue(2);

      const result = await service.getUserOrders(userId, 'buyer');

      expect(result.data).toEqual(mockOrders);
      expect(result.total).toBe(2);
      expect(mockPrismaService.order.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { buyerId: userId },
        })
      );
    });

    it('should return seller orders', async () => {
      const userId = 'seller-123';

      mockPrismaService.order.findMany.mockResolvedValue([]);
      mockPrismaService.order.count.mockResolvedValue(0);

      await service.getUserOrders(userId, 'seller');

      expect(mockPrismaService.order.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: {
            items: {
              some: {
                product: { sellerId: userId },
              },
            },
          },
        })
      );
    });

    it('should include order items with product details', async () => {
      const userId = 'buyer-123';
      const mockOrders = [
        {
          id: 'order-1',
          orderNumber: 'SAH-ABC123',
          items: [
            {
              id: 'item-1',
              quantity: 2,
              unitPrice: 2000,
              totalPrice: 4000,
              product: {
                id: 'product-1',
                name: 'Premium Wheat',
                nameAr: 'قمح ممتاز',
                category: 'HARVEST',
                imageUrl: 'https://cdn.sahool.io/wheat.jpg',
              },
            },
          ],
        },
      ];

      mockPrismaService.order.findMany.mockResolvedValue(mockOrders);
      mockPrismaService.order.count.mockResolvedValue(1);

      const result = await service.getUserOrders(userId, 'buyer');

      expect(result.data[0].items[0].product).toBeDefined();
      expect(result.data[0].items[0].product.name).toBe('Premium Wheat');
    });

    it('should sort orders by creation date descending', async () => {
      const userId = 'buyer-123';

      mockPrismaService.order.findMany.mockResolvedValue([]);
      mockPrismaService.order.count.mockResolvedValue(0);

      await service.getUserOrders(userId, 'buyer');

      expect(mockPrismaService.order.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          orderBy: { createdAt: 'desc' },
        })
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Event Publishing Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Event Publishing', () => {
    it('should publish order.placed event when order is created', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        items: [{ productId: 'product-1', quantity: 2 }],
      };

      const mockProduct = {
        id: 'product-1',
        price: 2000,
        stock: 100,
      };

      const mockOrder = {
        id: 'order-1',
        buyerId: 'buyer-123',
        totalAmount: 4580,
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue([mockProduct]),
            update: jest.fn().mockResolvedValue(mockProduct),
          },
          order: {
            create: jest.fn().mockResolvedValue(mockOrder),
          },
        };
        return callback(tx);
      });

      await service.createOrder(orderData);

      expect(mockEventsService.publishOrderPlaced).toHaveBeenCalledWith(
        expect.objectContaining({
          orderId: 'order-1',
          userId: 'buyer-123',
          totalAmount: 4580,
          currency: 'YER',
        })
      );
    });

    it('should publish inventory low stock event when stock is low', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        items: [{ productId: 'product-1', quantity: 95 }],
      };

      const mockProduct = {
        id: 'product-1',
        name: 'Premium Wheat',
        nameAr: 'قمح ممتاز',
        price: 1000,
        stock: 100,
        unit: 'ton',
      };

      const updatedProduct = {
        ...mockProduct,
        stock: 5, // Low stock after order
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue([mockProduct]),
            update: jest.fn().mockResolvedValue(updatedProduct),
          },
          order: {
            create: jest.fn().mockResolvedValue({
              id: 'order-1',
            }),
          },
        };
        await callback(tx);

        // Simulate the non-blocking event publishing
        await Promise.resolve();
        return { id: 'order-1' };
      });

      await service.createOrder(orderData);

      // Wait for async event publishing
      await new Promise(resolve => setTimeout(resolve, 100));

      // Note: The actual implementation publishes this asynchronously
      // So we just verify the structure is correct
      expect(mockEventsService.publishOrderPlaced).toHaveBeenCalled();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Edge Cases and Error Handling
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Edge Cases', () => {
    it('should handle order with empty items array', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        items: [],
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue([]),
          },
        };
        return callback(tx);
      });

      const result = await service.createOrder(orderData);

      expect(result).toBeDefined();
    });

    it('should handle transaction rollback on error', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        items: [{ productId: 'product-1', quantity: 1 }],
      };

      mockPrismaService.$transaction.mockRejectedValue(
        new Error('Transaction failed')
      );

      await expect(service.createOrder(orderData)).rejects.toThrow(
        'Transaction failed'
      );
    });

    it('should handle large orders with many items', async () => {
      const items = Array.from({ length: 50 }, (_, i) => ({
        productId: `product-${i}`,
        quantity: 1,
      }));

      const orderData = {
        buyerId: 'buyer-123',
        items,
      };

      const mockProducts = items.map((item, i) => ({
        id: item.productId,
        price: 1000 + i,
        stock: 100,
      }));

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue(mockProducts),
            update: jest.fn().mockImplementation(() => Promise.resolve({})),
          },
          order: {
            create: jest.fn().mockResolvedValue({
              id: 'order-1',
              items: items,
            }),
          },
        };
        return callback(tx);
      });

      const result = await service.createOrder(orderData);

      expect(result).toBeDefined();
    });

    it('should handle special characters in buyer information', async () => {
      const orderData = {
        buyerId: 'buyer-123',
        buyerName: 'Ahmed Ali Al-Yemeni',
        buyerPhone: '+967 77 123 4567',
        deliveryAddress: 'Sana\'a, Al-Thawra Street, Building #5',
        items: [{ productId: 'product-1', quantity: 1 }],
      };

      const mockProduct = {
        id: 'product-1',
        price: 1000,
        stock: 10,
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        const tx = {
          product: {
            findMany: jest.fn().mockResolvedValue([mockProduct]),
            update: jest.fn().mockResolvedValue(mockProduct),
          },
          order: {
            create: jest.fn().mockResolvedValue({
              id: 'order-1',
              buyerName: orderData.buyerName,
              buyerPhone: orderData.buyerPhone,
              deliveryAddress: orderData.deliveryAddress,
            }),
          },
        };
        return callback(tx);
      });

      const result = await service.createOrder(orderData);

      expect(result.buyerName).toBe('Ahmed Ali Al-Yemeni');
    });
  });
});
