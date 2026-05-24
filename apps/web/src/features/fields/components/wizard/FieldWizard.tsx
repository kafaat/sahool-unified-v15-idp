'use client';

/**
 * FieldWizard — 6-step guided field creation
 * معالج إنشاء الحقل — 6 خطوات
 *
 * Step 1: Field Location   — farm select + full-height Leaflet map bbox drawing
 * Step 2: Field Info       — name + computed area
 * Step 3: Growing Season   — season name, planting date, harvest date
 * Step 4: Crop             — crop type + previous crop
 * Step 5: Soil             — soil type + visual preview
 * Step 6: Irrigation       — irrigation type (card-style)
 *
 * On save: calls createField then optionally createCropSeason.
 */

import React from 'react';
import { useRouter } from 'next/navigation';
import { useWizardState } from './useWizardState';
import { WizardStepper } from './WizardStepper';
import { WizardNav } from './WizardNav';
import { Step1Location } from './steps/Step1Location';
import { Step2Info } from './steps/Step2Info';
import { Step3Season } from './steps/Step3Season';
import { Step4Crop } from './steps/Step4Crop';
import { Step5Soil } from './steps/Step5Soil';
import { Step6Irrigation } from './steps/Step6Irrigation';
import { useCreateField } from '../../hooks/useFieldMutations';
import { cropSeasonsApi, type CreateCropSeasonPayload } from '../../api/crop-seasons-api';
import { fieldsApi } from '../../api';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/stores/auth.store';
import { ErrorTracking } from '@/lib/monitoring/error-tracking';
import { logger } from '@/lib/logger';

interface FieldWizardProps {
  onClose: () => void;
}

export function FieldWizard({ onClose }: FieldWizardProps) {
  const router = useRouter();
  const { step, data, update, validateStep, canNext, goNext, goPrev } = useWizardState();
  const createField = useCreateField();
  const { showToast } = useToast();
  const { user } = useAuth();

  const stepError = validateStep(step);

  const handleSave = async () => {
    // Validate required steps before submit
    const err1 = validateStep(0);
    if (err1) {
      showToast({ type: 'error', message: err1 });
      return;
    }
    const err2 = validateStep(1);
    if (err2) {
      showToast({ type: 'error', message: err2 });
      return;
    }

    try {
      ErrorTracking.addBreadcrumb({
        type: 'click',
        category: 'ui',
        message: 'Creating field via wizard',
        data: { fieldName: data.name },
      });

      const name = data.name.trim();

      // Build create payload — only include optional fields when non-empty
      const createPayload: Record<string, unknown> = {
        name,
        nameAr: name,
        area: data.area,
        polygon: data.polygon ?? undefined,
      };

      if (data.farmId) createPayload.farmId = data.farmId;
      if (data.cropType) { createPayload.crop = data.cropType; createPayload.cropAr = data.cropType; }
      if (data.soilType) createPayload.soilType = data.soilType;
      if (data.irrigationType) createPayload.irrigationType = data.irrigationType;
      if (data.plantingDate) createPayload.plantingDate = data.plantingDate;
      if (data.harvestDate) createPayload.expectedHarvest = data.harvestDate;
      if (data.previousCrop) createPayload.metadata = { previousCrop: data.previousCrop };

      const createdField = await createField.mutateAsync({
        data: createPayload as never,
        tenantId: user?.tenant_id,
      });

      // Create crop season if any season data was provided
      const hasSeasonData = data.cropType || data.plantingDate || data.seasonName;
      if (hasSeasonData && createdField?.id) {
        try {
          const seasonPayload: CreateCropSeasonPayload = {
            cropType: data.cropType || 'other',
            sowingDate: data.plantingDate || new Date().toISOString().slice(0, 10),
          };
          if (data.harvestDate) seasonPayload.expectedHarvestDate = data.harvestDate;
          if (data.irrigationType) seasonPayload.irrigationType = data.irrigationType;
          if (data.seasonName) seasonPayload.metadata = { seasonName: data.seasonName };

          await cropSeasonsApi.create(createdField.id, seasonPayload);
        } catch (seasonErr) {
          // Non-fatal — field was created, just log the season creation failure
          logger.warn('Crop season creation failed', { error: seasonErr, fieldId: createdField.id });
        }
      }

      showToast({ type: 'success', message: 'تم إنشاء الحقل بنجاح' });
      onClose();

      // Fire-and-forget KPI refresh
      if (createdField?.centroid?.coordinates) {
        const [lng, lat] = createdField.centroid.coordinates;
        fieldsApi.triggerKpiRefresh(createdField.id, lat, lng, user?.tenant_id).catch((error) => {
          logger.warn('KPI refresh failed', { error, fieldId: createdField.id });
        });
      }

      router.push(`/fields/${createdField.id}`);
    } catch (error) {
      ErrorTracking.captureError(
        error instanceof Error ? error : new Error('Failed to create field'),
        undefined,
        { data }
      );

      let errorMessage = 'فشل في إنشاء الحقل';
      if (error && typeof error === 'object') {
        const e = error as { messageAr?: string; message?: string };
        if (e.messageAr) errorMessage = e.messageAr;
        else if (e.message) errorMessage = e.message;
      }
      showToast({ type: 'error', message: errorMessage });
    }
  };

  return (
    <div className="flex flex-col h-full bg-white" dir="rtl">
      {/* Stepper header */}
      <WizardStepper currentStep={step} />

      {/* Step content — fills remaining height */}
      <div className="flex-1 min-h-0 flex flex-col overflow-hidden">
        {step === 0 && (
          <Step1Location
            data={data}
            update={update}
            error={step === 0 && data.polygon === null ? null : stepError}
          />
        )}
        {step === 1 && <Step2Info data={data} update={update} error={stepError} />}
        {step === 2 && <Step3Season data={data} update={update} />}
        {step === 3 && <Step4Crop data={data} update={update} />}
        {step === 4 && <Step5Soil data={data} update={update} />}
        {step === 5 && <Step6Irrigation data={data} update={update} />}
      </div>

      {/* Navigation footer */}
      <WizardNav
        currentStep={step}
        canNext={canNext()}
        isSubmitting={createField.isPending}
        onNext={goNext}
        onPrev={goPrev}
        onSave={handleSave}
      />
    </div>
  );
}
