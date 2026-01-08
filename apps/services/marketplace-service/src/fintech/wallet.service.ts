/**
 * SAHOOL Wallet Service
 * خدمة المحفظة الرقمية
 *
 * Features:
 * - Digital wallet management with double-spend protection
 * - Deposit/Withdraw with idempotency keys
 * - Audit logging for all operations
 * - Daily limits and transaction limits
 */

import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class WalletService {
  constructor(private prisma: PrismaService) {}

  /**
   * الحصول على محفظة المستخدم (إنشاء إذا لم توجد)
   */
  async getWallet(userId: string, userType: string = 'farmer') {
    let wallet = await this.prisma.wallet.findUnique({
      where: { userId },
    });

    if (!wallet) {
      wallet = await this.prisma.wallet.create({
        data: {
          userId,
          userType,
          balance: 0,
          creditScore: 300,
          creditTier: 'BRONZE',
        },
      });
    }

    return {
      ...wallet,
      creditTierAr: this.getCreditTierAr(wallet.creditTier),
      availableCredit: wallet.loanLimit - wallet.currentLoan,
    };
  }

  /**
   * الحصول على ترجمة التصنيف الائتماني
   */
  getCreditTierAr(tier: string): string {
    const tiers: Record<string, string> = {
      BRONZE: 'برونزي',
      SILVER: 'فضي',
      GOLD: 'ذهبي',
      PLATINUM: 'بلاتيني',
    };
    return tiers[tier] || tier;
  }

  /**
   * إيداع مبلغ في المحفظة (مع حماية من التكرار والتدقيق)
   * Deposit to wallet with idempotency protection and audit logging
   */
  async deposit(
    walletId: string,
    amount: number,
    description?: string,
    idempotencyKey?: string,
    userId?: string,
    ipAddress?: string,
  ) {
    if (amount <= 0) {
      throw new BadRequestException('المبلغ يجب أن يكون أكبر من صفر');
    }

    // Check for duplicate transaction using idempotency key
    if (idempotencyKey) {
      const existingTransaction = await this.prisma.transaction.findUnique({
        where: { idempotencyKey },
      });
      if (existingTransaction) {
        const wallet = await this.prisma.wallet.findUnique({
          where: { id: walletId },
        });
        return { wallet, transaction: existingTransaction, duplicate: true };
      }
    }

    // Use SERIALIZABLE isolation level for critical financial transactions
    return await this.prisma.$transaction(
      async (tx) => {
        // Lock wallet row with SELECT FOR UPDATE
        const wallet = await tx.$queryRaw<any[]>`
          SELECT * FROM wallets WHERE id = ${walletId}::uuid FOR UPDATE
        `;

        if (!wallet || wallet.length === 0) {
          throw new NotFoundException('المحفظة غير موجودة');
        }

        const currentWallet = wallet[0];
        const balanceBefore = currentWallet.balance;
        const versionBefore = currentWallet.version;
        const newBalance = balanceBefore + amount;
        const newVersion = versionBefore + 1;

        // Update wallet balance and version atomically
        const updatedWallet = await tx.wallet.update({
          where: {
            id: walletId,
            version: versionBefore,
          },
          data: {
            balance: newBalance,
            version: newVersion,
          },
        });

        // Create transaction record with idempotency key
        const transaction = await tx.transaction.create({
          data: {
            walletId,
            type: 'DEPOSIT',
            amount,
            balanceAfter: newBalance,
            balanceBefore,
            description: description || 'Deposit',
            descriptionAr: description || 'إيداع في المحفظة',
            status: 'COMPLETED',
            idempotencyKey,
            userId,
            ipAddress,
          },
        });

        // Create audit log entry
        await tx.walletAuditLog.create({
          data: {
            walletId,
            transactionId: transaction.id,
            userId,
            operation: 'DEPOSIT',
            balanceBefore,
            balanceAfter: newBalance,
            amount,
            versionBefore,
            versionAfter: newVersion,
            idempotencyKey,
            ipAddress,
          },
        });

        return { wallet: updatedWallet, transaction, duplicate: false };
      },
      {
        isolationLevel: 'Serializable',
        maxWait: 5000,
        timeout: 10000,
      },
    );
  }

  /**
   * سحب مبلغ من المحفظة (مع حماية مزدوجة من الصرف المزدوج)
   * Withdraw from wallet with double-spend protection
   */
  async withdraw(
    walletId: string,
    amount: number,
    description?: string,
    idempotencyKey?: string,
    userId?: string,
    ipAddress?: string,
  ) {
    if (amount <= 0) {
      throw new BadRequestException('المبلغ يجب أن يكون أكبر من صفر');
    }

    // Check for duplicate transaction using idempotency key
    if (idempotencyKey) {
      const existingTransaction = await this.prisma.transaction.findUnique({
        where: { idempotencyKey },
      });
      if (existingTransaction) {
        const wallet = await this.prisma.wallet.findUnique({
          where: { id: walletId },
        });
        return { wallet, transaction: existingTransaction, duplicate: true };
      }
    }

    // Use SERIALIZABLE isolation level to prevent race conditions
    return await this.prisma.$transaction(
      async (tx) => {
        // CRITICAL: Lock wallet row with SELECT FOR UPDATE
        const walletRows = await tx.$queryRaw<any[]>`
          SELECT * FROM wallets WHERE id = ${walletId}::uuid FOR UPDATE
        `;

        if (!walletRows || walletRows.length === 0) {
          throw new NotFoundException('المحفظة غير موجودة');
        }

        const wallet = walletRows[0];
        const balanceBefore = wallet.balance;
        const versionBefore = wallet.version;

        // CRITICAL: Check balance WITHIN the transaction after locking
        if (balanceBefore < amount) {
          throw new BadRequestException(
            `الرصيد غير كافي. الرصيد الحالي: ${balanceBefore}, المبلغ المطلوب: ${amount}`,
          );
        }

        // Check wallet limits
        await this.checkWithdrawLimitsInTransaction(wallet, amount);

        const newBalance = balanceBefore - amount;
        const newVersion = versionBefore + 1;
        const newDailyWithdrawn = this.updateDailyWithdrawn(wallet, amount);

        // Update wallet with optimistic locking check
        const updatedWallet = await tx.wallet.update({
          where: {
            id: walletId,
            version: versionBefore,
          },
          data: {
            balance: newBalance,
            version: newVersion,
            dailyWithdrawnToday: newDailyWithdrawn.dailyWithdrawnToday,
            lastWithdrawReset: newDailyWithdrawn.lastWithdrawReset,
          },
        });

        // Create transaction record with audit trail
        const transaction = await tx.transaction.create({
          data: {
            walletId,
            type: 'WITHDRAWAL',
            amount: -amount,
            balanceAfter: newBalance,
            balanceBefore,
            description: description || 'Withdrawal',
            descriptionAr: description || 'سحب من المحفظة',
            status: 'COMPLETED',
            idempotencyKey,
            userId,
            ipAddress,
          },
        });

        // Create audit log entry
        await tx.walletAuditLog.create({
          data: {
            walletId,
            transactionId: transaction.id,
            userId,
            operation: 'WITHDRAWAL',
            balanceBefore,
            balanceAfter: newBalance,
            amount: -amount,
            versionBefore,
            versionAfter: newVersion,
            idempotencyKey,
            ipAddress,
            metadata: {
              dailyWithdrawnBefore: wallet.dailyWithdrawnToday,
              dailyWithdrawnAfter: newDailyWithdrawn.dailyWithdrawnToday,
            },
          },
        });

        return { wallet: updatedWallet, transaction, duplicate: false };
      },
      {
        isolationLevel: 'Serializable',
        maxWait: 5000,
        timeout: 10000,
      },
    );
  }

  /**
   * Check withdraw limits (transaction-safe version)
   */
  private async checkWithdrawLimitsInTransaction(wallet: any, amount: number) {
    if (amount > wallet.singleTransactionLimit) {
      throw new BadRequestException(
        `المبلغ يتجاوز حد المعاملة الواحدة (${wallet.singleTransactionLimit} ر.ي)`,
      );
    }

    const now = new Date();
    const lastReset = wallet.lastWithdrawReset
      ? new Date(wallet.lastWithdrawReset)
      : null;
    const needsReset = !lastReset || this.isNewDay(lastReset, now);

    const currentDailyWithdrawn = needsReset ? 0 : wallet.dailyWithdrawnToday;
    const newDailyTotal = currentDailyWithdrawn + amount;

    if (newDailyTotal > wallet.dailyWithdrawLimit) {
      throw new BadRequestException(
        `تجاوزت حد السحب اليومي (${wallet.dailyWithdrawLimit} ر.ي). المتبقي: ${wallet.dailyWithdrawLimit - currentDailyWithdrawn} ر.ي`,
      );
    }
  }

  /**
   * تحديث حد السحب اليومي
   */
  private updateDailyWithdrawn(wallet: any, amount: number) {
    const now = new Date();
    const lastReset = wallet.lastWithdrawReset
      ? new Date(wallet.lastWithdrawReset)
      : null;
    const needsReset = !lastReset || this.isNewDay(lastReset, now);

    return {
      dailyWithdrawnToday: needsReset ? amount : wallet.dailyWithdrawnToday + amount,
      lastWithdrawReset: needsReset ? now : wallet.lastWithdrawReset,
    };
  }

  /**
   * التحقق من يوم جديد
   */
  private isNewDay(date1: Date, date2: Date): boolean {
    return (
      date1.getDate() !== date2.getDate() ||
      date1.getMonth() !== date2.getMonth() ||
      date1.getFullYear() !== date2.getFullYear()
    );
  }

  /**
   * الحصول على سجل المعاملات
   */
  async getTransactions(walletId: string, limit: number = 20) {
    return this.prisma.transaction.findMany({
      where: { walletId },
      orderBy: { createdAt: 'desc' },
      take: limit,
    });
  }

  /**
   * الحصول على حدود المحفظة
   */
  async getWalletLimits(walletId: string) {
    const wallet = await this.prisma.wallet.findUnique({
      where: { id: walletId },
    });

    if (!wallet) {
      throw new NotFoundException('المحفظة غير موجودة');
    }

    const now = new Date();
    const lastReset = wallet.lastWithdrawReset
      ? new Date(wallet.lastWithdrawReset)
      : null;
    const needsReset = !lastReset || this.isNewDay(lastReset, now);
    const currentDailyWithdrawn = needsReset ? 0 : wallet.dailyWithdrawnToday;

    return {
      dailyWithdrawLimit: wallet.dailyWithdrawLimit,
      dailyRemaining: wallet.dailyWithdrawLimit - currentDailyWithdrawn,
      singleTransactionLimit: wallet.singleTransactionLimit,
      requiresPinForAmount: wallet.requiresPinForAmount,
      creditTier: wallet.creditTier,
    };
  }

  /**
   * تحديث حدود المحفظة (بناءً على التصنيف الائتماني)
   */
  async updateWalletLimits(walletId: string) {
    const wallet = await this.prisma.wallet.findUnique({
      where: { id: walletId },
    });

    if (!wallet) {
      throw new NotFoundException('المحفظة غير موجودة');
    }

    let dailyLimit: number;
    let singleLimit: number;
    let pinAmount: number;

    switch (wallet.creditTier) {
      case 'PLATINUM':
        dailyLimit = 100000;
        singleLimit = 500000;
        pinAmount = 50000;
        break;
      case 'GOLD':
        dailyLimit = 50000;
        singleLimit = 200000;
        pinAmount = 20000;
        break;
      case 'SILVER':
        dailyLimit = 20000;
        singleLimit = 100000;
        pinAmount = 10000;
        break;
      default:
        dailyLimit = 10000;
        singleLimit = 50000;
        pinAmount = 5000;
    }

    return this.prisma.wallet.update({
      where: { id: walletId },
      data: {
        dailyWithdrawLimit: dailyLimit,
        singleTransactionLimit: singleLimit,
        requiresPinForAmount: pinAmount,
      },
    });
  }

  /**
   * الحصول على إحصائيات لوحة تحكم المحفظة
   */
  async getWalletDashboard(walletId: string) {
    const wallet = await this.prisma.wallet.findUnique({
      where: { id: walletId },
    });

    if (!wallet) {
      throw new NotFoundException('المحفظة غير موجودة');
    }

    const [buyerEscrows, sellerEscrows] = await Promise.all([
      this.prisma.escrow.findMany({
        where: {
          buyerWalletId: walletId,
          status: 'HELD',
        },
      }),
      this.prisma.escrow.findMany({
        where: {
          sellerWalletId: walletId,
          status: 'HELD',
        },
      }),
    ]);

    const escrowAsBuyer = buyerEscrows.reduce((sum, e) => sum + e.amount, 0);
    const escrowAsSeller = sellerEscrows.reduce((sum, e) => sum + e.amount, 0);

    const pendingPayments = await this.prisma.scheduledPayment.findMany({
      where: {
        walletId,
        isActive: true,
        nextPaymentDate: {
          lte: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
        },
      },
    });

    const totalPendingPayments = pendingPayments.reduce((sum, p) => sum + p.amount, 0);

    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
    const transactions = await this.prisma.transaction.findMany({
      where: {
        walletId,
        createdAt: { gte: thirtyDaysAgo },
      },
      orderBy: { createdAt: 'asc' },
    });

    const dailyStats: Record<string, { date: string; income: number; expense: number }> = {};

    transactions.forEach((tx) => {
      const dateKey = tx.createdAt.toISOString().split('T')[0];
      if (!dailyStats[dateKey]) {
        dailyStats[dateKey] = { date: dateKey, income: 0, expense: 0 };
      }

      if (tx.amount > 0) {
        dailyStats[dateKey].income += tx.amount;
      } else {
        dailyStats[dateKey].expense += Math.abs(tx.amount);
      }
    });

    const monthlyChart = Object.values(dailyStats);

    const now = new Date();
    const lastReset = wallet.lastWithdrawReset
      ? new Date(wallet.lastWithdrawReset)
      : null;
    const needsReset = !lastReset || this.isNewDay(lastReset, now);
    const currentDailyWithdrawn = needsReset ? 0 : wallet.dailyWithdrawnToday;

    return {
      wallet: {
        id: wallet.id,
        balance: wallet.balance,
        escrowBalance: wallet.escrowBalance,
        creditScore: wallet.creditScore,
        creditTier: wallet.creditTier,
        creditTierAr: this.getCreditTierAr(wallet.creditTier),
      },
      summary: {
        totalBalance: wallet.balance,
        inEscrowAsBuyer: escrowAsBuyer,
        inEscrowAsSeller: escrowAsSeller,
        pendingPaymentsAmount: totalPendingPayments,
        pendingPaymentsCount: pendingPayments.length,
        availableCredit: wallet.loanLimit - wallet.currentLoan,
        currentLoan: wallet.currentLoan,
      },
      limits: {
        dailyWithdrawLimit: wallet.dailyWithdrawLimit,
        dailyRemaining: wallet.dailyWithdrawLimit - currentDailyWithdrawn,
        singleTransactionLimit: wallet.singleTransactionLimit,
      },
      monthlyChart,
      recentTransactions: transactions.slice(-10),
    };
  }
}
