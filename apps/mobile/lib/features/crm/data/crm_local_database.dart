/// CRM Local Database
/// قاعدة البيانات المحلية لإدارة علاقات المزارعين
///
/// Drift tables for offline-first CRM functionality
library;

import 'package:drift/drift.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Farmers Table
// ═══════════════════════════════════════════════════════════════════════════════

/// Farmers Table - جدول المزارعين
@TableIndex(name: 'farmers_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'farmers_status_idx', columns: {#status})
@TableIndex(name: 'farmers_segment_idx', columns: {#segment})
@TableIndex(name: 'farmers_synced_idx', columns: {#synced})
@TableIndex(name: 'farmers_deleted_idx', columns: {#isDeleted})
@TableIndex(name: 'farmers_agent_idx', columns: {#assignedAgentId})
@TableIndex(name: 'farmers_phone_idx', columns: {#phone})
@TableIndex(name: 'farmers_updated_idx', columns: {#updatedAt})
@TableIndex(name: 'farmers_tenant_status_idx', columns: {#tenantId, #status, #isDeleted})
class CrmFarmers extends Table {
  TextColumn get id => text()();
  TextColumn get tenantId => text()();
  TextColumn get remoteId => text().nullable()();

  // Basic information
  TextColumn get name => text()();
  TextColumn get nameAr => text().nullable()();
  TextColumn get phone => text()();
  TextColumn get phoneAlt => text().nullable()();
  TextColumn get whatsappNumber => text().nullable()();
  TextColumn get email => text().nullable()();
  TextColumn get nationalId => text().nullable()();
  TextColumn get avatarUrl => text().nullable()();

  // Location
  TextColumn get governorate => text().nullable()();
  TextColumn get district => text().nullable()();
  TextColumn get village => text().nullable()();
  TextColumn get address => text().nullable()();
  RealColumn get latitude => real().nullable()();
  RealColumn get longitude => real().nullable()();

  // Farm information
  RealColumn get totalAreaHectares => real().nullable()();
  TextColumn get mainCrops => text().withDefault(const Constant('[]'))(); // JSON array
  IntColumn get fieldCount => integer().nullable()();
  TextColumn get waterSource => text().nullable()();
  TextColumn get irrigationType => text().nullable()();

  // CRM information
  TextColumn get status => text().withDefault(const Constant('active'))();
  TextColumn get segment => text().withDefault(const Constant('regular'))();
  TextColumn get contactPreference => text().withDefault(const Constant('phone'))();
  TextColumn get languagePreference => text().withDefault(const Constant('arabic'))();
  TextColumn get assignedAgentId => text().nullable()();
  TextColumn get assignedAgentName => text().nullable()();
  TextColumn get leadSource => text().nullable()();
  TextColumn get tags => text().withDefault(const Constant('[]'))(); // JSON array
  TextColumn get notes => text().nullable()();

  // Statistics (cached)
  IntColumn get interactionCount => integer().withDefault(const Constant(0))();
  DateTimeColumn get lastInteractionAt => dateTime().nullable()();
  RealColumn get totalPurchaseValue => real().nullable()();
  RealColumn get lifetimeValue => real().nullable()();
  RealColumn get rating => real().nullable()();

  // Sync metadata
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
  BoolColumn get isDeleted => boolean().withDefault(const Constant(false))();
  TextColumn get etag => text().nullable()();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  DateTimeColumn get serverUpdatedAt => dateTime().nullable()();

  // Additional metadata
  TextColumn get metadata => text().nullable()(); // JSON

  @override
  Set<Column> get primaryKey => {id};
}

// ═══════════════════════════════════════════════════════════════════════════════
// Interactions Table
// ═══════════════════════════════════════════════════════════════════════════════

/// Interactions Table - جدول التفاعلات
@TableIndex(name: 'interactions_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'interactions_farmer_idx', columns: {#farmerId})
@TableIndex(name: 'interactions_type_idx', columns: {#type})
@TableIndex(name: 'interactions_outcome_idx', columns: {#outcome})
@TableIndex(name: 'interactions_synced_idx', columns: {#synced})
@TableIndex(name: 'interactions_deleted_idx', columns: {#isDeleted})
@TableIndex(name: 'interactions_follow_up_idx', columns: {#followUpAt})
@TableIndex(name: 'interactions_date_idx', columns: {#interactionAt})
@TableIndex(name: 'interactions_farmer_date_idx', columns: {#farmerId, #interactionAt})
class CrmInteractions extends Table {
  TextColumn get id => text()();
  TextColumn get tenantId => text()();
  TextColumn get remoteId => text().nullable()();
  TextColumn get farmerId => text()();
  TextColumn get farmerName => text().nullable()();

  // Interaction details
  TextColumn get type => text()();
  TextColumn get direction => text().withDefault(const Constant('outbound'))();
  TextColumn get outcome => text().withDefault(const Constant('pending'))();
  TextColumn get subject => text()();
  TextColumn get subjectAr => text().nullable()();
  TextColumn get description => text().nullable()();
  TextColumn get descriptionAr => text().nullable()();
  IntColumn get durationMinutes => integer().nullable()();

  // Dates
  DateTimeColumn get interactionAt => dateTime()();
  DateTimeColumn get followUpAt => dateTime().nullable()();
  TextColumn get followUpNotes => text().nullable()();

  // Agent
  TextColumn get agentId => text().nullable()();
  TextColumn get agentName => text().nullable()();

  // Location (for visits)
  RealColumn get latitude => real().nullable()();
  RealColumn get longitude => real().nullable()();
  TextColumn get locationName => text().nullable()();
  TextColumn get fieldId => text().nullable()();

  // Attachments (JSON arrays)
  TextColumn get photos => text().withDefault(const Constant('[]'))();
  TextColumn get documents => text().withDefault(const Constant('[]'))();
  TextColumn get voiceRecordingUrl => text().nullable()();

  // Related entities
  TextColumn get opportunityId => text().nullable()();
  TextColumn get taskId => text().nullable()();
  TextColumn get orderId => text().nullable()();

  // Metadata
  TextColumn get tags => text().withDefault(const Constant('[]'))();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
  BoolColumn get isDeleted => boolean().withDefault(const Constant(false))();
  TextColumn get etag => text().nullable()();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  TextColumn get metadata => text().nullable()();

  @override
  Set<Column> get primaryKey => {id};
}

// ═══════════════════════════════════════════════════════════════════════════════
// Opportunities Table
// ═══════════════════════════════════════════════════════════════════════════════

/// Opportunities Table - جدول الفرص البيعية
@TableIndex(name: 'opportunities_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'opportunities_farmer_idx', columns: {#farmerId})
@TableIndex(name: 'opportunities_stage_idx', columns: {#stage})
@TableIndex(name: 'opportunities_priority_idx', columns: {#priority})
@TableIndex(name: 'opportunities_synced_idx', columns: {#synced})
@TableIndex(name: 'opportunities_deleted_idx', columns: {#isDeleted})
@TableIndex(name: 'opportunities_agent_idx', columns: {#assignedAgentId})
@TableIndex(name: 'opportunities_close_date_idx', columns: {#expectedCloseDate})
@TableIndex(name: 'opportunities_tenant_stage_idx', columns: {#tenantId, #stage, #isDeleted})
class CrmOpportunities extends Table {
  TextColumn get id => text()();
  TextColumn get tenantId => text()();
  TextColumn get remoteId => text().nullable()();
  TextColumn get farmerId => text()();
  TextColumn get farmerName => text().nullable()();

  // Basic information
  TextColumn get name => text()();
  TextColumn get nameAr => text().nullable()();
  TextColumn get description => text().nullable()();
  TextColumn get descriptionAr => text().nullable()();
  TextColumn get type => text().withDefault(const Constant('newSale'))();
  TextColumn get stage => text().withDefault(const Constant('lead'))();
  TextColumn get priority => text().withDefault(const Constant('medium'))();

  // Financial
  RealColumn get expectedAmount => real()();
  TextColumn get currency => text().withDefault(const Constant('YER'))();
  IntColumn get probability => integer().withDefault(const Constant(50))();
  RealColumn get actualAmount => real().nullable()();

  // Products (JSON arrays)
  TextColumn get productIds => text().withDefault(const Constant('[]'))();
  TextColumn get productNames => text().withDefault(const Constant('[]'))();
  IntColumn get quantity => integer().nullable()();
  TextColumn get unit => text().nullable()();

  // Dates
  DateTimeColumn get expectedCloseDate => dateTime().nullable()();
  DateTimeColumn get actualCloseDate => dateTime().nullable()();
  DateTimeColumn get nextFollowUpAt => dateTime().nullable()();
  DateTimeColumn get lastActivityAt => dateTime().nullable()();

  // Assignment
  TextColumn get assignedAgentId => text().nullable()();
  TextColumn get assignedAgentName => text().nullable()();
  TextColumn get leadSource => text().nullable()();
  TextColumn get campaignId => text().nullable()();

  // Closure
  TextColumn get lossReason => text().nullable()();
  TextColumn get competitorName => text().nullable()();
  TextColumn get closeNotes => text().nullable()();

  // Related entities
  TextColumn get fieldIds => text().withDefault(const Constant('[]'))();
  TextColumn get orderId => text().nullable()();
  TextColumn get quoteId => text().nullable()();

  // Metadata
  TextColumn get tags => text().withDefault(const Constant('[]'))();
  TextColumn get notes => text().nullable()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
  BoolColumn get isDeleted => boolean().withDefault(const Constant(false))();
  TextColumn get etag => text().nullable()();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  TextColumn get metadata => text().nullable()();

  @override
  Set<Column> get primaryKey => {id};
}

// ═══════════════════════════════════════════════════════════════════════════════
// Activity Log Table
// ═══════════════════════════════════════════════════════════════════════════════

/// Activity Log Table - جدول سجل النشاط
@TableIndex(name: 'activity_log_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'activity_log_farmer_idx', columns: {#farmerId})
@TableIndex(name: 'activity_log_type_idx', columns: {#activityType})
@TableIndex(name: 'activity_log_date_idx', columns: {#activityAt})
@TableIndex(name: 'activity_log_farmer_date_idx', columns: {#farmerId, #activityAt})
class CrmActivityLogs extends Table {
  TextColumn get id => text()();
  TextColumn get tenantId => text()();
  TextColumn get farmerId => text()();
  TextColumn get farmerName => text().nullable()();

  // Activity details
  TextColumn get activityType => text()();
  TextColumn get source => text().withDefault(const Constant('manual'))();
  TextColumn get title => text()();
  TextColumn get titleAr => text().nullable()();
  TextColumn get description => text().nullable()();
  TextColumn get descriptionAr => text().nullable()();

  // Related entities
  TextColumn get interactionId => text().nullable()();
  TextColumn get opportunityId => text().nullable()();
  TextColumn get orderId => text().nullable()();
  TextColumn get fieldId => text().nullable()();
  TextColumn get taskId => text().nullable()();

  // Actor
  TextColumn get userId => text().nullable()();
  TextColumn get userName => text().nullable()();
  TextColumn get agentId => text().nullable()();
  TextColumn get agentName => text().nullable()();

  // Change tracking
  TextColumn get previousValue => text().nullable()();
  TextColumn get newValue => text().nullable()();
  TextColumn get changedField => text().nullable()();

  // Metadata
  DateTimeColumn get activityAt => dateTime()();
  IntColumn get durationMinutes => integer().nullable()();
  RealColumn get amount => real().nullable()();
  TextColumn get currency => text().nullable()();
  BoolColumn get isImportant => boolean().withDefault(const Constant(false))();
  TextColumn get tags => text().withDefault(const Constant('[]'))();
  TextColumn get metadata => text().nullable()();
  DateTimeColumn get createdAt => dateTime()();

  @override
  Set<Column> get primaryKey => {id};
}

// ═══════════════════════════════════════════════════════════════════════════════
// CRM Sync Status Table
// ═══════════════════════════════════════════════════════════════════════════════

/// CRM Sync Status Table - حالة مزامنة CRM
class CrmSyncStatus extends Table {
  TextColumn get entityType => text()(); // farmers, interactions, opportunities
  DateTimeColumn get lastSyncAt => dateTime().nullable()();
  IntColumn get syncedCount => integer().withDefault(const Constant(0))();
  IntColumn get pendingCount => integer().withDefault(const Constant(0))();
  TextColumn get lastError => text().nullable()();
  DateTimeColumn get updatedAt => dateTime()();

  @override
  Set<Column> get primaryKey => {entityType};
}
