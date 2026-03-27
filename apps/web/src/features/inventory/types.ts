/**
 * Inventory Feature - Types
 * أنواع ميزة المخزون
 */

export type InventoryStatus = 'in_stock' | 'low_stock' | 'out_of_stock' | 'expired';
export type InventoryCategory =
  | 'seeds'
  | 'fertilizers'
  | 'pesticides'
  | 'equipment'
  | 'fuel'
  | 'other';

export interface InventoryItem {
  id: string;
  name: string;
  nameAr: string;
  category: InventoryCategory;
  status: InventoryStatus;
  sku: string;
  quantity: number;
  unit: string;
  unitAr: string;
  minQuantity: number;
  maxQuantity: number;
  purchasePrice: number;
  sellingPrice?: number;
  supplier?: string;
  location?: string;
  locationAr?: string;
  expiryDate?: string;
  batchNumber?: string;
  lastRestocked?: string;
  notes?: string;
  imageUrl?: string;
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface InventoryFilters {
  category?: InventoryCategory;
  status?: InventoryStatus;
  search?: string;
  lowStock?: boolean;
}

export interface InventoryFormData {
  name: string;
  nameAr: string;
  category: InventoryCategory;
  sku: string;
  quantity: number;
  unit: string;
  unitAr: string;
  minQuantity: number;
  maxQuantity?: number;
  purchasePrice: number;
  sellingPrice?: number;
  supplier?: string;
  location?: string;
  locationAr?: string;
  expiryDate?: string;
  batchNumber?: string;
  notes?: string;
}

export interface InventoryTransaction {
  id: string;
  itemId: string;
  itemName: string;
  type: 'in' | 'out' | 'adjustment';
  quantity: number;
  reason: string;
  reasonAr: string;
  performedBy: string;
  createdAt: string;
}

export interface InventoryStats {
  totalItems: number;
  totalValue: number;
  lowStockItems: number;
  outOfStockItems: number;
  expiringItems: number;
  byCategory: Record<string, number>;
}
