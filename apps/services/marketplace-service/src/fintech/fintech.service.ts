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
import { IdempotencyService } from "./idempotency.service";

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
    private idempotencyService: IdempotencyService,
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
    description: string | undefined,
    idempotencyKey: string | undefined,
    userId: string | undefined,
    ipAddress: string | undefined,
    tenantId: string,
    currency?: string,
  ) {
    // Wrap in the idempotency cache so a retry with the same
    // `Idempotency-Key` header returns the exact same response body.
    // The wallet-level uniqueness constraint on `transactions.idempotency_key`
    // still provides a second line of defence inside the SQL transaction.
    const effectiveUser = userId ?? "system";
    const result = await this.idempotencyService.executeIdempotent(
      idempotencyKey,
      tenantId,
      effectiveUser,
      "wallet.deposit",
      { walletId, amount, description, currency },
      () =>
        this.walletService.deposit(
          walletId,
          amount,
          description,
          idempotencyKey,
          userId,
          ipAddress,
          tenantId,
        ),
    );
    return result.value;
  }

  async withdraw(
    walletId: string,
    amount: number,
    description: string | undefined,
    idempotencyKey: string | undefined,
    userId: string | undefined,
    ipAddress: string | undefined,
    pin: string | undefined,
    tenantId: string,
    currency?: string,
  ) {
    const effectiveUser = userId ?? "system";
    const result = await this.idempotencyService.executeIdempotent(
      idempotencyKey,
      tenantId,
      effectiveUser,
      "wallet.withdraw",
      { walletId, amount, description, currency },
      () =>
        this.walletService.withdraw(
          walletId,
          amount,
          description,
          idempotencyKey,
          userId,
          ipAddress,
          pin,
          tenantId,
        ),
    );
    return result.value;
  }

  async transfer(
    fromWalletId: string,
    toWalletId: string,
    amount: number,
    description: string | undefined,
    idempotencyKey: string | undefined,
    userId: string | undefined,
    ipAddress: string | undefined,
    pin: string | undefined,
    tenantId: string,
    currency?: string,
  ) {
    const effectiveUser = userId ?? "system";
    const result = await this.idempotencyService.executeIdempotent(
      idempotencyKey,
      tenantId,
      effectiveUser,
      "wallet.transfer",
      { fromWalletId, toWalletId, amount, description, currency },
      () =>
        this.walletService.transfer(
          fromWalletId,
          toWalletId,
          amount,
          description,
          idempotencyKey,
          userId,
          ipAddress,
          pin,
          tenantId,
        ),
    );
    return result.value;
  }

  async getTransactions(walletId: string, tenantId: string, limit: number = 20) {
    return this.walletService.getTransactions(walletId, tenantId, limit);
  }

  async getWalletLimits(walletId: string, tenantId: string) {
    return this.walletService.getWalletLimits(walletId, tenantId);
  }

  async updateWalletLimits(walletId: string, tenantId: string) {
    return this.walletService.updateWalletLimits(walletId, tenantId);
  }

  /**
   * Get wallet by ID for authorization checks
   * Returns wallet with userId for ownership verification
   */
  async getWalletById(walletId: string, tenantId: string) {
    return this.prisma.wallet.findUnique({
      where: { id_tenantId: { id: walletId, tenantId } },
      select: { id: true, userId: true, tenantId: true },
    });
  }

  async getWalletDashboard(walletId: string, tenantId: string) {
    return this.walletService.getWalletDashboard(walletId, tenantId);
  }

  // PIN Management
  async setPin(walletId: string, pin: string, tenantId: string, userId?: string) {
    return this.walletService.setPin(walletId, pin, tenantId, userId);
  }

  async verifyPin(walletId: string, pin: string, tenantId: string) {
    return this.walletService.verifyPin(walletId, pin, tenantId);
  }

  async changePin(
    walletId: string,
    oldPin: string,
    newPin: string,
    tenantId: string,
    userId?: string,
  ) {
    return this.walletService.changePin(walletId, oldPin, newPin, tenantId, userId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // التصنيف الائتماني - Credit Scoring (delegated to CreditService)
  // ═══════════════════════════════════════════════════════════════════════════

  async calculateCreditScore(userId: string, farmData: FarmData, tenantId?: string) {
    return this.creditService.calculateCreditScore(userId, farmData);
  }

  async calculateAdvancedCreditScore(userId: string, factors: CreditFactors, tenantId?: string) {
    return this.creditService.calculateAdvancedCreditScore(userId, factors);
  }

  async getCreditFactors(userId: string): Promise<CreditFactors> {
    return this.creditService.getCreditFactors(userId);
  }

  async recordCreditEvent(data: RecordCreditEventDto, tenantId: string) {
    return this.creditService.recordCreditEvent(data, tenantId);
  }

  async getCreditReport(userId: string): Promise<CreditReport> {
    return this.creditService.getCreditReport(userId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // القروض - Loans (delegated to LoanService)
  // ═══════════════════════════════════════════════════════════════════════════

  async requestLoan(data: CreateLoanDto, tenantId: string) {
    return this.loanService.requestLoan(data, tenantId);
  }

  async approveLoan(loanId: string, tenantId: string) {
    return this.loanService.approveLoan(loanId, tenantId);
  }

  async repayLoan(
    loanId: string,
    amount: number,
    tenantId: string,
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
      tenantId,
    );
  }

  async getUserLoans(walletId: string, tenantId: string) {
    return this.loanService.getUserLoans(walletId, tenantId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الدفعات المجدولة - Scheduled Payments (delegated to LoanService)
  // ═══════════════════════════════════════════════════════════════════════════

  async createScheduledPayment(
    walletId: string,
    amount: number,
    frequency: string,
    nextPaymentDate: Date,
    tenantId: string,
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
      tenantId,
    );
  }

  async getScheduledPayments(walletId: string, tenantId: string, activeOnly: boolean = true) {
    return this.loanService.getScheduledPayments(walletId, tenantId, activeOnly);
  }

  async cancelScheduledPayment(paymentId: string, tenantId: string) {
    return this.loanService.cancelScheduledPayment(paymentId, tenantId);
  }

  async executeScheduledPayment(paymentId: string, tenantId: string) {
    return this.loanService.executeScheduledPayment(paymentId, tenantId);
  }

  async processDuePayments() {
    return this.loanService.processDuePayments();
  }

  /**
   * Get scheduled payment by ID for authorization checks
   * Returns payment with wallet info for ownership verification
   */
  async getScheduledPaymentById(paymentId: string, tenantId: string) {
    return this.prisma.scheduledPayment.findUnique({
      where: { id_tenantId: { id: paymentId, tenantId } },
      select: {
        id: true,
        walletId: true,
        wallet: {
          select: { userId: true },
        },
      },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الإسكرو - Escrow (delegated to EscrowService)
  // ═══════════════════════════════════════════════════════════════════════════

  async createEscrow(
    orderId: string,
    buyerWalletId: string,
    sellerWalletId: string,
    amount: number,
    tenantId: string,
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
      tenantId,
    );
  }

  async releaseEscrow(
    escrowId: string,
    tenantId: string,
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
      tenantId,
    );
  }

  async refundEscrow(
    escrowId: string,
    tenantId: string,
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
      tenantId,
    );
  }

  async disputeEscrow(
    escrowId: string,
    reason: string,
    tenantId: string,
    userId?: string,
    ipAddress?: string,
  ) {
    return this.escrowService.disputeEscrow(
      escrowId,
      reason,
      userId,
      ipAddress,
      tenantId,
    );
  }

  async resolveDispute(
    escrowId: string,
    resolution: "release" | "refund",
    adminNotes: string,
    tenantId: string,
    userId?: string,
    ipAddress?: string,
  ) {
    return this.escrowService.resolveDispute(
      escrowId,
      resolution,
      adminNotes,
      userId,
      ipAddress,
      tenantId,
    );
  }

  async getEscrowByOrder(orderId: string, tenantId: string) {
    return this.escrowService.getEscrowByOrder(orderId, tenantId);
  }

  async getWalletEscrows(walletId: string, tenantId: string) {
    return this.escrowService.getWalletEscrows(walletId, tenantId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الإحصائيات - Statistics
  // ═══════════════════════════════════════════════════════════════════════════

  async getFinanceStats(tenantId?: string) {
    const tenantFilter = tenantId ? { tenantId } : {};

    const [totalWallets, totalBalance, activeLoans, paidLoans] =
      await Promise.all([
        this.prisma.wallet.count({ where: { ...tenantFilter } }),
        this.prisma.wallet.aggregate({ where: { ...tenantFilter }, _sum: { balance: true } }),
        this.prisma.loan.count({ where: { status: "ACTIVE", ...tenantFilter } }),
        this.prisma.loan.count({ where: { status: "PAID", ...tenantFilter } }),
      ]);

    const avgCreditScore = await this.prisma.wallet.aggregate({
      where: { ...tenantFilter },
      _avg: { creditScore: true },
    });

    return {
      totalWallets,
      totalBalance: Number(totalBalance._sum.balance ?? 0),
      activeLoans,
      paidLoans,
      avgCreditScore: Math.round(avgCreditScore._avg.creditScore || 0),
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Helper Methods
  // ═══════════════════════════════════════════════════════════════════════════

  // Wallet Freeze/Unfreeze
  async freezeWallet(walletId: string, userId: string, tenantId: string, reason?: string) {
    return this.walletService.freezeWallet(walletId, userId, tenantId, reason);
  }

  async unfreezeWallet(walletId: string, userId: string, tenantId: string, reason?: string) {
    return this.walletService.unfreezeWallet(walletId, userId, tenantId, reason);
  }

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
