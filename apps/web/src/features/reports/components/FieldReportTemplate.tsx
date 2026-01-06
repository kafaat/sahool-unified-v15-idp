/**
 * Field Report Template Component
 * قالب تقرير الحقل
 *
 * Renders a printable field report layout with RTL support for Arabic PDF generation
 */

'use client';

import React from 'react';
import {
  MapPin,
  Calendar,
  Sprout,
  TrendingUp,
  Droplets,
  Wind,
  Sun,
  AlertCircle,
  CheckCircle2,
  Activity,
} from 'lucide-react';
import type { FieldReportData, ReportSection } from '../types/reports';
import {
  formatDateForPDF,
  formatNumberForPDF,
  formatArea,
  getSectionTitle,
  orderSections,
} from '../utils/pdf-generator';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface FieldReportTemplateProps {
  data: FieldReportData;
  sections: ReportSection[];
  language?: 'ar' | 'en' | 'both';
  startDate?: string;
  endDate?: string;
  title?: string;
  titleAr?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export const FieldReportTemplate: React.FC<FieldReportTemplateProps> = ({
  data,
  sections,
  language = 'both',
  startDate,
  endDate,
  title,
  titleAr,
}) => {
  const isRTL = language === 'ar';
  const showBoth = language === 'both';
  const orderedSections = orderSections(sections, 'field');

  // Helper to render bilingual text
  const BilingualText = ({ en, ar }: { en: string; ar: string }) => {
    if (language === 'ar') return <span>{ar}</span>;
    if (language === 'en') return <span>{en}</span>;
    return (
      <div className="space-y-1">
        <div className="text-right" dir="rtl">{ar}</div>
        <div className="text-left" dir="ltr">{en}</div>
      </div>
    );
  };

  return (
    <div
      className="bg-white p-8 max-w-5xl mx-auto print:p-0"
      dir={isRTL ? 'rtl' : 'ltr'}
      style={{ fontFamily: isRTL ? 'Tajawal, Noto Sans Arabic, sans-serif' : 'Inter, Arial, sans-serif' }}
    >
      {/* Header */}
      <div className="border-b-4 border-green-500 pb-6 mb-8 print:mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
              <Sprout className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {showBoth ? (
                  <>
                    <div className="text-right" dir="rtl">{titleAr || 'تقرير أداء الحقل'}</div>
                    <div className="text-xl text-left mt-1" dir="ltr">{title || 'Field Performance Report'}</div>
                  </>
                ) : isRTL ? (
                  titleAr || 'تقرير أداء الحقل'
                ) : (
                  title || 'Field Performance Report'
                )}
              </h1>
            </div>
          </div>
          <div className="text-right text-sm text-gray-600">
            <div>{formatDateForPDF(new Date(), language === 'ar' ? 'ar' : 'en')}</div>
            <div className="text-xs text-gray-500 mt-1">SAHOOL Platform</div>
          </div>
        </div>

        {/* Field Name */}
        <div className="bg-green-50 rounded-lg p-4 mt-4">
          <h2 className="text-2xl font-bold text-green-900">
            {showBoth ? (
              <>
                <div className="text-right" dir="rtl">{data.field.nameAr}</div>
                <div className="text-lg mt-1" dir="ltr">{data.field.name}</div>
              </>
            ) : isRTL ? (
              data.field.nameAr
            ) : (
              data.field.name
            )}
          </h2>
        </div>
      </div>

      {/* Render Sections */}
      {orderedSections.includes('field_info') && (
        <Section
          title={getSectionTitle('field_info', language === 'ar' ? 'ar' : 'en')}
          titleAr={getSectionTitle('field_info', 'ar')}
          language={language}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InfoCard
              icon={<MapPin className="w-5 h-5 text-green-500" />}
              label={{ en: 'Location', ar: 'الموقع' }}
              value={{
                en: data.field.location.governorate,
                ar: data.field.location.governorateAr,
              }}
              language={language}
            />
            <InfoCard
              icon={<Sprout className="w-5 h-5 text-green-500" />}
              label={{ en: 'Crop Type', ar: 'نوع المحصول' }}
              value={{ en: data.field.cropType, ar: data.field.cropTypeAr }}
              language={language}
            />
            <InfoCard
              icon={<Activity className="w-5 h-5 text-green-500" />}
              label={{ en: 'Field Area', ar: 'مساحة الحقل' }}
              value={{
                en: formatArea(data.field.area, 'hectare', 'en'),
                ar: formatArea(data.field.area, 'hectare', 'ar'),
              }}
              language={language}
            />
            <InfoCard
              icon={<Calendar className="w-5 h-5 text-green-500" />}
              label={{ en: 'Planting Date', ar: 'تاريخ الزراعة' }}
              value={{
                en: formatDateForPDF(data.field.plantingDate, 'en'),
                ar: formatDateForPDF(data.field.plantingDate, 'ar'),
              }}
              language={language}
            />
            {data.field.harvestDate && (
              <InfoCard
                icon={<Calendar className="w-5 h-5 text-green-500" />}
                label={{ en: 'Expected Harvest', ar: 'موعد الحصاد المتوقع' }}
                value={{
                  en: formatDateForPDF(data.field.harvestDate, 'en'),
                  ar: formatDateForPDF(data.field.harvestDate, 'ar'),
                }}
                language={language}
              />
            )}
            <InfoCard
              icon={<MapPin className="w-5 h-5 text-green-500" />}
              label={{ en: 'Coordinates', ar: 'الإحداثيات' }}
              value={{
                en: `${data.field.location.latitude.toFixed(6)}, ${data.field.location.longitude.toFixed(6)}`,
                ar: `${data.field.location.latitude.toFixed(6)}, ${data.field.location.longitude.toFixed(6)}`,
              }}
              language={language}
            />
          </div>
        </Section>
      )}

      {/* NDVI Trend Section */}
      {orderedSections.includes('ndvi_trend') && data.ndviTrend && (
        <Section
          title={getSectionTitle('ndvi_trend', language === 'ar' ? 'ar' : 'en')}
          titleAr={getSectionTitle('ndvi_trend', 'ar')}
          language={language}
        >
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="text-center">
                <div className="text-sm text-gray-600">
                  <BilingualText en="Average NDVI" ar="متوسط NDVI" />
                </div>
                <div className="text-2xl font-bold text-green-600 mt-1">
                  {data.ndviTrend.average.toFixed(3)}
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600">
                  <BilingualText en="Trend" ar="الاتجاه" />
                </div>
                <div className="text-2xl font-bold mt-1">
                  {data.ndviTrend.trend === 'increasing' && (
                    <span className="text-green-600 flex items-center justify-center gap-1">
                      <TrendingUp className="w-6 h-6" />
                      <BilingualText en="Improving" ar="تحسن" />
                    </span>
                  )}
                  {data.ndviTrend.trend === 'decreasing' && (
                    <span className="text-red-600 flex items-center justify-center gap-1">
                      <TrendingUp className="w-6 h-6 rotate-180" />
                      <BilingualText en="Declining" ar="تراجع" />
                    </span>
                  )}
                  {data.ndviTrend.trend === 'stable' && (
                    <span className="text-blue-600">
                      <BilingualText en="Stable" ar="مستقر" />
                    </span>
                  )}
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600">
                  <BilingualText en="Observations" ar="عدد القياسات" />
                </div>
                <div className="text-2xl font-bold text-gray-900 mt-1">
                  {data.ndviTrend.values.length}
                </div>
              </div>
            </div>
            <div className="h-64 bg-white rounded-lg p-4 flex items-center justify-center">
              <div className="text-center text-gray-500">
                <Activity className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <BilingualText en="NDVI Chart will be rendered here" ar="سيتم عرض مخطط NDVI هنا" />
              </div>
            </div>
          </div>
        </Section>
      )}

      {/* Health Zones Section */}
      {orderedSections.includes('health_zones') && data.healthZones && (
        <Section
          title={getSectionTitle('health_zones', language === 'ar' ? 'ar' : 'en')}
          titleAr={getSectionTitle('health_zones', 'ar')}
          language={language}
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <HealthZoneCard
              label={{ en: 'Healthy', ar: 'صحي' }}
              percentage={data.healthZones.healthy}
              color="green"
              language={language}
            />
            <HealthZoneCard
              label={{ en: 'Moderate', ar: 'متوسط' }}
              percentage={data.healthZones.moderate}
              color="yellow"
              language={language}
            />
            <HealthZoneCard
              label={{ en: 'Stressed', ar: 'إجهاد' }}
              percentage={data.healthZones.stressed}
              color="orange"
              language={language}
            />
            <HealthZoneCard
              label={{ en: 'Critical', ar: 'حرج' }}
              percentage={data.healthZones.critical}
              color="red"
              language={language}
            />
          </div>
        </Section>
      )}

      {/* Weather Summary Section */}
      {orderedSections.includes('weather_summary') && data.weatherSummary && (
        <Section
          title={getSectionTitle('weather_summary', language === 'ar' ? 'ar' : 'en')}
          titleAr={getSectionTitle('weather_summary', 'ar')}
          language={language}
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <InfoCard
              icon={<Sun className="w-5 h-5 text-orange-500" />}
              label={{ en: 'Avg Temperature', ar: 'متوسط الحرارة' }}
              value={{
                en: `${data.weatherSummary.avgTemperature}°C`,
                ar: `${data.weatherSummary.avgTemperature}°م`,
              }}
              language={language}
            />
            <InfoCard
              icon={<Droplets className="w-5 h-5 text-blue-500" />}
              label={{ en: 'Total Rainfall', ar: 'إجمالي الأمطار' }}
              value={{
                en: `${data.weatherSummary.totalRainfall} mm`,
                ar: `${formatNumberForPDF(data.weatherSummary.totalRainfall, 'ar')} مم`,
              }}
              language={language}
            />
            <InfoCard
              icon={<Droplets className="w-5 h-5 text-cyan-500" />}
              label={{ en: 'Avg Humidity', ar: 'متوسط الرطوبة' }}
              value={{
                en: `${data.weatherSummary.avgHumidity}%`,
                ar: `${formatNumberForPDF(data.weatherSummary.avgHumidity, 'ar')}%`,
              }}
              language={language}
            />
            <InfoCard
              icon={<Wind className="w-5 h-5 text-gray-500" />}
              label={{ en: 'Avg Wind Speed', ar: 'متوسط سرعة الرياح' }}
              value={{
                en: `${data.weatherSummary.avgWindSpeed} km/h`,
                ar: `${formatNumberForPDF(data.weatherSummary.avgWindSpeed, 'ar')} كم/س`,
              }}
              language={language}
            />
          </div>
        </Section>
      )}

      {/* Tasks Summary Section */}
      {orderedSections.includes('tasks_summary') && data.recentTasks && (
        <Section
          title={getSectionTitle('tasks_summary', language === 'ar' ? 'ar' : 'en')}
          titleAr={getSectionTitle('tasks_summary', 'ar')}
          language={language}
        >
          <div className="space-y-3">
            {data.recentTasks.map((task) => (
              <div
                key={task.id}
                className="bg-gray-50 rounded-lg p-4 flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                  <div>
                    <div className="font-medium text-gray-900">
                      {language === 'ar' ? task.titleAr : task.title}
                    </div>
                    <div className="text-sm text-gray-600">
                      {language === 'ar' ? task.type : task.type}
                    </div>
                  </div>
                </div>
                {task.completedAt && (
                  <div className="text-sm text-gray-500">
                    {formatDateForPDF(task.completedAt, language === 'ar' ? 'ar' : 'en')}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Recommendations Section */}
      {orderedSections.includes('recommendations') && data.recommendations && (
        <Section
          title={getSectionTitle('recommendations', language === 'ar' ? 'ar' : 'en')}
          titleAr={getSectionTitle('recommendations', 'ar')}
          language={language}
        >
          <div className="space-y-4">
            {data.recommendations.map((rec) => (
              <div
                key={rec.id}
                className={`rounded-lg p-4 border-l-4 ${
                  rec.priority === 'high'
                    ? 'bg-red-50 border-red-500'
                    : rec.priority === 'medium'
                      ? 'bg-yellow-50 border-yellow-500'
                      : 'bg-blue-50 border-blue-500'
                }`}
              >
                <div className="flex items-start gap-3">
                  <AlertCircle
                    className={`w-5 h-5 mt-0.5 ${
                      rec.priority === 'high'
                        ? 'text-red-500'
                        : rec.priority === 'medium'
                          ? 'text-yellow-500'
                          : 'text-blue-500'
                    }`}
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 mb-1">
                      {language === 'ar' ? rec.titleAr : rec.title}
                    </div>
                    <div className="text-sm text-gray-700">
                      {language === 'ar' ? rec.descriptionAr : rec.description}
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                      <BilingualText
                        en={`Priority: ${rec.priority}`}
                        ar={`الأولوية: ${rec.priority === 'high' ? 'عالية' : rec.priority === 'medium' ? 'متوسطة' : 'منخفضة'}`}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Footer */}
      <div className="mt-12 pt-6 border-t border-gray-200 text-center text-sm text-gray-600">
        <div className="flex items-center justify-between">
          <div>
            {startDate && endDate && (
              <BilingualText
                en={`Report Period: ${formatDateForPDF(startDate, 'en')} - ${formatDateForPDF(endDate, 'en')}`}
                ar={`فترة التقرير: ${formatDateForPDF(startDate, 'ar')} - ${formatDateForPDF(endDate, 'ar')}`}
              />
            )}
          </div>
          <div>
            <BilingualText
              en="Generated by SAHOOL Platform"
              ar="تم إنشاؤه بواسطة منصة ساهول"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Helper Components
// ═══════════════════════════════════════════════════════════════════════════

interface SectionProps {
  title: string;
  titleAr?: string;
  language?: 'ar' | 'en' | 'both';
  children: React.ReactNode;
}

const Section: React.FC<SectionProps> = ({ title, titleAr, language = 'both', children }) => {
  return (
    <div className="mb-8 print:mb-6 print:break-inside-avoid">
      <h3 className="text-xl font-bold text-green-600 mb-4 pb-2 border-b-2 border-gray-200">
        {language === 'both' && titleAr ? (
          <>
            <div className="text-right" dir="rtl">{titleAr}</div>
            <div className="text-lg text-left mt-1" dir="ltr">{title}</div>
          </>
        ) : language === 'ar' && titleAr ? (
          titleAr
        ) : (
          title
        )}
      </h3>
      {children}
    </div>
  );
};

interface InfoCardProps {
  icon: React.ReactNode;
  label: { en: string; ar: string };
  value: { en: string; ar: string };
  language?: 'ar' | 'en' | 'both';
}

const InfoCard: React.FC<InfoCardProps> = ({ icon, label, value, language = 'both' }) => {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <div className="text-sm font-medium text-gray-600">
          {language === 'ar' ? label.ar : language === 'en' ? label.en : (
            <>
              <div className="text-right" dir="rtl">{label.ar}</div>
              <div className="text-xs" dir="ltr">{label.en}</div>
            </>
          )}
        </div>
      </div>
      <div className="text-lg font-semibold text-gray-900">
        {language === 'ar' ? value.ar : language === 'en' ? value.en : (
          <>
            <div className="text-right" dir="rtl">{value.ar}</div>
            <div className="text-sm" dir="ltr">{value.en}</div>
          </>
        )}
      </div>
    </div>
  );
};

interface HealthZoneCardProps {
  label: { en: string; ar: string };
  percentage: number;
  color: 'green' | 'yellow' | 'orange' | 'red';
  language?: 'ar' | 'en' | 'both';
}

const HealthZoneCard: React.FC<HealthZoneCardProps> = ({ label, percentage, color, language = 'both' }) => {
  const colorClasses = {
    green: 'bg-green-50 text-green-700 border-green-200',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    orange: 'bg-orange-50 text-orange-700 border-orange-200',
    red: 'bg-red-50 text-red-700 border-red-200',
  };

  return (
    <div className={`rounded-lg p-4 border-2 ${colorClasses[color]}`}>
      <div className="text-center">
        <div className="text-3xl font-bold mb-1">
          {formatNumberForPDF(percentage, language === 'ar' ? 'ar' : 'en', 1)}%
        </div>
        <div className="text-sm font-medium">
          {language === 'ar' ? label.ar : language === 'en' ? label.en : (
            <>
              <div dir="rtl">{label.ar}</div>
              <div className="text-xs" dir="ltr">{label.en}</div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default FieldReportTemplate;
