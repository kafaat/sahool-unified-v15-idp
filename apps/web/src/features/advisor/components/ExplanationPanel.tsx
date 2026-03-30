/**
 * ExplanationPanel Component
 * لوحة تفسير التوصيات
 *
 * Displays AI recommendation explanations with bilingual support,
 * contributing factors, confidence score, and alternatives.
 */

'use client';

import { useState } from 'react';
import type {
  Explanation,
  ContributingFactor,
  AlternativeRecommendation,
  RuleExplanation,
} from '../types/explainability';
import { ImpactLevel, FactorType } from '../types/explainability';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const IMPACT_BADGE_STYLES: Record<ImpactLevel, string> = {
  [ImpactLevel.CRITICAL]:
    'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
  [ImpactLevel.HIGH]:
    'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
  [ImpactLevel.MEDIUM]:
    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
  [ImpactLevel.LOW]:
    'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
};

const IMPACT_LABELS: Record<ImpactLevel, { en: string; ar: string }> = {
  [ImpactLevel.CRITICAL]: { en: 'Critical', ar: 'حرج' },
  [ImpactLevel.HIGH]: { en: 'High', ar: 'عالي' },
  [ImpactLevel.MEDIUM]: { en: 'Medium', ar: 'متوسط' },
  [ImpactLevel.LOW]: { en: 'Low', ar: 'منخفض' },
};

const FACTOR_ICONS: Record<FactorType, string> = {
  [FactorType.WEATHER]: '\u2601\uFE0F', // cloud
  [FactorType.SOIL]: '\uD83E\uDEA8',    // rock (soil)
  [FactorType.CROP_STAGE]: '\uD83C\uDF31', // seedling
  [FactorType.HISTORICAL]: '\uD83D\uDCCA', // chart
  [FactorType.SENSOR]: '\uD83D\uDCE1',     // satellite antenna
  [FactorType.MARKET]: '\uD83D\uDCB0',     // money bag
  [FactorType.RESOURCE]: '\uD83D\uDCA7',   // droplet
  [FactorType.CALENDAR]: '\uD83D\uDCC5',   // calendar
  [FactorType.USER_PREFERENCE]: '\u2699\uFE0F', // gear
};

const DIRECTION_COLORS: Record<string, string> = {
  supports: 'text-green-600 dark:text-green-400',
  opposes: 'text-red-600 dark:text-red-400',
  neutral: 'text-gray-500 dark:text-gray-400',
};

function confidenceColor(value: number): string {
  if (value >= 0.8) return 'bg-green-500 dark:bg-green-400';
  if (value >= 0.6) return 'bg-yellow-500 dark:bg-yellow-400';
  return 'bg-red-500 dark:bg-red-400';
}

