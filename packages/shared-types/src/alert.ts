/**
 * SAHOOL Alert and Notification Types
 * Domain types for alerts, notifications, and real-time messaging
 *
 * Alerts notify farmers of critical conditions requiring immediate attention.
 * Notifications are general messages about system events and updates.
 */

import type {
  TenantEntity,
  Priority,
  ISODateTimeString,
} from "./common";

// ═══════════════════════════════════════════════════════════════════════════════
// Alert Severity and Status Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Alert severity levels
 * Determines visual treatment and escalation behavior
 */
export type AlertSeverity =
  | "info"      // Informational, no action needed
  | "warning"   // Potential issue, monitor closely
  | "critical"  // Requires prompt attention
  | "emergency"; // Immediate action required

/**
 * Alert category classifications
 */
export type AlertCategory =
  | "ndvi"           // Vegetation health anomaly
  | "weather"        // Weather-related alerts
  | "irrigation"     // Irrigation system issues
  | "pest"           // Pest detection
  | "disease"        // Disease detection
  | "nutrient"       // Nutrient deficiency
  | "water_stress"   // Water stress indicators
  | "heat_stress"    // Heat stress indicators
  | "frost"          // Frost warning
  | "equipment"      // Equipment malfunction
  | "sensor"         // Sensor offline/error
  | "harvest"        // Harvest timing
  | "compliance"     // Regulatory compliance
  | "system";        // System notifications

/**
 * Alert lifecycle status
 */
export type AlertStatus =
  | "active"       // Currently active, needs attention
  | "acknowledged" // Seen but not resolved
  | "in_progress"  // Being addressed
  | "resolved"     // Issue resolved
  | "dismissed"    // Manually dismissed
  | "expired";     // Auto-expired after time window

// ═══════════════════════════════════════════════════════════════════════════════
// Alert Entity Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Core alert entity
 */
