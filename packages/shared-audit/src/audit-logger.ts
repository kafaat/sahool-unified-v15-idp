/**
 * Enhanced Audit Logger for SAHOOL Platform
 * Provides field-level change tracking, automatic diff generation, and hash chain integrity
 */

import { Injectable, Logger } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import { diff } from 'deep-diff';
import * as crypto from 'crypto';
import * as fs from 'fs';
import * as path from 'path';
import {
  AuditEvent,
  AuditLogOptions,
  AuditLoggerConfig,
  AuditSeverity,
  AuditCategory,
  ActorType,
  FieldChange,
  AuditDiff,
  AuditQueryOptions,
  AuditStats,
  HashChainValidation,
  AuditFallbackConfig,
} from './audit-types';
import { AuditAlertService } from './audit-alerts';

/**
 * Enhanced audit logger with field-level tracking and hash chain
 */
@Injectable()
export class AuditLogger {
  private readonly logger = new Logger(AuditLogger.name);
  private readonly config: Required<AuditLoggerConfig>;
  private alertService?: AuditAlertService;
  private auditFailureCount = 0;
  private lastFailureAlertTime = 0;
  private static readonly FAILURE_ALERT_INTERVAL_MS = 60000; // Alert at most once per minute

  constructor(config: AuditLoggerConfig = {}) {
    this.config = {
      prisma: config.prisma || null,
      defaultTenantId: config.defaultTenantId || 'default',
      enableHashChain: config.enableHashChain ?? true,
      enableAlerts: config.enableAlerts ?? true,
      alertConfig: config.alertConfig || {},
      globalRedactFields: config.globalRedactFields || [
        'password',
        'token',
        'secret',
        'apiKey',
        'privateKey',
        'accessToken',
        'refreshToken',
      ],
      hashFunction: config.hashFunction || this.defaultHashFunction,
      fallbackConfig: config.fallbackConfig || {
        enabled: true,
        maxRetries: 3,
        retryDelayMs: 100,
        emitFailureMetrics: true,
      },
    };

    if (this.config.enableAlerts) {
      this.alertService = new AuditAlertService(this.config.alertConfig);
    }
  }

  /**
   * Log an audit event
   */
  async log(event: Partial<AuditEvent>, options: AuditLogOptions = {}): Promise<AuditEvent> {
    // Set defaults
    const completeEvent: AuditEvent = {
      tenantId: event.tenantId || this.config.defaultTenantId,
      actorId: event.actorId,
      actorType: event.actorType || ActorType.SYSTEM,
      action: event.action || 'unknown',
      category: event.category || AuditCategory.SYSTEM,
      severity: event.severity || AuditSeverity.INFO,
      resourceType: event.resourceType || 'unknown',
      resourceId: event.resourceId || 'unknown',
      correlationId: event.correlationId || uuidv4(),
      sessionId: event.sessionId,
      ipAddress: event.ipAddress,
      userAgent: event.userAgent,
      changes: event.changes || [],
      diff: event.diff,
      metadata: event.metadata || {},
      success: event.success ?? true,
      errorCode: event.errorCode,
      errorMessage: event.errorMessage,
      timestamp: new Date(),
    };

    // Redact sensitive fields
    this.redactSensitiveData(completeEvent, options);

    // Add hash chain if enabled
    if (this.config.enableHashChain && this.config.prisma) {
      await this.addHashChain(completeEvent);
    }

    // Store in database
    if (this.config.prisma) {
      await this.storeEvent(completeEvent);
    }

    // Trigger alerts if enabled
    if (this.config.enableAlerts && this.alertService && options.triggerAlerts !== false) {
      await this.alertService.checkEvent(completeEvent);
    }

    // Log to console for debugging
    this.logToConsole(completeEvent);

    return completeEvent;
  }

  /**
   * Log with automatic field-level change tracking
   */
  async logWithChanges(
    event: Partial<AuditEvent>,
    oldValue: Record<string, unknown>,
    newValue: Record<string, unknown>,
    options: AuditLogOptions = {}
  ): Promise<AuditEvent> {
    const changes = this.detectFieldChanges(oldValue, newValue, options.excludeFields || []);
    const auditDiff = options.generateDiff ? this.generateDiff(oldValue, newValue) : undefined;

    return this.log(
      {
        ...event,
        changes,
        diff: auditDiff,
      },
      options
    );
  }

