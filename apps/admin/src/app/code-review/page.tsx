'use client';

/**
 * Code Review Operator Dashboard
 * لوحة تشغيل مراجعات الكود
 */

import { useEffect, useState, useMemo, useCallback, Suspense } from 'react';
import Header from '@/components/layout/Header';
import {
  FileCode2,
  Shield,
  AlertTriangle,
  Gauge,
  RefreshCw,
  Send,
  Loader2,
  CheckCircle2,
  XCircle,
  Database,
  Cpu,
  ChevronDown,
  ChevronUp,
  Trash2,
  Leaf,
} from 'lucide-react';

// ─── Types ───────────────────────────────────────────────────────────────────

interface ReviewResponse {
  summary: string;
  critical_issues: string[];
  suggestions: string[];
  security_concerns: string[];
  agricultural_issues: string[];
  score: number;
  model_used: string | null;
  cached: boolean;
}

interface ModelInfo {
  name: string;
  url: string;
  available: boolean;
  priority: number;
}

interface HealthStatus {
  status: 'healthy' | 'degraded';
  service: string;
  ollama_connected: boolean;
  available_models: string[];
  cache_enabled: boolean;
  github_enabled: boolean;
  version: string;
}

interface CacheStats {
  backend: string;
  size: number | null;
  hits: number;
  misses: number;
  hit_rate: string;
}

// ─── API Helpers ─────────────────────────────────────────────────────────────

const CODE_REVIEW_API = '/api/code-review';

async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${CODE_REVIEW_API}?action=health`);
  if (!res.ok) throw new Error('Service unavailable');
  return res.json();
}

async function fetchModels(): Promise<ModelInfo[]> {
  const res = await fetch(`${CODE_REVIEW_API}?action=models`);
  if (!res.ok) throw new Error('Failed to fetch models');
  return res.json();
}

async function fetchCacheStats(): Promise<CacheStats> {
  const res = await fetch(`${CODE_REVIEW_API}?action=cache`);
  if (!res.ok) throw new Error('Failed to fetch cache stats');
  return res.json();
}

async function clearCache(): Promise<void> {
  const res = await fetch(CODE_REVIEW_API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'clear_cache' }),
  });
  if (!res.ok) throw new Error('Failed to clear cache');
}

async function submitReview(
  code: string,
  language?: string,
  filename?: string,
  model?: string
): Promise<ReviewResponse> {
  const res = await fetch(CODE_REVIEW_API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'review', code, language, filename, model, use_cache: true }),
  });
  if (!res.ok) throw new Error('Review failed');
  return res.json();
}

// ─── Score Badge ─────────────────────────────────────────────────────────────

function ScoreBadge({ score }: { score: number }) {
  const color =
    score >= 80
      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
      : score >= 60
        ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
        : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium ${color}`}
    >
      {score}/100
    </span>
  );
}

// ─── Stat Card ───────────────────────────────────────────────────────────────

