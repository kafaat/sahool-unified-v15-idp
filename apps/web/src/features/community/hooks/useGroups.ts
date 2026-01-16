/**
 * Community Feature - React Hooks for Groups
 * خطافات React لمجموعات المجتمع
 */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { Group, GroupFilters, ExpertQuestion } from "../types";
import { communityApi } from "../api";

// Query Keys
const GROUPS_KEYS = {
  all: ["groups"] as const,
  list: (filters?: GroupFilters) =>
    [...GROUPS_KEYS.all, "list", filters] as const,
  group: (id: string) => [...GROUPS_KEYS.all, "group", id] as const,
  members: (groupId: string) =>
    [...GROUPS_KEYS.all, "members", groupId] as const,
  messages: (groupId: string) =>
    [...GROUPS_KEYS.all, "messages", groupId] as const,
  myGroups: () => [...GROUPS_KEYS.all, "my-groups"] as const,
  experts: () => [...GROUPS_KEYS.all, "experts"] as const,
  expertQuestions: () => [...GROUPS_KEYS.all, "expert-questions"] as const,
};

/**
 * Hook to fetch groups
 */
export function useGroups(filters?: GroupFilters) {
  return useQuery({
    queryKey: GROUPS_KEYS.list(filters),
    queryFn: () => communityApi.getGroups(filters),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch a single group
 */
export function useGroup(id: string) {
  return useQuery({
    queryKey: GROUPS_KEYS.group(id),
    queryFn: () => communityApi.getGroupById(id),
    enabled: !!id,
  });
}

/**
 * Hook to fetch user's joined groups
 */
export function useMyGroups() {
  return useQuery({
    queryKey: GROUPS_KEYS.myGroups(),
    queryFn: () => communityApi.getMyGroups(),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to create a group
 */
export function useCreateGroup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Group>) => communityApi.createGroup(data),
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
    mutationFn: (groupId: string) => communityApi.joinGroup(groupId),
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
    mutationFn: (groupId: string) => communityApi.leaveGroup(groupId),
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
    queryFn: () => communityApi.getGroupMembers(groupId),
    enabled: !!groupId,
  });
}

/**
 * Hook to fetch group chat messages
 */
export function useGroupMessages(groupId: string) {
  return useQuery({
    queryKey: GROUPS_KEYS.messages(groupId),
    queryFn: () => communityApi.getGroupMessages(groupId),
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
    mutationFn: ({
      groupId,
      content,
      type,
    }: {
      groupId: string;
      content: string;
      type?: "text" | "image" | "file" | "voice";
    }) => communityApi.sendMessage(groupId, content, type),
    onSuccess: (_, { groupId }) => {
      queryClient.invalidateQueries({
        queryKey: GROUPS_KEYS.messages(groupId),
      });
    },
  });
}

/**
 * Hook to fetch experts
 */
export function useExperts() {
  return useQuery({
    queryKey: GROUPS_KEYS.experts(),
    queryFn: () => communityApi.getExperts(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to ask an expert
 */
export function useAskExpert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<ExpertQuestion>) => communityApi.askExpert(data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: GROUPS_KEYS.expertQuestions(),
      });
    },
  });
}

/**
 * Hook to fetch expert questions
 */
export function useExpertQuestions() {
  return useQuery({
    queryKey: GROUPS_KEYS.expertQuestions(),
    queryFn: () => communityApi.getExpertQuestions(),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to rate expert answer
 */
export function useRateExpertAnswer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      questionId,
      helpful,
    }: {
      questionId: string;
      helpful: boolean;
    }) => communityApi.rateExpertAnswer(questionId, helpful),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: GROUPS_KEYS.expertQuestions(),
      });
    },
  });
}
