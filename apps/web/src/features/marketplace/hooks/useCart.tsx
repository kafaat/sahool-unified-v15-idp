/**
 * Marketplace Feature - Cart Hook
 * خطاف سلة التسوق
 */

'use client';

import { createContext, useContext, useState, useCallback, useMemo, ReactNode, useEffect } from 'react';
import { z } from 'zod';
import CryptoJS from 'crypto-js';
import type { Product, CartItem, Cart } from '../types';

// Encryption key for cart data (should be stored securely in env variables in production)
const CART_ENCRYPTION_KEY = process.env.NEXT_PUBLIC_CART_ENCRYPTION_KEY || 'sahool-cart-secret-key-2025';
const CART_STORAGE_KEY = 'sahool-cart-encrypted';

// Zod schemas for validation
const ProductSchema: z.ZodType<Product> = z.object({
  id: z.string(),
  name: z.string(),
  nameAr: z.string(),
  description: z.string(),
  descriptionAr: z.string(),
  category: z.enum(['seeds', 'fertilizers', 'pesticides', 'equipment', 'tools', 'irrigation', 'produce', 'other']),
  price: z.number().positive(),
  currency: z.string(),
  unit: z.string(),
  unitAr: z.string(),
  status: z.enum(['available', 'out_of_stock', 'discontinued']),
  stock: z.number().nonnegative(),
  imageUrl: z.string().optional(),
  images: z.array(z.string()).optional(),
  sellerId: z.string(),
  sellerName: z.string(),
  sellerRating: z.number().optional(),
  location: z.object({
    city: z.string(),
    cityAr: z.string(),
    region: z.string(),
    regionAr: z.string(),
  }).optional(),
  specifications: z.record(z.string(), z.unknown()).optional(),
  tags: z.array(z.string()).optional(),
  discount: z.object({
    percentage: z.number(),
    validUntil: z.string(),
  }).optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
}) as z.ZodType<Product>;

const CartItemSchema = z.object({
  productId: z.string(),
  product: ProductSchema,
  quantity: z.number().positive().int(),
  addedAt: z.string(),
});

const CartItemsSchema = z.array(CartItemSchema);

/**
 * Encrypt cart data
 */
function encryptCartData(data: CartItem[]): string {
  try {
    const jsonString = JSON.stringify(data);
    return CryptoJS.AES.encrypt(jsonString, CART_ENCRYPTION_KEY).toString();
  } catch (error) {
    console.error('Failed to encrypt cart data:', error);
    return '';
  }
}

/**
 * Decrypt and validate cart data
 */
function decryptCartData(encryptedData: string): CartItem[] {
  try {
    const bytes = CryptoJS.AES.decrypt(encryptedData, CART_ENCRYPTION_KEY);
    const decryptedString = bytes.toString(CryptoJS.enc.Utf8);

    if (!decryptedString) {
      console.warn('Failed to decrypt cart data');
      return [];
    }

    const parsed = JSON.parse(decryptedString);

    // Validate with Zod schema
    const validated = CartItemsSchema.parse(parsed);
    return validated;
  } catch (error) {
    console.error('Failed to decrypt or validate cart data:', error);
    return [];
  }
}

interface CartContextType {
  cart: Cart;
  addItem: (product: Product, quantity?: number) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
}

const CartContext = createContext<CartContextType | null>(null);

/**
 * Calculate cart totals
 */
function calculateTotals(items: CartItem[]): Cart {
  const subtotal = items.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
  const tax = subtotal * 0.15; // 15% VAT
  const shipping = subtotal > 500 ? 0 : 25; // Free shipping over 500 SAR
  const total = subtotal + tax + shipping;

  return {
    items,
    subtotal,
    tax,
    shipping,
    total,
    currency: 'SAR',
  };
}

/**
 * Cart Provider Component
 */
export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);

  // Load cart from localStorage on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      const encryptedCart = localStorage.getItem(CART_STORAGE_KEY);
      if (encryptedCart) {
        const decryptedItems = decryptCartData(encryptedCart);
        setItems(decryptedItems);
      } else {
        // Try to migrate from old unencrypted cart
        const oldCart = localStorage.getItem('sahool-cart');
        if (oldCart) {
          try {
            const parsed = JSON.parse(oldCart);
            const validated = CartItemsSchema.parse(parsed);
            setItems(validated);
            // Remove old unencrypted cart
            localStorage.removeItem('sahool-cart');
          } catch (error) {
            console.error('Failed to migrate old cart:', error);
          }
        }
      }
    } catch (error) {
      console.error('Failed to load cart:', error);
    }
  }, []);

  // Save cart to localStorage on change (encrypted)
  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      const encrypted = encryptCartData(items);
      if (encrypted) {
        localStorage.setItem(CART_STORAGE_KEY, encrypted);
      }
    } catch (error) {
      console.error('Failed to save cart:', error);
    }
  }, [items]);

  const addItem = useCallback((product: Product, quantity = 1) => {
    setItems((prevItems) => {
      const existingItem = prevItems.find((item) => item.productId === product.id);

      if (existingItem) {
        // Update quantity of existing item
        return prevItems.map((item) =>
          item.productId === product.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
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

  const removeItem = useCallback((productId: string) => {
    setItems((prevItems) => prevItems.filter((item) => item.productId !== productId));
  }, []);

  const updateQuantity = useCallback((productId: string, quantity: number) => {
    if (quantity <= 0) {
      setItems((prevItems) => prevItems.filter((item) => item.productId !== productId));
      return;
    }

    setItems((prevItems) =>
      prevItems.map((item) => (item.productId === productId ? { ...item, quantity } : item))
    );
  }, []);

  const clearCart = useCallback(() => {
    setItems([]);
  }, []);

  const cart = useMemo(() => calculateTotals(items), [items]);

  const value = useMemo(
    () => ({ cart, addItem, removeItem, updateQuantity, clearCart }),
    [cart, addItem, removeItem, updateQuantity, clearCart]
  );

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
}

/**
 * Hook to use cart
 */
export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
};
