/// SAHOOL Outbox Pattern Implementation
/// تنفيذ نمط صندوق الصادر للمزامنة
///
/// This module implements the transactional outbox pattern for reliable
/// offline-first data synchronization in the SAHOOL mobile app.
///
/// ## Features
///
/// - **Reliable Queuing**: All write operations are queued locally before sync
/// - **Priority-based Processing**: Critical operations processed first
/// - **Idempotency**: Duplicate operations are detected and handled
/// - **Exponential Backoff**: Automatic retry with increasing delays
/// - **Circuit Breaker**: Failing endpoints are temporarily disabled
/// - **Conflict Resolution**: Multiple strategies for handling conflicts
/// - **ETag Support**: Optimistic locking with server-side validation
/// - **Connectivity-aware**: Automatic sync when network is restored
///
/// ## Usage
///
/// ```dart
/// // Initialize services (typically in main.dart)
/// final db = AppDatabase();
/// final outboxService = OutboxService(database: db);
/// final processor = OutboxProcessor(
///   database: db,
///   outboxService: outboxService,
/// );
///
/// // Start processing
/// processor.start();
///
/// // Queue operations
/// await outboxService.enqueueCreate(
///   tenantId: 'tenant_123',
///   entityType: 'field',
///   entityId: 'field_456',
///   apiEndpoint: '/api/v1/fields',
///   payload: {'name': 'North Field', 'area': 10.5},
/// );
///
/// // Check sync status
/// final stats = await outboxService.getStats();
/// print('Pending: ${stats.pendingCount}');
///
/// // Force immediate sync
/// final result = await processor.processNow();
/// print('Synced: ${result.processed}');
/// ```
///
/// ## Architecture
///
/// ```
/// ┌─────────────────────────────────────────────────────────────┐
/// │                    SAHOOL Outbox Pattern                     │
/// ├─────────────────────────────────────────────────────────────┤
/// │                                                              │
/// │  ┌────────────┐    ┌────────────┐    ┌────────────────┐     │
/// │  │ Repository │───▶│  Outbox    │───▶│   Outbox       │     │
/// │  │ (write op) │    │  Service   │    │   Processor    │     │
/// │  └────────────┘    └────────────┘    └────────────────┘     │
/// │        │                 │                   │               │
/// │        │                 ▼                   ▼               │
/// │        │           ┌─────────┐         ┌─────────┐          │
/// │        └──────────▶│  Drift  │         │   API   │          │
/// │                    │   DB    │         │  Client │          │
/// │                    └─────────┘         └─────────┘          │
/// │                         │                   │               │
/// │                         │                   ▼               │
/// │                         │           ┌─────────────┐         │
/// │                         └──────────▶│  Conflict   │         │
/// │                                     │  Handler    │         │
/// │                                     └─────────────┘         │
/// │                                                              │
/// └─────────────────────────────────────────────────────────────┘
/// ```
library;

// Core models
export 'outbox_entry.dart';

// Database tables
export 'outbox_tables.dart';

// Services
export 'outbox_service.dart';

// Processing
export 'outbox_processor.dart';

// Conflict handling
export 'conflict_handler.dart';

// Status providers
export 'sync_status_provider.dart';

// UI widgets
export 'sync_status_widget.dart';
