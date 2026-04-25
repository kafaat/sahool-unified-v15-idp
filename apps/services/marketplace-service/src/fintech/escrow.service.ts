/**
 * SAHOOL Escrow Service
 * خدمة الإسكرو (الضمان)
 *
 * Features:
 * - Escrow creation with double-spend protection
 * - Escrow release to seller upon delivery
 * - Escrow refund to buyer upon cancellation
 * - Dispute handling
 */

import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { Prisma } from "../../prisma/generated/client";
import { PrismaService } from "../prisma/prisma.service";

/** Safely convert a Prisma.Decimal (or number) to a plain number for arithmetic. */
function toNum(v: Prisma.Decimal | number | null | undefined): number {
  if (v == null) return 0;
  return typeof v === "number" ? v : Number(v);
}

@Injectable()
export class EscrowService {
  constructor(private prisma: PrismaService) {}

  /**
   * Guard: every tenant-scoped public method must receive a tenantId.
   */
  private ensureTenantId(tenantId: string): void {
    if (!tenantId) {
      throw new BadRequestException("tenantId required");
    }
  }

  /**
   * إنشاء إسكرو جديد للطلب (مع حماية من الصرف المزدوج)
   */
  async createEscrow(
    orderId: string,
    buyerWalletId: string,
    sellerWalletId: string,
    amount: number,
    notes: string | undefined,
    idempotencyKey: string | undefined,
    userId: string | undefined,
    ipAddress: string | undefined,
    tenantId: string,
  ) {
    this.ensureTenantId(tenantId);

    if (amount <= 0) {
      throw new BadRequestException("المبلغ يجب أن يكون أكبر من صفر");
    }

    if (idempotencyKey) {
      const existingTransaction = await this.prisma.transaction.findUnique({
        where: { idempotencyKey },
      });
      if (existingTransaction) {
        const escrow = await this.prisma.escrow.findFirst({
          where: { orderId, tenantId },
        });
        if (!escrow) {
          throw new NotFoundException("الإسكرو غير موجود للطلب المكرر");
        }
        return { escrow, duplicate: true, transaction: existingTransaction };
      }
    }

    return await this.prisma.$transaction(
      async (tx) => {
        const existingEscrow = await tx.escrow.findFirst({
          where: { orderId, tenantId },
        });

        if (existingEscrow) {
          throw new BadRequestException("يوجد إسكرو لهذا الطلب بالفعل");
        }

        // Tenant-scope buyer wallet: id comes from request payload.
        const buyerWalletTenantCheck = await tx.wallet.findUnique({
          where: { id_tenantId: { id: buyerWalletId, tenantId } },
          select: { id: true },
        });
        if (!buyerWalletTenantCheck) {
          throw new NotFoundException("محفظة المشتري غير موجودة");
        }

        const buyerWalletRows = await tx.$queryRaw<any[]>`
          SELECT * FROM wallets WHERE id = ${buyerWalletId}::uuid AND tenant_id = ${tenantId} FOR UPDATE
        `;

        if (!buyerWalletRows || buyerWalletRows.length === 0) {
          throw new NotFoundException("محفظة المشتري غير موجودة");
        }

        const buyerWallet = buyerWalletRows[0];
        const balanceBefore = toNum(buyerWallet.balance);
        const escrowBalanceBefore = toNum(buyerWallet.escrow_balance ?? buyerWallet.escrowBalance);
        const versionBefore = buyerWallet.version;

        if (balanceBefore < amount) {
          throw new BadRequestException(
            `رصيد المشتري غير كافي. الرصيد: ${balanceBefore}, المطلوب: ${amount}`,
          );
        }

        const newBalance = balanceBefore - amount;
        const newEscrowBalance = escrowBalanceBefore + amount;
        const newVersion = versionBefore + 1;

        // Tenant-scope seller wallet: id comes from request payload.
        const sellerWalletExists = await tx.wallet.findUnique({
          where: { id_tenantId: { id: sellerWalletId, tenantId } },
        });
        if (!sellerWalletExists) {
          throw new NotFoundException("محفظة البائع غير موجودة");
        }

        const escrow = await tx.escrow.create({
          data: {
            tenantId,
            orderId,
            buyerWalletId,
            sellerWalletId,
            amount,
            status: "HELD",
            notes,
          },
        });

        const updatedBuyerWallet = await tx.wallet.update({
          where: {
            id_tenantId: { id: buyerWalletId, tenantId },
            version: versionBefore,
          },
          data: {
            balance: newBalance,
            escrowBalance: newEscrowBalance,
            version: newVersion,
          },
        });

        const transaction = await tx.transaction.create({
          data: {
            tenantId,
            walletId: buyerWalletId,
            type: "ESCROW_HOLD",
            amount: -amount,
            balanceAfter: newBalance,
            balanceBefore,
            referenceId: orderId,
            referenceType: "order",
            description: "Funds held in escrow for order",
            descriptionAr: "مبلغ محجوز في الإسكرو للطلب",
            status: "COMPLETED",
            idempotencyKey,
            userId,
            ipAddress,
          },
        });

        await tx.walletAuditLog.create({
          data: {
            tenantId,
            walletId: buyerWalletId,
            transactionId: transaction.id,
            userId,
            operation: "ESCROW_HOLD",
            balanceBefore,
            balanceAfter: newBalance,
            amount: -amount,
            escrowBalanceBefore,
            escrowBalanceAfter: newEscrowBalance,
            versionBefore,
            versionAfter: newVersion,
            idempotencyKey,
            ipAddress,
            metadata: {
              orderId,
              escrowId: escrow.id,
              sellerWalletId,
            },
          },
        });

        return {
          escrow,
          wallet: updatedBuyerWallet,
          transaction,
          duplicate: false,
        };
      },
      {
        isolationLevel: "Serializable",
        maxWait: 5000,
        timeout: 10000,
      },
    );
  }

