/**
 * Profiles Service
 * خدمة إدارة ملفات البائعين والمشترين
 *
 * ─────────────────────────────────────────────────────────────────────────
 * SECURITY — tenant isolation model
 * ─────────────────────────────────────────────────────────────────────────
 * Both `SellerProfile.userId` and `BuyerProfile.userId` are @unique globally
 * (one profile per user across all tenants). `tenantId` on the row is a
 * stamp that records where the profile was originally created.
 *
 * Lookups by `userId` are safe when `userId` is the authenticated caller's
 * own id (derived from JWT), since an attacker cannot forge another user's
 * JWT. Lookups by `id` or by a URL-parameter `userId` MUST carry `tenantId`
 * (bound via the new `id_tenantId` composite unique) to prevent cross-tenant
 * PII leakage — these profiles expose `taxId`, `bankAccount`, and
 * `shippingAddresses`.
 */

import {
  Injectable,
  NotFoundException,
  ConflictException,
  BadRequestException,
} from "@nestjs/common";
// Note: Using 'any' type for JSON fields to avoid Prisma version-specific type issues
import { PrismaService } from "../prisma/prisma.service";
import {
  CreateSellerProfileDto,
  UpdateSellerProfileDto,
  CreateBuyerProfileDto,
  UpdateBuyerProfileDto,
  AddShippingAddressDto,
  UpdateLoyaltyPointsDto,
  ShippingAddress,
} from "../dto/profiles.dto";

@Injectable()
export class ProfilesService {
  constructor(private readonly prisma: PrismaService) {}

