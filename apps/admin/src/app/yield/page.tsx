// Sahool Admin Dashboard - Yield Prediction Calculator
// حاسبة التنبؤ بالإنتاجية

"use client";

import { useState } from "react";
import { apiClient, API_URLS } from "@/lib/api";
import {
  TrendingUp,
  Loader2,
  DollarSign,
  Scale,
  Droplets,
  Thermometer,
} from "lucide-react";
import { logger } from "../../lib/logger";

interface YieldPrediction {
  prediction_id: string;
  crop_type: string;
  crop_name_ar: string;
  area_hectares: number;
  predicted_yield_tons: number;
  predicted_yield_per_hectare: number;
  yield_range_min: number;
  yield_range_max: number;
  estimated_revenue_usd: number;
  estimated_revenue_yer: number;
  confidence_percent: number;
  factors_applied: string[];
  recommendations: string[];
}

const CROP_OPTIONS = [
  { value: "wheat", label: "قمح", icon: "🌾" },
  { value: "corn", label: "ذرة", icon: "🌽" },
  { value: "tomato", label: "طماطم", icon: "🍅" },
  { value: "potato", label: "بطاطس", icon: "🥔" },
  { value: "coffee", label: "بن يمني", icon: "☕" },
  { value: "date_palm", label: "نخيل (تمر)", icon: "🌴" },
  { value: "mango", label: "مانجو", icon: "🥭" },
  { value: "sorghum", label: "ذرة رفيعة", icon: "🌾" },
  { value: "banana", label: "موز", icon: "🍌" },
  { value: "grape", label: "عنب", icon: "🍇" },
];

const SOIL_OPTIONS = [
  { value: "poor", label: "ضعيفة" },
  { value: "medium", label: "متوسطة" },
  { value: "good", label: "ممتازة" },
];

const IRRIGATION_OPTIONS = [
  { value: "rain-fed", label: "اعتماد على الأمطار" },
  { value: "flood", label: "ري غمر" },
  { value: "sprinkler", label: "ري رشاش" },
  { value: "drip", label: "ري بالتنقيط" },
  { value: "smart", label: "ري ذكي" },
];

