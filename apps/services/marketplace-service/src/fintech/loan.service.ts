/**
 * SAHOOL Loan Service
 * خدمة القروض الزراعية
 *
 * Features:
 * - Islamic finance compatible agricultural loans
 * - Loan application and approval workflow
 * - Loan repayment with double-spend protection
 * - Scheduled payments management
 */

import {
  Injectable,
  Logger,
  NotFoundException,
  BadRequestException,
  OnModuleInit,
  OnModuleDestroy,
} from "@nestjs/common";
import { Prisma } from "../../prisma/generated/client";
import { PrismaService } from "../prisma/prisma.service";

/** Safely convert a Prisma.Decimal (or number) to a plain number for arithmetic. */
function toNum(v: Prisma.Decimal | number | null | undefined): number {
  if (v == null) return 0;
  return typeof v === "number" ? v : Number(v);
}

interface CreateLoanDto {
  walletId: string;
  amount: number;
  termMonths: number;
  purpose: string;
  purposeDetails?: string;
  collateralType?: string;
  collateralValue?: number;
}

@Injectable()
export class LoanService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(LoanService.name);
  private schedulerInterval: NodeJS.Timeout | null = null;
  private readonly SCHEDULER_INTERVAL_MS = 60 * 60 * 1000; // 1 hour
  private readonly MAX_FAILED_ATTEMPTS = 3;

  constructor(private prisma: PrismaService) {}

  async onModuleInit() {
    this.startPaymentScheduler();
  }

  async onModuleDestroy() {
    this.stopPaymentScheduler();
  }

  /**
   * بدء جدولة الدفعات التلقائية
   */
  private startPaymentScheduler() {
    this.logger.log("Starting scheduled payment processor...");
    this.schedulerInterval = setInterval(() => {
      this.processDuePayments().catch((err) => {
        this.logger.error(`Scheduled payment processing failed: ${err.message}`);
      });
    }, this.SCHEDULER_INTERVAL_MS);

    // Run once on startup after a short delay
    setTimeout(() => {
      this.processDuePayments().catch((err) => {
        this.logger.error(`Initial payment processing failed: ${err.message}`);
      });
    }, 10_000);
  }

  private stopPaymentScheduler() {
    if (this.schedulerInterval) {
      clearInterval(this.schedulerInterval);
      this.schedulerInterval = null;
      this.logger.log("Stopped scheduled payment processor");
    }
  }

  /**
   * معالجة الدفعات المستحقة
   * NOTE: This is a system-level scheduled job (cron) that intentionally
   * processes due payments across all tenants. Tenant isolation is not
   * applied here because the scheduler must handle payments globally.
   */
  async processDuePayments(): Promise<{ processed: number; failed: number }> {
    const now = new Date();

    const duePayments = await this.prisma.scheduledPayment.findMany({
      where: {
        isActive: true,
        nextPaymentDate: { lte: now },
        failedAttempts: { lt: this.MAX_FAILED_ATTEMPTS },
      },
      take: 50, // Process in batches
      orderBy: { nextPaymentDate: "asc" },
    });

    if (duePayments.length === 0) {
      return { processed: 0, failed: 0 };
    }

    this.logger.log(`Processing ${duePayments.length} due scheduled payments`);

    let processed = 0;
    let failed = 0;

    for (const payment of duePayments) {
      try {
        await this.executeScheduledPayment(payment.id);
        processed++;
      } catch (error) {
        failed++;
        this.logger.warn(
          `Failed to execute scheduled payment ${payment.id}: ${error instanceof Error ? error.message : String(error)}`,
        );

        // Auto-deactivate if max attempts exceeded
        const updated = await this.prisma.scheduledPayment.findUnique({
          where: { id: payment.id },
        });
        if (updated && updated.failedAttempts >= this.MAX_FAILED_ATTEMPTS) {
          await this.prisma.scheduledPayment.update({
            where: { id: payment.id },
            data: {
              isActive: false,
              lastFailureReason: `تم تعطيل الدفعة بعد ${this.MAX_FAILED_ATTEMPTS} محاولات فاشلة`,
            },
          });
          this.logger.warn(
            `Deactivated scheduled payment ${payment.id} after ${this.MAX_FAILED_ATTEMPTS} failed attempts`,
          );
        }
      }
    }

    this.logger.log(
      `Scheduled payments processed: ${processed} success, ${failed} failed`,
    );
    return { processed, failed };
  }

  /**
   * ترجمة غرض القرض
   */
  getLoanPurposeAr(purpose: string): string {
    const purposes: Record<string, string> = {
      SEEDS: "شراء بذور",
      FERTILIZER: "شراء أسمدة",
      EQUIPMENT: "شراء معدات",
      IRRIGATION: "نظام ري",
      EXPANSION: "توسيع المزرعة",
      EMERGENCY: "طوارئ",
      OTHER: "أخرى",
    };
    return purposes[purpose] || purpose;
  }

  /**
   * طلب قرض جديد
   */
  async requestLoan(data: CreateLoanDto) {
    const wallet = await this.prisma.wallet.findUnique({
      where: { id: data.walletId },
    });

    if (!wallet) {
      throw new NotFoundException("المحفظة غير موجودة");
    }

    const availableCredit = toNum(wallet.loanLimit) - toNum(wallet.currentLoan);

    if (data.amount > availableCredit) {
      throw new BadRequestException(
        `المبلغ المطلوب يتجاوز الحد الائتماني المتاح (${availableCredit} ر.ي)`,
      );
    }

    // حساب المبلغ الإجمالي (بدون فائدة - تمويل إسلامي)
    const adminFee = data.amount * 0.02; // 2% رسوم إدارية
    const totalDue = data.amount + adminFee;

    const startDate = new Date();
    const dueDate = new Date();
    dueDate.setMonth(dueDate.getMonth() + data.termMonths);

    const loan = await this.prisma.loan.create({
      data: {
        walletId: data.walletId,
        amount: data.amount,
        interestRate: 0,
        totalDue,
        termMonths: data.termMonths,
        startDate,
        dueDate,
        purpose: data.purpose as any,
        purposeDetails: data.purposeDetails,
        collateralType: data.collateralType,
        collateralValue: data.collateralValue,
        status: "PENDING",
      },
    });

    return {
      loan,
      message: "تم تقديم طلب القرض بنجاح. سيتم مراجعته خلال 24-48 ساعة.",
      nextSteps: [
        "سيتم التحقق من بياناتك",
        "قد نطلب مستندات إضافية",
        "سيتم إيداع المبلغ في محفظتك عند الموافقة",
      ],
    };
  }

  /**
   * الموافقة على القرض (للإدارة)
   */
  async approveLoan(loanId: string) {
    const loan = await this.prisma.loan.findUnique({
      where: { id: loanId },
      include: { wallet: true },
    });

    if (!loan) {
      throw new NotFoundException("القرض غير موجود");
    }

    if (loan.status !== "PENDING") {
      throw new BadRequestException("لا يمكن الموافقة على هذا القرض");
    }

    const [updatedLoan, updatedWallet, transaction] =
      await this.prisma.$transaction([
        this.prisma.loan.update({
          where: { id: loanId },
          data: { status: "ACTIVE" },
        }),
        this.prisma.wallet.update({
          where: { id: loan.walletId },
          data: {
            balance: { increment: loan.amount },
            currentLoan: { increment: loan.totalDue },
          },
        }),
        this.prisma.transaction.create({
          data: {
            walletId: loan.walletId,
            type: "LOAN",
            amount: loan.amount,
            balanceAfter: toNum(loan.wallet.balance) + toNum(loan.amount),
            referenceId: loanId,
            referenceType: "loan",
            description: `Agricultural loan - ${loan.purpose}`,
            descriptionAr: `قرض زراعي - ${this.getLoanPurposeAr(loan.purpose)}`,
            status: "COMPLETED",
          },
        }),
      ]);

    return { loan: updatedLoan, wallet: updatedWallet, transaction };
  }

  /**
   * سداد القرض (مع حماية من الصرف المزدوج)
   */
  async repayLoan(
    loanId: string,
    amount: number,
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
        const loan = await this.prisma.loan.findUnique({
          where: { id: loanId },
          include: { wallet: true },
        });
        if (!loan) {
          throw new NotFoundException("القرض غير موجود للمعاملة المكررة");
        }
        return {
          loan,
          wallet: loan.wallet,
          transaction: existingTransaction,
          duplicate: true,
        };
      }
    }

    return await this.prisma.$transaction(
      async (tx) => {
        const loan = await tx.loan.findUnique({
          where: { id: loanId },
          include: { wallet: true },
        });

        if (!loan) {
          throw new NotFoundException("القرض غير موجود");
        }

        if (loan.status !== "ACTIVE") {
          throw new BadRequestException("القرض غير نشط");
        }

        const walletRows = await tx.$queryRaw<any[]>`
          SELECT * FROM wallets WHERE id = ${loan.walletId}::uuid FOR UPDATE
        `;

        if (!walletRows || walletRows.length === 0) {
          throw new NotFoundException("المحفظة غير موجودة");
        }

        const wallet = walletRows[0];
        const balanceBefore = toNum(wallet.balance);
        const versionBefore = wallet.version;

        const loanTotalDue = toNum(loan.totalDue);
        const loanPaidAmount = toNum(loan.paidAmount);
        const remainingDue = loanTotalDue - loanPaidAmount;
        const paymentAmount = Math.min(amount, remainingDue);

        if (balanceBefore < paymentAmount) {
          throw new BadRequestException(
            `الرصيد غير كافي للسداد. الرصيد: ${balanceBefore}, المطلوب: ${paymentAmount}`,
          );
        }

        const newPaidAmount = loanPaidAmount + paymentAmount;
        const isFullyPaid = newPaidAmount >= loanTotalDue;
        const newBalance = balanceBefore - paymentAmount;
        const newVersion = versionBefore + 1;

        const updatedLoan = await tx.loan.update({
          where: { id: loanId },
          data: {
            paidAmount: newPaidAmount,
            status: isFullyPaid ? "PAID" : "ACTIVE",
          },
        });

        const updatedWallet = await tx.wallet.update({
          where: {
            id: loan.walletId,
            version: versionBefore,
          },
          data: {
            balance: newBalance,
            currentLoan: { decrement: paymentAmount },
            version: newVersion,
          },
        });

        const transaction = await tx.transaction.create({
          data: {
            walletId: loan.walletId,
            type: "REPAYMENT",
            amount: -paymentAmount,
            balanceAfter: newBalance,
            balanceBefore,
            referenceId: loanId,
            referenceType: "loan",
            description: `Loan repayment`,
            descriptionAr: isFullyPaid ? "سداد كامل للقرض" : "سداد جزئي للقرض",
            status: "COMPLETED",
            idempotencyKey,
            userId,
            ipAddress,
          },
        });

        await tx.walletAuditLog.create({
          data: {
            walletId: loan.walletId,
            transactionId: transaction.id,
            userId,
            operation: "LOAN_REPAYMENT",
            balanceBefore,
            balanceAfter: newBalance,
            amount: -paymentAmount,
            versionBefore,
            versionAfter: newVersion,
            idempotencyKey,
            ipAddress,
            metadata: {
              loanId,
              paidAmount: paymentAmount,
              totalPaid: newPaidAmount,
              remainingDue: loanTotalDue - newPaidAmount,
              isFullyPaid,
            },
          },
        });

        if (isFullyPaid) {
          const dueDate = new Date(loan.dueDate);
          const isOnTime = new Date() <= dueDate;

          await tx.creditEvent.create({
            data: {
              walletId: loan.walletId,
              eventType: isOnTime ? "LOAN_REPAID_ONTIME" : "LOAN_REPAID_LATE",
              amount: loanTotalDue,
              impact: isOnTime ? 15 : -10,
              description: isOnTime
                ? "قرض مسدد في الوقت المحدد"
                : "قرض مسدد متأخر",
            },
          });
        }

        return {
          loan: updatedLoan,
          wallet: updatedWallet,
          transaction,
          remainingAmount: loanTotalDue - newPaidAmount,
          message: isFullyPaid
            ? "تهانينا! تم سداد القرض بالكامل. تم رفع تصنيفك الائتماني."
            : `تم السداد بنجاح. المتبقي: ${loanTotalDue - newPaidAmount} ر.ي`,
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
   * الحصول على قروض المستخدم
   */
  async getUserLoans(walletId: string) {
    return this.prisma.loan.findMany({
      where: { walletId },
      orderBy: { createdAt: "desc" },
      take: 100,
    });
  }

  /**
   * إنشاء دفعة مجدولة
   */
  async createScheduledPayment(
    walletId: string,
    amount: number,
    frequency: string,
    nextPaymentDate: Date,
    loanId?: string,
    description?: string,
    descriptionAr?: string,
  ) {
    const wallet = await this.prisma.wallet.findUnique({
      where: { id: walletId },
    });

    if (!wallet) {
      throw new NotFoundException("المحفظة غير موجودة");
    }

    const scheduledPayment = await this.prisma.scheduledPayment.create({
      data: {
        walletId,
        amount,
        frequency: frequency as any,
        nextPaymentDate,
        loanId,
        description,
        descriptionAr,
        isActive: true,
      },
    });

    return {
      scheduledPayment,
      message: "تم إنشاء الدفعة المجدولة بنجاح",
    };
  }

  /**
   * الحصول على الدفعات المجدولة للمحفظة
   */
  async getScheduledPayments(walletId: string, activeOnly: boolean = true) {
    return this.prisma.scheduledPayment.findMany({
      where: {
        walletId,
        ...(activeOnly && { isActive: true }),
      },
      orderBy: { nextPaymentDate: "asc" },
      take: 100,
    });
  }

  /**
   * إلغاء دفعة مجدولة
   */
  async cancelScheduledPayment(paymentId: string) {
    const payment = await this.prisma.scheduledPayment.findUnique({
      where: { id: paymentId },
    });

    if (!payment) {
      throw new NotFoundException("الدفعة المجدولة غير موجودة");
    }

    return this.prisma.scheduledPayment.update({
      where: { id: paymentId },
      data: { isActive: false },
    });
  }

  /**
   * تنفيذ دفعة مجدولة
   */
  async executeScheduledPayment(paymentId: string) {
    const payment = await this.prisma.scheduledPayment.findUnique({
      where: { id: paymentId },
      include: { wallet: true },
    });

    if (!payment) {
      throw new NotFoundException("الدفعة المجدولة غير موجودة");
    }

    if (!payment.isActive) {
      throw new BadRequestException("الدفعة المجدولة غير نشطة");
    }

    if (toNum(payment.wallet.balance) < toNum(payment.amount)) {
      await this.prisma.scheduledPayment.update({
        where: { id: paymentId },
        data: {
          failedAttempts: { increment: 1 },
          lastFailureReason: "الرصيد غير كافي",
        },
      });
      throw new BadRequestException("الرصيد غير كافي لتنفيذ الدفعة المجدولة");
    }

    const nextDate = new Date(payment.nextPaymentDate);
    switch (payment.frequency) {
      case "DAILY":
        nextDate.setDate(nextDate.getDate() + 1);
        break;
      case "WEEKLY":
        nextDate.setDate(nextDate.getDate() + 7);
        break;
      case "BIWEEKLY":
        nextDate.setDate(nextDate.getDate() + 14);
        break;
      case "MONTHLY":
        nextDate.setMonth(nextDate.getMonth() + 1);
        break;
      case "QUARTERLY":
        nextDate.setMonth(nextDate.getMonth() + 3);
        break;
      case "YEARLY":
        nextDate.setFullYear(nextDate.getFullYear() + 1);
        break;
    }

    const paymentAmountNum = toNum(payment.amount);
    const newBalance = toNum(payment.wallet.balance) - paymentAmountNum;

    const [updatedPayment, updatedWallet, transaction] =
      await this.prisma.$transaction([
        this.prisma.scheduledPayment.update({
          where: { id: paymentId },
          data: {
            lastPaymentDate: new Date(),
            nextPaymentDate: nextDate,
            failedAttempts: 0,
            lastFailureReason: null,
          },
        }),
        this.prisma.wallet.update({
          where: { id: payment.walletId },
          data: { balance: newBalance },
        }),
        this.prisma.transaction.create({
          data: {
            walletId: payment.walletId,
            type: "SCHEDULED_PAYMENT",
            amount: -paymentAmountNum,
            balanceAfter: newBalance,
            referenceId: payment.loanId || paymentId,
            referenceType: payment.loanId ? "loan" : "scheduled_payment",
            description: payment.description || "Scheduled payment",
            descriptionAr: payment.descriptionAr || "دفعة مجدولة",
            status: "COMPLETED",
          },
        }),
      ]);

    return { payment: updatedPayment, wallet: updatedWallet, transaction };
  }
}
