/**
 * Profiles Service
 * خدمة إدارة ملفات البائعين والمشترين
 */

import {
  Injectable,
  NotFoundException,
  ConflictException,
  BadRequestException,
} from '@nestjs/common';
// Note: Using 'any' type for JSON fields to avoid Prisma version-specific type issues
import { PrismaService } from '../prisma/prisma.service';
import {
  CreateSellerProfileDto,
  UpdateSellerProfileDto,
  CreateBuyerProfileDto,
  UpdateBuyerProfileDto,
  AddShippingAddressDto,
  UpdateLoyaltyPointsDto,
  ShippingAddress,
} from '../dto/profiles.dto';

@Injectable()
export class ProfilesService {
  constructor(private readonly prisma: PrismaService) {}

  // ═══════════════════════════════════════════════════════════════════════════
  // Seller Profile Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء ملف تعريف بائع جديد
   */
  async createSellerProfile(dto: CreateSellerProfileDto) {
    // Check if seller profile already exists
    const existing = await this.prisma.sellerProfile.findUnique({
      where: { userId: dto.userId },
    });

    if (existing) {
      throw new ConflictException(
        'Seller profile already exists for this user',
      );
    }

    return this.prisma.sellerProfile.create({
      data: {
        userId: dto.userId,
        tenantId: dto.tenantId,
        businessName: dto.businessName,
        businessType: dto.businessType,
        taxId: dto.taxId,
        bankAccount: dto.bankAccount,
        payoutPreferences: dto.payoutPreferences,
      },
    });
  }

  /**
   * جلب ملف تعريف البائع بواسطة معرف المستخدم
   */
  async getSellerProfileByUserId(userId: string) {
    const profile = await this.prisma.sellerProfile.findUnique({
      where: { userId },
      include: {
        reviewResponses: {
          include: {
            review: true,
          },
          orderBy: { createdAt: 'desc' },
          take: 10,
        },
      },
    });

    if (!profile) {
      throw new NotFoundException('Seller profile not found');
    }

    return profile;
  }

  /**
   * جلب ملف تعريف البائع بواسطة المعرف
   */
  async getSellerProfileById(id: string) {
    const profile = await this.prisma.sellerProfile.findUnique({
      where: { id },
      include: {
        reviewResponses: {
          include: {
            review: true,
          },
          orderBy: { createdAt: 'desc' },
          take: 10,
        },
      },
    });

    if (!profile) {
      throw new NotFoundException('Seller profile not found');
    }

    return profile;
  }

