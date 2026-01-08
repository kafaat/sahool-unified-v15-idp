/**
 * SAHOOL Credit Scoring Service
 * خدمة التصنيف الائتماني
 *
 * Features:
 * - Credit scoring based on farm data & activity
 * - Advanced multi-factor scoring algorithm
 * - Credit events tracking
 * - Credit report generation with recommendations
 */

import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

// Types
export interface FarmData {
  totalArea: number;
  activeSeasons: number;
  fieldCount: number;
  diseaseRisk: 'Low' | 'Medium' | 'High';
  irrigationType: string;
  avgYieldScore: number;
  onTimePayments: number;
  latePayments: number;
}

export interface CreditFactors {
  farmArea: number;
  numberOfSeasons: number;
  diseaseRiskScore: number;
  irrigationType: 'rainfed' | 'drip' | 'flood' | 'sprinkler';
  yieldScore: number;
  paymentHistory: number;
  cropDiversity: number;
  marketplaceHistory: number;
  loanRepaymentRate: number;
  verificationLevel: 'basic' | 'verified' | 'premium';
  landOwnership: 'owned' | 'leased' | 'shared';
  cooperativeMember: boolean;
  yearsOfExperience: number;
  satelliteVerified: boolean;
}

export interface CreditRecommendation {
  action: string;
  impact: number;
  priority: 'high' | 'medium' | 'low';
  category: string;
}

