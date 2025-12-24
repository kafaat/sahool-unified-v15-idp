/**
 * Crop Health Page
 * صفحة صحة المحصول والتشخيص
 */

'use client';

import React, { useState } from 'react';
import { Metadata } from 'next';
import { Camera, Activity } from 'lucide-react';
import { HealthDashboard, DiagnosisTool, DiagnosisResultComponent } from '@/features/crop-health';

export default function CropHealthPage() {
  const [activeView, setActiveView] = useState<'dashboard' | 'diagnosis'>('dashboard');
  const [diagnosisId, setDiagnosisId] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* View Toggle */}
      {!diagnosisId && (
        <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex gap-4" dir="rtl">
              <button
                onClick={() => setActiveView('dashboard')}
                className={`
                  flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-colors
                  ${
                    activeView === 'dashboard'
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }
                `}
              >
                <Activity className="w-5 h-5" />
                <span>لوحة المعلومات</span>
              </button>
              <button
                onClick={() => setActiveView('diagnosis')}
                className={`
                  flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-colors
                  ${
                    activeView === 'diagnosis'
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }
                `}
              >
                <Camera className="w-5 h-5" />
                <span>تشخيص جديد</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {diagnosisId ? (
          <div>
            <button
              onClick={() => setDiagnosisId(null)}
              className="mb-6 text-green-600 hover:text-green-700 font-medium"
              dir="rtl"
            >
              ← العودة
            </button>
            <DiagnosisResultComponent requestId={diagnosisId} />
          </div>
        ) : activeView === 'dashboard' ? (
          <HealthDashboard />
        ) : (
          <DiagnosisTool
            onDiagnosisCreated={(id) => setDiagnosisId(id)}
          />
        )}
      </div>
    </div>
  );
}
