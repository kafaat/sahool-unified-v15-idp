'use client';

/**
 * SAHOOL Copilot Chat Page
 * صفحة المساعد الذكي
 *
 * AI-powered agricultural advisor with SSE streaming support.
 * Connects to copilot-api service on port 8088.
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Bot, User, Sparkles, Loader2, Trash2, RotateCcw, Leaf } from 'lucide-react';
import { AI_ENDPOINTS } from '@sahool/shared-types/contracts';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const COPILOT_API_BASE = process.env.NEXT_PUBLIC_COPILOT_API_URL || '';

const QUICK_QUESTIONS = [
  { label: 'متى أسقي القمح؟', icon: 'droplet' },
  { label: 'ما أفضل سماد للطماطم؟', icon: 'leaf' },
  { label: 'كيف أكتشف أمراض المحاصيل؟', icon: 'bug' },
  { label: 'ما توقعات الطقس اليوم؟', icon: 'cloud' },
  { label: 'نصائح لتحسين الإنتاجية', icon: 'trending' },
  { label: 'جدول الري الأمثل لهذا الأسبوع', icon: 'calendar' },
];

const WELCOME_MESSAGE: ChatMessage = {
  id: 'welcome',
  role: 'assistant',
  content: `مرحبا! أنا مساعد سهول الذكي 🌱

أستطيع مساعدتك في:
- **إدارة الحقول والمحاصيل** - نصائح الزراعة والعناية
- **جدولة الري** - توصيات ري مخصصة لحقولك
- **تشخيص الأمراض** - كشف وعلاج أمراض المحاصيل
- **توقعات الطقس** - تحليل الطقس وتأثيره على الزراعة
- **توصيات الأسمدة** - خطط تسميد مثالية

اسألني أي سؤال زراعي!

---

Hello! I'm SAHOOL's AI assistant 🌱

I can help you with field management, irrigation scheduling, disease diagnosis, weather analysis, and fertilizer recommendations.

Ask me any agricultural question!`,
  timestamp: new Date(),
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function generateId(): string {
  const rand =
    typeof globalThis.crypto?.randomUUID === 'function'
      ? globalThis.crypto.randomUUID().substring(0, 7)
      : Math.random().toString(36).slice(2, 9);
  return `msg-${Date.now()}-${rand}`;
}

function generateSessionId(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback UUID v4 using crypto.getRandomValues where available
  if (typeof crypto !== 'undefined' && typeof crypto.getRandomValues === 'function') {
    const bytes = new Uint8Array(16);
    crypto.getRandomValues(bytes);

    // Per RFC 4122 section 4.4, set the version to 4 and the variant to RFC 4122
    bytes[6] = (bytes[6]! & 0x0f) | 0x40;
    bytes[8] = (bytes[8]! & 0x3f) | 0x80;

    const byteToHex: string[] = [];
    for (let i = 0; i < 256; ++i) {
      byteToHex.push((i + 0x100).toString(16).substring(1));
    }

    const hex = (i: number) => byteToHex[bytes[i]!]!;
    return (
      hex(0) +
      hex(1) +
      hex(2) +
      hex(3) +
      '-' +
      hex(4) +
      hex(5) +
      '-' +
      hex(6) +
      hex(7) +
      '-' +
      hex(8) +
      hex(9) +
      '-' +
      hex(10) +
      hex(11) +
      hex(12) +
      hex(13) +
      hex(14) +
      hex(15)
    );
  }

  // Last-resort fallback: deterministic ID without relying on Math.random.
  // This should only be hit in very constrained environments (e.g. SSR).
  return '00000000-0000-4000-8000-000000000000';
}

// Session ID is generated per page load - not persisted to storage.
// This avoids XSS exposure via sessionStorage while maintaining
// session continuity within a single browser tab.
// معرف الجلسة يُنشأ لكل تحميل صفحة - لا يُخزن في التخزين المحلي
let _cachedSessionId: string | null = null;

function getStoredSessionId(): string {
  if (typeof window === 'undefined') return generateSessionId();
  if (!_cachedSessionId) {
    _cachedSessionId = generateSessionId();
  }
  return _cachedSessionId;
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('ar-SA', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CopilotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId] = useState<string>(getStoredSessionId);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Auto-scroll to bottom when messages change
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Abort in-flight SSE streams on unmount to avoid leaking controllers/readers.
  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
      abortControllerRef.current = null;
    };
  }, []);

  // -------------------------------------------------------------------
  // Non-streaming fallback
  // -------------------------------------------------------------------
  const fallbackNonStreaming = useCallback(
    async (allMessages: Array<{ role: string; content: string }>, assistantId: string) => {
      const response = await fetch(`${COPILOT_API_BASE}${AI_ENDPOINTS.COPILOT_CHAT_DIRECT}`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          messages: allMessages,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail?.error_ar ||
            errorData?.detail?.error ||
            errorData?.detail ||
            `HTTP ${response.status}`
        );
      }

      const data = await response.json();
      const content = data.message?.content || '';

      setMessages((prev) =>
        prev.map((m) => (m.id === assistantId ? { ...m, content, timestamp: new Date() } : m))
      );
    },
    [sessionId]
  );

  // -------------------------------------------------------------------
  // Send message with SSE streaming
  // -------------------------------------------------------------------
  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isStreaming) return;

      setError(null);
      const userMessage: ChatMessage = {
        id: generateId(),
        role: 'user',
        content: content.trim(),
        timestamp: new Date(),
      };

      const assistantId = generateId();
      const assistantMessage: ChatMessage = {
        id: assistantId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);
      setInput('');
      setIsStreaming(true);

      // Build the request body
      const allUserMessages = [
        ...messages
          .filter((m) => m.id !== 'welcome')
          .map((m) => ({ role: m.role, content: m.content })),
        { role: 'user' as const, content: content.trim() },
      ];

      const requestBody = JSON.stringify({
        session_id: sessionId,
        messages: allUserMessages,
        stream: true,
      });

      // Use fetch with SSE for streaming
      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        const response = await fetch(`${COPILOT_API_BASE}${AI_ENDPOINTS.COPILOT_CHAT_STREAM_DIRECT}`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'text/event-stream',
          },
          body: requestBody,
          signal: controller.signal,
        });

        if (!response.ok) {
          if (response.status === 429) {
            throw new Error(
              'طلبات كثيرة جداً، يرجى الانتظار | Too many requests, please wait'
            );
          }
          const errorData = await response.json().catch(() => null);
          throw new Error(
            errorData?.detail?.error_ar ||
              errorData?.detail?.error ||
              errorData?.detail ||
              `HTTP ${response.status}`
          );
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error('No response stream');

        const decoder = new TextDecoder();
        let accumulated = '';

        try {
          while (true) {
            if (controller.signal.aborted) break;
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') break;
                accumulated += data;
                // Update the assistant message content
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantId ? { ...m, content: accumulated, timestamp: new Date() } : m
                  )
                );
              }
            }
          }
        } finally {
          // Always release the reader, including on unmount/abort.
          await reader.cancel().catch(() => {});
        }

        // If aborted mid-stream, exit silently — component is unmounting or
        // the user cleared the chat.
        if (controller.signal.aborted) {
          return;
        }

        // If we received no content, fall back to non-streaming
        if (!accumulated) {
          await fallbackNonStreaming(allUserMessages, assistantId);
        }
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === 'AbortError') {
          // User cancelled - do nothing
          return;
        }

        // Streaming failed - try non-streaming fallback

        // Try non-streaming fallback
        try {
          await fallbackNonStreaming(allUserMessages, assistantId);
        } catch (fallbackErr) {
          const errorMessage =
            fallbackErr instanceof Error ? fallbackErr.message : 'حدث خطأ في الاتصال';
          setError(errorMessage);
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? {
                    ...m,
                    content: `عذرا، حدث خطأ أثناء الاتصال بالمساعد الذكي.\n\nSorry, an error occurred while connecting to the AI assistant.\n\n_${errorMessage}_`,
                  }
                : m
            )
          );
        }
      } finally {
        setIsStreaming(false);
        abortControllerRef.current = null;
        inputRef.current?.focus();
      }
    },
    [isStreaming, messages, sessionId, fallbackNonStreaming]
  );

  // -------------------------------------------------------------------
  // Actions
  // -------------------------------------------------------------------
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const handleQuickQuestion = (question: string) => {
    sendMessage(question);
  };

  const handleClearChat = () => {
    if (isStreaming) {
      abortControllerRef.current?.abort();
    }
    setMessages([WELCOME_MESSAGE]);
    setError(null);
    setIsStreaming(false);
    // Rotate session (in-memory only, no storage persistence)
    _cachedSessionId = generateSessionId();
  };

  const handleRetry = () => {
    const lastUserMessage = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUserMessage) {
      // Remove the last assistant message
      setMessages((prev) => prev.slice(0, -1));
      sendMessage(lastUserMessage.content);
    }
  };

  // -------------------------------------------------------------------
  // Render helpers
  // -------------------------------------------------------------------
  const hasUserMessages = messages.some((m) => m.role === 'user');

  return (
    <div className="flex flex-col h-[calc(100vh-5rem)] -m-6">
      {/* Header Bar */}
      <div className="flex-shrink-0 bg-white border-b-2 border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-sahool-green-500 to-sahool-green-700 rounded-xl flex items-center justify-center shadow-sm">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">المساعد الذكي</h1>
              <p className="text-sm text-gray-500">AI Copilot</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {hasUserMessages && (
              <button
                onClick={handleClearChat}
                className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="مسح المحادثة"
              >
                <Trash2 className="w-4 h-4" />
                <span className="hidden sm:inline">مسح المحادثة</span>
              </button>
            )}
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-sahool-green-50 text-sahool-green-700 rounded-lg text-sm font-medium">
              <div className="w-2 h-2 bg-sahool-green-500 rounded-full animate-pulse" />
              <span>متصل</span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-4 bg-gray-50/50">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {/* Typing indicator */}
        {isStreaming &&
          messages[messages.length - 1]?.role === 'assistant' &&
          messages[messages.length - 1]?.content === '' && (
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-sahool-green-500 to-sahool-green-700 rounded-lg flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-white rounded-2xl rounded-tr-md px-4 py-3 border border-gray-200 shadow-sm">
                <div className="flex items-center gap-2 text-gray-500">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">جاري التفكير...</span>
                </div>
              </div>
            </div>
          )}

        {/* Error with retry */}
        {error && !isStreaming && (
          <div className="flex justify-center">
            <button
              onClick={handleRetry}
              className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 hover:bg-red-100 rounded-lg text-sm transition-colors border border-red-200"
            >
              <RotateCcw className="w-4 h-4" />
              <span>إعادة المحاولة - Retry</span>
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Questions (show only when no user messages yet) */}
      {!hasUserMessages && (
        <div className="flex-shrink-0 px-4 sm:px-6 py-3 bg-white border-t border-gray-100">
          <p className="text-xs text-gray-400 mb-2 font-medium">
            أسئلة مقترحة | Suggested questions
          </p>
          <div className="flex flex-wrap gap-2">
            {QUICK_QUESTIONS.map((q) => (
              <button
                key={q.label}
                onClick={() => handleQuickQuestion(q.label)}
                disabled={isStreaming}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-sahool-green-50 hover:bg-sahool-green-100 text-sahool-green-700 rounded-full text-sm font-medium transition-colors border border-sahool-green-200 disabled:opacity-50"
              >
                <Leaf className="w-3.5 h-3.5" />
                <span>{q.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="flex-shrink-0 bg-white border-t-2 border-gray-200 px-4 sm:px-6 py-4">
        <form onSubmit={handleSubmit} className="flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="اكتب سؤالك الزراعي هنا... | Type your agricultural question..."
              rows={1}
              disabled={isStreaming}
              className="w-full resize-none rounded-xl border-2 border-gray-200 bg-gray-50 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-sahool-green-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-sahool-green-500 transition-colors disabled:opacity-60 disabled:cursor-not-allowed text-sm sm:text-base"
              style={{ minHeight: '48px', maxHeight: '120px' }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = '48px';
                target.style.height = `${Math.min(target.scrollHeight, 120)}px`;
              }}
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isStreaming}
            className="flex-shrink-0 w-12 h-12 flex items-center justify-center bg-sahool-green-600 hover:bg-sahool-green-700 text-white rounded-xl transition-colors disabled:opacity-40 disabled:cursor-not-allowed shadow-sm"
            title="إرسال - Send"
          >
            {isStreaming ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5 rtl:-scale-x-100" />
            )}
          </button>
        </form>
        <p className="text-xs text-gray-400 mt-2 text-center">
          المساعد الذكي قد يخطئ. تحقق من المعلومات المهمة.
          <span className="mx-1">|</span>
          AI may make mistakes. Verify important information.
        </p>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// MessageBubble sub-component
// ---------------------------------------------------------------------------

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
          isUser ? 'bg-blue-600' : 'bg-gradient-to-br from-sahool-green-500 to-sahool-green-700'
        }`}
      >
        {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
      </div>

      {/* Message Content */}
      <div
        className={`max-w-[80%] sm:max-w-[70%] ${
          isUser
            ? 'bg-blue-600 text-white rounded-2xl rounded-tl-md'
            : 'bg-white text-gray-900 rounded-2xl rounded-tr-md border border-gray-200 shadow-sm'
        } px-4 py-3`}
      >
        {/* Render markdown-like content */}
        <div
          className={`text-sm sm:text-base leading-relaxed whitespace-pre-wrap break-words ${
            isUser ? 'text-white' : 'text-gray-800'
          }`}
        >
          <MessageContent content={message.content} isUser={isUser} />
        </div>

        {/* Timestamp */}
        <div className={`text-[11px] mt-1.5 ${isUser ? 'text-blue-200' : 'text-gray-400'}`}>
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// MessageContent - simple markdown rendering
// ---------------------------------------------------------------------------

function MessageContent({ content, isUser }: { content: string; isUser: boolean }) {
  if (!content) return null;

  // Split content into lines and render with basic formatting
  const lines = content.split('\n');

  return (
    <>
      {lines.map((line, i) => {
        // Horizontal rule
        if (line.trim() === '---') {
          return (
            <hr key={i} className={`my-2 ${isUser ? 'border-blue-400' : 'border-gray-200'}`} />
          );
        }

        // Heading (## or ###)
        if (line.startsWith('### ')) {
          return (
            <p key={i} className="font-bold text-base mt-2 mb-1">
              {line.slice(4)}
            </p>
          );
        }
        if (line.startsWith('## ')) {
          return (
            <p key={i} className="font-bold text-base mt-2 mb-1">
              {line.slice(3)}
            </p>
          );
        }

        // Bullet point
        if (line.startsWith('- ')) {
          return (
            <div key={i} className="flex gap-2 my-0.5">
              <span className="flex-shrink-0 mt-1.5 w-1.5 h-1.5 rounded-full bg-current opacity-60" />
              <span>{renderInline(line.slice(2), isUser)}</span>
            </div>
          );
        }

        // Numbered list
        const numberedMatch = line.match(/^(\d+)\.\s/);
        if (numberedMatch) {
          return (
            <div key={i} className="flex gap-2 my-0.5">
              <span className="flex-shrink-0 font-medium opacity-70">{numberedMatch[1]}.</span>
              <span>{renderInline(line.slice(numberedMatch[0].length), isUser)}</span>
            </div>
          );
        }

        // Empty line
        if (line.trim() === '') {
          return <div key={i} className="h-2" />;
        }

        // Regular paragraph
        return (
          <p key={i} className="my-0.5">
            {renderInline(line, isUser)}
          </p>
        );
      })}
    </>
  );
}

/**
 * Render inline markdown (bold, italic, code)
 */
function renderInline(text: string, isUser: boolean): React.ReactNode {
  const parts: React.ReactNode[] = [];
  // Match **bold**, *italic*, `code`, _italic_
  const regex = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|_(.+?)_)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    // Add preceding text
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    if (match[2]) {
      // **bold**
      parts.push(
        <strong key={match.index} className="font-bold">
          {match[2]}
        </strong>
      );
    } else if (match[3]) {
      // *italic*
      parts.push(
        <em key={match.index} className="italic">
          {match[3]}
        </em>
      );
    } else if (match[4]) {
      // `code`
      parts.push(
        <code
          key={match.index}
          className={`px-1 py-0.5 rounded text-xs font-mono ${
            isUser ? 'bg-blue-500/30 text-blue-100' : 'bg-gray-100 text-sahool-green-700'
          }`}
        >
          {match[4]}
        </code>
      );
    } else if (match[5]) {
      // _italic_
      parts.push(
        <em key={match.index} className="italic">
          {match[5]}
        </em>
      );
    }

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length > 0 ? parts : text;
}
