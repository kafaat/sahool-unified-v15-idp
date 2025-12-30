'use client';

/**
 * SAHOOL Marketplace Page Client Component
 * صفحة السوق الزراعي
 */

import React, { useState } from 'react';
import { ShoppingCart as ShoppingCartIcon, Package, TrendingUp } from 'lucide-react';
import {
  ProductsGrid,
  CartSidebar,
  CartProvider,
  useCart,
  useProducts,
  useOrders,
} from '@/features/marketplace';
import { ErrorTracking } from '@/lib/monitoring/error-tracking';

function MarketplaceContent() {
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [, setSelectedProductId] = useState<string | null>(null);
  const { cart } = useCart();
  const { data: products } = useProducts();
  const { data: orders } = useOrders();

  const totalProducts = products?.length || 0;
  const totalOrders = orders?.length || 0;
  const cartItemsCount = cart.items.length;

  const handleCheckout = () => {
    try {
      ErrorTracking.addBreadcrumb({
        type: 'click',
        category: 'ui',
        message: 'Checkout initiated',
        data: {
          itemsCount: cart.items.length,
          total: cart.total,
          currency: cart.currency
        },
      });
      // TODO: Implement checkout flow
      alert('ميزة الدفع قيد التطوير | Checkout feature coming soon');
      setIsCartOpen(false);
    } catch (error) {
      ErrorTracking.captureError(
        error instanceof Error ? error : new Error('Checkout failed'),
        undefined,
        { cart }
      );
    }
  };

  return (
    <div className="space-y-6" data-testid="marketplace-page">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="marketplace-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900" data-testid="marketplace-title">السوق الزراعي</h1>
            <p className="text-gray-600 mt-1" data-testid="marketplace-subtitle">Agricultural Marketplace</p>
          </div>
          <button
            onClick={() => setIsCartOpen(true)}
            data-testid="cart-button"
            className="relative flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            <ShoppingCartIcon className="w-5 h-5" />
            <span>السلة</span>
            {cartItemsCount > 0 && (
              <span className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs font-bold" data-testid="cart-count-badge">
                {cartItemsCount}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6" data-testid="statistics-cards">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="stat-card-products">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Package className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1" data-testid="stat-products-count">{totalProducts}</h3>
          <p className="text-sm text-gray-600">منتجات متاحة | Available Products</p>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="stat-card-cart">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <ShoppingCartIcon className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1" data-testid="stat-cart-count">{cartItemsCount}</h3>
          <p className="text-sm text-gray-600">منتجات في السلة | Items in Cart</p>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="stat-card-orders">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-orange-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1" data-testid="stat-orders-count">{totalOrders}</h3>
          <p className="text-sm text-gray-600">طلباتي | My Orders</p>
        </div>
      </div>

      {/* Cart Summary Banner */}
      {cartItemsCount > 0 && (
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-6 text-white" data-testid="cart-summary-banner">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold mb-1" data-testid="cart-summary-title">لديك {cartItemsCount} منتجات في السلة</h3>
              <p className="text-blue-100" data-testid="cart-summary-total">
                الإجمالي: {cart.total.toFixed(2)} {cart.currency}
              </p>
            </div>
            <button
              onClick={() => setIsCartOpen(true)}
              data-testid="cart-summary-button"
              className="px-6 py-3 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-semibold"
            >
              مراجعة السلة
            </button>
          </div>
        </div>
      )}

      {/* Products Grid */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="products-section">
        <h2 className="text-xl font-bold text-gray-900 mb-6" data-testid="products-heading">المنتجات</h2>
        <ProductsGrid onProductClick={setSelectedProductId} />
      </div>

      {/* Cart Sidebar */}
      <CartSidebar
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        onCheckout={handleCheckout}
      />
    </div>
  );
}

export default function MarketplaceClient() {
  return (
    <CartProvider>
      <MarketplaceContent />
    </CartProvider>
  );
}
