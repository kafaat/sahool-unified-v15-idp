/**
 * Community Feature - React Hooks for Posts
 * خطافات React لمنشورات المجتمع
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { Post, Comment, CommunityFilters } from '../types';
import { communityApi } from '../api';

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
    queryFn: () => communityApi.getPosts(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to fetch a single post
 */
export function usePost(id: string) {
  return useQuery({
    queryKey: COMMUNITY_KEYS.post(id),
    queryFn: () => communityApi.getPostById(id),
    enabled: !!id,
  });
}

/**
 * Hook to fetch trending posts
 */
export function useTrendingPosts() {
  return useQuery({
    queryKey: COMMUNITY_KEYS.trending(),
    queryFn: () => communityApi.getTrendingPosts(),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch user's saved posts
 */
export function useSavedPosts() {
  return useQuery({
    queryKey: COMMUNITY_KEYS.saved(),
    queryFn: () => communityApi.getSavedPosts(),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch user's own posts
 */
export function useMyPosts() {
  return useQuery({
    queryKey: COMMUNITY_KEYS.myPosts(),
    queryFn: () => communityApi.getMyPosts(),
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Hook to create a new post
 */
export function useCreatePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Post>) => communityApi.createPost(data),
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
    mutationFn: ({ id, data }: { id: string; data: Partial<Post> }) =>
      communityApi.updatePost(id, data),
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
    mutationFn: (id: string) => communityApi.deletePost(id),
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
    mutationFn: (postId: string) => communityApi.likePost(postId),
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
    mutationFn: (postId: string) => communityApi.savePost(postId),
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
    mutationFn: (postId: string) => communityApi.sharePost(postId),
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
    queryFn: () => communityApi.getComments(postId),
    enabled: !!postId,
  });
}

/**
 * Hook to add a comment
 */
export function useAddComment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      postId,
      content,
      parentId,
    }: {
      postId: string;
      content: string;
      parentId?: string;
    }) => communityApi.addComment(postId, content, parentId),
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
    mutationFn: ({ postId, commentId }: { postId: string; commentId: string }) =>
      communityApi.likeComment(postId, commentId),
    onSuccess: (_, { postId }) => {
      queryClient.invalidateQueries({ queryKey: COMMUNITY_KEYS.comments(postId) });
    },
  });
}
