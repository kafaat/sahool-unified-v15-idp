'use client';

/**
 * SAHOOL Fields Page Client Component
 * صفحة الحقول
 */

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { FieldsList } from '@/features/fields';
import { FieldForm } from '@/features/fields/components/FieldForm';
import type { FieldFormData } from '@/features/fields/types';
import { Modal } from '@/components/ui/modal';
import { Plus } from 'lucide-react';
import { ErrorTracking } from '@/lib/monitoring/error-tracking';
import { logger } from '@/lib/logger';

export default function FieldsClient() {
  const router = useRouter();
  const t = useTranslations('fields');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const handleFieldClick = (fieldId: string) => {
    ErrorTracking.addBreadcrumb({
      type: 'click',
      category: 'ui',
      message: 'Field clicked',
      data: { fieldId },
    });

    // Navigate to field details page
    router.push(`/fields/${fieldId}`);
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
      alert(t('createSuccess'));
      setShowCreateModal(false);
    } catch (error) {
      ErrorTracking.captureError(
        error instanceof Error ? error : new Error('Failed to create field'),
        undefined,
        { data }
      );
      alert(t('createFailed'));
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('title')}</h1>
            <p className="text-gray-600">{t('management')}</p>
          </div>
          <button
            onClick={handleCreateClick}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
          >
            <Plus className="w-5 h-5" />
            <span className="font-medium">{t('addNewField')}</span>
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
        titleAr={t('addNewField')}
        title={t('createNewField')}
      >
        <FieldForm
          onSubmit={handleSubmit}
          onCancel={handleCloseModal}
        />
      </Modal>
    </div>
  );
}
