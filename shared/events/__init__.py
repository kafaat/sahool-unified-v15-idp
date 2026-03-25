"""
SAHOOL Events Module
====================
نظام الأحداث الموزع لمنصة سهول

Event schemas, models, publishers, and subscribers for event-driven architecture.

Exports:
    - Event contracts (Pydantic models) for type-safe event handling
    - NATS subject constants
    - EventPublisher for publishing events
    - EventSubscriber for consuming events
    - Legacy event models from models.py
    - JSON schemas are in shared/contracts/events/

Usage:
    # Publishing events
    from shared.events import EventPublisher, FieldCreatedEvent, SAHOOL_FIELD_CREATED

    publisher = EventPublisher()
    await publisher.connect()

    event = FieldCreatedEvent(field_id=..., farm_id=..., name="Field 1")
    await publisher.publish_event(SAHOOL_FIELD_CREATED, event)

    # Subscribing to events
    from shared.events import EventSubscriber, SAHOOL_FIELD_ALL

    subscriber = EventSubscriber()
    await subscriber.connect()

    async def handle_field_event(event):
        print(f"Field event: {event}")

    await subscriber.subscribe(SAHOOL_FIELD_ALL, handle_field_event)
    await subscriber.run()
"""

# Legacy event models (for backward compatibility)
# New event contracts
from .contracts import (
    AgentExecutionCompletedEvent,
    AgentExecutionFailedEvent,
    # AI Agent events
    AgentExecutionStartedEvent,
    AgentStepCompletedEvent,
    BaseEvent,
    BatchExpiredEvent,
    CropStressEvent,
    DataModelCreatedEvent,
    # Health events
    DiseaseDetectedEvent,
    # CRM/Farmer events
    FarmerCreatedEvent,
    FarmerStatusChangedEvent,
    FarmerUpdatedEvent,
    # Field events
    FieldCreatedEvent,
    FieldDeletedEvent,
    FieldUpdatedEvent,
    HarvestDealCreatedEvent,
    HarvestDealStageChangedEvent,
    InteractionLoggedEvent,
    # Inventory events
    LowStockEvent,
    # Low-Code events
    PageCreatedEvent,
    PagePublishedEvent,
    PaymentCompletedEvent,
    PaymentFailedEvent,
    SatelliteAnomalyEvent,
    # Satellite events
    SatelliteDataReadyEvent,
    # Billing events
    SubscriptionCreatedEvent,
    SubscriptionRenewedEvent,
    WeatherAlertEvent,
    # Weather events
    WeatherForecastEvent,
    WeChatChatSummarizedEvent,
    WeChatContactAddedEvent,
    # WeChat events
    WeChatMessageReceivedEvent,
    WeChatMessageSentEvent,
    WeChatMomentPublishedEvent,
    WorkflowExecutedEvent,
)

# DLQ Support
from .dlq_config import (
    DLQConfig,
    DLQMessageMetadata,
    create_dlq_streams,
    is_retriable_error,
    should_retry,
)
from .dlq_monitoring import (
    DLQAlert,
    DLQMonitor,
)

# Outbox Pattern (transactional event publishing)
from .outbox import (
    OutboxRelay,
    ensure_outbox_table,
    write_outbox_event,
)

try:
    from .dlq_service import (
        DLQManager,
        create_dlq_router,
    )
except ImportError:
    DLQManager = None  # type: ignore[assignment,misc]
    create_dlq_router = None  # type: ignore[assignment]

