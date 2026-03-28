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
  ValidationPipe,
  Req,
  ForbiddenException,
} from "@nestjs/common";
import { Throttle } from "@nestjs/throttler";
import { MarketService } from "./market/market.service";
import { FintechService } from "./fintech/fintech.service";
import { PrismaService } from "./prisma/prisma.service";
import { EventsService } from "./events/events.service";
import { JwtAuthGuard } from "./auth/jwt-auth.guard";
import { Public } from "./auth/public.decorator";
import { SkipTenantCheck } from "./auth/tenant.guard";
import {
  CreateProductDto,
  CreateOrderDto,
  ListHarvestDto,
  CalculateCreditScoreDto,
  CalculateAdvancedCreditScoreDto,
  RecordCreditEventDto,
  RequestLoanDto,
  WalletTransactionDto,
} from "./dto/market.dto";

@Controller()
export class AppController {
  constructor(
    private readonly marketService: MarketService,
    private readonly fintechService: FintechService,
    private readonly prismaService: PrismaService,
    private readonly eventsService: EventsService,
  ) {}

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Check
  // ═══════════════════════════════════════════════════════════════════════════

  @Public()
  @SkipTenantCheck()
  @Throttle({ default: { limit: 10, ttl: 60000 } })
  @Get("healthz")
  healthCheck() {
    return {
      status: "ok",
      service: "marketplace-service",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
    };
  }

  @Public()
  @SkipTenantCheck()
  @Throttle({ default: { limit: 10, ttl: 60000 } })
  @Get("readyz")
  async readinessCheck() {
    const checks: Record<string, string> = {};

    // Check database connection
    try {
      await this.prismaService.$queryRaw`SELECT 1`;
      checks.database = "connected";
    } catch {
      checks.database = "disconnected";
    }

    // Check NATS connection
    const natsConfigured = !!process.env.NATS_URL;
    if (!natsConfigured) {
      checks.nats = "not_configured";
    } else {
      const eventsConnected = this.eventsService?.isConnected?.() ?? false;
      checks.nats = eventsConnected ? "connected" : "disconnected";
    }

    const allReady = Object.values(checks).every(v => v === "connected" || v === "not_configured");

    return {
      status: allReady ? "ready" : "degraded",
      service: "marketplace-service",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
      checks,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // السوق - Marketplace
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * جلب جميع المنتجات
   * GET /api/v1/market/products
   */
  @Get("market/products")
  async getProducts(
    @Req() req: any,
    @Query("category") category?: string,
    @Query("governorate") governorate?: string,
    @Query("sellerId") sellerId?: string,
    @Query("minPrice") minPrice?: string,
    @Query("maxPrice") maxPrice?: string,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.marketService.findAllProducts({
      category,
      governorate,
      sellerId,
      tenantId,
      minPrice: minPrice ? parseFloat(minPrice) : undefined,
      maxPrice: maxPrice ? parseFloat(maxPrice) : undefined,
    });
  }

  /**
   * جلب منتج بالمعرف
   * GET /api/v1/market/products/:id
   */
  @Get("market/products/:id")
  async getProduct(@Param("id") id: string) {
    return this.marketService.findProductById(id);
  }

  /**
   * إنشاء منتج جديد
   * POST /api/v1/market/products
   */
  @Post("market/products")
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.CREATED)
  async createProduct(
    @Req() req: any,
    @Body(ValidationPipe) body: CreateProductDto,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.marketService.createProduct(body, tenantId);
  }

  /**
   * ⭐ تحويل توقع الحصاد إلى منتج في السوق
   * POST /api/v1/market/list-harvest
   */
  @Post("market/list-harvest")
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.CREATED)
  async listHarvest(
    @Req() req: any,
    @Body(ValidationPipe) body: ListHarvestDto,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.marketService.convertYieldToProduct(
      body.userId,
      body.yieldData,
      tenantId,
    );
  }

