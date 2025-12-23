/**
 * Community Feature - React Hooks for Groups
 * خطافات React لمجموعات المجتمع
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import type { Group, GroupMember, GroupFilters, ChatMessage, Expert, ExpertQuestion } from '../types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Query Keys
const GROUPS_KEYS = {
  all: ['groups'] as const,
  list: (filters?: GroupFilters) => [...GROUPS_KEYS.all, 'list', filters] as const,
  group: (id: string) => [...GROUPS_KEYS.all, 'group', id] as const,
  members: (groupId: string) => [...GROUPS_KEYS.all, 'members', groupId] as const,
  messages: (groupId: string) => [...GROUPS_KEYS.all, 'messages', groupId] as const,
  myGroups: () => [...GROUPS_KEYS.all, 'my-groups'] as const,
  experts: () => [...GROUPS_KEYS.all, 'experts'] as const,
  expertQuestions: () => [...GROUPS_KEYS.all, 'expert-questions'] as const,
};

/**
 * Hook to fetch groups
 */
export function useGroups(filters?: GroupFilters) {
  return useQuery({
    queryKey: GROUPS_KEYS.list(filters),
    queryFn: async (): Promise<Group[]> => {
      const params = new URLSearchParams();
      if (filters?.category) params.set('category', filters.category);
      if (filters?.privacy) params.set('privacy', filters.privacy);
      if (filters?.joined !== undefined) params.set('joined', String(filters.joined));
      if (filters?.sortBy) params.set('sort_by', filters.sortBy);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`/v1/community/groups?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch a single group
 */
export function useGroup(id: string) {
  return useQuery({
    queryKey: GROUPS_KEYS.group(id),
    queryFn: async (): Promise<Group> => {
      const response = await api.get(`/v1/community/groups/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Hook to fetch user's joined groups
 */
export function useMyGroups() {
  return useQuery({
    queryKey: GROUPS_KEYS.myGroups(),
    queryFn: async (): Promise<Group[]> => {
      const response = await api.get('/v1/community/groups/my-groups');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to create a group
 */
export function useCreateGroup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<Group>): Promise<Group> => {
      const response = await api.post('/v1/community/groups', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GROUPS_KEYS.all });
    },
  });
}

/**
 * Hook to join a group
 */
export function useJoinGroup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (groupId: string): Promise<void> => {
      await api.post(`/v1/community/groups/${groupId}/join`);
    },
    onSuccess: (_, groupId) => {
      queryClient.invalidateQueries({ queryKey: GROUPS_KEYS.group(groupId) });
      queryClient.invalidateQueries({ queryKey: GROUPS_KEYS.myGroups() });
    },
  });
}

/**
 * Hook to leave a group
 */
export function useLeaveGroup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (groupId: string): Promise<void> => {
      await api.post(`/v1/community/groups/${groupId}/leave`);
    },
    onSuccess: (_, groupId) => {
      queryClient.invalidateQueries({ queryKey: GROUPS_KEYS.group(groupId) });
      queryClient.invalidateQueries({ queryKey: GROUPS_KEYS.myGroups() });
    },
  });
}

/**
 * Hook to fetch group members
 */
export function useGroupMembers(groupId: string) {
  return useQuery({
    queryKey: GROUPS_KEYS.members(groupId),
    queryFn: async (): Promise<GroupMember[]> => {
      const response = await api.get(`/v1/community/groups/${groupId}/members`);
      return response.data;
    },
    enabled: !!groupId,
  });
}

/**
 * Hook to fetch group chat messages
 */
export function useGroupMessages(groupId: string) {
  return useQuery({
    queryKey: GROUPS_KEYS.messages(groupId),
    queryFn: async (): Promise<ChatMessage[]> => {
      const response = await api.get(`/v1/community/groups/${groupId}/messages`);
      return response.data;
    },
    enabled: !!groupId,
    refetchInterval: 10000, // Poll every 10 seconds for new messages
  });
}

/**
 * Hook to send a message
 */
export function useSendMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      groupId,
      content,
      type,
    }: {
      groupId: string;
      content: string;
      type?: 'text' | 'image' | 'file' | 'voice';
    }): Promise<ChatMessage> => {
      const response = await api.post(`/v1/community/groups/${groupId}/messages`, {
        content,
        type: type || 'text',
      });
      return response.data;
    },
    onSuccess: (_, { groupId }) => {
      queryClient.invalidateQueries({ queryKey: GROUPS_KEYS.messages(groupId) });
    },
  });
}

/**
 * Hook to fetch experts
 */
export function useExperts() {
  return useQuery({
    queryKey: GROUPS_KEYS.experts(),
    queryFn: async (): Promise<Expert[]> => {
      const response = await api.get('/v1/community/experts');
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to ask an expert
 */
export function useAskExpert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<ExpertQuestion>): Promise<ExpertQuestion> => {
      const response = await api.post('/v1/community/expert-questions', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GROUPS_KEYS.expertQuestions() });
    },
  });
}

/**
 * Hook to fetch expert questions
 */
export function useExpertQuestions() {
  return useQuery({
    queryKey: GROUPS_KEYS.expertQuestions(),
    queryFn: async (): Promise<ExpertQuestion[]> => {
      const response = await api.get('/v1/community/expert-questions');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to rate expert answer
 */
export function useRateExpertAnswer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      questionId,
      helpful,
    }: {
      questionId: string;
      helpful: boolean;
    }): Promise<void> => {
      await api.post(`/v1/community/expert-questions/${questionId}/rate`, { helpful });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GROUPS_KEYS.expertQuestions() });
    },
  });
}