# Edge device events
from .edge_events import (
    SAHOOL_EDGE_ALL,
    SAHOOL_EDGE_DATA_COLLECTED,
    SAHOOL_EDGE_DEVICE_ERROR,
    SAHOOL_EDGE_DEVICE_HEALTH_UPDATE,
    SAHOOL_EDGE_DEVICE_OFFLINE,
    SAHOOL_EDGE_DEVICE_ONLINE,
    SAHOOL_EDGE_DEVICE_REGISTERED,
    SAHOOL_EDGE_FIRMWARE_UPDATE_AVAILABLE,
    SAHOOL_EDGE_JOB_COMPLETED,
    SAHOOL_EDGE_JOB_FAILED,
    SAHOOL_EDGE_JOB_PROGRESS,
    SAHOOL_EDGE_JOB_QUEUED,
    SAHOOL_EDGE_JOB_STARTED,
    SAHOOL_EDGE_MODEL_DEPLOYED,
    SAHOOL_EDGE_MODEL_DEPLOYMENT_FAILED,
    SAHOOL_EDGE_MODEL_DEPLOYMENT_STARTED,
    SAHOOL_EDGE_SYNC_COMPLETED,
    SAHOOL_EDGE_SYNC_CONFLICT,
    SAHOOL_EDGE_SYNC_FAILED,
    SAHOOL_EDGE_SYNC_STARTED,
    DataCollectedEvent,
    DataUploadedEvent,
    DeviceCapabilities,
    DeviceErrorEvent,
    DeviceHealth,
    DeviceHealthUpdateEvent,
    DeviceOfflineEvent,
    DeviceOnlineEvent,
    DeviceRegisteredEvent,
    EdgeSubjects,
    FirmwareUpdateAvailableEvent,
    FirmwareUpdateCompletedEvent,
    JobCancelledEvent,
    JobCompletedEvent,
    JobFailedEvent,
    JobProgressEvent,
    JobQueuedEvent,
    JobResult,
    JobStartedEvent,
    ModelDeployedEvent,
    ModelDeploymentFailedEvent,
    ModelDeploymentStartedEvent,
    ModelRollbackEvent,
    NetworkStatus,
    SyncCompletedEvent,
    SyncConflictEvent,
    SyncFailedEvent,
    SyncProgressEvent,
    SyncStartedEvent,
    SyncStatistics,
)
from .models import (
    AdvisorRecommendationEvent,
    AlertCreatedEvent,
    CropPlantedEvent,
    FarmCreatedEvent,
    TaskCompletedEvent,
    TaskCreatedEvent,
)
from .models import (
    BaseEvent as LegacyBaseEvent,
)
from .models import (
    FieldCreatedEvent as LegacyFieldCreatedEvent,
)
from .models import (
    FieldUpdatedEvent as LegacyFieldUpdatedEvent,
)

# Publisher and Subscriber
from .publisher import (
    EventPublisher,
    PublisherConfig,
    chain_event,
    close_publisher,
    get_publisher,
    publish_event,
)

