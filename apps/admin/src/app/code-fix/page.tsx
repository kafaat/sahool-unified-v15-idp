'use client';

/**
 * Code Fix Agent Page — Developer Platform Tool
 * صفحة وكيل إصلاح الكود — أداة مطوري المنصة
 *
 * Admin-only: Protected by route-protection.ts
 * Connects to: code-fix-agent (port 8162) via /api/code-fix proxy
 */

import { useCallback, useEffect, useState } from 'react';
import Header from '@/components/layout/Header';
import {
  Bug,
  FileCode2,
  Loader2,
  Send,
  CheckCircle2,
  XCircle,
  Shield,
  Zap,
  Cpu,
  Code2,
  TestTube2,
} from 'lucide-react';

// ─── Types ──────────────────────────────────────────────────────────────────

interface AgentResponse {
  success: boolean;
  action_type: string;
  data: Record<string, unknown> | null;
  confidence?: number;
  reasoning?: string;
  reasoning_ar?: string;
  response_time_ms?: number;
  agent_id?: string;
}

interface AgentInfo {
  agent_id: string;
  name: string;
  name_ar: string;
  version: string;
  status: string;
  total_requests: number;
  success_rate?: number;
}

type ActionType = 'analyze' | 'fix' | 'generate-tests';

const LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'dart', label: 'Dart / Flutter' },
  { value: 'go', label: 'Go' },
  { value: 'yaml', label: 'YAML' },
  { value: 'sql', label: 'SQL' },
];

const ACTIONS: { value: ActionType; label: string; labelAr: string; icon: typeof Bug }[] = [
  { value: 'analyze', label: 'Analyze', labelAr: 'تحليل', icon: Bug },
  { value: 'fix', label: 'Fix', labelAr: 'إصلاح', icon: Zap },
  { value: 'generate-tests', label: 'Generate Tests', labelAr: 'توليد اختبارات', icon: TestTube2 },
];

// ─── Component ──────────────────────────────────────────────────────────────

