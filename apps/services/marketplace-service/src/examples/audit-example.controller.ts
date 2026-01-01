/**
 * Example Controller: Using Enhanced Audit System
 * This demonstrates how to use the audit decorators and middleware
 */

import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
} from '@nestjs/common';
import {
  AuditCreate,
  AuditUpdate,
  AuditDelete,
  AuditFinancial,
  AuditSecurity,
  Audit,
  TenantId,
  ActorId,
  CorrelationId,
  type AuditContext,
  AuditLogger,
  AuditCategory,
  AuditSeverity,
  ActorType,
} from '@sahool/shared-audit';
import { FintechService } from '../fintech/fintech.service';
import { MarketService } from '../market/market.service';

/**
 * Example: Product Management with Audit Trail
 */
@Controller('products')
export class AuditExampleController {
  constructor(
    private readonly marketService: MarketService,
    private readonly auditLogger: AuditLogger,
  ) {}

  /**
   * Example 1: Automatic audit with @AuditCreate decorator
   * This will automatically log product creation
   */
  @Post()
  @AuditCreate('product', {
    trackChanges: true,
    excludeFields: ['createdAt', 'updatedAt'],
  })
  async createProduct(
    @Body() createDto: any,
    @Audit() audit: AuditContext,
    @TenantId() tenantId: string,
    @ActorId() actorId: string,
  ) {
    // Your business logic here
    const product = {
      id: 'product-123',
      ...createDto,
      tenantId,
      createdBy: actorId,
      createdAt: new Date(),
    };

    // The audit log will be created automatically by the interceptor
    return product;
  }

  /**
   * Example 2: Update with field-level change tracking
   * This tracks exactly which fields changed
   */
  @Put(':id')
  @AuditUpdate('product', {
    trackChanges: true,
    generateDiff: true,
    redactFields: ['internalNotes', 'costPrice'],
  })
  async updateProduct(@Param('id') id: string, @Body() updateDto: any) {
    // Fetch old value
    const oldProduct = {
      id,
      name: 'Old Product Name',
      price: 100,
      stock: 50,
    };

    // Apply updates
    const newProduct = {
      ...oldProduct,
      ...updateDto,
      updatedAt: new Date(),
    };

    // The audit log will capture the before/after changes automatically
    return newProduct;
  }

  /**
   * Example 3: Delete with audit
   */
  @Delete(':id')
  @AuditDelete('product', {
    severity: AuditSeverity.WARNING,
  })
  async deleteProduct(@Param('id') id: string, @CorrelationId() correlationId: string) {
    // Your deletion logic
    console.log(`Deleting product ${id}, correlation: ${correlationId}`);
    return { deleted: true, id };
  }

  /**
   * Example 4: Manual audit logging for complex operations
   */
  @Post(':id/purchase')
  @AuditFinancial('product.purchase', {
    severity: AuditSeverity.WARNING,
    trackChanges: true,
  })
  async purchaseProduct(
    @Param('id') id: string,
    @Body() purchaseDto: { quantity: number; paymentMethod: string },
    @Audit() audit: AuditContext,
  ) {
    // Manual audit logging with detailed information
    await this.auditLogger.log({
      tenantId: audit.tenantId,
      actorId: audit.actorId,
      actorType: audit.actorType,
      action: 'product.purchase',
      category: AuditCategory.FINANCIAL,
      severity: AuditSeverity.WARNING,
      resourceType: 'product',
      resourceId: id,
      correlationId: audit.correlationId,
      sessionId: audit.sessionId,
      ipAddress: audit.ipAddress,
      userAgent: audit.userAgent,
      metadata: {
        quantity: purchaseDto.quantity,
        paymentMethod: purchaseDto.paymentMethod,
        totalAmount: purchaseDto.quantity * 100, // Example calculation
      },
      success: true,
    });

    return { success: true, productId: id };
  }

  /**
   * Example 5: Security audit for sensitive operations
   */
  @Post(':id/admin-override')
  @AuditSecurity('product.admin_override', {
    severity: AuditSeverity.CRITICAL,
  })
  async adminOverride(
    @Param('id') id: string,
    @Body() overrideDto: any,
    @Audit() audit: AuditContext,
  ) {
    // Critical security operation - will trigger alerts
    return {
      success: true,
      message: 'Admin override applied',
    };
  }

  /**
   * Example 6: Manual audit with change tracking
   * Shows how to manually log changes between old and new values
   */
  @Put(':id/price')
  async updatePrice(
    @Param('id') id: string,
    @Body() priceDto: { newPrice: number; reason: string },
    @Audit() audit: AuditContext,
  ) {
    // Fetch old value
    const oldProduct = {
      id,
      price: 100,
      lastPriceChange: new Date('2024-01-01'),
    };

    // Update price
    const newProduct = {
      ...oldProduct,
      price: priceDto.newPrice,
      lastPriceChange: new Date(),
      priceChangeReason: priceDto.reason,
    };

    // Manual audit with field-level tracking
    await this.auditLogger.logWithChanges(
      {
        tenantId: audit.tenantId,
        actorId: audit.actorId,
        actorType: audit.actorType,
        action: 'product.price_change',
        category: AuditCategory.DATA,
        severity: AuditSeverity.WARNING,
        resourceType: 'product',
        resourceId: id,
        correlationId: audit.correlationId,
        sessionId: audit.sessionId,
        ipAddress: audit.ipAddress,
        userAgent: audit.userAgent,
        metadata: {
          reason: priceDto.reason,
        },
        success: true,
      },
      oldProduct,
      newProduct,
      {
        trackChanges: true,
        generateDiff: true,
        excludeFields: ['lastPriceChange'],
      },
    );

    return newProduct;
  }

  /**
   * Example 7: Query audit logs
   */
  @Get('audit-logs')
  async getAuditLogs(
    @Query('resourceId') resourceId: string,
    @TenantId() tenantId: string,
  ) {
    const logs = await this.auditLogger.query({
      tenantId,
      resourceType: 'product',
      resourceId,
      limit: 50,
    });

    return {
      total: logs.length,
      logs: logs.map((log) => ({
        id: log.id,
        action: log.action,
        actorId: log.actorId,
        timestamp: log.timestamp,
        changes: log.changes,
        diff: log.diff,
        success: log.success,
      })),
    };
  }

  /**
   * Example 8: Get audit statistics
   */
  @Get('audit-stats')
  async getAuditStats(@TenantId() tenantId: string) {
    const stats = await this.auditLogger.getStats(tenantId, new Date());
    return stats;
  }

  /**
   * Example 9: Validate hash chain integrity
   */
  @Get('audit-validate')
  @AuditSecurity('audit.validate_chain', {
    severity: AuditSeverity.INFO,
  })
  async validateAuditChain(@TenantId() tenantId: string) {
    const validation = await this.auditLogger.validateHashChain(tenantId);
    return {
      valid: validation.valid,
      totalEntries: validation.totalEntries,
      validatedEntries: validation.validatedEntries,
      errors: validation.errors,
      invalidEntries: validation.invalidEntries,
    };
  }
}

/**
 * Example: DTO with field-level audit annotations
 * (Note: This requires the @AuditField decorator from shared-audit)
 */
export class CreateProductDto {
  name: string;
  description: string;
  price: number; // Sensitive - will be redacted if configured
  stock: number;
  category: string;

  // This would be excluded from audit logs
  internalNotes?: string;
}

export class UpdateProductDto {
  name?: string;
  description?: string;
  price?: number;
  stock?: number;
  category?: string;

  // Sensitive fields that should be redacted
  costPrice?: number;
  profitMargin?: number;
  internalNotes?: string;
}
