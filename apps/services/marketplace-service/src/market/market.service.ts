/**
 * SAHOOL Market Service
 * خدمة السوق - إدارة المنتجات والطلبات
 *
 * Features:
 * - Product listing and management
 * - Smart harvest-to-product conversion
 * - Order processing
 */

import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

// Types
interface YieldData {
  crop: string;
  cropAr: string;
  predictedYieldTons: number;
  pricePerTon: number;
  harvestDate?: string;
  qualityGrade?: string;
  governorate?: string;
  district?: string;
}

interface CreateProductDto {
  name: string;
  nameAr: string;
  category: string;
  price: number;
  stock: number;
  unit: string;
  description?: string;
  descriptionAr?: string;
  imageUrl?: string;
  sellerId: string;
  sellerType: string;
  sellerName?: string;
  cropType?: string;
  governorate?: string;
}

interface CreateOrderDto {
  buyerId: string;
  buyerName?: string;
  buyerPhone?: string;
  items: { productId: string; quantity: number }[];
  deliveryAddress?: string;
  paymentMethod?: string;
}

@Injectable()
export class MarketService {
  constructor(private prisma: PrismaService) {}

  // ═══════════════════════════════════════════════════════════════════════════
  // المنتجات - Products
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * الحصول على جميع المنتجات
   */
  async findAllProducts(filters?: {
    category?: string;
    governorate?: string;
    sellerId?: string;
    minPrice?: number;
    maxPrice?: number;
  }) {
    const where: any = { status: 'AVAILABLE' };

    if (filters?.category) where.category = filters.category;
    if (filters?.governorate) where.governorate = filters.governorate;
    if (filters?.sellerId) where.sellerId = filters.sellerId;
    if (filters?.minPrice || filters?.maxPrice) {
      where.price = {};
      if (filters.minPrice) where.price.gte = filters.minPrice;
      if (filters.maxPrice) where.price.lte = filters.maxPrice;
    }

    return this.prisma.product.findMany({
      where,
      orderBy: [{ featured: 'desc' }, { createdAt: 'desc' }],
    });
  }

  /**
   * الحصول على منتج بالمعرف
   */
  async findProductById(id: string) {
    const product = await this.prisma.product.findUnique({ where: { id } });
    if (!product) throw new NotFoundException('المنتج غير موجود');
    return product;
  }

  /**
   * إنشاء منتج جديد
   */
  async createProduct(data: CreateProductDto) {
    return this.prisma.product.create({
      data: {
        name: data.name,
        nameAr: data.nameAr,
        category: data.category,
        price: data.price,
        stock: data.stock,
        unit: data.unit,
        description: data.description,
        descriptionAr: data.descriptionAr,
        imageUrl: data.imageUrl,
        sellerId: data.sellerId,
        sellerType: data.sellerType,
        sellerName: data.sellerName,
        cropType: data.cropType,
        governorate: data.governorate,
      },
    });
  }

  /**
   * ⭐ الميزة الذكية: تحويل توقع الحصاد إلى منتج
   * يتم استدعاء هذا عندما يوافق المزارع على توقع yield-engine
   */
  async convertYieldToProduct(userId: string, yieldData: YieldData) {
    const currentYear = new Date().getFullYear();

    return this.prisma.product.create({
      data: {
        name: `Premium ${yieldData.crop} Harvest - ${currentYear} Season`,
        nameAr: `حصاد ${yieldData.cropAr} عالي الجودة - موسم ${currentYear}`,
        description: `High-quality ${yieldData.crop} harvest with predicted yield of ${yieldData.predictedYieldTons} tons. Verified SAHOOL farmer.`,
        descriptionAr: `محصول ${yieldData.cropAr} عالي الجودة بإنتاجية متوقعة ${yieldData.predictedYieldTons} طن. مزارع موثق عبر منصة سهول.`,
        category: 'HARVEST',
        price: yieldData.pricePerTon,
        stock: yieldData.predictedYieldTons,
        unit: 'ton',
        sellerId: userId,
        sellerType: 'FARMER',
        cropType: yieldData.crop,
        harvestDate: yieldData.harvestDate
          ? new Date(yieldData.harvestDate)
          : null,
        qualityGrade: yieldData.qualityGrade || 'A',
        governorate: yieldData.governorate,
        district: yieldData.district,
        imageUrl: this.getCropImageUrl(yieldData.crop),
      },
    });
  }

