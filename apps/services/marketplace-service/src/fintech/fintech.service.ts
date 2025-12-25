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

// ⭐ Advanced Credit Factors Interface
interface CreditFactors {
  // Existing basic factors
  farmArea: number;
  numberOfSeasons: number;
  diseaseRiskScore: number; // 0-100
  irrigationType: 'rainfed' | 'drip' | 'flood' | 'sprinkler';
  yieldScore: number; // 0-100
  paymentHistory: number; // 0-100

  // NEW advanced factors
  cropDiversity: number; // Number of different crops (1-10)
  marketplaceHistory: number; // Completed orders (0-100)
  loanRepaymentRate: number; // % of loans repaid on time (0-100)
  verificationLevel: 'basic' | 'verified' | 'premium';
  landOwnership: 'owned' | 'leased' | 'shared';
  cooperativeMember: boolean;
  yearsOfExperience: number;
  satelliteVerified: boolean; // Farm verified by satellite
}

interface CreditRecommendation {
  action: string;
  impact: number; // Potential score increase
  priority: 'high' | 'medium' | 'low';
  category: string;
}

interface CreditReport {
  userId: string;
  currentScore: number;
  creditTier: string;
  factors: CreditFactors;
  scoreBreakdown: {
    farmDataScore: number;
    paymentHistoryScore: number;
    verificationScore: number;
    bonusScore: number;
  };
  recommendations: CreditRecommendation[];
  recentEvents: any[];
  availableCredit: number;
  riskLevel: 'low' | 'medium' | 'high';
}

interface RecordCreditEventDto {
  walletId: string;
  eventType: string;
  amount?: number;
  description: string;
  metadata?: any;
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

    // Check wallet limits
    await this.checkWithdrawLimits(wallet, amount);

    const newBalance = wallet.balance - amount;
    const newDailyWithdrawn = this.updateDailyWithdrawn(wallet, amount);

