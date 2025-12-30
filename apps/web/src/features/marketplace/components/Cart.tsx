/**
 * Cart Component
 * سلة التسوق
 */

'use client';

import React from 'react';
import { X, Minus, Plus, ShoppingCart, Trash2, CreditCard } from 'lucide-react';
import { useCart } from '../hooks/useCart';

interface CartProps {
  isOpen: boolean;
  onClose: () => void;
  onCheckout?: () => void;
}

export const Cart: React.FC<CartProps> = ({ isOpen, onClose, onCheckout }) => {
  const { cart, removeItem, updateQuantity } = useCart();

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
        data-testid="cart-backdrop"
      />

      {/* Cart Sidebar */}
      <div className="fixed top-0 right-0 h-full w-full sm:w-96 bg-white z-50 shadow-2xl transform transition-transform duration-300" data-testid="cart-sidebar">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200" data-testid="cart-header">
          <div className="flex items-center gap-2">
            <ShoppingCart className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold" data-testid="cart-title">سلة التسوق</h2>
            <span className="px-2 py-1 bg-blue-100 text-blue-600 rounded-full text-sm font-semibold" data-testid="cart-items-count">
              {cart.items.length}
            </span>
          </div>
          <button
            onClick={onClose}
            data-testid="cart-close-button"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Cart Items */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 h-[calc(100vh-280px)]" data-testid="cart-items-container">
          {cart.items.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-16" data-testid="cart-empty-state">
              <ShoppingCart className="w-16 h-16 text-gray-300 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">سلة التسوق فارغة</h3>
              <p className="text-gray-500">ابدأ بإضافة المنتجات إلى سلتك</p>
            </div>
          ) : (
            cart.items.map((item) => (
              <CartItem
                key={item.productId}
                item={item}
                onRemove={() => removeItem(item.productId)}
                onUpdateQuantity={(quantity) => updateQuantity(item.productId, quantity)}
              />
            ))
          )}
        </div>

        {/* Cart Summary & Checkout */}
        {cart.items.length > 0 && (
          <div className="border-t border-gray-200 p-4 space-y-4" data-testid="cart-summary">
            {/* Summary */}
            <div className="space-y-2 text-sm">
              <div className="flex justify-between text-gray-600" data-testid="cart-subtotal">
                <span>المجموع الفرعي</span>
                <span>
                  {cart.subtotal.toFixed(2)} {cart.currency}
                </span>
              </div>
              <div className="flex justify-between text-gray-600" data-testid="cart-tax">
                <span>الضريبة (15%)</span>
                <span>
                  {cart.tax.toFixed(2)} {cart.currency}
                </span>
              </div>
              <div className="flex justify-between text-gray-600" data-testid="cart-shipping">
                <span>الشحن</span>
                <span>
                  {cart.shipping === 0 ? (
                    <span className="text-green-600 font-semibold">مجاني</span>
                  ) : (
                    `${cart.shipping.toFixed(2)} ${cart.currency}`
                  )}
                </span>
              </div>
              {cart.shipping > 0 && cart.subtotal > 400 && (
                <div className="text-xs text-orange-600" data-testid="cart-free-shipping-notice">
                  أضف منتجات بقيمة {(500 - cart.subtotal).toFixed(2)} {cart.currency} للشحن
                  المجاني!
                </div>
              )}
              <div className="flex justify-between text-lg font-bold pt-2 border-t border-gray-200" data-testid="cart-total">
                <span>الإجمالي</span>
                <span className="text-blue-600">
                  {cart.total.toFixed(2)} {cart.currency}
                </span>
              </div>
            </div>

            {/* Checkout Button */}
            <button
              onClick={onCheckout}
              data-testid="checkout-button"
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
            >
              <CreditCard className="w-5 h-5" />
              <span>إتمام الطلب</span>
            </button>
          </div>
        )}
      </div>
    </>
  );
};

/**
 * Cart Item Component
 */
interface CartItemProps {
  item: {
    productId: string;
    product: {
      id: string;
      name: string;
      nameAr: string;
      price: number;
      currency: string;
      imageUrl?: string;
      unit: string;
      unitAr: string;
    };
    quantity: number;
  };
  onRemove: () => void;
  onUpdateQuantity: (quantity: number) => void;
}

const CartItem: React.FC<CartItemProps> = ({ item, onRemove, onUpdateQuantity }) => {
  const { product, quantity } = item;
  const total = product.price * quantity;

  return (
    <div className="flex gap-3 p-3 bg-gray-50 rounded-lg" data-testid="cart-item" data-product-id={product.id}>
      {/* Image */}
      <div className="w-20 h-20 flex-shrink-0 bg-white rounded-lg overflow-hidden" data-testid="cart-item-image">
        {product.imageUrl ? (
          <img src={product.imageUrl} alt={product.name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <ShoppingCart className="w-8 h-8 text-gray-300" />
          </div>
        )}
      </div>

      {/* Details */}
      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-gray-900 line-clamp-1" data-testid="cart-item-name-ar">{product.nameAr}</h4>
        <p className="text-sm text-gray-600 line-clamp-1" data-testid="cart-item-name-en">{product.name}</p>

        <div className="flex items-center justify-between mt-2">
          {/* Quantity Controls */}
          <div className="flex items-center gap-2" data-testid="cart-item-quantity-controls">
            <button
              onClick={() => onUpdateQuantity(quantity - 1)}
              data-testid="cart-item-decrease-quantity"
              className="p-1 hover:bg-gray-200 rounded transition-colors"
            >
              <Minus className="w-4 h-4" />
            </button>
            <span className="w-8 text-center font-semibold" data-testid="cart-item-quantity">{quantity}</span>
            <button
              onClick={() => onUpdateQuantity(quantity + 1)}
              data-testid="cart-item-increase-quantity"
              className="p-1 hover:bg-gray-200 rounded transition-colors"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          {/* Price */}
          <div className="text-right">
            <div className="font-bold text-gray-900" data-testid="cart-item-total">
              {total.toFixed(2)} {product.currency}
            </div>
            <div className="text-xs text-gray-500" data-testid="cart-item-unit-price">
              {product.price.toFixed(2)} / {product.unitAr}
            </div>
          </div>
        </div>
      </div>

      {/* Remove Button */}
      <button
        onClick={onRemove}
        data-testid="cart-item-remove"
        className="p-2 hover:bg-red-50 text-red-600 rounded-lg transition-colors self-start"
      >
        <Trash2 className="w-5 h-5" />
      </button>
    </div>
  );
};

export default Cart;