  /**
   * إطلاق الإسكرو للبائع (عند التسليم)
   */
  async releaseEscrow(
    escrowId: string,
    notes: string | undefined,
    idempotencyKey: string | undefined,
    userId: string | undefined,
    ipAddress: string | undefined,
    tenantId: string,
  ) {
    this.ensureTenantId(tenantId);

    if (idempotencyKey) {
      const existingTransaction = await this.prisma.transaction.findUnique({
        where: { idempotencyKey },
      });
      if (existingTransaction) {
        const escrow = await this.prisma.escrow.findUnique({
          where: { id_tenantId: { id: escrowId, tenantId } },
          include: {
            buyerWallet: true,
            sellerWallet: true,
          },
        });
        if (!escrow) {
          throw new NotFoundException("الإسكرو غير موجود للمعاملة المكررة");
        }
        return { escrow, duplicate: true, transaction: existingTransaction };
      }
    }

    return await this.prisma.$transaction(
      async (tx) => {
        const escrow = await tx.escrow.findUnique({
          where: { id_tenantId: { id: escrowId, tenantId } },
        });

        if (!escrow) {
          throw new NotFoundException("الإسكرو غير موجود");
        }

        if (escrow.status !== "HELD") {
          throw new BadRequestException(
            `الإسكرو ليس في حالة محجوز. الحالة الحالية: ${escrow.status}`,
          );
        }

        const [buyerWalletRows, sellerWalletRows] = await Promise.all([
          tx.$queryRaw<any[]>`
            SELECT * FROM wallets WHERE id = ${escrow.buyerWalletId}::uuid AND tenant_id = ${tenantId} FOR UPDATE
          `,
          tx.$queryRaw<any[]>`
            SELECT * FROM wallets WHERE id = ${escrow.sellerWalletId}::uuid AND tenant_id = ${tenantId} FOR UPDATE
          `,
        ]);

        if (!buyerWalletRows || buyerWalletRows.length === 0) {
          throw new NotFoundException("محفظة المشتري غير موجودة");
        }

        if (!sellerWalletRows || sellerWalletRows.length === 0) {
          throw new NotFoundException("محفظة البائع غير موجودة");
        }

        const buyerWallet = buyerWalletRows[0];
        const sellerWallet = sellerWalletRows[0];

        const buyerEscrowBefore = toNum(buyerWallet.escrow_balance ?? buyerWallet.escrowBalance);
        const sellerBalanceBefore = toNum(sellerWallet.balance);
        const buyerVersionBefore = buyerWallet.version;
        const sellerVersionBefore = sellerWallet.version;

        const escrowAmount = toNum(escrow.amount);
        if (buyerEscrowBefore < escrowAmount) {
          throw new BadRequestException(
            "رصيد الإسكرو غير كافي - قد يكون تم إطلاقه مسبقاً",
          );
        }

        const now = new Date();
        const buyerEscrowAfter = buyerEscrowBefore - escrowAmount;
        const sellerBalanceAfter = sellerBalanceBefore + escrowAmount;

        const updatedEscrow = await tx.escrow.update({
          where: { id_tenantId: { id: escrowId, tenantId } },
          data: {
            status: "RELEASED",
            releasedAt: now,
            notes: notes || escrow.notes,
          },
        });

        const updatedBuyerWallet = await tx.wallet.update({
          where: {
            id_tenantId: { id: escrow.buyerWalletId, tenantId },
            version: buyerVersionBefore,
          },
          data: {
            escrowBalance: buyerEscrowAfter,
            version: buyerVersionBefore + 1,
          },
        });

        const updatedSellerWallet = await tx.wallet.update({
          where: {
            id_tenantId: { id: escrow.sellerWalletId, tenantId },
            version: sellerVersionBefore,
          },
          data: {
            balance: sellerBalanceAfter,
            version: sellerVersionBefore + 1,
          },
        });

        const buyerBalanceNum = toNum(buyerWallet.balance);
        const buyerTx = await tx.transaction.create({
          data: {
            tenantId,
            walletId: escrow.buyerWalletId,
            type: "ESCROW_RELEASE",
            amount: 0,
            balanceAfter: buyerBalanceNum,
            balanceBefore: buyerBalanceNum,
            referenceId: escrow.orderId,
            referenceType: "order",
            description: "Escrow released to seller",
            descriptionAr: "تم إطلاق الإسكرو للبائع",
            status: "COMPLETED",
            idempotencyKey: idempotencyKey
              ? `${idempotencyKey}-buyer`
              : undefined,
            userId,
            ipAddress,
          },
        });

        const sellerTx = await tx.transaction.create({
          data: {
            tenantId,
            walletId: escrow.sellerWalletId,
            type: "MARKETPLACE_SALE",
            amount: escrowAmount,
            balanceAfter: sellerBalanceAfter,
            balanceBefore: sellerBalanceBefore,
            referenceId: escrow.orderId,
            referenceType: "order",
            description: "Payment received from escrow",
            descriptionAr: "استلام دفعة من الإسكرو",
            status: "COMPLETED",
            idempotencyKey,
            userId,
            ipAddress,
          },
        });

        await Promise.all([
          tx.walletAuditLog.create({
            data: {
              tenantId,
              walletId: escrow.buyerWalletId,
              transactionId: buyerTx.id,
              userId,
              operation: "ESCROW_RELEASE_BUYER",
              balanceBefore: buyerBalanceNum,
              balanceAfter: buyerBalanceNum,
              amount: 0,
              escrowBalanceBefore: buyerEscrowBefore,
              escrowBalanceAfter: buyerEscrowAfter,
              versionBefore: buyerVersionBefore,
              versionAfter: buyerVersionBefore + 1,
              ipAddress,
              metadata: {
                escrowId,
                orderId: escrow.orderId,
                releasedAmount: escrowAmount,
              },
            },
          }),
          tx.walletAuditLog.create({
            data: {
              tenantId,
              walletId: escrow.sellerWalletId,
              transactionId: sellerTx.id,
              userId,
              operation: "ESCROW_RELEASE_SELLER",
              balanceBefore: sellerBalanceBefore,
              balanceAfter: sellerBalanceAfter,
              amount: escrowAmount,
              versionBefore: sellerVersionBefore,
              versionAfter: sellerVersionBefore + 1,
              ipAddress,
              metadata: {
                escrowId,
                orderId: escrow.orderId,
              },
            },
          }),
        ]);

        await tx.creditEvent.create({
          data: {
            tenantId,
            walletId: escrow.sellerWalletId,
            eventType: "ORDER_COMPLETED",
            amount: escrowAmount,
            impact: 5,
            description: "طلب مكتمل بنجاح في السوق",
            metadata: { orderId: escrow.orderId, escrowId },
          },
        });

        return {
          escrow: updatedEscrow,
          buyerWallet: updatedBuyerWallet,
          sellerWallet: updatedSellerWallet,
          transactions: [buyerTx, sellerTx],
          duplicate: false,
        };
      },
      {
        isolationLevel: "Serializable",
        maxWait: 5000,
        timeout: 10000,
      },
    );
  }

