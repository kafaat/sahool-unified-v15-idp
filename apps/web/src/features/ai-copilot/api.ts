/**
 * AI Copilot Feature - API Layer
 * طبقة API لميزة المساعد الذكي
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { AI_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type { ChatMessage, ChatHistory, CopilotTool, RagDocument, RagSearchResult } from './types';

const api = createApiClient({ timeout: 60000 });

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. AI assistant unavailable.',
    ar: 'خطأ في الاتصال. المساعد الذكي غير متاح.',
  },
  CHAT_FAILED: {
    en: 'Failed to send message to AI assistant.',
    ar: 'فشل في إرسال الرسالة للمساعد الذكي.',
  },
  FETCH_HISTORY_FAILED: {
    en: 'Failed to fetch chat history.',
    ar: 'فشل في جلب سجل المحادثات.',
  },
  FETCH_TOOLS_FAILED: {
    en: 'Failed to fetch available tools.',
    ar: 'فشل في جلب الأدوات المتاحة.',
  },
  UPLOAD_DOCUMENT_FAILED: {
    en: 'Failed to upload document.',
    ar: 'فشل في رفع المستند.',
  },
  SEARCH_FAILED: {
    en: 'Failed to search knowledge base.',
    ar: 'فشل في البحث في قاعدة المعرفة.',
  },
};

export const copilotApi = {
  sendMessage: async (message: string, context?: Record<string, unknown>): Promise<ChatMessage> => {
    return safeFetch(AI_ENDPOINTS.COPILOT_CHAT, async () => {
      const response = await api.post(AI_ENDPOINTS.COPILOT_CHAT, {
        message,
        context,
      });
      return response.data.data || response.data;
    });
  },

  getChatHistory: async (limit?: number): Promise<ChatHistory[]> => {
    return safeFetch(AI_ENDPOINTS.COPILOT_HISTORY, async () => {
      const params = limit ? `?limit=${limit}` : '';
      const response = await api.get(`${AI_ENDPOINTS.COPILOT_HISTORY}${params}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getTools: async (): Promise<CopilotTool[]> => {
    return safeFetch(AI_ENDPOINTS.COPILOT_TOOLS, async () => {
      const response = await api.get(AI_ENDPOINTS.COPILOT_TOOLS);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  executeTool: async (toolName: string, params: Record<string, unknown>): Promise<unknown> => {
    return safeFetch(AI_ENDPOINTS.COPILOT_EXECUTE_TOOL, async () => {
      const url = buildUrl(AI_ENDPOINTS.COPILOT_EXECUTE_TOOL, { toolName });
      const response = await api.post(url, params);
      return response.data.data || response.data;
    });
  },

  uploadDocument: async (file: File, metadata?: Record<string, string>): Promise<RagDocument> => {
    return safeFetch(AI_ENDPOINTS.RAG_DOCUMENTS, async () => {
      const formData = new FormData();
      formData.append('document', file);
      if (metadata) {
        Object.entries(metadata).forEach(([key, value]) => formData.append(key, value));
      }
      const response = await api.post(AI_ENDPOINTS.RAG_DOCUMENTS, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    });
  },

  searchKnowledge: async (query: string, topK?: number): Promise<RagSearchResult[]> => {
    return safeFetch(AI_ENDPOINTS.RAG_SEARCH, async () => {
      const response = await api.post(AI_ENDPOINTS.RAG_SEARCH, { query, top_k: topK || 5 });
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  queryAdvisor: async (query: string, fieldId?: string): Promise<ChatMessage> => {
    return safeFetch(AI_ENDPOINTS.AI_ADVISOR_QUERY, async () => {
      const response = await api.post(AI_ENDPOINTS.AI_ADVISOR_QUERY, {
        query,
        field_id: fieldId,
      });
      return response.data.data || response.data;
    });
  },

  getAdvisorHistory: async (): Promise<ChatHistory[]> => {
    return safeFetch(AI_ENDPOINTS.AI_ADVISOR_HISTORY, async () => {
      const response = await api.get(AI_ENDPOINTS.AI_ADVISOR_HISTORY);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },
};
