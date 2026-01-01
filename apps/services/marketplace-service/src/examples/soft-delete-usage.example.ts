/**
 * Soft Delete Usage Examples
 * أمثلة استخدام الحذف الناعم
 *
 * This file demonstrates how to use the soft delete pattern
 * in the marketplace service.
 */

import { PrismaService } from '../prisma/prisma.service';
import {
  softDelete,
  softDeleteMany,
  restore,
  restoreMany,
  findWithDeleted,
  isDeleted,
  getDeletionMetadata,
} from '@sahool/shared-db';

/**
 * Example Service demonstrating soft delete operations
 */
export class SoftDeleteExamplesService {
  constructor(private readonly prisma: PrismaService) {}

  // ═══════════════════════════════════════════════════════════════════════════
  // Basic Operations - العمليات الأساسية
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Example 1: Soft delete a product
   * مثال 1: حذف ناعم لمنتج
   */
  async softDeleteProduct(productId: string, deletedBy: string) {
    // Method 1: Using helper function
    const product = await softDelete(
      this.prisma.product,
      { id: productId },
      { deletedBy }
    );

    // Method 2: Using Prisma delete (automatically converted to soft delete)
    // This is converted by middleware to an update with deletedAt
    const product2 = await this.prisma.product.delete({
      where: { id: productId },
      // @ts-ignore - deletedBy is not in Prisma types but handled by middleware
      deletedBy,
    });

    return product;
  }

  /**
   * Example 2: Soft delete multiple products
   * مثال 2: حذف ناعم لعدة منتجات
   */
  async softDeleteProductsByCategory(category: string, deletedBy: string) {
    const result = await softDeleteMany(
      this.prisma.product,
      { category },
      { deletedBy }
    );

    console.log(`Deleted ${result.count} products`);
    return result;
  }

  /**
   * Example 3: Find products (automatically excludes deleted ones)
   * مثال 3: البحث عن المنتجات (يستبعد المحذوفة تلقائياً)
   */
  async findActiveProducts() {
    // This automatically excludes soft-deleted products
    const products = await this.prisma.product.findMany({
      where: {
        status: 'AVAILABLE',
      },
    });

    return products;
  }

  /**
   * Example 4: Find products including deleted ones
   * مثال 4: البحث عن المنتجات بما في ذلك المحذوفة
   */
  async findAllProductsIncludingDeleted() {
    // Method 1: Using helper function
    const products = await findWithDeleted(this.prisma.product, {
      where: { status: 'AVAILABLE' },
    });

    // Method 2: Using includeDeleted flag
    const products2 = await this.prisma.product.findMany({
      where: { status: 'AVAILABLE' },
      // @ts-ignore - includeDeleted is handled by middleware
      includeDeleted: true,
    });

    return products;
  }

  /**
   * Example 5: Find only deleted products
   * مثال 5: البحث عن المنتجات المحذوفة فقط
   */
  async findDeletedProducts() {
    const products = await this.prisma.product.findMany({
      where: {
        deletedAt: { not: null },
      },
      // @ts-ignore
      includeDeleted: true,
    });

    return products;
  }

  /**
   * Example 6: Restore a deleted product
   * مثال 6: استعادة منتج محذوف
   */
  async restoreProduct(productId: string) {
    const product = await restore(this.prisma.product, { id: productId });

    console.log(`Product ${productId} restored`);
    return product;
  }

  /**
   * Example 7: Restore multiple products
   * مثال 7: استعادة عدة منتجات
   */
  async restoreProductsByCategory(category: string) {
    const result = await restoreMany(this.prisma.product, { category });

    console.log(`Restored ${result.count} products`);
    return result;
  }