function StatCard({
  icon: Icon,
  value,
  label,
  labelAr,
  color,
}: {
  icon: React.ElementType;
  value: string | number;
  label: string;
  labelAr: string;
  color: string;
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 ${color} rounded-lg flex items-center justify-center`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{value}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400" title={label}>
            {labelAr}
          </p>
        </div>
      </div>
    </div>
  );
}

// ─── Issue List ──────────────────────────────────────────────────────────────

function IssueList({
  title,
  titleAr,
  items,
  icon: Icon,
  color,
}: {
  title: string;
  titleAr: string;
  items: string[];
  icon: React.ElementType;
  color: string;
}) {
  if (items.length === 0) return null;

  return (
    <div className="mt-4">
      <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
        <Icon className={`w-4 h-4 ${color}`} />
        {titleAr} ({items.length}) — {title}
      </h4>
      <ul className="space-y-1">
        {items.map((item, i) => (
          <li
            key={i}
            className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/50 rounded px-3 py-1.5"
          >
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

// ─── Main Content ────────────────────────────────────────────────────────────

const LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'dart', label: 'Dart' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
  { value: 'yaml', label: 'YAML' },
  { value: 'sql', label: 'SQL' },
];

function CodeReviewContent() {
  // Service state
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null);
  const [serviceError, setServiceError] = useState<string | null>(null);

  // Review form
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [filename, setFilename] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Review results
  const [reviews, setReviews] = useState<
    (ReviewResponse & { filename: string; language: string; timestamp: Date })[]
  >([]);
  const [expandedReview, setExpandedReview] = useState<number | null>(null);

  // Load service info
  const loadServiceInfo = useCallback(async () => {
    setServiceError(null);
    try {
      const [h, m, c] = await Promise.all([fetchHealth(), fetchModels(), fetchCacheStats()]);
      setHealth(h);
      setModels(m);
      setCacheStats(c);
    } catch {
      setServiceError('تعذر الاتصال بخدمة مراجعة الكود — Service unavailable');
    }
  }, []);

  useEffect(() => {
    loadServiceInfo();
  }, [loadServiceInfo]);

  // Submit review
  const handleSubmit = async () => {
    if (!code.trim()) return;
    setIsSubmitting(true);
    try {
      const result = await submitReview(
        code,
        language,
        filename || undefined,
        selectedModel || undefined
      );
      setReviews((prev) => [
        { ...result, filename: filename || 'untitled', language, timestamp: new Date() },
        ...prev,
      ]);
      setExpandedReview(0);
    } catch {
      setServiceError('فشل في إرسال المراجعة — Review submission failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Clear cache
  const handleClearCache = async () => {
    try {
      await clearCache();
      const c = await fetchCacheStats();
      setCacheStats(c);
    } catch {
      // ignore
    }
  };

  // Computed stats
  const avgScore = useMemo(() => {
    if (reviews.length === 0) return 0;
    return Math.round(reviews.reduce((s, r) => s + r.score, 0) / reviews.length);
  }, [reviews]);

  const totalIssues = useMemo(() => {
    return reviews.reduce(
      (s, r) =>
        s +
        r.critical_issues.length +
        r.suggestions.length +
        r.security_concerns.length +
        r.agricultural_issues.length,
      0
    );
  }, [reviews]);

  const availableModels = models.filter((m) => m.available);

  return (
    <div className="p-6">
      <Header title="مراجعات الكود" subtitle="Code Review Operator" />

      {/* Service Error */}
      {serviceError && (
        <div className="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center gap-3">
          <XCircle className="w-5 h-5 text-red-500 shrink-0" />
          <p className="text-sm text-red-700 dark:text-red-300">{serviceError}</p>
          <button onClick={loadServiceInfo} className="ml-auto text-red-600 hover:text-red-800">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={FileCode2}
          value={reviews.length}
          label="Reviews"
          labelAr="مراجعات"
          color="bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400"
        />
        <StatCard
          icon={Gauge}
          value={avgScore ? `${avgScore}%` : '—'}
          label="Avg Score"
          labelAr="متوسط التقييم"
          color="bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400"
        />
        <StatCard
          icon={AlertTriangle}
          value={totalIssues}
          label="Issues Found"
          labelAr="مشاكل مكتشفة"
          color="bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400"
        />
        <StatCard
          icon={Cpu}
          value={availableModels.length}
          label="Models Available"
          labelAr="نماذج متاحة"
          color="bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400"
        />
      </div>

      {/* Service Status Bar */}
      {health && (
        <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
          <span className="flex items-center gap-1">
            <span
              className={`w-2 h-2 rounded-full ${health.status === 'healthy' ? 'bg-green-500' : 'bg-amber-500'}`}
            />
            {health.status === 'healthy' ? 'متصل' : 'متدهور'} — v{health.version}
          </span>
          <span>Ollama: {health.ollama_connected ? '✓' : '✗'}</span>
          <span>Cache: {health.cache_enabled ? '✓' : '✗'}</span>
          <span>GitHub: {health.github_enabled ? '✓' : '✗'}</span>
          {cacheStats && (
            <span className="flex items-center gap-1">
              <Database className="w-3 h-3" />
              Hit rate: {cacheStats.hit_rate} ({cacheStats.backend})
              <button
                onClick={handleClearCache}
                title="مسح الكاش"
                className="text-gray-400 hover:text-red-500"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </span>
          )}
          <button
            onClick={loadServiceInfo}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <RefreshCw className="w-3 h-3" />
          </button>
        </div>
      )}

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Review Form */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-4">
            إرسال مراجعة جديدة — Submit Review
          </h3>

          {/* Language + Filename */}
          <div className="flex gap-3 mb-3">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm"
            >
              {LANGUAGES.map((l) => (
                <option key={l.value} value={l.value}>
                  {l.label}
                </option>
              ))}
            </select>
            <input
              type="text"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              placeholder="اسم الملف (اختياري)"
              className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm"
            />
          </div>

          {/* Model selector */}
          {availableModels.length > 0 && (
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full mb-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm"
            >
              <option value="">نموذج تلقائي — Auto</option>
              {availableModels.map((m) => (
                <option key={m.name} value={m.name}>
                  {m.name} (priority: {m.priority})
                </option>
              ))}
            </select>
          )}

          {/* Code textarea */}
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="الصق الكود هنا للمراجعة...&#10;Paste code here for review..."
            rows={14}
            className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 px-3 py-2 text-sm font-mono resize-y"
            dir="ltr"
          />

          <button
            onClick={handleSubmit}
            disabled={isSubmitting || !code.trim()}
            className="mt-3 w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white py-2.5 text-sm font-medium transition-colors"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                جاري المراجعة...
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                إرسال للمراجعة — Submit
              </>
            )}
          </button>
        </div>

        {/* Right: Review Results */}
        <div className="space-y-4">
          {reviews.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
              <FileCode2 className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                لا توجد مراجعات بعد
              </h3>
              <p className="text-gray-500 dark:text-gray-400 text-sm">
                Submit code on the left to get AI-powered code reviews
              </p>
            </div>
          ) : (
            reviews.map((review, idx) => {
              const isExpanded = expandedReview === idx;
              return (
                <div
                  key={idx}
                  className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden"
                >
                  {/* Review header */}
                  <button
                    onClick={() => setExpandedReview(isExpanded ? null : idx)}
                    className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors text-left"
                  >
                    <div className="flex items-center gap-3">
                      <ScoreBadge score={review.score} />
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {review.filename}
                          <span className="text-gray-400 mx-1">·</span>
                          <span className="text-gray-500">{review.language}</span>
                        </p>
                        <p className="text-xs text-gray-400 mt-0.5 line-clamp-1">
                          {review.summary}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {review.cached && (
                        <span className="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded">
                          cached
                        </span>
                      )}
                      {review.model_used && (
                        <span className="text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 px-2 py-0.5 rounded">
                          {review.model_used}
                        </span>
                      )}
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  </button>

                  {/* Expanded content */}
                  {isExpanded && (
                    <div className="border-t border-gray-100 dark:border-gray-700 px-4 pb-4">
                      <p className="mt-3 text-sm text-gray-700 dark:text-gray-300">
                        {review.summary}
                      </p>

                      <IssueList
                        title="Critical Issues"
                        titleAr="مشاكل حرجة"
                        items={review.critical_issues}
                        icon={XCircle}
                        color="text-red-500"
                      />
                      <IssueList
                        title="Security Concerns"
                        titleAr="مخاوف أمنية"
                        items={review.security_concerns}
                        icon={Shield}
                        color="text-orange-500"
                      />
                      <IssueList
                        title="Agricultural Issues"
                        titleAr="مشاكل زراعية"
                        items={review.agricultural_issues}
                        icon={Leaf}
                        color="text-green-500"
                      />
                      <IssueList
                        title="Suggestions"
                        titleAr="اقتراحات"
                        items={review.suggestions}
                        icon={CheckCircle2}
                        color="text-blue-500"
                      />
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Page Export ──────────────────────────────────────────────────────────────

export default function CodeReviewPage() {
  return (
    <Suspense
      fallback={
        <div className="p-6 flex items-center justify-center min-h-[60vh]">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      }
    >
      <CodeReviewContent />
    </Suspense>
  );
}
