/**
 * WebSocket Types
 * Types for real-time communication
 */

export type WebSocketEventType =
  | 'alert'
  | 'sensor'
  | 'irrigation'
  | 'diagnosis'
  | 'farm_update'
  | 'weather'
  | 'task'
  | 'connected'
  | 'disconnected'
  | 'error';

export interface WebSocketMessage<T = unknown> {
  type: WebSocketEventType;
  data: T;
  timestamp?: string;
  correlationId?: string;
}

export interface AlertMessage {
  id: string;
  type: 'pest' | 'disease' | 'weather' | 'irrigation' | 'general';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  farmId?: string;
  fieldId?: string;
  timestamp: string;
  read?: boolean;
}

export interface SensorMessage {
  id: string;
  sensorId: string;
  type: 'temperature' | 'humidity' | 'soil_moisture' | 'ph' | 'light';
  value: number;
  unit: string;
  timestamp: string;
  farmId?: string;
  fieldId?: string;
}

export interface IrrigationMessage {
  id: string;
  systemId: string;
  status: 'on' | 'off' | 'scheduled' | 'error';
  flowRate?: number;
  duration?: number;
  timestamp: string;
  farmId?: string;
  fieldId?: string;
}

export interface DiagnosisMessage {
  id: string;
  type: 'pest' | 'disease' | 'nutrient' | 'general';
  confidence: number;
  diagnosis: string;
  recommendations?: string[];
  imageUrl?: string;
  timestamp: string;
  farmId?: string;
  fieldId?: string;
}

export enum ConnectionStatus {
  CONNECTED = 'connected',
  CONNECTING = 'connecting',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error',
}

export interface WebSocketClientOptions {
  url: string;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}