  /**
   * Detect field-level changes between old and new values
   */
  private detectFieldChanges(
    oldValue: Record<string, unknown>,
    newValue: Record<string, unknown>,
    excludeFields: string[] = []
  ): FieldChange[] {
    const changes: FieldChange[] = [];
    const allKeys = new Set([...Object.keys(oldValue), ...Object.keys(newValue)]);

    for (const key of allKeys) {
      if (excludeFields.includes(key)) continue;

      const oldVal = oldValue[key];
      const newVal = newValue[key];

      if (!(key in oldValue)) {
        // Field was created
        changes.push({
          field: key,
          oldValue: undefined,
          newValue: newVal,
          type: 'create',
        });
      } else if (!(key in newValue)) {
        // Field was deleted
        changes.push({
          field: key,
          oldValue: oldVal,
          newValue: undefined,
          type: 'delete',
        });
      } else if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
        // Field was modified
        changes.push({
          field: key,
          oldValue: oldVal,
          newValue: newVal,
          type: 'update',
        });
      }
    }

    return changes;
  }

  /**
   * Generate automatic diff using deep-diff library
   */
  private generateDiff(
    oldValue: Record<string, unknown>,
    newValue: Record<string, unknown>
  ): AuditDiff {
    const differences = diff(oldValue, newValue) || [];

    const result: AuditDiff = {
      added: {},
      modified: [],
      deleted: {},
    };

    for (const change of differences) {
      const path = change.path?.join('.') || 'root';

      switch (change.kind) {
        case 'N': // New
          result.added[path] = (change as any).rhs;
          break;
        case 'D': // Deleted
          result.deleted[path] = (change as any).lhs;
          break;
        case 'E': // Edited
          result.modified.push({
            field: path,
            oldValue: (change as any).lhs,
            newValue: (change as any).rhs,
            type: 'update',
          });
          break;
        case 'A': // Array change
          result.modified.push({
            field: path,
            oldValue: (change as any).item?.lhs,
            newValue: (change as any).item?.rhs,
            type: 'update',
          });
          break;
      }
    }

    return result;
  }

  /**
   * Redact sensitive data from audit event
   */
  private redactSensitiveData(event: AuditEvent, options: AuditLogOptions): void {
    const redactFields = [...this.config.globalRedactFields, ...(options.redactFields || [])];

    // Redact in changes
    if (event.changes) {
      for (const change of event.changes) {
        if (
          redactFields.some((field) => change.field.toLowerCase().includes(field.toLowerCase()))
        ) {
          change.oldValue = '[REDACTED]';
          change.newValue = '[REDACTED]';
        }
      }
    }

    // Redact in diff
    if (event.diff) {
      for (const field of redactFields) {
        const lowerField = field.toLowerCase();
        for (const key of Object.keys(event.diff.added)) {
          if (key.toLowerCase().includes(lowerField)) {
            event.diff.added[key] = '[REDACTED]';
          }
        }
        for (const key of Object.keys(event.diff.deleted)) {
          if (key.toLowerCase().includes(lowerField)) {
            event.diff.deleted[key] = '[REDACTED]';
          }
        }
      }
    }

    // Redact in metadata
    if (event.metadata) {
      for (const field of redactFields) {
        const lowerField = field.toLowerCase();
        for (const key of Object.keys(event.metadata)) {
          if (key.toLowerCase().includes(lowerField)) {
            event.metadata[key] = '[REDACTED]';
          }
        }
      }
    }
  }

  /**
   * Add hash chain to event
   */
  private async addHashChain(event: AuditEvent): Promise<void> {
    try {
      // Get last hash for tenant
      const lastEntry = await this.config.prisma.auditLog.findFirst({
        where: { tenantId: event.tenantId },
        orderBy: { createdAt: 'desc' },
        select: { entryHash: true },
      });

      event.prevHash = lastEntry?.entryHash || null;

      // Compute entry hash
      const canonical = this.buildCanonicalString(event);
      event.entryHash = this.config.hashFunction(canonical);
    } catch (error) {
      this.logger.error('Failed to add hash chain', error);
      // Continue without hash chain
    }
  }

  /**
   * Build canonical string for hashing
   */
  private buildCanonicalString(event: AuditEvent): string {
    const parts = [
      event.tenantId,
      event.actorId || 'null',
      event.actorType,
      event.action,
      event.resourceType,
      event.resourceId,
      event.correlationId,
      JSON.stringify(event.changes || []),
      JSON.stringify(event.metadata || {}),
      event.timestamp?.toISOString() || new Date().toISOString(),
      event.prevHash || 'null',
    ];

    return parts.join('|');
  }

  /**
   * Default hash function (SHA-256)
   */
  private defaultHashFunction(data: string): string {
    return crypto.createHash('sha256').update(data).digest('hex');
  }

  /**
   * Store event in database with retry and fallback mechanisms
   */
  private async storeEvent(event: AuditEvent): Promise<void> {
    const fallbackConfig = this.config.fallbackConfig;
    const maxRetries = fallbackConfig?.maxRetries || 3;
    const retryDelayMs = fallbackConfig?.retryDelayMs || 100;
    let lastError: Error | null = null;

    // Try to store with retry logic
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        await this.config.prisma.auditLog.create({
          data: {
            id: uuidv4(),
            tenantId: event.tenantId,
            actorId: event.actorId,
            actorType: event.actorType,
            action: event.action,
            category: event.category,
            severity: event.severity,
            resourceType: event.resourceType,
            resourceId: event.resourceId,
            correlationId: event.correlationId,
            sessionId: event.sessionId,
            ipAddress: event.ipAddress,
            userAgent: event.userAgent,
            changes: event.changes || [],
            diff: event.diff || {},
            metadata: event.metadata || {},
            success: event.success,
            errorCode: event.errorCode,
            errorMessage: event.errorMessage,
            prevHash: event.prevHash,
            entryHash: event.entryHash,
            createdAt: event.timestamp,
          },
        });
        // Success - reset failure count
        this.auditFailureCount = 0;
        return;
      } catch (error) {
        lastError = error as Error;
        this.logger.warn(
          `Audit storage attempt ${attempt}/${maxRetries} failed: ${lastError.message}`
        );

        if (attempt < maxRetries) {
          // Exponential backoff
          await this.sleep(retryDelayMs * Math.pow(2, attempt - 1));
        }
      }
    }

    // All retries failed - execute fallback mechanisms
    await this.handleAuditFailure(event, lastError!);
  }

  /**
   * Handle audit storage failure with fallback mechanisms
   */
  private async handleAuditFailure(event: AuditEvent, error: Error): Promise<void> {
    const fallbackConfig = this.config.fallbackConfig;
    this.auditFailureCount++;

    // Log the failure (always)
    this.logger.error(
      `CRITICAL: Audit storage failed after all retries. Event: ${event.action} on ${event.resourceType}/${event.resourceId}. Error: ${error.message}`,
      { event, error: error.stack }
    );

    // Emit failure metrics if enabled
    if (fallbackConfig?.emitFailureMetrics) {
      this.emitAuditFailureMetric(event, error);
    }

    // Write to fallback file if configured
    if (fallbackConfig?.enabled && fallbackConfig.fallbackFilePath) {
      await this.writeToFallbackFile(event, error);
    }

    // Send emergency webhook notification if configured (rate-limited)
    if (fallbackConfig?.emergencyWebhookUrl) {
      await this.sendEmergencyWebhook(event, error);
    }

    // Call custom failure handler if provided
    if (fallbackConfig?.onFailure) {
      try {
        await fallbackConfig.onFailure(event, error);
      } catch (handlerError) {
        this.logger.error('Custom audit failure handler threw an error', handlerError);
      }
    }

    // Alert if we haven't alerted recently
    await this.maybeAlertOnFailure(event, error);
  }

  /**
   * Allowed base directory for fallback audit files
   * This prevents path traversal attacks by ensuring all writes stay within this directory
   */
  private static readonly FALLBACK_BASE_DIR =
    process.env.AUDIT_FALLBACK_DIR || '/var/log/sahool/audit';

  /**
   * Validate and sanitize fallback file path to prevent path traversal attacks
   * @returns Sanitized absolute path or null if path is invalid
   */
  private sanitizeFallbackPath(configuredPath: string): string | null {
    try {
      // Resolve to absolute path
      const resolvedPath = path.resolve(
        AuditLogger.FALLBACK_BASE_DIR,
        path.basename(configuredPath)
      );

      // Ensure the resolved path is within the allowed base directory
      const normalizedBase = path.normalize(AuditLogger.FALLBACK_BASE_DIR);
      const normalizedResolved = path.normalize(resolvedPath);

      if (!normalizedResolved.startsWith(normalizedBase + path.sep)) {
        this.logger.error(
          `Path traversal attempt detected: ${configuredPath} resolved outside allowed directory`
        );
        return null;
      }

      // Additional check: reject paths with directory traversal sequences
      if (configuredPath.includes('..') || configuredPath.includes('\0')) {
        this.logger.error(`Invalid path detected (traversal or null byte): ${configuredPath}`);
        return null;
      }

      return resolvedPath;
    } catch (error) {
      this.logger.error(`Path sanitization failed: ${(error as Error).message}`);
      return null;
    }
  }

  /**
   * Sanitize a string value for safe file logging
   * Removes/replaces potentially dangerous characters and limits length
   */
  private sanitizeForLog(value: string | undefined | null, maxLength = 256): string | null {
    if (value === null || value === undefined) {
      return null;
    }
    // Remove control characters, null bytes, and limit length
    // Only allow printable ASCII and common unicode characters
    const sanitized = String(value)
      .replace(/[\x00-\x1f\x7f]/g, '') // Remove control characters
      .replace(/[<>'"&\\]/g, '_') // Replace potentially dangerous chars
      .substring(0, maxLength);
    return sanitized || null;
  }

  /**
   * Create a sanitized copy of the event for file logging
   * Removes or sanitizes fields that could contain untrusted network data
   */
  private sanitizeEventForFileLog(event: AuditEvent): Record<string, unknown> {
    return {
      tenantId: this.sanitizeForLog(event.tenantId, 64),
      actorId: this.sanitizeForLog(event.actorId, 64),
      actorType: event.actorType,
      action: this.sanitizeForLog(event.action, 128),
      category: event.category,
      severity: event.severity,
      resourceType: this.sanitizeForLog(event.resourceType, 64),
      resourceId: this.sanitizeForLog(event.resourceId, 128),
      correlationId: this.sanitizeForLog(event.correlationId, 64),
      sessionId: this.sanitizeForLog(event.sessionId, 64),
      // Sanitize network-derived fields more aggressively
      ipAddress: this.sanitizeForLog(event.ipAddress, 45), // Max IPv6 length
      userAgent: this.sanitizeForLog(event.userAgent, 256),
      // Exclude raw changes/diff/metadata from file fallback for security
      // Only include essential audit info
      success: event.success,
      errorCode: this.sanitizeForLog(event.errorCode, 64),
      errorMessage: this.sanitizeForLog(event.errorMessage, 512),
      timestamp: event.timestamp?.toISOString(),
      entryHash: event.entryHash,
    };
  }

  /**
   * Write audit event to fallback file (append-only)
   */
  private async writeToFallbackFile(event: AuditEvent, error: Error): Promise<void> {
    const configuredPath = this.config.fallbackConfig?.fallbackFilePath;
    if (!configuredPath) return;

    // Sanitize and validate the path to prevent path traversal
    const fallbackPath = this.sanitizeFallbackPath(configuredPath);
    if (!fallbackPath) {
      this.logger.error('Fallback file path validation failed, skipping write');
      return;
    }

    try {
      // Sanitize event data before writing to file to prevent log injection
      const sanitizedEvent = this.sanitizeEventForFileLog(event);

      const fallbackEntry = {
        timestamp: new Date().toISOString(),
        event: sanitizedEvent,
        error: {
          message: this.sanitizeForLog(error.message, 512),
          name: this.sanitizeForLog(error.name, 64),
        },
        failureCount: this.auditFailureCount,
      };

      // Ensure directory exists
      const dir = path.dirname(fallbackPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      // Append to file (newline-delimited JSON)
      fs.appendFileSync(fallbackPath, JSON.stringify(fallbackEntry) + '\n', {
        encoding: 'utf8',
        flag: 'a',
      });

      this.logger.warn(`Audit event written to fallback file: ${fallbackPath}`);
    } catch (fileError) {
      this.logger.error(`Failed to write to fallback file: ${(fileError as Error).message}`);
    }
  }

  /**
   * Send emergency webhook notification (rate-limited)
   */
  private async sendEmergencyWebhook(event: AuditEvent, error: Error): Promise<void> {
    const webhookUrl = this.config.fallbackConfig?.emergencyWebhookUrl;
    if (!webhookUrl) return;

    const now = Date.now();
    if (now - this.lastFailureAlertTime < AuditLogger.FAILURE_ALERT_INTERVAL_MS) {
      return; // Rate limited
    }
    this.lastFailureAlertTime = now;

    try {
      const payload = {
        alert_type: 'audit_storage_failure',
        severity: 'critical',
        message: `Audit logging failed: ${error.message}`,
        event_summary: {
          action: event.action,
          resourceType: event.resourceType,
          resourceId: event.resourceId,
          tenantId: event.tenantId,
          timestamp: event.timestamp?.toISOString(),
        },
        failure_count: this.auditFailureCount,
        timestamp: new Date().toISOString(),
      };

      // Use native fetch (Node.js 18+) or fall back to http module
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        this.logger.error(`Emergency webhook returned ${response.status}: ${response.statusText}`);
      }
    } catch (webhookError) {
      this.logger.error(`Failed to send emergency webhook: ${(webhookError as Error).message}`);
    }
  }

  /**
   * Emit audit failure metric for monitoring systems
   */
  private emitAuditFailureMetric(event: AuditEvent, error: Error): void {
    // Emit metric in Prometheus format via console (can be scraped by log aggregator)
    const metric = {
      metric_name: 'sahool_audit_storage_failure_total',
      labels: {
        tenant_id: event.tenantId,
        action: event.action,
        resource_type: event.resourceType,
        error_type: error.name,
      },
      value: 1,
      timestamp: Date.now(),
    };

    // Log as structured JSON for metric scrapers
    this.logger.warn(`METRIC: ${JSON.stringify(metric)}`);
  }

  /**
   * Alert on audit failure if we haven't recently
   */
  private async maybeAlertOnFailure(event: AuditEvent, error: Error): Promise<void> {
    if (!this.alertService) return;

    const now = Date.now();
    if (now - this.lastFailureAlertTime < AuditLogger.FAILURE_ALERT_INTERVAL_MS) {
      return; // Already alerted recently
    }

    // Create a synthetic audit event for the failure itself
    const failureEvent: AuditEvent = {
      tenantId: event.tenantId,
      actorType: ActorType.SYSTEM,
      action: 'audit_storage_failure',
      category: AuditCategory.SYSTEM,
      severity: AuditSeverity.CRITICAL,
      resourceType: 'audit_system',
      resourceId: 'primary_storage',
      correlationId: event.correlationId,
      metadata: {
        originalEvent: {
          action: event.action,
          resourceType: event.resourceType,
          resourceId: event.resourceId,
        },
        errorMessage: error.message,
        failureCount: this.auditFailureCount,
      },
      success: false,
      errorCode: 'AUDIT_STORAGE_FAILURE',
      errorMessage: error.message,
      timestamp: new Date(),
    };

    await this.alertService.checkEvent(failureEvent);
  }

  /**
   * Sleep helper for retry delays
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Log to console for debugging
   */
  private logToConsole(event: AuditEvent): void {
    const message = `[AUDIT] ${event.action} on ${event.resourceType}/${event.resourceId} by ${event.actorType}/${event.actorId || 'system'}`;

    switch (event.severity) {
      case AuditSeverity.CRITICAL:
      case AuditSeverity.ERROR:
        this.logger.error(message, { event });
        break;
      case AuditSeverity.WARNING:
        this.logger.warn(message, { event });
        break;
      default:
        this.logger.log(message);
    }
  }

  /**
   * Query audit logs
   */
  async query(options: AuditQueryOptions): Promise<AuditEvent[]> {
    if (!this.config.prisma) {
      throw new Error('Prisma client not configured');
    }

    const where: any = {
      tenantId: options.tenantId,
    };

    if (options.actorId) where.actorId = options.actorId;
    if (options.resourceType) where.resourceType = options.resourceType;
    if (options.resourceId) where.resourceId = options.resourceId;
    if (options.action) where.action = options.action;
    if (options.category) where.category = options.category;
    if (options.severity) where.severity = options.severity;

    if (options.startDate || options.endDate) {
      where.createdAt = {};
      if (options.startDate) where.createdAt.gte = options.startDate;
      if (options.endDate) where.createdAt.lte = options.endDate;
    }

    const entries = await this.config.prisma.auditLog.findMany({
      where,
      orderBy: { createdAt: options.orderBy || 'desc' },
      take: options.limit || 100,
      skip: options.offset || 0,
    });

    return entries;
  }

  /**
   * Get audit statistics
   */
  async getStats(tenantId: string, date: Date): Promise<AuditStats> {
    if (!this.config.prisma) {
      throw new Error('Prisma client not configured');
    }

    const startOfDay = new Date(date);
    startOfDay.setHours(0, 0, 0, 0);
    const endOfDay = new Date(date);
    endOfDay.setHours(23, 59, 59, 999);

    const events = await this.config.prisma.auditLog.findMany({
      where: {
        tenantId,
        createdAt: {
          gte: startOfDay,
          lte: endOfDay,
        },
      },
    });

    const stats: AuditStats = {
      tenantId,
      date,
      totalEvents: events.length,
      eventsByCategory: {} as Record<AuditCategory, number>,
      eventsBySeverity: {} as Record<AuditSeverity, number>,
      uniqueActors: new Set(events.map((e: any) => e.actorId)).size,
      uniqueResources: new Set(events.map((e: any) => `${e.resourceType}:${e.resourceId}`)).size,
      failedEvents: events.filter((e: any) => !e.success).length,
      criticalEvents: events.filter((e: any) => e.severity === AuditSeverity.CRITICAL).length,
    };

    // Count by category
    for (const category of Object.values(AuditCategory)) {
      stats.eventsByCategory[category] = events.filter((e: any) => e.category === category).length;
    }

    // Count by severity
    for (const severity of Object.values(AuditSeverity)) {
      stats.eventsBySeverity[severity] = events.filter((e: any) => e.severity === severity).length;
    }

    return stats;
  }

  /**
   * Validate hash chain integrity
   */
  async validateHashChain(tenantId: string): Promise<HashChainValidation> {
    if (!this.config.prisma || !this.config.enableHashChain) {
      throw new Error('Hash chain validation not available');
    }

    const entries = await this.config.prisma.auditLog.findMany({
      where: { tenantId },
      orderBy: { createdAt: 'asc' },
    });

    const validation: HashChainValidation = {
      valid: true,
      invalidEntries: [],
      totalEntries: entries.length,
      validatedEntries: 0,
      errors: [],
    };

    let expectedPrevHash: string | null = null;

    for (const entry of entries) {
      // Check if prev_hash matches
      if (entry.prevHash !== expectedPrevHash) {
        validation.valid = false;
        validation.invalidEntries.push(entry.id);
        validation.errors.push(
          `Entry ${entry.id}: Expected prev_hash ${expectedPrevHash}, got ${entry.prevHash}`
        );
      }

      // Verify entry hash
      const canonical = this.buildCanonicalString(entry);
      const computedHash = this.config.hashFunction(canonical);

      if (entry.entryHash !== computedHash) {
        validation.valid = false;
        validation.invalidEntries.push(entry.id);
        validation.errors.push(
          `Entry ${entry.id}: Hash mismatch. Expected ${computedHash}, got ${entry.entryHash}`
        );
      } else {
        validation.validatedEntries++;
      }

      expectedPrevHash = entry.entryHash;
    }

    return validation;
  }
}
