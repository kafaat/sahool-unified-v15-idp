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
  Headers,
  ForbiddenException,
  UnauthorizedException,
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
  WalletTransferDto,
} from "./dto/market.dto";

@Controller()
export class AppController {
  constructor(
    private readonly marketService: MarketService,
    private readonly fintechService: FintechService,
    private readonly prismaService: PrismaService,
    private readonly eventsService: EventsService,
  ) {}

  /**
   * Resolve the authenticated tenant id **strictly** from the JWT
   * (`tenant_id` claim, surfaced by JwtAuthGuard as `req.user.tenantId`).
   *
   * Used on money-moving endpoints where we must NOT trust the
   * `X-Tenant-Id` header. If the header fallback ever came back those
   * endpoints would be vulnerable to tenant-hopping attacks.
   */
  private requireTenantId(req: any): string {
    const tenantId: unknown = req?.user?.tenantId;
    if (typeof tenantId !== "string" || tenantId.length === 0) {
      throw new UnauthorizedException(
        "Missing tenant claim in authentication token",
      );
    }
    return tenantId;
  }

  /** Resolve the authenticated user id (JWT `sub`). */
  private requireUserId(req: any): string {
    const userId: unknown = req?.user?.id;
    if (typeof userId !== "string" || userId.length === 0) {
      throw new UnauthorizedException(
        "Missing user claim in authentication token",
      );
    }
    return userId;
  }

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
    // SECURITY (IDOR fix): override sellerId from the JWT so no caller can
    // impersonate another seller by supplying a foreign user-id in the body.
    const authenticatedUserId: string | undefined = req.user?.id ?? req.user?.sub;
    if (!authenticatedUserId) {
      throw new UnauthorizedException("Authenticated user id is missing from JWT payload");
    }
    const safeBody: CreateProductDto = { ...body, sellerId: authenticatedUserId };
    return this.marketService.createProduct(safeBody, tenantId);
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
    // SECURITY (IDOR fix): userId must match the authenticated principal.
    const authenticatedUserId: string | undefined = req.user?.id ?? req.user?.sub;
    if (!authenticatedUserId) {
      throw new UnauthorizedException("Authenticated user id is missing from JWT payload");
    }
    return this.marketService.convertYieldToProduct(
      authenticatedUserId,
      body.yieldData,
      tenantId,
    );
  }

  /**
   * إنشاء طلب شراء
   * POST /api/v1/market/orders
   *
   * Money-moving endpoint: tenant is taken from the JWT claim only (no
   * header fallback) and the `Idempotency-Key` header is honoured to
   * prevent duplicate orders on client retries.
   */
  @Post("market/orders")
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.CREATED)
  async createOrder(
    @Req() req: any,
    @Body(ValidationPipe) body: CreateOrderDto,
    @Headers("idempotency-key") idempotencyKey?: string,
  ) {
    const tenantId = this.requireTenantId(req);
    const userId = this.requireUserId(req);
    return this.marketService.createOrder(
      body,
      tenantId,
      idempotencyKey,
      userId,
    );
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
   *
   * Money-moving endpoint: tenant is resolved from the JWT claim (no
   * header fallback) and the `Idempotency-Key` header is persisted so
   * a client retry of the exact same request returns the same response.
   */
  @Post("fintech/wallet/:walletId/deposit")
  @UseGuards(JwtAuthGuard)
  async deposit(
    @Req() request: any,
    @Param("walletId") walletId: string,
    @Body(ValidationPipe) body: WalletTransactionDto,
    @Headers("idempotency-key") idempotencyKey?: string,
  ) {
    const tenantId = this.requireTenantId(request);
    const userId = this.requireUserId(request);
    return this.fintechService.deposit(
      walletId,
      body.amount,
      body.description,
      idempotencyKey,
      userId,
      request.ip,
      tenantId,
      body.currency,
    );
  }

  /**
   * سحب من المحفظة (مع رمز PIN للمبالغ الكبيرة)
   * POST /api/v1/fintech/wallet/:walletId/withdraw
   *
   * Money-moving endpoint: tenant is resolved from the JWT claim (no
   * header fallback) and the `Idempotency-Key` header is persisted via
   * the IdempotencyService so client retries are safe.
   */
  @Post("fintech/wallet/:walletId/withdraw")
  @UseGuards(JwtAuthGuard)
  async withdraw(
    @Req() request: any,
    @Param("walletId") walletId: string,
    @Body(ValidationPipe) body: WalletTransactionDto & { pin?: string },
    @Headers("idempotency-key") idempotencyKey?: string,
  ) {
    const tenantId = this.requireTenantId(request);
    const userId = this.requireUserId(request);
    return this.fintechService.withdraw(
      walletId,
      body.amount,
      body.description,
      idempotencyKey,
      userId,
      request.ip,
      body.pin,
      tenantId,
      body.currency,
    );
  }

  /**
   * سجل المعاملات
   * GET /api/v1/fintech/wallet/:walletId/transactions
   */
  @Get("fintech/wallet/:walletId/transactions")
  @UseGuards(JwtAuthGuard)
  async getTransactions(
    @Req() request: any,
    @Param("walletId") walletId: string,
    @Query("limit") limit?: string,
  ) {
    const tenantId = this.requireTenantId(request);
    const parsedLimit = Math.min(parseInt(limit ?? "20") || 20, 100);

    // Verify wallet ownership or admin role
    const wallet = await this.fintechService.getWalletById(walletId, tenantId);
    if (!wallet) {
      throw new ForbiddenException("Wallet not found");
    }

    const authenticatedUser = request.user;
    const isAdmin = authenticatedUser.roles?.includes("admin");
    const isOwner = authenticatedUser.id === wallet.userId;

    if (!isOwner && !isAdmin) {
      throw new ForbiddenException(
        "You are not authorized to view transactions for this wallet",
      );
    }

    return this.fintechService.getTransactions(
      walletId,
      tenantId,
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
  async approveLoan(@Req() req: any, @Param("id") id: string) {
    const tenantId = this.requireTenantId(req);
    return this.fintechService.approveLoan(id, tenantId);
  }

  /**
   * سداد القرض
   * POST /api/v1/fintech/loans/:id/repay
   */
  @Post("fintech/loans/:id/repay")
  @UseGuards(JwtAuthGuard)
  async repayLoan(
    @Req() req: any,
    @Param("id") id: string,
    @Body() body: { amount: number },
    @Headers("idempotency-key") idempotencyKey?: string,
  ) {
    const tenantId = this.requireTenantId(req);
    const userId = this.requireUserId(req);
    return this.fintechService.repayLoan(
      id,
      body.amount,
      tenantId,
      idempotencyKey,
      userId,
      req.ip,
    );
  }

  /**
   * جلب قروض المستخدم
   * GET /api/v1/fintech/loans/:walletId
   */
  @Get("fintech/loans/:walletId")
  @UseGuards(JwtAuthGuard)
  async getUserLoans(@Req() req: any, @Param("walletId") walletId: string) {
    const tenantId = this.requireTenantId(req);
    return this.fintechService.getUserLoans(walletId, tenantId);
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
  async getWalletLimits(
    @Req() request: any,
    @Param("walletId") walletId: string,
  ) {
    const tenantId = this.requireTenantId(request);

    // Verify wallet ownership or admin role
    const wallet = await this.fintechService.getWalletById(walletId, tenantId);
    if (!wallet) {
      throw new ForbiddenException("Wallet not found");
    }

    const authenticatedUser = request.user;
    const isAdmin = authenticatedUser.roles?.includes("admin");
    const isOwner = authenticatedUser.id === wallet.userId;

    if (!isOwner && !isAdmin) {
      throw new ForbiddenException(
        "You are not authorized to view limits for this wallet",
      );
    }

    return this.fintechService.getWalletLimits(walletId, tenantId);
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
    const tenantId = this.requireTenantId(request);
    // Verify wallet ownership or admin role
    const wallet = await this.fintechService.getWalletById(walletId, tenantId);
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

    return this.fintechService.updateWalletLimits(walletId, tenantId);
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
    const tenantId = this.requireTenantId(request);
    const wallet = await this.fintechService.getWalletById(walletId, tenantId);
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

    return this.fintechService.setPin(walletId, body.pin, tenantId, authenticatedUser.id);
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
    const tenantId = this.requireTenantId(request);
    const wallet = await this.fintechService.getWalletById(walletId, tenantId);
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

    const valid = await this.fintechService.verifyPin(walletId, body.pin, tenantId);
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
    const tenantId = this.requireTenantId(request);
    const wallet = await this.fintechService.getWalletById(walletId, tenantId);
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
      tenantId,
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
    @Req() request: any,
    @Body()
    body: {
      orderId: string;
      buyerWalletId: string;
      sellerWalletId: string;
      amount: number;
      notes?: string;
    },
    @Headers("idempotency-key") idempotencyKey?: string,
  ) {
    const tenantId = this.requireTenantId(request);
    const userId = this.requireUserId(request);
    return this.fintechService.createEscrow(
      body.orderId,
      body.buyerWalletId,
      body.sellerWalletId,
      body.amount,
      tenantId,
      body.notes,
      idempotencyKey,
      userId,
      request.ip,
    );
  }

  /**
   * إطلاق الإسكرو للبائع
   * POST /api/v1/fintech/escrow/:id/release
   */
  @Post("fintech/escrow/:id/release")
  @UseGuards(JwtAuthGuard)
  async releaseEscrow(
    @Req() request: any,
    @Param("id") id: string,
    @Body() body: { notes?: string },
    @Headers("idempotency-key") idempotencyKey?: string,
  ) {
    const tenantId = this.requireTenantId(request);
    const userId = this.requireUserId(request);
    return this.fintechService.releaseEscrow(
      id,
      tenantId,
      body.notes,
      idempotencyKey,
      userId,
      request.ip,
    );
  }

  /**
   * استرداد الإسكرو للمشتري
   * POST /api/v1/fintech/escrow/:id/refund
   */
  @Post("fintech/escrow/:id/refund")
  @UseGuards(JwtAuthGuard)
  async refundEscrow(
    @Req() request: any,
    @Param("id") id: string,
    @Body() body: { reason?: string },
    @Headers("idempotency-key") idempotencyKey?: string,
  ) {
    const tenantId = this.requireTenantId(request);
    const userId = this.requireUserId(request);
    return this.fintechService.refundEscrow(
      id,
      tenantId,
      body.reason,
      idempotencyKey,
      userId,
      request.ip,
    );
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
    const tenantId = this.requireTenantId(request);
    const authenticatedUser = request.user;
    return this.fintechService.disputeEscrow(
      id,
      body.reason,
      tenantId,
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
    const tenantId = this.requireTenantId(request);
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
      tenantId,
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
  async getEscrowByOrder(@Req() req: any, @Param("orderId") orderId: string) {
    const tenantId = this.requireTenantId(req);
    return this.fintechService.getEscrowByOrder(orderId, tenantId);
  }

  /**
   * الحصول على جميع إسكرو المحفظة
   * GET /api/v1/fintech/wallet/:walletId/escrows
   */
  @Get("fintech/wallet/:walletId/escrows")
  @UseGuards(JwtAuthGuard)
  async getWalletEscrows(
    @Req() request: any,
    @Param("walletId") walletId: string,
  ) {
    const tenantId = this.requireTenantId(request);

    // Verify wallet ownership or admin role
    const wallet = await this.fintechService.getWalletById(walletId, tenantId);
    if (!wallet) {
      throw new ForbiddenException("Wallet not found");
    }

    const authenticatedUser = request.user;
    const isAdmin = authenticatedUser.roles?.includes("admin");
    const isOwner = authenticatedUser.id === wallet.userId;

    if (!isOwner && !isAdmin) {
      throw new ForbiddenException(
        "You are not authorized to view escrows for this wallet",
      );
    }

    return this.fintechService.getWalletEscrows(walletId, tenantId);
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
    const tenantId = this.requireTenantId(request);
    // Verify wallet ownership or admin role
    const wallet = await this.fintechService.getWalletById(walletId, tenantId);
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
      tenantId,
      body.loanId,
      body.description,
      body.descriptionAr,
    );
  }

  /**
   * الحصول على الدفعات المجدولة للمحفظة.
   * GET /api/v1/fintech/wallet/:walletId/scheduled-payments
   *
   * SECURITY FIX (2026-04-21): this endpoint previously had NO
   * authentication guard — anyone could enumerate the scheduled
   * payments (including amount + schedule metadata) of any wallet. Now
   * requires JwtAuthGuard + a wallet-ownership check (except for
   * admin callers).
   */
  @Get("fintech/wallet/:walletId/scheduled-payments")
  @UseGuards(JwtAuthGuard)
  async getScheduledPayments(
    @Req() req: any,
    @Param("walletId") walletId: string,
    @Query("activeOnly") activeOnly?: string,
  ) {
    const tenantId = this.requireTenantId(req);
    const callerUserId = this.requireUserId(req);

    // Verify the caller owns this wallet (or is admin). getWalletById
    // returns `{id, userId}` when the row exists in the caller's tenant.
    const wallet = await this.fintechService.getWalletById(walletId, tenantId);
    if (!wallet) {
      throw new ForbiddenException("Wallet not found");
    }
    const authenticatedUser = req.user;
    const isAdmin = authenticatedUser?.roles?.includes("admin");
    if (wallet.userId !== callerUserId && !isAdmin) {
      throw new ForbiddenException(
        "You may only view scheduled payments for your own wallet",
      );
    }

    return this.fintechService.getScheduledPayments(
      walletId,
      tenantId,
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
    const tenantId = this.requireTenantId(request);
    // Verify scheduled payment ownership or admin role
    const scheduledPayment = await this.fintechService.getScheduledPaymentById(id, tenantId);
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

    return this.fintechService.cancelScheduledPayment(id, tenantId);
  }

  /**
   * تنفيذ دفعة مجدولة
   * POST /api/v1/fintech/scheduled-payment/:id/execute
   */
  @Post("fintech/scheduled-payment/:id/execute")
  @UseGuards(JwtAuthGuard)
  async executeScheduledPayment(@Req() request: any, @Param("id") id: string) {
    const tenantId = this.requireTenantId(request);
    // Verify scheduled payment ownership or admin role
    const scheduledPayment = await this.fintechService.getScheduledPaymentById(id, tenantId);
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

    return this.fintechService.executeScheduledPayment(id, tenantId);
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
  async getWalletDashboard(
    @Req() request: any,
    @Param("walletId") walletId: string,
  ) {
    const tenantId = this.requireTenantId(request);

    // Verify wallet ownership or admin role
    const wallet = await this.fintechService.getWalletById(walletId, tenantId);
    if (!wallet) {
      throw new ForbiddenException("Wallet not found");
    }

    const authenticatedUser = request.user;
    const isAdmin = authenticatedUser.roles?.includes("admin");
    const isOwner = authenticatedUser.id === wallet.userId;

    if (!isOwner && !isAdmin) {
      throw new ForbiddenException(
        "You are not authorized to view this wallet dashboard",
      );
    }

    return this.fintechService.getWalletDashboard(walletId, tenantId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // التحويلات - Wallet Transfers
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * تحويل بين المحافظ
   * POST /api/v1/fintech/wallet/transfer
   *
   * Money-moving endpoint: tenant from JWT claim only, Idempotency-Key
   * header persisted so retries are safe. Currency must be in the
   * allow-list enforced by WalletTransferDto.
   */
  @Post("fintech/wallet/transfer")
  @UseGuards(JwtAuthGuard)
  async transfer(
    @Req() request: any,
    @Body(ValidationPipe) body: WalletTransferDto,
    @Headers("idempotency-key") idempotencyKey?: string,
  ) {
    const tenantId = this.requireTenantId(request);
    const userId = this.requireUserId(request);

    // Verify sender wallet ownership
    const wallet = await this.fintechService.getWalletById(body.fromWalletId, tenantId);
    if (!wallet) {
      throw new ForbiddenException("Sender wallet not found");
    }

    const isOwner = userId === wallet.userId;
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
      idempotencyKey,
      userId,
      request.ip,
      body.pin,
      tenantId,
      body.currency,
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
    const tenantId = this.requireTenantId(request);
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
      tenantId,
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
    const tenantId = this.requireTenantId(request);
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
      tenantId,
      body.reason,
    );
  }
}
