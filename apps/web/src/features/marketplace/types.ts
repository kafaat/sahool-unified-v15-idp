/**
 * Marketplace Feature - Types
 * أنواع ميزة السوق الزراعي
 */

export type ProductCategory =
  | 'seeds'
  | 'fertilizers'
  | 'pesticides'
  | 'equipment'
  | 'tools'
  | 'irrigation'
  | 'produce'
  | 'other';

export type ProductStatus = 'available' | 'out_of_stock' | 'discontinued';
export type OrderStatus = 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
export type PaymentStatus = 'pending' | 'paid' | 'failed' | 'refunded';

export interface Product {
  id: string;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
  category: ProductCategory;
  price: number;
  currency: string;
  unit: string;
  unitAr: string;
  status: ProductStatus;
  stock: number;
  imageUrl?: string;
  images?: string[];
  sellerId: string;
  sellerName: string;
  sellerRating?: number;
  location?: {
    city: string;
    cityAr: string;
    region: string;
    regionAr: string;
  };
  specifications?: Record<string, unknown>;
  tags?: string[];
  discount?: {
    percentage: number;
    validUntil: string;
  };
  createdAt: string;
  updatedAt: string;
}

export interface CartItem {
  productId: string;
  product: Product;
  quantity: number;
  addedAt: string;
}

export interface Cart {
  items: CartItem[];
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
  currency: string;
}

export interface Order {
  id: string;
  orderNumber: string;
  userId: string;
  items: Array<{
    productId: string;
    productName: string;
    productNameAr: string;
    quantity: number;
    price: number;
    subtotal: number;
  }>;
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
  currency: string;
  status: OrderStatus;
  paymentStatus: PaymentStatus;
  paymentMethod?: string;
  shippingAddress: {
    name: string;
    phone: string;
    addressLine1: string;
    addressLine2?: string;
    city: string;
    region: string;
    postalCode?: string;
    country: string;
  };
  notes?: string;
  trackingNumber?: string;
  estimatedDelivery?: string;
  deliveredAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ProductFilters {
  category?: ProductCategory;
  search?: string;
  minPrice?: number;
  maxPrice?: number;
  sellerId?: string;
  status?: ProductStatus;
  sortBy?: 'price_asc' | 'price_desc' | 'name' | 'newest' | 'rating';
}

export interface OrderFilters {
  status?: OrderStatus;
  paymentStatus?: PaymentStatus;
  dateFrom?: string;
  dateTo?: string;
}