  // ═══════════════════════════════════════════════════════════════════════════
  // Seller Profile Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء ملف تعريف بائع جديد.
   *
   * SECURITY: tenantId is REQUIRED and sourced from the authenticated
   * caller's JWT — NOT from `dto.tenantId` (which would allow tenant
   * forgery). The controller is responsible for overriding `dto.userId`
   * with `req.user.id` before calling this method.
   */
  async createSellerProfile(
    dto: CreateSellerProfileDto,
    tenantId: string,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    // Check if seller profile already exists (userId is @unique globally).
    const existing = await this.prisma.sellerProfile.findUnique({
      where: { userId: dto.userId },
    });

    if (existing) {
      throw new ConflictException(
        "Seller profile already exists for this user",
      );
    }

    return this.prisma.sellerProfile.create({
      data: {
        userId: dto.userId,
        tenantId,
        businessName: dto.businessName,
        businessType: dto.businessType,
        taxId: dto.taxId,
        bankAccount: dto.bankAccount,
        payoutPreferences: dto.payoutPreferences,
      },
    });
  }

  /**
   * جلب ملف تعريف البائع بواسطة معرف المستخدم.
   *
   * SECURITY: when `tenantId` is supplied the lookup filters on it via
   * `findFirst({userId, tenantId})` — a cross-tenant `userId` returns null.
   * When `tenantId` is omitted, behaviour is unchanged for internal tooling.
   */
  async getSellerProfileByUserId(userId: string, tenantId?: string) {
    const profile = tenantId
      ? await this.prisma.sellerProfile.findFirst({
          where: { userId, tenantId },
          include: {
            reviewResponses: {
              include: { review: true },
              orderBy: { createdAt: "desc" },
              take: 10,
            },
          },
        })
      : await this.prisma.sellerProfile.findUnique({
          where: { userId },
          include: {
            reviewResponses: {
              include: { review: true },
              orderBy: { createdAt: "desc" },
              take: 10,
            },
          },
        });

    if (!profile) {
      throw new NotFoundException("Seller profile not found");
    }

    return profile;
  }

  /**
   * جلب ملف تعريف البائع بواسطة المعرف — REQUIRES tenantId.
   *
   * SECURITY: this is the hot IDOR surface. `id` is exposed on URLs and
   * a cross-tenant caller could guess it and read another tenant's
   * seller PII (taxId, bankAccount). The composite id_tenantId unique
   * makes this impossible without a matching tenantId.
   */
  async getSellerProfileById(id: string, tenantId: string) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const profile = await this.prisma.sellerProfile.findUnique({
      where: { id_tenantId: { id, tenantId } },
      include: {
        reviewResponses: {
          include: { review: true },
          orderBy: { createdAt: "desc" },
          take: 10,
        },
      },
    });

    if (!profile) {
      throw new NotFoundException("Seller profile not found");
    }

    return profile;
  }

  /**
   * تحديث ملف تعريف البائع.
   *
   * SECURITY: the `userId` passed in MUST be the authenticated caller's
   * own id (controller enforces this via JWT `sub`). tenantId is used
   * on both the pre-check and the UPDATE so a stale/forged userId from a
   * different tenant returns 404.
   */
  async updateSellerProfile(
    userId: string,
    dto: UpdateSellerProfileDto,
    tenantId: string,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const profile = await this.prisma.sellerProfile.findFirst({
      where: { userId, tenantId },
    });

    if (!profile) {
      throw new NotFoundException("Seller profile not found");
    }

    return this.prisma.sellerProfile.update({
      where: { id_tenantId: { id: profile.id, tenantId } },
      data: {
        ...(dto.businessName && { businessName: dto.businessName }),
        ...(dto.businessType && { businessType: dto.businessType }),
        ...(dto.taxId !== undefined && { taxId: dto.taxId }),
        ...(dto.bankAccount !== undefined && { bankAccount: dto.bankAccount }),
        ...(dto.payoutPreferences !== undefined && {
          payoutPreferences: dto.payoutPreferences,
        }),
      },
    });
  }

  /**
   * التحقق من ملف تعريف البائع — admin / KYC operation.
   */
  async verifySellerProfile(
    userId: string,
    verified: boolean,
    tenantId: string,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const profile = await this.prisma.sellerProfile.findFirst({
      where: { userId, tenantId },
    });

    if (!profile) {
      throw new NotFoundException("Seller profile not found");
    }

    return this.prisma.sellerProfile.update({
      where: { id_tenantId: { id: profile.id, tenantId } },
      data: {
        verified,
        verifiedAt: verified ? new Date() : null,
      },
    });
  }

  /**
   * جلب جميع البائعين (مع الفلترة).
   *
   * SECURITY: `tenantId` is REQUIRED for non-admin callers. Callers must
   * set `isAdmin` via server-side role check — never trust a client-
   * supplied flag (the controller enforces this from the JWT).
   */
  async getAllSellers(filters: {
    businessType?: string;
    verified?: boolean;
    tenantId?: string;
    minRating?: number;
    isAdmin?: boolean;
  }) {
    const where: any = {};

    if (filters.businessType) {
      where.businessType = filters.businessType;
    }

    if (filters.verified !== undefined) {
      where.verified = filters.verified;
    }

    // tenantId is required for non-admin callers. `isAdmin` MUST only be
    // set by the controller after a server-side role check — never from
    // a request parameter.
    if (filters.tenantId) {
      where.tenantId = filters.tenantId;
    } else if (!filters.isAdmin) {
      throw new BadRequestException(
        "tenantId required for non-admin access to seller list",
      );
    }

    if (filters.minRating) {
      where.rating = { gte: filters.minRating };
    }

    return this.prisma.sellerProfile.findMany({
      where,
      orderBy: { rating: "desc" },
      take: 100,
    });
  }

  /**
   * تحديث إحصائيات البائع (داخلي - يتم استدعاؤه عند إتمام طلب).
   *
   * SECURITY: internal helper invoked from the order flow. tenantId is
   * REQUIRED — the caller already knows the tenant that owns the order.
   */
  async updateSellerStats(
    userId: string,
    saleAmount: number,
    tenantId: string,
    incrementSales = 1,
  ) {
    const profile = await this.prisma.sellerProfile.findFirst({
      where: { userId, tenantId },
    });

    if (!profile) {
      return null;
    }

    return this.prisma.sellerProfile.update({
      where: { id_tenantId: { id: profile.id, tenantId } },
      data: {
        totalSales: { increment: incrementSales },
        totalRevenue: { increment: saleAmount },
      },
    });
  }

  /**
   * تحديث تقييم البائع (داخلي - يتم استدعاؤه عند إضافة تقييم).
   */
  async updateSellerRating(
    sellerId: string,
    newAverageRating: number,
    tenantId: string,
  ) {
    return this.prisma.sellerProfile.update({
      where: { id_tenantId: { id: sellerId, tenantId } },
      data: { rating: newAverageRating },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Buyer Profile Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء ملف تعريف مشتري جديد.
   * SECURITY: see createSellerProfile — tenantId from JWT only.
   */
  async createBuyerProfile(dto: CreateBuyerProfileDto, tenantId: string) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const existing = await this.prisma.buyerProfile.findUnique({
      where: { userId: dto.userId },
    });

    if (existing) {
      throw new ConflictException("Buyer profile already exists for this user");
    }

    return this.prisma.buyerProfile.create({
      data: {
        userId: dto.userId,
        tenantId,
        shippingAddresses: (dto.shippingAddresses || []) as any,
        preferredPayment: dto.preferredPayment,
      },
    });
  }

  async getBuyerProfileByUserId(userId: string, tenantId?: string) {
    const profile = tenantId
      ? await this.prisma.buyerProfile.findFirst({
          where: { userId, tenantId },
          include: {
            reviews: { orderBy: { createdAt: "desc" }, take: 10 },
          },
        })
      : await this.prisma.buyerProfile.findUnique({
          where: { userId },
          include: {
            reviews: { orderBy: { createdAt: "desc" }, take: 10 },
          },
        });

    if (!profile) {
      throw new NotFoundException("Buyer profile not found");
    }

    return profile;
  }

  /**
   * جلب ملف تعريف المشتري بواسطة المعرف — REQUIRES tenantId (PII).
   */
  async getBuyerProfileById(id: string, tenantId: string) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const profile = await this.prisma.buyerProfile.findUnique({
      where: { id_tenantId: { id, tenantId } },
      include: {
        reviews: { orderBy: { createdAt: "desc" }, take: 10 },
      },
    });

    if (!profile) {
      throw new NotFoundException("Buyer profile not found");
    }

    return profile;
  }

  async updateBuyerProfile(
    userId: string,
    dto: UpdateBuyerProfileDto,
    tenantId: string,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const profile = await this.prisma.buyerProfile.findFirst({
      where: { userId, tenantId },
    });

    if (!profile) {
      throw new NotFoundException("Buyer profile not found");
    }

    return this.prisma.buyerProfile.update({
      where: { id_tenantId: { id: profile.id, tenantId } },
      data: {
        ...(dto.shippingAddresses !== undefined && {
          shippingAddresses: dto.shippingAddresses as any,
        }),
        ...(dto.preferredPayment !== undefined && {
          preferredPayment: dto.preferredPayment,
        }),
      },
    });
  }

  async addShippingAddress(
    userId: string,
    dto: AddShippingAddressDto,
    tenantId: string,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const profile = await this.prisma.buyerProfile.findFirst({
      where: { userId, tenantId },
    });

    if (!profile) {
      throw new NotFoundException("Buyer profile not found");
    }

    const addresses =
      (profile.shippingAddresses as unknown as ShippingAddress[]) || [];

    if (dto.isDefault) {
      addresses.forEach((addr) => (addr.isDefault = false));
    }

    const isDefault = addresses.length === 0 ? true : dto.isDefault || false;

    addresses.push({
      label: dto.label,
      address: dto.address,
      city: dto.city,
      phone: dto.phone,
      isDefault,
    });

    return this.prisma.buyerProfile.update({
      where: { id_tenantId: { id: profile.id, tenantId } },
      data: { shippingAddresses: addresses as any },
    });
  }

  async removeShippingAddress(
    userId: string,
    addressLabel: string,
    tenantId: string,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const profile = await this.prisma.buyerProfile.findFirst({
      where: { userId, tenantId },
    });

    if (!profile) {
      throw new NotFoundException("Buyer profile not found");
    }

    const addresses =
      (profile.shippingAddresses as unknown as ShippingAddress[]) || [];
    const filteredAddresses = addresses.filter(
      (addr) => addr.label !== addressLabel,
    );

    return this.prisma.buyerProfile.update({
      where: { id_tenantId: { id: profile.id, tenantId } },
      data: { shippingAddresses: filteredAddresses as any },
    });
  }

  async updateLoyaltyPoints(
    userId: string,
    dto: UpdateLoyaltyPointsDto,
    tenantId: string,
  ) {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }

    const profile = await this.prisma.buyerProfile.findFirst({
      where: { userId, tenantId },
    });

    if (!profile) {
      throw new NotFoundException("Buyer profile not found");
    }

    const newPoints = profile.loyaltyPoints + dto.points;

    if (newPoints < 0) {
      throw new BadRequestException("Insufficient loyalty points");
    }

    return this.prisma.buyerProfile.update({
      where: { id_tenantId: { id: profile.id, tenantId } },
      data: { loyaltyPoints: newPoints },
    });
  }

  /**
   * تحديث إحصائيات المشتري (داخلي - يتم استدعاؤه عند إتمام طلب).
   */
  async updateBuyerStats(
    userId: string,
    purchaseAmount: number,
    tenantId: string,
    incrementPurchases = 1,
  ) {
    const profile = await this.prisma.buyerProfile.findFirst({
      where: { userId, tenantId },
    });

    if (!profile) {
      return null;
    }

    const loyaltyPointsEarned = Math.floor(purchaseAmount / 100);

    return this.prisma.buyerProfile.update({
      where: { id_tenantId: { id: profile.id, tenantId } },
      data: {
        totalPurchases: { increment: incrementPurchases },
        totalSpent: { increment: purchaseAmount },
        loyaltyPoints: { increment: loyaltyPointsEarned },
      },
    });
  }

  /**
   * جلب جميع المشترين (مع الفلترة).
   */
  async getAllBuyers(filters: {
    tenantId?: string;
    minPurchases?: number;
    minLoyaltyPoints?: number;
    isAdmin?: boolean;
  }) {
    const where: any = {};

    if (filters.tenantId) {
      where.tenantId = filters.tenantId;
    } else if (!filters.isAdmin) {
      throw new BadRequestException(
        "tenantId required for non-admin access to buyer list",
      );
    }

    if (filters.minPurchases) {
      where.totalPurchases = { gte: filters.minPurchases };
    }

    if (filters.minLoyaltyPoints) {
      where.loyaltyPoints = { gte: filters.minLoyaltyPoints };
    }

    return this.prisma.buyerProfile.findMany({
      where,
      orderBy: { totalSpent: "desc" },
      take: 100,
    });
  }
}
