/**
 * SAHOOL FinTech Service
 * خدمة التمويل الزراعي - المحفظة والتصنيف الائتماني
 *
 * Features:
 * - Digital wallet management
 * - Credit scoring based on farm data & activity
 * - Agricultural loans (Islamic finance compatible)
 * - Transaction history
 */

import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

// Types
interface FarmData {
  totalArea: number; // مساحة المزرعة بالهكتار
  activeSeasons: number; // عدد المواسم النشطة
  fieldCount: number; // عدد الحقول
  diseaseRisk: 'Low' | 'Medium' | 'High'; // مستوى خطر الأمراض
  irrigationType: string; // نوع الري
  avgYieldScore: number; // متوسط درجة الإنتاجية (0-100)
  onTimePayments: number; // عدد المدفوعات في الوقت
  latePayments: number; // عدد المدفوعات المتأخرة
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

interface TransferDto {
  fromWalletId: string;
  toWalletId: string;
  amount: number;
  description?: string;
}

@Injectable()
export class FintechService {
  constructor(private prisma: PrismaService) {}

  // ═══════════════════════════════════════════════════════════════════════════
  // المحفظة - Wallet
  // ═══════════════════════════════════════════════════════════════════════════

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
  private getCreditTierAr(tier: string): string {
    const tiers: Record<string, string> = {
      BRONZE: 'برونزي',
      SILVER: 'فضي',
      GOLD: 'ذهبي',
      PLATINUM: 'بلاتيني',
    };
    return tiers[tier] || tier;
  }

  /**
   * إيداع مبلغ في المحفظة
   */
  async deposit(walletId: string, amount: number, description?: string) {
    if (amount <= 0) {
      throw new BadRequestException('المبلغ يجب أن يكون أكبر من صفر');
    }

    const wallet = await this.prisma.wallet.findUnique({
      where: { id: walletId },
    });

    if (!wallet) {
      throw new NotFoundException('المحفظة غير موجودة');
    }

    const newBalance = wallet.balance + amount;

    // تحديث الرصيد وإنشاء معاملة
    const [updatedWallet, transaction] = await this.prisma.$transaction([
      this.prisma.wallet.update({
        where: { id: walletId },
        data: { balance: newBalance },
      }),
      this.prisma.transaction.create({
        data: {
          walletId,
          type: 'DEPOSIT',
          amount,
          balanceAfter: newBalance,
          description: description || 'إيداع',
          descriptionAr: description || 'إيداع في المحفظة',
          status: 'COMPLETED',
        },
      }),
    ]);

    return { wallet: updatedWallet, transaction };
  }