export default function CodeFixPage() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [action, setAction] = useState<ActionType>('analyze');
  const [errors, setErrors] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AgentResponse | null>(null);
  const [agentInfo, setAgentInfo] = useState<AgentInfo | null>(null);
  const [healthy, setHealthy] = useState<boolean | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      const res = await fetch('/api/code-fix?action=health');
      setHealthy(res.ok);
    } catch {
      setHealthy(false);
    }
  }, []);

  const fetchAgentInfo = useCallback(async () => {
    try {
      const res = await fetch('/api/code-fix?action=info');
      if (res.ok) {
        setAgentInfo(await res.json());
      }
    } catch {
      // non-critical
    }
  }, []);

  useEffect(() => {
    checkHealth();
    fetchAgentInfo();
  }, [checkHealth, fetchAgentInfo]);

  const handleSubmit = async () => {
    if (!code.trim()) return;
    setLoading(true);
    setResult(null);
    setSubmitError(null);

    try {
      const body: Record<string, unknown> = { action, code, language };

      if (action === 'fix') {
        // Parse errors textarea as JSON array or plain text lines
        let parsedErrors: unknown[];
        try {
          parsedErrors = JSON.parse(errors || '[]');
        } catch {
          parsedErrors = errors
            .split('\n')
            .filter(Boolean)
            .map((line) => ({ message: line, severity: 'error' }));
        }
        body.errors = parsedErrors;
      }

      if (action === 'generate-tests') {
        body.framework = language === 'python' ? 'pytest' : 'vitest';
        body.coverage_target = 80;
      }

      const res = await fetch('/api/code-fix', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || `HTTP ${res.status}`);
      }

      setResult(await res.json());
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'فشل العملية');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <Header title="وكيل إصلاح الكود" subtitle="Code Fix Agent — Developer Platform Tool" />

      {/* Agent Info & Health */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${healthy ? 'bg-green-100' : healthy === false ? 'bg-red-100' : 'bg-gray-100'}`}>
              <Cpu className={`w-5 h-5 ${healthy ? 'text-green-600' : healthy === false ? 'text-red-600' : 'text-gray-400'}`} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {healthy ? 'متصل' : healthy === false ? 'غير متصل' : 'جارٍ الفحص...'}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">حالة الخدمة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Code2 className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {agentInfo?.version || '—'}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">إصدار الوكيل</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <FileCode2 className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {agentInfo?.total_requests?.toLocaleString('ar-SA') || '0'}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">إجمالي الطلبات</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {agentInfo?.status || '—'}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">حالة الوكيل</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Panel */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">إدخال الكود</h3>

          {/* Action selector */}
          <div className="flex gap-2 mb-4">
            {ACTIONS.map((a) => {
              const Icon = a.icon;
              return (
                <button
                  key={a.value}
                  onClick={() => setAction(a.value)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm border transition-colors ${
                    action === a.value
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {a.labelAr}
                </button>
              );
            })}
          </div>

          {/* Language selector */}
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full mb-4 px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-sm text-gray-900 dark:text-gray-100"
          >
            {LANGUAGES.map((l) => (
              <option key={l.value} value={l.value}>{l.label}</option>
            ))}
          </select>

          {/* Code input */}
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="الصق الكود هنا..."
            rows={14}
            className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-sm font-mono text-gray-900 dark:text-gray-100 resize-y"
            dir="ltr"
          />

          {/* Errors input (for fix action) */}
          {action === 'fix' && (
            <textarea
              value={errors}
              onChange={(e) => setErrors(e.target.value)}
              placeholder='أخطاء (سطر لكل خطأ أو JSON)...\nمثال: E501 line too long\nTypeError: x is not a function'
              rows={4}
              className="w-full mt-3 px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-sm font-mono text-gray-900 dark:text-gray-100 resize-y"
              dir="ltr"
            />
          )}

          {/* Submit */}
          <button
            onClick={handleSubmit}
            disabled={loading || !code.trim() || !healthy}
            className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                جارٍ المعالجة...
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                {action === 'analyze' ? 'تحليل الكود' : action === 'fix' ? 'إصلاح الكود' : 'توليد اختبارات'}
              </>
            )}
          </button>
        </div>

        {/* Results Panel */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">النتائج</h3>
            {result?.response_time_ms && (
              <span className="text-xs text-gray-400">{result.response_time_ms}ms</span>
            )}
          </div>

          {submitError && (
            <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg mb-4">
              <XCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <p className="text-sm text-red-700 dark:text-red-300">{submitError}</p>
            </div>
          )}

          {!result && !submitError && (
            <div className="text-center py-16">
              <FileCode2 className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400 text-sm">
                أدخل الكود واختر إجراء لعرض النتائج
              </p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {/* Status badge */}
              <div className="flex items-center gap-3">
                {result.success ? (
                  <span className="flex items-center gap-1.5 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                    <CheckCircle2 className="w-4 h-4" /> نجاح
                  </span>
                ) : (
                  <span className="flex items-center gap-1.5 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm">
                    <XCircle className="w-4 h-4" /> فشل
                  </span>
                )}
                {result.confidence != null && (
                  <span className="text-sm text-gray-500">
                    الثقة: {(result.confidence * 100).toFixed(0)}%
                  </span>
                )}
              </div>

              {/* Reasoning */}
              {(result.reasoning_ar || result.reasoning) && (
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    {result.reasoning_ar || result.reasoning}
                  </p>
                </div>
              )}

              {/* Data output */}
              {result.data && (
                <div className="border border-gray-200 dark:border-gray-600 rounded-lg overflow-hidden">
                  <div className="bg-gray-50 dark:bg-gray-700/50 px-3 py-2 text-xs text-gray-500 dark:text-gray-400">
                    {result.action_type} — {result.agent_id}
                  </div>
                  <pre
                    className="p-3 text-xs font-mono text-gray-800 dark:text-gray-200 overflow-auto max-h-[400px]"
                    dir="ltr"
                  >
                    {JSON.stringify(result.data, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
