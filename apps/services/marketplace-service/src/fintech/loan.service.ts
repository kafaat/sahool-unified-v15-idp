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

import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

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
export class LoanService {
  constructor(private prisma: PrismaService) {}

  /**
   * ترجمة غرض القرض
   */
  getLoanPurposeAr(purpose: string): string {
    const purposes: Record<string, string> = {
      SEEDS: 'شراء بذور',
      FERTILIZER: 'شراء أسمدة',
      EQUIPMENT: 'شراء معدات',
      IRRIGATION: 'نظام ري',
      EXPANSION: 'توسيع المزرعة',
      EMERGENCY: 'طوارئ',
      OTHER: 'أخرى',
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
      throw new NotFoundException('المحفظة غير موجودة');
    }

    const availableCredit = wallet.loanLimit - wallet.currentLoan;

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
        status: 'PENDING',
      },
    });

    return {
      loan,
      message: 'تم تقديم طلب القرض بنجاح. سيتم مراجعته خلال 24-48 ساعة.',
      nextSteps: [
        'سيتم التحقق من بياناتك',
        'قد نطلب مستندات إضافية',
        'سيتم إيداع المبلغ في محفظتك عند الموافقة',
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
      throw new NotFoundException('القرض غير موجود');
    }

    if (loan.status !== 'PENDING') {
      throw new BadRequestException('لا يمكن الموافقة على هذا القرض');
    }

    const [updatedLoan, updatedWallet, transaction] = await this.prisma.$transaction([
      this.prisma.loan.update({
        where: { id: loanId },
        data: { status: 'ACTIVE' },
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
          type: 'LOAN',
          amount: loan.amount,
          balanceAfter: loan.wallet.balance + loan.amount,
          referenceId: loanId,
          referenceType: 'loan',
          description: `Agricultural loan - ${loan.purpose}`,
          descriptionAr: `قرض زراعي - ${this.getLoanPurposeAr(loan.purpose)}`,
          status: 'COMPLETED',
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
      throw new BadRequestException('المبلغ يجب أن يكون أكبر من صفر');
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
        return {
          loan,
          wallet: loan?.wallet,
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
          throw new NotFoundException('القرض غير موجود');
        }

        if (loan.status !== 'ACTIVE') {
          throw new BadRequestException('القرض غير نشط');
        }

        const walletRows = await tx.$queryRaw<any[]>`
          SELECT * FROM wallets WHERE id = ${loan.walletId}::uuid FOR UPDATE
        `;

        if (!walletRows || walletRows.length === 0) {
          throw new NotFoundException('المحفظة غير موجودة');
        }

        const wallet = walletRows[0];
        const balanceBefore = wallet.balance;
        const versionBefore = wallet.version;

        const remainingDue = loan.totalDue - loan.paidAmount;
        const paymentAmount = Math.min(amount, remainingDue);

        if (balanceBefore < paymentAmount) {
          throw new BadRequestException(
            `الرصيد غير كافي للسداد. الرصيد: ${balanceBefore}, المطلوب: ${paymentAmount}`,
          );
        }

        const newPaidAmount = loan.paidAmount + paymentAmount;
        const isFullyPaid = newPaidAmount >= loan.totalDue;
        const newBalance = balanceBefore - paymentAmount;
        const newVersion = versionBefore + 1;

        const updatedLoan = await tx.loan.update({
          where: { id: loanId },
          data: {
            paidAmount: newPaidAmount,
            status: isFullyPaid ? 'PAID' : 'ACTIVE',
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
            type: 'REPAYMENT',
            amount: -paymentAmount,
            balanceAfter: newBalance,
            balanceBefore,
            referenceId: loanId,
            referenceType: 'loan',
            description: `Loan repayment`,
            descriptionAr: isFullyPaid ? 'سداد كامل للقرض' : 'سداد جزئي للقرض',
            status: 'COMPLETED',
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
            operation: 'LOAN_REPAYMENT',
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
              remainingDue: loan.totalDue - newPaidAmount,
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
              eventType: isOnTime ? 'LOAN_REPAID_ONTIME' : 'LOAN_REPAID_LATE',
              amount: loan.totalDue,
              impact: isOnTime ? 15 : -10,
              description: isOnTime
                ? 'قرض مسدد في الوقت المحدد'
                : 'قرض مسدد متأخر',
            },
          });
        }

        return {
          loan: updatedLoan,
          wallet: updatedWallet,
          transaction,
          remainingAmount: loan.totalDue - newPaidAmount,
          message: isFullyPaid
            ? 'تهانينا! تم سداد القرض بالكامل. تم رفع تصنيفك الائتماني.'
            : `تم السداد بنجاح. المتبقي: ${loan.totalDue - newPaidAmount} ر.ي`,
          duplicate: false,
        };
      },
      {
        isolationLevel: 'Serializable',
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
      orderBy: { createdAt: 'desc' },
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
      throw new NotFoundException('المحفظة غير موجودة');
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
      message: 'تم إنشاء الدفعة المجدولة بنجاح',
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
      orderBy: { nextPaymentDate: 'asc' },
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
      throw new NotFoundException('الدفعة المجدولة غير موجودة');
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
      throw new NotFoundException('الدفعة المجدولة غير موجودة');
    }

    if (!payment.isActive) {
      throw new BadRequestException('الدفعة المجدولة غير نشطة');
    }

    if (payment.wallet.balance < payment.amount) {
      await this.prisma.scheduledPayment.update({
        where: { id: paymentId },
        data: {
          failedAttempts: { increment: 1 },
          lastFailureReason: 'الرصيد غير كافي',
        },
      });
      throw new BadRequestException('الرصيد غير كافي لتنفيذ الدفعة المجدولة');
    }

    const nextDate = new Date(payment.nextPaymentDate);
    switch (payment.frequency) {
      case 'DAILY':
        nextDate.setDate(nextDate.getDate() + 1);
        break;
      case 'WEEKLY':
        nextDate.setDate(nextDate.getDate() + 7);
        break;
      case 'BIWEEKLY':
        nextDate.setDate(nextDate.getDate() + 14);
        break;
      case 'MONTHLY':
        nextDate.setMonth(nextDate.getMonth() + 1);
        break;
      case 'QUARTERLY':
        nextDate.setMonth(nextDate.getMonth() + 3);
        break;
      case 'YEARLY':
        nextDate.setFullYear(nextDate.getFullYear() + 1);
        break;
    }

    const newBalance = payment.wallet.balance - payment.amount;

    const [updatedPayment, updatedWallet, transaction] = await this.prisma.$transaction([
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
          type: 'SCHEDULED_PAYMENT',
          amount: -payment.amount,
          balanceAfter: newBalance,
          referenceId: payment.loanId || paymentId,
          referenceType: payment.loanId ? 'loan' : 'scheduled_payment',
          description: payment.description || 'Scheduled payment',
          descriptionAr: payment.descriptionAr || 'دفعة مجدولة',
          status: 'COMPLETED',
        },
      }),
    ]);

    return { payment: updatedPayment, wallet: updatedWallet, transaction };
  }
}