  /**
   * تحديث ملف تعريف البائع
   */
  async updateSellerProfile(userId: string, dto: UpdateSellerProfileDto) {
    const profile = await this.prisma.sellerProfile.findUnique({
      where: { userId },
    });

    if (!profile) {
      throw new NotFoundException('Seller profile not found');
    }

    return this.prisma.sellerProfile.update({
      where: { userId },
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
   * التحقق من ملف تعريف البائع
   */
  async verifySellerProfile(userId: string, verified: boolean) {
    const profile = await this.prisma.sellerProfile.findUnique({
      where: { userId },
    });

    if (!profile) {
      throw new NotFoundException('Seller profile not found');
    }

    return this.prisma.sellerProfile.update({
      where: { userId },
      data: {
        verified,
        verifiedAt: verified ? new Date() : null,
      },
    });
  }

  /**
   * جلب جميع البائعين (مع الفلترة)
   */
  async getAllSellers(filters?: {
    businessType?: string;
    verified?: boolean;
    tenantId?: string;
    minRating?: number;
  }) {
    const where: any = {};

    if (filters?.businessType) {
      where.businessType = filters.businessType;
    }

    if (filters?.verified !== undefined) {
      where.verified = filters.verified;
    }

    if (filters?.tenantId) {
      where.tenantId = filters.tenantId;
    }

    if (filters?.minRating) {
      where.rating = { gte: filters.minRating };
    }

    return this.prisma.sellerProfile.findMany({
      where,
      orderBy: { rating: 'desc' },
    });
  }

  /**
   * تحديث إحصائيات البائع (داخلي - يتم استدعاؤه عند إتمام طلب)
   */
  async updateSellerStats(
    userId: string,
    saleAmount: number,
    incrementSales = 1,
  ) {
    const profile = await this.prisma.sellerProfile.findUnique({
      where: { userId },
    });

    if (!profile) {
      return null;
    }

    return this.prisma.sellerProfile.update({
      where: { userId },
      data: {
        totalSales: { increment: incrementSales },
        totalRevenue: { increment: saleAmount },
      },
    });
  }

  /**
   * تحديث تقييم البائع (داخلي - يتم استدعاؤه عند إضافة تقييم)
   */
  async updateSellerRating(sellerId: string, newAverageRating: number) {
    return this.prisma.sellerProfile.update({
      where: { id: sellerId },
      data: { rating: newAverageRating },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Buyer Profile Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء ملف تعريف مشتري جديد
   */
  async createBuyerProfile(dto: CreateBuyerProfileDto) {
    // Check if buyer profile already exists
    const existing = await this.prisma.buyerProfile.findUnique({
      where: { userId: dto.userId },
    });

    if (existing) {
      throw new ConflictException('Buyer profile already exists for this user');
    }

    return this.prisma.buyerProfile.create({
      data: {
        userId: dto.userId,
        tenantId: dto.tenantId,
        shippingAddresses: (dto.shippingAddresses || []) as any,
        preferredPayment: dto.preferredPayment,
      },
    });
  }

  /**
   * جلب ملف تعريف المشتري بواسطة معرف المستخدم
   */
  async getBuyerProfileByUserId(userId: string) {
    const profile = await this.prisma.buyerProfile.findUnique({
      where: { userId },
      include: {
        reviews: {
          orderBy: { createdAt: 'desc' },
          take: 10,
        },
      },
    });

    if (!profile) {
      throw new NotFoundException('Buyer profile not found');
    }

    return profile;
  }

  /**
   * جلب ملف تعريف المشتري بواسطة المعرف
   */
  async getBuyerProfileById(id: string) {
    const profile = await this.prisma.buyerProfile.findUnique({
      where: { id },
      include: {
        reviews: {
          orderBy: { createdAt: 'desc' },
          take: 10,
        },
      },
    });

    if (!profile) {
      throw new NotFoundException('Buyer profile not found');
    }

    return profile;
  }

  /**
   * تحديث ملف تعريف المشتري
   */
  async updateBuyerProfile(userId: string, dto: UpdateBuyerProfileDto) {
    const profile = await this.prisma.buyerProfile.findUnique({
      where: { userId },
    });

    if (!profile) {
      throw new NotFoundException('Buyer profile not found');
    }

    return this.prisma.buyerProfile.update({
      where: { userId },
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

  /**
   * إضافة عنوان شحن
   */
  async addShippingAddress(userId: string, dto: AddShippingAddressDto) {
    const profile = await this.prisma.buyerProfile.findUnique({
      where: { userId },
    });

    if (!profile) {
      throw new NotFoundException('Buyer profile not found');
    }

    const addresses =
      (profile.shippingAddresses as unknown as ShippingAddress[]) || [];

    // If this is the default address, unset all other defaults
    if (dto.isDefault) {
      addresses.forEach((addr) => (addr.isDefault = false));
    }

    // If this is the first address, make it default
    const isDefault = addresses.length === 0 ? true : dto.isDefault || false;

    addresses.push({
      label: dto.label,
      address: dto.address,
      city: dto.city,
      phone: dto.phone,
      isDefault,
    });

    return this.prisma.buyerProfile.update({
      where: { userId },
      data: { shippingAddresses: addresses as any },
    });
  }

  /**
   * حذف عنوان شحن
   */
  async removeShippingAddress(userId: string, addressLabel: string) {
    const profile = await this.prisma.buyerProfile.findUnique({
      where: { userId },
    });

    if (!profile) {
      throw new NotFoundException('Buyer profile not found');
    }

    const addresses =
      (profile.shippingAddresses as unknown as ShippingAddress[]) || [];
    const filteredAddresses = addresses.filter(
      (addr) => addr.label !== addressLabel,
    );

    return this.prisma.buyerProfile.update({
      where: { userId },
      data: { shippingAddresses: filteredAddresses as any },
    });
  }

  /**
   * تحديث نقاط الولاء
   */
  async updateLoyaltyPoints(userId: string, dto: UpdateLoyaltyPointsDto) {
    const profile = await this.prisma.buyerProfile.findUnique({
      where: { userId },
    });

    if (!profile) {
      throw new NotFoundException('Buyer profile not found');
    }

    const newPoints = profile.loyaltyPoints + dto.points;

    if (newPoints < 0) {
      throw new BadRequestException('Insufficient loyalty points');
    }

    return this.prisma.buyerProfile.update({
      where: { userId },
      data: { loyaltyPoints: newPoints },
    });
  }

  /**
   * تحديث إحصائيات المشتري (داخلي - يتم استدعاؤه عند إتمام طلب)
   */
  async updateBuyerStats(
    userId: string,
    purchaseAmount: number,
    incrementPurchases = 1,
  ) {
    const profile = await this.prisma.buyerProfile.findUnique({
      where: { userId },
    });

    if (!profile) {
      return null;
    }

    // Award loyalty points (1 point per 100 YER spent)
    const loyaltyPointsEarned = Math.floor(purchaseAmount / 100);

    return this.prisma.buyerProfile.update({
      where: { userId },
      data: {
        totalPurchases: { increment: incrementPurchases },
        totalSpent: { increment: purchaseAmount },
        loyaltyPoints: { increment: loyaltyPointsEarned },
      },
    });
  }

  /**
   * جلب جميع المشترين (مع الفلترة)
   */
  async getAllBuyers(filters?: {
    tenantId?: string;
    minPurchases?: number;
    minLoyaltyPoints?: number;
  }) {
    const where: any = {};

    if (filters?.tenantId) {
      where.tenantId = filters.tenantId;
    }

    if (filters?.minPurchases) {
      where.totalPurchases = { gte: filters.minPurchases };
    }

    if (filters?.minLoyaltyPoints) {
      where.loyaltyPoints = { gte: filters.minLoyaltyPoints };
    }

    return this.prisma.buyerProfile.findMany({
      where,
      orderBy: { totalSpent: 'desc' },
    });
  }
}
