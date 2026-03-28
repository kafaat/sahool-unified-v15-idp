/**
 * SAHOOL Market Service
 * خدمة السوق - إدارة المنتجات والطلبات
 *
 * Features:
 * - Product listing and management
 * - Smart harvest-to-product conversion
 * - Order processing
 * - Redis caching for performance
 */

import {
  Injectable,
  NotFoundException,
  Inject,
  forwardRef,
  Logger,
} from "@nestjs/common";
import { Prisma } from "../../prisma/generated/client";
import { PrismaService } from "../prisma/prisma.service";
import { EventsService } from "../events/events.service";

/** Safely convert a Prisma.Decimal (or number) to a plain number for arithmetic. */
function toNum(v: Prisma.Decimal | number | null | undefined): number {
  if (v == null) return 0;
  return typeof v === "number" ? v : Number(v);
}
import { CacheService, CACHE_KEYS, CACHE_TTL } from "../cache/cache.service";
import {
  calculatePagination,
  createPaginatedResponse,
  GENERAL_TRANSACTION_CONFIG,
  type PaginationParams,
  type PaginatedResponse,
} from "../utils/db-utils";

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
  private readonly logger = new Logger(MarketService.name);

  /** Service fee rate applied to order subtotal (2%) */
  private static readonly SERVICE_FEE_RATE = parseFloat(
    process.env.MARKETPLACE_SERVICE_FEE_RATE || "0.02",
  );

  /** Fixed delivery fee in YER (Yemeni Rial) */
  private static readonly DELIVERY_FEE = parseFloat(
    process.env.MARKETPLACE_DELIVERY_FEE || "500",
  );

  constructor(
    private prisma: PrismaService,
    @Inject(forwardRef(() => EventsService))
    private eventsService: EventsService,
    private cacheService: CacheService,
  ) {}

  // ═══════════════════════════════════════════════════════════════════════════
  // المنتجات - Products
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * الحصول على جميع المنتجات
   */
  async findAllProducts(
    filters?: {
      category?: string;
      governorate?: string;
      sellerId?: string;
      tenantId?: string;
      minPrice?: number;
      maxPrice?: number;
    } & PaginationParams,
  ): Promise<PaginatedResponse<any>> {
    const {
      category,
      governorate,
      sellerId,
      minPrice,
      maxPrice,
      ...paginationParams
    } = filters || {};

    // Calculate pagination with enforced limits
    const { skip, take, page } = calculatePagination(paginationParams);

    // Build where clause
    const where: any = { status: "AVAILABLE" };

    if (category) where.category = category;
    if (governorate) where.governorate = governorate;
    if (sellerId) where.sellerId = sellerId;
    if (minPrice || maxPrice) {
      where.price = {};
      if (minPrice) where.price.gte = minPrice;
      if (maxPrice) where.price.lte = maxPrice;
    }

    // Execute queries in parallel
    const [data, total] = await Promise.all([
      this.prisma.product.findMany({
        where,
        select: {
          id: true,
          name: true,
          nameAr: true,
          category: true,
          price: true,
          stock: true,
          unit: true,
          imageUrl: true,
          featured: true,
          sellerId: true,
          sellerType: true,
          sellerName: true,
          cropType: true,
          governorate: true,
          district: true,
          qualityGrade: true,
          harvestDate: true,
          createdAt: true,
        },
        skip,
        take,
        orderBy: [{ featured: "desc" }, { createdAt: "desc" }],
      }),
      this.prisma.product.count({ where }),
    ]);

    return createPaginatedResponse(data, total, { page, take });
  }

  /**
   * الحصول على منتج بالمعرف (مع التخزين المؤقت)
   */
  async findProductById(id: string, tenantId?: string) {
    const cacheKey = CACHE_KEYS.PRODUCT(id);

    // Try cache first
    const cached = await this.cacheService.get<any>(cacheKey);
    if (cached) {
      // Validate tenant isolation even for cached results
      if (tenantId && cached.tenantId && cached.tenantId !== tenantId) {
        throw new NotFoundException("المنتج غير موجود");
      }
      this.logger.debug(`Product ${id} served from cache`);
      return cached;
    }

    const product = await this.prisma.product.findUnique({ where: { id } });
    if (!product) throw new NotFoundException("المنتج غير موجود");

    // Validate tenant isolation
    if (tenantId && product.tenantId && product.tenantId !== tenantId) {
      throw new NotFoundException("المنتج غير موجود");
    }

    // Cache the product
    await this.cacheService.set(cacheKey, product, CACHE_TTL.MEDIUM);

    return product;
  }

  /**
   * إنشاء منتج جديد (مع إبطال التخزين المؤقت)
   */
  async createProduct(data: CreateProductDto, tenantId?: string) {
    const product = await this.prisma.product.create({
      data: {
        name: data.name,
        nameAr: data.nameAr,
        category: data.category as any, // Cast to Prisma enum type
        price: data.price,
        stock: data.stock,
        unit: data.unit,
        description: data.description,
        descriptionAr: data.descriptionAr,
        imageUrl: data.imageUrl,
        sellerId: data.sellerId,
        sellerType: data.sellerType as any, // Cast to Prisma enum type
        sellerName: data.sellerName,
        cropType: data.cropType,
        governorate: data.governorate,
      },
    });

    // Invalidate relevant caches
    await this.cacheService.invalidateProduct(product.id, data.sellerId);

    return product;
  }

  /**
   * ⭐ الميزة الذكية: تحويل توقع الحصاد إلى منتج
   * يتم استدعاء هذا عندما يوافق المزارع على توقع yield-engine
   */
  async convertYieldToProduct(userId: string, yieldData: YieldData, tenantId?: string) {
    const currentYear = new Date().getFullYear();

    return this.prisma.product.create({
      data: {
        name: `Premium ${yieldData.crop} Harvest - ${currentYear} Season`,
        nameAr: `حصاد ${yieldData.cropAr} عالي الجودة - موسم ${currentYear}`,
        description: `High-quality ${yieldData.crop} harvest with predicted yield of ${yieldData.predictedYieldTons} tons. Verified SAHOOL farmer.`,
        descriptionAr: `محصول ${yieldData.cropAr} عالي الجودة بإنتاجية متوقعة ${yieldData.predictedYieldTons} طن. مزارع موثق عبر منصة سهول.`,
        category: "HARVEST",
        price: yieldData.pricePerTon,
        stock: yieldData.predictedYieldTons,
        unit: "ton",
        sellerId: userId,
        sellerType: "FARMER",
        cropType: yieldData.crop,
        harvestDate: yieldData.harvestDate
          ? new Date(yieldData.harvestDate)
          : null,
        qualityGrade: yieldData.qualityGrade || "A",
        governorate: yieldData.governorate,
        district: yieldData.district,
        imageUrl: this.getCropImageUrl(yieldData.crop),
      },
    });
  }

  /**
   * الحصول على صورة افتراضية للمحصول
   */
  // TODO: Move crop images to CDN configuration (env var or database)
  private getCropImageUrl(crop: string): string {
    const cropImages: Record<string, string> = {
      wheat: "https://cdn.sahool.io/crops/wheat.jpg",
      coffee: "https://cdn.sahool.io/crops/coffee.jpg",
      tomato: "https://cdn.sahool.io/crops/tomato.jpg",
      banana: "https://cdn.sahool.io/crops/banana.jpg",
      mango: "https://cdn.sahool.io/crops/mango.jpg",
      grapes: "https://cdn.sahool.io/crops/grapes.jpg",
      corn: "https://cdn.sahool.io/crops/corn.jpg",
      potato: "https://cdn.sahool.io/crops/potato.jpg",
    };
    return (
      cropImages[crop.toLowerCase()] ||
      "https://cdn.sahool.io/crops/default.jpg"
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الطلبات - Orders
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء طلب جديد
   * Uses transaction to prevent race conditions in stock management
   */
  async createOrder(data: CreateOrderDto, tenantId?: string) {
    // Use transaction with timeout to ensure atomic stock check and decrement
    return this.prisma.$transaction(async (tx) => {
      // Batch fetch all products at once to avoid N+1 queries
      const productIds = data.items.map((item) => item.productId);
      const products = await tx.product.findMany({
        where: { id: { in: productIds } },
      });

      // Create a typed map for quick lookup
      type ProductType = (typeof products)[number];
      const productMap = new Map<string, ProductType>(
        products.map((p: ProductType): [string, ProductType] => [p.id, p]),
      );

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
          throw new Error(
            `الكمية المطلوبة غير متوفرة للمنتج: ${product.nameAr}`,
          );
        }

        const productPrice = toNum(product.price);
        const totalPrice = productPrice * item.quantity;
        subtotal += totalPrice;

        orderItems.push({
          productId: item.productId,
          quantity: item.quantity,
          unitPrice: productPrice,
          totalPrice,
        });

        stockUpdates.push({
          id: item.productId,
          quantity: item.quantity,
        });
      }

      // Batch update stock atomically within transaction
      const updatedProducts = await Promise.all(
        stockUpdates.map((update) =>
          tx.product.update({
            where: { id: update.id },
            data: { stock: { decrement: update.quantity } },
          }),
        ),
      );

      // Check for low stock after update (outside transaction to avoid blocking)
      // We'll do this in a non-blocking way after the transaction completes
      Promise.all(
        updatedProducts.map(async (product: ProductType) => {
          const LOW_STOCK_THRESHOLD = parseInt(process.env.LOW_STOCK_THRESHOLD || "10", 10);
          if (product.stock <= LOW_STOCK_THRESHOLD && product.stock > 0) {
            await this.eventsService.publishInventoryLowStock({
              productId: product.id,
              productName: product.nameAr || product.name,
              currentStock: product.stock,
              threshold: LOW_STOCK_THRESHOLD,
              unit: product.unit,
            });
          }
        }),
      ).catch((err) => {
        // Log error but don't fail the order
        console.error("Error publishing inventory low stock events:", err);
      });

      const serviceFee = subtotal * MarketService.SERVICE_FEE_RATE;
      const deliveryFee = MarketService.DELIVERY_FEE;
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

      // Publish order.placed event to NATS
      await this.eventsService.publishOrderPlaced({
        orderId: order.id,
        userId: order.buyerId,
        items: orderItems.map((item) => ({
          productId: item.productId,
          quantity: item.quantity,
          price: item.unitPrice,
        })),
        totalAmount: toNum(order.totalAmount),
        currency: "YER", // Yemeni Rial
      });

      return order;
    }, GENERAL_TRANSACTION_CONFIG);
  }

  /**
   * الحصول على طلبات المستخدم مع الترقيم
   */
  async getUserOrders(
    userId: string,
    role: "buyer" | "seller",
    params?: PaginationParams,
  ): Promise<PaginatedResponse<any>> {
    // Calculate pagination with enforced limits
    const { skip, take, page } = calculatePagination(params);

    // Build where clause based on role
    const where =
      role === "buyer"
        ? { buyerId: userId }
        : {
            items: {
              some: {
                product: { sellerId: userId },
              },
            },
          };

    // Execute queries in parallel
    const [data, total] = await Promise.all([
      this.prisma.order.findMany({
        where,
        select: {
          id: true,
          orderNumber: true,
          buyerId: true,
          buyerName: true,
          buyerPhone: true,
          status: true,
          subtotal: true,
          serviceFee: true,
          deliveryFee: true,
          totalAmount: true,
          deliveryAddress: true,
          paymentMethod: true,
          createdAt: true,
          updatedAt: true,
          items: {
            select: {
              id: true,
              quantity: true,
              unitPrice: true,
              totalPrice: true,
              product: {
                select: {
                  id: true,
                  name: true,
                  nameAr: true,
                  category: true,
                  imageUrl: true,
                  unit: true,
                  sellerId: true,
                  sellerName: true,
                },
              },
            },
          },
        },
        skip,
        take,
        orderBy: { createdAt: "desc" },
      }),
      this.prisma.order.count({ where }),
    ]);

    return createPaginatedResponse(data, total, { page, take });
  }

  /**
   * الحصول على إحصائيات السوق (مع التخزين المؤقت)
   */
  async getMarketStats(tenantId?: string) {
    const cacheKey = CACHE_KEYS.MARKET_STATS();

    // Try cache first
    const cached = await this.cacheService.get<any>(cacheKey);
    if (cached) {
      this.logger.debug("Market stats served from cache");
      return cached;
    }

    const tenantFilter = tenantId ? { tenantId } : {};

    const [totalProducts, totalHarvests, totalOrders, recentProducts] =
      await Promise.all([
        this.prisma.product.count({ where: { status: "AVAILABLE", ...tenantFilter } }),
        this.prisma.product.count({
          where: { category: "HARVEST", status: "AVAILABLE", ...tenantFilter },
        }),
        this.prisma.order.count({ where: { ...tenantFilter } }),
        this.prisma.product.findMany({
          where: { status: "AVAILABLE", ...tenantFilter },
          orderBy: { createdAt: "desc" },
          take: 5,
          select: {
            id: true,
            name: true,
            nameAr: true,
            category: true,
            price: true,
            stock: true,
            unit: true,
            imageUrl: true,
            createdAt: true,
          },
        }),
      ]);

    const stats = {
      totalProducts,
      totalHarvests,
      totalOrders,
      recentProducts,
      timestamp: new Date().toISOString(),
    };

    // Cache the stats
    await this.cacheService.set(cacheKey, stats, CACHE_TTL.STATS);

    return stats;
  }
}
