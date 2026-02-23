/**
 * Community Feature - API Layer
 * طبقة API لميزة المجتمع الزراعي
 */

import { type AxiosError } from "axios";
import { createApiClient, logger } from "@/lib/api/factory";
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
} from "./types";
import { COMMUNITY_ENDPOINTS, buildUrl } from "@sahool/shared-types/contracts";

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: "Network error. Using offline data.",
    ar: "خطأ في الاتصال. استخدام البيانات المحفوظة.",
  },
  FETCH_POSTS_FAILED: {
    en: "Failed to fetch posts. Using cached data.",
    ar: "فشل في جلب المنشورات. استخدام البيانات المخزنة.",
  },
  FETCH_GROUPS_FAILED: {
    en: "Failed to fetch groups. Using cached data.",
    ar: "فشل في جلب المجموعات. استخدام البيانات المخزنة.",
  },
  CREATE_POST_FAILED: {
    en: "Failed to create post. Please try again.",
    ar: "فشل في إنشاء المنشور. الرجاء المحاولة مرة أخرى.",
  },
  UPDATE_POST_FAILED: {
    en: "Failed to update post. Please try again.",
    ar: "فشل في تحديث المنشور. الرجاء المحاولة مرة أخرى.",
  },
  DELETE_POST_FAILED: {
    en: "Failed to delete post. Please try again.",
    ar: "فشل في حذف المنشور. الرجاء المحاولة مرة أخرى.",
  },
  CREATE_COMMENT_FAILED: {
    en: "Failed to add comment. Please try again.",
    ar: "فشل في إضافة التعليق. الرجاء المحاولة مرة أخرى.",
  },
  JOIN_GROUP_FAILED: {
    en: "Failed to join group. Please try again.",
    ar: "فشل في الانضمام للمجموعة. الرجاء المحاولة مرة أخرى.",
  },
  LEAVE_GROUP_FAILED: {
    en: "Failed to leave group. Please try again.",
    ar: "فشل في مغادرة المجموعة. الرجاء المحاولة مرة أخرى.",
  },
  SEND_MESSAGE_FAILED: {
    en: "Failed to send message. Please try again.",
    ar: "فشل في إرسال الرسالة. الرجاء المحاولة مرة أخرى.",
  },
  ASK_EXPERT_FAILED: {
    en: "Failed to submit question. Please try again.",
    ar: "فشل في إرسال السؤال. الرجاء المحاولة مرة أخرى.",
  },
  NOT_FOUND: {
    en: "Resource not found.",
    ar: "المورد غير موجود.",
  },
};

// Mock data helpers - dynamic import for dead-code elimination in production builds.
// In production, mock modules are never bundled because the import() is unreachable.
async function getMockPosts() {
  if (process.env.NODE_ENV !== "production") {
    const { MOCK_POSTS } = await import("./api.mock");
    return MOCK_POSTS;
  }
  return [];
}

async function getMockGroups() {
  if (process.env.NODE_ENV !== "production") {
    const { MOCK_GROUPS } = await import("./api.mock");
    return MOCK_GROUPS;
  }
  return [];
}

