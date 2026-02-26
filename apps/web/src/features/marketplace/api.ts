/**
 * Marketplace Feature - API
 * واجهة برمجية لميزة السوق الزراعي
 */

import { createApiClient, logger } from "@/lib/api/factory";
import { MARKETPLACE_ENDPOINTS, buildUrl, API_PREFIX } from "@sahool/shared-types/contracts";
import type {
  Product,
  ProductFilters,
  Order,
  OrderFilters,
  CartItem,
} from "./types";

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Error messages
export const ERROR_MESSAGES = {
  FETCH_PRODUCTS: {
    en: "Failed to fetch products",
    ar: "فشل في جلب المنتجات",
  },
  FETCH_PRODUCT: {
    en: "Failed to fetch product details",
    ar: "فشل في جلب تفاصيل المنتج",
  },
  CREATE_PRODUCT: {
    en: "Failed to create product",
    ar: "فشل في إنشاء المنتج",
  },
  UPDATE_PRODUCT: {
    en: "Failed to update product",
    ar: "فشل في تحديث المنتج",
  },
  DELETE_PRODUCT: {
    en: "Failed to delete product",
    ar: "فشل في حذف المنتج",
  },
  FETCH_ORDERS: {
    en: "Failed to fetch orders",
    ar: "فشل في جلب الطلبات",
  },
  CREATE_ORDER: {
    en: "Failed to create order",
    ar: "فشل في إنشاء الطلب",
  },
  CANCEL_ORDER: {
    en: "Failed to cancel order",
    ar: "فشل في إلغاء الطلب",
  },
  ADD_TO_CART: {
    en: "Failed to add item to cart",
    ar: "فشل في إضافة المنتج للسلة",
  },
  FETCH_CATEGORIES: {
    en: "Failed to fetch categories",
    ar: "فشل في جلب الفئات",
  },
};

// Mock data for fallback (extracted to separate file for bundle optimization)
import { MOCK_PRODUCTS, MOCK_CATEGORIES } from "./api.mock";

// Helper function to filter mock products
function filterMockProducts(
  products: Product[],
  filters?: ProductFilters,
): Product[] {
  let result = [...products];

  if (filters?.category) {
    result = result.filter((p) => p.category === filters.category);
  }

  if (filters?.search) {
    const search = filters.search.toLowerCase();
    result = result.filter(
      (p) =>
        p.name.toLowerCase().includes(search) ||
        p.nameAr.includes(search) ||
        p.description.toLowerCase().includes(search),
    );
  }

  if (filters?.minPrice !== undefined) {
    result = result.filter((p) => p.price >= filters.minPrice!);
  }

  if (filters?.maxPrice !== undefined) {
    result = result.filter((p) => p.price <= filters.maxPrice!);
  }

  if (filters?.status) {
    result = result.filter((p) => p.status === filters.status);
  }

  // Sorting
  if (filters?.sortBy) {
    switch (filters.sortBy) {
      case "price_asc":
        result.sort((a, b) => a.price - b.price);
        break;
      case "price_desc":
        result.sort((a, b) => b.price - a.price);
        break;
      case "name":
        result.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case "newest":
        result.sort(
          (a, b) =>
            new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
        );
        break;
      case "rating":
        result.sort((a, b) => (b.sellerRating || 0) - (a.sellerRating || 0));
        break;
    }
  }

  return result;
}

