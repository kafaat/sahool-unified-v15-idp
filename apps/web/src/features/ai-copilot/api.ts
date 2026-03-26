/**
 * AI Copilot Feature - API Layer
 * طبقة API لميزة المساعد الذكي
 */

import { createApiClient, logger } from '@/lib/api/factory';
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

const MOCK_HISTORY: ChatHistory[] = [];

const MOCK_TOOLS: CopilotTool[] = [
  {
    name: 'weather_lookup',
    nameAr: 'البحث عن الطقس',
    description: 'Get current weather and forecast for a location',
    descriptionAr: 'الحصول على الطقس الحالي والتوقعات لموقع معين',
    category: 'data',
    enabled: true,
  },
  {
    name: 'crop_diagnosis',
    nameAr: 'تشخيص المحصول',
    description: 'Diagnose crop health issues from description or images',
    descriptionAr: 'تشخيص مشاكل صحة المحصول من الوصف أو الصور',
    category: 'ai',
    enabled: true,
  },
  {
    name: 'irrigation_calculator',
    nameAr: 'حاسبة الري',
    description: 'Calculate optimal irrigation schedule',
    descriptionAr: 'حساب جدول الري الأمثل',
    category: 'calculation',
    enabled: true,
  },
];

export const copilotApi = {
  sendMessage: async (message: string, context?: Record<string, unknown>): Promise<ChatMessage> => {
    try {
      const response = await api.post(AI_ENDPOINTS.COPILOT_CHAT, {
        message,
        context,
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to send message to copilot:', error);
      throw new Error(ERROR_MESSAGES.CHAT_FAILED.en);
    }
  },

  getChatHistory: async (limit?: number): Promise<ChatHistory[]> => {
    try {
      const params = limit ? `?limit=${limit}` : '';
      const response = await api.get(`${AI_ENDPOINTS.COPILOT_HISTORY}${params}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return MOCK_HISTORY;
    } catch (error) {
      logger.warn('Failed to fetch chat history, using mock data:', error);
      return MOCK_HISTORY;
    }
  },

  getTools: async (): Promise<CopilotTool[]> => {
    try {
      const response = await api.get(AI_ENDPOINTS.COPILOT_TOOLS);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return MOCK_TOOLS;
    } catch (error) {
      logger.warn('Failed to fetch tools, using mock data:', error);
      return MOCK_TOOLS;
    }
  },

  executeTool: async (toolName: string, params: Record<string, unknown>): Promise<unknown> => {
    try {
      const url = buildUrl(AI_ENDPOINTS.COPILOT_EXECUTE_TOOL, { toolName });
      const response = await api.post(url, params);
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to execute tool ${toolName}:`, error);
      throw error;
    }
  },

  uploadDocument: async (file: File, metadata?: Record<string, string>): Promise<RagDocument> => {
    try {
      const formData = new FormData();
      formData.append('document', file);
      if (metadata) {
        Object.entries(metadata).forEach(([key, value]) => formData.append(key, value));
      }
      const response = await api.post(AI_ENDPOINTS.RAG_DOCUMENTS, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to upload document:', error);
      throw new Error(ERROR_MESSAGES.UPLOAD_DOCUMENT_FAILED.en);
    }
  },

  searchKnowledge: async (query: string, topK?: number): Promise<RagSearchResult[]> => {
    try {
      const response = await api.post(AI_ENDPOINTS.RAG_SEARCH, { query, top_k: topK || 5 });
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    } catch (error) {
      logger.warn('Failed to search knowledge base:', error);
      return [];
    }
  },

  queryAdvisor: async (query: string, fieldId?: string): Promise<ChatMessage> => {
    try {
      const response = await api.post(AI_ENDPOINTS.AI_ADVISOR_QUERY, {
        query,
        field_id: fieldId,
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to query AI advisor:', error);
      throw new Error(ERROR_MESSAGES.CHAT_FAILED.en);
    }
  },

  getAdvisorHistory: async (): Promise<ChatHistory[]> => {
    try {
      const response = await api.get(AI_ENDPOINTS.AI_ADVISOR_HISTORY);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    } catch (error) {
      logger.warn('Failed to fetch advisor history:', error);
      return [];
    }
  },
};
