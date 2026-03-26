/**
 * Drone Feature - Types
 * أنواع ميزة الطائرات بدون طيار
 */

export interface DroneFlight {
  id: string;
  name: string;
  nameAr: string;
  droneId: string;
  droneName: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  status: 'planned' | 'in_progress' | 'completed' | 'failed' | 'cancelled';
  missionType: 'survey' | 'spray' | 'mapping' | 'inspection';
  altitude: number;
  speed: number;
  duration?: number;
  coverage?: number;
  waypoints?: Array<{ lat: number; lng: number; altitude: number }>;
  startedAt?: string;
  completedAt?: string;
  createdAt: string;
}

export interface DroneDevice {
  id: string;
  name: string;
  nameAr: string;
  model: string;
  manufacturer: string;
  status: 'available' | 'in_flight' | 'charging' | 'maintenance' | 'offline';
  battery: number;
  lastFlight?: string;
  totalFlightHours: number;
  firmware?: string;
}

export interface FlightPlan {
  name: string;
  nameAr: string;
  droneId: string;
  fieldId: string;
  missionType: 'survey' | 'spray' | 'mapping' | 'inspection';
  altitude: number;
  speed: number;
  overlap?: number;
  waypoints?: Array<{ lat: number; lng: number; altitude: number }>;
}

export interface DroneFilters {
  status?: string;
  droneId?: string;
  fieldId?: string;
  missionType?: string;
}