# NATS subject constants
from .subjects import (
    SAHOOL_AGENT_ALL,
    SAHOOL_AGENT_EXECUTION_ALL,
    SAHOOL_AGENT_EXECUTION_COMPLETED,
    SAHOOL_AGENT_EXECUTION_FAILED,
    # Agent subjects
    SAHOOL_AGENT_EXECUTION_STARTED,
    SAHOOL_AGENT_FARM_ADVISOR,
    SAHOOL_AGENT_PLANNER,
    SAHOOL_AGENT_RESEARCH,
    SAHOOL_AGENT_STEP_COMPLETED,
    SAHOOL_ALERT_ACKNOWLEDGED,
    SAHOOL_ALERT_ALL,
    # Alert subjects
    SAHOOL_ALERT_CREATED,
    SAHOOL_ALERT_RESOLVED,
    # Billing subjects
    SAHOOL_BILLING_ALL,
    SAHOOL_BILLING_PAYMENT_COMPLETED,
    SAHOOL_BILLING_PAYMENT_FAILED,
    SAHOOL_BILLING_SUBSCRIPTION_CREATED,
    SAHOOL_FARMER_ALL,
    # Farmer subjects
    SAHOOL_FARMER_CREATED,
    SAHOOL_FARMER_STATUS_CHANGED,
    SAHOOL_FARMER_UPDATED,
    # Field subjects
    SAHOOL_FIELD_ALL,
    SAHOOL_FIELD_CREATED,
    SAHOOL_FIELD_DELETED,
    SAHOOL_FIELD_UPDATED,
    SAHOOL_HARVEST_ALL,
    # Harvest subjects
    SAHOOL_HARVEST_DEAL_CREATED,
    SAHOOL_HARVEST_DEAL_STAGE_CHANGED,
    # Health subjects
    SAHOOL_HEALTH_ALL,
    SAHOOL_HEALTH_DISEASE_DETECTED,
    SAHOOL_HEALTH_STRESS_DETECTED,
    SAHOOL_INTERACTION_ALL,
    # Interaction subjects
    SAHOOL_INTERACTION_LOGGED,
    # Inventory subjects
    SAHOOL_INVENTORY_ALL,
    SAHOOL_INVENTORY_BATCH_EXPIRED,
    SAHOOL_INVENTORY_LOW_STOCK,
    # Satellite subjects
    SAHOOL_NDVI_COMPUTED,
    SAHOOL_RECOMMENDATION_ALL,
    # Recommendation subjects
    SAHOOL_RECOMMENDATION_CREATED,
    SAHOOL_RECOMMENDATION_FERTILIZER,
    SAHOOL_RECOMMENDATION_HARVEST,
    SAHOOL_RECOMMENDATION_IRRIGATION,
    SAHOOL_RECOMMENDATION_PEST_CONTROL,
    SAHOOL_SATELLITE_ALL,
    SAHOOL_SATELLITE_ANOMALY,
    SAHOOL_SATELLITE_DATA_READY,
    SAHOOL_TASK_ALL,
    SAHOOL_TASK_ASSIGNED,
    SAHOOL_TASK_COMPLETED,
    # Task subjects
    SAHOOL_TASK_CREATED,
    SAHOOL_TASK_DELETED,
    SAHOOL_TASK_UPDATED,
    # Weather subjects
    SAHOOL_WEATHER_ALERT,
    SAHOOL_WEATHER_ALL,
    SAHOOL_WEATHER_FORECAST,
    # Utility functions
    get_subject_for_event,
    lookup_subject,
)
from .subscriber import (
    EventSubscriber,
    SubscriberConfig,
    close_subscriber,
    get_subscriber,
)

# Terrain analysis events
from .terrain_events import (
    SAHOOL_TERRAIN_ALL,
    SAHOOL_TERRAIN_ANALYSIS_COMPLETED,
    SAHOOL_TERRAIN_ANALYSIS_FAILED,
    SAHOOL_TERRAIN_ANALYSIS_STARTED,
    SAHOOL_TERRAIN_DEM_UPDATED,
    SAHOOL_TERRAIN_DRAINAGE_ISSUE,
    SAHOOL_TERRAIN_DRAINAGE_RECOMMENDED,
    SAHOOL_TERRAIN_HIGH_EROSION_RISK,
    SAHOOL_TERRAIN_LEVELING_RECOMMENDED,
    SAHOOL_TERRAIN_WATERLOGGING_DETECTED,
    ContourFarmingRecommendedEvent,
    DEMUpdatedEvent,
    DrainageIssueEvent,
    DrainageRecommendedEvent,
    DrainageZone,
    ElevationStatistics,
    ErosionZone,
    HighErosionRiskEvent,
    LevelingRecommendedEvent,
    LevelingZone,
    SlopeStatistics,
    TerrainAnalysisCompletedEvent,
    TerrainAnalysisFailedEvent,
    TerrainAnalysisStartedEvent,
    TerrainSubjects,
    WaterloggingDetectedEvent,
)

# Vision events (YOLO26 detection)
from .vision_events import (
    SAHOOL_VISION_ALL,
    SAHOOL_VISION_ANALYSIS_COMPLETED,
    SAHOOL_VISION_ANALYSIS_FAILED,
    SAHOOL_VISION_ANALYSIS_STARTED,
    SAHOOL_VISION_CRITICAL_ALERT,
    SAHOOL_VISION_DISEASE_DETECTED,
    SAHOOL_VISION_PEST_DETECTED,
    SAHOOL_VISION_PLANT_COUNT_COMPLETED,
    SAHOOL_VISION_WEED_DETECTED,
    BoundingBox,
    GeoLocation,
    PestDetectedEvent,
    PlantCountCompletedEvent,
    VisionAnalysisCompletedEvent,
    VisionAnalysisFailedEvent,
    VisionAnalysisStartedEvent,
    VisionCriticalAlertEvent,
    VisionDiseaseDetectedEvent,
    VisionSubjects,
    WeedDetectedEvent,
)

