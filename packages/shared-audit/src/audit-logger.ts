/**
 * Enhanced Audit Logger for SAHOOL Platform
 * Provides field-level change tracking, automatic diff generation, and hash chain integrity
 */

import { Injectable, Logger } from "@nestjs/common";
import { v4 as uuidv4 } from "uuid";
import { diff } from "deep-diff";
import * as crypto from "crypto";
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
} from "./audit-types";
import { AuditAlertService } from "./audit-alerts";

/**
 * Enhanced audit logger with field-level tracking and hash chain
 */
@Injectable()
export class AuditLogger {
  private readonly logger = new Logger(AuditLogger.name);
  private readonly config: Required<AuditLoggerConfig>;
  private alertService?: AuditAlertService;

  constructor(config: AuditLoggerConfig = {}) {
    this.config = {
      prisma: config.prisma || null,
      defaultTenantId: config.defaultTenantId || "default",
      enableHashChain: config.enableHashChain ?? true,
      enableAlerts: config.enableAlerts ?? true,
      alertConfig: config.alertConfig || {},
      globalRedactFields: config.globalRedactFields || [
        "password",
        "token",
        "secret",
        "apiKey",
        "privateKey",
        "accessToken",
        "refreshToken",
      ],
      hashFunction: config.hashFunction || this.defaultHashFunction,
    };

    if (this.config.enableAlerts) {
      this.alertService = new AuditAlertService(this.config.alertConfig);
    }
  }