    const [updatedWallet, transaction] = await this.prisma.$transaction([
      this.prisma.wallet.update({
        where: { id: walletId },
        data: {
          balance: newBalance,
          dailyWithdrawnToday: newDailyWithdrawn.dailyWithdrawnToday,
          lastWithdrawReset: newDailyWithdrawn.lastWithdrawReset,
        },
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

  // ═══════════════════════════════════════════════════════════════════════════
  // التصنيف الائتماني المتقدم - Advanced Credit Scoring
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * ⭐ حساب التصنيف الائتماني المتقدم
   * Advanced Credit Scoring with Multiple Factors
   *
   * Score Breakdown:
   * - Base score from farm data (40%)
   * - Payment/marketplace history (30%)
   * - Verification & trust factors (20%)
   * - Bonus factors (10%)
   */
  async calculateAdvancedCreditScore(userId: string, factors: CreditFactors) {
    let score = 300; // Starting score
    const breakdown = {
      farmDataScore: 0,
      paymentHistoryScore: 0,
      verificationScore: 0,
      bonusScore: 0,
    };

    // ═══════════════════════════════════════════════════════════════════════
    // 1. Farm Data Score (40% = 340 points max)
    // ═══════════════════════════════════════════════════════════════════════
    let farmDataScore = 0;

    // Farm area (100 points)
    if (factors.farmArea >= 10) farmDataScore += 100;
    else if (factors.farmArea >= 5) farmDataScore += 80;
    else if (factors.farmArea >= 2) farmDataScore += 60;
    else if (factors.farmArea >= 1) farmDataScore += 40;
    else if (factors.farmArea > 0) farmDataScore += 20;

    // Crop diversity (60 points)
    farmDataScore += Math.min(60, factors.cropDiversity * 6);

    // Years of experience (80 points)
    if (factors.yearsOfExperience >= 10) farmDataScore += 80;
    else if (factors.yearsOfExperience >= 5) farmDataScore += 60;
    else if (factors.yearsOfExperience >= 3) farmDataScore += 40;
    else if (factors.yearsOfExperience >= 1) farmDataScore += 20;

    // Irrigation type (50 points)
    if (factors.irrigationType === 'drip') farmDataScore += 50;
    else if (factors.irrigationType === 'sprinkler') farmDataScore += 40;
    else if (factors.irrigationType === 'flood') farmDataScore += 25;
    else if (factors.irrigationType === 'rainfed') farmDataScore += 10;

    // Disease risk (50 points)
    farmDataScore += Math.round(factors.diseaseRiskScore * 0.5);

    breakdown.farmDataScore = Math.min(340, farmDataScore);
    score += breakdown.farmDataScore;

    // ═══════════════════════════════════════════════════════════════════════
    // 2. Payment & Marketplace History (30% = 255 points max)
    // ═══════════════════════════════════════════════════════════════════════
    let paymentScore = 0;

    // Payment history (100 points)
    paymentScore += factors.paymentHistory;

    // Loan repayment rate (100 points)
    paymentScore += factors.loanRepaymentRate;

    // Marketplace history (55 points)
    paymentScore += Math.min(55, factors.marketplaceHistory * 0.55);

    breakdown.paymentHistoryScore = Math.min(255, paymentScore);
    score += breakdown.paymentHistoryScore;

    // ═══════════════════════════════════════════════════════════════════════
    // 3. Verification & Trust Factors (20% = 170 points max)
    // ═══════════════════════════════════════════════════════════════════════
    let verificationScore = 0;

    // Verification level (70 points)
    if (factors.verificationLevel === 'premium') verificationScore += 70;
    else if (factors.verificationLevel === 'verified') verificationScore += 50;
    else if (factors.verificationLevel === 'basic') verificationScore += 20;

    // Land ownership (50 points)
    if (factors.landOwnership === 'owned') verificationScore += 50;
    else if (factors.landOwnership === 'leased') verificationScore += 30;
    else if (factors.landOwnership === 'shared') verificationScore += 15;

    // Satellite verification (50 points)
    if (factors.satelliteVerified) verificationScore += 50;

    breakdown.verificationScore = Math.min(170, verificationScore);
    score += breakdown.verificationScore;

    // ═══════════════════════════════════════════════════════════════════════
    // 4. Bonus Factors (10% = 85 points max)
    // ═══════════════════════════════════════════════════════════════════════
    let bonusScore = 0;

    // Cooperative membership (40 points)
    if (factors.cooperativeMember) bonusScore += 40;

    // Yield performance (45 points)
    bonusScore += Math.round(factors.yieldScore * 0.45);

    breakdown.bonusScore = Math.min(85, bonusScore);
    score += breakdown.bonusScore;

    // ═══════════════════════════════════════════════════════════════════════
    // Final Score Calculation (Max: 850)
    // ═══════════════════════════════════════════════════════════════════════
    score = Math.min(850, Math.max(300, score));

    // Determine credit tier and loan multiplier
    let creditTier: 'BRONZE' | 'SILVER' | 'GOLD' | 'PLATINUM';
    let loanMultiplier: number;

    if (score >= 750) {
      creditTier = 'PLATINUM';
      loanMultiplier = 50;
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

    // Update wallet
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
      score,
      creditTier,
      creditTierAr: this.getCreditTierAr(creditTier),
      loanLimit,
      availableCredit: loanLimit - wallet.currentLoan,
      breakdown,
      factors,
    };
  }

  /**
   * جلب عوامل التصنيف الائتماني بالتفصيل
   * Get detailed credit factors for a user
   */
  async getCreditFactors(userId: string): Promise<CreditFactors> {
    const wallet = await this.prisma.wallet.findUnique({
      where: { userId },
      include: {
        loans: true,
        creditEvents: {
          take: 50,
          orderBy: { createdAt: 'desc' },
        },
      },
    });

    if (!wallet) {
      throw new NotFoundException('المحفظة غير موجودة');
    }

    // Calculate factors from wallet data and credit events
    const totalLoans = wallet.loans.length;
    const paidLoans = wallet.loans.filter((l) => l.status === 'PAID').length;
    const lateLoans = wallet.loans.filter((l) => l.status === 'DEFAULTED').length;
    const loanRepaymentRate = totalLoans > 0 ? (paidLoans / totalLoans) * 100 : 0;

    // Count completed orders from credit events
    const completedOrders = wallet.creditEvents.filter(
      (e) => e.eventType === 'ORDER_COMPLETED',
    ).length;

    // Check verification status from events
    const hasVerificationUpgrade = wallet.creditEvents.some(
      (e) => e.eventType === 'VERIFICATION_UPGRADE',
    );
    const hasFarmVerification = wallet.creditEvents.some(
      (e) => e.eventType === 'FARM_VERIFIED',
    );
    const hasLandVerification = wallet.creditEvents.some(
      (e) => e.eventType === 'LAND_VERIFIED',
    );
    const hasCooperative = wallet.creditEvents.some(
      (e) => e.eventType === 'COOPERATIVE_JOINED',
    );

    // Determine verification level
    let verificationLevel: 'basic' | 'verified' | 'premium' = 'basic';
    if (hasVerificationUpgrade && hasFarmVerification && hasLandVerification) {
      verificationLevel = 'premium';
    } else if (wallet.isVerified || hasFarmVerification) {
      verificationLevel = 'verified';
    }

    // Build credit factors (with defaults for demo)
    const factors: CreditFactors = {
      farmArea: 5, // Default - should come from farm-core service
      numberOfSeasons: 3, // Default - should come from field-core service
      diseaseRiskScore: 75, // Default - should come from crop-health-ai
      irrigationType: 'drip', // Default
      yieldScore: 80, // Default - should come from yield-engine
      paymentHistory: Math.min(100, (paidLoans / Math.max(totalLoans, 1)) * 100),
      cropDiversity: 3, // Default - should come from field-core
      marketplaceHistory: completedOrders,
      loanRepaymentRate,
      verificationLevel,
      landOwnership: hasLandVerification ? 'owned' : 'leased',
      cooperativeMember: hasCooperative,
      yearsOfExperience: 3, // Default - should calculate from user creation date
      satelliteVerified: hasFarmVerification,
    };

    return factors;
  }

  /**
   * تسجيل حدث ائتماني جديد
   * Record a credit event (payment, default, verification, etc.)
   */
  async recordCreditEvent(data: RecordCreditEventDto) {
    const wallet = await this.prisma.wallet.findUnique({
      where: { id: data.walletId },
    });

    if (!wallet) {
      throw new NotFoundException('المحفظة غير موجودة');
    }

    // Determine impact based on event type
    const impactMap: Record<string, number> = {
      LOAN_REPAID_ONTIME: 15,
      LOAN_REPAID_LATE: -10,
      LOAN_DEFAULTED: -50,
      ORDER_COMPLETED: 5,
      ORDER_CANCELLED: -5,
      VERIFICATION_UPGRADE: 30,
      FARM_VERIFIED: 20,
      COOPERATIVE_JOINED: 10,
      LAND_VERIFIED: 15,
    };

    const impact = impactMap[data.eventType] || 0;

    // Create credit event
    const event = await this.prisma.creditEvent.create({
      data: {
        walletId: data.walletId,
        eventType: data.eventType as any,
        amount: data.amount,
        impact,
        description: data.description,
        metadata: data.metadata,
      },
    });

    // Update credit score
    const newScore = Math.min(850, Math.max(300, wallet.creditScore + impact));

    // Recalculate tier
    let newTier: 'BRONZE' | 'SILVER' | 'GOLD' | 'PLATINUM' = wallet.creditTier as any;
    if (newScore >= 750) newTier = 'PLATINUM';
    else if (newScore >= 650) newTier = 'GOLD';
    else if (newScore >= 500) newTier = 'SILVER';
    else newTier = 'BRONZE';

    const updatedWallet = await this.prisma.wallet.update({
      where: { id: data.walletId },
      data: {
        creditScore: newScore,
        creditTier: newTier,
      },
    });

    return {
      event,
      wallet: updatedWallet,
      impact,
      message: impact > 0
        ? `رائع! ارتفع تصنيفك الائتماني بمقدار ${impact} نقطة`
        : impact < 0
        ? `تنبيه: انخفض تصنيفك الائتماني بمقدار ${Math.abs(impact)} نقطة`
        : 'تم تسجيل الحدث',
    };
  }

  /**
   * جلب التقرير الائتماني الكامل
   * Get full credit report with recommendations
   */
  async getCreditReport(userId: string): Promise<CreditReport> {
    const wallet = await this.prisma.wallet.findUnique({
      where: { userId },
      include: {
        creditEvents: {
          take: 20,
          orderBy: { createdAt: 'desc' },
        },
        loans: true,
      },
    });

    if (!wallet) {
      throw new NotFoundException('المحفظة غير موجودة');
    }

    // Get detailed credit factors
    const factors = await this.getCreditFactors(userId);

    // Calculate score breakdown (simplified version)
    const scoreBreakdown = {
      farmDataScore: Math.round(wallet.creditScore * 0.4),
      paymentHistoryScore: Math.round(wallet.creditScore * 0.3),
      verificationScore: Math.round(wallet.creditScore * 0.2),
      bonusScore: Math.round(wallet.creditScore * 0.1),
    };

    // Generate recommendations
    const recommendations = this.generateRecommendations(factors, wallet.creditScore);

    // Determine risk level
    let riskLevel: 'low' | 'medium' | 'high' = 'medium';
    if (wallet.creditScore >= 700) riskLevel = 'low';
    else if (wallet.creditScore < 500) riskLevel = 'high';

    return {
      userId,
      currentScore: wallet.creditScore,
      creditTier: this.getCreditTierAr(wallet.creditTier),
      factors,
      scoreBreakdown,
      recommendations,
      recentEvents: wallet.creditEvents,
      availableCredit: wallet.loanLimit - wallet.currentLoan,
      riskLevel,
    };
  }

  /**
   * إنشاء توصيات لتحسين التصنيف الائتماني
   * Generate actionable recommendations to improve credit score
   */
  private generateRecommendations(
    factors: CreditFactors,
    currentScore: number,
  ): CreditRecommendation[] {
    const recommendations: CreditRecommendation[] = [];

    // Satellite verification
    if (!factors.satelliteVerified) {
      recommendations.push({
        action: 'قم بالتحقق من مزرعتك عبر صور الأقمار الصناعية',
        impact: 20,
        priority: 'high',
        category: 'verification',
      });
    }

    // Verification upgrade
    if (factors.verificationLevel === 'basic') {
      recommendations.push({
        action: 'قم برفع مستوى التحقق من حسابك إلى "موثق"',
        impact: 30,
        priority: 'high',
        category: 'verification',
      });
    } else if (factors.verificationLevel === 'verified') {
      recommendations.push({
        action: 'قم بالترقية إلى مستوى "بريميوم" بتوثيق جميع المستندات',
        impact: 20,
        priority: 'medium',
        category: 'verification',
      });
    }

    // Marketplace activity
    if (factors.marketplaceHistory < 5) {
      recommendations.push({
        action: `أكمل ${5 - factors.marketplaceHistory} طلبات إضافية في السوق`,
        impact: 15,
        priority: 'medium',
        category: 'activity',
      });
    }

    // Cooperative membership
    if (!factors.cooperativeMember) {
      recommendations.push({
        action: 'انضم إلى تعاونية زراعية لزيادة مصداقيتك',
        impact: 10,
        priority: 'medium',
        category: 'trust',
      });
    }

    // Land ownership
    if (factors.landOwnership !== 'owned') {
      recommendations.push({
        action: 'وثق ملكية الأرض لزيادة تصنيفك',
        impact: 35,
        priority: 'high',
        category: 'verification',
      });
    }

    // Crop diversity
    if (factors.cropDiversity < 3) {
      recommendations.push({
        action: 'زد من تنوع المحاصيل (حاليًا: ' + factors.cropDiversity + ' محاصيل)',
        impact: 12,
        priority: 'low',
        category: 'farming',
      });
    }

    // Irrigation improvement
    if (factors.irrigationType === 'rainfed' || factors.irrigationType === 'flood') {
      recommendations.push({
        action: 'حسّن نظام الري إلى الري بالتنقيط أو الرش',
        impact: 25,
        priority: 'medium',
        category: 'farming',
      });
    }

    // Payment history
    if (factors.loanRepaymentRate < 90 && factors.loanRepaymentRate > 0) {
      recommendations.push({
        action: 'حافظ على سداد القروض في الوقت المحدد',
        impact: 20,
        priority: 'high',
        category: 'payment',
      });
    }

    // Sort by priority and impact
    recommendations.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      }
      return b.impact - a.impact;
    });

    return recommendations.slice(0, 5); // Top 5 recommendations
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // حدود المحفظة والأمان - Wallet Limits & Security
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * التحقق من حدود السحب
   */
  private async checkWithdrawLimits(wallet: any, amount: number) {
    // Check single transaction limit
    if (amount > wallet.singleTransactionLimit) {
      throw new BadRequestException(
        `المبلغ يتجاوز حد المعاملة الواحدة (${wallet.singleTransactionLimit} ر.ي)`,
      );
    }

    // Check and reset daily limit if needed
    const now = new Date();
    const lastReset = wallet.lastWithdrawReset ? new Date(wallet.lastWithdrawReset) : null;
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
    const lastReset = wallet.lastWithdrawReset ? new Date(wallet.lastWithdrawReset) : null;
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
    const lastReset = wallet.lastWithdrawReset ? new Date(wallet.lastWithdrawReset) : null;
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

    // Set limits based on credit tier
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
      default: // BRONZE
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
  // الإسكرو - Escrow (لحماية معاملات السوق)
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء إسكرو جديد للطلب
   */
  async createEscrow(
    orderId: string,
    buyerWalletId: string,
    sellerWalletId: string,
    amount: number,
    notes?: string,
  ) {
    const buyerWallet = await this.prisma.wallet.findUnique({
      where: { id: buyerWalletId },
    });

    if (!buyerWallet) {
      throw new NotFoundException('محفظة المشتري غير موجودة');
    }

    if (buyerWallet.balance < amount) {
      throw new BadRequestException('رصيد المشتري غير كافي');
    }

    // Check if escrow already exists for this order
    const existingEscrow = await this.prisma.escrow.findUnique({
      where: { orderId },
    });

    if (existingEscrow) {
      throw new BadRequestException('يوجد إسكرو لهذا الطلب بالفعل');
    }

    // Create escrow and update wallet balances in a transaction
    const [escrow, updatedBuyerWallet, transaction] = await this.prisma.$transaction([
      this.prisma.escrow.create({
        data: {
          orderId,
          buyerWalletId,
          sellerWalletId,
          amount,
          status: 'HELD',
          notes,
        },
      }),
      this.prisma.wallet.update({
        where: { id: buyerWalletId },
        data: {
          balance: { decrement: amount },
          escrowBalance: { increment: amount },
        },
      }),
      this.prisma.transaction.create({
        data: {
          walletId: buyerWalletId,
          type: 'ESCROW_HOLD',
          amount: -amount,
          balanceAfter: buyerWallet.balance - amount,
          referenceId: orderId,
          referenceType: 'order',
          description: 'Funds held in escrow for order',
          descriptionAr: 'مبلغ محجوز في الإسكرو للطلب',
          status: 'COMPLETED',
        },
      }),
    ]);

    return { escrow, wallet: updatedBuyerWallet, transaction };
  }

  /**
   * إطلاق الإسكرو للبائع (عند التسليم)
   */
  async releaseEscrow(escrowId: string, notes?: string) {
    const escrow = await this.prisma.escrow.findUnique({
      where: { id: escrowId },
      include: {
        buyerWallet: true,
        sellerWallet: true,
      },
    });

    if (!escrow) {
      throw new NotFoundException('الإسكرو غير موجود');
    }

    if (escrow.status !== 'HELD') {
      throw new BadRequestException('الإسكرو ليس في حالة محجوز');
    }

    const now = new Date();

    const [updatedEscrow, updatedBuyerWallet, updatedSellerWallet, buyerTx, sellerTx] =
      await this.prisma.$transaction([
        this.prisma.escrow.update({
          where: { id: escrowId },
          data: {
            status: 'RELEASED',
            releasedAt: now,
            notes: notes || escrow.notes,
          },
        }),
        this.prisma.wallet.update({
          where: { id: escrow.buyerWalletId },
          data: {
            escrowBalance: { decrement: escrow.amount },
          },
        }),
        this.prisma.wallet.update({
          where: { id: escrow.sellerWalletId },
          data: {
            balance: { increment: escrow.amount },
          },
        }),
        this.prisma.transaction.create({
          data: {
            walletId: escrow.buyerWalletId,
            type: 'ESCROW_RELEASE',
            amount: 0,
            balanceAfter: escrow.buyerWallet.balance,
            referenceId: escrow.orderId,
            referenceType: 'order',
            description: 'Escrow released to seller',
            descriptionAr: 'تم إطلاق الإسكرو للبائع',
            status: 'COMPLETED',
          },
        }),
        this.prisma.transaction.create({
          data: {
            walletId: escrow.sellerWalletId,
            type: 'MARKETPLACE_SALE',
            amount: escrow.amount,
            balanceAfter: escrow.sellerWallet.balance + escrow.amount,
            referenceId: escrow.orderId,
            referenceType: 'order',
            description: 'Payment received from escrow',
            descriptionAr: 'استلام دفعة من الإسكرو',
            status: 'COMPLETED',
          },
        }),
      ]);

    return {
      escrow: updatedEscrow,
      buyerWallet: updatedBuyerWallet,
      sellerWallet: updatedSellerWallet,
      transactions: [buyerTx, sellerTx],
    };
  }

  /**
   * استرداد الإسكرو للمشتري (في حالة الإلغاء)
   */
  async refundEscrow(escrowId: string, reason?: string) {
    const escrow = await this.prisma.escrow.findUnique({
      where: { id: escrowId },
      include: {
        buyerWallet: true,
      },
    });

    if (!escrow) {
      throw new NotFoundException('الإسكرو غير موجود');
    }

    if (escrow.status !== 'HELD' && escrow.status !== 'DISPUTED') {
      throw new BadRequestException('لا يمكن استرداد هذا الإسكرو');
    }

    const now = new Date();

    const [updatedEscrow, updatedBuyerWallet, transaction] = await this.prisma.$transaction([
      this.prisma.escrow.update({
        where: { id: escrowId },
        data: {
          status: 'REFUNDED',
          refundedAt: now,
          disputeReason: reason,
        },
      }),
      this.prisma.wallet.update({
        where: { id: escrow.buyerWalletId },
        data: {
          balance: { increment: escrow.amount },
          escrowBalance: { decrement: escrow.amount },
        },
      }),
      this.prisma.transaction.create({
        data: {
          walletId: escrow.buyerWalletId,
          type: 'ESCROW_REFUND',
          amount: escrow.amount,
          balanceAfter: escrow.buyerWallet.balance + escrow.amount,
          referenceId: escrow.orderId,
          referenceType: 'order',
          description: `Escrow refunded: ${reason || 'Order cancelled'}`,
          descriptionAr: `استرداد الإسكرو: ${reason || 'تم إلغاء الطلب'}`,
          status: 'COMPLETED',
        },
      }),
    ]);

    return { escrow: updatedEscrow, wallet: updatedBuyerWallet, transaction };
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
        orderBy: { createdAt: 'desc' },
      }),
      this.prisma.escrow.findMany({
        where: { sellerWalletId: walletId },
        orderBy: { createdAt: 'desc' },
      }),
    ]);

