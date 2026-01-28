/**
 * SAHOOL FinTech Service (Facade)
 * خدمة التمويل الزراعي - واجهة موحدة
 *
 * This service acts as a facade for the modular FinTech services:
 * - WalletService: Digital wallet management
 * - CreditService: Credit scoring based on farm data & activity
 * - LoanService: Agricultural loans (Islamic finance compatible)
 * - EscrowService: Marketplace transaction protection
 *
 * @version 16.0.0
 */

import { Injectable } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { WalletService } from "./wallet.service";
import {
  CreditService,
  FarmData,
  CreditFactors,
  CreditReport,
} from "./credit.service";
import { LoanService } from "./loan.service";
import { EscrowService } from "./escrow.service";

// Re-export types for backward compatibility
export { FarmData, CreditFactors, CreditReport } from "./credit.service";
export { CreditRecommendation } from "./credit.service";

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
  constructor(
    private prisma: PrismaService,
    private walletService: WalletService,
    private creditService: CreditService,
    private loanService: LoanService,
    private escrowService: EscrowService,
  ) {}

  // ═══════════════════════════════════════════════════════════════════════════
  // المحفظة - Wallet (delegated to WalletService)
  // ═══════════════════════════════════════════════════════════════════════════

  async getWallet(userId: string, userType: string = "farmer") {
    return this.walletService.getWallet(userId, userType);
  }

  async deposit(
    walletId: string,
    amount: number,
    description?: string,
    idempotencyKey?: string,
    userId?: string,
    ipAddress?: string,
  ) {
    return this.walletService.deposit(
      walletId,
      amount,
      description,
      idempotencyKey,
      userId,
      ipAddress,
    );
  }

  async withdraw(
    walletId: string,
    amount: number,
    description?: string,
    idempotencyKey?: string,
    userId?: string,
    ipAddress?: string,
  ) {
    return this.walletService.withdraw(
      walletId,
      amount,
      description,
      idempotencyKey,
      userId,
      ipAddress,
    );
  }

  async getTransactions(walletId: string, limit: number = 20) {
    return this.walletService.getTransactions(walletId, limit);
  }

  async getWalletLimits(walletId: string) {
    return this.walletService.getWalletLimits(walletId);
  }

  async updateWalletLimits(walletId: string) {
    return this.walletService.updateWalletLimits(walletId);
  }

  async getWalletDashboard(walletId: string) {
    return this.walletService.getWalletDashboard(walletId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // التصنيف الائتماني - Credit Scoring (delegated to CreditService)
  // ═══════════════════════════════════════════════════════════════════════════

  async calculateCreditScore(userId: string, farmData: FarmData) {
    return this.creditService.calculateCreditScore(userId, farmData);
  }

  async calculateAdvancedCreditScore(userId: string, factors: CreditFactors) {
    return this.creditService.calculateAdvancedCreditScore(userId, factors);
  }

  async getCreditFactors(userId: string): Promise<CreditFactors> {
    return this.creditService.getCreditFactors(userId);
  }

  async recordCreditEvent(data: RecordCreditEventDto) {
    return this.creditService.recordCreditEvent(data);
  }

  async getCreditReport(userId: string): Promise<CreditReport> {
    return this.creditService.getCreditReport(userId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // القروض - Loans (delegated to LoanService)
  // ═══════════════════════════════════════════════════════════════════════════

  async requestLoan(data: CreateLoanDto) {
    return this.loanService.requestLoan(data);
  }

  async approveLoan(loanId: string) {
    return this.loanService.approveLoan(loanId);
  }

  async repayLoan(
    loanId: string,
    amount: number,
    idempotencyKey?: string,
    userId?: string,
    ipAddress?: string,
  ) {
    return this.loanService.repayLoan(
      loanId,
      amount,
      idempotencyKey,
      userId,
      ipAddress,
    );
  }

  async getUserLoans(walletId: string) {
    return this.loanService.getUserLoans(walletId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الدفعات المجدولة - Scheduled Payments (delegated to LoanService)
  // ═══════════════════════════════════════════════════════════════════════════

  async createScheduledPayment(
    walletId: string,
    amount: number,
    frequency: string,
    nextPaymentDate: Date,
    loanId?: string,
    description?: string,
    descriptionAr?: string,
  ) {
    return this.loanService.createScheduledPayment(
      walletId,
      amount,
      frequency,
      nextPaymentDate,
      loanId,
      description,
      descriptionAr,
    );
  }

  async getScheduledPayments(walletId: string, activeOnly: boolean = true) {
    return this.loanService.getScheduledPayments(walletId, activeOnly);
  }

  async cancelScheduledPayment(paymentId: string) {
    return this.loanService.cancelScheduledPayment(paymentId);
  }

  async executeScheduledPayment(paymentId: string) {
    return this.loanService.executeScheduledPayment(paymentId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الإسكرو - Escrow (delegated to EscrowService)
  // ═══════════════════════════════════════════════════════════════════════════

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
    return this.escrowService.createEscrow(
      orderId,
      buyerWalletId,
      sellerWalletId,
      amount,
      notes,
      idempotencyKey,
      userId,
      ipAddress,
    );
  }

  async releaseEscrow(
    escrowId: string,
    notes?: string,
    idempotencyKey?: string,
    userId?: string,
    ipAddress?: string,
  ) {
    return this.escrowService.releaseEscrow(
      escrowId,
      notes,
      idempotencyKey,
      userId,
      ipAddress,
    );
  }

  async refundEscrow(
    escrowId: string,
    reason?: string,
    idempotencyKey?: string,
    userId?: string,
    ipAddress?: string,
  ) {
    return this.escrowService.refundEscrow(
      escrowId,
      reason,
      idempotencyKey,
      userId,
      ipAddress,
    );
  }

  async getEscrowByOrder(orderId: string) {
    return this.escrowService.getEscrowByOrder(orderId);
  }

  async getWalletEscrows(walletId: string) {
    return this.escrowService.getWalletEscrows(walletId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الإحصائيات - Statistics
  // ═══════════════════════════════════════════════════════════════════════════

  async getFinanceStats() {
    const [totalWallets, totalBalance, activeLoans, paidLoans] =
      await Promise.all([
        this.prisma.wallet.count(),
        this.prisma.wallet.aggregate({ _sum: { balance: true } }),
        this.prisma.loan.count({ where: { status: "ACTIVE" } }),
        this.prisma.loan.count({ where: { status: "PAID" } }),
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
  // Helper Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * الحصول على ترجمة التصنيف الائتماني
   */
  getCreditTierAr(tier: string): string {
    return this.walletService.getCreditTierAr(tier);
  }

  /**
   * ترجمة غرض القرض
   */
  getLoanPurposeAr(purpose: string): string {
    return this.loanService.getLoanPurposeAr(purpose);
  }
}
