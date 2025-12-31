/**
 * Marketplace Feature - API
 * واجهة برمجية لميزة السوق الزراعي
 */

import type { Product, ProductFilters, Order, OrderFilters } from './types';

// const API_BASE = '/api/marketplace';

// Mock data for development
const mockProducts: Product[] = [
  {
    id: '1',
    name: 'Organic Wheat Seeds',
    nameAr: 'بذور قمح عضوية',
    description: 'High-quality organic wheat seeds, suitable for various soil types',
    descriptionAr: 'بذور قمح عضوية عالية الجودة، مناسبة لأنواع التربة المختلفة',
    category: 'seeds',
    price: 150,
    currency: 'SAR',
    unit: 'kg',
    unitAr: 'كجم',
    status: 'available',
    stock: 500,
    imageUrl: 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400',
    sellerId: 'seller1',
    sellerName: 'مؤسسة البذور الزراعية',
    sellerRating: 4.5,
    location: {
      city: 'Riyadh',
      cityAr: 'الرياض',
      region: 'Central',
      regionAr: 'الوسطى',
    },
    tags: ['organic', 'wheat', 'seeds'],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    name: 'NPK Fertilizer 20-20-20',
    nameAr: 'سماد NPK 20-20-20',
    description: 'Balanced NPK fertilizer for all crops',
    descriptionAr: 'سماد NPK متوازن لجميع المحاصيل',
    category: 'fertilizers',
    price: 85,
    currency: 'SAR',
    unit: 'bag (25kg)',
    unitAr: 'كيس (25 كجم)',
    status: 'available',
    stock: 200,
    imageUrl: 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400',
    sellerId: 'seller2',
    sellerName: 'الأسمدة الحديثة',
    sellerRating: 4.8,
    location: {
      city: 'Jeddah',
      cityAr: 'جدة',
      region: 'Western',
      regionAr: 'الغربية',
    },
    tags: ['fertilizer', 'NPK', 'nutrients'],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

export const marketplaceApi = {
  /**
   * Get products list
   */
  async getProducts(filters?: ProductFilters): Promise<Product[]> {
    // In production, this would be an actual API call
    // For now, return mock data with filtering
    let products = [...mockProducts];

    if (filters?.category) {
      products = products.filter((p) => p.category === filters.category);
    }

    if (filters?.search) {
      const search = filters.search.toLowerCase();
      products = products.filter(
        (p) =>
          p.name.toLowerCase().includes(search) ||
          p.nameAr.includes(search) ||
          p.description.toLowerCase().includes(search)
      );
    }

    if (filters?.minPrice !== undefined) {
      products = products.filter((p) => p.price >= filters.minPrice!);
    }

    if (filters?.maxPrice !== undefined) {
      products = products.filter((p) => p.price <= filters.maxPrice!);
    }

    if (filters?.status) {
      products = products.filter((p) => p.status === filters.status);
    }

    // Sorting
    if (filters?.sortBy) {
      switch (filters.sortBy) {
        case 'price_asc':
          products.sort((a, b) => a.price - b.price);
          break;
        case 'price_desc':
          products.sort((a, b) => b.price - a.price);
          break;
        case 'name':
          products.sort((a, b) => a.name.localeCompare(b.name));
          break;
        case 'newest':
          products.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
          break;
        case 'rating':
          products.sort((a, b) => (b.sellerRating || 0) - (a.sellerRating || 0));
          break;
      }
    }

    return new Promise((resolve) => setTimeout(() => resolve(products), 500));
  },

  /**
   * Get product by ID
   */
  async getProductById(id: string): Promise<Product> {
    const product = mockProducts.find((p) => p.id === id);
    if (!product) {
      throw new Error('Product not found');
    }
    return new Promise((resolve) => setTimeout(() => resolve(product), 300));
  },

  /**
   * Get orders list
   */
  async getOrders(_filters?: OrderFilters): Promise<Order[]> {
    // Mock orders data - filters will be used when connecting to real API
    const orders: Order[] = [];
    return new Promise((resolve) => setTimeout(() => resolve(orders), 500));
  },

  /**
   * Get order by ID
   */
  async getOrderById(_id: string): Promise<Order> {
    // TODO: Implement actual API call when backend is ready
    throw new Error('Order not found');
  },

  /**
   * Create order
   */
  async createOrder(data: {
    items: Array<{ productId: string; quantity: number }>;
    shippingAddress: Order['shippingAddress'];
    notes?: string;
  }): Promise<Order> {
    // Mock order creation
    const order: Order = {
      id: Date.now().toString(),
      orderNumber: `ORD-${Date.now()}`,
      userId: 'current-user',
      items: [],
      subtotal: 0,
      tax: 0,
      shipping: 0,
      total: 0,
      currency: 'SAR',
      status: 'pending',
      paymentStatus: 'pending',
      shippingAddress: data.shippingAddress,
      notes: data.notes,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    return new Promise((resolve) => setTimeout(() => resolve(order), 500));
  },

  /**
   * Cancel order
   */
  async cancelOrder(_id: string): Promise<Order> {
    // TODO: Implement actual API call when backend is ready
    throw new Error('Not implemented');
  },
};
