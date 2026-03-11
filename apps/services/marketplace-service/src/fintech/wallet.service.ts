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

import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { Prisma } from "../prisma/generated/client";
import { PrismaService } from "../prisma/prisma.service";
import * as crypto from "crypto";

/** Safely convert a Prisma.Decimal (or number) to a plain number for arithmetic. */
function toNum(v: Prisma.Decimal | number | null | undefined): number {
  if (v == null) return 0;
  return typeof v === "number" ? v : Number(v);
}

@Injectable()
export class WalletService {
  constructor(private prisma: PrismaService) {}

  /**
   * الحصول على محفظة المستخدم (إنشاء إذا لم توجد)
   */
  async getWallet(userId: string, userType: string = "farmer") {
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
          creditTier: "BRONZE",
        },
      });
    }

    return {
      ...wallet,
      creditTierAr: this.getCreditTierAr(wallet.creditTier),
      availableCredit: toNum(wallet.loanLimit) - toNum(wallet.currentLoan),
    };
  }

  /**
   * الحصول على ترجمة التصنيف الائتماني
   */
  getCreditTierAr(tier: string): string {
    const tiers: Record<string, string> = {
      BRONZE: "برونزي",
      SILVER: "فضي",
      GOLD: "ذهبي",
      PLATINUM: "بلاتيني",
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
      throw new BadRequestException("المبلغ يجب أن يكون أكبر من صفر");
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
        if (!wallet) {
          throw new NotFoundException("المحفظة غير موجودة");
        }
        return { wallet, transaction: existingTransaction, duplicate: true };
      }
    }

    // Use SERIALIZABLE isolation level for critical financial transactions
    return await this.prisma.$transaction(
      async (tx) => {
        // Lock wallet row then fetch with Prisma for proper field names
        await tx.$executeRaw`SELECT 1 FROM wallets WHERE id = ${walletId}::uuid FOR UPDATE`;
        const currentWallet = await tx.wallet.findUnique({ where: { id: walletId } });

        if (!currentWallet) {
          throw new NotFoundException("المحفظة غير موجودة");
        }

        if (currentWallet.deletedAt) {
          throw new BadRequestException("المحفظة مجمدة أو محذوفة. يرجى التواصل مع الدعم");
        }

        const balanceBefore = toNum(currentWallet.balance);
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
            type: "DEPOSIT",
            amount,
            balanceAfter: newBalance,
            balanceBefore,
            description: description || "Deposit",
            descriptionAr: description || "إيداع في المحفظة",
            status: "COMPLETED",
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
            operation: "DEPOSIT",
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
        isolationLevel: "Serializable",
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
    pin?: string,
  ) {
    if (amount <= 0) {
      throw new BadRequestException("المبلغ يجب أن يكون أكبر من صفر");
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
        if (!wallet) {
          throw new NotFoundException("المحفظة غير موجودة");
        }
        return { wallet, transaction: existingTransaction, duplicate: true };
      }
    }

    // Pre-check: PIN enforcement for large amounts
    await this.enforcePinForAmount(walletId, amount, pin);

    // Use SERIALIZABLE isolation level to prevent race conditions
    return await this.prisma.$transaction(
      async (tx) => {
        // CRITICAL: Lock wallet row then fetch with Prisma for proper field names
        await tx.$executeRaw`SELECT 1 FROM wallets WHERE id = ${walletId}::uuid FOR UPDATE`;
        const wallet = await tx.wallet.findUnique({ where: { id: walletId } });

        if (!wallet) {
          throw new NotFoundException("المحفظة غير موجودة");
        }

        // Check wallet is not frozen
        this.assertWalletActive(wallet);

        const balanceBefore = toNum(wallet.balance);
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
            type: "WITHDRAWAL",
            amount: -amount,
            balanceAfter: newBalance,
            balanceBefore,
            description: description || "Withdrawal",
            descriptionAr: description || "سحب من المحفظة",
            status: "COMPLETED",
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
            operation: "WITHDRAWAL",
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
        isolationLevel: "Serializable",
        maxWait: 5000,
        timeout: 10000,
      },
    );
  }

  /**
   * Check withdraw limits (transaction-safe version)
   */
  private async checkWithdrawLimitsInTransaction(wallet: any, amount: number) {
    const singleLimit = toNum(wallet.singleTransactionLimit);
    if (amount > singleLimit) {
      throw new BadRequestException(
        `المبلغ يتجاوز حد المعاملة الواحدة (${singleLimit} ر.ي)`,
      );
    }

    const now = new Date();
    const lastReset = wallet.lastWithdrawReset
      ? new Date(wallet.lastWithdrawReset)
      : null;
    const needsReset = !lastReset || this.isNewDay(lastReset, now);

    const currentDailyWithdrawn = needsReset ? 0 : toNum(wallet.dailyWithdrawnToday);
    const newDailyTotal = currentDailyWithdrawn + amount;
    const dailyLimit = toNum(wallet.dailyWithdrawLimit);

    if (newDailyTotal > dailyLimit) {
      throw new BadRequestException(
        `تجاوزت حد السحب اليومي (${dailyLimit} ر.ي). المتبقي: ${dailyLimit - currentDailyWithdrawn} ر.ي`,
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
      dailyWithdrawnToday: needsReset
        ? amount
        : toNum(wallet.dailyWithdrawnToday) + amount,
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
      orderBy: { createdAt: "desc" },
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
      throw new NotFoundException("المحفظة غير موجودة");
    }

    const now = new Date();
    const lastReset = wallet.lastWithdrawReset
      ? new Date(wallet.lastWithdrawReset)
      : null;
    const needsReset = !lastReset || this.isNewDay(lastReset, now);
    const currentDailyWithdrawn = needsReset ? 0 : toNum(wallet.dailyWithdrawnToday);
    const dailyLimit = toNum(wallet.dailyWithdrawLimit);

    return {
      dailyWithdrawLimit: dailyLimit,
      dailyRemaining: dailyLimit - currentDailyWithdrawn,
      singleTransactionLimit: toNum(wallet.singleTransactionLimit),
      requiresPinForAmount: toNum(wallet.requiresPinForAmount),
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
      throw new NotFoundException("المحفظة غير موجودة");
    }

    let dailyLimit: number;
    let singleLimit: number;
    let pinAmount: number;

    switch (wallet.creditTier) {
      case "PLATINUM":
        dailyLimit = 100000;
        singleLimit = 500000;
        pinAmount = 50000;
        break;
      case "GOLD":
        dailyLimit = 50000;
        singleLimit = 200000;
        pinAmount = 20000;
        break;
      case "SILVER":
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

  // ═══════════════════════════════════════════════════════════════════════════
  // إدارة رمز PIN - PIN Management
  // ═══════════════════════════════════════════════════════════════════════════

  private readonly PIN_SALT_LENGTH = 16;
  private readonly PIN_KEY_LENGTH = 32;
  private readonly PIN_SCRYPT_COST = 16384;
  private readonly MAX_PIN_ATTEMPTS = 5;
  private readonly PIN_LOCKOUT_WINDOW_MS = 30 * 60 * 1000; // 30 دقيقة
  private readonly KYC_REQUIRED_AMOUNT = 50000;

  /**
   * تشفير رمز PIN باستخدام scrypt
   */
  private hashPin(pin: string): string {
    const salt = crypto.randomBytes(this.PIN_SALT_LENGTH);
    const derived = crypto.scryptSync(pin, salt, this.PIN_KEY_LENGTH, {
      N: this.PIN_SCRYPT_COST,
    });
    return `${salt.toString("hex")}:${derived.toString("hex")}`;
  }

  /**
   * التحقق من رمز PIN
   */
  private verifyPinHash(pin: string, storedHash: string): boolean {
    const [saltHex, hashHex] = storedHash.split(":");
    if (!saltHex || !hashHex) return false;
    const salt = Buffer.from(saltHex, "hex");
    const derived = crypto.scryptSync(pin, salt, this.PIN_KEY_LENGTH, {
      N: this.PIN_SCRYPT_COST,
    });
    return crypto.timingSafeEqual(derived, Buffer.from(hashHex, "hex"));
  }

  /**
   * تعيين رمز PIN للمحفظة
   */
  async setPin(walletId: string, pin: string, userId?: string) {
    if (!/^\d{4,6}$/.test(pin)) {
      throw new BadRequestException(
        "رمز PIN يجب أن يكون 4-6 أرقام",
      );
    }

    const wallet = await this.prisma.wallet.findUnique({
      where: { id: walletId },
    });

    if (!wallet) {
      throw new NotFoundException("المحفظة غير موجودة");
    }

    if (wallet.pin) {
      throw new BadRequestException(
        "رمز PIN موجود بالفعل. استخدم تغيير رمز PIN",
      );
    }

    const hashedPin = this.hashPin(pin);

    await this.prisma.wallet.update({
      where: { id: walletId },
      data: { pin: hashedPin },
    });

    await this.prisma.walletAuditLog.create({
      data: {
        walletId,
        userId,
        operation: "PIN_SET",
        balanceBefore: wallet.balance,
        balanceAfter: wallet.balance,
        amount: 0,
        versionBefore: wallet.version,
        versionAfter: wallet.version,
      },
    });

    return {
      success: true,
      message: "تم تعيين رمز PIN بنجاح",
    };
  }

  /**
   * التحقق من رمز PIN
   */
  async verifyPin(walletId: string, pin: string): Promise<boolean> {
    const wallet = await this.prisma.wallet.findUnique({
      where: { id: walletId },
    });

    if (!wallet) {
      throw new NotFoundException("المحفظة غير موجودة");
    }

    if (!wallet.pin) {
      throw new BadRequestException("لم يتم تعيين رمز PIN بعد");
    }

    return this.verifyPinHash(pin, wallet.pin);
  }

  /**
   * تغيير رمز PIN
   */
  async changePin(
    walletId: string,
    oldPin: string,
    newPin: string,
    userId?: string,
  ) {
    if (!/^\d{4,6}$/.test(newPin)) {
      throw new BadRequestException(
        "رمز PIN الجديد يجب أن يكون 4-6 أرقام",
      );
    }

    const wallet = await this.prisma.wallet.findUnique({
      where: { id: walletId },
    });

    if (!wallet) {
      throw new NotFoundException("المحفظة غير موجودة");
    }

    if (!wallet.pin) {
      throw new BadRequestException("لم يتم تعيين رمز PIN بعد");
    }

    if (!this.verifyPinHash(oldPin, wallet.pin)) {
      throw new BadRequestException("رمز PIN الحالي غير صحيح");
    }

    const hashedPin = this.hashPin(newPin);

    await this.prisma.wallet.update({
      where: { id: walletId },
      data: { pin: hashedPin },
    });

    await this.prisma.walletAuditLog.create({
      data: {
        walletId,
        userId,
        operation: "PIN_CHANGED",
        balanceBefore: wallet.balance,
        balanceAfter: wallet.balance,
        amount: 0,
        versionBefore: wallet.version,
        versionAfter: wallet.version,
      },
    });

    return {
      success: true,
      message: "تم تغيير رمز PIN بنجاح",
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // أمان المحفظة - Wallet Security
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * التحقق من أن المحفظة نشطة وغير مجمدة
   */
  private assertWalletActive(wallet: any): void {
    if (wallet.deletedAt) {
      throw new BadRequestException(
        "المحفظة مجمدة أو محذوفة. يرجى التواصل مع الدعم",
      );
    }
  }

  /**
   * فرض رمز PIN للمبالغ الكبيرة مع حماية KYC
   */
  private async enforcePinForAmount(
    walletId: string,
    amount: number,
    pin?: string,
  ): Promise<void> {
    const wallet = await this.prisma.wallet.findUnique({
      where: { id: walletId },
      select: {
        requiresPinForAmount: true,
        pin: true,
        isVerified: true,
        kycStatus: true,
      },
    });

    if (!wallet) {
      throw new NotFoundException("المحفظة غير موجودة");
    }

    // Enforce KYC for large amounts
    if (amount >= this.KYC_REQUIRED_AMOUNT) {
      if (!wallet.isVerified || wallet.kycStatus !== "approved") {
        throw new BadRequestException(
          `المعاملات التي تزيد عن ${this.KYC_REQUIRED_AMOUNT} ر.ي تتطلب التحقق من الهوية (KYC)`,
        );
      }
    }

    // Check if PIN is required for this amount
    if (amount >= toNum(wallet.requiresPinForAmount)) {
      if (!wallet.pin) {
        throw new BadRequestException(
          "يجب تعيين رمز PIN قبل إجراء معاملات كبيرة. استخدم set-pin أولاً",
        );
      }

      await this.checkPinLockout(walletId);

      if (!pin) {
        throw new BadRequestException(
          `المبلغ يتطلب رمز PIN (للمبالغ أكبر من ${wallet.requiresPinForAmount} ر.ي)`,
        );
      }

      const valid = this.verifyPinHash(pin, wallet.pin);
      await this.recordPinAttempt(walletId, valid);

      if (!valid) {
        throw new BadRequestException("رمز PIN غير صحيح");
      }
    }
  }

  /**
   * التحقق من قفل PIN بسبب محاولات فاشلة متكررة
   */
  private async checkPinLockout(walletId: string): Promise<void> {
    const windowStart = new Date(Date.now() - this.PIN_LOCKOUT_WINDOW_MS);

    const recentFailures = await this.prisma.walletAuditLog.count({
      where: {
        walletId,
        operation: "PIN_FAILED",
        createdAt: { gte: windowStart },
      },
    });

    if (recentFailures >= this.MAX_PIN_ATTEMPTS) {
      throw new BadRequestException(
        `تم قفل المحفظة بسبب ${this.MAX_PIN_ATTEMPTS} محاولات PIN فاشلة. حاول مرة أخرى بعد 30 دقيقة`,
      );
    }
  }

  /**
   * تسجيل محاولة PIN فاشلة في سجل التدقيق
   */
  private async recordPinAttempt(
    walletId: string,
    success: boolean,
  ): Promise<void> {
    if (!success) {
      const wallet = await this.prisma.wallet.findUnique({
        where: { id: walletId },
        select: { balance: true, version: true },
      });

      await this.prisma.walletAuditLog.create({
        data: {
          walletId,
          operation: "PIN_FAILED",
          balanceBefore: wallet?.balance ?? 0,
          balanceAfter: wallet?.balance ?? 0,
          amount: 0,
          versionBefore: wallet?.version ?? 0,
          versionAfter: wallet?.version ?? 0,
        },
      });
    }
  }

  /**
   * الحصول على إحصائيات لوحة تحكم المحفظة
   */
  async getWalletDashboard(walletId: string) {
    const wallet = await this.prisma.wallet.findUnique({
      where: { id: walletId },
    });

    if (!wallet) {
      throw new NotFoundException("المحفظة غير موجودة");
    }

    const [buyerEscrows, sellerEscrows] = await Promise.all([
      this.prisma.escrow.findMany({
        where: {
          buyerWalletId: walletId,
          status: "HELD",
        },
        take: 100,
      }),
      this.prisma.escrow.findMany({
        where: {
          sellerWalletId: walletId,
          status: "HELD",
        },
        take: 100,
      }),
    ]);

    const escrowAsBuyer = buyerEscrows.reduce((sum: number, e: any) => sum + toNum(e.amount), 0);
    const escrowAsSeller = sellerEscrows.reduce((sum: number, e: any) => sum + toNum(e.amount), 0);

    const pendingPayments = await this.prisma.scheduledPayment.findMany({
      where: {
        walletId,
        isActive: true,
        nextPaymentDate: {
          lte: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
        },
      },
    });

    const totalPendingPayments = pendingPayments.reduce(
      (sum: number, p: any) => sum + toNum(p.amount),
      0,
    );

    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
    const transactions = await this.prisma.transaction.findMany({
      where: {
        walletId,
        createdAt: { gte: thirtyDaysAgo },
      },
      orderBy: { createdAt: "asc" },
      take: 1000,
    });

    const dailyStats: Record<
      string,
      { date: string; income: number; expense: number }
    > = {};

    transactions.forEach((tx: any) => {
      const dateKey = tx.createdAt.toISOString().split("T")[0];
      if (!dailyStats[dateKey]) {
        dailyStats[dateKey] = { date: dateKey, income: 0, expense: 0 };
      }

      const txAmount = toNum(tx.amount);
      if (txAmount > 0) {
        dailyStats[dateKey].income += txAmount;
      } else {
        dailyStats[dateKey].expense += Math.abs(txAmount);
      }
    });

    const monthlyChart = Object.values(dailyStats);

    const now = new Date();
    const lastReset = wallet.lastWithdrawReset
      ? new Date(wallet.lastWithdrawReset)
      : null;
    const needsReset = !lastReset || this.isNewDay(lastReset, now);
    const currentDailyWithdrawn = needsReset ? 0 : toNum(wallet.dailyWithdrawnToday);
    const walletBalance = toNum(wallet.balance);
    const walletEscrow = toNum(wallet.escrowBalance);
    const walletLoanLimit = toNum(wallet.loanLimit);
    const walletCurrentLoan = toNum(wallet.currentLoan);
    const walletDailyLimit = toNum(wallet.dailyWithdrawLimit);

    return {
      wallet: {
        id: wallet.id,
        balance: walletBalance,
        escrowBalance: walletEscrow,
        creditScore: wallet.creditScore,
        creditTier: wallet.creditTier,
        creditTierAr: this.getCreditTierAr(wallet.creditTier),
      },
      summary: {
        totalBalance: walletBalance,
        inEscrowAsBuyer: escrowAsBuyer,
        inEscrowAsSeller: escrowAsSeller,
        pendingPaymentsAmount: totalPendingPayments,
        pendingPaymentsCount: pendingPayments.length,
        availableCredit: walletLoanLimit - walletCurrentLoan,
        currentLoan: walletCurrentLoan,
      },
      limits: {
        dailyWithdrawLimit: walletDailyLimit,
        dailyRemaining: walletDailyLimit - currentDailyWithdrawn,
        singleTransactionLimit: toNum(wallet.singleTransactionLimit),
      },
      monthlyChart,
      recentTransactions: transactions.slice(-10),
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // التحويلات - Wallet-to-Wallet Transfers
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * تحويل بين المحافظ مع حماية كاملة من الصرف المزدوج
   * Atomic wallet-to-wallet transfer with deadlock prevention
   */
  async transfer(
    fromWalletId: string,
    toWalletId: string,
    amount: number,
    description?: string,
    idempotencyKey?: string,
    userId?: string,
    ipAddress?: string,
    pin?: string,
  ) {
    if (amount <= 0) {
      throw new BadRequestException("المبلغ يجب أن يكون أكبر من صفر");
    }

    if (fromWalletId === toWalletId) {
      throw new BadRequestException("لا يمكن التحويل إلى نفس المحفظة");
    }

    // Check idempotency
    if (idempotencyKey) {
      const existing = await this.prisma.transaction.findUnique({
        where: { idempotencyKey },
      });
      if (existing) {
        return { transaction: existing, duplicate: true };
      }
    }

    // PIN + KYC enforcement on sender
    await this.enforcePinForAmount(fromWalletId, amount, pin);

    return await this.prisma.$transaction(
      async (tx) => {
        // Lock both wallets ordered by ID to prevent deadlocks
        const [firstId, secondId] =
          fromWalletId < toWalletId
            ? [fromWalletId, toWalletId]
            : [toWalletId, fromWalletId];

        await tx.$executeRaw`SELECT 1 FROM wallets WHERE id = ${firstId}::uuid FOR UPDATE`;
        await tx.$executeRaw`SELECT 1 FROM wallets WHERE id = ${secondId}::uuid FOR UPDATE`;

        const fromWallet = await tx.wallet.findUnique({ where: { id: fromWalletId } });
        const toWallet = await tx.wallet.findUnique({ where: { id: toWalletId } });

        if (!fromWallet || !toWallet) {
          throw new NotFoundException("إحدى المحفظتين غير موجودة");
        }

        this.assertWalletActive(fromWallet);
        this.assertWalletActive(toWallet);

        const fromBalance = toNum(fromWallet.balance);
        if (fromBalance < amount) {
          throw new BadRequestException(
            `الرصيد غير كافي. الرصيد الحالي: ${fromBalance}`,
          );
        }

        await this.checkWithdrawLimitsInTransaction(fromWallet, amount);

        const fromNewBalance = fromBalance - amount;
        const toNewBalance = toNum(toWallet.balance) + amount;
        const fromNewVersion = fromWallet.version + 1;
        const toNewVersion = toWallet.version + 1;
        const dailyWithdrawn = this.updateDailyWithdrawn(fromWallet, amount);

        // Update sender
        await tx.wallet.update({
          where: { id: fromWalletId, version: fromWallet.version },
          data: {
            balance: fromNewBalance,
            version: fromNewVersion,
            dailyWithdrawnToday: dailyWithdrawn.dailyWithdrawnToday,
            lastWithdrawReset: dailyWithdrawn.lastWithdrawReset,
          },
        });

        // Update receiver
        await tx.wallet.update({
          where: { id: toWalletId, version: toWallet.version },
          data: {
            balance: toNewBalance,
            version: toNewVersion,
          },
        });

        // Create outbound transaction
        const outTransaction = await tx.transaction.create({
          data: {
            walletId: fromWalletId,
            type: "TRANSFER_OUT",
            amount: -amount,
            balanceAfter: fromNewBalance,
            balanceBefore: fromBalance,
            description: description || "Transfer to wallet",
            descriptionAr: description || "تحويل إلى محفظة أخرى",
            status: "COMPLETED",
            idempotencyKey,
            userId,
            ipAddress,
          },
        });

        // Create inbound transaction
        await tx.transaction.create({
          data: {
            walletId: toWalletId,
            type: "TRANSFER_IN",
            amount,
            balanceAfter: toNewBalance,
            balanceBefore: toWallet.balance,
            description: description || "Transfer from wallet",
            descriptionAr: description || "تحويل من محفظة أخرى",
            status: "COMPLETED",
            userId,
            ipAddress,
          },
        });

        // Audit logs
        await tx.walletAuditLog.create({
          data: {
            walletId: fromWalletId,
            transactionId: outTransaction.id,
            userId,
            operation: "TRANSFER_OUT",
            balanceBefore: fromWallet.balance,
            balanceAfter: fromNewBalance,
            amount: -amount,
            versionBefore: fromWallet.version,
            versionAfter: fromNewVersion,
            idempotencyKey,
            ipAddress,
            metadata: { toWalletId },
          },
        });

        await tx.walletAuditLog.create({
          data: {
            walletId: toWalletId,
            userId,
            operation: "TRANSFER_IN",
            balanceBefore: toWallet.balance,
            balanceAfter: toNewBalance,
            amount,
            versionBefore: toWallet.version,
            versionAfter: toNewVersion,
            ipAddress,
            metadata: { fromWalletId },
          },
        });

        return { outTransaction, duplicate: false };
      },
      {
        isolationLevel: "Serializable",
        maxWait: 5000,
        timeout: 15000,
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // تجميد المحفظة - Wallet Freeze/Suspend
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * تجميد المحفظة (للإدارة فقط)
   */
  async freezeWallet(walletId: string, userId: string, reason?: string) {
    const wallet = await this.prisma.wallet.findUnique({
      where: { id: walletId },
    });

    if (!wallet) {
      throw new NotFoundException("المحفظة غير موجودة");
    }

    if (wallet.deletedAt) {
      throw new BadRequestException("المحفظة مجمدة بالفعل");
    }

    await this.prisma.wallet.update({
      where: { id: walletId },
      data: {
        deletedAt: new Date(),
        deletedBy: userId,
      },
    });

    await this.prisma.walletAuditLog.create({
      data: {
        walletId,
        userId,
        operation: "WALLET_FROZEN",
        balanceBefore: wallet.balance,
        balanceAfter: wallet.balance,
        amount: 0,
        versionBefore: wallet.version,
        versionAfter: wallet.version,
        metadata: { reason: reason || "Admin action" },
      },
    });

    return {
      success: true,
      message: "تم تجميد المحفظة بنجاح",
      walletId,
    };
  }

  /**
   * إلغاء تجميد المحفظة (للإدارة فقط)
   */
  async unfreezeWallet(walletId: string, userId: string, reason?: string) {
    const wallet = await this.prisma.wallet.findUnique({
      where: { id: walletId },
    });

    if (!wallet) {
      throw new NotFoundException("المحفظة غير موجودة");
    }

    if (!wallet.deletedAt) {
      throw new BadRequestException("المحفظة ليست مجمدة");
    }

    await this.prisma.wallet.update({
      where: { id: walletId },
      data: {
        deletedAt: null,
        deletedBy: null,
      },
    });

    await this.prisma.walletAuditLog.create({
      data: {
        walletId,
        userId,
        operation: "WALLET_UNFROZEN",
        balanceBefore: wallet.balance,
        balanceAfter: wallet.balance,
        amount: 0,
        versionBefore: wallet.version,
        versionAfter: wallet.version,
        metadata: { reason: reason || "Admin action" },
      },
    });

    return {
      success: true,
      message: "تم إلغاء تجميد المحفظة بنجاح",
      walletId,
    };
  }
}
