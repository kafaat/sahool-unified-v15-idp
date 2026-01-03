/**
 * Community Feature - API Layer
 * طبقة API لميزة المجتمع الزراعي
 */

import axios, { type AxiosError } from 'axios';
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
import { logger } from '@/lib/logger';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Only warn during development, don't throw during build
if (!API_BASE_URL && typeof window !== 'undefined') {
  console.warn('NEXT_PUBLIC_API_URL environment variable is not set');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Add auth token interceptor
// SECURITY: Use js-cookie library for safe cookie parsing instead of manual parsing
import Cookies from 'js-cookie';

api.interceptors.request.use((config) => {
  // Get token from cookie using secure cookie parser
  if (typeof window !== 'undefined') {
    const token = Cookies.get('access_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

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

// Mock data for fallback
const MOCK_POSTS: Post[] = [
  {
    id: '1',
    userId: 'user1',
    userName: 'Ahmed Al-Malki',
    userNameAr: 'أحمد المالكي',
    userAvatar: '/avatars/user1.jpg',
    userBadge: 'farmer',
    type: 'question',
    title: 'Best irrigation method for wheat in summer?',
    titleAr: 'أفضل طريقة ري للقمح في الصيف؟',
    content: 'I am looking for efficient irrigation methods for my wheat farm during the hot summer months.',
    contentAr: 'أبحث عن طرق ري فعالة لمزرعة القمح الخاصة بي خلال أشهر الصيف الحارة.',
    status: 'active',
    tags: ['irrigation', 'wheat', 'summer'],
    tagsAr: ['ري', 'قمح', 'صيف'],
    location: {
      city: 'Riyadh',
      cityAr: 'الرياض',
      region: 'Central',
      regionAr: 'الوسطى',
    },
    likes: 12,
    comments: 5,
    shares: 2,
    views: 45,
    isLiked: false,
    isSaved: false,
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '2',
    userId: 'user2',
    userName: 'Fatima Hassan',
    userNameAr: 'فاطمة حسن',
    userAvatar: '/avatars/user2.jpg',
    userBadge: 'expert',
    type: 'tip',
    title: 'Organic pest control for tomatoes',
    titleAr: 'مكافحة آفات الطماطم بطريقة عضوية',
    content: 'Share my experience with natural pest control methods that work great for tomatoes.',
    contentAr: 'أشارك تجربتي مع طرق مكافحة الآفات الطبيعية التي تعمل بشكل رائع للطماطم.',
    status: 'active',
    images: ['/posts/tomato-pest-control.jpg'],
    tags: ['organic', 'tomatoes', 'pest-control'],
    tagsAr: ['عضوي', 'طماطم', 'مكافحة الآفات'],
    location: {
      city: 'Jeddah',
      cityAr: 'جدة',
      region: 'Western',
      regionAr: 'الغربية',
    },
    likes: 28,
    comments: 8,
    shares: 6,
    views: 120,
    isLiked: true,
    isSaved: true,
    createdAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '3',
    userId: 'user3',
    userName: 'Mohammed Ali',
    userNameAr: 'محمد علي',
    userAvatar: '/avatars/user3.jpg',
    userBadge: 'verified',
    type: 'experience',
    title: 'My journey with drip irrigation system',
    titleAr: 'تجربتي مع نظام الري بالتنقيط',
    content: 'After installing drip irrigation, I reduced water consumption by 40% and increased yield by 25%.',
    contentAr: 'بعد تركيب الري بالتنقيط، قللت استهلاك المياه بنسبة 40% وزادت الإنتاجية بنسبة 25%.',
    status: 'active',
    images: ['/posts/drip-irrigation-1.jpg', '/posts/drip-irrigation-2.jpg'],
    tags: ['irrigation', 'technology', 'water-saving'],
    tagsAr: ['ري', 'تقنية', 'توفير المياه'],
    location: {
      city: 'Dammam',
      cityAr: 'الدمام',
      region: 'Eastern',
      regionAr: 'الشرقية',
    },
    likes: 45,
    comments: 12,
    shares: 15,
    views: 230,
    isLiked: false,
    isSaved: true,
    createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
  },
];

const MOCK_GROUPS: Group[] = [
  {
    id: 'group1',
    name: 'Wheat Farmers Saudi Arabia',
    nameAr: 'مزارعو القمح في السعودية',
    description: 'Community for wheat farmers to share experiences and best practices',
    descriptionAr: 'مجتمع لمزارعي القمح لمشاركة الخبرات وأفضل الممارسات',
    image: '/groups/wheat-farmers.jpg',
    coverImage: '/groups/wheat-cover.jpg',
    category: 'crops',
    privacy: 'public',
    memberCount: 450,
    postCount: 128,
    isJoined: true,
    isModerator: false,
    createdBy: 'admin1',
    createdAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ['wheat', 'crops', 'farming'],
    tagsAr: ['قمح', 'محاصيل', 'زراعة'],
  },
  {
    id: 'group2',
    name: 'Organic Farming Enthusiasts',
    nameAr: 'عشاق الزراعة العضوية',
    description: 'For farmers interested in organic and sustainable farming methods',
    descriptionAr: 'لمزارعين المهتمين بطرق الزراعة العضوية والمستدامة',
    image: '/groups/organic-farming.jpg',
    category: 'organic',
    privacy: 'public',
    memberCount: 320,
    postCount: 89,
    isJoined: false,
    isModerator: false,
    createdBy: 'admin2',
    createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ['organic', 'sustainable', 'eco-friendly'],
    tagsAr: ['عضوي', 'مستدام', 'صديق للبيئة'],
  },
  {
    id: 'group3',
    name: 'Smart Irrigation Technology',
    nameAr: 'تقنية الري الذكي',
    description: 'Discussing latest irrigation technologies and water conservation',
    descriptionAr: 'مناقشة أحدث تقنيات الري والحفاظ على المياه',
    image: '/groups/irrigation-tech.jpg',
    category: 'irrigation',
    privacy: 'public',
    memberCount: 280,
    postCount: 65,
    isJoined: true,
    isModerator: false,
    createdBy: 'admin3',
    createdAt: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ['irrigation', 'technology', 'water'],
    tagsAr: ['ري', 'تقنية', 'مياه'],
  },
];

const MOCK_EXPERTS: Expert[] = [
  {
    id: 'expert1',
    name: 'Dr. Abdullah Al-Rashid',
    nameAr: 'د. عبدالله الراشد',
    avatar: '/experts/expert1.jpg',
    title: 'Agricultural Engineer',
    titleAr: 'مهندس زراعي',
    specialization: ['Irrigation Systems', 'Water Management', 'Crop Planning'],
    specializationAr: ['نظم الري', 'إدارة المياه', 'تخطيط المحاصيل'],
    bio: '15+ years of experience in agricultural engineering and water management systems',
    bioAr: 'أكثر من 15 عاماً من الخبرة في الهندسة الزراعية ونظم إدارة المياه',
    rating: 4.8,
    totalAnswers: 234,
    verifiedAnswers: 198,
    availability: 'available',
    responseTime: 2.5,
  },
  {
    id: 'expert2',
    name: 'Dr. Sarah Al-Mutairi',
    nameAr: 'د. سارة المطيري',
    avatar: '/experts/expert2.jpg',
    title: 'Plant Pathologist',
    titleAr: 'أخصائية أمراض النبات',
    specialization: ['Plant Diseases', 'Pest Control', 'Organic Farming'],
    specializationAr: ['أمراض النبات', 'مكافحة الآفات', 'الزراعة العضوية'],
    bio: 'Expert in plant diseases and sustainable pest management solutions',
    bioAr: 'خبيرة في أمراض النبات وحلول إدارة الآفات المستدامة',
    rating: 4.9,
    totalAnswers: 312,
    verifiedAnswers: 287,
    availability: 'available',
    responseTime: 1.8,
  },
  {
    id: 'expert3',
    name: 'Eng. Khalid Al-Dosari',
    nameAr: 'م. خالد الدوسري',
    avatar: '/experts/expert3.jpg',
    title: 'Agricultural Technology Specialist',
    titleAr: 'أخصائي التقنية الزراعية',
    specialization: ['Smart Farming', 'IoT in Agriculture', 'Automation'],
    specializationAr: ['الزراعة الذكية', 'إنترنت الأشياء الزراعي', 'الأتمتة'],
    bio: 'Specialist in implementing modern agricultural technologies and automation',
    bioAr: 'متخصص في تنفيذ التقنيات الزراعية الحديثة والأتمتة',
    rating: 4.7,
    totalAnswers: 189,
    verifiedAnswers: 156,
    availability: 'busy',
    responseTime: 4.2,
  },
];

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
      if (filters?.type) params.set('type', filters.type);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.tags?.length) params.set('tags', filters.tags.join(','));
      if (filters?.location) params.set('location', filters.location);
      if (filters?.sortBy) params.set('sort_by', filters.sortBy);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`/v1/community/posts?${params.toString()}`);

      // Handle different response formats
      const posts = response.data.data || response.data;

      if (Array.isArray(posts)) {
        return posts;
      }

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_POSTS;
    } catch (error) {
      logger.warn('Failed to fetch posts from API, using mock data:', error);
      return MOCK_POSTS;
    }
  },

  /**
   * Get trending posts
   */
  getTrendingPosts: async (): Promise<Post[]> => {
    try {
      const response = await api.get('/v1/community/posts/trending');
      const posts = response.data.data || response.data;

      if (Array.isArray(posts)) {
        return posts;
      }

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_POSTS.slice(0, 2);
    } catch (error) {
      logger.warn('Failed to fetch trending posts from API, using mock data:', error);
      return MOCK_POSTS.slice(0, 2);
    }
  },

  /**
   * Get user's saved posts
   */
  getSavedPosts: async (): Promise<Post[]> => {
    try {
      const response = await api.get('/v1/community/posts/saved');
      const posts = response.data.data || response.data;

      if (Array.isArray(posts)) {
        return posts;
      }

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_POSTS.filter(p => p.isSaved);
    } catch (error) {
      logger.warn('Failed to fetch saved posts from API, using mock data:', error);
      return MOCK_POSTS.filter(p => p.isSaved);
    }
  },

  /**
   * Get user's own posts
   */
  getMyPosts: async (): Promise<Post[]> => {
    try {
      const response = await api.get('/v1/community/posts/my-posts');
      const posts = response.data.data || response.data;

      if (Array.isArray(posts)) {
        return posts;
      }

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_POSTS.slice(0, 1);
    } catch (error) {
      logger.warn('Failed to fetch my posts from API, using mock data:', error);
      return MOCK_POSTS.slice(0, 1);
    }
  },

  /**
   * Get post by ID
   */
  getPostById: async (id: string): Promise<Post> => {
    try {
      const response = await api.get(`/v1/community/posts/${id}`);
      const post = response.data.data || response.data;
      return post;
    } catch (error) {
      logger.warn(`Failed to fetch post ${id} from API, using mock data:`, error);

      // Fallback to mock data
      const mockPost = MOCK_POSTS.find(p => p.id === id);
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
      const response = await api.post('/v1/community/posts', data);
      const post = response.data.data || response.data;
      return post;
    } catch (error) {
      logger.error('Failed to create post:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.CREATE_POST_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.CREATE_POST_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Update post
   */
  updatePost: async (id: string, data: Partial<Post>): Promise<Post> => {
    try {
      const response = await api.put(`/v1/community/posts/${id}`, data);
      const post = response.data.data || response.data;
      return post;
    } catch (error) {
      logger.error(`Failed to update post ${id}:`, error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.UPDATE_POST_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.UPDATE_POST_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Delete post
   */
  deletePost: async (id: string): Promise<void> => {
    try {
      await api.delete(`/v1/community/posts/${id}`);
    } catch (error) {
      logger.error(`Failed to delete post ${id}:`, error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.DELETE_POST_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.DELETE_POST_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Like/unlike a post
   */
  likePost: async (postId: string): Promise<void> => {
    try {
      await api.post(`/v1/community/posts/${postId}/like`);
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
      await api.post(`/v1/community/posts/${postId}/save`);
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
      await api.post(`/v1/community/posts/${postId}/share`);
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
      const response = await api.get(`/v1/community/posts/${postId}/comments`);
      const comments = response.data.data || response.data;

      if (Array.isArray(comments)) {
        return comments;
      }

      logger.warn('API returned unexpected format, returning empty comments');
      return [];
    } catch (error) {
      logger.warn(`Failed to fetch comments for post ${postId} from API:`, error);
      return [];
    }
  },

  /**
   * Add a comment
   */
  addComment: async (postId: string, content: string, parentId?: string): Promise<Comment> => {
    try {
      const response = await api.post(`/v1/community/posts/${postId}/comments`, {
        content,
        parentId,
      });
      const comment = response.data.data || response.data;
      return comment;
    } catch (error) {
      logger.error(`Failed to add comment to post ${postId}:`, error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.CREATE_COMMENT_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.CREATE_COMMENT_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Like a comment
   */
  likeComment: async (postId: string, commentId: string): Promise<void> => {
    try {
      await api.post(`/v1/community/posts/${postId}/comments/${commentId}/like`);
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
      if (filters?.category) params.set('category', filters.category);
      if (filters?.privacy) params.set('privacy', filters.privacy);
      if (filters?.joined !== undefined) params.set('joined', String(filters.joined));
      if (filters?.sortBy) params.set('sort_by', filters.sortBy);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`/v1/community/groups?${params.toString()}`);

      // Handle different response formats
      const groups = response.data.data || response.data;

      if (Array.isArray(groups)) {
        return groups;
      }

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_GROUPS;
    } catch (error) {
      logger.warn('Failed to fetch groups from API, using mock data:', error);
      return MOCK_GROUPS;
    }
  },

  /**
   * Get group by ID
   */
  getGroupById: async (id: string): Promise<Group> => {
    try {
      const response = await api.get(`/v1/community/groups/${id}`);
      const group = response.data.data || response.data;
      return group;
    } catch (error) {
      logger.warn(`Failed to fetch group ${id} from API, using mock data:`, error);

      // Fallback to mock data
      const mockGroup = MOCK_GROUPS.find(g => g.id === id);
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
      const response = await api.get('/v1/community/groups/my-groups');
      const groups = response.data.data || response.data;

      if (Array.isArray(groups)) {
        return groups;
      }

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_GROUPS.filter(g => g.isJoined);
    } catch (error) {
      logger.warn('Failed to fetch my groups from API, using mock data:', error);
      return MOCK_GROUPS.filter(g => g.isJoined);
    }
  },

  /**
   * Create a group
   */
  createGroup: async (data: Partial<Group>): Promise<Group> => {
    try {
      const response = await api.post('/v1/community/groups', data);
      const group = response.data.data || response.data;
      return group;
    } catch (error) {
      logger.error('Failed to create group:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || 'Failed to create group';
      const errorMessageAr = axiosError.response?.data?.message_ar || 'فشل في إنشاء المجموعة';

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Join a group
   */
  joinGroup: async (groupId: string): Promise<void> => {
    try {
      await api.post(`/v1/community/groups/${groupId}/join`);
    } catch (error) {
      logger.error(`Failed to join group ${groupId}:`, error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.JOIN_GROUP_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.JOIN_GROUP_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Leave a group
   */
  leaveGroup: async (groupId: string): Promise<void> => {
    try {
      await api.post(`/v1/community/groups/${groupId}/leave`);
    } catch (error) {
      logger.error(`Failed to leave group ${groupId}:`, error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.LEAVE_GROUP_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.LEAVE_GROUP_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Get group members
   */
  getGroupMembers: async (groupId: string): Promise<GroupMember[]> => {
    try {
      const response = await api.get(`/v1/community/groups/${groupId}/members`);
      const members = response.data.data || response.data;

      if (Array.isArray(members)) {
        return members;
      }

      logger.warn('API returned unexpected format, returning empty members');
      return [];
    } catch (error) {
      logger.warn(`Failed to fetch members for group ${groupId} from API:`, error);
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
      const response = await api.get(`/v1/community/groups/${groupId}/messages`);
      const messages = response.data.data || response.data;

      if (Array.isArray(messages)) {
        return messages;
      }

      logger.warn('API returned unexpected format, returning empty messages');
      return [];
    } catch (error) {
      logger.warn(`Failed to fetch messages for group ${groupId} from API:`, error);
      return [];
    }
  },

  /**
   * Send a message
   */
  sendMessage: async (
    groupId: string,
    content: string,
    type: 'text' | 'image' | 'file' | 'voice' = 'text'
  ): Promise<ChatMessage> => {
    try {
      const response = await api.post(`/v1/community/groups/${groupId}/messages`, {
        content,
        type,
      });
      const message = response.data.data || response.data;
      return message;
    } catch (error) {
      logger.error(`Failed to send message to group ${groupId}:`, error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.SEND_MESSAGE_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.SEND_MESSAGE_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
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
      const response = await api.get('/v1/community/experts');
      const experts = response.data.data || response.data;

      if (Array.isArray(experts)) {
        return experts;
      }

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_EXPERTS;
    } catch (error) {
      logger.warn('Failed to fetch experts from API, using mock data:', error);
      return MOCK_EXPERTS;
    }
  },

  /**
   * Ask an expert
   */
  askExpert: async (data: Partial<ExpertQuestion>): Promise<ExpertQuestion> => {
    try {
      const response = await api.post('/v1/community/expert-questions', data);
      const question = response.data.data || response.data;
      return question;
    } catch (error) {
      logger.error('Failed to submit expert question:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.ASK_EXPERT_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.ASK_EXPERT_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Get expert questions
   */
  getExpertQuestions: async (): Promise<ExpertQuestion[]> => {
    try {
      const response = await api.get('/v1/community/expert-questions');
      const questions = response.data.data || response.data;

      if (Array.isArray(questions)) {
        return questions;
      }

      logger.warn('API returned unexpected format, returning empty questions');
      return [];
    } catch (error) {
      logger.warn('Failed to fetch expert questions from API:', error);
      return [];
    }
  },

  /**
   * Rate expert answer
   */
  rateExpertAnswer: async (questionId: string, helpful: boolean): Promise<void> => {
    try {
      await api.post(`/v1/community/expert-questions/${questionId}/rate`, { helpful });
    } catch (error) {
      logger.error(`Failed to rate expert answer ${questionId}:`, error);
      throw error;
    }
  },
};
