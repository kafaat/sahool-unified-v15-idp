/**
 * SAHOOL Edge Device Types
 * أنواع أجهزة الحوسبة الطرفية
 *
 * Type definitions for edge computing devices including:
 * - Device management (إدارة الأجهزة)
 * - Model deployment (نشر النماذج)
 * - Synchronization (المزامنة)
 * - Offline capabilities (القدرات دون اتصال)
 */

// ═══════════════════════════════════════════════════════════════════════════
// Device Types
// أنواع الأجهزة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Edge device hardware type
 */
export type EdgeDeviceType =
  | 'jetson_orin' // NVIDIA Jetson Orin
  | 'jetson_nano' // NVIDIA Jetson Nano
  | 'jetson_xavier' // NVIDIA Jetson Xavier
  | 'raspberry_pi_4' // Raspberry Pi 4
  | 'raspberry_pi_5' // Raspberry Pi 5
  | 'coral_dev_board' // Google Coral Dev Board
  | 'intel_nuc' // Intel NUC
  | 'custom'; // Custom device

/**
 * Device status
 */
export type DeviceStatus =
  | 'online' // متصل
  | 'offline' // غير متصل
  | 'busy' // مشغول
  | 'maintenance' // صيانة
  | 'error' // خطأ
  | 'updating'; // تحديث

/**
 * Connection type
 */
export type ConnectionType =
  | 'wifi'
  | 'ethernet'
  | 'cellular_4g'
  | 'cellular_5g'
  | 'lora'
  | 'satellite';

/**
 * Geographic point for device location
 */
