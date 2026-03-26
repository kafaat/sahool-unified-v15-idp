/**
 * AI Copilot Feature - Types
 * أنواع ميزة المساعد الذكي
 */

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  contentAr?: string;
  toolCalls?: ToolCall[];
  sources?: string[];
  confidence?: number;
  createdAt: string;
}

export interface ChatHistory {
  id: string;
  title: string;
  titleAr?: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}

export interface ToolCall {
  toolName: string;
  arguments: Record<string, unknown>;
  result?: unknown;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

export interface CopilotTool {
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
  category: 'data' | 'ai' | 'calculation' | 'action';
  enabled: boolean;
}

export interface RagDocument {
  id: string;
  name: string;
  nameAr?: string;
  type: string;
  size: number;
  uploadedAt: string;
  status: 'processing' | 'indexed' | 'failed';
}

export interface RagSearchResult {
  id: string;
  content: string;
  score: number;
  source: string;
  metadata?: Record<string, unknown>;
}

export interface CopilotFilters {
  dateFrom?: string;
  dateTo?: string;
  toolName?: string;
}
