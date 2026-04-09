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
import { useCreateField } from '@/features/fields/hooks/useFieldMutations';
import { Modal } from '@/components/ui/modal';
import { Plus } from 'lucide-react';
import { ErrorTracking } from '@/lib/monitoring/error-tracking';
import { useToast } from '@/components/ui/toast';
import { fieldsApi } from '@/features/fields/api';
import { useAuth } from '@/stores/auth.store';

export default function FieldsClient() {
  const router = useRouter();
  const t = useTranslations('fields');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const { showToast } = useToast();
  const createField = useCreateField();
  const { user } = useAuth();

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

      const createdField = await createField.mutateAsync({ data, tenantId: user?.tenant_id });

      showToast({
        type: 'success',
        message: t('createSuccess'),
      });
      setShowCreateModal(false);

      // Fire-and-forget KPI fetch — non-blocking
      if (createdField?.centroid?.coordinates) {
        const [lng, lat] = createdField.centroid.coordinates;
        fieldsApi.triggerKpiRefresh(createdField.id, lat, lng, user?.tenant_id).catch(() => {/* silent */});
      }

      router.push(`/fields/${createdField.id}`);
    } catch (error) {
      ErrorTracking.captureError(
        error instanceof Error ? error : new Error('Failed to create field'),
        undefined,
        { data }
      );

      // Parse bilingual error message if available
      let errorMessage = t('createFailed');
      if (error instanceof Error) {
        try {
          const errorData = JSON.parse(error.message);
          errorMessage = errorData.messageAr || errorData.message || errorMessage;
        } catch {
          // Use default error message
        }
      }

      showToast({
        type: 'error',
        message: errorMessage,
      });
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
            disabled={createField.isPending}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-50"
          >
            <Plus className="w-5 h-5" />
            <span className="font-medium">{t('addNewField')}</span>
          </button>
        </div>
      </div>

      {/* Fields List */}
      <FieldsList onFieldClick={handleFieldClick} onCreateClick={handleCreateClick} />

      {/* Create Field Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={handleCloseModal}
        titleAr={t('addNewField')}
        title={t('createNewField')}
        size="full"
      >
        <FieldForm
          onSubmit={handleSubmit}
          onCancel={handleCloseModal}
          isSubmitting={createField.isPending}
        />
      </Modal>
    </div>
  );
}
