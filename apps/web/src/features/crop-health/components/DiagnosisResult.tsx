/**
 * Diagnosis Result Component
 * مكون نتيجة التشخيص
 */

'use client';

import React, { useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  TrendingUp,
  Package,
  Calendar,
  AlertCircle,
  Loader2,
  ExternalLink,
} from 'lucide-react';
import { useDiagnosisResult, useRequestConsultation } from '../hooks/useCropHealth';
import type { DiagnosedDisease, Treatment } from '../types';

interface DiagnosisResultProps {
  requestId: string;
}

export const DiagnosisResult: React.FC<DiagnosisResultProps> = ({ requestId }) => {
  const { data: result, isLoading } = useDiagnosisResult(requestId);
  const [expandedTreatment, setExpandedTreatment] = useState<string | null>(null);
  const requestConsultation = useRequestConsultation();

  if (isLoading || !result) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8" dir="rtl">
        <div className="flex flex-col items-center justify-center">
          <Loader2 className="w-12 h-12 text-green-500 animate-spin mb-4" />
          <p className="text-gray-600 font-medium">جاري تحليل الصور...</p>
          <p className="text-sm text-gray-500 mt-1">
            Analyzing images with AI...
          </p>
        </div>
      </div>
    );
  }

  const urgencyConfig = {
    immediate: {
      label: 'فوري',
      labelEn: 'Immediate',
      color: 'text-red-600',
      bg: 'bg-red-50',
      border: 'border-red-200',
      icon: AlertTriangle,
    },
    soon: {
      label: 'قريباً',
      labelEn: 'Soon',
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      icon: Clock,
    },
    monitor: {
      label: 'مراقبة',
      labelEn: 'Monitor',
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      icon: TrendingUp,
    },
  };

  const handleRequestConsultation = async () => {
    try {
      await requestConsultation.mutateAsync({
        diagnosisId: requestId,
      });
      alert('تم إرسال طلب الاستشارة بنجاح');
    } catch (err) {
      alert('حدث خطأ أثناء إرسال طلب الاستشارة');
      console.error(err);
    }
  };

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">نتيجة التشخيص</h2>
            <p className="text-sm text-gray-600 mt-1">Diagnosis Result</p>
          </div>
          <div className="text-left">
            <p className="text-sm text-gray-600">مستوى الثقة</p>
            <p className="text-2xl font-bold text-green-600 mt-1">
              {result.confidence.toFixed(1)}%
            </p>
          </div>
        </div>

        {result.confidence < 70 && (
          <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-yellow-900">
              <p className="font-medium">مستوى ثقة منخفض</p>
              <p className="mt-1">
                قد تحتاج إلى استشارة خبير للحصول على تشخيص أكثر دقة. يمكنك طلب
                استشارة خبير من الأسفل.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Diagnosed Diseases */}
      {result.diseases.map((diagnosed: DiagnosedDisease, index: number) => {
        const urgency = urgencyConfig[diagnosed.urgency];
        const UrgencyIcon = urgency.icon;

        return (
          <div
            key={diagnosed.disease.id}
            className={`bg-white rounded-xl shadow-sm border-2 ${urgency.border} overflow-hidden`}
          >
            {/* Disease Header */}
            <div className={`${urgency.bg} p-6 border-b ${urgency.border}`}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="flex items-center justify-center w-8 h-8 bg-white rounded-full text-sm font-bold text-gray-700">
                      {index + 1}
                    </span>
                    <h3 className="text-xl font-bold text-gray-900">
                      {diagnosed.disease.nameAr}
                    </h3>
                  </div>
                  <p className="text-sm text-gray-600">{diagnosed.disease.name}</p>
                  <p className="text-sm text-gray-700 mt-2">
                    {diagnosed.disease.descriptionAr}
                  </p>
                </div>
                <div className="text-left">
                  <p className="text-sm text-gray-600">مستوى الثقة</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {diagnosed.confidence.toFixed(1)}%
                  </p>
                </div>
              </div>

              {/* Urgency Badge */}
              <div className="mt-4 flex items-center gap-2">
                <div
                  className={`flex items-center gap-2 px-3 py-1.5 bg-white border-2 ${urgency.border} rounded-lg`}
                >
                  <UrgencyIcon className={`w-4 h-4 ${urgency.color}`} />
                  <span className={`text-sm font-semibold ${urgency.color}`}>
                    {urgency.label} - {urgency.labelEn}
                  </span>
                </div>
                {diagnosed.affectedArea && (
                  <div className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg">
                    <span className="text-sm text-gray-700">
                      المساحة المتأثرة: {diagnosed.affectedArea.toFixed(1)}%
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Disease Details */}
            <div className="p-6 space-y-6">
              {/* Symptoms */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-gray-600" />
                  الأعراض
                </h4>
                <ul className="space-y-1">
                  {diagnosed.disease.symptomsAr.map((symptom, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                      <span className="text-green-500 mt-1">•</span>
                      <span>{symptom}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Spread Estimation */}
              {diagnosed.estimatedSpread && (
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <h4 className="font-semibold text-orange-900 mb-2">
                    تقدير الانتشار
                  </h4>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-xs text-orange-700">حالياً</p>
                      <p className="text-lg font-bold text-orange-900">
                        {diagnosed.estimatedSpread.current.toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-orange-700">
                        متوقع بعد {diagnosed.estimatedSpread.days} أيام
                      </p>
                      <p className="text-lg font-bold text-orange-900">
                        {diagnosed.estimatedSpread.projected.toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-orange-700">معدل الانتشار</p>
                      <p className="text-lg font-bold text-orange-900">
                        {(
                          (diagnosed.estimatedSpread.projected -
                            diagnosed.estimatedSpread.current) /
                          diagnosed.estimatedSpread.days
                        ).toFixed(1)}
                        % يومياً
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Recommended Treatments */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Package className="w-5 h-5 text-gray-600" />
                  العلاجات الموصى بها
                </h4>
                <div className="space-y-3">
                  {diagnosed.recommendedTreatments.map((treatment: Treatment) => (
                    <div
                      key={treatment.id}
                      className="border border-gray-200 rounded-lg overflow-hidden"
                    >
                      <button
                        onClick={() =>
                          setExpandedTreatment(
                            expandedTreatment === treatment.id ? null : treatment.id
                          )
                        }
                        className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors flex items-center justify-between"
                      >
                        <div className="text-right">
                          <p className="font-medium text-gray-900">
                            {treatment.nameAr}
                          </p>
                          <p className="text-sm text-gray-600">{treatment.name}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-1 rounded text-xs font-medium ${
                              treatment.type === 'chemical'
                                ? 'bg-purple-100 text-purple-700'
                                : treatment.type === 'biological'
                                ? 'bg-green-100 text-green-700'
                                : treatment.type === 'cultural'
                                ? 'bg-blue-100 text-blue-700'
                                : 'bg-gray-100 text-gray-700'
                            }`}
                          >
                            {treatment.type === 'chemical'
                              ? 'كيميائي'
                              : treatment.type === 'biological'
                              ? 'حيوي'
                              : treatment.type === 'cultural'
                              ? 'ثقافي'
                              : 'وقائي'}
                          </span>
                          <ExternalLink className="w-4 h-4 text-gray-400" />
                        </div>
                      </button>

                      {expandedTreatment === treatment.id && (
                        <div className="p-4 space-y-4">
                          {/* Description */}
                          <div>
                            <p className="text-sm text-gray-700">
                              {treatment.descriptionAr}
                            </p>
                          </div>

                          {/* Steps */}
                          <div>
                            <p className="text-sm font-semibold text-gray-900 mb-2">
                              خطوات التطبيق:
                            </p>
                            <ol className="space-y-2">
                              {treatment.stepsAr.map((step, idx) => (
                                <li
                                  key={idx}
                                  className="text-sm text-gray-700 flex items-start gap-2"
                                >
                                  <span className="flex items-center justify-center w-5 h-5 bg-green-100 text-green-700 rounded-full text-xs font-semibold flex-shrink-0 mt-0.5">
                                    {idx + 1}
                                  </span>
                                  <span>{step}</span>
                                </li>
                              ))}
                            </ol>
                          </div>

                          {/* Materials */}
                          {treatment.materials && treatment.materials.length > 0 && (
                            <div>
                              <p className="text-sm font-semibold text-gray-900 mb-2">
                                المواد المطلوبة:
                              </p>
                              <div className="space-y-2">
                                {treatment.materials.map((material, idx) => (
                                  <div
                                    key={idx}
                                    className="flex items-center justify-between p-2 bg-gray-50 rounded"
                                  >
                                    <span className="text-sm text-gray-900">
                                      {material.nameAr}
                                    </span>
                                    <span className="text-sm text-gray-600">
                                      {material.quantityAr}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Timing & Frequency */}
                          {(treatment.timingAr || treatment.frequencyAr) && (
                            <div className="grid grid-cols-2 gap-4">
                              {treatment.timingAr && (
                                <div>
                                  <p className="text-xs text-gray-600 mb-1 flex items-center gap-1">
                                    <Calendar className="w-3 h-3" />
                                    التوقيت
                                  </p>
                                  <p className="text-sm text-gray-900">
                                    {treatment.timingAr}
                                  </p>
                                </div>
                              )}
                              {treatment.frequencyAr && (
                                <div>
                                  <p className="text-xs text-gray-600 mb-1 flex items-center gap-1">
                                    <Clock className="w-3 h-3" />
                                    التكرار
                                  </p>
                                  <p className="text-sm text-gray-900">
                                    {treatment.frequencyAr}
                                  </p>
                                </div>
                              )}
                            </div>
                          )}

                          {/* Precautions */}
                          {treatment.precautionsAr &&
                            treatment.precautionsAr.length > 0 && (
                              <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                                <p className="text-sm font-semibold text-yellow-900 mb-2">
                                  احتياطات:
                                </p>
                                <ul className="space-y-1">
                                  {treatment.precautionsAr.map((precaution, idx) => (
                                    <li
                                      key={idx}
                                      className="text-sm text-yellow-800 flex items-start gap-2"
                                    >
                                      <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                                      <span>{precaution}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                          {/* Cost */}
                          {treatment.cost && (
                            <div className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded">
                              <span className="text-sm font-medium text-blue-900">
                                التكلفة التقديرية:
                              </span>
                              <span className="text-sm font-bold text-blue-900">
                                {treatment.cost.min.toLocaleString('ar-SA')} -{' '}
                                {treatment.cost.max.toLocaleString('ar-SA')}{' '}
                                {treatment.cost.currency}
                              </span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );
      })}

      {/* Expert Consultation CTA */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-900">
              هل تحتاج إلى رأي خبير؟
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              يمكنك طلب استشارة من خبير زراعي للحصول على توصيات مخصصة
            </p>
          </div>
          <button
            onClick={handleRequestConsultation}
            disabled={requestConsultation.isPending}
            className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            {requestConsultation.isPending ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                جاري الإرسال...
              </>
            ) : (
              <>
                <CheckCircle2 className="w-5 h-5" />
                طلب استشارة
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DiagnosisResult;
