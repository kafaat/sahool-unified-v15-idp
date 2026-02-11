"use client";

// Tasks Management Page - Placeholder
// صفحة إدارة المهام

import Header from "@/components/layout/Header";
import { CheckSquare, Clock, Users, AlertCircle } from "lucide-react";

export default function TasksPage() {
  return (
    <div className="p-6">
      <Header title="إدارة المهام" subtitle="قريباً - Full CRUD Implementation Coming Soon" />

      <div className="mt-6 bg-white rounded-xl p-8 border border-gray-100 text-center">
        <div className="w-20 h-20 bg-sahool-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckSquare className="w-10 h-10 text-sahool-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">صفحة إدارة المهام</h2>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          هذه الصفحة قيد التطوير حالياً. سيتم إضافة وظائف CRUD الكاملة قريباً لإدارة المهام الزراعية.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 max-w-4xl mx-auto">
          <div className="p-6 bg-gray-50 rounded-lg">
            <Clock className="w-8 h-8 text-blue-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">جدولة المهام</h3>
            <p className="text-sm text-gray-600">
              إنشاء وجدولة المهام الزراعية مع تحديد المواعيد والأولويات
            </p>
          </div>
          
          <div className="p-6 bg-gray-50 rounded-lg">
            <Users className="w-8 h-8 text-green-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">تعيين المهام</h3>
            <p className="text-sm text-gray-600">
              تعيين المهام للمستخدمين ومتابعة حالة الإنجاز
            </p>
          </div>
          
          <div className="p-6 bg-gray-50 rounded-lg">
            <AlertCircle className="w-8 h-8 text-yellow-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">التنبيهات</h3>
            <p className="text-sm text-gray-600">
              تنبيهات تلقائية للمهام المتأخرة والقادمة
            </p>
          </div>
        </div>

        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg inline-block">
          <p className="text-sm text-blue-800">
            <strong>API Integration:</strong> taskService from /lib/api/extended-services
          </p>
        </div>
      </div>
    </div>
  );
}