export interface CreditReport {
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

@Injectable()
export class CreditService {
  constructor(private prisma: PrismaService) {}

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
   * حساب التصنيف الائتماني بناءً على بيانات المزرعة
   */
  async calculateCreditScore(userId: string, farmData: FarmData) {
    let score = 300;

    // 1. عامل الأصول والمساحة (200 نقطة كحد أقصى)
    if (farmData.totalArea > 0) {
      if (farmData.totalArea >= 10) score += 100;
      else if (farmData.totalArea >= 5) score += 75;
      else if (farmData.totalArea >= 2) score += 50;
      else score += 25;

      if (farmData.fieldCount >= 5) score += 50;
      else if (farmData.fieldCount >= 3) score += 30;
      else if (farmData.fieldCount >= 2) score += 15;
    }

    // 2. عامل الخبرة والاستمرارية (100 نقطة)
    if (farmData.activeSeasons >= 5) score += 100;
    else if (farmData.activeSeasons >= 3) score += 75;
    else if (farmData.activeSeasons >= 2) score += 50;
    else if (farmData.activeSeasons >= 1) score += 25;

    // 3. عامل إدارة المخاطر الزراعية (100 نقطة)
    if (farmData.diseaseRisk === 'Low') score += 100;
    else if (farmData.diseaseRisk === 'Medium') score += 50;

    // 4. عامل البنية التحتية (50 نقطة)
    const modernIrrigation = ['drip', 'sprinkler', 'smart'];
    if (modernIrrigation.includes(farmData.irrigationType?.toLowerCase())) {
      score += 50;
    } else if (farmData.irrigationType) {
      score += 25;
    }

    // 5. عامل الإنتاجية (100 نقطة)
    if (farmData.avgYieldScore >= 80) score += 100;
    else if (farmData.avgYieldScore >= 60) score += 75;
    else if (farmData.avgYieldScore >= 40) score += 50;
    else if (farmData.avgYieldScore > 0) score += 25;

    // 6. عامل السلوك المالي (100 نقطة)
    const totalPayments = farmData.onTimePayments + farmData.latePayments;
    if (totalPayments > 0) {
      const onTimeRatio = farmData.onTimePayments / totalPayments;
      if (onTimeRatio >= 0.95) score += 100;
      else if (onTimeRatio >= 0.85) score += 75;
      else if (onTimeRatio >= 0.70) score += 50;
      else if (onTimeRatio >= 0.50) score += 25;
      else score -= 50;
    }

    score = Math.min(850, Math.max(300, score));

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

  /**
   * حساب التصنيف الائتماني المتقدم
   */
  async calculateAdvancedCreditScore(userId: string, factors: CreditFactors) {
    let score = 300;
    const breakdown = {
      farmDataScore: 0,
      paymentHistoryScore: 0,
      verificationScore: 0,
      bonusScore: 0,
    };

    // 1. Farm Data Score (40% = 340 points max)
    let farmDataScore = 0;

    if (factors.farmArea >= 10) farmDataScore += 100;
    else if (factors.farmArea >= 5) farmDataScore += 80;
    else if (factors.farmArea >= 2) farmDataScore += 60;
    else if (factors.farmArea >= 1) farmDataScore += 40;
    else if (factors.farmArea > 0) farmDataScore += 20;

    farmDataScore += Math.min(60, factors.cropDiversity * 6);

    if (factors.yearsOfExperience >= 10) farmDataScore += 80;
    else if (factors.yearsOfExperience >= 5) farmDataScore += 60;
    else if (factors.yearsOfExperience >= 3) farmDataScore += 40;
    else if (factors.yearsOfExperience >= 1) farmDataScore += 20;

    if (factors.irrigationType === 'drip') farmDataScore += 50;
    else if (factors.irrigationType === 'sprinkler') farmDataScore += 40;
    else if (factors.irrigationType === 'flood') farmDataScore += 25;
    else if (factors.irrigationType === 'rainfed') farmDataScore += 10;

    farmDataScore += Math.round(factors.diseaseRiskScore * 0.5);

    breakdown.farmDataScore = Math.min(340, farmDataScore);
    score += breakdown.farmDataScore;

    // 2. Payment & Marketplace History (30% = 255 points max)
    let paymentScore = 0;
    paymentScore += factors.paymentHistory;
    paymentScore += factors.loanRepaymentRate;
    paymentScore += Math.min(55, factors.marketplaceHistory * 0.55);

    breakdown.paymentHistoryScore = Math.min(255, paymentScore);
    score += breakdown.paymentHistoryScore;

    // 3. Verification & Trust Factors (20% = 170 points max)
    let verificationScore = 0;

    if (factors.verificationLevel === 'premium') verificationScore += 70;
    else if (factors.verificationLevel === 'verified') verificationScore += 50;
    else if (factors.verificationLevel === 'basic') verificationScore += 20;

    if (factors.landOwnership === 'owned') verificationScore += 50;
    else if (factors.landOwnership === 'leased') verificationScore += 30;
    else if (factors.landOwnership === 'shared') verificationScore += 15;

    if (factors.satelliteVerified) verificationScore += 50;

    breakdown.verificationScore = Math.min(170, verificationScore);
    score += breakdown.verificationScore;

    // 4. Bonus Factors (10% = 85 points max)
    let bonusScore = 0;
    if (factors.cooperativeMember) bonusScore += 40;
    bonusScore += Math.round(factors.yieldScore * 0.45);

    breakdown.bonusScore = Math.min(85, bonusScore);
    score += breakdown.bonusScore;

    score = Math.min(850, Math.max(300, score));

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

    const totalLoans = wallet.loans.length;
    const paidLoans = wallet.loans.filter((l) => l.status === 'PAID').length;
    const loanRepaymentRate = totalLoans > 0 ? (paidLoans / totalLoans) * 100 : 0;

    const completedOrders = wallet.creditEvents.filter(
      (e) => e.eventType === 'ORDER_COMPLETED',
    ).length;

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

    let verificationLevel: 'basic' | 'verified' | 'premium' = 'basic';
    if (hasVerificationUpgrade && hasFarmVerification && hasLandVerification) {
      verificationLevel = 'premium';
    } else if (wallet.isVerified || hasFarmVerification) {
      verificationLevel = 'verified';
    }

    const factors: CreditFactors = {
      farmArea: 5,
      numberOfSeasons: 3,
      diseaseRiskScore: 75,
      irrigationType: 'drip',
      yieldScore: 80,
      paymentHistory: Math.min(100, (paidLoans / Math.max(totalLoans, 1)) * 100),
      cropDiversity: 3,
      marketplaceHistory: completedOrders,
      loanRepaymentRate,
      verificationLevel,
      landOwnership: hasLandVerification ? 'owned' : 'leased',
      cooperativeMember: hasCooperative,
      yearsOfExperience: 3,
      satelliteVerified: hasFarmVerification,
    };

    return factors;
  }

  /**
   * تسجيل حدث ائتماني جديد
   */
  async recordCreditEvent(data: RecordCreditEventDto) {
    const wallet = await this.prisma.wallet.findUnique({
      where: { id: data.walletId },
    });

    if (!wallet) {
      throw new NotFoundException('المحفظة غير موجودة');
    }

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

    const newScore = Math.min(850, Math.max(300, wallet.creditScore + impact));

    type CreditTier = 'BRONZE' | 'SILVER' | 'GOLD' | 'PLATINUM';
    let newTier: CreditTier = wallet.creditTier as CreditTier;
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
      message:
        impact > 0
          ? `رائع! ارتفع تصنيفك الائتماني بمقدار ${impact} نقطة`
          : impact < 0
          ? `تنبيه: انخفض تصنيفك الائتماني بمقدار ${Math.abs(impact)} نقطة`
          : 'تم تسجيل الحدث',
    };
  }