export const marketplaceApi = {
  /**
   * Get products list
   */
  async getProducts(filters?: ProductFilters): Promise<Product[]> {
    try {
      const params = new URLSearchParams();
      if (filters?.category) params.append("category", filters.category);
      if (filters?.search) params.append("search", filters.search);
      if (filters?.minPrice)
        params.append("minPrice", filters.minPrice.toString());
      if (filters?.maxPrice)
        params.append("maxPrice", filters.maxPrice.toString());
      if (filters?.status) params.append("status", filters.status);
      if (filters?.sortBy) params.append("sortBy", filters.sortBy);

      const response = await api.get(
        `${MARKETPLACE_ENDPOINTS.PRODUCTS}?${params.toString()}`,
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Using mock products data:", error);
      return filterMockProducts(MOCK_PRODUCTS, filters);
    }
  },

  /**
   * Get product by ID
   */
  async getProductById(id: string): Promise<Product> {
    try {
      const response = await api.get(buildUrl(MARKETPLACE_ENDPOINTS.PRODUCT_GET, { productId: id }));
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Using mock product data:", error);
      const product = MOCK_PRODUCTS.find((p) => p.id === id);
      if (!product) {
        throw new Error(ERROR_MESSAGES.FETCH_PRODUCT.en);
      }
      return product;
    }
  },

  /**
   * Create product listing
   */
  async createProduct(data: Partial<Product>): Promise<Product> {
    try {
      const response = await api.post(MARKETPLACE_ENDPOINTS.PRODUCTS, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to create product:", error);
      throw new Error(ERROR_MESSAGES.CREATE_PRODUCT.ar);
    }
  },

  /**
   * Update product
   */
  async updateProduct(id: string, data: Partial<Product>): Promise<Product> {
    try {
      const response = await api.patch(
        buildUrl(MARKETPLACE_ENDPOINTS.PRODUCT_GET, { productId: id }),
        data,
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to update product:", error);
      throw new Error(ERROR_MESSAGES.UPDATE_PRODUCT.ar);
    }
  },

  /**
   * Delete product
   */
  async deleteProduct(id: string): Promise<void> {
    try {
      await api.delete(buildUrl(MARKETPLACE_ENDPOINTS.PRODUCT_GET, { productId: id }));
    } catch (error) {
      logger.error("Failed to delete product:", error);
      throw new Error(ERROR_MESSAGES.DELETE_PRODUCT.ar);
    }
  },

  /**
   * Get product categories
   */
  async getCategories(): Promise<typeof MOCK_CATEGORIES> {
    try {
      const response = await api.get(`${MARKETPLACE_ENDPOINTS.PRODUCTS}/categories`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Using mock categories:", error);
      return MOCK_CATEGORIES;
    }
  },

  /**
   * Get featured products
   */
  async getFeaturedProducts(): Promise<Product[]> {
    try {
      const response = await api.get(`${MARKETPLACE_ENDPOINTS.PRODUCTS}/featured`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Using mock featured products:", error);
      return MOCK_PRODUCTS.slice(0, 3);
    }
  },

  /**
   * Get seller products
   */
  async getSellerProducts(sellerId: string): Promise<Product[]> {
    try {
      const response = await api.get(
        `${API_PREFIX}/marketplace/sellers/${sellerId}/products`,
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Using mock seller products:", error);
      return MOCK_PRODUCTS.filter((p) => p.sellerId === sellerId);
    }
  },

  /**
   * Get orders list
   */
  async getOrders(filters?: OrderFilters): Promise<Order[]> {
    try {
      const params = new URLSearchParams();
      if (filters?.status) params.append("status", filters.status);
      if (filters?.dateFrom) params.append("dateFrom", filters.dateFrom);
      if (filters?.dateTo) params.append("dateTo", filters.dateTo);

      const response = await api.get(
        `${MARKETPLACE_ENDPOINTS.ORDERS}?${params.toString()}`,
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Orders API not available:", error);
      return [];
    }
  },

  /**
   * Get order by ID
   */
  async getOrderById(id: string): Promise<Order | null> {
    try {
      const response = await api.get(`${MARKETPLACE_ENDPOINTS.ORDERS}/${id}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to fetch order:", error);
      return null;
    }
  },

  /**
   * Create order
   */
  async createOrder(data: {
    items: Array<{ productId: string; quantity: number }>;
    shippingAddress: Order["shippingAddress"];
    notes?: string;
  }): Promise<Order> {
    try {
      const response = await api.post(MARKETPLACE_ENDPOINTS.ORDERS, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to create order:", error);
      // Return mock order for development
      const order: Order = {
        id: Date.now().toString(),
        orderNumber: `ORD-${Date.now()}`,
        userId: "current-user",
        items: [],
        subtotal: 0,
        tax: 0,
        shipping: 0,
        total: 0,
        currency: "SAR",
        status: "pending",
        paymentStatus: "pending",
        shippingAddress: data.shippingAddress,
        notes: data.notes,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      return order;
    }
  },

  /**
   * Cancel order
   */
  async cancelOrder(id: string): Promise<{ success: boolean; error?: string }> {
    try {
      const response = await api.post(
        `${MARKETPLACE_ENDPOINTS.ORDERS}/${id}/cancel`,
      );
      return { success: true, ...response.data };
    } catch (error) {
      logger.error("Failed to cancel order:", error);
      return {
        success: false,
        error: ERROR_MESSAGES.CANCEL_ORDER.ar,
      };
    }
  },

  /**
   * Get cart items
   */
  async getCart(): Promise<CartItem[]> {
    try {
      const response = await api.get(`${API_PREFIX}/marketplace/cart`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Cart API not available:", error);
      return [];
    }
  },

  /**
   * Add item to cart
   */
  async addToCart(productId: string, quantity: number): Promise<CartItem> {
    try {
      const response = await api.post(`${API_PREFIX}/marketplace/cart`, {
        productId,
        quantity,
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to add to cart:", error);
      throw new Error(ERROR_MESSAGES.ADD_TO_CART.ar);
    }
  },

  /**
   * Update cart item quantity
   */
  async updateCartItem(itemId: string, quantity: number): Promise<CartItem> {
    try {
      const response = await api.patch(`${API_PREFIX}/marketplace/cart/${itemId}`, {
        quantity,
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to update cart item:", error);
      throw new Error(ERROR_MESSAGES.ADD_TO_CART.ar);
    }
  },

  /**
   * Remove item from cart
   */
  async removeFromCart(itemId: string): Promise<void> {
    try {
      await api.delete(`${API_PREFIX}/marketplace/cart/${itemId}`);
    } catch (error) {
      logger.error("Failed to remove from cart:", error);
      throw error;
    }
  },

  /**
   * Clear cart
   */
  async clearCart(): Promise<void> {
    try {
      await api.delete(`${API_PREFIX}/marketplace/cart`);
    } catch (error) {
      logger.error("Failed to clear cart:", error);
      throw error;
    }
  },

  /**
   * Search products
   */
  async searchProducts(query: string): Promise<Product[]> {
    try {
      const response = await api.get(
        `${MARKETPLACE_ENDPOINTS.PRODUCTS}/search?q=${encodeURIComponent(query)}`,
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Using mock search:", error);
      return filterMockProducts(MOCK_PRODUCTS, { search: query });
    }
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
    try {
      const response = await api.get(
        `${buildUrl(MARKETPLACE_ENDPOINTS.PRODUCT_GET, { productId })}/reviews`,
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Reviews API not available:", error);
      return [];
    }
  },

  /**
   * Add product review
   */
  async addProductReview(
    productId: string,
    data: { rating: number; comment: string },
  ): Promise<void> {
    try {
      await api.post(`${buildUrl(MARKETPLACE_ENDPOINTS.PRODUCT_GET, { productId })}/reviews`, data);
    } catch (error) {
      logger.error("Failed to add review:", error);
      throw error;
    }
  },
};
