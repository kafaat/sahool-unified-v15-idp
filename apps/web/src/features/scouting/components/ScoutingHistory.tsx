'use client';

/**
 * Scouting History Component
 * مكون سجل الكشافة الحقلية
 *
 * Displays past scouting sessions with:
 * - Session list with key metrics
 * - Filter by date range, field, severity
 * - Session details view
 * - Statistics overview
 */

import React, { useState, useMemo } from 'react';
import { useLocale } from 'next-intl';
import {
  Calendar,
  MapPin,
  Eye,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Filter,
  Download,
  ChevronDown,
  ChevronUp,
  Search,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Loading } from '@/components/ui/loading';
import { useScoutingHistory, useScoutingStatistics, useGenerateReport } from '../hooks/useScouting';
import type {
  ScoutingHistoryFilter,
  ScoutingSession,
  ObservationCategory,
  Severity,
} from '../types/scouting';
import { CATEGORY_OPTIONS, SEVERITY_LABELS } from '../types/scouting';
import { clsx } from 'clsx';
import { format } from 'date-fns';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface ScoutingHistoryProps {
  fieldId?: string;
  onSelectSession?: (sessionId: string) => void;
  showFilters?: boolean;
  showStatistics?: boolean;
}

interface FilterState {
  fieldId?: string;
  category?: ObservationCategory;
  minSeverity?: Severity;
  startDate?: string;
  endDate?: string;
  searchQuery?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export const ScoutingHistory: React.FC<ScoutingHistoryProps> = ({
  fieldId,
  onSelectSession,
  showFilters = true,
  showStatistics = true,
}) => {
  const locale = useLocale();
  const isArabic = locale === 'ar';

  // State
  const [filters, setFilters] = useState<FilterState>({
    fieldId,
  });
  const [showFilterPanel, setShowFilterPanel] = useState(false);
  const [expandedSession, setExpandedSession] = useState<string | null>(null);

  // Build API filter
  const apiFilters: ScoutingHistoryFilter = useMemo(() => {
    return {
      fieldId: filters.fieldId,
      category: filters.category,
      minSeverity: filters.minSeverity,
      startDate: filters.startDate,
      endDate: filters.endDate,
      status: 'completed',
    };
  }, [filters]);

  // Fetch data
  const { data: sessions = [], isLoading, error } = useScoutingHistory(apiFilters);
  const { data: statistics } = useScoutingStatistics(fieldId);
  const generateReport = useGenerateReport();

  // Filter sessions by search query
  const filteredSessions = useMemo(() => {
    if (!filters.searchQuery) return sessions;

    const query = filters.searchQuery.toLowerCase();
    return sessions.filter(
      (session) =>
        session.fieldName.toLowerCase().includes(query) ||
        session.fieldNameAr.includes(query) ||
        session.notes?.toLowerCase().includes(query) ||
        session.notesAr?.toLowerCase().includes(query)
    );
  }, [sessions, filters.searchQuery]);

  // ─────────────────────────────────────────────────────────────────────────
  // Handlers
  // ─────────────────────────────────────────────────────────────────────────

  const handleFilterChange = (key: keyof FilterState, value: any) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleClearFilters = () => {
    setFilters({ fieldId });
  };

  const handleGenerateReport = async (sessionId: string) => {
    try {
      const result = await generateReport.mutateAsync({
        sessionId,
        config: {
          includePhotos: true,
          includeMap: true,
          language: 'both',
          format: 'pdf',
        },
      });

      // Open download in new tab
      if (result.downloadUrl) {
        window.open(result.downloadUrl, '_blank');
      }
    } catch (error) {
      console.error('Failed to generate report:', error);
    }
  };

  const toggleSessionExpansion = (sessionId: string) => {
    setExpandedSession((prev) => (prev === sessionId ? null : sessionId));
  };

  // ─────────────────────────────────────────────────────────────────────────
  // Calculate active filters count
  // ─────────────────────────────────────────────────────────────────────────

  const activeFiltersCount = useMemo(() => {
    let count = 0;
    if (filters.category) count++;
    if (filters.minSeverity) count++;
    if (filters.startDate) count++;
    if (filters.endDate) count++;
    return count;
  }, [filters]);

  // ─────────────────────────────────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="p-6">
          <div className="flex items-center gap-3 text-red-600">
            <AlertTriangle className="w-5 h-5" />
            <p>{isArabic ? 'فشل في تحميل السجل' : 'Failed to load history'}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics Overview */}
      {showStatistics && statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">
                    {isArabic ? 'إجمالي الجلسات' : 'Total Sessions'}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {statistics.totalSessions}
                  </p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Calendar className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">
                    {isArabic ? 'إجمالي الملاحظات' : 'Total Observations'}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {statistics.totalObservations}
                  </p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <Eye className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">
                    {isArabic ? 'هذا الأسبوع' : 'This Week'}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {statistics.sessionsThisWeek}
                  </p>
                </div>
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">
                    {isArabic ? 'متوسط الملاحظات' : 'Avg. Observations'}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {statistics.averageObservationsPerSession.toFixed(1)}
                  </p>
                </div>
                <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Search and Filter Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <Input
                  type="text"
                  placeholder={isArabic ? 'البحث في السجل...' : 'Search history...'}
                  value={filters.searchQuery || ''}
                  onChange={(e) => handleFilterChange('searchQuery', e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Filter Toggle */}
            {showFilters && (
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => setShowFilterPanel(!showFilterPanel)}
                  className="relative"
                >
                  <Filter className="w-4 h-4 mr-2" />
                  {isArabic ? 'تصفية' : 'Filter'}
                  {activeFiltersCount > 0 && (
                    <Badge
                      variant="default"
                      className="absolute -top-2 -right-2 bg-sahool-green-600 text-white w-5 h-5 flex items-center justify-center p-0 text-xs"
                    >
                      {activeFiltersCount}
                    </Badge>
                  )}
                </Button>

                {activeFiltersCount > 0 && (
                  <Button variant="outline" size="sm" onClick={handleClearFilters}>
                    {isArabic ? 'مسح' : 'Clear'}
                  </Button>
                )}
              </div>
            )}
          </div>

          {/* Filter Panel */}
          {showFilterPanel && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Category Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {isArabic ? 'الفئة' : 'Category'}
                  </label>
                  <select
                    value={filters.category || ''}
                    onChange={(e) =>
                      handleFilterChange('category', e.target.value || undefined)
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-transparent"
                  >
                    <option value="">{isArabic ? 'الكل' : 'All'}</option>
                    {CATEGORY_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {isArabic ? option.labelAr : option.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Severity Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {isArabic ? 'الشدة الدنيا' : 'Min Severity'}
                  </label>
                  <select
                    value={filters.minSeverity || ''}
                    onChange={(e) =>
                      handleFilterChange(
                        'minSeverity',
                        e.target.value ? Number(e.target.value) : undefined
                      )
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-transparent"
                  >
                    <option value="">{isArabic ? 'الكل' : 'All'}</option>
                    {[1, 2, 3, 4, 5].map((severity) => (
                      <option key={severity} value={severity}>
                        {isArabic
                          ? SEVERITY_LABELS[severity as Severity].ar
                          : SEVERITY_LABELS[severity as Severity].en}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Start Date */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {isArabic ? 'من تاريخ' : 'From Date'}
                  </label>
                  <Input
                    type="date"
                    value={filters.startDate || ''}
                    onChange={(e) => handleFilterChange('startDate', e.target.value || undefined)}
                  />
                </div>

                {/* End Date */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {isArabic ? 'إلى تاريخ' : 'To Date'}
                  </label>
                  <Input
                    type="date"
                    value={filters.endDate || ''}
                    onChange={(e) => handleFilterChange('endDate', e.target.value || undefined)}
                  />
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Sessions List */}
      <div className="space-y-4">
        {filteredSessions.length === 0 ? (
          <Card className="border-dashed">
            <CardContent className="p-12 text-center">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">
                {isArabic ? 'لا توجد جلسات كشافة' : 'No scouting sessions found'}
              </p>
            </CardContent>
          </Card>
        ) : (
          filteredSessions.map((session) => {
            const isExpanded = expandedSession === session.id;
            const avgSeverity = session.averageSeverity || 0;
            const severityColor =
              avgSeverity >= 4
                ? 'text-red-600 bg-red-100'
                : avgSeverity >= 3
                ? 'text-orange-600 bg-orange-100'
                : 'text-green-600 bg-green-100';

            return (
              <Card key={session.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  {/* Session Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* Field Name */}
                      <div className="flex items-center gap-2 mb-2">
                        <MapPin className="w-5 h-5 text-sahool-green-600" />
                        <h3 className="font-bold text-lg text-gray-900">
                          {isArabic ? session.fieldNameAr : session.fieldName}
                        </h3>
                      </div>

                      {/* Date & Duration */}
                      <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          <span>
                            {format(new Date(session.startTime), 'MMM dd, yyyy', {
                              locale: isArabic ? undefined : undefined,
                            })}
                          </span>
                        </div>
                        {session.duration && (
                          <div className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            <span>
                              {session.duration} {isArabic ? 'دقيقة' : 'min'}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Stats */}
                      <div className="flex flex-wrap gap-2">
                        <Badge variant="default" className="bg-blue-100 text-blue-800">
                          {session.observationsCount} {isArabic ? 'ملاحظة' : 'observations'}
                        </Badge>

                        {avgSeverity > 0 && (
                          <Badge variant="default" className={severityColor}>
                            {isArabic ? 'الشدة المتوسطة:' : 'Avg Severity:'} {avgSeverity.toFixed(1)}
                          </Badge>
                        )}

                        {session.scoutName && (
                          <Badge variant="default" className="bg-gray-100 text-gray-800">
                            {session.scoutName}
                          </Badge>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 ml-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleGenerateReport(session.id)}
                        disabled={generateReport.isPending}
                      >
                        <Download className="w-4 h-4" />
                      </Button>

                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => toggleSessionExpansion(session.id)}
                      >
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                      </Button>

                      {onSelectSession && (
                        <Button
                          size="sm"
                          variant="primary"
                          onClick={() => onSelectSession(session.id)}
                        >
                          <Eye className="w-4 h-4 mr-2" />
                          {isArabic ? 'عرض' : 'View'}
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      {/* Category Breakdown */}
                      {session.categoryCounts && Object.keys(session.categoryCounts).length > 0 && (
                        <div className="mb-4">
                          <h4 className="text-sm font-semibold text-gray-700 mb-2">
                            {isArabic ? 'تفصيل الفئات' : 'Category Breakdown'}
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {Object.entries(session.categoryCounts).map(([category, count]) => {
                              const categoryOption = CATEGORY_OPTIONS.find(
                                (opt) => opt.value === category
                              );
                              return (
                                <Badge
                                  key={category}
                                  variant="default"
                                  style={{
                                    backgroundColor: `${categoryOption?.color}20`,
                                    color: categoryOption?.color,
                                  }}
                                >
                                  {isArabic ? categoryOption?.labelAr : categoryOption?.label}: {count}
                                </Badge>
                              );
                            })}
                          </div>
                        </div>
                      )}

                      {/* Notes */}
                      {(session.notes || session.notesAr) && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-2">
                            {isArabic ? 'ملاحظات' : 'Notes'}
                          </h4>
                          <p className="text-sm text-gray-600">
                            {isArabic ? session.notesAr : session.notes}
                          </p>
                        </div>
                      )}

                      {/* Weather */}
                      {session.weather && (
                        <div className="mt-3">
                          <h4 className="text-sm font-semibold text-gray-700 mb-2">
                            {isArabic ? 'الطقس' : 'Weather'}
                          </h4>
                          <div className="flex gap-4 text-sm text-gray-600">
                            {session.weather.temperature && (
                              <span>
                                {isArabic ? 'الحرارة:' : 'Temperature:'} {session.weather.temperature}°C
                              </span>
                            )}
                            {session.weather.humidity && (
                              <span>
                                {isArabic ? 'الرطوبة:' : 'Humidity:'} {session.weather.humidity}%
                              </span>
                            )}
                            {session.weather.conditions && (
                              <span>{session.weather.conditions}</span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
};

export default ScoutingHistory;
