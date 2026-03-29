/**
 * Marketplace Feature - API
 * واجهة برمجية لميزة السوق الزراعي
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { MARKETPLACE_ENDPOINTS, buildUrl, API_PREFIX } from '@sahool/shared-types/contracts';
import type { Product, ProductFilters, Order, OrderFilters, CartItem } from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Error messages
export const ERROR_MESSAGES = {
  FETCH_PRODUCTS: {
    en: 'Failed to fetch products',
    ar: 'فشل في جلب المنتجات',
  },
  FETCH_PRODUCT: {
    en: 'Failed to fetch product details',
    ar: 'فشل في جلب تفاصيل المنتج',
  },
  CREATE_PRODUCT: {
    en: 'Failed to create product',
    ar: 'فشل في إنشاء المنتج',
  },
  UPDATE_PRODUCT: {
    en: 'Failed to update product',
    ar: 'فشل في تحديث المنتج',
  },
  DELETE_PRODUCT: {
    en: 'Failed to delete product',
    ar: 'فشل في حذف المنتج',
  },
  FETCH_ORDERS: {
    en: 'Failed to fetch orders',
    ar: 'فشل في جلب الطلبات',
  },
  CREATE_ORDER: {
    en: 'Failed to create order',
    ar: 'فشل في إنشاء الطلب',
  },
  CANCEL_ORDER: {
    en: 'Failed to cancel order',
    ar: 'فشل في إلغاء الطلب',
  },
  ADD_TO_CART: {
    en: 'Failed to add item to cart',
    ar: 'فشل في إضافة المنتج للسلة',
  },
  FETCH_CATEGORIES: {
    en: 'Failed to fetch categories',
    ar: 'فشل في جلب الفئات',
  },
};

export const marketplaceApi = {
  /**
   * Get products list
   */
  async getProducts(filters?: ProductFilters): Promise<Product[]> {
    return safeFetch(MARKETPLACE_ENDPOINTS.PRODUCTS, async () => {
      const params = new URLSearchParams();
      if (filters?.category) params.append('category', filters.category);
      if (filters?.search) params.append('search', filters.search);
      if (filters?.minPrice) params.append('minPrice', filters.minPrice.toString());
      if (filters?.maxPrice) params.append('maxPrice', filters.maxPrice.toString());
      if (filters?.status) params.append('status', filters.status);
      if (filters?.sortBy) params.append('sortBy', filters.sortBy);

      const response = await api.get(`${MARKETPLACE_ENDPOINTS.PRODUCTS}?${params.toString()}`);
      return response.data.data || response.data;
    });
  },

  async getProductById(id: string): Promise<Product> {
    return safeFetch(MARKETPLACE_ENDPOINTS.PRODUCT_GET, async () => {
      const response = await api.get(
        buildUrl(MARKETPLACE_ENDPOINTS.PRODUCT_GET, { productId: id })
      );
      return response.data.data || response.data;
    });
  },

  async createProduct(data: Partial<Product>): Promise<Product> {
    return safeFetch(MARKETPLACE_ENDPOINTS.PRODUCTS, async () => {
      const response = await api.post(MARKETPLACE_ENDPOINTS.PRODUCTS, data);
      return response.data.data || response.data;
    });
  },

  async updateProduct(id: string, data: Partial<Product>): Promise<Product> {
    return safeFetch(MARKETPLACE_ENDPOINTS.PRODUCT_GET, async () => {
      const response = await api.patch(
        buildUrl(MARKETPLACE_ENDPOINTS.PRODUCT_GET, { productId: id }),
        data
      );
      return response.data.data || response.data;
    });
  },

  async deleteProduct(id: string): Promise<void> {
    return safeFetch(MARKETPLACE_ENDPOINTS.PRODUCT_GET, async () => {
      await api.delete(buildUrl(MARKETPLACE_ENDPOINTS.PRODUCT_GET, { productId: id }));
    });
  },

  async getCategories(): Promise<unknown[]> {
    return safeFetch(`${MARKETPLACE_ENDPOINTS.PRODUCTS}/categories`, async () => {
      const response = await api.get(`${MARKETPLACE_ENDPOINTS.PRODUCTS}/categories`);
      return response.data.data || response.data;
    });
  },

  async getFeaturedProducts(): Promise<Product[]> {
    return safeFetch(`${MARKETPLACE_ENDPOINTS.PRODUCTS}/featured`, async () => {
      const response = await api.get(`${MARKETPLACE_ENDPOINTS.PRODUCTS}/featured`);
      return response.data.data || response.data;
    });
  },

  async getSellerProducts(sellerId: string): Promise<Product[]> {
    return safeFetch(`${API_PREFIX}/marketplace/sellers/${sellerId}/products`, async () => {
      const response = await api.get(`${API_PREFIX}/marketplace/sellers/${sellerId}/products`);
      return response.data.data || response.data;
    });
  },

  /**
   * Get orders list
   */
  async getOrders(filters?: OrderFilters): Promise<Order[]> {
    return safeFetch(MARKETPLACE_ENDPOINTS.ORDERS, async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.append('status', filters.status);
      if (filters?.dateFrom) params.append('dateFrom', filters.dateFrom);
      if (filters?.dateTo) params.append('dateTo', filters.dateTo);

      const response = await api.get(`${MARKETPLACE_ENDPOINTS.ORDERS}?${params.toString()}`);
      return response.data.data || response.data;
    });
  },

  /**
   * Get order by ID
   */
  async getOrderById(id: string): Promise<Order | null> {
    return safeFetch(`${MARKETPLACE_ENDPOINTS.ORDERS}/${id}`, async () => {
      const response = await api.get(`${MARKETPLACE_ENDPOINTS.ORDERS}/${id}`);
      return response.data.data || response.data;
    });
  },

  async createOrder(data: {
    items: Array<{ productId: string; quantity: number }>;
    shippingAddress: Order['shippingAddress'];
    notes?: string;
  }): Promise<Order> {
    return safeFetch(MARKETPLACE_ENDPOINTS.ORDERS, async () => {
      const response = await api.post(MARKETPLACE_ENDPOINTS.ORDERS, data);
      return response.data.data || response.data;
    });
  },

  async cancelOrder(id: string): Promise<{ success: boolean; error?: string }> {
    return safeFetch(`${MARKETPLACE_ENDPOINTS.ORDERS}/${id}/cancel`, async () => {
      const response = await api.post(`${MARKETPLACE_ENDPOINTS.ORDERS}/${id}/cancel`);
      return { success: true, ...response.data };
    });
  },

  /**
   * Get cart items
   */
  async getCart(): Promise<CartItem[]> {
    return safeFetch(`${API_PREFIX}/marketplace/cart`, async () => {
      const response = await api.get(`${API_PREFIX}/marketplace/cart`);
      return response.data.data || response.data;
    });
  },

  /**
   * Add item to cart
   */
  async addToCart(productId: string, quantity: number): Promise<CartItem> {
    return safeFetch(`${API_PREFIX}/marketplace/cart`, async () => {
      const response = await api.post(`${API_PREFIX}/marketplace/cart`, {
        productId,
        quantity,
      });
      return response.data.data || response.data;
    });
  },

  async updateCartItem(itemId: string, quantity: number): Promise<CartItem> {
    return safeFetch(`${API_PREFIX}/marketplace/cart/${itemId}`, async () => {
      const response = await api.patch(`${API_PREFIX}/marketplace/cart/${itemId}`, {
        quantity,
      });
      return response.data.data || response.data;
    });
  },

  async removeFromCart(itemId: string): Promise<void> {
    return safeFetch(`${API_PREFIX}/marketplace/cart/${itemId}`, async () => {
      await api.delete(`${API_PREFIX}/marketplace/cart/${itemId}`);
    });
  },

  async clearCart(): Promise<void> {
    return safeFetch(`${API_PREFIX}/marketplace/cart`, async () => {
      await api.delete(`${API_PREFIX}/marketplace/cart`);
    });
  },

  async searchProducts(query: string): Promise<Product[]> {
    return safeFetch(`${MARKETPLACE_ENDPOINTS.PRODUCTS}/search`, async () => {
      const response = await api.get(
        `${MARKETPLACE_ENDPOINTS.PRODUCTS}/search?q=${encodeURIComponent(query)}`
      );
      return response.data.data || response.data;
    });
  },

  /**
   * Get product reviews
   */
  async getProductReviews(productId: string): Promise<
    Array<{
      id: string;
      userId: string;
      userName: string;
      rating: number;
      comment: string;
      createdAt: string;
    }>
  > {
    return safeFetch(
      `${buildUrl(MARKETPLACE_ENDPOINTS.PRODUCT_GET, { productId })}/reviews`,
      async () => {
        const response = await api.get(
          `${buildUrl(MARKETPLACE_ENDPOINTS.PRODUCT_GET, { productId })}/reviews`
        );
        return response.data.data || response.data;
      }
    );
  },

  /**
   * Add product review
   */
  async addProductReview(
    productId: string,
    data: { rating: number; comment: string }
  ): Promise<void> {
    return safeFetch(
      `${buildUrl(MARKETPLACE_ENDPOINTS.PRODUCT_GET, { productId })}/reviews`,
      async () => {
        await api.post(
          `${buildUrl(MARKETPLACE_ENDPOINTS.PRODUCT_GET, { productId })}/reviews`,
          data
        );
      }
    );
  },
};
