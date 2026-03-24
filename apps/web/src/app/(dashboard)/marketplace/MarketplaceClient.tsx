'use client';

/**
 * SAHOOL Marketplace Page Client Component
 * صفحة السوق الزراعي
 */

import React, { useState } from 'react';
import {
  ShoppingCart as ShoppingCartIcon,
  Package,
  TrendingUp,
  Loader2,
  CheckCircle,
  MapPin,
} from 'lucide-react';
import {
  ProductsGrid,
  CartSidebar,
  CartProvider,
  useCart,
  useProducts,
  useOrders,
  useCreateOrder,
} from '@/features/marketplace';
import type { Order } from '@/features/marketplace';
import { ErrorTracking } from '@/lib/monitoring/error-tracking';
import { Modal, ModalFooter, useToast } from '@/components/ui';

// Initial shipping address state
const initialShippingAddress: Order['shippingAddress'] = {
  name: '',
  phone: '',
  addressLine1: '',
  addressLine2: '',
  city: '',
  region: '',
  postalCode: '',
  country: 'Saudi Arabia',
};

function MarketplaceContent() {
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [isOrderSuccess, setIsOrderSuccess] = useState(false);
  const [orderNumber, setOrderNumber] = useState<string | null>(null);
  const [, setSelectedProductId] = useState<string | null>(null);
  const [shippingAddress, setShippingAddress] =
    useState<Order['shippingAddress']>(initialShippingAddress);
  const [orderNotes, setOrderNotes] = useState('');

  const { cart, clearCart } = useCart();
  const { data: products } = useProducts();
  const { data: orders } = useOrders();
  const { showToast } = useToast();
  const createOrderMutation = useCreateOrder();

  const totalProducts = products?.length || 0;
  const totalOrders = orders?.length || 0;
  const cartItemsCount = cart.items.length;

  // Validate shipping address
  const isAddressValid = () => {
    return (
      shippingAddress.name.trim() !== '' &&
      shippingAddress.phone.trim() !== '' &&
      shippingAddress.addressLine1.trim() !== '' &&
      shippingAddress.city.trim() !== '' &&
      shippingAddress.region.trim() !== ''
    );
  };

  // Handle opening checkout modal
  const handleCheckout = () => {
    try {
      ErrorTracking.addBreadcrumb({
        type: 'click',
        category: 'ui',
        message: 'Checkout initiated',
        data: {
          itemsCount: cart.items.length,
          total: cart.total,
          currency: cart.currency,
        },
      });

      // Close cart sidebar and open checkout modal
      setIsCartOpen(false);
      setIsCheckoutOpen(true);
    } catch (error) {
      ErrorTracking.captureError(
        error instanceof Error ? error : new Error('Checkout failed'),
        undefined,
        { cart }
      );
    }
  };

  // Handle order submission
  const handleSubmitOrder = async () => {
    if (!isAddressValid()) {
      showToast({
        type: 'error',
        message: 'Please fill in all required fields',
        messageAr: 'يرجى ملء جميع الحقول المطلوبة',
      });
      return;
    }

    try {
      ErrorTracking.addBreadcrumb({
        type: 'click',
        category: 'checkout',
        message: 'Order submission started',
        data: {
          itemsCount: cart.items.length,
          total: cart.total,
        },
      });

      const orderItems = cart.items.map((item) => ({
        productId: item.productId,
        quantity: item.quantity,
      }));

      const result = await createOrderMutation.mutateAsync({
        items: orderItems,
        shippingAddress,
        notes: orderNotes || undefined,
      });

      // Success - show success screen
      setOrderNumber(result.orderNumber);
      setIsOrderSuccess(true);
      clearCart();

      showToast({
        type: 'success',
        message: `Order ${result.orderNumber} placed successfully!`,
        messageAr: `تم تأكيد الطلب ${result.orderNumber} بنجاح!`,
      });

      ErrorTracking.addBreadcrumb({
        type: 'console',
        category: 'checkout',
        message: 'Order placed successfully',
        data: { orderId: result.id, orderNumber: result.orderNumber },
      });
    } catch (error) {
      ErrorTracking.captureError(
        error instanceof Error ? error : new Error('Order submission failed'),
        undefined,
        { cart, shippingAddress }
      );

      showToast({
        type: 'error',
        message: 'Failed to place order. Please try again.',
        messageAr: 'فشل في إتمام الطلب. يرجى المحاولة مرة أخرى.',
      });
    }
  };

  // Handle closing checkout modal
  const handleCloseCheckout = () => {
    setIsCheckoutOpen(false);
    setIsOrderSuccess(false);
    setOrderNumber(null);
    setShippingAddress(initialShippingAddress);
    setOrderNotes('');
  };

  // Update shipping address field
  const updateShippingField = (field: keyof Order['shippingAddress'], value: string) => {
    setShippingAddress((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">السوق الزراعي</h1>
            <p className="text-gray-600 mt-1">Agricultural Marketplace</p>
          </div>
          <button
            onClick={() => setIsCartOpen(true)}
            className="relative flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            <ShoppingCartIcon className="w-5 h-5" />
            <span>السلة</span>
            {cartItemsCount > 0 && (
              <span className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                {cartItemsCount}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Package className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">{totalProducts}</h3>
          <p className="text-sm text-gray-600">منتجات متاحة | Available Products</p>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <ShoppingCartIcon className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">{cartItemsCount}</h3>
          <p className="text-sm text-gray-600">منتجات في السلة | Items in Cart</p>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-orange-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">{totalOrders}</h3>
          <p className="text-sm text-gray-600">طلباتي | My Orders</p>
        </div>
      </div>

      {/* Cart Summary Banner */}
      {cartItemsCount > 0 && (
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold mb-1">لديك {cartItemsCount} منتجات في السلة</h3>
              <p className="text-blue-100">
                الإجمالي: {cart.total.toFixed(2)} {cart.currency}
              </p>
            </div>
            <button
              onClick={() => setIsCartOpen(true)}
              className="px-6 py-3 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-semibold"
            >
              مراجعة السلة
            </button>
          </div>
        </div>
      )}

      {/* Products Grid */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">المنتجات</h2>
        <ProductsGrid onProductClick={setSelectedProductId} />
      </div>

      {/* Cart Sidebar */}
      <CartSidebar
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        onCheckout={handleCheckout}
      />

      {/* Checkout Modal */}
      <Modal
        isOpen={isCheckoutOpen}
        onClose={handleCloseCheckout}
        title="Checkout"
        titleAr="إتمام الطلب"
        size="lg"
        closeOnOverlay={!createOrderMutation.isPending}
      >
        {isOrderSuccess ? (
          // Order Success Screen
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">تم تأكيد طلبك بنجاح!</h3>
            <p className="text-gray-600 mb-1">Order Confirmed Successfully!</p>
            <p className="text-lg font-semibold text-blue-600 mb-6">رقم الطلب: {orderNumber}</p>
            <p className="text-sm text-gray-500 mb-6">
              سيتم إرسال تفاصيل الطلب إلى هاتفك
              <br />
              Order details will be sent to your phone
            </p>
            <button
              onClick={handleCloseCheckout}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
            >
              متابعة التسوق | Continue Shopping
            </button>
          </div>
        ) : (
          // Checkout Form
          <div className="space-y-6">
            {/* Order Summary */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <ShoppingCartIcon className="w-5 h-5" />
                ملخص الطلب | Order Summary
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">عدد المنتجات | Items</span>
                  <span className="font-semibold">{cart.items.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">المجموع الفرعي | Subtotal</span>
                  <span>
                    {cart.subtotal.toFixed(2)} {cart.currency}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">الضريبة | Tax (15%)</span>
                  <span>
                    {cart.tax.toFixed(2)} {cart.currency}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">الشحن | Shipping</span>
                  <span>
                    {cart.shipping === 0 ? (
                      <span className="text-green-600">مجاني | Free</span>
                    ) : (
                      `${cart.shipping.toFixed(2)} ${cart.currency}`
                    )}
                  </span>
                </div>
                <div className="flex justify-between pt-2 border-t border-gray-200 text-lg font-bold">
                  <span>الإجمالي | Total</span>
                  <span className="text-blue-600">
                    {cart.total.toFixed(2)} {cart.currency}
                  </span>
                </div>
              </div>
            </div>

            {/* Shipping Address Form */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <MapPin className="w-5 h-5" />
                عنوان الشحن | Shipping Address
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    الاسم | Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={shippingAddress.name}
                    onChange={(e) => updateShippingField('name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="الاسم الكامل"
                    disabled={createOrderMutation.isPending}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    الهاتف | Phone <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="tel"
                    value={shippingAddress.phone}
                    onChange={(e) => updateShippingField('phone', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="+966 5XX XXX XXXX"
                    dir="ltr"
                    disabled={createOrderMutation.isPending}
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    العنوان | Address Line 1 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={shippingAddress.addressLine1}
                    onChange={(e) => updateShippingField('addressLine1', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="الشارع، رقم المبنى"
                    disabled={createOrderMutation.isPending}
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    العنوان الإضافي | Address Line 2
                  </label>
                  <input
                    type="text"
                    value={shippingAddress.addressLine2 || ''}
                    onChange={(e) => updateShippingField('addressLine2', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="الشقة، الطابق (اختياري)"
                    disabled={createOrderMutation.isPending}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    المدينة | City <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={shippingAddress.city}
                    onChange={(e) => updateShippingField('city', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="المدينة"
                    disabled={createOrderMutation.isPending}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    المنطقة | Region <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={shippingAddress.region}
                    onChange={(e) => updateShippingField('region', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="المنطقة"
                    disabled={createOrderMutation.isPending}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    الرمز البريدي | Postal Code
                  </label>
                  <input
                    type="text"
                    value={shippingAddress.postalCode || ''}
                    onChange={(e) => updateShippingField('postalCode', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="12345"
                    dir="ltr"
                    disabled={createOrderMutation.isPending}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    الدولة | Country
                  </label>
                  <input
                    type="text"
                    value={shippingAddress.country}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-600"
                    disabled
                  />
                </div>
              </div>
            </div>

            {/* Order Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                ملاحظات | Order Notes
              </label>
              <textarea
                value={orderNotes}
                onChange={(e) => setOrderNotes(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                placeholder="ملاحظات إضافية للتوصيل (اختياري)"
                disabled={createOrderMutation.isPending}
              />
            </div>

            {/* Payment Info Note */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
              <p className="font-semibold mb-1">طريقة الدفع | Payment Method</p>
              <p>الدفع عند الاستلام | Cash on Delivery (COD)</p>
            </div>
          </div>
        )}

        {/* Modal Footer - only show when not in success state */}
        {!isOrderSuccess && (
          <ModalFooter className="-mx-6 -mb-6 mt-6">
            <button
              onClick={handleCloseCheckout}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              disabled={createOrderMutation.isPending}
            >
              إلغاء | Cancel
            </button>
            <button
              onClick={handleSubmitOrder}
              disabled={createOrderMutation.isPending || !isAddressValid()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {createOrderMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  جاري المعالجة...
                </>
              ) : (
                <>تأكيد الطلب | Confirm Order</>
              )}
            </button>
          </ModalFooter>
        )}
      </Modal>
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
