/**
 * ProductsGrid Component
 * شبكة المنتجات
 */

'use client';

import React, { useState } from 'react';
import { Search, Filter, ShoppingBag } from 'lucide-react';
import { useProducts } from '../hooks/useProducts';
import { ProductCard } from './ProductCard';
import type { ProductFilters } from '../types';

interface ProductsGridProps {
  onProductClick?: (productId: string) => void;
}

export const ProductsGrid: React.FC<ProductsGridProps> = ({ onProductClick }) => {
  const [filters, setFilters] = useState<ProductFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  const { data: products, isLoading } = useProducts(filters);

  const handleSearch = (search: string) => {
    setFilters((prev) => ({ ...prev, search }));
  };

  const handleCategoryFilter = (category: ProductFilters['category']) => {
    setFilters((prev) => ({ ...prev, category }));
  };

  const handleSortChange = (sortBy: ProductFilters['sortBy']) => {
    setFilters((prev) => ({ ...prev, sortBy }));
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="h-10 w-64 bg-gray-200 rounded-lg animate-pulse" />
          <div className="h-10 w-32 bg-gray-200 rounded-lg animate-pulse" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-96 bg-gray-200 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          {/* Search */}
          <div className="flex-1 w-full sm:w-auto">
            <div className="relative">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="ابحث عن منتجات... | Search products..."
                className="w-full pr-10 pl-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
                onChange={(e) => handleSearch(e.target.value)}
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {/* Sort */}
            <select
              value={filters.sortBy || ''}
              onChange={(e) => handleSortChange(e.target.value as ProductFilters['sortBy'])}
              className="px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            >
              <option value="">ترتيب حسب</option>
              <option value="price_asc">السعر: من الأقل للأعلى</option>
              <option value="price_desc">السعر: من الأعلى للأقل</option>
              <option value="newest">الأحدث</option>
              <option value="rating">الأعلى تقييماً</option>
            </select>

            {/* Filter Toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 border-2 border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <Filter className="w-5 h-5" />
              <span>فلتر</span>
            </button>
          </div>
        </div>

        {/* Category Filters */}
        {showFilters && (
          <div className="flex flex-wrap gap-2 p-4 bg-gray-50 rounded-lg">
            <button
              onClick={() => handleCategoryFilter(undefined)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                !filters.category
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border-2 border-gray-200 hover:border-blue-400'
              }`}
            >
              الكل
            </button>
            <button
              onClick={() => handleCategoryFilter('seeds')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filters.category === 'seeds'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border-2 border-gray-200 hover:border-blue-400'
              }`}
            >
              بذور
            </button>
            <button
              onClick={() => handleCategoryFilter('fertilizers')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filters.category === 'fertilizers'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border-2 border-gray-200 hover:border-blue-400'
              }`}
            >
              أسمدة
            </button>
            <button
              onClick={() => handleCategoryFilter('pesticides')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filters.category === 'pesticides'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border-2 border-gray-200 hover:border-blue-400'
              }`}
            >
              مبيدات
            </button>
            <button
              onClick={() => handleCategoryFilter('equipment')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filters.category === 'equipment'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border-2 border-gray-200 hover:border-blue-400'
              }`}
            >
              معدات
            </button>
            <button
              onClick={() => handleCategoryFilter('tools')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filters.category === 'tools'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border-2 border-gray-200 hover:border-blue-400'
              }`}
            >
              أدوات
            </button>
          </div>
        )}
      </div>

      {/* Products Grid */}
      {!products || products.length === 0 ? (
        <div className="text-center py-16">
          <ShoppingBag className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">لا توجد منتجات</h3>
          <p className="text-gray-500">جرب البحث بكلمات مختلفة أو تغيير الفلاتر</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onClick={() => onProductClick?.(product.id)}
              />
            ))}
          </div>

          {/* Results Count */}
          <div className="text-center text-sm text-gray-500">
            عرض {products.length} منتج | Showing {products.length} products
          </div>
        </>
      )}
    </div>
  );
};

export default ProductsGrid;