  /**
   * جلب التقرير الائتماني الكامل
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

    const factors = await this.getCreditFactors(userId);

    const scoreBreakdown = {
      farmDataScore: Math.round(wallet.creditScore * 0.4),
      paymentHistoryScore: Math.round(wallet.creditScore * 0.3),
      verificationScore: Math.round(wallet.creditScore * 0.2),
      bonusScore: Math.round(wallet.creditScore * 0.1),
    };

    const recommendations = this.generateRecommendations(factors, wallet.creditScore);

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
   */
  private generateRecommendations(
    factors: CreditFactors,
    currentScore: number,
  ): CreditRecommendation[] {
    const recommendations: CreditRecommendation[] = [];

    if (!factors.satelliteVerified) {
      recommendations.push({
        action: 'قم بالتحقق من مزرعتك عبر صور الأقمار الصناعية',
        impact: 20,
        priority: 'high',
        category: 'verification',
      });
    }

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

    if (factors.marketplaceHistory < 5) {
      recommendations.push({
        action: `أكمل ${5 - factors.marketplaceHistory} طلبات إضافية في السوق`,
        impact: 15,
        priority: 'medium',
        category: 'activity',
      });
    }

    if (!factors.cooperativeMember) {
      recommendations.push({
        action: 'انضم إلى تعاونية زراعية لزيادة مصداقيتك',
        impact: 10,
        priority: 'medium',
        category: 'trust',
      });
    }

    if (factors.landOwnership !== 'owned') {
      recommendations.push({
        action: 'وثق ملكية الأرض لزيادة تصنيفك',
        impact: 35,
        priority: 'high',
        category: 'verification',
      });
    }

    if (factors.cropDiversity < 3) {
      recommendations.push({
        action: 'زد من تنوع المحاصيل (حاليًا: ' + factors.cropDiversity + ' محاصيل)',
        impact: 12,
        priority: 'low',
        category: 'farming',
      });
    }

    if (factors.irrigationType === 'rainfed' || factors.irrigationType === 'flood') {
      recommendations.push({
        action: 'حسّن نظام الري إلى الري بالتنقيط أو الرش',
        impact: 25,
        priority: 'medium',
        category: 'farming',
      });
    }

    if (factors.loanRepaymentRate < 90 && factors.loanRepaymentRate > 0) {
      recommendations.push({
        action: 'حافظ على سداد القروض في الوقت المحدد',
        impact: 20,
        priority: 'high',
        category: 'payment',
      });
    }

    recommendations.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      }
      return b.impact - a.impact;
    });

    return recommendations.slice(0, 5);
  }
}
