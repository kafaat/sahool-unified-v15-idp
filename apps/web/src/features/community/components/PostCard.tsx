/**
 * Post Card Component
 * مكون بطاقة المنشور
 */

'use client';

import React, { useState } from 'react';
import {
  ThumbsUp,
  MessageCircle,
  Share2,
  Bookmark,
  MoreVertical,
  CheckCircle,
  Award,
} from 'lucide-react';
import { useLikePost, useSavePost, useSharePost, useComments } from '../hooks/useCommunity';
import type { Post } from '../types';

interface PostCardProps {
  post: Post;
}

const postTypeColors = {
  question: 'bg-blue-100 text-blue-800',
  tip: 'bg-green-100 text-green-800',
  experience: 'bg-purple-100 text-purple-800',
  discussion: 'bg-yellow-100 text-yellow-800',
  update: 'bg-gray-100 text-gray-800',
};

const postTypeLabels = {
  question: 'سؤال',
  tip: 'نصيحة',
  experience: 'تجربة',
  discussion: 'نقاش',
  update: 'تحديث',
};

const badgeIcons = {
  farmer: '👨‍🌾',
  expert: '👨‍🏫',
  verified: <CheckCircle className="w-4 h-4 text-blue-500" />,
  moderator: <Award className="w-4 h-4 text-yellow-500" />,
};

export const PostCard: React.FC<PostCardProps> = ({ post }) => {
  const [showComments, setShowComments] = useState(false);

  const likeMutation = useLikePost();
  const saveMutation = useSavePost();
  const shareMutation = useSharePost();
  const { data: comments } = useComments(post.id);

  const handleLike = () => {
    likeMutation.mutate(post.id);
  };

  const handleSave = () => {
    saveMutation.mutate(post.id);
  };

  const handleShare = () => {
    shareMutation.mutate(post.id);
  };

  const formatDate = (date: string) => {
    const now = new Date();
    const postDate = new Date(date);
    const diffMs = now.getTime() - postDate.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `منذ ${diffMins} دقيقة`;
    if (diffHours < 24) return `منذ ${diffHours} ساعة`;
    if (diffDays < 7) return `منذ ${diffDays} يوم`;
    return postDate.toLocaleDateString('ar-SA');
  };

  return (
    <div
      className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
      data-testid="post-card"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            {/* Avatar */}
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center text-white font-bold text-lg" data-testid="post-avatar">
              {post.userName[0]}
            </div>

            {/* User Info */}
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-900" data-testid="post-author">{post.userNameAr}</span>
                {post.userBadge && <span data-testid="user-badge">{badgeIcons[post.userBadge]}</span>}
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-gray-600" data-testid="post-timestamp">{formatDate(post.createdAt)}</span>
                {post.location && (
                  <>
                    <span className="text-gray-400">•</span>
                    <span className="text-sm text-gray-600" data-testid="post-location">{post.location.cityAr}</span>
                  </>
                )}
              </div>
            </div>
          </div>

          <button
            className="text-gray-400 hover:text-gray-600"
            aria-label="خيارات المنشور"
          >
            <MoreVertical className="w-5 h-5" />
          </button>
        </div>

        {/* Type Badge */}
        <div className="mt-3">
          <span
            className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
              postTypeColors[post.type]
            }`}
            data-testid="post-type-badge"
          >
            {postTypeLabels[post.type]}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="text-xl font-semibold text-gray-900 mb-2" data-testid="post-title">{post.titleAr}</h3>
        <p className="text-gray-700 whitespace-pre-line" data-testid="post-content">{post.contentAr}</p>

        {/* Images */}
        {post.images && post.images.length > 0 && (
          <div className="mt-4 grid grid-cols-2 gap-2" data-testid="post-images">
            {post.images.slice(0, 4).map((image, index) => (
              <img
                key={index}
                src={image}
                alt={`Post image ${index + 1}`}
                className="w-full h-48 object-cover rounded-lg"
                data-testid={`post-image-${index}`}
              />
            ))}
          </div>
        )}

        {/* Tags */}
        {post.tagsAr && post.tagsAr.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2" data-testid="post-tags">
            {post.tagsAr.map((tag) => (
              <span
                key={`tag-${post.id}-${tag}`}
                className="text-sm text-green-600 hover:text-green-700 cursor-pointer"
                data-testid="post-tag"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-gray-100">
        {/* Stats */}
        <div className="flex items-center gap-4 text-sm text-gray-600 mb-3" data-testid="post-stats">
          <span data-testid="post-likes-count">{post.likes.toLocaleString('ar-SA')} إعجاب</span>
          <span data-testid="post-comments-count">{post.comments.toLocaleString('ar-SA')} تعليق</span>
          <span data-testid="post-views-count">{post.views.toLocaleString('ar-SA')} مشاهدة</span>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2" data-testid="post-actions">
          <button
            onClick={handleLike}
            disabled={likeMutation.isPending}
            aria-label={post.isLiked ? 'إلغاء الإعجاب' : 'إعجاب بالمنشور'}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 ${
              post.isLiked
                ? 'bg-green-50 text-green-600'
                : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
            }`}
            data-testid="post-like-button"
          >
            <ThumbsUp className={`w-5 h-5 ${post.isLiked ? 'fill-current' : ''}`} />
            <span>إعجاب</span>
          </button>

          <button
            onClick={() => setShowComments(!showComments)}
            aria-label={showComments ? 'إخفاء التعليقات' : 'عرض التعليقات'}
            aria-expanded={showComments}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-50 text-gray-700 rounded-lg font-medium hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            data-testid="post-comment-button"
          >
            <MessageCircle className="w-5 h-5" />
            <span>تعليق</span>
          </button>

          <button
            onClick={handleShare}
            disabled={shareMutation.isPending}
            aria-label="مشاركة المنشور"
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-50 text-gray-700 rounded-lg font-medium hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            data-testid="post-share-button"
          >
            <Share2 className="w-5 h-5" />
            <span>مشاركة</span>
          </button>

          <button
            onClick={handleSave}
            disabled={saveMutation.isPending}
            aria-label={post.isSaved ? 'إلغاء الحفظ' : 'حفظ المنشور'}
            className={`flex items-center justify-center p-2 rounded-lg transition-colors ${
              post.isSaved
                ? 'bg-green-50 text-green-600'
                : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
            }`}
            data-testid="post-save-button"
          >
            <Bookmark className={`w-5 h-5 ${post.isSaved ? 'fill-current' : ''}`} />
          </button>
        </div>
      </div>

      {/* Comments Section */}
      {showComments && comments && (
        <div className="p-4 bg-gray-50 border-t border-gray-200" data-testid="comments-section">
          <p className="text-sm text-gray-600 mb-3" data-testid="comments-count">{comments.length} تعليق</p>
          <div className="space-y-3">
            {comments.slice(0, 3).map((comment) => (
              <div key={comment.id} className="bg-white p-3 rounded-lg" data-testid="comment-card">
                <div className="flex items-start gap-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-sm font-bold" data-testid="comment-avatar">
                    {comment.userName[0]}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm text-gray-900" data-testid="comment-author">{comment.userNameAr}</p>
                    <p className="text-sm text-gray-700 mt-1" data-testid="comment-content">{comment.contentAr}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PostCard;
