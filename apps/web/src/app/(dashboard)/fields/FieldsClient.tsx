'use client';

/**
 * SAHOOL Fields Page Client Component
 * صفحة الحقول
 */

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { FieldsList } from '@/features/fields';
import { FieldWizard } from '@/features/fields/components/wizard/FieldWizard';
import { Modal } from '@/components/ui/modal';
import { Plus } from 'lucide-react';

export default function FieldsClient() {
  const router = useRouter();
  const t = useTranslations('fields');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const handleFieldClick = (fieldId: string) => {
    router.push(`/fields/${fieldId}`);
  };

  const handleCreateClick = () => {
    setShowCreateModal(true);
  };

  const handleCloseModal = () => {
    setShowCreateModal(false);
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
      <FieldsList onFieldClick={handleFieldClick} onCreateClick={handleCreateClick} />

      {/* Create Field Wizard Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={handleCloseModal}
        size="full"
        showCloseButton={true}
      >
        <FieldWizard onClose={handleCloseModal} />
      </Modal>
    </div>
  );
}