export interface GeoPoint {
  latitude: number;
  longitude: number;
  altitude?: number;
  accuracy?: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Model Deployment Types
// أنواع نشر النماذج
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Model format for edge deployment
 */
export type ModelFormat =
  | 'tensorrt' // NVIDIA TensorRT
  | 'onnx' // Open Neural Network Exchange
  | 'tflite' // TensorFlow Lite
  | 'pytorch' // PyTorch
  | 'openvino'; // Intel OpenVINO

/**
 * Model deployment status
 */
export type DeploymentStatus =
  | 'pending' // قيد الانتظار
  | 'downloading' // جاري التحميل
  | 'installing' // جاري التثبيت
  | 'deployed' // تم النشر
  | 'failed' // فشل
  | 'uninstalling'; // جاري الإزالة

/**
 * Deployed model on edge device
 */
export interface DeployedModel {
  modelId: string;
  modelName: string;
  modelNameAr: string;
  version: string;
  format: ModelFormat;
  sizeBytes: number;
  deployedAt: Date;
  status: DeploymentStatus;
  statusAr: string;
  inferenceCount: number;
  avgInferenceTimeMs: number;
  lastInferenceAt?: Date;
  accuracy?: number;
  memoryUsageBytes?: number;
  gpuMemoryUsageBytes?: number;
}

/**
 * Model deployment request
 */
export interface ModelDeploymentRequest {
  deviceId: string;
  modelId: string;
  modelVersion: string;
  format: ModelFormat;
  priority?: 'low' | 'normal' | 'high';
  scheduledTime?: Date;
  replaceExisting?: boolean;
}

/**
 * Model deployment response
 */
export interface ModelDeploymentResponse {
  success: boolean;
  deploymentId: string;
  status: DeploymentStatus;
  estimatedTimeSeconds?: number;
  error?: string;
  errorAr?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Edge Device Types
// أنواع أجهزة الحوسبة الطرفية
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hardware specifications
 */
export interface HardwareSpecs {
  cpuModel: string;
  cpuCores: number;
  cpuFrequencyMhz: number;
  ramBytes: number;
  storageBytes: number;
  gpuModel?: string;
  gpuMemoryBytes?: number;
  gpuCudaCores?: number;
  tensorCores?: number;
  hasNpu?: boolean;
  npuTops?: number; // Tera Operations Per Second
}

/**
 * System metrics
 */
export interface SystemMetrics {
  cpuUsagePercent: number;
  memoryUsagePercent: number;
  storageUsagePercent: number;
  gpuUsagePercent?: number;
  gpuMemoryUsagePercent?: number;
  temperatureCelsius: number;
  gpuTemperatureCelsius?: number;
  powerWatts?: number;
  uptimeSeconds: number;
  networkBytesIn: number;
  networkBytesOut: number;
}

/**
 * Edge device entity
 */
export interface EdgeDevice {
  deviceId: string;
  deviceName: string;
  deviceNameAr?: string;
  deviceType: EdgeDeviceType;
  deviceTypeAr: string;
  status: DeviceStatus;
  statusAr: string;
  serialNumber?: string;
  firmwareVersion: string;
  osVersion: string;
  hardwareSpecs: HardwareSpecs;
  deployedModels: DeployedModel[];
  currentLocation?: GeoPoint;
  assignedFieldIds?: string[];
  assignedFarmId?: string;
  connectionType?: ConnectionType;
  connectionTypeAr?: string;
  ipAddress?: string;
  macAddress?: string;
  lastSyncAt?: Date;
  lastHeartbeatAt?: Date;
  registeredAt: Date;
  updatedAt: Date;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

/**
 * Edge device creation payload
 */
export interface CreateEdgeDevicePayload {
  deviceName: string;
  deviceNameAr?: string;
  deviceType: EdgeDeviceType;
  serialNumber?: string;
  firmwareVersion: string;
  osVersion: string;
  hardwareSpecs: HardwareSpecs;
  currentLocation?: GeoPoint;
  assignedFieldIds?: string[];
  assignedFarmId?: string;
  connectionType?: ConnectionType;
  tags?: string[];
}

/**
 * Edge device update payload
 */
export interface UpdateEdgeDevicePayload {
  deviceName?: string;
  deviceNameAr?: string;
  firmwareVersion?: string;
  osVersion?: string;
  currentLocation?: GeoPoint;
  assignedFieldIds?: string[];
  assignedFarmId?: string;
  connectionType?: ConnectionType;
  tags?: string[];
  status?: DeviceStatus;
}

// ═══════════════════════════════════════════════════════════════════════════
// Synchronization Types
// أنواع المزامنة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Sync status
 */
export type SyncStatus =
  | 'synced' // متزامن
  | 'syncing' // جاري المزامنة
  | 'pending' // قيد الانتظار
  | 'failed' // فشل
  | 'conflict'; // تعارض

/**
 * Sync direction
 */
export type SyncDirection = 'upload' | 'download' | 'bidirectional';

/**
 * Data type for synchronization
 */
export type SyncDataType =
  | 'detections' // Detections data
  | 'models' // Model files
  | 'configurations' // Device configurations
  | 'telemetry' // System telemetry
  | 'logs' // Device logs
  | 'media'; // Images/videos

/**
 * Sync job
 */
export interface SyncJob {
  syncId: string;
  deviceId: string;
  dataType: SyncDataType;
  direction: SyncDirection;
  status: SyncStatus;
  statusAr: string;
  totalRecords: number;
  syncedRecords: number;
  failedRecords: number;
  bytesTransferred: number;
  totalBytes: number;
  startedAt: Date;
  completedAt?: Date;
  error?: string;
  errorAr?: string;
  retryCount: number;
  maxRetries: number;
}

/**
 * Sync configuration
 */
export interface SyncConfiguration {
  deviceId: string;
  autoSyncEnabled: boolean;
  syncIntervalMinutes: number;
  syncOnWifiOnly: boolean;
  syncOnCellular: boolean;
  maxSyncBytesPerDay?: number;
  priorityDataTypes: SyncDataType[];
  excludedDataTypes?: SyncDataType[];
  conflictResolution: 'cloud_wins' | 'device_wins' | 'newest_wins' | 'manual';
  conflictResolutionAr: string;
  lastSyncAt?: Date;
  nextScheduledSync?: Date;
}

/**
 * Offline queue item
 */
export interface OfflineQueueItem {
  queueId: string;
  deviceId: string;
  dataType: SyncDataType;
  action: 'create' | 'update' | 'delete';
  payload: Record<string, unknown>;
  createdAt: Date;
  retryCount: number;
  status: 'queued' | 'processing' | 'synced' | 'failed';
  statusAr: string;
  error?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Telemetry Types
// أنواع القياس عن بعد
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Device telemetry data
 */
export interface DeviceTelemetry {
  deviceId: string;
  timestamp: Date;
  metrics: SystemMetrics;
  location?: GeoPoint;
  connectionQuality?: {
    signalStrength: number; // dBm
    latencyMs: number;
    packetLossPercent: number;
  };
  inferenceStats?: {
    totalInferences: number;
    successfulInferences: number;
    failedInferences: number;
    avgInferenceTimeMs: number;
    peakInferenceTimeMs: number;
  };
  alerts?: Array<{
    alertId: string;
    type: 'warning' | 'error' | 'critical';
    message: string;
    messageAr: string;
    timestamp: Date;
  }>;
}

/**
 * Aggregated telemetry
 */
export interface AggregatedTelemetry {
  deviceId: string;
  period: 'hourly' | 'daily' | 'weekly' | 'monthly';
  startTime: Date;
  endTime: Date;
  avgCpuUsage: number;
  avgMemoryUsage: number;
  avgGpuUsage?: number;
  avgTemperature: number;
  maxTemperature: number;
  totalInferences: number;
  avgInferenceTime: number;
  uptimePercent: number;
  dataTransferredBytes: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Edge Fleet Management Types
// أنواع إدارة أسطول الأجهزة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Device group
 */
export interface DeviceGroup {
  groupId: string;
  groupName: string;
  groupNameAr: string;
  description?: string;
  descriptionAr?: string;
  deviceIds: string[];
  deviceCount: number;
  assignedModels?: string[];
  syncConfiguration?: SyncConfiguration;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Fleet summary
 */
export interface FleetSummary {
  totalDevices: number;
  onlineDevices: number;
  offlineDevices: number;
  busyDevices: number;
  errorDevices: number;
  devicesByType: Record<EdgeDeviceType, number>;
  devicesByStatus: Record<DeviceStatus, number>;
  totalDeployedModels: number;
  totalInferencesToday: number;
  avgCpuUsage: number;
  avgMemoryUsage: number;
  pendingSyncJobs: number;
  lastUpdated: Date;
}

/**
 * Device health report
 */
export interface DeviceHealthReport {
  deviceId: string;
  deviceName: string;
  overallHealth: 'healthy' | 'degraded' | 'unhealthy' | 'critical';
  overallHealthAr: string;
  healthScore: number; // 0-100
  issues: Array<{
    category: 'hardware' | 'software' | 'connectivity' | 'performance';
    severity: 'low' | 'medium' | 'high' | 'critical';
    description: string;
    descriptionAr: string;
    recommendation: string;
    recommendationAr: string;
  }>;
  lastChecked: Date;
  nextCheckScheduled?: Date;
}

// ═══════════════════════════════════════════════════════════════════════════
// Edge API Request/Response Types
// أنواع طلبات واستجابات واجهة برمجة الأجهزة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Device list filters
 */
export interface DeviceFilters {
  status?: DeviceStatus | DeviceStatus[];
  deviceType?: EdgeDeviceType | EdgeDeviceType[];
  assignedFarmId?: string;
  assignedFieldIds?: string[];
  tags?: string[];
  search?: string;
  page?: number;
  limit?: number;
  sortBy?: 'deviceName' | 'status' | 'lastSyncAt' | 'registeredAt';
  sortOrder?: 'asc' | 'desc';
}

/**
 * Device list response
 */
export interface DeviceListResponse {
  devices: EdgeDevice[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasMore: boolean;
  };
}

/**
 * Command to send to edge device
 */
export interface DeviceCommand {
  commandId: string;
  deviceId: string;
  command:
    | 'restart'
    | 'update_firmware'
    | 'sync_now'
    | 'clear_cache'
    | 'run_diagnostics'
    | 'shutdown';
  commandAr: string;
  parameters?: Record<string, unknown>;
  issuedAt: Date;
  issuedBy: string;
  status: 'pending' | 'sent' | 'acknowledged' | 'completed' | 'failed' | 'timeout';
  statusAr: string;
  completedAt?: Date;
  result?: Record<string, unknown>;
  error?: string;
  errorAr?: string;
}

/**
 * OTA update request
 */
export interface OTAUpdateRequest {
  deviceIds: string[];
  updateType: 'firmware' | 'os' | 'model' | 'application';
  version: string;
  downloadUrl: string;
  checksum: string;
  scheduledTime?: Date;
  priority?: 'low' | 'normal' | 'high' | 'critical';
  rollbackOnFailure?: boolean;
}

/**
 * OTA update status
 */
export interface OTAUpdateStatus {
  updateId: string;
  deviceId: string;
  updateType: string;
  targetVersion: string;
  currentVersion: string;
  status:
    | 'scheduled'
    | 'downloading'
    | 'installing'
    | 'verifying'
    | 'completed'
    | 'failed'
    | 'rolled_back';
  statusAr: string;
  progress: number; // 0-100
  startedAt?: Date;
  completedAt?: Date;
  error?: string;
  errorAr?: string;
}