  /**
   * استرداد الإسكرو للمشتري (في حالة الإلغاء)
   */
  async refundEscrow(
    escrowId: string,
    reason: string | undefined,
    idempotencyKey: string | undefined,
    userId: string | undefined,
    ipAddress: string | undefined,
    tenantId: string,
  ) {
    this.ensureTenantId(tenantId);

    if (idempotencyKey) {
      const existingTransaction = await this.prisma.transaction.findUnique({
        where: { idempotencyKey },
      });
      if (existingTransaction) {
        const escrow = await this.prisma.escrow.findUnique({
          where: { id_tenantId: { id: escrowId, tenantId } },
          include: { buyerWallet: true },
        });
        if (!escrow) {
          throw new NotFoundException("الإسكرو غير موجود للمعاملة المكررة");
        }
        return { escrow, duplicate: true, transaction: existingTransaction };
      }
    }

    return await this.prisma.$transaction(
      async (tx) => {
        const escrow = await tx.escrow.findUnique({
          where: { id_tenantId: { id: escrowId, tenantId } },
        });

        if (!escrow) {
          throw new NotFoundException("الإسكرو غير موجود");
        }

        if (escrow.status !== "HELD" && escrow.status !== "DISPUTED") {
          throw new BadRequestException(
            `لا يمكن استرداد هذا الإسكرو. الحالة الحالية: ${escrow.status}`,
          );
        }

        const buyerWalletRows = await tx.$queryRaw<any[]>`
          SELECT * FROM wallets WHERE id = ${escrow.buyerWalletId}::uuid AND tenant_id = ${tenantId} FOR UPDATE
        `;

        if (!buyerWalletRows || buyerWalletRows.length === 0) {
          throw new NotFoundException("محفظة المشتري غير موجودة");
        }

        const buyerWallet = buyerWalletRows[0];
        const balanceBefore = toNum(buyerWallet.balance);
        const escrowBalanceBefore = toNum(buyerWallet.escrow_balance ?? buyerWallet.escrowBalance);
        const versionBefore = buyerWallet.version;
        const refundAmount = toNum(escrow.amount);

        if (escrowBalanceBefore < refundAmount) {
          throw new BadRequestException(
            "رصيد الإسكرو غير كافي - قد يكون تم استرداده مسبقاً",
          );
        }

        const now = new Date();
        const newBalance = balanceBefore + refundAmount;
        const newEscrowBalance = escrowBalanceBefore - refundAmount;
        const newVersion = versionBefore + 1;

        const updatedEscrow = await tx.escrow.update({
          where: { id_tenantId: { id: escrowId, tenantId } },
          data: {
            status: "REFUNDED",
            refundedAt: now,
            disputeReason: reason,
          },
        });

        const updatedBuyerWallet = await tx.wallet.update({
          where: {
            id_tenantId: { id: escrow.buyerWalletId, tenantId },
            version: versionBefore,
          },
          data: {
            balance: newBalance,
            escrowBalance: newEscrowBalance,
            version: newVersion,
          },
        });

        const transaction = await tx.transaction.create({
          data: {
            tenantId,
            walletId: escrow.buyerWalletId,
            type: "ESCROW_REFUND",
            amount: refundAmount,
            balanceAfter: newBalance,
            balanceBefore,
            referenceId: escrow.orderId,
            referenceType: "order",
            description: `Escrow refunded: ${reason || "Order cancelled"}`,
            descriptionAr: `استرداد الإسكرو: ${reason || "تم إلغاء الطلب"}`,
            status: "COMPLETED",
            idempotencyKey,
            userId,
            ipAddress,
          },
        });

        await tx.walletAuditLog.create({
          data: {
            tenantId,
            walletId: escrow.buyerWalletId,
            transactionId: transaction.id,
            userId,
            operation: "ESCROW_REFUND",
            balanceBefore,
            balanceAfter: newBalance,
            amount: refundAmount,
            escrowBalanceBefore,
            escrowBalanceAfter: newEscrowBalance,
            versionBefore,
            versionAfter: newVersion,
            idempotencyKey,
            ipAddress,
            metadata: {
              escrowId,
              orderId: escrow.orderId,
              refundReason: reason,
            },
          },
        });

        await tx.creditEvent.create({
          data: {
            tenantId,
            walletId: escrow.sellerWalletId,
            eventType: "ORDER_CANCELLED",
            amount: refundAmount,
            impact: -5,
            description: "طلب ملغي - تم استرداد المبلغ للمشتري",
            metadata: { orderId: escrow.orderId, escrowId, reason },
          },
        });

        return {
          escrow: updatedEscrow,
          wallet: updatedBuyerWallet,
          transaction,
          duplicate: false,
        };
      },
      {
        isolationLevel: "Serializable",
        maxWait: 5000,
        timeout: 10000,
      },
    );
  }

