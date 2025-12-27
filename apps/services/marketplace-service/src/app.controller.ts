/**
 * SAHOOL Marketplace & FinTech API Controller
 * وحدة التحكم في واجهة برمجة التطبيقات
 */

import {
  Controller,
  Get,
  Post,
  Put,
  Body,
  Param,
  Query,
  HttpCode,
  HttpStatus,
  UseGuards,
} from '@nestjs/common';
import { MarketService } from './market/market.service';
import { FintechService } from './fintech/fintech.service';
import { JwtAuthGuard } from './auth/jwt-auth.guard';

@Controller()
export class AppController {
  constructor(
    private readonly marketService: MarketService,
    private readonly fintechService: FintechService,
  ) {}

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Check
  // ═══════════════════════════════════════════════════════════════════════════

  @Get('healthz')
  healthCheck() {
    return {
      status: 'ok',
      service: 'marketplace-service',
      version: '15.3.0',
      timestamp: new Date().toISOString(),
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // السوق - Marketplace
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * جلب جميع المنتجات
   * GET /api/v1/market/products
   */
  @Get('market/products')
  async getProducts(
    @Query('category') category?: string,
    @Query('governorate') governorate?: string,
    @Query('sellerId') sellerId?: string,
    @Query('minPrice') minPrice?: string,
    @Query('maxPrice') maxPrice?: string,
  ) {
    return this.marketService.findAllProducts({
      category,
      governorate,
      sellerId,
      minPrice: minPrice ? parseFloat(minPrice) : undefined,
      maxPrice: maxPrice ? parseFloat(maxPrice) : undefined,
    });
  }

  /**
   * جلب منتج بالمعرف
   * GET /api/v1/market/products/:id
   */
  @Get('market/products/:id')
  async getProduct(@Param('id') id: string) {
    return this.marketService.findProductById(id);
  }

  /**
   * إنشاء منتج جديد
   * POST /api/v1/market/products
   */
  @Post('market/products')
  @HttpCode(HttpStatus.CREATED)
  async createProduct(@Body() body: any) {
    return this.marketService.createProduct(body);
  }

  /**
   * ⭐ تحويل توقع الحصاد إلى منتج في السوق
   * POST /api/v1/market/list-harvest
   */
  @Post('market/list-harvest')
  @HttpCode(HttpStatus.CREATED)
  async listHarvest(@Body() body: { userId: string; yieldData: any }) {
    return this.marketService.convertYieldToProduct(body.userId, body.yieldData);
  }

  /**
   * إنشاء طلب شراء
   * POST /api/v1/market/orders
   */
  @Post('market/orders')
  @HttpCode(HttpStatus.CREATED)
  async createOrder(@Body() body: any) {
    return this.marketService.createOrder(body);
  }

  /**
   * جلب طلبات المستخدم
   * GET /api/v1/market/orders/:userId
   */
  @Get('market/orders/:userId')
  async getUserOrders(
    @Param('userId') userId: string,
    @Query('role') role: 'buyer' | 'seller' = 'buyer',
  ) {
    return this.marketService.getUserOrders(userId, role);
  }

  /**
   * إحصائيات السوق
   * GET /api/v1/market/stats
   */
  @Get('market/stats')
  async getMarketStats() {
    return this.marketService.getMarketStats();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // المحفظة والتمويل - Wallet & FinTech
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * جلب محفظة المستخدم
   * GET /api/v1/fintech/wallet/:userId
   */
  @Get('fintech/wallet/:userId')
  async getWallet(
    @Param('userId') userId: string,
    @Query('userType') userType?: string,
  ) {
    return this.fintechService.getWallet(userId, userType);
  }

  /**
   * إيداع في المحفظة
   * POST /api/v1/fintech/wallet/:walletId/deposit
   */
  @Post('fintech/wallet/:walletId/deposit')
  async deposit(
    @Param('walletId') walletId: string,
    @Body() body: { amount: number; description?: string },
  ) {
    return this.fintechService.deposit(walletId, body.amount, body.description);
  }

  /**
   * سحب من المحفظة
   * POST /api/v1/fintech/wallet/:walletId/withdraw
   */
  @Post('fintech/wallet/:walletId/withdraw')
  async withdraw(
    @Param('walletId') walletId: string,
    @Body() body: { amount: number; description?: string },
  ) {
    return this.fintechService.withdraw(walletId, body.amount, body.description);
  }

  /**
   * سجل المعاملات
   * GET /api/v1/fintech/wallet/:walletId/transactions
   */
  @Get('fintech/wallet/:walletId/transactions')
  async getTransactions(
    @Param('walletId') walletId: string,
    @Query('limit') limit?: string,
  ) {
    return this.fintechService.getTransactions(
      walletId,
      limit ? parseInt(limit) : 20,
    );
  }

  /**
   * ⭐ حساب التصنيف الائتماني (الطريقة القديمة)
   * POST /api/v1/fintech/calculate-score
   */
  @Post('fintech/calculate-score')
  async calculateCreditScore(@Body() body: { userId: string; farmData: any }) {
    return this.fintechService.calculateCreditScore(body.userId, body.farmData);
  }

  /**
   * ⭐ حساب التصنيف الائتماني المتقدم (جديد)
   * POST /api/v1/fintech/calculate-advanced-score
   */
  @Post('fintech/calculate-advanced-score')
  async calculateAdvancedCreditScore(
    @Body() body: { userId: string; factors: any },
  ) {
    return this.fintechService.calculateAdvancedCreditScore(
      body.userId,
      body.factors,
    );
  }

  /**
   * جلب عوامل التصنيف الائتماني
   * GET /api/v1/fintech/credit-factors/:userId
   */
  @Get('fintech/credit-factors/:userId')
  async getCreditFactors(@Param('userId') userId: string) {
    return this.fintechService.getCreditFactors(userId);
  }

  /**
   * تسجيل حدث ائتماني
   * POST /api/v1/fintech/credit-history
   */
  @Post('fintech/credit-history')
  @HttpCode(HttpStatus.CREATED)
  async recordCreditEvent(@Body() body: any) {
    return this.fintechService.recordCreditEvent(body);
  }

  /**
   * جلب التقرير الائتماني الكامل
   * GET /api/v1/fintech/credit-report/:userId
   */
  @Get('fintech/credit-report/:userId')
  async getCreditReport(@Param('userId') userId: string) {
    return this.fintechService.getCreditReport(userId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // القروض - Loans
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * طلب قرض جديد
   * POST /api/v1/fintech/loans
   */
  @Post('fintech/loans')
  @HttpCode(HttpStatus.CREATED)
  async requestLoan(@Body() body: any) {
    return this.fintechService.requestLoan(body);
  }

  /**
   * الموافقة على القرض (للإدارة)
   * PUT /api/v1/fintech/loans/:id/approve
   */
  @Put('fintech/loans/:id/approve')
  @UseGuards(JwtAuthGuard)
  async approveLoan(@Param('id') id: string) {
    return this.fintechService.approveLoan(id);
  }

  /**
   * سداد القرض
   * POST /api/v1/fintech/loans/:id/repay
   */
  @Post('fintech/loans/:id/repay')
  @UseGuards(JwtAuthGuard)
  async repayLoan(@Param('id') id: string, @Body() body: { amount: number }) {
    return this.fintechService.repayLoan(id, body.amount);
  }

  /**
   * جلب قروض المستخدم
   * GET /api/v1/fintech/loans/:walletId
   */
  @Get('fintech/loans/:walletId')
  async getUserLoans(@Param('walletId') walletId: string) {
    return this.fintechService.getUserLoans(walletId);
  }

  /**
   * إحصائيات التمويل
   * GET /api/v1/fintech/stats
   */
  @Get('fintech/stats')
  async getFinanceStats() {
    return this.fintechService.getFinanceStats();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // حدود المحفظة - Wallet Limits
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * الحصول على حدود المحفظة
   * GET /api/v1/fintech/wallet/:walletId/limits
   */
  @Get('fintech/wallet/:walletId/limits')
  async getWalletLimits(@Param('walletId') walletId: string) {
    return this.fintechService.getWalletLimits(walletId);
  }

  /**
   * تحديث حدود المحفظة (بناءً على التصنيف الائتماني)
   * PUT /api/v1/fintech/wallet/:walletId/limits
   */
  @Put('fintech/wallet/:walletId/limits')
  async updateWalletLimits(@Param('walletId') walletId: string) {
    return this.fintechService.updateWalletLimits(walletId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الإسكرو - Escrow
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء إسكرو جديد
   * POST /api/v1/fintech/escrow
   */
  @Post('fintech/escrow')
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.CREATED)
  async createEscrow(
    @Body()
    body: {
      orderId: string;
      buyerWalletId: string;
      sellerWalletId: string;
      amount: number;
      notes?: string;
    },
  ) {
    return this.fintechService.createEscrow(
      body.orderId,
      body.buyerWalletId,
      body.sellerWalletId,
      body.amount,
      body.notes,
    );
  }

  /**
   * إطلاق الإسكرو للبائع
   * POST /api/v1/fintech/escrow/:id/release
   */
  @Post('fintech/escrow/:id/release')
  @UseGuards(JwtAuthGuard)
  async releaseEscrow(
    @Param('id') id: string,
    @Body() body: { notes?: string },
  ) {
    return this.fintechService.releaseEscrow(id, body.notes);
  }

  /**
   * استرداد الإسكرو للمشتري
   * POST /api/v1/fintech/escrow/:id/refund
   */
  @Post('fintech/escrow/:id/refund')
  @UseGuards(JwtAuthGuard)
  async refundEscrow(
    @Param('id') id: string,
    @Body() body: { reason?: string },
  ) {
    return this.fintechService.refundEscrow(id, body.reason);
  }

  /**
   * الحصول على إسكرو بالطلب
   * GET /api/v1/fintech/escrow/order/:orderId
   */
  @Get('fintech/escrow/order/:orderId')
  async getEscrowByOrder(@Param('orderId') orderId: string) {
    return this.fintechService.getEscrowByOrder(orderId);
  }

  /**
   * الحصول على جميع إسكرو المحفظة
   * GET /api/v1/fintech/wallet/:walletId/escrows
   */
  @Get('fintech/wallet/:walletId/escrows')
  async getWalletEscrows(@Param('walletId') walletId: string) {
    return this.fintechService.getWalletEscrows(walletId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الدفعات المجدولة - Scheduled Payments
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء دفعة مجدولة
   * POST /api/v1/fintech/wallet/:walletId/scheduled-payment
   */
  @Post('fintech/wallet/:walletId/scheduled-payment')
  @HttpCode(HttpStatus.CREATED)
  async createScheduledPayment(
    @Param('walletId') walletId: string,
    @Body()
    body: {
      amount: number;
      frequency: string;
      nextPaymentDate: string;
      loanId?: string;
      description?: string;
      descriptionAr?: string;
    },
  ) {
    return this.fintechService.createScheduledPayment(
      walletId,
      body.amount,
      body.frequency,
      new Date(body.nextPaymentDate),
      body.loanId,
      body.description,
      body.descriptionAr,
    );
  }

  /**
   * الحصول على الدفعات المجدولة للمحفظة
   * GET /api/v1/fintech/wallet/:walletId/scheduled-payments
   */
  @Get('fintech/wallet/:walletId/scheduled-payments')
  async getScheduledPayments(
    @Param('walletId') walletId: string,
    @Query('activeOnly') activeOnly?: string,
  ) {
    return this.fintechService.getScheduledPayments(
      walletId,
      activeOnly !== 'false',
    );
  }

  /**
   * إلغاء دفعة مجدولة
   * POST /api/v1/fintech/scheduled-payment/:id/cancel
   */
  @Post('fintech/scheduled-payment/:id/cancel')
  async cancelScheduledPayment(@Param('id') id: string) {
    return this.fintechService.cancelScheduledPayment(id);
  }

  /**
   * تنفيذ دفعة مجدولة
   * POST /api/v1/fintech/scheduled-payment/:id/execute
   */
  @Post('fintech/scheduled-payment/:id/execute')
  async executeScheduledPayment(@Param('id') id: string) {
    return this.fintechService.executeScheduledPayment(id);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // لوحة تحكم المحفظة - Wallet Dashboard
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * الحصول على لوحة تحكم المحفظة
   * GET /api/v1/fintech/wallet/:walletId/dashboard
   */
  @Get('fintech/wallet/:walletId/dashboard')
  async getWalletDashboard(@Param('walletId') walletId: string) {
    return this.fintechService.getWalletDashboard(walletId);
  }
}
