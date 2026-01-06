'use client';

/**
 * SAHOOL Invite Member Dialog Component
 * مكون نافذة دعوة عضو
 */

import React, { useState } from 'react';
import { Send, X } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { RoleSelector } from './RoleSelector';
import { useInviteMember } from '../hooks/useTeam';
import { Role, InviteRequest } from '../types/team';

interface InviteMemberDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

export const InviteMemberDialog: React.FC<InviteMemberDialogProps> = ({
  isOpen,
  onClose,
}) => {
  const inviteMutation = useInviteMember();

  const [formData, setFormData] = useState<InviteRequest>({
    email: '',
    firstName: '',
    lastName: '',
    role: Role.VIEWER,
    phone: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = <K extends keyof InviteRequest>(
    field: K,
    value: InviteRequest[K]
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error when user types
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.email) {
      newErrors.email = 'البريد الإلكتروني مطلوب';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'البريد الإلكتروني غير صالح';
    }

    if (!formData.firstName) {
      newErrors.firstName = 'الاسم الأول مطلوب';
    }

    if (!formData.lastName) {
      newErrors.lastName = 'اسم العائلة مطلوب';
    }

    if (formData.phone && !/^\+?[0-9]{10,15}$/.test(formData.phone.replace(/\s/g, ''))) {
      newErrors.phone = 'رقم الهاتف غير صالح';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      await inviteMutation.mutateAsync(formData);

      // Reset form and close dialog
      setFormData({
        email: '',
        firstName: '',
        lastName: '',
        role: Role.VIEWER,
        phone: '',
      });
      onClose();
    } catch (error) {
      console.error('Failed to invite member:', error);
      setErrors({ submit: 'فشل في إرسال الدعوة. الرجاء المحاولة مرة أخرى.' });
    }
  };

  const handleClose = () => {
    setFormData({
      email: '',
      firstName: '',
      lastName: '',
      role: Role.VIEWER,
      phone: '',
    });
    setErrors({});
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Invite Team Member"
      titleAr="دعوة عضو فريق"
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            البريد الإلكتروني <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => handleChange('email', e.target.value)}
            className={`w-full px-4 py-2 border-2 rounded-lg focus:outline-none ${
              errors.email ? 'border-red-500' : 'border-gray-200 focus:border-blue-500'
            }`}
            placeholder="example@sahool.sa"
            dir="ltr"
          />
          {errors.email && (
            <p className="text-red-500 text-sm mt-1">{errors.email}</p>
          )}
        </div>

        {/* Name Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* First Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              الاسم الأول <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.firstName}
              onChange={(e) => handleChange('firstName', e.target.value)}
              className={`w-full px-4 py-2 border-2 rounded-lg focus:outline-none ${
                errors.firstName ? 'border-red-500' : 'border-gray-200 focus:border-blue-500'
              }`}
              placeholder="أحمد"
            />
            {errors.firstName && (
              <p className="text-red-500 text-sm mt-1">{errors.firstName}</p>
            )}
          </div>

          {/* Last Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              اسم العائلة <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.lastName}
              onChange={(e) => handleChange('lastName', e.target.value)}
              className={`w-full px-4 py-2 border-2 rounded-lg focus:outline-none ${
                errors.lastName ? 'border-red-500' : 'border-gray-200 focus:border-blue-500'
              }`}
              placeholder="السعيد"
            />
            {errors.lastName && (
              <p className="text-red-500 text-sm mt-1">{errors.lastName}</p>
            )}
          </div>
        </div>

        {/* Phone (Optional) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            رقم الهاتف (اختياري)
          </label>
          <input
            type="tel"
            value={formData.phone}
            onChange={(e) => handleChange('phone', e.target.value)}
            className={`w-full px-4 py-2 border-2 rounded-lg focus:outline-none ${
              errors.phone ? 'border-red-500' : 'border-gray-200 focus:border-blue-500'
            }`}
            placeholder="+966501234567"
            dir="ltr"
          />
          {errors.phone && (
            <p className="text-red-500 text-sm mt-1">{errors.phone}</p>
          )}
        </div>

        {/* Role */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            الدور <span className="text-red-500">*</span>
          </label>
          <RoleSelector
            value={formData.role}
            onChange={(role) => handleChange('role', role)}
          />
        </div>

        {/* Submit Error */}
        {errors.submit && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {errors.submit}
          </div>
        )}

        {/* Footer Actions */}
        <ModalFooter className="px-0 py-0 bg-transparent border-0">
          <Button
            type="button"
            variant="ghost"
            onClick={handleClose}
            disabled={inviteMutation.isPending}
          >
            <X className="w-4 h-4 ml-2" />
            إلغاء
          </Button>
          <Button
            type="submit"
            variant="primary"
            isLoading={inviteMutation.isPending}
            disabled={inviteMutation.isPending}
          >
            <Send className="w-4 h-4 ml-2" />
            {inviteMutation.isPending ? 'جاري الإرسال...' : 'إرسال الدعوة'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
};

export default InviteMemberDialog;