  /**
   * Log an audit event
   */
  async log(
    event: Partial<AuditEvent>,
    options: AuditLogOptions = {},
  ): Promise<AuditEvent> {
    // Set defaults
    const completeEvent: AuditEvent = {
      tenantId: event.tenantId || this.config.defaultTenantId,
      actorId: event.actorId,
      actorType: event.actorType || ActorType.SYSTEM,
      action: event.action || "unknown",
      category: event.category || AuditCategory.SYSTEM,
      severity: event.severity || AuditSeverity.INFO,
      resourceType: event.resourceType || "unknown",
      resourceId: event.resourceId || "unknown",
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
    if (
      this.config.enableAlerts &&
      this.alertService &&
      options.triggerAlerts !== false
    ) {
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
    options: AuditLogOptions = {},
  ): Promise<AuditEvent> {
    const changes = this.detectFieldChanges(
      oldValue,
      newValue,
      options.excludeFields || [],
    );
    const auditDiff = options.generateDiff
      ? this.generateDiff(oldValue, newValue)
      : undefined;

    return this.log(
      {
        ...event,
        changes,
        diff: auditDiff,
      },
      options,
    );
  }

  /**
   * Detect field-level changes between old and new values
   */
  private detectFieldChanges(
    oldValue: Record<string, unknown>,
    newValue: Record<string, unknown>,
    excludeFields: string[] = [],
  ): FieldChange[] {
    const changes: FieldChange[] = [];
    const allKeys = new Set([
      ...Object.keys(oldValue),
      ...Object.keys(newValue),
    ]);

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
          type: "create",
        });
      } else if (!(key in newValue)) {
        // Field was deleted
        changes.push({
          field: key,
          oldValue: oldVal,
          newValue: undefined,
          type: "delete",
        });
      } else if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
        // Field was modified
        changes.push({
          field: key,
          oldValue: oldVal,
          newValue: newVal,
          type: "update",
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
    newValue: Record<string, unknown>,
  ): AuditDiff {
    const differences = diff(oldValue, newValue) || [];

    const result: AuditDiff = {
      added: {},
      modified: [],
      deleted: {},
    };

    for (const change of differences) {
      const path = change.path?.join(".") || "root";

      switch (change.kind) {
        case "N": // New
          result.added[path] = (change as any).rhs;
          break;
        case "D": // Deleted
          result.deleted[path] = (change as any).lhs;
          break;
        case "E": // Edited
          result.modified.push({
            field: path,
            oldValue: (change as any).lhs,
            newValue: (change as any).rhs,
            type: "update",
          });
          break;
        case "A": // Array change
          result.modified.push({
            field: path,
            oldValue: (change as any).item?.lhs,
            newValue: (change as any).item?.rhs,
            type: "update",
          });
          break;
      }
    }

    return result;
  }

  /**
   * Redact sensitive data from audit event
   */
  private redactSensitiveData(
    event: AuditEvent,
    options: AuditLogOptions,
  ): void {
    const redactFields = [
      ...this.config.globalRedactFields,
      ...(options.redactFields || []),
    ];

    // Redact in changes
    if (event.changes) {
      for (const change of event.changes) {
        if (
          redactFields.some((field) =>
            change.field.toLowerCase().includes(field.toLowerCase()),
          )
        ) {
          change.oldValue = "[REDACTED]";
          change.newValue = "[REDACTED]";
        }
      }
    }

    // Redact in diff
    if (event.diff) {
      for (const field of redactFields) {
        const lowerField = field.toLowerCase();
        for (const key of Object.keys(event.diff.added)) {
          if (key.toLowerCase().includes(lowerField)) {
            event.diff.added[key] = "[REDACTED]";
          }
        }
        for (const key of Object.keys(event.diff.deleted)) {
          if (key.toLowerCase().includes(lowerField)) {
            event.diff.deleted[key] = "[REDACTED]";
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
            event.metadata[key] = "[REDACTED]";
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
        orderBy: { createdAt: "desc" },
        select: { entryHash: true },
      });

      event.prevHash = lastEntry?.entryHash || null;

      // Compute entry hash
      const canonical = this.buildCanonicalString(event);
      event.entryHash = this.config.hashFunction(canonical);
    } catch (error) {
      this.logger.error("Failed to add hash chain", error);
      // Continue without hash chain
    }
  }

  /**
   * Build canonical string for hashing
   */
  private buildCanonicalString(event: AuditEvent): string {
    const parts = [
      event.tenantId,
      event.actorId || "null",
      event.actorType,
      event.action,
      event.resourceType,
      event.resourceId,
      event.correlationId,
      JSON.stringify(event.changes || []),
      JSON.stringify(event.metadata || {}),
      event.timestamp?.toISOString() || new Date().toISOString(),
      event.prevHash || "null",
    ];

    return parts.join("|");
  }

  /**
   * Default hash function (SHA-256)
   */
  private defaultHashFunction(data: string): string {
    return crypto.createHash("sha256").update(data).digest("hex");
  }

  /**
   * Store event in database
   */
  private async storeEvent(event: AuditEvent): Promise<void> {
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
    } catch (error) {
      this.logger.error("Failed to store audit event", error);
      // Don't throw - audit logging should not break the application
    }
  }

  /**
   * Log to console for debugging
   */
  private logToConsole(event: AuditEvent): void {
    const message = `[AUDIT] ${event.action} on ${event.resourceType}/${event.resourceId} by ${event.actorType}/${event.actorId || "system"}`;

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
      throw new Error("Prisma client not configured");
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
      orderBy: { createdAt: options.orderBy || "desc" },
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
      throw new Error("Prisma client not configured");
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
      uniqueActors: new Set(events.map((e) => e.actorId)).size,
      uniqueResources: new Set(
        events.map((e) => `${e.resourceType}:${e.resourceId}`),
      ).size,
      failedEvents: events.filter((e) => !e.success).length,
      criticalEvents: events.filter(
        (e) => e.severity === AuditSeverity.CRITICAL,
      ).length,
    };

    // Count by category
    for (const category of Object.values(AuditCategory)) {
      stats.eventsByCategory[category] = events.filter(
        (e) => e.category === category,
      ).length;
    }

    // Count by severity
    for (const severity of Object.values(AuditSeverity)) {
      stats.eventsBySeverity[severity] = events.filter(
        (e) => e.severity === severity,
      ).length;
    }

    return stats;
  }

  /**
   * Validate hash chain integrity
   */
  async validateHashChain(tenantId: string): Promise<HashChainValidation> {
    if (!this.config.prisma || !this.config.enableHashChain) {
      throw new Error("Hash chain validation not available");
    }

    const entries = await this.config.prisma.auditLog.findMany({
      where: { tenantId },
      orderBy: { createdAt: "asc" },
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
          `Entry ${entry.id}: Expected prev_hash ${expectedPrevHash}, got ${entry.prevHash}`,
        );
      }

      // Verify entry hash
      const canonical = this.buildCanonicalString(entry);
      const computedHash = this.config.hashFunction(canonical);

      if (entry.entryHash !== computedHash) {
        validation.valid = false;
        validation.invalidEntries.push(entry.id);
        validation.errors.push(
          `Entry ${entry.id}: Hash mismatch. Expected ${computedHash}, got ${entry.entryHash}`,
        );
      } else {
        validation.validatedEntries++;
      }

      expectedPrevHash = entry.entryHash;
    }

    return validation;
  }
}
