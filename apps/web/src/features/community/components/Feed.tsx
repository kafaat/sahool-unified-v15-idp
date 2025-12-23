/**
 * Community Feed Component
 * مكون موجز المجتمع
 */

'use client';

import React, { useState } from 'react';
import { Search, Filter, TrendingUp } from 'lucide-react';
import { usePosts } from '../hooks/useCommunity';
import { PostCard } from './PostCard';
import { CreatePost } from './CreatePost';
import type { CommunityFilters, PostType } from '../types';

export const Feed: React.FC = () => {
  const [filters, setFilters] = useState<CommunityFilters>({
    sortBy: 'recent',
  });
  const [showCreatePost, setShowCreatePost] = useState(false);

  const { data: posts, isLoading } = usePosts(filters);

  const postTypes: Array<{ value: PostType | 'all'; label: string; labelAr: string }> = [
    { value: 'all', label: 'All', labelAr: 'الكل' },
    { value: 'question', label: 'Questions', labelAr: 'أسئلة' },
    { value: 'tip', label: 'Tips', labelAr: 'نصائح' },
    { value: 'experience', label: 'Experience', labelAr: 'تجارب' },
    { value: 'discussion', label: 'Discussion', labelAr: 'نقاشات' },
  ];

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">مجتمع المزارعين</h1>
          <p className="text-sm text-gray-600 mt-1">Farmer Community</p>
        </div>

        {/* Create Post Button */}
        <button
          onClick={() => setShowCreatePost(true)}
          className="w-full mb-6 p-4 bg-white border-2 border-dashed border-gray-300 rounded-xl text-gray-600 hover:border-green-500 hover:text-green-600 transition-colors"
        >
          <span className="font-medium">انشر سؤالاً أو تجربة أو نصيحة...</span>
        </button>

        {/* Filters */}
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-6">
          <div className="flex items-center gap-4 flex-wrap">
            {/* Search */}
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="ابحث في المجتمع..."
                  value={filters.search || ''}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                  className="w-full pr-10 pl-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Type Filter */}
            <select
              value={filters.type || 'all'}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  type: e.target.value === 'all' ? undefined : (e.target.value as PostType),
                })
              }
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              {postTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.labelAr}
                </option>
              ))}
            </select>

            {/* Sort */}
            <select
              value={filters.sortBy || 'recent'}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  sortBy: e.target.value as CommunityFilters['sortBy'],
                })
              }
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="recent">الأحدث</option>
              <option value="popular">الأكثر شعبية</option>
              <option value="trending">الرائج</option>
            </select>
          </div>
        </div>

        {/* Posts */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
          </div>
        ) : posts && posts.length > 0 ? (
          <div className="space-y-4">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
        ) : (
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 text-center">
            <p className="text-gray-600">لا توجد منشورات</p>
            <p className="text-sm text-gray-500 mt-1">No posts found</p>
          </div>
        )}

        {/* Create Post Modal */}
        {showCreatePost && <CreatePost onClose={() => setShowCreatePost(false)} />}
      </div>
    </div>
  );
};

export default Feed;
