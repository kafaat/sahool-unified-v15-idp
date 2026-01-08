'use client';

/**
 * Living Field Card Component
 * مكون بطاقة الحقل الحي
 *
 * Displays a comprehensive health score for a field with:
 * - Circular progress indicator for overall score
 * - Four smaller indicators for sub-scores
 * - Trend arrow (up/down/stable)
 * - Alert badges with count
 * - Expandable recommendations section
 * - Animated transitions
 * - Tooltip explanations for each score
 * - Color coding: green (>70), yellow (40-70), red (<40)
 */

import React, { useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Droplets,
  Heart,
  Eye,
  Moon,
  Info,
} from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useLivingFieldScore, type FieldAlert, type Recommendation, type LivingFieldScore } from '../hooks/useLivingFieldScore';

type TrendType = LivingFieldScore['trend'];

interface LivingFieldCardProps {
  fieldId: string;
  fieldName?: string;
  fieldNameAr?: string;
}

/**
 * Get color class based on score
 */
function getScoreColor(score: number): {
  border: string;
  bg: string;
  text: string;
  fill: string;
} {
  if (score >= 70) {
    return {
      border: 'border-green-500',
      bg: 'bg-green-50',
      text: 'text-green-700',
      fill: 'stroke-green-500',
    };
  }
  if (score >= 40) {
    return {
      border: 'border-yellow-500',
      bg: 'bg-yellow-50',
      text: 'text-yellow-700',
      fill: 'stroke-yellow-500',
    };
  }
  return {
    border: 'border-red-500',
    bg: 'bg-red-50',
    text: 'text-red-700',
    fill: 'stroke-red-500',
  };
}

/**
 * Get trend icon and color
 */
function getTrendIcon(trend: TrendType): {
  icon: React.ReactNode;
  color: string;
  label: string;
  labelAr: string;
} {
  switch (trend) {
    case 'improving':
      return {
        icon: <TrendingUp className="w-5 h-5" />,
        color: 'text-green-600',
        label: 'Improving',
        labelAr: 'يتحسن',
      };
    case 'declining':
      return {
        icon: <TrendingDown className="w-5 h-5" />,
        color: 'text-red-600',
        label: 'Declining',
        labelAr: 'يتراجع',
      };
    default:
      return {
        icon: <Minus className="w-5 h-5" />,
        color: 'text-gray-600',
        label: 'Stable',
        labelAr: 'مستقر',
      };
  }
}

/**
 * Get alert severity badge variant
 */
function getAlertVariant(severity: string): 'default' | 'success' | 'warning' | 'danger' {
  switch (severity) {
    case 'critical':
    case 'emergency':
      return 'danger';
    case 'warning':
      return 'warning';
    case 'info':
    default:
      return 'default';
  }
}

/**
 * Circular progress indicator component
 */
interface CircularProgressProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  label: string;
  labelAr: string;
  icon?: React.ReactNode;
  showTooltip?: boolean;
}

const CircularProgress: React.FC<CircularProgressProps> = ({
  score,
  size = 120,
  strokeWidth = 8,
  label,
  labelAr,
  icon,
  showTooltip = false,
}) => {
  const [showInfo, setShowInfo] = useState(false);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;
  const colors = getScoreColor(score);

  return (
    <div className="relative inline-flex flex-col items-center">
      <div
        className="relative group"
        onMouseEnter={() => setShowInfo(true)}
        onMouseLeave={() => setShowInfo(false)}
      >
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="none"
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className={`${colors.fill} transition-all duration-1000 ease-out`}
            strokeLinecap="round"
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {icon && <div className="mb-1">{icon}</div>}
          <span className={`text-2xl font-bold ${colors.text}`}>{score}</span>
        </div>

        {/* Tooltip */}
        {showTooltip && showInfo && (
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg whitespace-nowrap z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            {label}
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
              <div className="border-4 border-transparent border-t-gray-900" />
            </div>
          </div>
        )}
      </div>

      {/* Label */}
      <span className="mt-2 text-sm font-medium text-gray-700 text-center">
        {labelAr}
      </span>
    </div>
  );
};

/**
 * Sub-score indicator component
 */
interface SubScoreProps {
  score: number;
  icon: React.ReactNode;
  label: string;
  labelAr: string;
}

