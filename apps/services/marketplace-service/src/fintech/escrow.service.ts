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
import { PrismaService } from "../prisma/prisma.service";

@Injectable()
export class EscrowService {
  constructor(private prisma: PrismaService) {}

  /**
   * إنشاء إسكرو جديد للطلب (مع حماية من الصرف المزدوج)
   */
  async createEscrow(
    orderId: string,
    buyerWalletId: string,
    sellerWalletId: string,
    amount: number,
    notes?: string,
    idempotencyKey?: string,
    userId?: string,
    ipAddress?: string,
  ) {
    if (amount <= 0) {
      throw new BadRequestException("المبلغ يجب أن يكون أكبر من صفر");
    }

    if (idempotencyKey) {
      const existingTransaction = await this.prisma.transaction.findUnique({
        where: { idempotencyKey },
      });
      if (existingTransaction) {
        const escrow = await this.prisma.escrow.findUnique({
          where: { orderId },
        });
        return { escrow, duplicate: true, transaction: existingTransaction };
      }
    }

    return await this.prisma.$transaction(
      async (tx) => {
        const existingEscrow = await tx.escrow.findUnique({
          where: { orderId },
        });

        if (existingEscrow) {
          throw new BadRequestException("يوجد إسكرو لهذا الطلب بالفعل");
        }

        const buyerWalletRows = await tx.$queryRaw<any[]>`
          SELECT * FROM wallets WHERE id = ${buyerWalletId}::uuid FOR UPDATE
        `;

        if (!buyerWalletRows || buyerWalletRows.length === 0) {
          throw new NotFoundException("محفظة المشتري غير موجودة");
        }

        const buyerWallet = buyerWalletRows[0];
        const balanceBefore = buyerWallet.balance;
        const escrowBalanceBefore = buyerWallet.escrowBalance || 0;
        const versionBefore = buyerWallet.version;

        if (balanceBefore < amount) {
          throw new BadRequestException(
            `رصيد المشتري غير كافي. الرصيد: ${balanceBefore}, المطلوب: ${amount}`,
          );
        }

        const newBalance = balanceBefore - amount;
        const newEscrowBalance = escrowBalanceBefore + amount;
        const newVersion = versionBefore + 1;

        const sellerWalletExists = await tx.wallet.findUnique({
          where: { id: sellerWalletId },
        });
        if (!sellerWalletExists) {
          throw new NotFoundException("محفظة البائع غير موجودة");
        }

        const escrow = await tx.escrow.create({
          data: {
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
            id: buyerWalletId,
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
    notes?: string,
    idempotencyKey?: string,
    userId?: string,
    ipAddress?: string,
  ) {
    if (idempotencyKey) {
      const existingTransaction = await this.prisma.transaction.findUnique({
        where: { idempotencyKey },
      });
      if (existingTransaction) {
        const escrow = await this.prisma.escrow.findUnique({
          where: { id: escrowId },
          include: {
            buyerWallet: true,
            sellerWallet: true,
          },
        });
        return { escrow, duplicate: true, transaction: existingTransaction };
      }
    }

    return await this.prisma.$transaction(
      async (tx) => {
        const escrow = await tx.escrow.findUnique({
          where: { id: escrowId },
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
            SELECT * FROM wallets WHERE id = ${escrow.buyerWalletId}::uuid FOR UPDATE
          `,
          tx.$queryRaw<any[]>`
            SELECT * FROM wallets WHERE id = ${escrow.sellerWalletId}::uuid FOR UPDATE
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

        const buyerEscrowBefore = buyerWallet.escrowBalance || 0;
        const sellerBalanceBefore = sellerWallet.balance;
        const buyerVersionBefore = buyerWallet.version;
        const sellerVersionBefore = sellerWallet.version;

        if (buyerEscrowBefore < escrow.amount) {
          throw new BadRequestException(
            "رصيد الإسكرو غير كافي - قد يكون تم إطلاقه مسبقاً",
          );
        }

        const now = new Date();
        const buyerEscrowAfter = buyerEscrowBefore - escrow.amount;
        const sellerBalanceAfter = sellerBalanceBefore + escrow.amount;

        const updatedEscrow = await tx.escrow.update({
          where: { id: escrowId },
          data: {
            status: "RELEASED",
            releasedAt: now,
            notes: notes || escrow.notes,
          },
        });

        const updatedBuyerWallet = await tx.wallet.update({
          where: {
            id: escrow.buyerWalletId,
            version: buyerVersionBefore,
          },
          data: {
            escrowBalance: buyerEscrowAfter,
            version: buyerVersionBefore + 1,
          },
        });

        const updatedSellerWallet = await tx.wallet.update({
          where: {
            id: escrow.sellerWalletId,
            version: sellerVersionBefore,
          },
          data: {
            balance: sellerBalanceAfter,
            version: sellerVersionBefore + 1,
          },
        });

        const buyerTx = await tx.transaction.create({
          data: {
            walletId: escrow.buyerWalletId,
            type: "ESCROW_RELEASE",
            amount: 0,
            balanceAfter: buyerWallet.balance,
            balanceBefore: buyerWallet.balance,
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
            walletId: escrow.sellerWalletId,
            type: "MARKETPLACE_SALE",
            amount: escrow.amount,
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
              walletId: escrow.buyerWalletId,
              transactionId: buyerTx.id,
              userId,
              operation: "ESCROW_RELEASE_BUYER",
              balanceBefore: buyerWallet.balance,
              balanceAfter: buyerWallet.balance,
              amount: 0,
              escrowBalanceBefore: buyerEscrowBefore,
              escrowBalanceAfter: buyerEscrowAfter,
              versionBefore: buyerVersionBefore,
              versionAfter: buyerVersionBefore + 1,
              ipAddress,
              metadata: {
                escrowId,
                orderId: escrow.orderId,
                releasedAmount: escrow.amount,
              },
            },
          }),
          tx.walletAuditLog.create({
            data: {
              walletId: escrow.sellerWalletId,
              transactionId: sellerTx.id,
              userId,
              operation: "ESCROW_RELEASE_SELLER",
              balanceBefore: sellerBalanceBefore,
              balanceAfter: sellerBalanceAfter,
              amount: escrow.amount,
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
            walletId: escrow.sellerWalletId,
            eventType: "ORDER_COMPLETED",
            amount: escrow.amount,
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
    reason?: string,
    idempotencyKey?: string,
    userId?: string,
    ipAddress?: string,
  ) {
    if (idempotencyKey) {
      const existingTransaction = await this.prisma.transaction.findUnique({
        where: { idempotencyKey },
      });
      if (existingTransaction) {
        const escrow = await this.prisma.escrow.findUnique({
          where: { id: escrowId },
          include: { buyerWallet: true },
        });
        return { escrow, duplicate: true, transaction: existingTransaction };
      }
    }

    return await this.prisma.$transaction(
      async (tx) => {
        const escrow = await tx.escrow.findUnique({
          where: { id: escrowId },
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
          SELECT * FROM wallets WHERE id = ${escrow.buyerWalletId}::uuid FOR UPDATE
        `;

        if (!buyerWalletRows || buyerWalletRows.length === 0) {
          throw new NotFoundException("محفظة المشتري غير موجودة");
        }

        const buyerWallet = buyerWalletRows[0];
        const balanceBefore = buyerWallet.balance;
        const escrowBalanceBefore = buyerWallet.escrowBalance || 0;
        const versionBefore = buyerWallet.version;

        if (escrowBalanceBefore < escrow.amount) {
          throw new BadRequestException(
            "رصيد الإسكرو غير كافي - قد يكون تم استرداده مسبقاً",
          );
        }

        const now = new Date();
        const newBalance = balanceBefore + escrow.amount;
        const newEscrowBalance = escrowBalanceBefore - escrow.amount;
        const newVersion = versionBefore + 1;

        const updatedEscrow = await tx.escrow.update({
          where: { id: escrowId },
          data: {
            status: "REFUNDED",
            refundedAt: now,
            disputeReason: reason,
          },
        });

        const updatedBuyerWallet = await tx.wallet.update({
          where: {
            id: escrow.buyerWalletId,
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
            walletId: escrow.buyerWalletId,
            type: "ESCROW_REFUND",
            amount: escrow.amount,
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
            walletId: escrow.buyerWalletId,
            transactionId: transaction.id,
            userId,
            operation: "ESCROW_REFUND",
            balanceBefore,
            balanceAfter: newBalance,
            amount: escrow.amount,
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
            walletId: escrow.sellerWalletId,
            eventType: "ORDER_CANCELLED",
            amount: escrow.amount,
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
   * الحصول على إسكرو بالطلب
   */
  async getEscrowByOrder(orderId: string) {
    return this.prisma.escrow.findUnique({
      where: { orderId },
      include: {
        buyerWallet: true,
        sellerWallet: true,
      },
    });
  }

  /**
   * الحصول على جميع إسكرو المحفظة
   */
  async getWalletEscrows(walletId: string) {
    const [asBuyer, asSeller] = await Promise.all([
      this.prisma.escrow.findMany({
        where: { buyerWalletId: walletId },
        orderBy: { createdAt: "desc" },
      }),
      this.prisma.escrow.findMany({
        where: { sellerWalletId: walletId },
        orderBy: { createdAt: "desc" },
      }),
    ]);

    return { asBuyer, asSeller };
  }
}
