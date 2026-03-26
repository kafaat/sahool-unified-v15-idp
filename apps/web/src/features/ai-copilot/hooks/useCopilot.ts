/**
 * AI Copilot Feature - React Hooks
 * خطافات React لميزة المساعد الذكي
 *
 * React Query hooks for chat messaging, tool execution, document upload,
 * knowledge search, and agricultural advisory.
 * خطافات للمحادثة، تنفيذ الأدوات، رفع المستندات،
 * البحث في المعرفة، والاستشارات الزراعية.
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { copilotApi } from '../api';
import type { ChatMessage, ChatHistory, CopilotTool, RagDocument } from '../types';

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys - مفاتيح الاستعلام
// ═══════════════════════════════════════════════════════════════════════════

export const copilotKeys = {
  all: ['copilot'] as const,
  chatHistory: (limit?: number) => [...copilotKeys.all, 'chatHistory', limit] as const,
  tools: () => [...copilotKeys.all, 'tools'] as const,
  advisorHistory: () => [...copilotKeys.all, 'advisorHistory'] as const,
  knowledge: () => [...copilotKeys.all, 'knowledge'] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks - خطافات الاستعلام
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch chat history
 * خطاف لجلب سجل المحادثة
 *
 * Retrieves the conversation history with the AI copilot.
 *
 * @param limit - Maximum number of messages to retrieve
 * @returns Query result with chat history
 */
export function useChatHistory(limit?: number) {
  return useQuery<ChatHistory[]>({
    queryKey: copilotKeys.chatHistory(limit),
    queryFn: () => copilotApi.getChatHistory(limit),
    staleTime: 1000 * 60 * 2, // 2 minutes - chat history updates frequently
  });
}

/**
 * Hook to fetch available copilot tools
 * خطاف لجلب أدوات المساعد المتاحة
 *
 * Retrieves the list of tools the copilot can invoke (e.g., weather, NDVI, advisory).
 *
 * @returns Query result with copilot tools list
 */
export function useCopilotTools() {
  return useQuery<CopilotTool[]>({
    queryKey: copilotKeys.tools(),
    queryFn: () => copilotApi.getTools(),
    staleTime: 1000 * 60 * 30, // 30 minutes - tools rarely change
  });
}

/**
 * Hook to fetch advisor conversation history
 * خطاف لجلب سجل محادثات المستشار
 *
 * Retrieves the agricultural advisory conversation history.
 *
 * @returns Query result with advisor history
 */
export function useAdvisorHistory() {
  return useQuery({
    queryKey: copilotKeys.advisorHistory(),
    queryFn: () => copilotApi.getAdvisorHistory(),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Hooks - خطافات الطفرة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to send a message to the copilot
 * خطاف لإرسال رسالة إلى المساعد الذكي
 *
 * Sends a user message and receives an AI-generated response.
 *
 * @returns Mutation result with AI response message
 */
export function useSendMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ message, context }: { message: string; context?: Record<string, unknown> }) =>
      copilotApi.sendMessage(message, context),
    onSuccess: (_result: ChatMessage) => {
      queryClient.invalidateQueries({ queryKey: copilotKeys.chatHistory() });
    },
  });
}

/**
 * Hook to execute a copilot tool
 * خطاف لتنفيذ أداة المساعد
 *
 * Invokes a specific tool with parameters (e.g., check weather, analyze NDVI).
 *
 * @returns Mutation result with tool execution output
 */
export function useExecuteTool() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ toolName, params }: { toolName: string; params: Record<string, unknown> }) =>
      copilotApi.executeTool(toolName, params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: copilotKeys.chatHistory() });
    },
  });
}

/**
 * Hook to upload a document for RAG knowledge
 * خطاف لرفع مستند لقاعدة المعرفة
 *
 * Uploads a document that will be indexed for retrieval-augmented generation.
 *
 * @returns Mutation result with uploaded document metadata
 */
export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, metadata }: { file: File; metadata?: Record<string, string> }) =>
      copilotApi.uploadDocument(file, metadata),
    onSuccess: (_result: RagDocument) => {
      queryClient.invalidateQueries({ queryKey: copilotKeys.knowledge() });
    },
  });
}

/**
 * Hook to search knowledge base
 * خطاف للبحث في قاعدة المعرفة
 *
 * Performs semantic search across the RAG knowledge base.
 *
 * @returns Mutation result with search results
 */
export function useSearchKnowledge() {
  return useMutation({
    mutationFn: ({ query, topK }: { query: string; topK?: number }) =>
      copilotApi.searchKnowledge(query, topK),
  });
}

/**
 * Hook to query the agricultural advisor
 * خطاف لاستشارة المستشار الزراعي
 *
 * Sends a query to the agricultural advisory system with optional field context.
 *
 * @returns Mutation result with advisory response
 */
export function useQueryAdvisor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ query, fieldId }: { query: string; fieldId?: string }) =>
      copilotApi.queryAdvisor(query, fieldId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: copilotKeys.advisorHistory() });
      queryClient.invalidateQueries({ queryKey: copilotKeys.chatHistory() });
    },
  });
}
