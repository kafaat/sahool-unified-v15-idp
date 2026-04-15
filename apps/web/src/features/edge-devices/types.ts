/**
 * Edge Devices Feature - Types
 * أنواع ميزة الأجهزة الطرفية
 */

export interface EdgeDevice {
  id: string;
  name: string;
  nameAr: string;
  type: 'jetson_orin' | 'jetson_nano' | 'raspberry_pi' | 'custom';
  status: 'online' | 'offline' | 'syncing' | 'error';
  ipAddress: string;
  location?: { latitude: number; longitude: number; fieldId?: string; fieldName?: string };
  models: string[];
  cpuUsage: number;
  memoryUsage: number;
  gpuUsage?: number;
  diskUsage: number;
  firmware?: string;
  lastSeen: string;
  createdAt: string;
}

export interface EdgeDeployment {
  id: string;
  deviceId: string;
  modelName: string;
  variant: string;
  status: 'queued' | 'downloading' | 'deploying' | 'running' | 'failed';
  progress: number;
  startedAt: string;
  completedAt?: string;
}

export interface EdgeSyncStatus {
  deviceId: string;
  status: 'syncing' | 'completed' | 'failed';
  progress: number;
  dataSize: number;
  startedAt: string;
  completedAt?: string;
}

export interface EdgeFilters {
  status?: string;
  type?: string;
  fieldId?: string;
}
