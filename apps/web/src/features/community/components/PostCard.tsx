/**
 * Post Card Component
 * مكون بطاقة المنشور
 */

'use client';

import React, { useState } from 'react';
import Image from 'next/image';
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

const PostCardComponent: React.FC<PostCardProps> = ({ post }) => {
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
    const postDate = new Date(date);
    // Guard against undefined/invalid dates from backend or offline cache.
    if (Number.isNaN(postDate.getTime())) return '';
    const now = new Date();
    const diffMs = now.getTime() - postDate.getTime();
    const diffMins = Math.max(0, Math.floor(diffMs / 60000));
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `منذ ${diffMins} دقيقة`;
    if (diffHours < 24) return `منذ ${diffHours} ساعة`;
    if (diffDays < 7) return `منذ ${diffDays} يوم`;
    return postDate.toLocaleDateString('ar-SA');
  };

  // Resilient avatar initials; never throw on empty username.
  const avatarInitial = (post.userName ?? post.userNameAr ?? '?').charAt(0) || '?';

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            {/* Avatar */}
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center text-white font-bold text-lg">
              {avatarInitial}
            </div>

            {/* User Info */}
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-900">{post.userNameAr}</span>
                {post.userBadge && badgeIcons[post.userBadge]}
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-gray-600">{formatDate(post.createdAt)}</span>
                {post.location && (
                  <>
                    <span className="text-gray-400">•</span>
                    <span className="text-sm text-gray-600">{post.location.cityAr}</span>
                  </>
                )}
              </div>
            </div>
          </div>

          <button className="text-gray-400 hover:text-gray-600">
            <MoreVertical className="w-5 h-5" />
          </button>
        </div>

        {/* Type Badge */}
        <div className="mt-3">
          <span
            className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
              postTypeColors[post.type]
            }`}
          >
            {postTypeLabels[post.type]}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">{post.titleAr}</h3>
        <p className="text-gray-700 whitespace-pre-line">{post.contentAr}</p>

        {/* Images */}
        {post.images && post.images.length > 0 && (
          <div className="mt-4 grid grid-cols-2 gap-2">
            {post.images.slice(0, 4).map((image, index) => (
              <div key={image} className="relative w-full h-48">
                <Image
                  src={image}
                  alt={`Post image ${index + 1}`}
                  fill
                  sizes="(max-width: 768px) 50vw, 33vw"
                  className="object-cover rounded-lg"
                  loading="lazy"
                  placeholder="blur"
                  blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAb/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWEREiMxUf/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q=="
                />
              </div>
            ))}
          </div>
        )}

        {/* Tags */}
        {post.tagsAr && post.tagsAr.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {post.tagsAr.map((tag) => (
              <span
                key={tag}
                className="text-sm text-green-600 hover:text-green-700 cursor-pointer"
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
        <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
          <span>{post.likes.toLocaleString('ar-SA')} إعجاب</span>
          <span>{post.comments.toLocaleString('ar-SA')} تعليق</span>
          <span>{post.views.toLocaleString('ar-SA')} مشاهدة</span>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleLike}
            disabled={likeMutation.isPending}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              post.isLiked
                ? 'bg-green-50 text-green-600'
                : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
            }`}
          >
            <ThumbsUp className={`w-5 h-5 ${post.isLiked ? 'fill-current' : ''}`} />
            <span>إعجاب</span>
          </button>

          <button
            onClick={() => setShowComments(!showComments)}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-50 text-gray-700 rounded-lg font-medium hover:bg-gray-100 transition-colors"
          >
            <MessageCircle className="w-5 h-5" />
            <span>تعليق</span>
          </button>

          <button
            onClick={handleShare}
            disabled={shareMutation.isPending}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-50 text-gray-700 rounded-lg font-medium hover:bg-gray-100 transition-colors"
          >
            <Share2 className="w-5 h-5" />
            <span>مشاركة</span>
          </button>

          <button
            onClick={handleSave}
            disabled={saveMutation.isPending}
            className={`flex items-center justify-center p-2 rounded-lg transition-colors ${
              post.isSaved
                ? 'bg-green-50 text-green-600'
                : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Bookmark className={`w-5 h-5 ${post.isSaved ? 'fill-current' : ''}`} />
          </button>
        </div>
      </div>

      {/* Comments Section */}
      {showComments && comments && (
        <div className="p-4 bg-gray-50 border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-3">{comments.length} تعليق</p>
          <div className="space-y-3">
            {comments.slice(0, 3).map((comment) => (
              <div key={comment.id} className="bg-white p-3 rounded-lg">
                <div className="flex items-start gap-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-sm font-bold">
                    {(comment.userName ?? comment.userNameAr ?? '?').charAt(0) || '?'}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm text-gray-900">{comment.userNameAr}</p>
                    <p className="text-sm text-gray-700 mt-1">{comment.contentAr}</p>
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

export const PostCard = React.memo(PostCardComponent);
PostCard.displayName = 'PostCard';

export default PostCard;
