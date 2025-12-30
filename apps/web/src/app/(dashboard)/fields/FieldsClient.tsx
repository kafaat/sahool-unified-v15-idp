'use client';

/**
 * SAHOOL Fields Page Client Component
 * صفحة الحقول
 */

import React, { useState } from 'react';
import { FieldsList } from '@/features/fields';
import { FieldForm } from '@/features/fields/components/FieldForm';
import { Modal } from '@/components/ui/modal';
import { Plus } from 'lucide-react';
import { ErrorTracking } from '@/lib/monitoring/error-tracking';

export default function FieldsClient() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [, setSelectedFieldId] = useState<string | null>(null);

  const handleFieldClick = (fieldId: string) => {
    setSelectedFieldId(fieldId);
    ErrorTracking.addBreadcrumb({
      type: 'click',
      category: 'ui',
      message: 'Field clicked',
      data: { fieldId },
    });
    // Navigate to field details or open modal
    // TODO: Implement field details navigation
  };

  const handleCreateClick = () => {
    setShowCreateModal(true);
  };

  const handleCloseModal = () => {
    setShowCreateModal(false);
  };

  const handleSubmit = async (data: any) => {
    try {
      ErrorTracking.addBreadcrumb({
        type: 'click',
        category: 'ui',
        message: 'Creating field',
        data: { fieldName: data?.name },
      });
      // TODO: Implement actual field creation
      // For now, just close the modal
      setShowCreateModal(false);
    } catch (error) {
      ErrorTracking.captureError(
        error instanceof Error ? error : new Error('Failed to create field'),
        undefined,
        { data }
      );
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
    </div>
  );
}