export default function YieldPage() {
  const [formData, setFormData] = useState({
    area_hectares: 10,
    crop_type: "wheat",
    avg_rainfall: 450,
    avg_temperature: 25,
    soil_quality: "medium",
    irrigation_type: "rain-fed",
  });

  const [prediction, setPrediction] = useState<YieldPrediction | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [_error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.post(
        `${API_URLS.yieldPrediction}/v1/predict`,
        formData,
      );
      setPrediction(response.data);
    } catch (err) {
      logger.error("Prediction failed:", err);
      // Mock prediction for development
      setPrediction({
        prediction_id: "mock-1",
        crop_type: formData.crop_type,
        crop_name_ar:
          CROP_OPTIONS.find((c) => c.value === formData.crop_type)?.label || "",
        area_hectares: formData.area_hectares,
        predicted_yield_tons:
          formData.area_hectares *
          2.5 *
          (formData.soil_quality === "good" ? 1.2 : 1),
        predicted_yield_per_hectare: 2.5,
        yield_range_min: formData.area_hectares * 2.1,
        yield_range_max: formData.area_hectares * 2.9,
        estimated_revenue_usd: formData.area_hectares * 2.5 * 350,
        estimated_revenue_yer: formData.area_hectares * 2.5 * 350 * 535,
        confidence_percent: 85,
        factors_applied: ["تربة متوسطة", "أمطار مثالية (+10%)"],
        recommendations: [
          "فكر في تركيب نظام ري بالتنقيط لزيادة الإنتاج 15-20%",
        ],
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat("ar-YE").format(Math.round(num));
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <TrendingUp className="text-green-600" />
          حاسبة التنبؤ بالإنتاجية
        </h1>
        <p className="text-gray-500 mt-1">
          توقع كمية المحصول والعائد المالي باستخدام الذكاء الاصطناعي
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-semibold mb-6">بيانات الحقل</h2>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Crop Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                نوع المحصول
              </label>
              <div className="grid grid-cols-5 gap-2">
                {CROP_OPTIONS.map((crop) => (
                  <button
                    key={crop.value}
                    type="button"
                    onClick={() =>
                      setFormData({ ...formData, crop_type: crop.value })
                    }
                    className={`p-3 rounded-xl text-center transition-all ${
                      formData.crop_type === crop.value
                        ? "bg-green-100 border-2 border-green-500"
                        : "bg-gray-50 border border-gray-200 hover:bg-gray-100"
                    }`}
                  >
                    <div className="text-2xl mb-1">{crop.icon}</div>
                    <div className="text-xs">{crop.label}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Area */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Scale className="inline w-4 h-4 ml-1" />
                المساحة (هكتار)
              </label>
              <input
                type="number"
                value={formData.area_hectares}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    area_hectares: parseFloat(e.target.value) || 0,
                  })
                }
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                min="0.1"
                step="0.1"
              />
            </div>

            {/* Weather */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Droplets className="inline w-4 h-4 ml-1" />
                  متوسط الأمطار (مم)
                </label>
                <input
                  type="number"
                  value={formData.avg_rainfall}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      avg_rainfall: parseFloat(e.target.value) || 0,
                    })
                  }
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Thermometer className="inline w-4 h-4 ml-1" />
                  متوسط الحرارة (°C)
                </label>
                <input
                  type="number"
                  value={formData.avg_temperature}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      avg_temperature: parseFloat(e.target.value) || 0,
                    })
                  }
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Soil & Irrigation */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  جودة التربة
                </label>
                <select
                  value={formData.soil_quality}
                  onChange={(e) =>
                    setFormData({ ...formData, soil_quality: e.target.value })
                  }
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  {SOIL_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  نوع الري
                </label>
                <select
                  value={formData.irrigation_type}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      irrigation_type: e.target.value,
                    })
                  }
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  {IRRIGATION_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-green-600 text-white py-4 rounded-xl font-semibold hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  جاري الحساب...
                </>
              ) : (
                <>
                  <TrendingUp className="w-5 h-5" />
                  احسب الإنتاجية المتوقعة
                </>
              )}
            </button>
          </form>
        </div>

        {/* Results */}
        <div>
          {prediction ? (
            <div className="space-y-6">
              {/* Main Result Card */}
              <div className="bg-gradient-to-br from-green-500 to-green-700 rounded-2xl p-6 text-white">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-3xl">
                    {
                      CROP_OPTIONS.find((c) => c.value === prediction.crop_type)
                        ?.icon
                    }
                  </span>
                  <div>
                    <h3 className="text-xl font-bold">
                      {prediction.crop_name_ar}
                    </h3>
                    <p className="text-green-100">
                      {prediction.area_hectares} هكتار
                    </p>
                  </div>
                </div>

                <div className="bg-white/20 rounded-xl p-4 mb-4">
                  <div className="text-green-100 text-sm mb-1">
                    الإنتاج المتوقع
                  </div>
                  <div className="text-4xl font-bold">
                    {formatNumber(prediction.predicted_yield_tons)}{" "}
                    <span className="text-xl">طن</span>
                  </div>
                  <div className="text-green-200 text-sm mt-1">
                    ({prediction.yield_range_min.toFixed(1)} -{" "}
                    {prediction.yield_range_max.toFixed(1)} طن)
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/10 rounded-xl p-3">
                    <div className="text-green-100 text-xs mb-1">
                      العائد بالدولار
                    </div>
                    <div className="text-xl font-bold flex items-center gap-1">
                      <DollarSign className="w-5 h-5" />
                      {formatNumber(prediction.estimated_revenue_usd)}
                    </div>
                  </div>
                  <div className="bg-white/10 rounded-xl p-3">
                    <div className="text-green-100 text-xs mb-1">
                      العائد بالريال
                    </div>
                    <div className="text-xl font-bold">
                      {formatNumber(prediction.estimated_revenue_yer)} ر.ي
                    </div>
                  </div>
                </div>

                <div className="mt-4 flex items-center justify-between">
                  <span className="text-green-100">نسبة الثقة</span>
                  <span className="bg-white/20 px-3 py-1 rounded-full text-sm font-medium">
                    {prediction.confidence_percent}%
                  </span>
                </div>
              </div>

              {/* Factors */}
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                <h3 className="font-semibold mb-4">العوامل المؤثرة</h3>
                <div className="space-y-2">
                  {prediction.factors_applied.map((factor, idx) => (
                    <div
                      key={idx}
                      className={`px-3 py-2 rounded-lg text-sm ${
                        factor.includes("+")
                          ? "bg-green-50 text-green-700"
                          : factor.includes("-")
                            ? "bg-red-50 text-red-700"
                            : "bg-gray-50 text-gray-700"
                      }`}
                    >
                      {factor}
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendations */}
              <div className="bg-yellow-50 rounded-2xl border border-yellow-200 p-6">
                <h3 className="font-semibold text-yellow-800 mb-4">التوصيات</h3>
                <ul className="space-y-2">
                  {prediction.recommendations.map((rec, idx) => (
                    <li
                      key={idx}
                      className="flex items-start gap-2 text-yellow-700"
                    >
                      <span className="text-yellow-500">💡</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200 p-12 text-center">
              <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-500 mb-2">
                أدخل بيانات الحقل
              </h3>
              <p className="text-gray-400">
                ستظهر نتائج التنبؤ هنا بعد إدخال البيانات
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
