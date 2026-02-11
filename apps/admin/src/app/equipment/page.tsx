"use client";

// Equipment Management Page - Placeholder
// صفحة إدارة المعدات

import Header from "@/components/layout/Header";
import { Wrench, Truck, Activity, DollarSign } from "lucide-react";

export default function EquipmentPage() {
  return (
    <div className="p-6">
      <Header title="إدارة المعدات" subtitle="قريباً - Full CRUD Implementation Coming Soon" />

      <div className="mt-6 bg-white rounded-xl p-8 border border-gray-100 text-center">
        <div className="w-20 h-20 bg-sahool-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Wrench className="w-10 h-10 text-sahool-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">صفحة إدارة المعدات</h2>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          هذه الصفحة قيد التطوير حالياً. سيتم إضافة وظائف CRUD الكاملة قريباً لإدارة المعدات الزراعية.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 max-w-4xl mx-auto">
          <div className="p-6 bg-gray-50 rounded-lg">
            <Truck className="w-8 h-8 text-blue-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">تتبع المعدات</h3>
            <p className="text-sm text-gray-600">
              تسجيل ومتابعة جميع المعدات والآلات الزراعية
            </p>
          </div>
          
          <div className="p-6 bg-gray-50 rounded-lg">
            <Activity className="w-8 h-8 text-green-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">جدولة الصيانة</h3>
            <p className="text-sm text-gray-600">
              جدولة الصيانة الدورية وتتبع ساعات التشغيل
            </p>
          </div>
          
          <div className="p-6 bg-gray-50 rounded-lg">
            <DollarSign className="w-8 h-8 text-yellow-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">إدارة التكاليف</h3>
            <p className="text-sm text-gray-600">
              متابعة تكاليف الشراء والصيانة والتشغيل
            </p>
          </div>
        </div>

        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg inline-block">
          <p className="text-sm text-blue-800">
            <strong>API Integration:</strong> equipmentService from /lib/api/services
          </p>
        </div>
      </div>
    </div>
  );
}
