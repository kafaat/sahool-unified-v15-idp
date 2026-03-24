/**
 * Logistics Feature - Types
 * أنواع ميزة اللوجستيات
 */

export type ShipmentStatus = 'pending' | 'in_transit' | 'delivered' | 'delayed' | 'cancelled';
export type CargoType = 'fertilizers' | 'seeds' | 'equipment' | 'produce' | 'chemicals' | 'other';

export interface Shipment {
  id: string;
  orderNumber: string;
  origin: string;
  originAr: string;
  originCoordinates?: { lat: number; lng: number };
  destination: string;
  destinationAr: string;
  destinationCoordinates?: { lat: number; lng: number };
  status: ShipmentStatus;
  cargoType: CargoType;
  cargo: string;
  cargoAr: string;
  weight: number;
  weightUnit: string;
  volume?: number;
  volumeUnit?: string;
  estimatedDelivery: string;
  actualDelivery?: string;
  driver?: {
    id: string;
    name: string;
    phone?: string;
  };
  vehicle?: {
    id: string;
    plateNumber: string;
    type: string;
  };
  trackingNumber?: string;
  cost?: number;
  notes?: string;
  notesAr?: string;
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface ShipmentFilters {
  status?: ShipmentStatus;
  cargoType?: CargoType;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

export interface ShipmentFormData {
  origin: string;
  originAr: string;
  destination: string;
  destinationAr: string;
  cargoType: CargoType;
  cargo: string;
  cargoAr: string;
  weight: number;
  weightUnit: string;
  estimatedDelivery: string;
  driverId?: string;
  vehicleId?: string;
  notes?: string;
  notesAr?: string;
}

export interface ShipmentTracking {
  id: string;
  shipmentId: string;
  status: ShipmentStatus;
  location?: { lat: number; lng: number };
  locationName?: string;
  timestamp: string;
  notes?: string;
}

export interface Driver {
  id: string;
  name: string;
  phone: string;
  licenseNumber: string;
  status: 'available' | 'on_trip' | 'off_duty';
  currentLocation?: { lat: number; lng: number };
}

export interface Vehicle {
  id: string;
  plateNumber: string;
  type: 'truck' | 'van' | 'pickup' | 'trailer';
  capacity: number;
  capacityUnit: string;
  status: 'available' | 'in_use' | 'maintenance';
}

export interface LogisticsStats {
  totalShipments: number;
  pendingShipments: number;
  inTransitShipments: number;
  deliveredShipments: number;
  delayedShipments: number;
  totalWeight: number;
  activeDrivers: number;
  availableVehicles: number;
}
