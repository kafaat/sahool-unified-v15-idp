/**
 * Community Feature - API Layer
 * طبقة API لميزة المجتمع الزراعي
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  Post,
  Comment,
  Group,
  GroupMember,
  ChatMessage,
  Expert,
  ExpertQuestion,
  CommunityFilters,
  GroupFilters,
} from './types';
import { COMMUNITY_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_POSTS_FAILED: {
    en: 'Failed to fetch posts. Using cached data.',
    ar: 'فشل في جلب المنشورات. استخدام البيانات المخزنة.',
  },
  FETCH_GROUPS_FAILED: {
    en: 'Failed to fetch groups. Using cached data.',
    ar: 'فشل في جلب المجموعات. استخدام البيانات المخزنة.',
  },
  CREATE_POST_FAILED: {
    en: 'Failed to create post. Please try again.',
    ar: 'فشل في إنشاء المنشور. الرجاء المحاولة مرة أخرى.',
  },
  UPDATE_POST_FAILED: {
    en: 'Failed to update post. Please try again.',
    ar: 'فشل في تحديث المنشور. الرجاء المحاولة مرة أخرى.',
  },
  DELETE_POST_FAILED: {
    en: 'Failed to delete post. Please try again.',
    ar: 'فشل في حذف المنشور. الرجاء المحاولة مرة أخرى.',
  },
  CREATE_COMMENT_FAILED: {
    en: 'Failed to add comment. Please try again.',
    ar: 'فشل في إضافة التعليق. الرجاء المحاولة مرة أخرى.',
  },
  JOIN_GROUP_FAILED: {
    en: 'Failed to join group. Please try again.',
    ar: 'فشل في الانضمام للمجموعة. الرجاء المحاولة مرة أخرى.',
  },
  LEAVE_GROUP_FAILED: {
    en: 'Failed to leave group. Please try again.',
    ar: 'فشل في مغادرة المجموعة. الرجاء المحاولة مرة أخرى.',
  },
  SEND_MESSAGE_FAILED: {
    en: 'Failed to send message. Please try again.',
    ar: 'فشل في إرسال الرسالة. الرجاء المحاولة مرة أخرى.',
  },
  ASK_EXPERT_FAILED: {
    en: 'Failed to submit question. Please try again.',
    ar: 'فشل في إرسال السؤال. الرجاء المحاولة مرة أخرى.',
  },
  NOT_FOUND: {
    en: 'Resource not found.',
    ar: 'المورد غير موجود.',
  },
};

// API Functions
export const communityApi = {
  /**
   * Posts API
   * ========================================================================
   */

  /**
   * Get all posts with filters
   */
  getPosts: async (filters?: CommunityFilters): Promise<Post[]> => {
    return safeFetch(COMMUNITY_ENDPOINTS.POSTS, async () => {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.tags?.length) params.set('tags', filters.tags.join(','));
      if (filters?.location) params.set('location', filters.location);
      if (filters?.sortBy) params.set('sort_by', filters.sortBy);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${COMMUNITY_ENDPOINTS.POSTS}?${params.toString()}`);
      const posts = response.data.data || response.data;
      if (Array.isArray(posts)) return posts;
      return [];
    });
  },

  /**
   * Get trending posts
   */
  getTrendingPosts: async (): Promise<Post[]> => {
    return safeFetch(COMMUNITY_ENDPOINTS.TRENDING, async () => {
      const response = await api.get(COMMUNITY_ENDPOINTS.TRENDING);
      const posts = response.data.data || response.data;
      if (Array.isArray(posts)) return posts;
      return [];
    });
  },

  /**
   * Get user's saved posts
   */
  getSavedPosts: async (): Promise<Post[]> => {
    return safeFetch(COMMUNITY_ENDPOINTS.SAVED, async () => {
      const response = await api.get(COMMUNITY_ENDPOINTS.SAVED);
      const posts = response.data.data || response.data;
      if (Array.isArray(posts)) return posts;
      return [];
    });
  },

  /**
   * Get user's own posts
   */
  getMyPosts: async (): Promise<Post[]> => {
    return safeFetch(COMMUNITY_ENDPOINTS.MY_POSTS, async () => {
      const response = await api.get(COMMUNITY_ENDPOINTS.MY_POSTS);
      const posts = response.data.data || response.data;
      if (Array.isArray(posts)) return posts;
      return [];
    });
  },

  /**
   * Get post by ID
   */
  getPostById: async (id: string): Promise<Post> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.POST_GET, { postId: id }), async () => {
      const response = await api.get(buildUrl(COMMUNITY_ENDPOINTS.POST_GET, { postId: id }));
      return response.data.data || response.data;
    });
  },

  /**
   * Create new post
   */
  createPost: async (data: Partial<Post>): Promise<Post> => {
    return safeFetch(COMMUNITY_ENDPOINTS.POSTS, async () => {
      const response = await api.post(COMMUNITY_ENDPOINTS.POSTS, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Update post
   */
  updatePost: async (id: string, data: Partial<Post>): Promise<Post> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.POST_UPDATE, { postId: id }), async () => {
      const response = await api.put(buildUrl(COMMUNITY_ENDPOINTS.POST_UPDATE, { postId: id }), data);
      return response.data.data || response.data;
    });
  },

  /**
   * Delete post
   */
  deletePost: async (id: string): Promise<void> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.POST_DELETE, { postId: id }), async () => {
      await api.delete(buildUrl(COMMUNITY_ENDPOINTS.POST_DELETE, { postId: id }));
    });
  },

  /**
   * Like/unlike a post
   */
  likePost: async (postId: string): Promise<void> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.POST_LIKE, { postId }), async () => {
      await api.post(buildUrl(COMMUNITY_ENDPOINTS.POST_LIKE, { postId }));
    });
  },

  /**
   * Save/unsave a post
   */
  savePost: async (postId: string): Promise<void> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.POST_SAVE, { postId }), async () => {
      await api.post(buildUrl(COMMUNITY_ENDPOINTS.POST_SAVE, { postId }));
    });
  },

  /**
   * Share a post
   */
  sharePost: async (postId: string): Promise<void> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.POST_SHARE, { postId }), async () => {
      await api.post(buildUrl(COMMUNITY_ENDPOINTS.POST_SHARE, { postId }));
    });
  },

  /**
   * Comments API
   * ========================================================================
   */

  /**
   * Get post comments
   */
  getComments: async (postId: string): Promise<Comment[]> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.POST_COMMENTS, { postId }), async () => {
      const response = await api.get(buildUrl(COMMUNITY_ENDPOINTS.POST_COMMENTS, { postId }));
      const comments = response.data.data || response.data;
      if (Array.isArray(comments)) return comments;
      return [];
    });
  },

  /**
   * Add a comment
   */
  addComment: async (postId: string, content: string, parentId?: string): Promise<Comment> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.POST_COMMENTS, { postId }), async () => {
      const response = await api.post(buildUrl(COMMUNITY_ENDPOINTS.POST_COMMENTS, { postId }), {
        content,
        parentId,
      });
      return response.data.data || response.data;
    });
  },

  /**
   * Like a comment
   */
  likeComment: async (postId: string, commentId: string): Promise<void> => {
    return safeFetch(`${buildUrl(COMMUNITY_ENDPOINTS.POST_COMMENTS, { postId })}/${commentId}/like`, async () => {
      await api.post(`${buildUrl(COMMUNITY_ENDPOINTS.POST_COMMENTS, { postId })}/${commentId}/like`);
    });
  },

  /**
   * Groups API
   * ========================================================================
   */

  /**
   * Get all groups with filters
   */
  getGroups: async (filters?: GroupFilters): Promise<Group[]> => {
    return safeFetch(COMMUNITY_ENDPOINTS.GROUPS, async () => {
      const params = new URLSearchParams();
      if (filters?.category) params.set('category', filters.category);
      if (filters?.privacy) params.set('privacy', filters.privacy);
      if (filters?.joined !== undefined) params.set('joined', String(filters.joined));
      if (filters?.sortBy) params.set('sort_by', filters.sortBy);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${COMMUNITY_ENDPOINTS.GROUPS}?${params.toString()}`);
      const groups = response.data.data || response.data;
      if (Array.isArray(groups)) return groups;
      return [];
    });
  },

  /**
   * Get group by ID
   */
  getGroupById: async (id: string): Promise<Group> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.GROUP_GET, { groupId: id }), async () => {
      const response = await api.get(buildUrl(COMMUNITY_ENDPOINTS.GROUP_GET, { groupId: id }));
      return response.data.data || response.data;
    });
  },

  /**
   * Get user's joined groups
   */
  getMyGroups: async (): Promise<Group[]> => {
    return safeFetch(COMMUNITY_ENDPOINTS.MY_GROUPS, async () => {
      const response = await api.get(COMMUNITY_ENDPOINTS.MY_GROUPS);
      const groups = response.data.data || response.data;
      if (Array.isArray(groups)) return groups;
      return [];
    });
  },

  /**
   * Create a group
   */
  createGroup: async (data: Partial<Group>): Promise<Group> => {
    return safeFetch(COMMUNITY_ENDPOINTS.GROUPS, async () => {
      const response = await api.post(COMMUNITY_ENDPOINTS.GROUPS, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Join a group
   */
  joinGroup: async (groupId: string): Promise<void> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.GROUP_JOIN, { groupId }), async () => {
      await api.post(buildUrl(COMMUNITY_ENDPOINTS.GROUP_JOIN, { groupId }));
    });
  },

  /**
   * Leave a group
   */
  leaveGroup: async (groupId: string): Promise<void> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.GROUP_LEAVE, { groupId }), async () => {
      await api.post(buildUrl(COMMUNITY_ENDPOINTS.GROUP_LEAVE, { groupId }));
    });
  },

  /**
   * Get group members
   */
  getGroupMembers: async (groupId: string): Promise<GroupMember[]> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.GROUP_MEMBERS, { groupId }), async () => {
      const response = await api.get(buildUrl(COMMUNITY_ENDPOINTS.GROUP_MEMBERS, { groupId }));
      const members = response.data.data || response.data;
      if (Array.isArray(members)) return members;
      return [];
    });
  },

  /**
   * Group Messages API
   * ========================================================================
   */

  /**
   * Get group chat messages
   */
  getGroupMessages: async (groupId: string): Promise<ChatMessage[]> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.GROUP_MESSAGES, { groupId }), async () => {
      const response = await api.get(buildUrl(COMMUNITY_ENDPOINTS.GROUP_MESSAGES, { groupId }));
      const messages = response.data.data || response.data;
      if (Array.isArray(messages)) return messages;
      return [];
    });
  },

  /**
   * Send a message
   */
  sendMessage: async (groupId: string, content: string, type: 'text' | 'image' | 'file' | 'voice' = 'text'): Promise<ChatMessage> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.GROUP_MESSAGES, { groupId }), async () => {
      const response = await api.post(buildUrl(COMMUNITY_ENDPOINTS.GROUP_MESSAGES, { groupId }), {
        content,
        type,
      });
      return response.data.data || response.data;
    });
  },

  /**
   * Experts API
   * ========================================================================
   */

  /**
   * Get all experts
   */
  getExperts: async (): Promise<Expert[]> => {
    return safeFetch(COMMUNITY_ENDPOINTS.EXPERTS, async () => {
      const response = await api.get(COMMUNITY_ENDPOINTS.EXPERTS);
      const experts = response.data.data || response.data;
      if (Array.isArray(experts)) return experts;
      return [];
    });
  },

  /**
   * Ask an expert
   */
  askExpert: async (data: Partial<ExpertQuestion>): Promise<ExpertQuestion> => {
    return safeFetch(COMMUNITY_ENDPOINTS.EXPERT_QUESTIONS, async () => {
      const response = await api.post(COMMUNITY_ENDPOINTS.EXPERT_QUESTIONS, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Get expert questions
   */
  getExpertQuestions: async (): Promise<ExpertQuestion[]> => {
    return safeFetch(COMMUNITY_ENDPOINTS.EXPERT_QUESTIONS, async () => {
      const response = await api.get(COMMUNITY_ENDPOINTS.EXPERT_QUESTIONS);
      const questions = response.data.data || response.data;
      if (Array.isArray(questions)) return questions;
      return [];
    });
  },

  /**
   * Rate expert answer
   */
  rateExpertAnswer: async (questionId: string, helpful: boolean): Promise<void> => {
    return safeFetch(buildUrl(COMMUNITY_ENDPOINTS.EXPERT_RATE, { questionId }), async () => {
      await api.post(buildUrl(COMMUNITY_ENDPOINTS.EXPERT_RATE, { questionId }), { helpful });
    });
  },
};