async function getMockExperts() {
  if (process.env.NODE_ENV !== "production") {
    const { MOCK_EXPERTS } = await import("./api.mock");
    return MOCK_EXPERTS;
  }
  return [];
}

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
    try {
      const params = new URLSearchParams();
      if (filters?.type) params.set("type", filters.type);
      if (filters?.status) params.set("status", filters.status);
      if (filters?.tags?.length) params.set("tags", filters.tags.join(","));
      if (filters?.location) params.set("location", filters.location);
      if (filters?.sortBy) params.set("sort_by", filters.sortBy);
      if (filters?.search) params.set("search", filters.search);

      const response = await api.get(
        `${COMMUNITY_ENDPOINTS.POSTS}?${params.toString()}`,
      );

      // Handle different response formats
      const posts = response.data.data || response.data;

      if (Array.isArray(posts)) {
        return posts;
      }

      logger.warn("API returned unexpected format, using mock data");
      return getMockPosts();
    } catch (error) {
      logger.warn("Failed to fetch posts from API, using mock data:", error);
      return getMockPosts();
    }
  },

  /**
   * Get trending posts
   */
  getTrendingPosts: async (): Promise<Post[]> => {
    try {
      const response = await api.get(COMMUNITY_ENDPOINTS.TRENDING);
      const posts = response.data.data || response.data;

      if (Array.isArray(posts)) {
        return posts;
      }

      logger.warn("API returned unexpected format, using mock data");
      return (await getMockPosts()).slice(0, 2);
    } catch (error) {
      logger.warn(
        "Failed to fetch trending posts from API, using mock data:",
        error,
      );
      return (await getMockPosts()).slice(0, 2);
    }
  },

  /**
   * Get user's saved posts
   */
  getSavedPosts: async (): Promise<Post[]> => {
    try {
      const response = await api.get(COMMUNITY_ENDPOINTS.SAVED);
      const posts = response.data.data || response.data;

      if (Array.isArray(posts)) {
        return posts;
      }

      logger.warn("API returned unexpected format, using mock data");
      return (await getMockPosts()).filter((p) => p.isSaved);
    } catch (error) {
      logger.warn(
        "Failed to fetch saved posts from API, using mock data:",
        error,
      );
      return (await getMockPosts()).filter((p) => p.isSaved);
    }
  },

  /**
   * Get user's own posts
   */
  getMyPosts: async (): Promise<Post[]> => {
    try {
      const response = await api.get(COMMUNITY_ENDPOINTS.MY_POSTS);
      const posts = response.data.data || response.data;

      if (Array.isArray(posts)) {
        return posts;
      }

      logger.warn("API returned unexpected format, using mock data");
      return (await getMockPosts()).slice(0, 1);
    } catch (error) {
      logger.warn("Failed to fetch my posts from API, using mock data:", error);
      return (await getMockPosts()).slice(0, 1);
    }
  },

  /**
   * Get post by ID
   */
  getPostById: async (id: string): Promise<Post> => {
    try {
      const response = await api.get(buildUrl(COMMUNITY_ENDPOINTS.POST_GET, { postId: id }));
      const post = response.data.data || response.data;
      return post;
    } catch (error) {
      logger.warn(
        `Failed to fetch post ${id} from API, using mock data:`,
        error,
      );

      // Fallback to mock data
      const mockPosts = await getMockPosts();
      const mockPost = mockPosts.find((p) => p.id === id);
      if (mockPost) {
        return mockPost;
      }

      throw new Error(ERROR_MESSAGES.NOT_FOUND.en);
    }
  },

  /**
   * Create new post
   */
  createPost: async (data: Partial<Post>): Promise<Post> => {
    try {
      const response = await api.post(COMMUNITY_ENDPOINTS.POSTS, data);
      const post = response.data.data || response.data;
      return post;
    } catch (error) {
      logger.error("Failed to create post:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.CREATE_POST_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.CREATE_POST_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Update post
   */
  updatePost: async (id: string, data: Partial<Post>): Promise<Post> => {
    try {
      const response = await api.put(buildUrl(COMMUNITY_ENDPOINTS.POST_UPDATE, { postId: id }), data);
      const post = response.data.data || response.data;
      return post;
    } catch (error) {
      logger.error(`Failed to update post ${id}:`, error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.UPDATE_POST_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.UPDATE_POST_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Delete post
   */
  deletePost: async (id: string): Promise<void> => {
    try {
      await api.delete(buildUrl(COMMUNITY_ENDPOINTS.POST_DELETE, { postId: id }));
    } catch (error) {
      logger.error(`Failed to delete post ${id}:`, error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.DELETE_POST_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.DELETE_POST_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Like/unlike a post
   */
  likePost: async (postId: string): Promise<void> => {
    try {
      await api.post(buildUrl(COMMUNITY_ENDPOINTS.POST_LIKE, { postId }));
    } catch (error) {
      logger.error(`Failed to like post ${postId}:`, error);
      throw error;
    }
  },

  /**
   * Save/unsave a post
   */
  savePost: async (postId: string): Promise<void> => {
    try {
      await api.post(buildUrl(COMMUNITY_ENDPOINTS.POST_SAVE, { postId }));
    } catch (error) {
      logger.error(`Failed to save post ${postId}:`, error);
      throw error;
    }
  },

  /**
   * Share a post
   */
  sharePost: async (postId: string): Promise<void> => {
    try {
      await api.post(buildUrl(COMMUNITY_ENDPOINTS.POST_SHARE, { postId }));
    } catch (error) {
      logger.error(`Failed to share post ${postId}:`, error);
      throw error;
    }
  },

  /**
   * Comments API
   * ========================================================================
   */

  /**
   * Get post comments
   */
  getComments: async (postId: string): Promise<Comment[]> => {
    try {
      const response = await api.get(
        buildUrl(COMMUNITY_ENDPOINTS.POST_COMMENTS, { postId }),
      );
      const comments = response.data.data || response.data;

      if (Array.isArray(comments)) {
        return comments;
      }

      logger.warn("API returned unexpected format, returning empty comments");
      return [];
    } catch (error) {
      logger.warn(
        `Failed to fetch comments for post ${postId} from API:`,
        error,
      );
      return [];
    }
  },

  /**
   * Add a comment
   */
  addComment: async (
    postId: string,
    content: string,
    parentId?: string,
  ): Promise<Comment> => {
    try {
      const response = await api.post(
        buildUrl(COMMUNITY_ENDPOINTS.POST_COMMENTS, { postId }),
        {
          content,
          parentId,
        },
      );
      const comment = response.data.data || response.data;
      return comment;
    } catch (error) {
      logger.error(`Failed to add comment to post ${postId}:`, error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.CREATE_COMMENT_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.CREATE_COMMENT_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Like a comment
   */
  likeComment: async (postId: string, commentId: string): Promise<void> => {
    try {
      await api.post(
        `${buildUrl(COMMUNITY_ENDPOINTS.POST_COMMENTS, { postId })}/${commentId}/like`,
      );
    } catch (error) {
      logger.error(`Failed to like comment ${commentId}:`, error);
      throw error;
    }
  },

  /**
   * Groups API
   * ========================================================================
   */

  /**
   * Get all groups with filters
   */
  getGroups: async (filters?: GroupFilters): Promise<Group[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.category) params.set("category", filters.category);
      if (filters?.privacy) params.set("privacy", filters.privacy);
      if (filters?.joined !== undefined)
        params.set("joined", String(filters.joined));
      if (filters?.sortBy) params.set("sort_by", filters.sortBy);
      if (filters?.search) params.set("search", filters.search);

      const response = await api.get(
        `${COMMUNITY_ENDPOINTS.GROUPS}?${params.toString()}`,
      );

      // Handle different response formats
      const groups = response.data.data || response.data;

      if (Array.isArray(groups)) {
        return groups;
      }

      logger.warn("API returned unexpected format, using mock data");
      return getMockGroups();
    } catch (error) {
      logger.warn("Failed to fetch groups from API, using mock data:", error);
      return getMockGroups();
    }
  },

  /**
   * Get group by ID
   */
  getGroupById: async (id: string): Promise<Group> => {
    try {
      const response = await api.get(buildUrl(COMMUNITY_ENDPOINTS.GROUP_GET, { groupId: id }));
      const group = response.data.data || response.data;
      return group;
    } catch (error) {
      logger.warn(
        `Failed to fetch group ${id} from API, using mock data:`,
        error,
      );

      // Fallback to mock data
      const mockGroups = await getMockGroups();
      const mockGroup = mockGroups.find((g) => g.id === id);
      if (mockGroup) {
        return mockGroup;
      }

      throw new Error(ERROR_MESSAGES.NOT_FOUND.en);
    }
  },

  /**
   * Get user's joined groups
   */
  getMyGroups: async (): Promise<Group[]> => {
    try {
      const response = await api.get(COMMUNITY_ENDPOINTS.MY_GROUPS);
      const groups = response.data.data || response.data;

      if (Array.isArray(groups)) {
        return groups;
      }

      logger.warn("API returned unexpected format, using mock data");
      return (await getMockGroups()).filter((g) => g.isJoined);
    } catch (error) {
      logger.warn(
        "Failed to fetch my groups from API, using mock data:",
        error,
      );
      return (await getMockGroups()).filter((g) => g.isJoined);
    }
  },

  /**
   * Create a group
   */
  createGroup: async (data: Partial<Group>): Promise<Group> => {
    try {
      const response = await api.post(COMMUNITY_ENDPOINTS.GROUPS, data);
      const group = response.data.data || response.data;
      return group;
    } catch (error) {
      logger.error("Failed to create group:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message || "Failed to create group";
      const errorMessageAr =
        axiosError.response?.data?.message_ar || "فشل في إنشاء المجموعة";

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Join a group
   */
  joinGroup: async (groupId: string): Promise<void> => {
    try {
      await api.post(buildUrl(COMMUNITY_ENDPOINTS.GROUP_JOIN, { groupId }));
    } catch (error) {
      logger.error(`Failed to join group ${groupId}:`, error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.JOIN_GROUP_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.JOIN_GROUP_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Leave a group
   */
  leaveGroup: async (groupId: string): Promise<void> => {
    try {
      await api.post(buildUrl(COMMUNITY_ENDPOINTS.GROUP_LEAVE, { groupId }));
    } catch (error) {
      logger.error(`Failed to leave group ${groupId}:`, error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.LEAVE_GROUP_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.LEAVE_GROUP_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Get group members
   */
  getGroupMembers: async (groupId: string): Promise<GroupMember[]> => {
    try {
      const response = await api.get(
        buildUrl(COMMUNITY_ENDPOINTS.GROUP_MEMBERS, { groupId }),
      );
      const members = response.data.data || response.data;

      if (Array.isArray(members)) {
        return members;
      }

      logger.warn("API returned unexpected format, returning empty members");
      return [];
    } catch (error) {
      logger.warn(
        `Failed to fetch members for group ${groupId} from API:`,
        error,
      );
      return [];
    }
  },

  /**
   * Group Messages API
   * ========================================================================
   */

  /**
   * Get group chat messages
   */
  getGroupMessages: async (groupId: string): Promise<ChatMessage[]> => {
    try {
      const response = await api.get(
        buildUrl(COMMUNITY_ENDPOINTS.GROUP_MESSAGES, { groupId }),
      );
      const messages = response.data.data || response.data;

      if (Array.isArray(messages)) {
        return messages;
      }

      logger.warn("API returned unexpected format, returning empty messages");
      return [];
    } catch (error) {
      logger.warn(
        `Failed to fetch messages for group ${groupId} from API:`,
        error,
      );
      return [];
    }
  },

  /**
   * Send a message
   */
  sendMessage: async (
    groupId: string,
    content: string,
    type: "text" | "image" | "file" | "voice" = "text",
  ): Promise<ChatMessage> => {
    try {
      const response = await api.post(
        buildUrl(COMMUNITY_ENDPOINTS.GROUP_MESSAGES, { groupId }),
        {
          content,
          type,
        },
      );
      const message = response.data.data || response.data;
      return message;
    } catch (error) {
      logger.error(`Failed to send message to group ${groupId}:`, error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.SEND_MESSAGE_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.SEND_MESSAGE_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Experts API
   * ========================================================================
   */

  /**
   * Get all experts
   */
  getExperts: async (): Promise<Expert[]> => {
    try {
      const response = await api.get(COMMUNITY_ENDPOINTS.EXPERTS);
      const experts = response.data.data || response.data;

      if (Array.isArray(experts)) {
        return experts;
      }

      logger.warn("API returned unexpected format, using mock data");
      return getMockExperts();
    } catch (error) {
      logger.warn("Failed to fetch experts from API, using mock data:", error);
      return getMockExperts();
    }
  },

  /**
   * Ask an expert
   */
  askExpert: async (data: Partial<ExpertQuestion>): Promise<ExpertQuestion> => {
    try {
      const response = await api.post(
        COMMUNITY_ENDPOINTS.EXPERT_QUESTIONS,
        data,
      );
      const question = response.data.data || response.data;
      return question;
    } catch (error) {
      logger.error("Failed to submit expert question:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.ASK_EXPERT_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.ASK_EXPERT_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Get expert questions
   */
  getExpertQuestions: async (): Promise<ExpertQuestion[]> => {
    try {
      const response = await api.get(COMMUNITY_ENDPOINTS.EXPERT_QUESTIONS);
      const questions = response.data.data || response.data;

      if (Array.isArray(questions)) {
        return questions;
      }

      logger.warn("API returned unexpected format, returning empty questions");
      return [];
    } catch (error) {
      logger.warn("Failed to fetch expert questions from API:", error);
      return [];
    }
  },

  /**
   * Rate expert answer
   */
  rateExpertAnswer: async (
    questionId: string,
    helpful: boolean,
  ): Promise<void> => {
    try {
      await api.post(buildUrl(COMMUNITY_ENDPOINTS.EXPERT_RATE, { questionId }), {
        helpful,
      });
    } catch (error) {
      logger.error(`Failed to rate expert answer ${questionId}:`, error);
      throw error;
    }
  },
};