  /**
   * سحب مبلغ من المحفظة
   */
  async withdraw(walletId: string, amount: number, description?: string) {
    if (amount <= 0) {
      throw new BadRequestException('المبلغ يجب أن يكون أكبر من صفر');
    }

    const wallet = await this.prisma.wallet.findUnique({
      where: { id: walletId },
    });

    if (!wallet) {
      throw new NotFoundException('المحفظة غير موجودة');
    }

    if (wallet.balance < amount) {
      throw new BadRequestException('الرصيد غير كافي');
    }

    const newBalance = wallet.balance - amount;

    const [updatedWallet, transaction] = await this.prisma.$transaction([
      this.prisma.wallet.update({
        where: { id: walletId },
        data: { balance: newBalance },
      }),
      this.prisma.transaction.create({
        data: {
          walletId,
          type: 'WITHDRAWAL',
          amount: -amount,
          balanceAfter: newBalance,
          description: description || 'سحب',
          descriptionAr: description || 'سحب من المحفظة',
          status: 'COMPLETED',
        },
      }),
    ]);

    return { wallet: updatedWallet, transaction };
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

  // ═══════════════════════════════════════════════════════════════════════════
  // التصنيف الائتماني - Credit Scoring
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * ⭐ حساب التصنيف الائتماني بناءً على بيانات المزرعة
   * هذه الخوارزمية تحول النشاط الزراعي إلى جدارة ائتمانية
   */
  async calculateCreditScore(userId: string, farmData: FarmData) {
    let score = 300; // البداية

    // ═══════════════════════════════════════════════════════════════════════
    // 1. عامل الأصول والمساحة (200 نقطة كحد أقصى)
    // ═══════════════════════════════════════════════════════════════════════
    if (farmData.totalArea > 0) {
      // مساحة كبيرة = ضمان أعلى
      if (farmData.totalArea >= 10) score += 100;
      else if (farmData.totalArea >= 5) score += 75;
      else if (farmData.totalArea >= 2) score += 50;
      else score += 25;

      // تعدد الحقول يعني تنويع المخاطر
      if (farmData.fieldCount >= 5) score += 50;
      else if (farmData.fieldCount >= 3) score += 30;
      else if (farmData.fieldCount >= 2) score += 15;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // 2. عامل الخبرة والاستمرارية (100 نقطة)
    // ═══════════════════════════════════════════════════════════════════════
    if (farmData.activeSeasons >= 5) score += 100;
    else if (farmData.activeSeasons >= 3) score += 75;
    else if (farmData.activeSeasons >= 2) score += 50;
    else if (farmData.activeSeasons >= 1) score += 25;

    // ═══════════════════════════════════════════════════════════════════════
    // 3. عامل إدارة المخاطر الزراعية (100 نقطة)
    // ═══════════════════════════════════════════════════════════════════════
    // من خدمة crop-health-ai
    if (farmData.diseaseRisk === 'Low') score += 100;
    else if (farmData.diseaseRisk === 'Medium') score += 50;
    // High = 0 نقاط إضافية

    // ═══════════════════════════════════════════════════════════════════════
    // 4. عامل البنية التحتية (50 نقطة)
    // ═══════════════════════════════════════════════════════════════════════
    const modernIrrigation = ['drip', 'sprinkler', 'smart'];
    if (modernIrrigation.includes(farmData.irrigationType?.toLowerCase())) {
      score += 50;
    } else if (farmData.irrigationType) {
      score += 25;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // 5. عامل الإنتاجية (100 نقطة)
    // ═══════════════════════════════════════════════════════════════════════
    // من yield-engine
    if (farmData.avgYieldScore >= 80) score += 100;
    else if (farmData.avgYieldScore >= 60) score += 75;
    else if (farmData.avgYieldScore >= 40) score += 50;
    else if (farmData.avgYieldScore > 0) score += 25;

    // ═══════════════════════════════════════════════════════════════════════
    // 6. عامل السلوك المالي (100 نقطة)
    // ═══════════════════════════════════════════════════════════════════════
    const totalPayments = farmData.onTimePayments + farmData.latePayments;
    if (totalPayments > 0) {
      const onTimeRatio = farmData.onTimePayments / totalPayments;
      if (onTimeRatio >= 0.95) score += 100;
      else if (onTimeRatio >= 0.85) score += 75;
      else if (onTimeRatio >= 0.70) score += 50;
      else if (onTimeRatio >= 0.50) score += 25;
      // أقل من 50% = عقوبة
      else score -= 50;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // تحديد التصنيف والحد الائتماني
    // ═══════════════════════════════════════════════════════════════════════
    // الحد الأقصى 850
    score = Math.min(850, Math.max(300, score));

    let creditTier: 'BRONZE' | 'SILVER' | 'GOLD' | 'PLATINUM';
    let loanMultiplier: number;

    if (score >= 750) {
      creditTier = 'PLATINUM';
      loanMultiplier = 50; // النقطة = 50 ريال
    } else if (score >= 650) {
      creditTier = 'GOLD';
      loanMultiplier = 35;
    } else if (score >= 500) {
      creditTier = 'SILVER';
      loanMultiplier = 20;
    } else {
      creditTier = 'BRONZE';
      loanMultiplier = 10;
    }

    const loanLimit = score * loanMultiplier;

    // تحديث أو إنشاء المحفظة
    const wallet = await this.prisma.wallet.upsert({
      where: { userId },
      update: {
        creditScore: score,
        creditTier,
        loanLimit,
      },
      create: {
        userId,
        userType: 'farmer',
        creditScore: score,
        creditTier,
        loanLimit,
      },
    });

    return {
      wallet,
      scoreBreakdown: {
        assetsScore: Math.min(200, score - 300),
        experienceScore: farmData.activeSeasons * 20,
        riskScore: farmData.diseaseRisk === 'Low' ? 100 : farmData.diseaseRisk === 'Medium' ? 50 : 0,
        yieldScore: Math.round(farmData.avgYieldScore),
      },
      creditTierAr: this.getCreditTierAr(creditTier),
      availableCredit: loanLimit - wallet.currentLoan,
      message:
        score >= 650
          ? 'تهانينا! لديك تصنيف ائتماني ممتاز يؤهلك للحصول على تمويل زراعي.'
          : score >= 500
          ? 'تصنيفك الائتماني جيد. استمر في تحسين مزرعتك لرفع حدك الائتماني.'
          : 'ننصحك بزيادة نشاطك الزراعي وتحسين صحة المحاصيل لرفع تصنيفك.',
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // القروض - Loans
  // ═══════════════════════════════════════════════════════════════════════════

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
    // يمكن إضافة رسوم إدارية ثابتة
    const adminFee = data.amount * 0.02; // 2% رسوم إدارية
    const totalDue = data.amount + adminFee;

    const startDate = new Date();
    const dueDate = new Date();
    dueDate.setMonth(dueDate.getMonth() + data.termMonths);

    const loan = await this.prisma.loan.create({
      data: {
        walletId: data.walletId,
        amount: data.amount,
        interestRate: 0, // تمويل إسلامي
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

    // تحديث القرض والمحفظة
    const [updatedLoan, updatedWallet, transaction] =
      await this.prisma.$transaction([
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
   * سداد القرض
   */
  async repayLoan(loanId: string, amount: number) {
    const loan = await this.prisma.loan.findUnique({
      where: { id: loanId },
      include: { wallet: true },
    });

    if (!loan) {
      throw new NotFoundException('القرض غير موجود');
    }

    if (loan.status !== 'ACTIVE') {
      throw new BadRequestException('القرض غير نشط');
    }

    if (loan.wallet.balance < amount) {
      throw new BadRequestException('الرصيد غير كافي للسداد');
    }

    const remainingDue = loan.totalDue - loan.paidAmount;
    const paymentAmount = Math.min(amount, remainingDue);
    const newPaidAmount = loan.paidAmount + paymentAmount;
    const isFullyPaid = newPaidAmount >= loan.totalDue;

    const [updatedLoan, updatedWallet, transaction] =
      await this.prisma.$transaction([
        this.prisma.loan.update({
          where: { id: loanId },
          data: {
            paidAmount: newPaidAmount,
            status: isFullyPaid ? 'PAID' : 'ACTIVE',
          },
        }),
        this.prisma.wallet.update({
          where: { id: loan.walletId },
          data: {
            balance: { decrement: paymentAmount },
            currentLoan: { decrement: paymentAmount },
          },
        }),
        this.prisma.transaction.create({
          data: {
            walletId: loan.walletId,
            type: 'REPAYMENT',
            amount: -paymentAmount,
            balanceAfter: loan.wallet.balance - paymentAmount,
            referenceId: loanId,
            referenceType: 'loan',
            description: `Loan repayment`,
            descriptionAr: isFullyPaid ? 'سداد كامل للقرض' : 'سداد جزئي للقرض',
            status: 'COMPLETED',
          },
        }),
      ]);

    return {
      loan: updatedLoan,
      wallet: updatedWallet,
      transaction,
      remainingAmount: loan.totalDue - newPaidAmount,
      message: isFullyPaid
        ? 'تهانينا! تم سداد القرض بالكامل. تم رفع تصنيفك الائتماني.'
        : `تم السداد بنجاح. المتبقي: ${loan.totalDue - newPaidAmount} ر.ي`,
    };
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
   * ترجمة غرض القرض
   */
  private getLoanPurposeAr(purpose: string): string {
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

  // ═══════════════════════════════════════════════════════════════════════════
  // الإحصائيات - Statistics
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إحصائيات الخدمة المالية
   */
  async getFinanceStats() {
    const [totalWallets, totalBalance, activeLoans, paidLoans] =
      await Promise.all([
        this.prisma.wallet.count(),
        this.prisma.wallet.aggregate({ _sum: { balance: true } }),
        this.prisma.loan.count({ where: { status: 'ACTIVE' } }),
        this.prisma.loan.count({ where: { status: 'PAID' } }),
      ]);

    const avgCreditScore = await this.prisma.wallet.aggregate({
      _avg: { creditScore: true },
    });

    return {
      totalWallets,
      totalBalance: totalBalance._sum.balance || 0,
      activeLoans,
      paidLoans,
      avgCreditScore: Math.round(avgCreditScore._avg.creditScore || 0),
    };
  }
}
