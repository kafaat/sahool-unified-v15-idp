/**
 * ProductCard Component
 * بطاقة المنتج
 */

'use client';

import React from 'react';
import { ShoppingCart, Star, MapPin, Tag } from 'lucide-react';
import type { Product } from '../types';
import { useCart } from '../hooks/useCart';

interface ProductCardProps {
  product: Product;
  onClick?: () => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product, onClick }) => {
  const { addItem } = useCart();

  const handleAddToCart = (e: React.MouseEvent) => {
    e.stopPropagation();
    addItem(product, 1);
  };

  const discountedPrice = product.discount
    ? product.price * (1 - product.discount.percentage / 100)
    : null;

  const isOutOfStock = product.status === 'out_of_stock';

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl border-2 border-gray-200 hover:border-blue-400 transition-all cursor-pointer overflow-hidden group"
    >
      {/* Image */}
      <div className="relative h-48 overflow-hidden bg-gray-100">
        {product.imageUrl ? (
          <img
            src={product.imageUrl}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Tag className="w-16 h-16 text-gray-300" />
          </div>
        )}

        {/* Discount Badge */}
        {product.discount && (
          <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded-lg text-sm font-semibold">
            -{product.discount.percentage}%
          </div>
        )}

        {/* Status Badge */}
        {isOutOfStock && (
          <div className="absolute top-2 right-2 bg-gray-800 text-white px-2 py-1 rounded-lg text-sm font-semibold">
            نفذت الكمية
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {/* Category */}
        <div className="text-xs text-blue-600 font-semibold uppercase">
          {getCategoryLabel(product.category)}
        </div>

        {/* Name */}
        <div>
          <h3 className="text-lg font-bold text-gray-900 line-clamp-1">{product.nameAr}</h3>
          <p className="text-sm text-gray-600 line-clamp-1">{product.name}</p>
        </div>

        {/* Seller & Location */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <MapPin className="w-4 h-4" />
          <span className="line-clamp-1">{product.sellerName}</span>
        </div>

        {product.sellerRating && (
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
            <span className="text-sm font-semibold">{product.sellerRating}</span>
          </div>
        )}

        {/* Price */}
        <div className="flex items-end justify-between pt-2 border-t border-gray-200">
          <div>
            {discountedPrice ? (
              <>
                <div className="text-2xl font-bold text-green-600">
                  {discountedPrice.toFixed(2)} {product.currency}
                </div>
                <div className="text-sm text-gray-500 line-through">
                  {product.price.toFixed(2)} {product.currency}
                </div>
              </>
            ) : (
              <div className="text-2xl font-bold text-gray-900">
                {product.price.toFixed(2)} {product.currency}
              </div>
            )}
            <div className="text-xs text-gray-500">
              {product.unitAr} | {product.unit}
            </div>
          </div>

          {/* Add to Cart Button */}
          <button
            onClick={handleAddToCart}
            disabled={isOutOfStock}
            className={`p-3 rounded-lg transition-all ${
              isOutOfStock
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
            }`}
          >
            <ShoppingCart className="w-5 h-5" />
          </button>
        </div>

        {/* Stock Indicator */}
        {!isOutOfStock && product.stock < 10 && (
          <div className="text-xs text-orange-600 font-semibold">
            الكمية المتبقية: {product.stock}
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Get category label in Arabic
 */
function getCategoryLabel(category: Product['category']): string {
  const labels: Record<typeof category, string> = {
    seeds: 'بذور',
    fertilizers: 'أسمدة',
    pesticides: 'مبيدات',
    equipment: 'معدات',
    tools: 'أدوات',
    irrigation: 'ري',
    produce: 'منتجات',
    other: 'أخرى',
  };
  return labels[category] || category;
}