  /**
   * فتح نزاع على الإسكرو
   * Dispute an escrow - freezes funds and records dispute reason
   */
  async disputeEscrow(
    escrowId: string,
    reason: string,
    userId: string | undefined,
    ipAddress: string | undefined,
    tenantId: string,
  ) {
    this.ensureTenantId(tenantId);

    if (!reason || reason.trim().length < 10) {
      throw new BadRequestException(
        "سبب النزاع يجب أن يكون 10 أحرف على الأقل",
      );
    }

    return await this.prisma.$transaction(
      async (tx) => {
        const escrow = await tx.escrow.findUnique({
          where: { id_tenantId: { id: escrowId, tenantId } },
        });

        if (!escrow) {
          throw new NotFoundException("الإسكرو غير موجود");
        }

        if (escrow.status !== "HELD") {
          throw new BadRequestException(
            `لا يمكن فتح نزاع على هذا الإسكرو. الحالة الحالية: ${escrow.status}`,
          );
        }

        const updatedEscrow = await tx.escrow.update({
          where: { id_tenantId: { id: escrowId, tenantId } },
          data: {
            status: "DISPUTED",
            disputeReason: reason.trim(),
          },
        });

        // Audit log for buyer wallet
        await tx.walletAuditLog.create({
          data: {
            tenantId,
            walletId: escrow.buyerWalletId,
            userId,
            operation: "ESCROW_DISPUTED",
            balanceBefore: 0,
            balanceAfter: 0,
            amount: 0,
            ipAddress,
            metadata: {
              escrowId,
              orderId: escrow.orderId,
              disputeReason: reason.trim(),
              disputedBy: userId,
            },
          },
        });

        return {
          escrow: updatedEscrow,
          message: "تم فتح النزاع بنجاح. سيتم مراجعته من قبل الإدارة.",
        };
      },
      {
        isolationLevel: "Serializable",
        maxWait: 5000,
        timeout: 10000,
      },
    );
  }