export interface Alert extends TenantEntity {
  /** Alert title */
  title: string;
  /** Title in Arabic */
  titleAr?: string;
  /** Detailed message */
  message: string;
  /** Message in Arabic */
  messageAr?: string;
  /** Severity level */
  severity: AlertSeverity;
  /** Alert category */
  category: AlertCategory;
  /** Current status */
  status: AlertStatus;
  /** Associated field ID */
  fieldId?: string;
  /** Field name (denormalized for display) */
  fieldName?: string;
  /** Associated farm ID */
  farmId?: string;
  /** Farm name (denormalized for display) */
  farmName?: string;
  /** Alert source system/service */
  source?: string;
  /** Detection/trigger timestamp */
  triggeredAt: ISODateTimeString;
  /** Acknowledgment timestamp */
  acknowledgedAt?: ISODateTimeString;
  /** Acknowledged by user ID */
  acknowledgedBy?: string;
  /** Resolution timestamp */
  resolvedAt?: ISODateTimeString;
  /** Resolved by user ID */
  resolvedBy?: string;
  /** Resolution notes */
  resolutionNotes?: string;
  /** Expiration timestamp */
  expiresAt?: ISODateTimeString;
  /** Whether alert has been read */
  read: boolean;
  /** Read timestamp */
  readAt?: ISODateTimeString;
  /** Recommended action */
  recommendedAction?: string;
  /** Recommended action in Arabic */
  recommendedActionAr?: string;
  /** Link to detailed view/action */
  actionUrl?: string;
  /** Related alert IDs (for correlated alerts) */
  relatedAlertIds?: string[];
  /** Threshold value that triggered alert */
  thresholdValue?: number;
  /** Actual value that exceeded threshold */
  actualValue?: number;
  /** Unit for threshold/actual values */
  valueUnit?: string;
  /** Additional metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Alert rule definition (for configuring automated alerts)
 */
export interface AlertRule {
  /** Rule ID */
  id: string;
  /** Tenant ID */
  tenantId: string;
  /** Rule name */
  name: string;
  /** Rule name in Arabic */
  nameAr?: string;
  /** Rule description */
  description?: string;
  /** Alert category this rule applies to */
  category: AlertCategory;
  /** Severity when triggered */
  severity: AlertSeverity;
  /** Condition type */
  conditionType: "threshold" | "change" | "absence" | "pattern";
  /** Field to monitor */
  monitoredField: string;
  /** Comparison operator */
  operator: "gt" | "gte" | "lt" | "lte" | "eq" | "neq";
  /** Threshold value */
  thresholdValue: number;
  /** Time window for evaluation (minutes) */
  evaluationWindowMin?: number;
  /** Minimum occurrences before triggering */
  minOccurrences?: number;
  /** Cooldown period between alerts (minutes) */
  cooldownMin?: number;
  /** Whether rule is enabled */
  enabled: boolean;
  /** Notification channels */
  notificationChannels?: NotificationChannel[];
  /** Recipient user IDs */
  recipientIds?: string[];
  /** Fields/farms this rule applies to */
  scope?: {
    fieldIds?: string[];
    farmIds?: string[];
    cropTypes?: string[];
  };
  /** Custom message template */
  messageTemplate?: string;
  /** Message template in Arabic */
  messageTemplateAr?: string;
  /** Created timestamp */
  createdAt: string;
  /** Last updated timestamp */
  updatedAt: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Notification Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Notification channel types
 */
export type NotificationChannel =
  | "in_app"    // In-application notification
  | "push"      // Mobile push notification
  | "sms"       // SMS text message
  | "email"     // Email notification
  | "whatsapp"  // WhatsApp message
  | "webhook";  // Webhook callback

/**
 * Notification type categories
 */
export type NotificationType =
  | "alert"           // From an alert
  | "task_assigned"   // Task assignment
  | "task_due"        // Task due reminder
  | "task_completed"  // Task completion
  | "advisory"        // Advisory/recommendation
  | "report_ready"    // Report generated
  | "system"          // System notification
  | "announcement"    // Platform announcement
  | "chat"            // Chat message
  | "mention";        // User mention

/**
 * Core notification entity
 */
export interface Notification extends TenantEntity {
  /** Notification type */
  type: NotificationType;
  /** Title */
  title: string;
  /** Title in Arabic */
  titleAr?: string;
  /** Message body */
  message: string;
  /** Message in Arabic */
  messageAr?: string;
  /** Priority level */
  priority: Priority;
  /** Recipient user ID */
  recipientId: string;
  /** Sender user ID (if applicable) */
  senderId?: string;
  /** Delivery channel */
  channel: NotificationChannel;
  /** Whether notification has been read */
  read: boolean;
  /** Read timestamp */
  readAt?: ISODateTimeString;
  /** Delivery status */
  deliveryStatus: "pending" | "sent" | "delivered" | "failed";
  /** Delivery timestamp */
  deliveredAt?: ISODateTimeString;
  /** Failure reason (if failed) */
  failureReason?: string;
  /** Action URL */
  actionUrl?: string;
  /** Action label */
  actionLabel?: string;
  /** Related entity type */
  relatedEntityType?: "alert" | "task" | "field" | "farm" | "report" | "chat";
  /** Related entity ID */
  relatedEntityId?: string;
  /** Icon identifier */
  icon?: string;
  /** Image URL */
  imageUrl?: string;
  /** Expiration timestamp */
  expiresAt?: ISODateTimeString;
  /** Additional data */
  data?: Record<string, unknown>;
}

/**
 * Notification preference settings
 */
export interface NotificationPreferences {
  /** User ID */
  userId: string;
  /** Enabled channels */
  enabledChannels: NotificationChannel[];
  /** Quiet hours start (HH:mm format) */
  quietHoursStart?: string;
  /** Quiet hours end (HH:mm format) */
  quietHoursEnd?: string;
  /** Minimum severity for push notifications */
  pushMinSeverity?: AlertSeverity;
  /** Enabled notification types */
  enabledTypes: NotificationType[];
  /** Email digest frequency */
  emailDigestFrequency?: "realtime" | "hourly" | "daily" | "weekly" | "none";
  /** Preferred language */
  preferredLanguage?: "ar" | "en";
  /** Custom settings per category */
  categorySettings?: Record<AlertCategory, {
    enabled: boolean;
    channels: NotificationChannel[];
    minSeverity?: AlertSeverity;
  }>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Alert Statistics Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Alert statistics summary
 */
export interface AlertStats {
  /** Total alerts */
  total: number;
  /** Active alerts */
  active: number;
  /** Acknowledged alerts */
  acknowledged: number;
  /** Resolved alerts */
  resolved: number;
  /** Dismissed alerts */
  dismissed: number;
  /** Alerts by severity */
  bySeverity: Record<AlertSeverity, number>;
  /** Alerts by category */
  byCategory: Record<AlertCategory, number>;
  /** Average time to acknowledge (minutes) */
  avgAcknowledgeTimeMin?: number;
  /** Average time to resolve (minutes) */
  avgResolveTimeMin?: number;
  /** Alerts in last 24 hours */
  last24Hours: number;
  /** Alerts in last 7 days */
  last7Days: number;
}

/**
 * Alert trend data point
 */
export interface AlertTrendPoint {
  /** Date */
  date: string;
  /** Count */
  count: number;
  /** Breakdown by severity */
  bySeverity?: Record<AlertSeverity, number>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Alert Request/Response Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Filters for querying alerts
 */
export interface AlertFilters {
  /** Filter by severity */
  severity?: AlertSeverity | AlertSeverity[];
  /** Filter by category */
  category?: AlertCategory | AlertCategory[];
  /** Filter by status */
  status?: AlertStatus | AlertStatus[];
  /** Filter by field */
  fieldId?: string;
  /** Filter by farm */
  farmId?: string;
  /** Filter by date range start */
  startDate?: string;
  /** Filter by date range end */
  endDate?: string;
  /** Filter by read status */
  read?: boolean;
  /** Search in title/message */
  search?: string;
}

/**
 * Request to acknowledge an alert
 */
export interface AcknowledgeAlertRequest {
  /** Alert ID */
  alertId: string;
  /** Acknowledgment notes */
  notes?: string;
}

/**
 * Request to resolve an alert
 */
export interface ResolveAlertRequest {
  /** Alert ID */
  alertId: string;
  /** Resolution notes */
  notes: string;
  /** Resolution notes in Arabic */
  notesAr?: string;
  /** Action taken */
  actionTaken?: string;
}

/**
 * Batch alert update request
 */
export interface BatchAlertUpdateRequest {
  /** Alert IDs to update */
  alertIds: string[];
  /** New status */
  status: AlertStatus;
  /** Notes */
  notes?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Type Guards
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Type guard for Alert
 */
export function isAlert(obj: unknown): obj is Alert {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "title" in obj &&
    "severity" in obj &&
    "category" in obj &&
    "status" in obj
  );
}

/**
 * Type guard for valid AlertSeverity
 */
export function isAlertSeverity(value: unknown): value is AlertSeverity {
  const validSeverities: AlertSeverity[] = ["info", "warning", "critical", "emergency"];
  return typeof value === "string" && validSeverities.includes(value as AlertSeverity);
}

/**
 * Type guard for valid AlertStatus
 */
export function isAlertStatus(value: unknown): value is AlertStatus {
  const validStatuses: AlertStatus[] = [
    "active",
    "acknowledged",
    "in_progress",
    "resolved",
    "dismissed",
    "expired",
  ];
  return typeof value === "string" && validStatuses.includes(value as AlertStatus);
}

/**
 * Type guard for Notification
 */
export function isNotification(obj: unknown): obj is Notification {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "type" in obj &&
    "title" in obj &&
    "recipientId" in obj
  );
}

/**
 * Check if alert is critical or emergency
 */
export function isCriticalAlert(alert: Alert): boolean {
  return alert.severity === "critical" || alert.severity === "emergency";
}

/**
 * Check if alert requires immediate action
 */
export function requiresImmediateAction(alert: Alert): boolean {
  return (
    alert.status === "active" &&
    (alert.severity === "critical" || alert.severity === "emergency")
  );
}