    return { asBuyer, asSeller };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الدفعات المجدولة - Scheduled Payments
  // ═══════════════════════════════════════════════════════════════════════════

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
      // Record failed attempt
      await this.prisma.scheduledPayment.update({
        where: { id: paymentId },
        data: {
          failedAttempts: { increment: 1 },
          lastFailureReason: 'الرصيد غير كافي',
        },
      });
      throw new BadRequestException('الرصيد غير كافي لتنفيذ الدفعة المجدولة');
    }

    // Calculate next payment date
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

    // Execute payment
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

  // ═══════════════════════════════════════════════════════════════════════════
  // لوحة تحكم المحفظة - Wallet Dashboard
  // ═══════════════════════════════════════════════════════════════════════════

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

    // Get escrow balances
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

    // Get pending scheduled payments
    const pendingPayments = await this.prisma.scheduledPayment.findMany({
      where: {
        walletId,
        isActive: true,
        nextPaymentDate: {
          lte: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // Next 30 days
        },
      },
    });

    const totalPendingPayments = pendingPayments.reduce((sum, p) => sum + p.amount, 0);

    // Get monthly transactions for chart data
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
    const transactions = await this.prisma.transaction.findMany({
      where: {
        walletId,
        createdAt: { gte: thirtyDaysAgo },
      },
      orderBy: { createdAt: 'asc' },
    });

    // Calculate income/expense by day
    const dailyStats: Record<
      string,
      { date: string; income: number; expense: number }
    > = {};

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
        dailyRemaining: wallet.dailyWithdrawLimit - wallet.dailyWithdrawnToday,
        singleTransactionLimit: wallet.singleTransactionLimit,
      },
      monthlyChart,
      recentTransactions: transactions.slice(-10),
    };
  }
}
