/**
 * Audit Alert Service
 * Detects patterns in audit events and triggers alerts for critical security events
 */

import { Injectable, Logger } from "@nestjs/common";
import { v4 as uuidv4 } from "uuid";
import {
  AuditEvent,
  AuditAlert,
  AuditSeverity,
  AuditCategory,
  AlertConfig,
  AlertRule,
  AlertCondition,
  AlertHandler,
} from "./audit-types";

/**
 * Default alert rules for common security patterns
 */
const DEFAULT_ALERT_RULES: AlertRule[] = [
  {
    name: "multiple_failed_logins",
    description: "Multiple failed login attempts from same IP",
    conditions: [
      { field: "action", operator: "equals", value: "auth.login" },
      { field: "success", operator: "equals", value: false },
    ],
    severity: AuditSeverity.WARNING,
    batchSimilar: true,
  },
  {
    name: "privilege_escalation",
    description: "User attempting to access admin resources",
    conditions: [
      { field: "category", operator: "equals", value: AuditCategory.ADMIN },
      { field: "success", operator: "equals", value: false },
    ],
    severity: AuditSeverity.CRITICAL,
  },
  {
    name: "financial_transaction_failure",
    description: "Financial transaction failed",
    conditions: [
      { field: "category", operator: "equals", value: AuditCategory.FINANCIAL },
      { field: "success", operator: "equals", value: false },
    ],
    severity: AuditSeverity.ERROR,
  },
  {
    name: "data_deletion",
    description: "Data deletion event",
    conditions: [
      { field: "action", operator: "contains", value: "delete" },
      { field: "category", operator: "equals", value: AuditCategory.DATA },
    ],
    severity: AuditSeverity.WARNING,
  },
  {
    name: "critical_error",
    description: "Critical severity event occurred",
    conditions: [
      { field: "severity", operator: "equals", value: AuditSeverity.CRITICAL },
    ],
    severity: AuditSeverity.CRITICAL,
  },
  {
    name: "unauthorized_access",
    description: "Unauthorized access attempt",
    conditions: [
      { field: "category", operator: "equals", value: AuditCategory.ACCESS },
      { field: "success", operator: "equals", value: false },
    ],
    severity: AuditSeverity.WARNING,
  },
  {
    name: "security_config_change",
    description: "Security configuration changed",
    conditions: [
      { field: "category", operator: "equals", value: AuditCategory.SECURITY },
      { field: "action", operator: "contains", value: "update" },
    ],
    severity: AuditSeverity.WARNING,
  },
  {
    name: "bulk_data_export",
    description: "Large data export detected",
    conditions: [
      { field: "action", operator: "contains", value: "export" },
      { field: "category", operator: "equals", value: AuditCategory.DATA },
    ],
    severity: AuditSeverity.INFO,
  },
];

/**
 * Alert service for pattern detection and notification
 */
@Injectable()
export class AuditAlertService {
  private readonly logger = new Logger(AuditAlertService.name);
  private readonly config: Required<AlertConfig>;
  private readonly handlers: Map<string, AlertHandler>;
  private readonly alertQueue: AuditAlert[] = [];
  private batchTimer?: NodeJS.Timeout;

  constructor(config: AlertConfig = {}) {
    this.config = {
      handlers: config.handlers || [],
      rules: [...DEFAULT_ALERT_RULES, ...(config.rules || [])],
      batchAlerts: config.batchAlerts ?? true,
      batchWindowMs: config.batchWindowMs || 60000, // 1 minute
    };

    this.handlers = new Map();
    for (const handler of this.config.handlers) {
      this.handlers.set(handler.name, handler);
    }

    // Start batch timer if batching is enabled
    if (this.config.batchAlerts) {
      this.startBatchTimer();
    }
  }

  /**
   * Check an event against all alert rules
   */
  async checkEvent(event: AuditEvent): Promise<void> {
    for (const rule of this.config.rules) {
      if (this.matchesRule(event, rule)) {
        await this.triggerAlert(rule, event);
      }
    }
  }

  /**
   * Check if event matches a rule
   */
  private matchesRule(event: AuditEvent, rule: AlertRule): boolean {
    for (const condition of rule.conditions) {
      if (!this.matchesCondition(event, condition)) {
        return false;
      }
    }
    return true;
  }

  /**
   * Check if event matches a condition
   */
  private matchesCondition(
    event: AuditEvent,
    condition: AlertCondition,
  ): boolean {
    const value = event[condition.field];

    switch (condition.operator) {
      case "equals":
        return value === condition.value;

      case "contains":
        if (typeof value === "string" && typeof condition.value === "string") {
          return value.includes(condition.value);
        }
        return false;

      case "startsWith":
        if (typeof value === "string" && typeof condition.value === "string") {
          return value.startsWith(condition.value);
        }
        return false;

      case "endsWith":
        if (typeof value === "string" && typeof condition.value === "string") {
          return value.endsWith(condition.value);
        }
        return false;

      case "matches":
        if (typeof value === "string" && typeof condition.value === "string") {
          try {
            const regex = new RegExp(condition.value);
            return regex.test(value);
          } catch {
            return false;
          }
        }
        return false;

      case "greaterThan":
        if (typeof value === "number" && typeof condition.value === "number") {
          return value > condition.value;
        }
        return false;

      case "lessThan":
        if (typeof value === "number" && typeof condition.value === "number") {
          return value < condition.value;
        }
        return false;

      default:
        return false;
    }
  }

