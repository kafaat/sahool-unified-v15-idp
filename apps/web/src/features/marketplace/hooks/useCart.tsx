/**
 * Marketplace Feature - Cart Hook
 * خطاف سلة التسوق
 */

"use client";

import * as React from "react";
import type { Product, CartItem, Cart } from "../types";
import { logger } from "@/lib/logger";

const CART_STORAGE_KEY = "sahool-cart";
const CART_STORAGE_VERSION = 1;

interface StoredCart {
  version: number;
  checksum: string;
  items: CartItem[];
}

/**
 * Simple checksum for cart data integrity validation.
 * Not cryptographic - just detects accidental corruption or tampering.
 */
function computeChecksum(items: CartItem[]): string {
  const data = JSON.stringify(items);
  let hash = 0;
  for (let i = 0; i < data.length; i++) {
    const char = data.charCodeAt(i);
    hash = ((hash << 5) - hash + char) | 0;
  }
  return `v${CART_STORAGE_VERSION}-${hash.toString(36)}`;
}

/**
 * Read cart items from localStorage with integrity validation.
 */
function readCartFromStorage(): CartItem[] {
  try {
    const raw = localStorage.getItem(CART_STORAGE_KEY);
    if (!raw) return [];

    const stored: StoredCart = JSON.parse(raw);

    // Validate storage version
    if (stored.version !== CART_STORAGE_VERSION) {
      logger.warn("Cart storage version mismatch, clearing cart");
      localStorage.removeItem(CART_STORAGE_KEY);
      return [];
    }

    // Validate checksum
    if (!stored.items || !Array.isArray(stored.items)) {
      logger.warn("Cart data invalid structure, clearing cart");
      localStorage.removeItem(CART_STORAGE_KEY);
      return [];
    }

    const expectedChecksum = computeChecksum(stored.items);
    if (stored.checksum !== expectedChecksum) {
      logger.warn("Cart data integrity check failed, clearing cart");
      localStorage.removeItem(CART_STORAGE_KEY);
      return [];
    }

    return stored.items;
  } catch (error) {
    logger.error("Failed to load cart:", error);
    localStorage.removeItem(CART_STORAGE_KEY);
    return [];
  }
}

/**
 * Write cart items to localStorage with checksum.
 */
function writeCartToStorage(items: CartItem[]): void {
  try {
    const stored: StoredCart = {
      version: CART_STORAGE_VERSION,
      checksum: computeChecksum(items),
      items,
    };
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(stored));
  } catch (error) {
    logger.error("Failed to save cart:", error);
  }
}

interface CartContextType {
  cart: Cart;
  addItem: (product: Product, quantity?: number) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
}

const CartContext = React.createContext<CartContextType | null>(null);

/**
 * Calculate cart totals
 */
function calculateTotals(items: CartItem[]): Cart {
  const subtotal = items.reduce(
    (sum, item) => sum + item.product.price * item.quantity,
    0,
  );
  const tax = subtotal * 0.15; // 15% VAT
  const shipping = subtotal > 500 ? 0 : 25; // Free shipping over 500 SAR
  const total = subtotal + tax + shipping;

  return {
    items,
    subtotal,
    tax,
    shipping,
    total,
    currency: "SAR",
  };
}

/**
 * Cart Provider Component
 */
export function CartProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = React.useState<CartItem[]>([]);

  // Load cart from localStorage on mount
  React.useEffect(() => {
    const loaded = readCartFromStorage();
    if (loaded.length > 0) {
      setItems(loaded);
    }
  }, []);

  // Save cart to localStorage on change
  React.useEffect(() => {
    writeCartToStorage(items);
  }, [items]);

  const addItem = React.useCallback((product: Product, quantity = 1) => {
    setItems((prevItems) => {
      const existingItem = prevItems.find(
        (item) => item.productId === product.id,
      );

      if (existingItem) {
        // Update quantity of existing item
        return prevItems.map((item) =>
          item.productId === product.id
            ? { ...item, quantity: item.quantity + quantity }
            : item,
        );
      }

      // Add new item
      return [
        ...prevItems,
        {
          productId: product.id,
          product,
          quantity,
          addedAt: new Date().toISOString(),
        },
      ];
    });
  }, []);

  const removeItem = React.useCallback((productId: string) => {
    setItems((prevItems) =>
      prevItems.filter((item) => item.productId !== productId),
    );
  }, []);

  const updateQuantity = React.useCallback(
    (productId: string, quantity: number) => {
      if (quantity <= 0) {
        setItems((prevItems) =>
          prevItems.filter((item) => item.productId !== productId),
        );
        return;
      }

      setItems((prevItems) =>
        prevItems.map((item) =>
          item.productId === productId ? { ...item, quantity } : item,
        ),
      );
    },
    [],
  );

  const clearCart = React.useCallback(() => {
    setItems([]);
  }, []);

  const cart = React.useMemo(() => calculateTotals(items), [items]);

  const value = React.useMemo(
    () => ({ cart, addItem, removeItem, updateQuantity, clearCart }),
    [cart, addItem, removeItem, updateQuantity, clearCart],
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

/**
 * Hook to use cart
 */
export const useCart = () => {
  const context = React.useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used within CartProvider");
  }
  return context;
};
