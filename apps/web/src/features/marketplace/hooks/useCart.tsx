/**
 * Marketplace Feature - Cart Hook
 * خطاف سلة التسوق
 */

"use client";

import * as React from "react";
import type { Product, CartItem, Cart } from "../types";
import { logger } from "@/lib/logger";

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
    const savedCart = localStorage.getItem("sahool-cart");
    if (savedCart) {
      try {
        setItems(JSON.parse(savedCart));
      } catch (error) {
        logger.error("Failed to load cart:", error);
      }
    }
  }, []);

  // Save cart to localStorage on change
  React.useEffect(() => {
    localStorage.setItem("sahool-cart", JSON.stringify(items));
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