__all__ = [
    # Base
    "BaseEvent",
    # Event Contracts - Field
    "FieldCreatedEvent",
    "FieldUpdatedEvent",
    "FieldDeletedEvent",
    # Event Contracts - Weather
    "WeatherForecastEvent",
    "WeatherAlertEvent",
    # Event Contracts - Satellite
    "SatelliteDataReadyEvent",
    "SatelliteAnomalyEvent",
    # Event Contracts - Health
    "DiseaseDetectedEvent",
    "CropStressEvent",
    # Event Contracts - Inventory
    "LowStockEvent",
    "BatchExpiredEvent",
    # Event Contracts - Billing
    "SubscriptionCreatedEvent",
    "PaymentCompletedEvent",
    "SubscriptionRenewedEvent",
    "PaymentFailedEvent",
    # Event Contracts - AI Agent
    "AgentExecutionStartedEvent",
    "AgentExecutionCompletedEvent",
    "AgentExecutionFailedEvent",
    "AgentStepCompletedEvent",
    # Event Contracts - Farmer/CRM
    "FarmerCreatedEvent",
    "FarmerUpdatedEvent",
    "FarmerStatusChangedEvent",
    "HarvestDealCreatedEvent",
    "HarvestDealStageChangedEvent",
    "InteractionLoggedEvent",
    # Event Contracts - Low-Code
    "PageCreatedEvent",
    "PagePublishedEvent",
    "DataModelCreatedEvent",
    "WorkflowExecutedEvent",
    # Event Contracts - WeChat
    "WeChatMessageReceivedEvent",
    "WeChatMessageSentEvent",
    "WeChatContactAddedEvent",
    "WeChatMomentPublishedEvent",
    "WeChatChatSummarizedEvent",
    # Legacy events (backward compatibility)
    "LegacyBaseEvent",
    "LegacyFieldCreatedEvent",
    "LegacyFieldUpdatedEvent",
    "FarmCreatedEvent",
    "CropPlantedEvent",
    "TaskCreatedEvent",
    "TaskCompletedEvent",
    "AdvisorRecommendationEvent",
    "AlertCreatedEvent",
    # NATS Subjects - Agent
    "SAHOOL_AGENT_EXECUTION_STARTED",
    "SAHOOL_AGENT_EXECUTION_COMPLETED",
    "SAHOOL_AGENT_EXECUTION_FAILED",
    "SAHOOL_AGENT_STEP_COMPLETED",
    "SAHOOL_AGENT_FARM_ADVISOR",
    "SAHOOL_AGENT_RESEARCH",
    "SAHOOL_AGENT_PLANNER",
    "SAHOOL_AGENT_ALL",
    "SAHOOL_AGENT_EXECUTION_ALL",
    # NATS Subjects - Farmer
    "SAHOOL_FARMER_CREATED",
    "SAHOOL_FARMER_UPDATED",
    "SAHOOL_FARMER_STATUS_CHANGED",
    "SAHOOL_FARMER_ALL",
    # NATS Subjects - Harvest
    "SAHOOL_HARVEST_DEAL_CREATED",
    "SAHOOL_HARVEST_DEAL_STAGE_CHANGED",
    "SAHOOL_HARVEST_ALL",
    # NATS Subjects - Interaction
    "SAHOOL_INTERACTION_LOGGED",
    "SAHOOL_INTERACTION_ALL",
    # NATS Subjects - Task
    "SAHOOL_TASK_CREATED",
    "SAHOOL_TASK_UPDATED",
    "SAHOOL_TASK_COMPLETED",
    "SAHOOL_TASK_DELETED",
    "SAHOOL_TASK_ASSIGNED",
    "SAHOOL_TASK_ALL",
    # NATS Subjects - Recommendation
    "SAHOOL_RECOMMENDATION_CREATED",
    "SAHOOL_RECOMMENDATION_IRRIGATION",
    "SAHOOL_RECOMMENDATION_FERTILIZER",
    "SAHOOL_RECOMMENDATION_PEST_CONTROL",
    "SAHOOL_RECOMMENDATION_HARVEST",
    "SAHOOL_RECOMMENDATION_ALL",
    # NATS Subjects - Alert
    "SAHOOL_ALERT_CREATED",
    "SAHOOL_ALERT_ACKNOWLEDGED",
    "SAHOOL_ALERT_RESOLVED",
    "SAHOOL_ALERT_ALL",
    # NATS Subjects - Field
    "SAHOOL_FIELD_CREATED",
    "SAHOOL_FIELD_UPDATED",
    "SAHOOL_FIELD_DELETED",
    "SAHOOL_FIELD_ALL",
    # NATS Subjects - Weather
    "SAHOOL_WEATHER_FORECAST",
    "SAHOOL_WEATHER_ALERT",
    "SAHOOL_WEATHER_ALL",
    # NATS Subjects - Satellite
    "SAHOOL_SATELLITE_DATA_READY",
    "SAHOOL_SATELLITE_ANOMALY",
    "SAHOOL_SATELLITE_ALL",
    "SAHOOL_NDVI_COMPUTED",
    # NATS Subjects - Health
    "SAHOOL_HEALTH_DISEASE_DETECTED",
    "SAHOOL_HEALTH_STRESS_DETECTED",
    "SAHOOL_HEALTH_ALL",
    # NATS Subjects - Inventory
    "SAHOOL_INVENTORY_LOW_STOCK",
    "SAHOOL_INVENTORY_BATCH_EXPIRED",
    "SAHOOL_INVENTORY_ALL",
    # NATS Subjects - Billing
    "SAHOOL_BILLING_SUBSCRIPTION_CREATED",
    "SAHOOL_BILLING_PAYMENT_COMPLETED",
    "SAHOOL_BILLING_PAYMENT_FAILED",
    "SAHOOL_BILLING_ALL",
    # Subject utilities
    "get_subject_for_event",
    "lookup_subject",
    # Publisher
    "EventPublisher",
    "PublisherConfig",
    "get_publisher",
    "close_publisher",
    "publish_event",
    "chain_event",
    # Outbox Pattern
    "OutboxRelay",
    "write_outbox_event",
    "ensure_outbox_table",
    # Subscriber
    "EventSubscriber",
    "SubscriberConfig",
    "get_subscriber",
    "close_subscriber",
    # DLQ Configuration
    "DLQConfig",
    "DLQMessageMetadata",
    "create_dlq_streams",
    "is_retriable_error",
    "should_retry",
    # DLQ Management
    "DLQManager",
    "create_dlq_router",
    # DLQ Monitoring
    "DLQMonitor",
    "DLQAlert",
    # Vision Events (YOLO26)
    "VisionSubjects",
    "BoundingBox",
    "GeoLocation",
    "PestDetectedEvent",
    "VisionDiseaseDetectedEvent",
    "WeedDetectedEvent",
    "PlantCountCompletedEvent",
    "VisionCriticalAlertEvent",
    "VisionAnalysisStartedEvent",
    "VisionAnalysisCompletedEvent",
    "VisionAnalysisFailedEvent",
    "SAHOOL_VISION_PEST_DETECTED",
    "SAHOOL_VISION_DISEASE_DETECTED",
    "SAHOOL_VISION_WEED_DETECTED",
    "SAHOOL_VISION_PLANT_COUNT_COMPLETED",
    "SAHOOL_VISION_CRITICAL_ALERT",
    "SAHOOL_VISION_ANALYSIS_STARTED",
    "SAHOOL_VISION_ANALYSIS_COMPLETED",
    "SAHOOL_VISION_ANALYSIS_FAILED",
    "SAHOOL_VISION_ALL",
    # Terrain Events
    "TerrainSubjects",
    "ElevationStatistics",
    "SlopeStatistics",
    "DrainageZone",
    "ErosionZone",
    "LevelingZone",
    "TerrainAnalysisStartedEvent",
    "TerrainAnalysisCompletedEvent",
    "TerrainAnalysisFailedEvent",
    "HighErosionRiskEvent",
    "WaterloggingDetectedEvent",
    "DrainageIssueEvent",
    "LevelingRecommendedEvent",
    "DrainageRecommendedEvent",
    "ContourFarmingRecommendedEvent",
    "DEMUpdatedEvent",
    "SAHOOL_TERRAIN_ANALYSIS_STARTED",
    "SAHOOL_TERRAIN_ANALYSIS_COMPLETED",
    "SAHOOL_TERRAIN_ANALYSIS_FAILED",
    "SAHOOL_TERRAIN_HIGH_EROSION_RISK",
    "SAHOOL_TERRAIN_WATERLOGGING_DETECTED",
    "SAHOOL_TERRAIN_DRAINAGE_ISSUE",
    "SAHOOL_TERRAIN_LEVELING_RECOMMENDED",
    "SAHOOL_TERRAIN_DRAINAGE_RECOMMENDED",
    "SAHOOL_TERRAIN_DEM_UPDATED",
    "SAHOOL_TERRAIN_ALL",
    # Edge Events
    "EdgeSubjects",
    "DeviceCapabilities",
    "DeviceHealth",
    "NetworkStatus",
    "SyncStatistics",
    "JobResult",
    "DeviceOnlineEvent",
    "DeviceOfflineEvent",
    "DeviceRegisteredEvent",
    "DeviceHealthUpdateEvent",
    "DeviceErrorEvent",
    "JobQueuedEvent",
    "JobStartedEvent",
    "JobProgressEvent",
    "JobCompletedEvent",
    "JobFailedEvent",
    "JobCancelledEvent",
    "SyncStartedEvent",
    "SyncProgressEvent",
    "SyncCompletedEvent",
    "SyncFailedEvent",
    "SyncConflictEvent",
    "ModelDeploymentStartedEvent",
    "ModelDeployedEvent",
    "ModelDeploymentFailedEvent",
    "ModelRollbackEvent",
    "DataCollectedEvent",
    "DataUploadedEvent",
    "FirmwareUpdateAvailableEvent",
    "FirmwareUpdateCompletedEvent",
    "SAHOOL_EDGE_DEVICE_ONLINE",
    "SAHOOL_EDGE_DEVICE_OFFLINE",
    "SAHOOL_EDGE_DEVICE_REGISTERED",
    "SAHOOL_EDGE_DEVICE_HEALTH_UPDATE",
    "SAHOOL_EDGE_DEVICE_ERROR",
    "SAHOOL_EDGE_JOB_QUEUED",
    "SAHOOL_EDGE_JOB_STARTED",
    "SAHOOL_EDGE_JOB_PROGRESS",
    "SAHOOL_EDGE_JOB_COMPLETED",
    "SAHOOL_EDGE_JOB_FAILED",
    "SAHOOL_EDGE_SYNC_STARTED",
    "SAHOOL_EDGE_SYNC_COMPLETED",
    "SAHOOL_EDGE_SYNC_FAILED",
    "SAHOOL_EDGE_SYNC_CONFLICT",
    "SAHOOL_EDGE_MODEL_DEPLOYED",
    "SAHOOL_EDGE_MODEL_DEPLOYMENT_STARTED",
    "SAHOOL_EDGE_MODEL_DEPLOYMENT_FAILED",
    "SAHOOL_EDGE_FIRMWARE_UPDATE_AVAILABLE",
    "SAHOOL_EDGE_DATA_COLLECTED",
    "SAHOOL_EDGE_ALL",
]
