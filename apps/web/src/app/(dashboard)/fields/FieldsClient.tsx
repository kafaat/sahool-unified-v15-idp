'use client';

/**
 * SAHOOL Fields Page Client Component
 * صفحة الحقول
 */

import React, { useState } from 'react';
import { FieldsList } from '@/features/fields';
import { FieldForm } from '@/features/fields/components/FieldForm';
import type { FieldFormData } from '@/features/fields/types';
import { Modal } from '@/components/ui/modal';
import { Plus } from 'lucide-react';
import { ErrorTracking } from '@/lib/monitoring/error-tracking';
import { logger } from '@/lib/logger';

export default function FieldsClient() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(null);
  const [showComingSoon, setShowComingSoon] = useState(false);

  const handleFieldClick = (fieldId: string) => {
    setSelectedFieldId(fieldId);
    ErrorTracking.addBreadcrumb({
      type: 'click',
      category: 'ui',
      message: 'Field clicked',
      data: { fieldId },
    });

    // Show coming soon notification for field details
    // When field details page is ready, navigate to: `/fields/${fieldId}`
    setShowComingSoon(true);
    setTimeout(() => setShowComingSoon(false), 3000);
  };

  const handleCreateClick = () => {
    setShowCreateModal(true);
  };

  const handleCloseModal = () => {
    setShowCreateModal(false);
  };

  const handleSubmit = async (data: FieldFormData) => {
    try {
      ErrorTracking.addBreadcrumb({
        type: 'click',
        category: 'ui',
        message: 'Creating field',
        data: { fieldName: data?.name },
      });

      // When backend is ready, implement:
      // const response = await fetch('/api/fields', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(data),
      // });
      // if (!response.ok) throw new Error('Failed to create field');
      // const newField = await response.json();

      // For now, simulate successful creation
      logger.log('Field creation data:', data);
      alert('تم إنشاء الحقل بنجاح | Field created successfully (mock)');
      setShowCreateModal(false);
    } catch (error) {
      ErrorTracking.captureError(
        error instanceof Error ? error : new Error('Failed to create field'),
        undefined,
        { data }
      );
      alert('فشل في إنشاء الحقل | Failed to create field');
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">الحقول</h1>
            <p className="text-gray-600">Fields Management</p>
          </div>
          <button
            onClick={handleCreateClick}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
          >
            <Plus className="w-5 h-5" />
            <span className="font-medium">إضافة حقل جديد</span>
          </button>
        </div>
      </div>

      {/* Fields List */}
      <FieldsList
        onFieldClick={handleFieldClick}
        onCreateClick={handleCreateClick}
      />

      {/* Create Field Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={handleCloseModal}
        titleAr="إضافة حقل جديد"
        title="Create New Field"
      >
        <FieldForm
          onSubmit={handleSubmit}
          onCancel={handleCloseModal}
        />
      </Modal>

      {/* Coming Soon Notification */}
      {showComingSoon && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 animate-fade-in">
          <div className="bg-blue-600 text-white px-6 py-4 rounded-lg shadow-xl border-2 border-blue-500">
            <div className="flex items-center gap-3">
              <div className="text-2xl">🚀</div>
              <div>
                <p className="font-bold">قريباً: صفحة تفاصيل الحقل</p>
                <p className="text-sm opacity-90">Coming Soon: Field Details Page</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
