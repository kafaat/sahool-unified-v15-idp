/**
 * Profile Form Component
 * مكون نموذج الملف الشخصي
 */

'use client';

import React, { useState, useEffect } from 'react';
import { User, MapPin, Building2, Upload, Loader2, Check } from 'lucide-react';
import { useUserProfile, useUpdateProfile, useUploadAvatar } from '../hooks/useSettings';
import type { UpdateProfilePayload } from '../types';
import { logger } from '@/lib/logger';

export const ProfileForm: React.FC = () => {
  const { data: profile, isLoading } = useUserProfile();
  const updateProfile = useUpdateProfile();
  const uploadAvatar = useUploadAvatar();

  const [formData, setFormData] = useState<UpdateProfilePayload>({});
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string>('');

  useEffect(() => {
    if (profile) {
      setFormData({
        name: profile.name,
        nameAr: profile.nameAr,
        phone: profile.phone,
        bio: profile.bio,
        bioAr: profile.bioAr,
        location: profile.location,
        farmDetails: profile.farmDetails,
        language: profile.language,
        timezone: profile.timezone,
        dateFormat: profile.dateFormat,
      });
      if (profile.avatar) {
        setAvatarPreview(profile.avatar);
      }
    }
  }, [profile]);

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAvatarFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // Upload avatar first if changed
      let avatarUrl = profile?.avatar;
      if (avatarFile) {
        avatarUrl = await uploadAvatar.mutateAsync(avatarFile);
      }

      // Update profile
      await updateProfile.mutateAsync({
        ...formData,
        avatar: avatarUrl,
      });

      alert('تم تحديث الملف الشخصي بنجاح');
    } catch (err) {
      alert('حدث خطأ أثناء تحديث الملف الشخصي');
      logger.error(err);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-12 h-12 text-green-500 animate-spin" />
      </div>
    );
  }

  const isSaving = updateProfile.isPending || uploadAvatar.isPending;

  return (
    <form onSubmit={handleSubmit} className="space-y-8" dir="rtl">
      {/* Avatar Upload */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-4">
          الصورة الشخصية
        </label>
        <div className="flex items-center gap-6">
          <div className="relative">
            {avatarPreview ? (
              <img
                src={avatarPreview}
                alt="Profile"
                className="w-24 h-24 rounded-full object-cover border-4 border-gray-200"
              />
            ) : (
              <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center">
                <User className="w-12 h-12 text-gray-400" />
              </div>
            )}
            <label className="absolute bottom-0 left-0 p-2 bg-green-500 text-white rounded-full cursor-pointer hover:bg-green-600 transition-colors">
              <Upload className="w-4 h-4" />
              <input
                type="file"
                accept="image/*"
                onChange={handleAvatarChange}
                className="hidden"
                disabled={isSaving}
              />
            </label>
          </div>
          <div>
            <p className="text-sm text-gray-600">
              صورة بحجم 400x400 بكسل على الأقل
            </p>
            <p className="text-xs text-gray-500 mt-1">
              JPG, PNG, or GIF (max 2MB)
            </p>
          </div>
        </div>
      </div>

      {/* Basic Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            الاسم بالعربية *
          </label>
          <input
            type="text"
            value={formData.nameAr || ''}
            onChange={(e) => setFormData({ ...formData, nameAr: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
            disabled={isSaving}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Name in English *
          </label>
          <input
            type="text"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
            disabled={isSaving}
            dir="ltr"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            رقم الهاتف
          </label>
          <input
            type="tel"
            value={formData.phone || ''}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            disabled={isSaving}
            dir="ltr"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            اللغة المفضلة
          </label>
          <select
            value={formData.language || 'ar'}
            onChange={(e) =>
              setFormData({ ...formData, language: e.target.value as 'ar' | 'en' | 'both' })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            disabled={isSaving}
          >
            <option value="ar">العربية</option>
            <option value="en">English</option>
            <option value="both">Both / كلاهما</option>
          </select>
        </div>
      </div>

      {/* Bio */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          نبذة عنك
        </label>
        <textarea
          value={formData.bioAr || ''}
          onChange={(e) => setFormData({ ...formData, bioAr: e.target.value })}
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          placeholder="اكتب نبذة مختصرة عنك وعن خبرتك في الزراعة..."
          disabled={isSaving}
        />
      </div>

      {/* Location */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <MapPin className="w-5 h-5 text-gray-600" />
          الموقع
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              المدينة
            </label>
            <input
              type="text"
              value={formData.location?.cityAr || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  location: { ...formData.location!, cityAr: e.target.value },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={isSaving}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              المنطقة
            </label>
            <input
              type="text"
              value={formData.location?.regionAr || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  location: { ...formData.location!, regionAr: e.target.value },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={isSaving}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              الدولة
            </label>
            <input
              type="text"
              value={formData.location?.countryAr || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  location: { ...formData.location!, countryAr: e.target.value },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={isSaving}
            />
          </div>
        </div>
      </div>

      {/* Farm Details */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Building2 className="w-5 h-5 text-gray-600" />
          تفاصيل المزرعة
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              اسم المزرعة
            </label>
            <input
              type="text"
              value={formData.farmDetails?.nameAr || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  farmDetails: { ...formData.farmDetails!, nameAr: e.target.value },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={isSaving}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              إجمالي المساحة (هكتار)
            </label>
            <input
              type="number"
              value={formData.farmDetails?.totalArea || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  farmDetails: {
                    ...formData.farmDetails!,
                    totalArea: parseFloat(e.target.value),
                  },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={isSaving}
              step="0.1"
              min="0"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              نوع المزرعة
            </label>
            <select
              value={formData.farmDetails?.farmType || 'individual'}
              onChange={(e) => {
                type FarmType = 'individual' | 'family' | 'company' | 'cooperative';
                const value = e.target.value as FarmType;
                setFormData({
                  ...formData,
                  farmDetails: {
                    ...formData.farmDetails!,
                    farmType: value,
                  },
                });
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={isSaving}
            >
              <option value="individual">فردية</option>
              <option value="family">عائلية</option>
              <option value="company">شركة</option>
              <option value="cooperative">تعاونية</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              سنة التأسيس
            </label>
            <input
              type="number"
              value={formData.farmDetails?.establishedYear || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  farmDetails: {
                    ...formData.farmDetails!,
                    establishedYear: parseInt(e.target.value),
                  },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={isSaving}
              min="1900"
              max={new Date().getFullYear()}
            />
          </div>
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex justify-end gap-4 pt-6 border-t border-gray-200">
        <button
          type="button"
          onClick={() => {
            if (profile) {
              setFormData({
                name: profile.name,
                nameAr: profile.nameAr,
                phone: profile.phone,
                bio: profile.bio,
                bioAr: profile.bioAr,
                location: profile.location,
                farmDetails: profile.farmDetails,
              });
              setAvatarFile(null);
              setAvatarPreview(profile.avatar || '');
            }
          }}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          disabled={isSaving}
        >
          إلغاء
        </button>
        <button
          type="submit"
          disabled={isSaving}
          className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {isSaving ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              جاري الحفظ...
            </>
          ) : (
            <>
              <Check className="w-5 h-5" />
              حفظ التغييرات
            </>
          )}
        </button>
      </div>
    </form>
  );
};

export default ProfileForm;