  /**
   * إنشاء طلب شراء
   * POST /api/v1/market/orders
   */
  @Post("market/orders")
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.CREATED)
  async createOrder(
    @Req() req: any,
    @Body(ValidationPipe) body: CreateOrderDto,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.marketService.createOrder(body, tenantId);
  }

  /**
   * جلب طلبات المستخدم
   * GET /api/v1/market/orders/:userId
   */
  @Get("market/orders/:userId")
  @UseGuards(JwtAuthGuard)
  async getUserOrders(
    @Req() request: any,
    @Param("userId") userId: string,
    @Query("role") role: "buyer" | "seller" = "buyer",
  ) {
    // Resource ownership validation
    const authenticatedUser = request.user;
    const isAdmin = authenticatedUser.roles?.includes("admin");
    const isOwner = authenticatedUser.id === userId;

    if (!isOwner && !isAdmin) {
      throw new ForbiddenException(
        "You are not authorized to access orders for this user",
      );
    }

    return this.marketService.getUserOrders(userId, role);
  }

  /**
   * إحصائيات السوق
   * GET /api/v1/market/stats
   */
  @Get("market/stats")
  @UseGuards(JwtAuthGuard)
  async getMarketStats(@Req() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.marketService.getMarketStats(tenantId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // المحفظة والتمويل - Wallet & FinTech
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * جلب محفظة المستخدم
   * GET /api/v1/fintech/wallet/:userId
   */
  @Get("fintech/wallet/:userId")
  @UseGuards(JwtAuthGuard)
  async getWallet(
    @Param("userId") userId: string,
    @Query("userType") userType?: string,
  ) {
    return this.fintechService.getWallet(userId, userType);
  }

  /**
   * إيداع في المحفظة
   * POST /api/v1/fintech/wallet/:walletId/deposit
   */
  @Post("fintech/wallet/:walletId/deposit")
  @UseGuards(JwtAuthGuard)
  async deposit(
    @Param("walletId") walletId: string,
    @Body(ValidationPipe) body: WalletTransactionDto,
  ) {
    return this.fintechService.deposit(walletId, body.amount, body.description);
  }

  /**
   * سحب من المحفظة (مع رمز PIN للمبالغ الكبيرة)
   * POST /api/v1/fintech/wallet/:walletId/withdraw
   */
  @Post("fintech/wallet/:walletId/withdraw")
  @UseGuards(JwtAuthGuard)
  async withdraw(
    @Req() request: any,
    @Param("walletId") walletId: string,
    @Body(ValidationPipe) body: WalletTransactionDto & { pin?: string },
  ) {
    const authenticatedUser = request.user;
    return this.fintechService.withdraw(
      walletId,
      body.amount,
      body.description,
      undefined,
      authenticatedUser.id,
      request.ip,
      body.pin,
    );
  }

  /**
   * سجل المعاملات
   * GET /api/v1/fintech/wallet/:walletId/transactions
   */
  @Get("fintech/wallet/:walletId/transactions")
  @UseGuards(JwtAuthGuard)
  async getTransactions(
    @Param("walletId") walletId: string,
    @Query("limit") limit?: string,
  ) {
    const parsedLimit = Math.min(parseInt(limit ?? "20") || 20, 100);
    return this.fintechService.getTransactions(
      walletId,
      parsedLimit,
    );
  }

  /**
   * ⭐ حساب التصنيف الائتماني (الطريقة القديمة)
   * POST /api/v1/fintech/calculate-score
   */
  @Post("fintech/calculate-score")
  @UseGuards(JwtAuthGuard)
  async calculateCreditScore(
    @Req() req: any,
    @Body(ValidationPipe) body: CalculateCreditScoreDto,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.fintechService.calculateCreditScore(body.userId, body.farmData, tenantId);
  }

  /**
   * ⭐ حساب التصنيف الائتماني المتقدم (جديد)
   * POST /api/v1/fintech/calculate-advanced-score
   */
  @Post("fintech/calculate-advanced-score")
  @UseGuards(JwtAuthGuard)
  async calculateAdvancedCreditScore(
    @Req() req: any,
    @Body(ValidationPipe) body: CalculateAdvancedCreditScoreDto,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.fintechService.calculateAdvancedCreditScore(
      body.userId,
      body.factors,
      tenantId,
    );
  }

  /**
   * جلب عوامل التصنيف الائتماني
   * GET /api/v1/fintech/credit-factors/:userId
   */
  @Get("fintech/credit-factors/:userId")
  @UseGuards(JwtAuthGuard)
  async getCreditFactors(@Param("userId") userId: string) {
    return this.fintechService.getCreditFactors(userId);
  }

  /**
   * تسجيل حدث ائتماني
   * POST /api/v1/fintech/credit-history
   */
  @Post("fintech/credit-history")
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.CREATED)
  async recordCreditEvent(
    @Req() req: any,
    @Body(ValidationPipe) body: RecordCreditEventDto,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.fintechService.recordCreditEvent(body, tenantId);
  }

  /**
   * جلب التقرير الائتماني الكامل
   * GET /api/v1/fintech/credit-report/:userId
   */
  @Get("fintech/credit-report/:userId")
  @UseGuards(JwtAuthGuard)
  async getCreditReport(@Param("userId") userId: string) {
    return this.fintechService.getCreditReport(userId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // القروض - Loans
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * طلب قرض جديد
   * POST /api/v1/fintech/loans
   */
  @Post("fintech/loans")
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.CREATED)
  async requestLoan(
    @Req() req: any,
    @Body(ValidationPipe) body: RequestLoanDto,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.fintechService.requestLoan(body, tenantId);
  }

  /**
   * الموافقة على القرض (للإدارة)
   * PUT /api/v1/fintech/loans/:id/approve
   */
  @Put("fintech/loans/:id/approve")
  @UseGuards(JwtAuthGuard)
  async approveLoan(@Param("id") id: string) {
    return this.fintechService.approveLoan(id);
  }

  /**
   * سداد القرض
   * POST /api/v1/fintech/loans/:id/repay
   */
  @Post("fintech/loans/:id/repay")
  @UseGuards(JwtAuthGuard)
  async repayLoan(@Param("id") id: string, @Body() body: { amount: number }) {
    return this.fintechService.repayLoan(id, body.amount);
  }

  /**
   * جلب قروض المستخدم
   * GET /api/v1/fintech/loans/:walletId
   */
  @Get("fintech/loans/:walletId")
  @UseGuards(JwtAuthGuard)
  async getUserLoans(@Param("walletId") walletId: string) {
    return this.fintechService.getUserLoans(walletId);
  }

  /**
   * إحصائيات التمويل
   * GET /api/v1/fintech/stats
   */
  @Get("fintech/stats")
  @UseGuards(JwtAuthGuard)
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
  @Get("fintech/wallet/:walletId/limits")
  @UseGuards(JwtAuthGuard)
  async getWalletLimits(@Param("walletId") walletId: string) {
    return this.fintechService.getWalletLimits(walletId);
  }

  /**
   * تحديث حدود المحفظة (بناءً على التصنيف الائتماني)
   * PUT /api/v1/fintech/wallet/:walletId/limits
   * Requires authentication and wallet ownership or admin role
   */
  @Put("fintech/wallet/:walletId/limits")
  @UseGuards(JwtAuthGuard)
  async updateWalletLimits(
    @Req() request: any,
    @Param("walletId") walletId: string,
  ) {
    // Verify wallet ownership or admin role
    const wallet = await this.fintechService.getWalletById(walletId);
    if (!wallet) {
      throw new ForbiddenException("Wallet not found");
    }

    const authenticatedUser = request.user;
    const isAdmin = authenticatedUser.roles?.includes("admin");
    const isOwner = authenticatedUser.id === wallet.userId;

    if (!isOwner && !isAdmin) {
      throw new ForbiddenException(
        "You are not authorized to update limits for this wallet",
      );
    }

    return this.fintechService.updateWalletLimits(walletId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // إدارة رمز PIN - PIN Management
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * تعيين رمز PIN للمحفظة
   * POST /api/v1/fintech/wallet/:walletId/set-pin
   */
  @Post("fintech/wallet/:walletId/set-pin")
  @UseGuards(JwtAuthGuard)
  async setPin(
    @Req() request: any,
    @Param("walletId") walletId: string,
    @Body() body: { pin: string },
  ) {
    const wallet = await this.fintechService.getWalletById(walletId);
    if (!wallet) {
      throw new ForbiddenException("Wallet not found");
    }

    const authenticatedUser = request.user;
    const isOwner = authenticatedUser.id === wallet.userId;

    if (!isOwner) {
      throw new ForbiddenException(
        "You are not authorized to set PIN for this wallet",
      );
    }

    return this.fintechService.setPin(walletId, body.pin, authenticatedUser.id);
  }

  /**
   * التحقق من رمز PIN
   * POST /api/v1/fintech/wallet/:walletId/verify-pin
   */
  @Post("fintech/wallet/:walletId/verify-pin")
  @UseGuards(JwtAuthGuard)
  async verifyPin(
    @Req() request: any,
    @Param("walletId") walletId: string,
    @Body() body: { pin: string },
  ) {
    const wallet = await this.fintechService.getWalletById(walletId);
    if (!wallet) {
      throw new ForbiddenException("Wallet not found");
    }

    const authenticatedUser = request.user;
    const isOwner = authenticatedUser.id === wallet.userId;

    if (!isOwner) {
      throw new ForbiddenException(
        "You are not authorized to verify PIN for this wallet",
      );
    }

    const valid = await this.fintechService.verifyPin(walletId, body.pin);
    return { valid };
  }

  /**
   * تغيير رمز PIN
   * POST /api/v1/fintech/wallet/:walletId/change-pin
   */
  @Post("fintech/wallet/:walletId/change-pin")
  @UseGuards(JwtAuthGuard)
  async changePin(
    @Req() request: any,
    @Param("walletId") walletId: string,
    @Body() body: { oldPin: string; newPin: string },
  ) {
    const wallet = await this.fintechService.getWalletById(walletId);
    if (!wallet) {
      throw new ForbiddenException("Wallet not found");
    }

    const authenticatedUser = request.user;
    const isOwner = authenticatedUser.id === wallet.userId;

    if (!isOwner) {
      throw new ForbiddenException(
        "You are not authorized to change PIN for this wallet",
      );
    }

    return this.fintechService.changePin(
      walletId,
      body.oldPin,
      body.newPin,
      authenticatedUser.id,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الإسكرو - Escrow
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء إسكرو جديد
   * POST /api/v1/fintech/escrow
   */
  @Post("fintech/escrow")
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
  @Post("fintech/escrow/:id/release")
  @UseGuards(JwtAuthGuard)
  async releaseEscrow(
    @Param("id") id: string,
    @Body() body: { notes?: string },
  ) {
    return this.fintechService.releaseEscrow(id, body.notes);
  }

  /**
   * استرداد الإسكرو للمشتري
   * POST /api/v1/fintech/escrow/:id/refund
   */
  @Post("fintech/escrow/:id/refund")
  @UseGuards(JwtAuthGuard)
  async refundEscrow(
    @Param("id") id: string,
    @Body() body: { reason?: string },
  ) {
    return this.fintechService.refundEscrow(id, body.reason);
  }

  /**
   * فتح نزاع على الإسكرو
   * POST /api/v1/fintech/escrow/:id/dispute
   */
  @Post("fintech/escrow/:id/dispute")
  @UseGuards(JwtAuthGuard)
  async disputeEscrow(
    @Req() request: any,
    @Param("id") id: string,
    @Body() body: { reason: string },
  ) {
    const authenticatedUser = request.user;
    return this.fintechService.disputeEscrow(
      id,
      body.reason,
      authenticatedUser.id,
      request.ip,
    );
  }

  /**
   * حل النزاع (للإدارة فقط)
   * POST /api/v1/fintech/escrow/:id/resolve-dispute
   */
  @Post("fintech/escrow/:id/resolve-dispute")
  @UseGuards(JwtAuthGuard)
  async resolveDispute(
    @Req() request: any,
    @Param("id") id: string,
    @Body() body: { resolution: "release" | "refund"; adminNotes: string },
  ) {
    const authenticatedUser = request.user;
    const isAdmin = authenticatedUser.roles?.includes("admin");

    if (!isAdmin) {
      throw new ForbiddenException(
        "Only administrators can resolve escrow disputes",
      );
    }

    return this.fintechService.resolveDispute(
      id,
      body.resolution,
      body.adminNotes,
      authenticatedUser.id,
      request.ip,
    );
  }

  /**
   * الحصول على إسكرو بالطلب
   * GET /api/v1/fintech/escrow/order/:orderId
   */
  @Get("fintech/escrow/order/:orderId")
  @UseGuards(JwtAuthGuard)
  async getEscrowByOrder(@Param("orderId") orderId: string) {
    return this.fintechService.getEscrowByOrder(orderId);
  }

  /**
   * الحصول على جميع إسكرو المحفظة
   * GET /api/v1/fintech/wallet/:walletId/escrows
   */
  @Get("fintech/wallet/:walletId/escrows")
  @UseGuards(JwtAuthGuard)
  async getWalletEscrows(@Param("walletId") walletId: string) {
    return this.fintechService.getWalletEscrows(walletId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الدفعات المجدولة - Scheduled Payments
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إنشاء دفعة مجدولة
   * POST /api/v1/fintech/wallet/:walletId/scheduled-payment
   */
  @Post("fintech/wallet/:walletId/scheduled-payment")
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.CREATED)
  async createScheduledPayment(
    @Req() request: any,
    @Param("walletId") walletId: string,
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
    // Verify wallet ownership or admin role
    const wallet = await this.fintechService.getWalletById(walletId);
    if (!wallet) {
      throw new ForbiddenException("Wallet not found");
    }

    const authenticatedUser = request.user;
    const isAdmin = authenticatedUser.roles?.includes("admin");
    const isOwner = authenticatedUser.id === wallet.userId;

    if (!isOwner && !isAdmin) {
      throw new ForbiddenException(
        "You are not authorized to create scheduled payments for this wallet",
      );
    }

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
  @Get("fintech/wallet/:walletId/scheduled-payments")
  async getScheduledPayments(
    @Param("walletId") walletId: string,
    @Query("activeOnly") activeOnly?: string,
  ) {
    return this.fintechService.getScheduledPayments(
      walletId,
      activeOnly !== "false",
    );
  }

  /**
   * إلغاء دفعة مجدولة
   * POST /api/v1/fintech/scheduled-payment/:id/cancel
   */
  @Post("fintech/scheduled-payment/:id/cancel")
  @UseGuards(JwtAuthGuard)
  async cancelScheduledPayment(@Req() request: any, @Param("id") id: string) {
    // Verify scheduled payment ownership or admin role
    const scheduledPayment = await this.fintechService.getScheduledPaymentById(id);
    if (!scheduledPayment) {
      throw new ForbiddenException("Scheduled payment not found");
    }

    const authenticatedUser = request.user;
    const isAdmin = authenticatedUser.roles?.includes("admin");
    const isOwner = authenticatedUser.id === scheduledPayment.wallet?.userId;

    if (!isOwner && !isAdmin) {
      throw new ForbiddenException(
        "You are not authorized to cancel this scheduled payment",
      );
    }

    return this.fintechService.cancelScheduledPayment(id);
  }

  /**
   * تنفيذ دفعة مجدولة
   * POST /api/v1/fintech/scheduled-payment/:id/execute
   */
  @Post("fintech/scheduled-payment/:id/execute")
  @UseGuards(JwtAuthGuard)
  async executeScheduledPayment(@Req() request: any, @Param("id") id: string) {
    // Verify scheduled payment ownership or admin role
    const scheduledPayment = await this.fintechService.getScheduledPaymentById(id);
    if (!scheduledPayment) {
      throw new ForbiddenException("Scheduled payment not found");
    }

    const authenticatedUser = request.user;
    const isAdmin = authenticatedUser.roles?.includes("admin");
    const isOwner = authenticatedUser.id === scheduledPayment.wallet?.userId;

    if (!isOwner && !isAdmin) {
      throw new ForbiddenException(
        "You are not authorized to execute this scheduled payment",
      );
    }

    return this.fintechService.executeScheduledPayment(id);
  }

  /**
   * معالجة الدفعات المستحقة (للإدارة)
   * POST /api/v1/fintech/scheduled-payments/process-due
   */
  @Post("fintech/scheduled-payments/process-due")
  @UseGuards(JwtAuthGuard)
  async processDuePayments(@Req() request: any) {
    const authenticatedUser = request.user;
    const isAdmin = authenticatedUser.roles?.includes("admin");

    if (!isAdmin) {
      throw new ForbiddenException(
        "Only administrators can trigger payment processing",
      );
    }

    return this.fintechService.processDuePayments();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // لوحة تحكم المحفظة - Wallet Dashboard
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * الحصول على لوحة تحكم المحفظة
   * GET /api/v1/fintech/wallet/:walletId/dashboard
   */
  @Get("fintech/wallet/:walletId/dashboard")
  @UseGuards(JwtAuthGuard)
  async getWalletDashboard(@Param("walletId") walletId: string) {
    return this.fintechService.getWalletDashboard(walletId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // التحويلات - Wallet Transfers
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * تحويل بين المحافظ
   * POST /api/v1/fintech/wallet/transfer
   */
  @Post("fintech/wallet/transfer")
  @UseGuards(JwtAuthGuard)
  async transfer(
    @Req() request: any,
    @Body()
    body: {
      fromWalletId: string;
      toWalletId: string;
      amount: number;
      description?: string;
      pin?: string;
    },
  ) {
    // Verify sender wallet ownership
    const wallet = await this.fintechService.getWalletById(body.fromWalletId);
    if (!wallet) {
      throw new ForbiddenException("Sender wallet not found");
    }

    const authenticatedUser = request.user;
    const isOwner = authenticatedUser.id === wallet.userId;

    if (!isOwner) {
      throw new ForbiddenException(
        "You are not authorized to transfer from this wallet",
      );
    }

    return this.fintechService.transfer(
      body.fromWalletId,
      body.toWalletId,
      body.amount,
      body.description,
      undefined,
      authenticatedUser.id,
      request.ip,
      body.pin,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // تجميد المحفظة - Wallet Freeze (Admin Only)
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * تجميد محفظة (للإدارة فقط)
   * POST /api/v1/fintech/wallet/:walletId/freeze
   */
  @Post("fintech/wallet/:walletId/freeze")
  @UseGuards(JwtAuthGuard)
  async freezeWallet(
    @Req() request: any,
    @Param("walletId") walletId: string,
    @Body() body: { reason?: string },
  ) {
    const authenticatedUser = request.user;
    const isAdmin = authenticatedUser.roles?.includes("admin");

    if (!isAdmin) {
      throw new ForbiddenException(
        "Only administrators can freeze wallets",
      );
    }

    return this.fintechService.freezeWallet(
      walletId,
      authenticatedUser.id,
      body.reason,
    );
  }

  /**
   * إلغاء تجميد محفظة (للإدارة فقط)
   * POST /api/v1/fintech/wallet/:walletId/unfreeze
   */
  @Post("fintech/wallet/:walletId/unfreeze")
  @UseGuards(JwtAuthGuard)
  async unfreezeWallet(
    @Req() request: any,
    @Param("walletId") walletId: string,
    @Body() body: { reason?: string },
  ) {
    const authenticatedUser = request.user;
    const isAdmin = authenticatedUser.roles?.includes("admin");

    if (!isAdmin) {
      throw new ForbiddenException(
        "Only administrators can unfreeze wallets",
      );
    }

    return this.fintechService.unfreezeWallet(
      walletId,
      authenticatedUser.id,
      body.reason,
    );
  }
}