  /**
   * Example 8: Check if a product is deleted
   * مثال 8: التحقق من حذف منتج
   */
  async checkIfProductIsDeleted(productId: string) {
    const product = await this.prisma.product.findUnique({
      where: { id: productId },
      // @ts-ignore
      includeDeleted: true,
    });

    if (!product) {
      return { found: false, deleted: false };
    }

    const deleted = isDeleted(product);
    const metadata = getDeletionMetadata(product);

    return {
      found: true,
      deleted,
      deletionInfo: metadata,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Advanced Examples - أمثلة متقدمة
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Example 9: Soft delete with related records
   * مثال 9: حذف ناعم مع السجلات المرتبطة
   */
  async softDeleteOrderWithItems(orderId: string, deletedBy: string) {
    // Get order with items
    const order = await this.prisma.order.findUnique({
      where: { id: orderId },
      include: { items: true },
    });

    if (!order) {
      throw new Error('Order not found');
    }

    // Soft delete the order
    // Note: OrderItem doesn't have soft delete fields, so it won't be deleted
    // If you want to delete items too, add soft delete fields to OrderItem model
    await softDelete(this.prisma.order, { id: orderId }, { deletedBy });

    return { orderId, deletedItemsCount: order.items.length };
  }

  /**
   * Example 10: Cascade soft delete for wallet and related records
   * مثال 10: حذف ناعم متتالي للمحفظة والسجلات المرتبطة
   */
  async softDeleteWalletAndRelated(walletId: string, deletedBy: string) {
    // Soft delete wallet (loans will remain because we might need them for audit)
    await softDelete(this.prisma.wallet, { id: walletId }, { deletedBy });

    // Optionally soft delete related loans
    await softDeleteMany(
      this.prisma.loan,
      { walletId },
      { deletedBy }
    );

    return { walletId, status: 'deleted' };
  }

  /**
   * Example 11: Query with complex filters and soft delete
   * مثال 11: استعلام مع فلاتر معقدة والحذف الناعم
   */
  async findProductsWithComplexFilters() {
    // This query automatically excludes deleted products
    const products = await this.prisma.product.findMany({
      where: {
        AND: [
          { status: 'AVAILABLE' },
          { stock: { gt: 0 } },
          {
            OR: [
              { category: 'SEEDS' },
              { category: 'FERTILIZER' },
            ],
          },
        ],
        // deletedAt: null is automatically added by middleware
      },
      orderBy: {
        createdAt: 'desc',
      },
      take: 10,
    });

    return products;
  }

  /**
   * Example 12: Count active vs deleted records
   * مثال 12: عد السجلات النشطة مقابل المحذوفة
   */
  async getProductStats() {
    // Count active products (excluding deleted)
    const activeCount = await this.prisma.product.count({
      where: { deletedAt: null },
    });

    // Count deleted products
    const deletedCount = await this.prisma.product.count({
      where: { deletedAt: { not: null } },
      // @ts-ignore
      includeDeleted: true,
    });

    // Total count (including deleted)
    const totalCount = await this.prisma.product.count({
      // @ts-ignore
      includeDeleted: true,
    });

    return {
      active: activeCount,
      deleted: deletedCount,
      total: totalCount,
    };
  }

  /**
   * Example 13: Bulk operations with soft delete
   * مثال 13: عمليات جماعية مع الحذف الناعم
   */
  async bulkDeleteExpiredProducts(deletedBy: string) {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const result = await softDeleteMany(
      this.prisma.product,
      {
        status: 'SOLD_OUT',
        updatedAt: { lt: thirtyDaysAgo },
      },
      { deletedBy }
    );

    return result;
  }

  /**
   * Example 14: Restore with validation
   * مثال 14: استعادة مع التحقق
   */
  async restoreProductWithValidation(productId: string) {
    // First, find the product including deleted ones
    const product = await this.prisma.product.findUnique({
      where: { id: productId },
      // @ts-ignore
      includeDeleted: true,
    });

    if (!product) {
      throw new Error('Product not found');
    }

    if (!isDeleted(product)) {
      throw new Error('Product is not deleted');
    }

    // Check deletion metadata
    const metadata = getDeletionMetadata(product);
    console.log(`Product was deleted by: ${metadata?.deletedBy}`);
    console.log(`Deleted at: ${metadata?.deletedAt}`);

    // Restore the product
    const restored = await restore(this.prisma.product, { id: productId });

    return restored;
  }

  /**
   * Example 15: Get deletion audit trail
   * مثال 15: الحصول على سجل التدقيق للحذف
   */
  async getDeletionAuditTrail(startDate: Date, endDate: Date) {
    // Find all products deleted in the date range
    const deletedProducts = await this.prisma.product.findMany({
      where: {
        deletedAt: {
          gte: startDate,
          lte: endDate,
        },
      },
      // @ts-ignore
      includeDeleted: true,
      select: {
        id: true,
        name: true,
        deletedAt: true,
        deletedBy: true,
        category: true,
      },
    });

    return deletedProducts.map(product => ({
      productId: product.id,
      productName: product.name,
      category: product.category,
      ...getDeletionMetadata(product),
    }));
  }
}
