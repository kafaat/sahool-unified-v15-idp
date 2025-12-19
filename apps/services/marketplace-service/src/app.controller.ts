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
} from '@nestjs/common';
import { MarketService } from './market/market.service';
import { FintechService } from './fintech/fintech.service';

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
   * ⭐ حساب التصنيف الائتماني
   * POST /api/v1/fintech/calculate-score
   */
  @Post('fintech/calculate-score')
  async calculateCreditScore(@Body() body: { userId: string; farmData: any }) {
    return this.fintechService.calculateCreditScore(body.userId, body.farmData);
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
  async approveLoan(@Param('id') id: string) {
    return this.fintechService.approveLoan(id);
  }

  /**
   * سداد القرض
   * POST /api/v1/fintech/loans/:id/repay
   */
  @Post('fintech/loans/:id/repay')
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
}
