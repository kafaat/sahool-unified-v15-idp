'use client';

import React from 'react';
import type { WizardData } from '../useWizardState';

interface Step4Props {
  data: WizardData;
  update: <K extends keyof WizardData>(key: K, value: WizardData[K]) => void;
}

/** Shared crop <optgroup> elements — matches FieldForm.tsx crop list exactly */
function CropOptions() {
  return (
    <>
      <optgroup label="🍎 الفواكه (Fruits)">
        {['تفاح','أفوكادو','موز','توت','توت أسود','توت أزرق','كرز','حمضيات','توت بري','قشطة','تمر','تين','عنب زبيب','عنب نبيذ','عنب مائدة','كيوي','ليمون','ليتشي','مانجو','شمام','نكتارين','زيتون','برتقال','خوخ','كمثرى','أناناس','برقوق','رمان','توت العليق','فراولة','سوجاربي','بطيخ'].map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </optgroup>
      <optgroup label="🥬 الخضروات (Vegetables)">
        {['فلفل أناهايم','خرشوف','هليون','فاصوليا طازجة','فلفل رومي','فول طازج','بروكلي','كرنب بروكسل','ملفوف','جزر','قرنبيط','كرفس','هندباء ورقي','هندباء جذر','ملفوف صيني','خيار مخلل','خيار تقطيع','باذنجان','أنديف','ثوم','بصل أخضر','خس رأس','فلفل هالابينيو','كيل','خس ورقي','كراث','نعناع','بصل','بازلاء طازجة','فلفل بوبلانو','بطاطس','قرع','فجل','فلفل سيرانو','سبانخ','ذرة حلوة','بطاطا حلوة','طماطم مكسيكية','طماطم'].map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </optgroup>
      <optgroup label="🌾 الحبوب والبقوليات (Grains & Legumes)">
        {['شعير','فاصوليا جافة','فول جاف','ذرة','عدس','دخن','شوفان','فول سوداني','بازلاء جافة','فشار','كينوا','أرز','ذرة بذور','ذرة رفيعة','فول الصويا','تيف','قمح','قمح شتوي'].map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </optgroup>
      <optgroup label="📌 محاصيل أخرى">
        {['برسيم / فصة','لوز','كاكاو','قهوة','كزبرة','قطن','أوكالبتوس','عشب','عشب المراعي','بندق','قنب','جنجل','مكاديميا','خردل','بيكان','فستق','حور','كانولا','ورد','قصب السكر','دوار الشمس','تبغ','توليب','عشب الملاعب','جوز'].map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </optgroup>
    </>
  );
}

export function Step4Crop({ data, update }: Step4Props) {
  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="w-full max-w-lg space-y-6">
        <div className="text-center mb-2">
          <h3 className="text-xl font-bold text-gray-900">المحصول</h3>
          <p className="text-sm text-gray-500 mt-1">حدد نوع المحصول والمحصول السابق</p>
        </div>

        {/* Current crop */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            نوع المحصول
          </label>
          <select
            value={data.cropType}
            onChange={(e) => update('cropType', e.target.value)}
            dir="rtl"
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-base focus:outline-none focus:border-blue-500 transition-colors bg-white"
          >
            <option value="">— اختر نوع المحصول —</option>
            <CropOptions />
          </select>
        </div>

        {/* Previous crop */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            المحصول السابق
            <span className="text-gray-400 font-normal mr-2">(اختياري)</span>
          </label>
          <select
            value={data.previousCrop}
            onChange={(e) => update('previousCrop', e.target.value)}
            dir="rtl"
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-base focus:outline-none focus:border-blue-500 transition-colors bg-white"
          >
            <option value="">— لا يوجد / غير محدد —</option>
            <CropOptions />
          </select>
          <p className="mt-1.5 text-xs text-gray-400">
            يساعد في تحسين توصيات التسميد ودورة المحاصيل
          </p>
        </div>
      </div>
    </div>
  );
}
