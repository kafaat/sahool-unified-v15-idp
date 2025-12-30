/**
 * Create Post Component
 * مكون إنشاء منشور
 */

'use client';

import React, { useState } from 'react';
import { X, Image as ImageIcon, Tag, MapPin } from 'lucide-react';
import { useCreatePost } from '../hooks/useCommunity';
import type { PostType } from '../types';

interface CreatePostProps {
  onClose: () => void;
}

export const CreatePost: React.FC<CreatePostProps> = ({ onClose }) => {
  const [type, setType] = useState<PostType>('discussion');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');

  const createMutation = useCreatePost();

  const postTypes: Array<{ value: PostType; label: string; labelAr: string }> = [
    { value: 'question', label: 'Question', labelAr: 'سؤال' },
    { value: 'tip', label: 'Tip', labelAr: 'نصيحة' },
    { value: 'experience', label: 'Experience', labelAr: 'تجربة' },
    { value: 'discussion', label: 'Discussion', labelAr: 'نقاش' },
    { value: 'update', label: 'Update', labelAr: 'تحديث' },
  ];

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setTags(tags.filter((t) => t !== tag));
  };

  const handleSubmit = async () => {
    if (!title.trim() || !content.trim()) return;

    try {
      await createMutation.mutateAsync({
        type,
        titleAr: title,
        contentAr: content,
        tagsAr: tags,
        status: 'active',
      });
      onClose();
    } catch (error) {
      console.error('Failed to create post:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" data-testid="create-post-modal">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" dir="rtl" role="dialog">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900" data-testid="modal-title">إنشاء منشور جديد</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="close"
            data-testid="close-modal-button"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Post Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              نوع المنشور
            </label>
            <div className="grid grid-cols-5 gap-2" data-testid="post-type-selector">
              {postTypes.map((postType) => (
                <button
                  key={postType.value}
                  onClick={() => setType(postType.value)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    type === postType.value
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  data-testid={`post-type-${postType.value}`}
                >
                  {postType.labelAr}
                </button>
              ))}
            </div>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              العنوان
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="أدخل عنوان المنشور..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              data-testid="post-title-input"
            />
          </div>

          {/* Content */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              المحتوى
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="شارك سؤالك أو تجربتك أو نصيحتك..."
              rows={8}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
              data-testid="post-content-input"
            />
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              الوسوم
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                placeholder="أضف وسماً..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                data-testid="tag-input"
              />
              <button
                onClick={handleAddTag}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                data-testid="add-tag-button"
              >
                <Tag className="w-5 h-5" />
              </button>
            </div>
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2" data-testid="tags-list">
                {tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
                    data-testid="tag-item"
                  >
                    #{tag}
                    <button
                      onClick={() => handleRemoveTag(tag)}
                      className="text-green-600 hover:text-green-800"
                      data-testid="remove-tag-button"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-4 pt-4 border-t border-gray-200">
            <button className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors">
              <ImageIcon className="w-5 h-5" />
              <span>إضافة صور</span>
            </button>
            <button className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors">
              <MapPin className="w-5 h-5" />
              <span>إضافة موقع</span>
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 p-4 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-6 py-2 text-gray-700 hover:text-gray-900 font-medium transition-colors"
            data-testid="cancel-button"
          >
            إلغاء
          </button>
          <button
            onClick={handleSubmit}
            disabled={!title.trim() || !content.trim() || createMutation.isPending}
            className="px-6 py-2 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            data-testid="submit-post-button"
          >
            {createMutation.isPending ? 'جاري النشر...' : 'نشر'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreatePost;
