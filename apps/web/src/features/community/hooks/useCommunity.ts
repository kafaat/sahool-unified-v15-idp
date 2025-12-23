/**
 * Community Feature - React Hooks for Posts
 * خطافات React لمنشورات المجتمع
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import type { Post, Comment, CommunityFilters } from '../types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Query Keys
const COMMUNITY_KEYS = {
  all: ['community'] as const,
  posts: (filters?: CommunityFilters) => [...COMMUNITY_KEYS.all, 'posts', filters] as const,
  post: (id: string) => [...COMMUNITY_KEYS.all, 'post', id] as const,
  comments: (postId: string) => [...COMMUNITY_KEYS.all, 'comments', postId] as const,
  trending: () => [...COMMUNITY_KEYS.all, 'trending'] as const,
  saved: () => [...COMMUNITY_KEYS.all, 'saved'] as const,
  myPosts: () => [...COMMUNITY_KEYS.all, 'my-posts'] as const,
};

/**
 * Hook to fetch community posts feed
 */
export function usePosts(filters?: CommunityFilters) {
  return useQuery({
    queryKey: COMMUNITY_KEYS.posts(filters),
    queryFn: async (): Promise<Post[]> => {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.tags?.length) params.set('tags', filters.tags.join(','));
      if (filters?.location) params.set('location', filters.location);
      if (filters?.sortBy) params.set('sort_by', filters.sortBy);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`/v1/community/posts?${params.toString()}`);
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to fetch a single post
 */
export function usePost(id: string) {
  return useQuery({
    queryKey: COMMUNITY_KEYS.post(id),
    queryFn: async (): Promise<Post> => {
      const response = await api.get(`/v1/community/posts/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Hook to fetch trending posts
 */
export function useTrendingPosts() {
  return useQuery({
    queryKey: COMMUNITY_KEYS.trending(),
    queryFn: async (): Promise<Post[]> => {
      const response = await api.get('/v1/community/posts/trending');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch user's saved posts
 */
export function useSavedPosts() {
  return useQuery({
    queryKey: COMMUNITY_KEYS.saved(),
    queryFn: async (): Promise<Post[]> => {
      const response = await api.get('/v1/community/posts/saved');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch user's own posts
 */
export function useMyPosts() {
  return useQuery({
    queryKey: COMMUNITY_KEYS.myPosts(),
    queryFn: async (): Promise<Post[]> => {
      const response = await api.get('/v1/community/posts/my-posts');
      return response.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Hook to create a new post
 */
export function useCreatePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<Post>): Promise<Post> => {
      const response = await api.post('/v1/community/posts', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: COMMUNITY_KEYS.all });
    },
  });
}

/**
 * Hook to update a post
 */
export function useUpdatePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Post> }): Promise<Post> => {
      const response = await api.put(`/v1/community/posts/${id}`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: COMMUNITY_KEYS.post(id) });
      queryClient.invalidateQueries({ queryKey: COMMUNITY_KEYS.posts() });
    },
  });
}

/**
 * Hook to delete a post
 */
export function useDeletePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      await api.delete(`/v1/community/posts/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: COMMUNITY_KEYS.all });
    },
  });
}

/**
 * Hook to like/unlike a post
 */
export function useLikePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (postId: string): Promise<void> => {
      await api.post(`/v1/community/posts/${postId}/like`);
    },
    onSuccess: (_, postId) => {
      queryClient.invalidateQueries({ queryKey: COMMUNITY_KEYS.post(postId) });
      queryClient.invalidateQueries({ queryKey: COMMUNITY_KEYS.posts() });
    },
  });
}

/**
 * Hook to save/unsave a post
 */
export function useSavePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (postId: string): Promise<void> => {
      await api.post(`/v1/community/posts/${postId}/save`);
    },
    onSuccess: (_, postId) => {
      queryClient.invalidateQueries({ queryKey: COMMUNITY_KEYS.post(postId) });
      queryClient.invalidateQueries({ queryKey: COMMUNITY_KEYS.saved() });
    },
  });
}

/**
 * Hook to share a post
 */
export function useSharePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (postId: string): Promise<void> => {
      await api.post(`/v1/community/posts/${postId}/share`);
    },
    onSuccess: (_, postId) => {
      queryClient.invalidateQueries({ queryKey: COMMUNITY_KEYS.post(postId) });
    },
  });
}

/**
 * Hook to fetch post comments
 */
export function useComments(postId: string) {
  return useQuery({
    queryKey: COMMUNITY_KEYS.comments(postId),
    queryFn: async (): Promise<Comment[]> => {
      const response = await api.get(`/v1/community/posts/${postId}/comments`);
      return response.data;
    },
    enabled: !!postId,
  });
}

/**
 * Hook to add a comment
 */
export function useAddComment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      postId,
      content,
      parentId,
    }: {
      postId: string;
      content: string;
      parentId?: string;
    }): Promise<Comment> => {
      const response = await api.post(`/v1/community/posts/${postId}/comments`, {
        content,
        parentId,
      });
      return response.data;
    },
    onSuccess: (_, { postId }) => {
      queryClient.invalidateQueries({ queryKey: COMMUNITY_KEYS.comments(postId) });
      queryClient.invalidateQueries({ queryKey: COMMUNITY_KEYS.post(postId) });
    },
  });
}

/**
 * Hook to like a comment
 */
export function useLikeComment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ postId, commentId }: { postId: string; commentId: string }): Promise<void> => {
      await api.post(`/v1/community/posts/${postId}/comments/${commentId}/like`);
    },
    onSuccess: (_, { postId }) => {
      queryClient.invalidateQueries({ queryKey: COMMUNITY_KEYS.comments(postId) });
    },
  });
}
