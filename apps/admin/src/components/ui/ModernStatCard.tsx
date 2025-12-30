'use client';

// Modern Statistics Card with Glassmorphism
// بطاقة الإحصائيات الحديثة بتأثير الزجاج

import { cn, formatNumber } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { useEffect, useState } from 'react';

interface ModernStatCardProps {
  title: string;
  value: number | string;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  suffix?: string;
  className?: string;
  iconColor?: string;
  variant?: 'glass' | 'gradient' | 'solid';
  animated?: boolean;
}

export default function ModernStatCard({
  title,
  value,
  icon: Icon,
  trend,
  suffix = '',
  className = '',
  iconColor = 'text-sahool-600',
  variant = 'glass',
  animated = true,
}: ModernStatCardProps) {
  const [displayValue, setDisplayValue] = useState<number>(0);
  const finalValue = typeof value === 'number' ? value : 0;

  // Animated counter effect
  useEffect(() => {
    if (!animated || typeof value !== 'number') {
      setDisplayValue(finalValue);
      return;
    }

    const duration = 1000; // 1 second
    const steps = 30;
    const stepValue = finalValue / steps;
    const stepDuration = duration / steps;
    let currentStep = 0;

    const timer = setInterval(() => {
      currentStep++;
      if (currentStep >= steps) {
        setDisplayValue(finalValue);
        clearInterval(timer);
      } else {
        setDisplayValue(Math.floor(stepValue * currentStep));
      }
    }, stepDuration);

    return () => clearInterval(timer);
  }, [value, finalValue, animated]);

  const formattedValue = typeof value === 'number'
    ? formatNumber(displayValue)
    : value;

  // Variant styles
  const variantStyles = {
    glass: 'glass-card hover-glow',
    gradient: 'card-gradient glass-card hover-glow',
    solid: 'bg-white dark:bg-gray-800 shadow-md hover:shadow-xl border border-gray-100 dark:border-gray-700',
  };

  return (
    <div
      className={cn(
        'rounded-2xl p-6 transition-all duration-300 group',
        'transform hover:-translate-y-2 hover:scale-[1.02]',
        animated && 'animate-scale-in',
        variantStyles[variant],
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Title */}
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
            {title}
          </p>

          {/* Value */}
          <div className="flex items-baseline gap-2">
            <p className={cn(
              "text-4xl font-bold transition-all duration-300",
              "bg-gradient-to-br from-gray-900 to-gray-600 dark:from-white dark:to-gray-300",
              "bg-clip-text text-transparent",
              "group-hover:scale-105"
            )}>
              {formattedValue}
            </p>
            {suffix && (
              <span className="text-lg text-gray-500 dark:text-gray-400 font-medium">
                {suffix}
              </span>
            )}
          </div>

          {/* Trend Indicator */}
          {trend && (
            <div
              className={cn(
                'flex items-center gap-1.5 mt-3 px-2.5 py-1 rounded-lg w-fit',
                'transition-all duration-300 backdrop-blur-sm',
                trend.isPositive
                  ? 'bg-green-100/80 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                  : 'bg-red-100/80 dark:bg-red-900/30 text-red-700 dark:text-red-400'
              )}
            >
              {trend.isPositive ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              <span className="text-sm font-semibold">
                {Math.abs(trend.value)}%
              </span>
              <span className="text-xs opacity-80">من الأسبوع الماضي</span>
            </div>
          )}
        </div>

        {/* Icon with animated background */}
        <div className="relative">
          {/* Animated glow background */}
          <div
            className={cn(
              'absolute inset-0 rounded-2xl blur-xl opacity-0 group-hover:opacity-100',
              'transition-opacity duration-500',
              iconColor.replace('text-', 'bg-').replace('-600', '-400')
            )}
          />

          {/* Icon container */}
          <div
            className={cn(
              'relative p-4 rounded-2xl transition-all duration-300',
              'transform group-hover:scale-110 group-hover:rotate-6',
              'bg-gradient-to-br shadow-lg',
              iconColor === 'text-sahool-600'
                ? 'from-sahool-500 to-sahool-600'
                : iconColor === 'text-blue-600'
                ? 'from-blue-500 to-blue-600'
                : iconColor === 'text-purple-600'
                ? 'from-purple-500 to-purple-600'
                : iconColor === 'text-orange-600'
                ? 'from-orange-500 to-orange-600'
                : iconColor === 'text-red-600'
                ? 'from-red-500 to-red-600'
                : 'from-gray-500 to-gray-600'
            )}
          >
            <Icon className="w-7 h-7 text-white drop-shadow-lg" />
          </div>
        </div>
      </div>

      {/* Decorative gradient line at bottom */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-sahool-500 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-b-2xl" />
    </div>
  );
}
