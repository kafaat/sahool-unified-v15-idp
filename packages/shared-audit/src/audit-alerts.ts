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
  // ═══════════════════════════════════════════════════════════════════════════
  // AUTHENTICATION & ACCESS CONTROL RULES
  // ═══════════════════════════════════════════════════════════════════════════
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
    name: "unauthorized_access",
    description: "Unauthorized access attempt",
    conditions: [
      { field: "category", operator: "equals", value: AuditCategory.ACCESS },
      { field: "success", operator: "equals", value: false },
    ],
    severity: AuditSeverity.WARNING,
  },
  {
    name: "concurrent_session_detected",
    description: "Same user logged in from multiple IP addresses simultaneously",
    conditions: [
      { field: "action", operator: "equals", value: "auth.concurrent_session" },
      { field: "category", operator: "equals", value: AuditCategory.SECURITY },
    ],
    severity: AuditSeverity.WARNING,
  },
  {
    name: "session_hijack_attempt",
    description: "Potential session hijacking attempt detected",
    conditions: [
      { field: "action", operator: "equals", value: "auth.session_hijack" },
      { field: "category", operator: "equals", value: AuditCategory.SECURITY },
    ],
    severity: AuditSeverity.CRITICAL,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // DATA SECURITY RULES
  // ═══════════════════════════════════════════════════════════════════════════
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
    name: "bulk_data_export",
    description: "Large data export detected",
    conditions: [
      { field: "action", operator: "contains", value: "export" },
      { field: "category", operator: "equals", value: AuditCategory.DATA },
    ],
    severity: AuditSeverity.INFO,
  },
  {
    name: "sensitive_field_access",
    description: "Access to sensitive data fields (PII, financial, medical)",
    conditions: [
      { field: "action", operator: "contains", value: "sensitive" },
      { field: "category", operator: "equals", value: AuditCategory.DATA },
    ],
    severity: AuditSeverity.WARNING,
  },
  {
    name: "database_schema_change",
    description: "Database schema modification detected",
    conditions: [
      { field: "action", operator: "matches", value: "^db\\.(alter|drop|truncate)" },
      { field: "category", operator: "equals", value: AuditCategory.DATA },
    ],
    severity: AuditSeverity.CRITICAL,
  },
  {
    name: "bulk_record_modification",
    description: "Bulk record modification (>100 records) detected",
    conditions: [
      { field: "action", operator: "contains", value: "bulk_update" },
      { field: "category", operator: "equals", value: AuditCategory.DATA },
    ],
    severity: AuditSeverity.WARNING,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // CONFIGURATION & SECURITY RULES
  // ═══════════════════════════════════════════════════════════════════════════
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
    name: "role_permission_change",
    description: "User role or permission change without approval workflow",
    conditions: [
      { field: "action", operator: "matches", value: "^(role|permission)\\.(create|update|delete)" },
      { field: "category", operator: "equals", value: AuditCategory.ADMIN },
    ],
    severity: AuditSeverity.WARNING,
  },
  {
    name: "api_key_created",
    description: "New API key created",
    conditions: [
      { field: "action", operator: "equals", value: "api_key.create" },
      { field: "category", operator: "equals", value: AuditCategory.SECURITY },
    ],
    severity: AuditSeverity.INFO,
  },
  {
    name: "api_key_expiration_warning",
    description: "API key approaching expiration",
    conditions: [
      { field: "action", operator: "equals", value: "api_key.expiration_warning" },
      { field: "category", operator: "equals", value: AuditCategory.SECURITY },
    ],
    severity: AuditSeverity.WARNING,
  },
  {
    name: "encryption_key_rotation",
    description: "Encryption key rotation event",
    conditions: [
      { field: "action", operator: "equals", value: "encryption.key_rotation" },
      { field: "category", operator: "equals", value: AuditCategory.SECURITY },
    ],
    severity: AuditSeverity.INFO,
  },
  {
    name: "encryption_key_rotation_overdue",
    description: "Encryption key rotation is overdue",
    conditions: [
      { field: "action", operator: "equals", value: "encryption.rotation_overdue" },
      { field: "category", operator: "equals", value: AuditCategory.SECURITY },
    ],
    severity: AuditSeverity.CRITICAL,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // FINANCIAL & COMPLIANCE RULES
  // ═══════════════════════════════════════════════════════════════════════════
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
    name: "high_value_transaction",
    description: "High-value financial transaction detected",
    conditions: [
      { field: "action", operator: "contains", value: "transaction.high_value" },
      { field: "category", operator: "equals", value: AuditCategory.FINANCIAL },
    ],
    severity: AuditSeverity.WARNING,
  },
  {
    name: "compliance_violation",
    description: "Compliance policy violation detected",
    conditions: [
      { field: "action", operator: "contains", value: "compliance.violation" },
      { field: "category", operator: "equals", value: AuditCategory.COMPLIANCE },
    ],
    severity: AuditSeverity.CRITICAL,
  },
  {
    name: "data_retention_breach",
    description: "Data retention policy breach detected",
    conditions: [
      { field: "action", operator: "equals", value: "compliance.retention_breach" },
      { field: "category", operator: "equals", value: AuditCategory.COMPLIANCE },
    ],
    severity: AuditSeverity.ERROR,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // SYSTEM & INFRASTRUCTURE RULES
  // ═══════════════════════════════════════════════════════════════════════════
  {
    name: "critical_error",
    description: "Critical severity event occurred",
    conditions: [
      { field: "severity", operator: "equals", value: AuditSeverity.CRITICAL },
    ],
    severity: AuditSeverity.CRITICAL,
  },
  {
    name: "backup_verification_failure",
    description: "Backup verification failed",
    conditions: [
      { field: "action", operator: "equals", value: "backup.verification_failed" },
      { field: "category", operator: "equals", value: AuditCategory.SYSTEM },
    ],
    severity: AuditSeverity.CRITICAL,
  },
  {
    name: "backup_creation_failure",
    description: "Backup creation failed",
    conditions: [
      { field: "action", operator: "equals", value: "backup.creation_failed" },
      { field: "category", operator: "equals", value: AuditCategory.SYSTEM },
    ],
    severity: AuditSeverity.CRITICAL,
  },
  {
    name: "audit_storage_failure",
    description: "Audit log storage failure detected",
    conditions: [
      { field: "action", operator: "equals", value: "audit_storage_failure" },
      { field: "category", operator: "equals", value: AuditCategory.SYSTEM },
    ],
    severity: AuditSeverity.CRITICAL,
  },
  {
    name: "service_health_degraded",
    description: "Service health degradation detected",
    conditions: [
      { field: "action", operator: "equals", value: "service.health_degraded" },
      { field: "category", operator: "equals", value: AuditCategory.SYSTEM },
    ],
    severity: AuditSeverity.WARNING,
  },
  {
    name: "rate_limit_exceeded",
    description: "API rate limit exceeded",
    conditions: [
      { field: "action", operator: "equals", value: "api.rate_limit_exceeded" },
      { field: "category", operator: "equals", value: AuditCategory.SECURITY },
    ],
    severity: AuditSeverity.WARNING,
    batchSimilar: true,
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
const consoleHandlerLogger = new Logger("ConsoleAlertHandler");

export const consoleAlertHandler: AlertHandler = {
  name: "console",
  async handle(alert: AuditAlert): Promise<void> {
    consoleHandlerLogger.error("=".repeat(80));
    consoleHandlerLogger.error(`SECURITY ALERT: ${alert.message}`);
    consoleHandlerLogger.error(`Severity: ${alert.severity}`);
    consoleHandlerLogger.error(`Events: ${alert.events.length}`);
    consoleHandlerLogger.error(`Timestamp: ${alert.timestamp.toISOString()}`);
    consoleHandlerLogger.error("=".repeat(80));
  },
};

/**
 * Email configuration from environment variables
 */
interface EmailConfig {
  apiKey: string;
  fromAddress: string;
  toAddresses: string[];
}

/**
 * Email parameters for sending
 */
interface EmailParams {
  to: string[];
  subject: string;
  body: string;
  htmlBody?: string;
}

/**
 * Get email configuration from environment variables
 */
function getEmailConfig(): EmailConfig | null {
  const apiKey = process.env.EMAIL_SERVICE_API_KEY;
  const fromAddress = process.env.EMAIL_FROM_ADDRESS;
  const toAddresses = process.env.EMAIL_ALERT_RECIPIENTS?.split(",").map(
    (e: string) => e.trim(),
  );

  if (!apiKey || !fromAddress) {
    return null;
  }

  return {
    apiKey,
    fromAddress,
    toAddresses: toAddresses || [],
  };
}

/**
 * Logger for email handler
 */
const emailLogger = new Logger("EmailAlertHandler");

/**
 * Send email via SendGrid API
 */
async function sendEmail(params: EmailParams): Promise<void> {
  const config = getEmailConfig();

  if (!config) {
    emailLogger.warn(
      "Email service not configured. Set EMAIL_SERVICE_API_KEY and EMAIL_FROM_ADDRESS environment variables.",
    );
    return;
  }

  const recipients = params.to.length > 0 ? params.to : config.toAddresses;

  if (recipients.length === 0) {
    emailLogger.warn(
      "No email recipients configured. Set EMAIL_ALERT_RECIPIENTS environment variable.",
    );
    return;
  }

  emailLogger.log(
    `Sending email alert to ${recipients.length} recipient(s): ${params.subject}`,
  );

  const payload = {
    personalizations: [
      {
        to: recipients.map((email) => ({ email })),
      },
    ],
    from: { email: config.fromAddress },
    subject: params.subject,
    content: [
      {
        type: "text/plain",
        value: params.body,
      },
      ...(params.htmlBody
        ? [
            {
              type: "text/html",
              value: params.htmlBody,
            },
          ]
        : []),
    ],
  };

  try {
    const response = await fetch("https://api.sendgrid.com/v3/mail/send", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${config.apiKey}`,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `SendGrid API error: ${response.status} ${response.statusText} - ${errorText}`,
      );
    }

    emailLogger.log(`Email alert sent successfully to ${recipients.join(", ")}`);
  } catch (error) {
    emailLogger.error(
      `Failed to send email alert: ${error instanceof Error ? error.message : String(error)}`,
    );
    throw error;
  }
}

/**
 * Format alert as plain text for email body
 */
function formatAlertAsText(alert: AuditAlert): string {
  const lines = [
    `SECURITY ALERT: ${alert.rule}`,
    ``,
    `Severity: ${alert.severity.toUpperCase()}`,
    `Message: ${alert.message}`,
    `Timestamp: ${alert.timestamp.toISOString()}`,
    `Alert ID: ${alert.id}`,
    ``,
    `Events (${alert.events.length}):`,
  ];

  for (const event of alert.events.slice(0, 10)) {
    lines.push(
      `  - ${event.action} on ${event.resourceType}/${event.resourceId} by ${event.actorType}/${event.actorId || "system"}`,
    );
  }

  if (alert.events.length > 10) {
    lines.push(`  ... and ${alert.events.length - 10} more events`);
  }

  return lines.join("\n");
}

/**
 * Format alert as HTML for email body
 */
function formatAlertAsHtml(alert: AuditAlert): string {
  const severityColor =
    {
      critical: "#dc2626",
      error: "#ea580c",
      warning: "#ca8a04",
      info: "#2563eb",
      debug: "#6b7280",
    }[alert.severity] || "#6b7280";

  const eventRows = alert.events
    .slice(0, 10)
    .map(
      (event) =>
        `<tr>
          <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">${event.action}</td>
          <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">${event.resourceType}/${event.resourceId}</td>
          <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">${event.actorType}/${event.actorId || "system"}</td>
        </tr>`,
    )
    .join("");

  return `
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <div style="background-color: ${severityColor}; color: white; padding: 16px; border-radius: 8px 8px 0 0;">
        <h2 style="margin: 0;">Security Alert: ${alert.rule}</h2>
      </div>
      <div style="border: 1px solid #e5e7eb; border-top: none; padding: 16px; border-radius: 0 0 8px 8px;">
        <p><strong>Severity:</strong> ${alert.severity.toUpperCase()}</p>
        <p><strong>Message:</strong> ${alert.message}</p>
        <p><strong>Timestamp:</strong> ${alert.timestamp.toISOString()}</p>
        <p><strong>Alert ID:</strong> ${alert.id}</p>

        <h3>Events (${alert.events.length})</h3>
        <table style="width: 100%; border-collapse: collapse;">
          <thead>
            <tr style="background-color: #f3f4f6;">
              <th style="padding: 8px; text-align: left;">Action</th>
              <th style="padding: 8px; text-align: left;">Resource</th>
              <th style="padding: 8px; text-align: left;">Actor</th>
            </tr>
          </thead>
          <tbody>
            ${eventRows}
          </tbody>
        </table>
        ${alert.events.length > 10 ? `<p><em>... and ${alert.events.length - 10} more events</em></p>` : ""}
      </div>
    </div>
  `;
}

/**
 * Email alert handler - sends security alerts via email using SendGrid
 *
 * Required environment variables:
 * - EMAIL_SERVICE_API_KEY: SendGrid API key
 * - EMAIL_FROM_ADDRESS: Sender email address (must be verified in SendGrid)
 * - EMAIL_ALERT_RECIPIENTS: Comma-separated list of recipient email addresses
 */
export const emailAlertHandler: AlertHandler = {
  name: "email",
  async handle(alert: AuditAlert): Promise<void> {
    const subject = `[${alert.severity.toUpperCase()}] Security Alert: ${alert.rule}`;
    const body = formatAlertAsText(alert);
    const htmlBody = formatAlertAsHtml(alert);

    await sendEmail({
      to: [],
      subject,
      body,
      htmlBody,
    });
  },
};

/**
 * Slack severity color mapping
 */
const SLACK_SEVERITY_COLORS: Record<AuditSeverity, string> = {
  [AuditSeverity.DEBUG]: "#808080", // Gray
  [AuditSeverity.INFO]: "#36a64f", // Green
  [AuditSeverity.WARNING]: "#ff9900", // Orange
  [AuditSeverity.ERROR]: "#ff0000", // Red
  [AuditSeverity.CRITICAL]: "#8b0000", // Dark red
};

/**
 * Slack message payload interface
 */
interface SlackMessagePayload {
  channel?: string;
  text: string;
  attachments?: SlackAttachment[];
}

/**
 * Slack attachment interface
 */
interface SlackAttachment {
  color: string;
  title: string;
  text: string;
  fields?: Array<{
    title: string;
    value: string;
    short: boolean;
  }>;
  footer?: string;
  ts?: number;
}

/**
 * Logger for Slack handler
 */
const slackLogger = new Logger("SlackAlertHandler");

/**
 * Slack alert handler - sends audit alerts to Slack via webhook
 */
export const slackAlertHandler: AlertHandler = {
  name: "slack",
  async handle(alert: AuditAlert): Promise<void> {
    const webhookUrl = process.env.SLACK_WEBHOOK_URL;

    if (!webhookUrl) {
      slackLogger.warn(
        "SLACK_WEBHOOK_URL not configured, skipping Slack notification",
      );
      return;
    }

    slackLogger.log(
      `Sending Slack notification for alert: ${alert.rule} (severity: ${alert.severity})`,
    );

    const payload: SlackMessagePayload = {
      text: `Security Alert: ${alert.message}`,
      attachments: [
        {
          color: SLACK_SEVERITY_COLORS[alert.severity] || "#808080",
          title: `Alert: ${alert.rule}`,
          text: alert.message,
          fields: [
            {
              title: "Severity",
              value: alert.severity.toUpperCase(),
              short: true,
            },
            {
              title: "Events",
              value: String(alert.events.length),
              short: true,
            },
            {
              title: "Alert ID",
              value: alert.id,
              short: true,
            },
            {
              title: "Timestamp",
              value: alert.timestamp.toISOString(),
              short: true,
            },
          ],
          footer: "SAHOOL Audit System",
          ts: Math.floor(alert.timestamp.getTime() / 1000),
        },
      ],
    };

    // Add channel override if specified in environment
    const slackChannel = process.env.SLACK_ALERT_CHANNEL;
    if (slackChannel) {
      payload.channel = slackChannel;
    }

    try {
      const response = await fetch(webhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Slack webhook failed with status ${response.status}: ${errorText}`,
        );
      }

      slackLogger.log(
        `Slack notification sent successfully for alert: ${alert.id}`,
      );
    } catch (error) {
      slackLogger.error(
        `Failed to send Slack notification for alert ${alert.id}: ${error instanceof Error ? error.message : String(error)}`,
      );
      // Re-throw to allow upstream handling if needed
      throw error;
    }
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
        const webhookLogger = new Logger("WebhookAlertHandler");
        webhookLogger.error(
          `Failed to send webhook alert: ${error instanceof Error ? error.message : String(error)}`,
        );
      }
    },
  };
}