  /**
   * حل النزاع (للإدارة فقط)
   * Resolve a dispute - either release to seller or refund to buyer
   */
  async resolveDispute(
    escrowId: string,
    resolution: "release" | "refund",
    adminNotes: string,
    userId: string | undefined,
    ipAddress: string | undefined,
    tenantId: string,
  ) {
    this.ensureTenantId(tenantId);

    const escrow = await this.prisma.escrow.findUnique({
      where: { id_tenantId: { id: escrowId, tenantId } },
    });

    if (!escrow) {
      throw new NotFoundException("الإسكرو غير موجود");
    }

    if (escrow.status !== "DISPUTED") {
      throw new BadRequestException(
        `الإسكرو ليس في حالة نزاع. الحالة الحالية: ${escrow.status}`,
      );
    }

    const notes = `[تم حل النزاع: ${resolution === "release" ? "إطلاق للبائع" : "استرداد للمشتري"}] ${adminNotes}`;

    if (resolution === "release") {
      return this.releaseEscrow(escrowId, notes, undefined, userId, ipAddress, tenantId);
    } else {
      return this.refundEscrow(escrowId, notes, undefined, userId, ipAddress, tenantId);
    }
  }

  /**
   * الحصول على إسكرو بالطلب
   */
  async getEscrowByOrder(orderId: string, tenantId: string) {
    this.ensureTenantId(tenantId);
    // orderId is unique globally but we still tenant-scope to prevent
    // cross-tenant leakage if a tenant uses another tenant's order id.
    return this.prisma.escrow.findFirst({
      where: { orderId, tenantId },
      include: {
        buyerWallet: true,
        sellerWallet: true,
      },
    });
  }

  /**
   * الحصول على جميع إسكرو المحفظة
   */
  async getWalletEscrows(walletId: string, tenantId: string) {
    this.ensureTenantId(tenantId);
    const [asBuyer, asSeller] = await Promise.all([
      this.prisma.escrow.findMany({
        where: { buyerWalletId: walletId, tenantId },
        orderBy: { createdAt: "desc" },
        take: 100,
      }),
      this.prisma.escrow.findMany({
        where: { sellerWalletId: walletId, tenantId },
        orderBy: { createdAt: "desc" },
        take: 100,
      }),
    ]);

    return { asBuyer, asSeller };
  }
}