  /**
   * الحصول على صورة افتراضية للمحصول
   */
  private getCropImageUrl(crop: string): string {
    const cropImages: Record<string, string> = {
      wheat: 'https://cdn.sahool.io/crops/wheat.jpg',
      coffee: 'https://cdn.sahool.io/crops/coffee.jpg',
      tomato: 'https://cdn.sahool.io/crops/tomato.jpg',
      banana: 'https://cdn.sahool.io/crops/banana.jpg',
      mango: 'https://cdn.sahool.io/crops/mango.jpg',
      grapes: 'https://cdn.sahool.io/crops/grapes.jpg',
      corn: 'https://cdn.sahool.io/crops/corn.jpg',
      potato: 'https://cdn.sahool.io/crops/potato.jpg',
    };
    return cropImages[crop.toLowerCase()] || 'https://cdn.sahool.io/crops/default.jpg';
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الطلبات - Orders
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء طلب جديد
   * Uses transaction to prevent race conditions in stock management
   */
  async createOrder(data: CreateOrderDto) {
    // Use transaction to ensure atomic stock check and decrement
    return this.prisma.$transaction(async (tx) => {
      // Batch fetch all products at once to avoid N+1 queries
      const productIds = data.items.map((item) => item.productId);
      const products = await tx.product.findMany({
        where: { id: { in: productIds } },
      });

      // Create a typed map for quick lookup
      type ProductType = typeof products[number];
      const productMap = new Map<string, ProductType>(products.map((p) => [p.id, p]));

      // حساب المبالغ
      let subtotal = 0;
      const orderItems: any[] = [];
      const stockUpdates: any[] = [];

      for (const item of data.items) {
        const product = productMap.get(item.productId);

        if (!product) {
          throw new Error(`المنتج غير موجود: ${item.productId}`);
        }

        if (product.stock < item.quantity) {
          throw new Error(`الكمية المطلوبة غير متوفرة للمنتج: ${product.nameAr}`);
        }

        const totalPrice = product.price * item.quantity;
        subtotal += totalPrice;

        orderItems.push({
          productId: item.productId,
          quantity: item.quantity,
          unitPrice: product.price,
          totalPrice,
        });

        stockUpdates.push({
          id: item.productId,
          quantity: item.quantity,
        });
      }

      // Batch update stock atomically within transaction
      await Promise.all(
        stockUpdates.map((update) =>
          tx.product.update({
            where: { id: update.id },
            data: { stock: { decrement: update.quantity } },
          }),
        ),
      );

      const serviceFee = subtotal * 0.02; // 2% رسوم خدمة
      const deliveryFee = 500; // رسوم توصيل ثابتة (ريال يمني)
      const totalAmount = subtotal + serviceFee + deliveryFee;

      // إنشاء رقم الطلب
      const orderNumber = `SAH-${Date.now().toString(36).toUpperCase()}`;

      // إنشاء الطلب
      const order = await tx.order.create({
        data: {
          orderNumber,
          buyerId: data.buyerId,
          buyerName: data.buyerName,
          buyerPhone: data.buyerPhone,
          subtotal,
          serviceFee,
          deliveryFee,
          totalAmount,
          deliveryAddress: data.deliveryAddress,
          paymentMethod: data.paymentMethod,
          items: {
            create: orderItems,
          },
        },
        include: { items: true },
      });

      return order;
    });
  }

  /**
   * الحصول على طلبات المستخدم
   */
  async getUserOrders(userId: string, role: 'buyer' | 'seller') {
    if (role === 'buyer') {
      return this.prisma.order.findMany({
        where: { buyerId: userId },
        include: { items: { include: { product: true } } },
        orderBy: { createdAt: 'desc' },
      });
    }

    // للبائع - نجلب الطلبات التي تحتوي على منتجاته
    return this.prisma.order.findMany({
      where: {
        items: {
          some: {
            product: { sellerId: userId },
          },
        },
      },
      include: { items: { include: { product: true } } },
      orderBy: { createdAt: 'desc' },
    });
  }

  /**
   * الحصول على إحصائيات السوق
   */
  async getMarketStats() {
    const [totalProducts, totalHarvests, totalOrders, recentProducts] =
      await Promise.all([
        this.prisma.product.count({ where: { status: 'AVAILABLE' } }),
        this.prisma.product.count({
          where: { category: 'HARVEST', status: 'AVAILABLE' },
        }),
        this.prisma.order.count(),
        this.prisma.product.findMany({
          where: { status: 'AVAILABLE' },
          orderBy: { createdAt: 'desc' },
          take: 5,
        }),
      ]);

    return {
      totalProducts,
      totalHarvests,
      totalOrders,
      recentProducts,
    };
  }
}
