'use client';

// Community Management Page
// صفحة إدارة المجتمع

import { useEffect, useState, useMemo } from 'react';
import Header from '@/components/layout/Header';
import DataTable from '@/components/ui/DataTable';
import { formatDate, cn } from '@/lib/utils';
import {
  MessageSquare,
  Search,
  RefreshCw,
  Eye,
  Trash2,
  Flag,
  ThumbsUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { logger } from '../../lib/logger';
import { MOCK_POSTS } from './community.mock';
import type { Post } from './community.mock';

export default function CommunityPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadPosts();
  }, []);

  async function loadPosts() {
    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      setPosts(MOCK_POSTS);
    } catch (error) {
      logger.error('Failed to load posts:', error);
    } finally {
      setIsLoading(false);
    }
  }

  const filteredPosts = useMemo(() => {
    return posts.filter((p) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !p.contentAr.toLowerCase().includes(query) &&
          !p.authorAr.toLowerCase().includes(query)
        ) {
          return false;
        }
      }
      if (categoryFilter && p.category !== categoryFilter) return false;
      if (statusFilter && p.status !== statusFilter) return false;
      return true;
    });
  }, [posts, searchQuery, categoryFilter, statusFilter]);

  const stats = useMemo(
    () => ({
      total: posts.length,
      active: posts.filter((p) => p.status === 'active').length,
      flagged: posts.filter((p) => p.status === 'flagged').length,
      pending: posts.filter((p) => p.status === 'pending').length,
    }),
    [posts]
  );

  const getStatusLabel = (status: Post['status']) => {
    const labels: Record<Post['status'], string> = {
      active: 'نشط',
      flagged: 'مُبلغ عنه',
      hidden: 'مخفي',
      pending: 'قيد المراجعة',
    };
    return labels[status];
  };

  const getStatusColor = (status: Post['status']) => {
    const colors: Record<Post['status'], string> = {
      active: 'bg-green-100 text-green-800',
      flagged: 'bg-red-100 text-red-800',
      hidden: 'bg-gray-100 text-gray-800',
      pending: 'bg-yellow-100 text-yellow-800',
    };
    return colors[status];
  };

  const columns = [
    {
      key: 'content',
      header: 'المنشور',
      render: (post: Post) => (
        <div className="max-w-md">
          <p className="font-medium text-gray-900 dark:text-gray-100 line-clamp-2">
            {post.contentAr}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            بواسطة: {post.authorAr} • {post.categoryAr}
          </p>
        </div>
      ),
    },
    {
      key: 'engagement',
      header: 'التفاعل',
      render: (post: Post) => (
        <div className="flex items-center gap-4 text-sm">
          <span className="flex items-center gap-1 text-gray-600 dark:text-gray-400">
            <ThumbsUp className="w-4 h-4" /> {post.likes}
          </span>
          <span className="flex items-center gap-1 text-gray-600 dark:text-gray-400">
            <MessageSquare className="w-4 h-4" /> {post.comments}
          </span>
        </div>
      ),
    },
    {
      key: 'reports',
      header: 'البلاغات',
      render: (post: Post) => (
        <span
          className={cn(
            'flex items-center gap-1',
            post.reports > 0 ? 'text-red-600 font-medium' : 'text-gray-400'
          )}
        >
          <Flag className="w-4 h-4" /> {post.reports}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'الحالة',
      render: (post: Post) => (
        <span
          className={cn('px-2 py-1 rounded-full text-xs font-medium', getStatusColor(post.status))}
        >
          {getStatusLabel(post.status)}
        </span>
      ),
    },
    {
      key: 'createdAt',
      header: 'التاريخ',
      render: (post: Post) => (
        <span className="text-gray-500 dark:text-gray-400 text-sm">
          {formatDate(post.createdAt)}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (post: Post) => (
        <div className="flex items-center gap-1">
          <button
            disabled
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            title="عرض (قريبًا)"
          >
            <Eye className="w-4 h-4 text-gray-500" />
          </button>
          {(post.status === 'flagged' || post.status === 'pending') && (
            <button
              disabled
              className="p-2 hover:bg-green-50 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              title="قبول (قريبًا)"
            >
              <CheckCircle className="w-4 h-4 text-green-500" />
            </button>
          )}
          {post.status !== 'hidden' && (
            <button
              disabled
              className="p-2 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              title="إخفاء (قريبًا)"
            >
              <XCircle className="w-4 h-4 text-red-500" />
            </button>
          )}
          <button
            disabled
            className="p-2 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            title="حذف (قريبًا)"
          >
            <Trash2 className="w-4 h-4 text-red-500" />
          </button>
        </div>
      ),
      className: 'w-40',
    },
  ];

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6">
      <Header title="إدارة المجتمع" subtitle={`${posts.length} منشور`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي المنشورات</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.active}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">نشط</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <Flag className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.flagged}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">مُبلغ عنه</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.pending}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">قيد المراجعة</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث في المنشورات..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الفئات</option>
            <option value="tips">نصائح</option>
            <option value="education">تعليم</option>
            <option value="questions">أسئلة</option>
            <option value="marketplace">سوق</option>
            <option value="other">أخرى</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="active">نشط</option>
            <option value="flagged">مُبلغ عنه</option>
            <option value="hidden">مخفي</option>
            <option value="pending">قيد المراجعة</option>
          </select>

          <button
            onClick={loadPosts}
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <RefreshCw
              className={cn(
                'w-5 h-5 text-gray-600 dark:text-gray-300',
                isLoading && 'animate-spin'
              )}
            />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6">
        {isLoading ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-8">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ))}
            </div>
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={filteredPosts}
            keyExtractor={(post) => post.id}
            emptyMessage="لا توجد منشورات مطابقة للبحث"
          />
        )}
      </div>
    </div>
  );
}
