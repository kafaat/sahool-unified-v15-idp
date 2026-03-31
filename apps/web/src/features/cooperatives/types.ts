/**
 * Cooperatives Feature - Types
 * أنواع ميزة التعاونيات
 */

export type CooperativeType =
  | 'production'
  | 'marketing'
  | 'service'
  | 'multi_purpose'
  | 'credit'
  | 'irrigation';

export type CooperativeStatus = 'forming' | 'active' | 'suspended' | 'dissolved';

export type MemberRole =
  | 'chairman'
  | 'vice_chairman'
  | 'treasurer'
  | 'secretary'
  | 'board_member'
  | 'member'
  | 'observer';

export type MemberStatus = 'pending' | 'active' | 'suspended' | 'withdrawn' | 'expelled';

export type ResourceType =
  | 'equipment'
  | 'storage'
  | 'transport'
  | 'processing'
  | 'irrigation'
  | 'land'
  | 'seeds'
  | 'fertilizer'
  | 'pesticide';

export type ResourceStatus = 'available' | 'in_use' | 'maintenance' | 'reserved' | 'retired';

export type PurchaseOrderStatus =
  | 'draft'
  | 'collecting'
  | 'confirmed'
  | 'ordered'
  | 'delivered'
  | 'distributed'
  | 'cancelled';

export type RevenueShareMethod =
  | 'equal'
  | 'contribution'
  | 'production'
  | 'land_area'
  | 'weighted'
  | 'hybrid';

export type BookingStatus = 'pending' | 'approved' | 'rejected' | 'completed' | 'cancelled';

export interface Cooperative {
  id: string;
  tenantId: string;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
  type: CooperativeType;
  status: CooperativeStatus;
  registrationNumber: string;
  registrationDate: string;
  licenseExpiry: string;
  contactPhone: string;
  contactEmail: string;
  address: string;
  serviceAreaKm: number;
  shareCapital: number;
  currency: string;
  memberCount: number;
  activeMemberCount: number;
  resourceCount: number;
  totalLandAreaHa: number;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

export interface CooperativeMember {
  id: string;
  cooperativeId: string;
  farmerId: string;
  farmerName: string;
  farmerNameAr: string;
  role: MemberRole;
  status: MemberStatus;
  joinDate: string;
  shareCount: number;
  shareValue: number;
  contributionValue: number;
  annualFeesPaid: boolean;
  phone: string;
  email: string;
}

export interface SharedResource {
  id: string;
  cooperativeId: string;
  resourceType: ResourceType;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
  specifications: string;
  location: string;
  purchaseDate: string;
  acquisitionCost: number;
  currency: string;
  operationalStatus: ResourceStatus;
  maintenanceSchedule: string;
  lastMaintenance: string;
  maxDailyUseHours: number;
  hourlyCost: number;
}

export interface ResourceBooking {
  id: string;
  resourceId: string;
  resourceName: string;
  resourceNameAr: string;
  memberId: string;
  memberName: string;
  memberNameAr: string;
  startDatetime: string;
  endDatetime: string;
  durationHours: number;
  purpose: string;
  purposeAr: string;
  status: BookingStatus;
  approvedBy: string;
  costCharged: number;
  paymentStatus: string;
}

export interface MemberDistribution {
  memberId: string;
  memberName: string;
  memberNameAr: string;
  sharePercentage: number;
  amount: number;
}

export interface MemberOrderLine {
  id: string;
  orderId: string;
  memberId: string;
  memberName: string;
  memberNameAr: string;
  quantity: number;
  cost: number;
}

export interface GroupPurchaseOrder {
  id: string;
  cooperativeId: string;
  orderDate: string;
  itemType: string;
  itemName: string;
  itemNameAr: string;
  status: PurchaseOrderStatus;
  membersParticipating: number;
  totalQuantity: number;
  unit: string;
  deliveryDate: string;
  totalCost: number;
  unitCost: number;
  discountPercentage: number;
  currency: string;
}

export interface RevenueDistribution {
  id: string;
  cooperativeId: string;
  period: string;
  totalRevenue: number;
  managementFee: number;
  reserveFund: number;
  distributableAmount: number;
  shareMethod: RevenueShareMethod;
  distributions: MemberDistribution[];
  currency: string;
}

export interface CooperativeFilters {
  type?: CooperativeType;
  status?: CooperativeStatus;
  search?: string;
}

export interface MemberFilters {
  role?: MemberRole;
  status?: MemberStatus;
  search?: string;
}

export interface ResourceFilters {
  resourceType?: ResourceType;
  operationalStatus?: ResourceStatus;
  search?: string;
}

export interface BookingFilters {
  status?: BookingStatus;
  resourceId?: string;
  memberId?: string;
  startDate?: string;
  endDate?: string;
}

export interface CooperativeFormData {
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
  type: CooperativeType;
  registrationNumber: string;
  registrationDate: string;
  licenseExpiry: string;
  contactPhone: string;
  contactEmail: string;
  address: string;
  serviceAreaKm: number;
  shareCapital: number;
  currency: string;
  tags: string[];
}

export interface MemberFormData {
  farmerId: string;
  role: MemberRole;
  shareCount: number;
  shareValue: number;
  phone: string;
  email: string;
}

export interface ResourceFormData {
  resourceType: ResourceType;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
  specifications: string;
  location: string;
  purchaseDate: string;
  acquisitionCost: number;
  currency: string;
  maintenanceSchedule: string;
  maxDailyUseHours: number;
  hourlyCost: number;
}

export interface BookingFormData {
  resourceId: string;
  startDatetime: string;
  endDatetime: string;
  purpose: string;
  purposeAr: string;
}

export interface PurchaseOrderFormData {
  itemType: string;
  itemName: string;
  itemNameAr: string;
  totalQuantity: number;
  unit: string;
  deliveryDate: string;
}

export interface CooperativeStats {
  totalCooperatives: number;
  byType: Record<string, number>;
  byStatus: Record<string, number>;
  totalMembers: number;
  totalResources: number;
  totalLandAreaHa: number;
}