  /**
   * Trigger an alert
   */
  private async triggerAlert(
    rule: AlertRule,
    event: AuditEvent,
  ): Promise<void> {
    const alert: AuditAlert = {
      id: uuidv4(),
      rule: rule.name,
      severity: rule.severity,
      message: this.buildAlertMessage(rule, event),
      events: [event],
      timestamp: new Date(),
    };

    if (this.config.batchAlerts && rule.batchSimilar) {
      // Add to queue for batching
      this.alertQueue.push(alert);
    } else {
      // Send immediately
      await this.sendAlert(alert, rule);
    }
  }

  /**
   * Build alert message
   */
  private buildAlertMessage(rule: AlertRule, event: AuditEvent): string {
    return `[${rule.name}] ${rule.description}: ${event.action} on ${event.resourceType}/${event.resourceId} by ${event.actorType}/${event.actorId || "system"}`;
  }

  /**
   * Send alert to handlers
   */
  private async sendAlert(alert: AuditAlert, rule: AlertRule): Promise<void> {
    this.logger.warn(`ALERT: ${alert.message}`, { alert });

    // Use custom handler if specified
    if (rule.handler) {
      const handler = this.handlers.get(rule.handler);
      if (handler) {
        try {
          await handler.handle(alert);
        } catch (error) {
          this.logger.error(
            `Failed to execute alert handler ${rule.handler}`,
            error,
          );
        }
      }
    }

    // Execute all global handlers
    for (const handler of this.config.handlers) {
      if (!rule.handler || handler.name !== rule.handler) {
        try {
          await handler.handle(alert);
        } catch (error) {
          this.logger.error(
            `Failed to execute alert handler ${handler.name}`,
            error,
          );
        }
      }
    }
  }

  /**
   * Start batch timer
   */
  private startBatchTimer(): void {
    this.batchTimer = setInterval(() => {
      this.processBatch();
    }, this.config.batchWindowMs);
  }

  /**
   * Process batched alerts
   */
  private async processBatch(): Promise<void> {
    if (this.alertQueue.length === 0) return;

    // Group alerts by rule
    const grouped = new Map<string, AuditAlert[]>();
    for (const alert of this.alertQueue) {
      const existing = grouped.get(alert.rule) || [];
      existing.push(alert);
      grouped.set(alert.rule, existing);
    }

    // Send batched alerts
    for (const [ruleName, alerts] of grouped) {
      const rule = this.config.rules.find((r) => r.name === ruleName);
      if (!rule) continue;

      if (alerts.length === 1) {
        // Single alert, send as-is
        await this.sendAlert(alerts[0], rule);
      } else {
        // Multiple alerts, batch them
        const batchedAlert: AuditAlert = {
          id: uuidv4(),
          rule: ruleName,
          severity: rule.severity,
          message: `[BATCH] ${rule.description}: ${alerts.length} events detected`,
          events: alerts.flatMap((a) => a.events),
          timestamp: new Date(),
        };
        await this.sendAlert(batchedAlert, rule);
      }
    }

    // Clear queue
    this.alertQueue.length = 0;
  }

  /**
   * Add custom handler
   */
  addHandler(handler: AlertHandler): void {
    this.handlers.set(handler.name, handler);
  }

  /**
   * Add custom rule
   */
  addRule(rule: AlertRule): void {
    this.config.rules.push(rule);
  }

  /**
   * Remove rule
   */
  removeRule(ruleName: string): void {
    const index = this.config.rules.findIndex((r) => r.name === ruleName);
    if (index !== -1) {
      this.config.rules.splice(index, 1);
    }
  }

  /**
   * Cleanup
   */
  destroy(): void {
    if (this.batchTimer) {
      clearInterval(this.batchTimer);
    }
  }
}

/**
 * Built-in alert handlers
 */

/**
 * Console alert handler (for debugging)
 */
export const consoleAlertHandler: AlertHandler = {
  name: "console",
  async handle(alert: AuditAlert): Promise<void> {
    console.error("=".repeat(80));
    console.error(`🚨 SECURITY ALERT: ${alert.message}`);
    console.error(`Severity: ${alert.severity}`);
    console.error(`Events: ${alert.events.length}`);
    console.error(`Timestamp: ${alert.timestamp.toISOString()}`);
    console.error("=".repeat(80));
  },
};

/**
 * Email alert handler (placeholder - integrate with your email service)
 */
export const emailAlertHandler: AlertHandler = {
  name: "email",
  async handle(alert: AuditAlert): Promise<void> {
    // TODO: Integrate with email service (SendGrid, AWS SES, etc.)
    console.log("Email alert:", alert.message);
  },
};

/**
 * Slack alert handler (placeholder - integrate with Slack)
 */
export const slackAlertHandler: AlertHandler = {
  name: "slack",
  async handle(alert: AuditAlert): Promise<void> {
    // TODO: Integrate with Slack webhook
    console.log("Slack alert:", alert.message);
  },
};

/**
 * Webhook alert handler
 */
export function createWebhookAlertHandler(url: string): AlertHandler {
  return {
    name: "webhook",
    async handle(alert: AuditAlert): Promise<void> {
      try {
        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(alert),
        });
        if (!response.ok) {
          throw new Error(`Webhook failed: ${response.statusText}`);
        }
      } catch (error) {
        console.error("Failed to send webhook alert:", error);
      }
    },
  };
}
