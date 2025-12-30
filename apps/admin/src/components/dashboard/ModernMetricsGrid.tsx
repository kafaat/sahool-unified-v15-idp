'use client';

// Modern Metrics Grid with Animations
// شبكة المقاييس الحديثة مع الرسوم المتحركة

import ModernStatCard from '@/components/ui/ModernStatCard';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState, useEffect } from 'react';

export interface ModernMetric {
  title: string;
  value: number | string;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  suffix?: string;
  iconColor?: string;
  variant?: 'glass' | 'gradient' | 'solid';
}

interface ModernMetricsGridProps {
  metrics: ModernMetric[];
  columns?: 2 | 3 | 4 | 5 | 6;
  className?: string;
  animated?: boolean;
  staggerDelay?: number;
}

export default function ModernMetricsGrid({
  metrics,
  columns = 4,
  className = '',
  animated = true,
  staggerDelay = 100,
}: ModernMetricsGridProps) {
  const [isVisible, setIsVisible] = useState(!animated);

  useEffect(() => {
    if (animated) {
      // Trigger animation after component mounts
      const timer = setTimeout(() => setIsVisible(true), 50);
      return () => clearTimeout(timer);
    }
  }, [animated]);

  const gridCols = {
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
    5: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-5',
    6: 'grid-cols-1 md:grid-cols-3 lg:grid-cols-6',
  };

  return (
    <div className={cn('relative', className)}>
      {/* Decorative background gradient */}
      <div className="absolute inset-0 gradient-mesh opacity-30 pointer-events-none rounded-3xl" />

      {/* Metrics Grid */}
      <div className={cn('relative grid gap-6', gridCols[columns])}>
        {metrics.map((metric, index) => (
          <div
            key={index}
            className={cn(
              'transition-all duration-500',
              isVisible
                ? 'opacity-100 translate-y-0'
                : 'opacity-0 translate-y-8'
            )}
            style={{
              transitionDelay: animated ? `${index * staggerDelay}ms` : '0ms',
            }}
          >
            <ModernStatCard
              title={metric.title}
              value={metric.value}
              icon={metric.icon}
              trend={metric.trend}
              suffix={metric.suffix}
              iconColor={metric.iconColor}
              variant={metric.variant || 'glass'}
              animated={animated}
            />
          </div>
        ))}
      </div>

      {/* Loading Skeleton (optional) */}
      {!isVisible && animated && (
        <div className={cn('absolute inset-0 grid gap-6', gridCols[columns])}>
          {metrics.map((_, index) => (
            <div
              key={`skeleton-${index}`}
              className="h-32 rounded-2xl skeleton"
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Quick Stats Summary Component
interface QuickStatsSummaryProps {
  title: string;
  stats: {
    label: string;
    value: string | number;
    color?: string;
  }[];
  className?: string;
}

export function QuickStatsSummary({
  title,
  stats,
  className = '',
}: QuickStatsSummaryProps) {
  return (
    <div className={cn('glass-card rounded-2xl p-6 animate-scale-in', className)}>
      <h3 className="text-lg font-bold gradient-text mb-4">{title}</h3>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <div
            key={index}
            className={cn(
              'text-center p-4 rounded-xl transition-all duration-300',
              'glass hover:glass-strong hover:scale-105',
              'animate-fade-in'
            )}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              {stat.label}
            </p>
            <p
              className={cn(
                'text-2xl font-bold',
                stat.color || 'gradient-text'
              )}
            >
              {stat.value}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

// Metric Comparison Component
interface MetricComparisonProps {
  title: string;
  current: {
    label: string;
    value: number;
  };
  previous: {
    label: string;
    value: number;
  };
  suffix?: string;
  className?: string;
}

export function MetricComparison({
  title,
  current,
  previous,
  suffix = '',
  className = '',
}: MetricComparisonProps) {
  const difference = current.value - previous.value;
  const percentChange = previous.value > 0
    ? ((difference / previous.value) * 100).toFixed(1)
    : 0;
  const isPositive = difference >= 0;

  return (
    <div className={cn('glass-card rounded-2xl p-6 animate-scale-in', className)}>
      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">
        {title}
      </h3>

      <div className="grid grid-cols-2 gap-6">
        {/* Current Value */}
        <div className="relative">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
            {current.label}
          </p>
          <div className="flex items-baseline gap-2">
            <p className="text-4xl font-bold gradient-text">
              {current.value}
            </p>
            {suffix && (
              <span className="text-lg text-gray-500 dark:text-gray-400">
                {suffix}
              </span>
            )}
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-1 gradient-sahool rounded-full" />
        </div>

        {/* Previous Value */}
        <div className="relative">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
            {previous.label}
          </p>
          <div className="flex items-baseline gap-2">
            <p className="text-4xl font-bold text-gray-400 dark:text-gray-500">
              {previous.value}
            </p>
            {suffix && (
              <span className="text-lg text-gray-400 dark:text-gray-500">
                {suffix}
              </span>
            )}
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-300 dark:bg-gray-600 rounded-full" />
        </div>
      </div>

      {/* Change Indicator */}
      <div className="mt-6 pt-4 border-t border-gray-200/50 dark:border-gray-700/50">
        <div className={cn(
          'flex items-center justify-center gap-2 px-4 py-2 rounded-xl w-fit mx-auto',
          'glass-strong transition-all duration-300',
          isPositive
            ? 'text-green-700 dark:text-green-400'
            : 'text-red-700 dark:text-red-400'
        )}>
          <span className="text-2xl font-bold">
            {isPositive ? '+' : ''}{difference}
          </span>
          <div className="text-right">
            <p className="text-xs opacity-80">التغير</p>
            <p className="text-sm font-semibold">
              {isPositive ? '+' : ''}{percentChange}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Circular Progress Metric
interface CircularProgressMetricProps {
  title: string;
  value: number;
  max: number;
  suffix?: string;
  color?: string;
  className?: string;
}

export function CircularProgressMetric({
  title,
  value,
  max,
  suffix = '',
  color = 'sahool',
  className = '',
}: CircularProgressMetricProps) {
  const percentage = Math.min((value / max) * 100, 100);
  const circumference = 2 * Math.PI * 45; // radius = 45
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const colorClasses = {
    sahool: 'text-sahool-500',
    blue: 'text-blue-500',
    purple: 'text-purple-500',
    orange: 'text-orange-500',
  };

  return (
    <div className={cn('glass-card rounded-2xl p-6 animate-scale-in', className)}>
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-4 text-center">
        {title}
      </h3>

      <div className="relative w-32 h-32 mx-auto">
        {/* Background Circle */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r="45"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-gray-200 dark:text-gray-700"
          />
          {/* Progress Circle */}
          <circle
            cx="64"
            cy="64"
            r="45"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={cn(
              'transition-all duration-1000 ease-out',
              colorClasses[color as keyof typeof colorClasses] || colorClasses.sahool
            )}
          />
        </svg>

        {/* Center Text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <p className="text-3xl font-bold gradient-text">
            {value}
          </p>
          {suffix && (
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {suffix}
            </p>
          )}
        </div>
      </div>

      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          من أصل {max} {suffix}
        </p>
        <p className={cn(
          'text-sm font-bold mt-1',
          colorClasses[color as keyof typeof colorClasses] || colorClasses.sahool
        )}>
          {percentage.toFixed(1)}%
        </p>
      </div>
    </div>
  );
}