const SubScore: React.FC<SubScoreProps> = ({ score, icon, label, labelAr }) => {
  const [showInfo, setShowInfo] = useState(false);
  const colors = getScoreColor(score);

  return (
    <div
      className="relative flex flex-col items-center p-3 rounded-lg border-2 transition-all duration-200 hover:shadow-md cursor-help"
      style={{ borderColor: colors.border.replace('border-', '') }}
      onMouseEnter={() => setShowInfo(true)}
      onMouseLeave={() => setShowInfo(false)}
    >
      <div className={`${colors.text} mb-2`}>{icon}</div>
      <span className={`text-xl font-bold ${colors.text}`}>{score}</span>
      <span className="text-xs text-gray-600 mt-1 text-center">{labelAr}</span>

      {/* Tooltip */}
      {showInfo && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg whitespace-nowrap z-10 opacity-0 hover:opacity-100 transition-opacity duration-200 pointer-events-none">
          {label}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
            <div className="border-4 border-transparent border-t-gray-900" />
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Alert item component
 */
const AlertItem: React.FC<{ alert: FieldAlert }> = ({ alert }) => {
  return (
    <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
      <AlertCircle className={`w-5 h-5 mt-0.5 flex-shrink-0 ${
        alert.severity === 'critical' || alert.severity === 'emergency' ? 'text-red-600' :
        alert.severity === 'warning' ? 'text-yellow-600' :
        'text-gray-600'
      }`} />
      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-gray-900 text-sm">{alert.titleAr}</h4>
        <p className="text-xs text-gray-600 mt-1">{alert.messageAr || alert.message}</p>
      </div>
      <Badge variant={getAlertVariant(alert.severity)} size="sm">
        {alert.severity}
      </Badge>
    </div>
  );
};

/**
 * Recommendation item component
 */
const RecommendationItem: React.FC<{ recommendation: Recommendation }> = ({ recommendation }) => {
  const priorityColorMap: Record<string, string> = {
    urgent: 'border-l-red-500 bg-red-50',
    high: 'border-l-orange-500 bg-orange-50',
    medium: 'border-l-yellow-500 bg-yellow-50',
    low: 'border-l-blue-500 bg-blue-50',
  };

  const priorityColors = priorityColorMap[recommendation.priority] || 'border-l-gray-500 bg-gray-50';

  return (
    <div className={`border-l-4 p-3 rounded-r-lg ${priorityColors}`}>
      <div className="flex items-start gap-2">
        <div className="flex-shrink-0 mt-1">
          <Info className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-gray-900 text-sm">{recommendation.titleAr || recommendation.title}</h4>
          <p className="text-xs text-gray-600 mt-1">{recommendation.descriptionAr || recommendation.description}</p>
          {recommendation.actionItems && recommendation.actionItems.length > 0 && (
            <ul className="text-xs text-gray-500 mt-2 list-disc list-inside">
              {recommendation.actionItems.slice(0, 3).map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          )}
        </div>
        <Badge size="sm" variant={
          recommendation.priority === 'urgent' || recommendation.priority === 'high' ? 'danger' :
          recommendation.priority === 'medium' ? 'warning' :
          'default'
        }>
          {recommendation.priority === 'urgent' ? 'عاجل' :
           recommendation.priority === 'high' ? 'عالي' :
           recommendation.priority === 'medium' ? 'متوسط' : 'منخفض'}
        </Badge>
      </div>
    </div>
  );
};

/**
 * Main Living Field Card Component
 */
export const LivingFieldCard: React.FC<LivingFieldCardProps> = ({
  fieldId,
  fieldName,
  fieldNameAr,
}) => {
  const [expandedRecommendations, setExpandedRecommendations] = useState(false);
  const { data: scoreData, isLoading, isError } = useLivingFieldScore(fieldId);

  if (isLoading || !scoreData) {
    return (
      <Card variant="elevated" className="animate-pulse">
        <CardHeader>
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-2" />
          <div className="h-4 bg-gray-200 rounded w-1/2" />
        </CardHeader>
        <CardContent>
          <div className="flex justify-center mb-6">
            <div className="w-32 h-32 bg-gray-200 rounded-full" />
          </div>
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-24 bg-gray-200 rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isError) {
    return (
      <Card variant="elevated">
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <AlertCircle className="w-12 h-12 text-red-500 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              خطأ في تحميل البيانات
            </h3>
            <p className="text-sm text-gray-600">حدث خطأ أثناء تحميل بيانات الحقل</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const score = scoreData;
  const trendInfo = getTrendIcon(score.trend);

  return (
    <Card variant="elevated" className="overflow-hidden">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900">
              {fieldNameAr || fieldName || 'الحقل الحي'}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              {fieldName && fieldNameAr ? fieldName : 'Living Field Score'}
            </p>
          </div>

          {/* Trend indicator */}
          <div className={`flex items-center gap-2 ${trendInfo.color}`}>
            {trendInfo.icon}
            <span className="text-sm font-medium">{trendInfo.labelAr}</span>
          </div>
        </div>

        {/* Alerts summary */}
        {score.alerts.length > 0 && (
          <div className="mt-3 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-orange-600" />
            <span className="text-sm text-gray-700">
              {score.alerts.length} {score.alerts.length === 1 ? 'تنبيه' : 'تنبيهات'}
            </span>
          </div>
        )}
      </CardHeader>

      <CardContent>
        {/* Overall Score - Large Circular Progress */}
        <div className="flex justify-center mb-8">
          <CircularProgress
            score={score.overall}
            size={140}
            strokeWidth={12}
            label="Overall Field Health Score"
            labelAr="النقاط الإجمالية"
            showTooltip
          />
        </div>

        {/* Sub-scores Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <SubScore
            score={score.health}
            icon={<Heart className="w-5 h-5" />}
            label="Health Score (from NDVI)"
            labelAr="الصحة"
          />
          <SubScore
            score={score.hydration}
            icon={<Droplets className="w-5 h-5" />}
            label="Hydration Score"
            labelAr="الترطيب"
          />
          <SubScore
            score={score.attention}
            icon={<Eye className="w-5 h-5" />}
            label="Attention Score (from tasks)"
            labelAr="الاهتمام"
          />
          <SubScore
            score={score.astral}
            icon={<Moon className="w-5 h-5" />}
            label="Astral Score (from calendar)"
            labelAr="الفلكي"
          />
        </div>

        {/* Color Legend */}
        <div className="flex items-center justify-center gap-6 mb-6 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-gray-600">ممتاز (&gt;70)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-gray-600">متوسط (40-70)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-gray-600">ضعيف (&lt;40)</span>
          </div>
        </div>

        {/* Alerts Section */}
        {score.alerts.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              التنبيهات
            </h3>
            <div className="space-y-2">
              {score.alerts.map((alert) => (
                <AlertItem key={alert.id} alert={alert} />
              ))}
            </div>
          </div>
        )}

        {/* Recommendations Section - Expandable */}
        {score.recommendations.length > 0 && (
          <div className="border-t border-gray-200 pt-4">
            <button
              onClick={() => setExpandedRecommendations(!expandedRecommendations)}
              className="w-full flex items-center justify-between text-sm font-semibold text-gray-900 hover:text-gray-700 transition-colors duration-200"
            >
              <span className="flex items-center gap-2">
                <Info className="w-4 h-4" />
                التوصيات ({score.recommendations.length})
              </span>
              {expandedRecommendations ? (
                <ChevronUp className="w-5 h-5" />
              ) : (
                <ChevronDown className="w-5 h-5" />
              )}
            </button>

            {/* Animated expansion */}
            <div
              className={`overflow-hidden transition-all duration-300 ease-in-out ${
                expandedRecommendations ? 'max-h-96 opacity-100 mt-3' : 'max-h-0 opacity-0'
              }`}
            >
              <div className="space-y-2 overflow-y-auto max-h-80">
                {score.recommendations.map((recommendation) => (
                  <RecommendationItem key={recommendation.id} recommendation={recommendation} />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* No recommendations message */}
        {score.recommendations.length === 0 && score.alerts.length === 0 && (
          <div className="text-center py-6 border-t border-gray-200">
            <div className="text-gray-400 mb-2">
              <Heart className="w-8 h-8 mx-auto" />
            </div>
            <p className="text-sm text-gray-600">
              الحقل في حالة ممتازة! لا توجد تنبيهات أو توصيات
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default LivingFieldCard;
