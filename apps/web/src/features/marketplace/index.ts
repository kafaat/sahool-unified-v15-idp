/**
 * Marketplace Feature
 * ميزة السوق الزراعي
 *
 * This feature handles:
 * - Product browsing and search
 * - Shopping cart management
 * - Order placement and tracking
 * - Seller information
 */

// API
export { marketplaceApi } from "./api";

// Types
export type {
  Product,
  ProductCategory,
  ProductStatus,
  ProductFilters,
  CartItem,
  Cart,
  Order,
  OrderStatus,
  PaymentStatus,
  OrderFilters,
} from "./types";

// Hooks - Products
export {
  useProducts,
  useProduct,
  useOrders,
  useOrder,
  useCreateOrder,
  useCancelOrder,
  marketplaceKeys,
} from "./hooks/useProducts";

// Hooks - Cart
export { useCart, CartProvider } from "./hooks/useCart";

// Components
export { ProductsGrid } from "./components/ProductsGrid";
export { ProductCard } from "./components/ProductCard";
export { Cart as CartSidebar } from "./components/Cart";
