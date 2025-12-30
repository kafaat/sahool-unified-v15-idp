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
  {
    id: '3',
    name: 'Corn Seeds Premium',
    nameAr: 'بذور ذرة ممتازة',
    description: 'Premium quality hybrid corn seeds with high yield',
    descriptionAr: 'بذور ذرة هجينة عالية الجودة مع إنتاجية عالية',
    category: 'seeds',
    price: 180,
    currency: 'SAR',
    unit: 'kg',
    unitAr: 'كجم',
    status: 'available',
    stock: 8,
    imageUrl: 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400',
    sellerId: 'seller1',
    sellerName: 'مؤسسة البذور الزراعية',
    sellerRating: 4.5,
    location: {
      city: 'Riyadh',
      cityAr: 'الرياض',
      region: 'Central',
      regionAr: 'الوسطى',
    },
    tags: ['corn', 'hybrid', 'seeds'],
    discount: {
      percentage: 15,
      validUntil: '2025-12-31',
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '4',
    name: 'Organic Pesticide Spray',
    nameAr: 'مبيد حشري عضوي',
    description: 'Eco-friendly organic pesticide for all crops',
    descriptionAr: 'مبيد حشري عضوي صديق للبيئة لجميع المحاصيل',
    category: 'pesticides',
    price: 95,
    currency: 'SAR',
    unit: 'liter',
    unitAr: 'لتر',
    status: 'available',
    stock: 150,
    imageUrl: 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400',
    sellerId: 'seller3',
    sellerName: 'شركة الحماية الزراعية',
    sellerRating: 4.2,
    location: {
      city: 'Dammam',
      cityAr: 'الدمام',
      region: 'Eastern',
      regionAr: 'الشرقية',
    },
    tags: ['organic', 'pesticide', 'eco-friendly'],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '5',
    name: 'Drip Irrigation Kit',
    nameAr: 'طقم ري بالتنقيط',
    description: 'Complete drip irrigation system for small farms',
    descriptionAr: 'نظام ري بالتنقيط كامل للمزارع الصغيرة',
    category: 'equipment',
    price: 450,
    currency: 'SAR',
    unit: 'set',
    unitAr: 'طقم',
    status: 'available',
    stock: 45,
    imageUrl: 'https://images.unsplash.com/photo-1560493676-04071c5f467b?w=400',
    sellerId: 'seller4',
    sellerName: 'معدات الري الحديثة',
    sellerRating: 4.9,
    location: {
      city: 'Riyadh',
      cityAr: 'الرياض',
      region: 'Central',
      regionAr: 'الوسطى',
    },
    tags: ['irrigation', 'equipment', 'drip'],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '6',
    name: 'Garden Hand Tools Set',
    nameAr: 'طقم أدوات يدوية للحديقة',
    description: 'Complete set of essential garden hand tools',
    descriptionAr: 'طقم كامل من الأدوات اليدوية الأساسية للحديقة',
    category: 'tools',
    price: 120,
    currency: 'SAR',
    unit: 'set',
    unitAr: 'طقم',
    status: 'available',
    stock: 75,
    imageUrl: 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400',
    sellerId: 'seller5',
    sellerName: 'أدوات الزراعة المتقدمة',
    sellerRating: 4.6,
    location: {
      city: 'Jeddah',
      cityAr: 'جدة',
      region: 'Western',
      regionAr: 'الغربية',
    },
    tags: ['tools', 'gardening', 'hand-tools'],
    discount: {
      percentage: 20,
      validUntil: '2025-12-31',
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '7',
    name: 'Tomato Seeds Hybrid',
    nameAr: 'بذور طماطم هجينة',
    description: 'Disease-resistant hybrid tomato seeds',
    descriptionAr: 'بذور طماطم هجينة مقاومة للأمراض',
    category: 'seeds',
    price: 65,
    currency: 'SAR',
    unit: 'packet (100g)',
    unitAr: 'عبوة (100 جم)',
    status: 'available',
    stock: 300,
    imageUrl: 'https://images.unsplash.com/photo-1592841200221-a6898f307baa?w=400',
    sellerId: 'seller1',
    sellerName: 'مؤسسة البذور الزراعية',
    sellerRating: 4.5,
    location: {
      city: 'Riyadh',
      cityAr: 'الرياض',
      region: 'Central',
      regionAr: 'الوسطى',
    },
    tags: ['tomato', 'hybrid', 'seeds'],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '8',
    name: 'Compost Fertilizer',
    nameAr: 'سماد عضوي كومبوست',
    description: 'Premium organic compost fertilizer',
    descriptionAr: 'سماد عضوي كومبوست عالي الجودة',
    category: 'fertilizers',
    price: 55,
    currency: 'SAR',
    unit: 'bag (20kg)',
    unitAr: 'كيس (20 كجم)',
    status: 'available',
    stock: 180,
    imageUrl: 'https://images.unsplash.com/photo-1615671524827-c1fe3973b648?w=400',
    sellerId: 'seller2',
    sellerName: 'الأسمدة الحديثة',
    sellerRating: 4.8,
    location: {
      city: 'Jeddah',
      cityAr: 'جدة',
      region: 'Western',
      regionAr: 'الغربية',
    },
    tags: ['organic', 'compost', 'fertilizer'],
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
    // Mock orders data
    const orders: Order[] = [];
    return new Promise((resolve) => setTimeout(() => resolve(orders), 500));
  },

  /**
   * Get order by ID
   */
  async getOrderById(_id: string): Promise<Order> {
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
    throw new Error('Not implemented');
  },
};