function confidenceLabel(value: number): { en: string; ar: string } {
  if (value >= 0.8) return { en: 'High', ar: 'عالية' };
  if (value >= 0.6) return { en: 'Moderate', ar: 'متوسطة' };
  return { en: 'Low', ar: 'منخفضة' };
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const label = confidenceLabel(value);
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-700 dark:text-gray-300">
          Confidence / <span lang="ar">الثقة</span>
        </span>
        <span className="font-semibold text-gray-900 dark:text-gray-100">
          {pct}% &mdash; {label.en} / <span lang="ar">{label.ar}</span>
        </span>
      </div>
      <div className="h-2.5 w-full rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          className={`h-2.5 rounded-full transition-all ${confidenceColor(value)}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function FactorCard({ factor }: { factor: ContributingFactor }) {
  const icon = FACTOR_ICONS[factor.factorType] ?? '';
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-lg" role="img" aria-hidden="true">
            {icon}
          </span>
          <div>
            <p className="font-medium text-gray-900 dark:text-gray-100">
              {factor.name}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400" lang="ar" dir="rtl">
              {factor.nameAr}
            </p>
          </div>
        </div>
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${IMPACT_BADGE_STYLES[factor.impact]}`}
        >
          {IMPACT_LABELS[factor.impact].en} / {IMPACT_LABELS[factor.impact].ar}
        </span>
      </div>

      <div className="mt-3 space-y-1.5">
        <p className="text-sm text-gray-700 dark:text-gray-300">
          <span className="font-medium">Value:</span> {String(factor.value)}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {factor.description}
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-400" lang="ar" dir="rtl">
          {factor.descriptionAr}
        </p>
        <div className="flex items-center gap-3 pt-1 text-xs">
          <span className={DIRECTION_COLORS[factor.direction] ?? ''}>
            {factor.direction === 'supports' && 'Supports'}
            {factor.direction === 'opposes' && 'Opposes'}
            {factor.direction === 'neutral' && 'Neutral'}
          </span>
          <span className="text-gray-400 dark:text-gray-500">
            Weight: {Math.round(factor.weight * 100)}%
          </span>
          {factor.source && (
            <span className="text-gray-400 dark:text-gray-500">
              Source: {factor.source}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

function AlternativeCard({ alt }: { alt: AlternativeRecommendation }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-medium text-gray-900 dark:text-gray-100">
            {alt.title}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400" lang="ar" dir="rtl">
            {alt.titleAr}
          </p>
        </div>
        <span className="shrink-0 rounded bg-gray-200 px-2 py-0.5 text-xs font-semibold text-gray-700 dark:bg-gray-700 dark:text-gray-300">
          Score: {alt.score}
        </span>
      </div>

      <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
        {alt.description}
      </p>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400" lang="ar" dir="rtl">
        {alt.descriptionAr}
      </p>

      {alt.rejectionReasons.length > 0 && (
        <div className="mt-3">
          <p className="text-xs font-medium text-red-600 dark:text-red-400">
            Not selected because:
          </p>
          <ul className="mt-1 list-inside list-disc text-xs text-gray-600 dark:text-gray-400">
            {alt.rejectionReasons.map((reason, i) => (
              <li key={i}>{reason}</li>
            ))}
          </ul>
        </div>
      )}

      {(alt.pros.length > 0 || alt.cons.length > 0) && (
        <div className="mt-3 grid grid-cols-2 gap-2">
          {alt.pros.length > 0 && (
            <div>
              <p className="text-xs font-medium text-green-600 dark:text-green-400">
                Pros
              </p>
              <ul className="mt-1 list-inside list-disc text-xs text-gray-600 dark:text-gray-400">
                {alt.pros.map((pro, i) => (
                  <li key={i}>{pro}</li>
                ))}
              </ul>
            </div>
          )}
          {alt.cons.length > 0 && (
            <div>
              <p className="text-xs font-medium text-red-600 dark:text-red-400">
                Cons
              </p>
              <ul className="mt-1 list-inside list-disc text-xs text-gray-600 dark:text-gray-400">
                {alt.cons.map((con, i) => (
                  <li key={i}>{con}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function RuleCard({ rule }: { rule: RuleExplanation }) {
  if (!rule.matched) return null;
  return (
    <div className="rounded-lg border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-900/20">
      <p className="text-sm font-medium text-blue-900 dark:text-blue-200">
        {rule.ruleName}
      </p>
      <p className="text-xs text-blue-700 dark:text-blue-300" lang="ar" dir="rtl">
        {rule.ruleNameAr}
      </p>
      <p className="mt-1.5 text-sm text-gray-700 dark:text-gray-300">
        {rule.action}
      </p>
      <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
        Condition: {rule.condition}
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// ChevronIcon (inline SVG to avoid external dependency)
// ---------------------------------------------------------------------------

function ChevronIcon({ open }: { open: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={`h-5 w-5 transition-transform ${open ? 'rotate-180' : ''}`}
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
    >
      <path
        fillRule="evenodd"
        d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
        clipRule="evenodd"
      />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export interface ExplanationPanelProps {
  explanation: Explanation;
  /** When true the details section starts expanded. Defaults to false. */
  defaultOpen?: boolean;
  className?: string;
}

export function ExplanationPanel({
  explanation,
  defaultOpen = false,
  className = '',
}: ExplanationPanelProps) {
  const [detailsOpen, setDetailsOpen] = useState(defaultOpen);

  const matchedRules = explanation.rules.filter((r) => r.matched);

  return (
    <section
      className={`rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-900 ${className}`}
    >
      {/* ---- Header ---- */}
      <div className="border-b border-gray-200 px-5 py-4 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Why This Recommendation?
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400" lang="ar" dir="rtl">
          لماذا هذه التوصية؟
        </p>
      </div>

      {/* ---- Summary ---- */}
      <div className="space-y-4 px-5 py-4">
        <div className="space-y-1.5">
          <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
            {explanation.summary}
          </p>
          <p
            className="text-sm leading-relaxed text-gray-500 dark:text-gray-400"
            lang="ar"
            dir="rtl"
          >
            {explanation.summaryAr}
          </p>
        </div>

        {/* Confidence bar */}
        <ConfidenceBar value={explanation.overallConfidence} />
      </div>

      {/* ---- Contributing Factors ---- */}
      {explanation.factors.length > 0 && (
        <div className="border-t border-gray-200 px-5 py-4 dark:border-gray-700">
          <h4 className="mb-3 text-sm font-semibold text-gray-900 dark:text-gray-100">
            Contributing Factors /{' '}
            <span lang="ar">العوامل المساهمة</span>
          </h4>
          <div className="grid gap-3 sm:grid-cols-2">
            {explanation.factors.map((factor, idx) => (
              <FactorCard key={idx} factor={factor} />
            ))}
          </div>
        </div>
      )}

      {/* ---- Alternatives ---- */}
      {explanation.alternatives.length > 0 && (
        <div className="border-t border-gray-200 px-5 py-4 dark:border-gray-700">
          <h4 className="mb-3 text-sm font-semibold text-gray-900 dark:text-gray-100">
            Alternatives Considered /{' '}
            <span lang="ar">البدائل المدروسة</span>
          </h4>
          <div className="grid gap-3">
            {explanation.alternatives.map((alt, idx) => (
              <AlternativeCard key={idx} alt={alt} />
            ))}
          </div>
        </div>
      )}

      {/* ---- Collapsible Details ---- */}
      <div className="border-t border-gray-200 dark:border-gray-700">
        <button
          type="button"
          onClick={() => setDetailsOpen((prev) => !prev)}
          className="flex w-full items-center justify-between px-5 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-800"
        >
          <span>
            Details / <span lang="ar">التفاصيل</span>
          </span>
          <ChevronIcon open={detailsOpen} />
        </button>

        {detailsOpen && (
          <div className="space-y-4 px-5 pb-5">
            {/* Rules */}
            {matchedRules.length > 0 && (
              <div>
                <h5 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  Applied Rules / <span lang="ar">القواعد المطبقة</span>
                </h5>
                <div className="grid gap-2">
                  {matchedRules.map((rule, idx) => (
                    <RuleCard key={idx} rule={rule} />
                  ))}
                </div>
              </div>
            )}

            {/* Uncertainty reasons */}
            {explanation.uncertaintyReasons.length > 0 && (
              <div>
                <h5 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  Uncertainty / <span lang="ar">عدم اليقين</span>
                </h5>
                <ul className="list-inside list-disc space-y-1 text-sm text-gray-600 dark:text-gray-400">
                  {explanation.uncertaintyReasons.map((reason, i) => (
                    <li key={i}>{reason}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Data sources */}
            {explanation.dataSources.length > 0 && (
              <div>
                <h5 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  Data Sources / <span lang="ar">مصادر البيانات</span>
                </h5>
                <div className="flex flex-wrap gap-2">
                  {explanation.dataSources.map((src, i) => (
                    <span
                      key={i}
                      className="rounded-full bg-gray-100 px-3 py-0.5 text-xs text-gray-700 dark:bg-gray-700 dark:text-gray-300"
                    >
                      {src}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Detailed explanation (markdown-like plain text) */}
            {explanation.detailedExplanation && (
              <div>
                <h5 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  Full Explanation
                </h5>
                <pre className="whitespace-pre-wrap rounded-lg bg-gray-50 p-3 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-300">
                  {explanation.detailedExplanation}
                </pre>
              </div>
            )}
            {explanation.detailedExplanationAr && (
              <div>
                <h5 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  <span lang="ar">الشرح التفصيلي</span>
                </h5>
                <pre
                  className="whitespace-pre-wrap rounded-lg bg-gray-50 p-3 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-300"
                  lang="ar"
                  dir="rtl"
                >
                  {explanation.detailedExplanationAr}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
