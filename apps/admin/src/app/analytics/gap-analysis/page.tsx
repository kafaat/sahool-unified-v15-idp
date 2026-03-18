"use client";

// Gap Analysis - Competitive Feature Assessment
// تحليل الفجوات - تقييم الميزات التنافسية

import React, { useState } from "react";
import Header from "@/components/layout/Header";
import StatCard from "@/components/ui/StatCard";
import { cn } from "@/lib/utils";
import {
  CheckCircle2,
  Zap,
  XCircle,
  Trophy,
  ChevronDown,
  ChevronUp,
  Clock,
  Cpu,
  Map,
  Satellite,
  Brain,
  Droplets,
  Tractor,
  Target,
  Cloud,
  ClipboardList,
  MessageCircle,
  Star,
  Server,
  Info,
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════

type FeatureStatus = "full" | "partial" | "gap" | "advantage";
type EffortLevel = "weeks" | "months" | "quarters";

interface InfraItem {
  id: string;
  icon: typeof Cpu;
  label: string;
  desc: string;
}

interface FeatureItem {
  id: string;
  name: string;
  from: string;
  status: FeatureStatus;
  effort: EffortLevel | null;
  infra: string[];
  sahool: string;
  missing: string;
  dev: string;
}

interface FeatureCategory {
  cat: string;
  icon: typeof Map;
  items: FeatureItem[];
}

// ═══════════════════════════════════════════════════════════════════
// SAHOOL INFRASTRUCTURE
// ═══════════════════════════════════════════════════════════════════

const INFRA: InfraItem[] = [
  { id: "flutter", icon: Cpu, label: "Flutter (Offline-First)", desc: "Drift + SQLCipher, RTL, iOS/Android" },
  { id: "fastapi", icon: Zap, label: "FastAPI Microservices", desc: "73+ Python, NestJS" },
  { id: "nextjs", icon: Server, label: "Next.js Web + Admin", desc: "SSR/SSG, Tailwind" },
  { id: "postgis", icon: Map, label: "PostGIS + PostgreSQL", desc: "Geospatial, RLS" },
  { id: "nats", icon: Satellite, label: "NATS JetStream", desc: "Event-driven, Pub/Sub" },
  { id: "ai", icon: Brain, label: "13 AI Agent", desc: "RAG, ML, CrewAI" },
  { id: "iot", icon: Cpu, label: "IoT Sensors", desc: "MQTT, Soil, Weather" },
  { id: "k8s", icon: Server, label: "Kubernetes + Argo CD", desc: "GitOps, HA" },
  { id: "kong", icon: Server, label: "Kong API Gateway", desc: "Auth, Rate Limiting" },
  { id: "ndvi", icon: Satellite, label: "NDVI Pipeline (Prototype)", desc: "Sentinel Hub - mock data" },
];

// ═══════════════════════════════════════════════════════════════════
// FEATURES — CORRECTED based on actual codebase validation
// ═══════════════════════════════════════════════════════════════════

const FEATURES: FeatureCategory[] = [
  {
    cat: "الخريطة والبيانات المكانية",
    icon: Map,
    items: [
      {
        id: "map-layers",
        name: "خرائط NDVI / SAVI / NDWI متعددة الطبقات",
        from: "Farmonaut + FieldView + CropX",
        status: "partial",
        effort: "months",
        infra: ["postgis", "ndvi", "flutter", "nextjs"],
        sahool: "PostGIS جاهز. NDVI Pipeline موجود لكن يعيد بيانات وهمية (sentinelhub غير مثبّت). يحتاج تفعيل Sentinel Hub الحقيقي ثم بناء UI طبقات تفاعلية.",
        missing: "تفعيل Sentinel Hub API (المكتبة غير مثبتة حالياً) + واجهة Side-by-Side comparison وTimeline موسمي.",
        dev: "1-2 شهر لتفعيل Pipeline الحقيقي + 3-4 أسابيع لبناء Map Layer UI.",
      },
      {
        id: "field-boundaries",
        name: "رسم وإدارة حدود الحقول بدقة",
        from: "John Deere + FieldView",
        status: "full",
        effort: null,
        infra: ["postgis", "flutter", "nextjs"],
        sahool: "PostGIS يدعم كل عمليات رسم وتخزين حدود الحقول. Flutter مع Mapbox/Google Maps يدعم الرسم التفاعلي.",
        missing: "لا شيء مفقود تقنياً — يحتاج تلميعاً في UX فقط.",
        dev: "جاهز للإنتاج بتلميع UX بسيط.",
      },
      {
        id: "productivity-map",
        name: "خريطة الإنتاجية التاريخية متعددة السنوات",
        from: "FieldView + CropX",
        status: "partial",
        effort: "months",
        infra: ["postgis", "ndvi", "ai"],
        sahool: "PostGIS يمكنه تراكم بيانات مكانية تاريخية. يحتاج Pipeline لتجميع صور NDVI التاريخية ودمجها في خريطة إنتاجية.",
        missing: "خوارزمية Stacking للصور القمرية التاريخية + UI عرض الأنماط متعددة السنوات.",
        dev: "2-3 أشهر لبناء Historical Stacking Pipeline والعرض البصري.",
      },
      {
        id: "soil-type-map",
        name: "خريطة أنواع التربة الجغرافية",
        from: "CropX + FieldView",
        status: "gap",
        effort: "quarters",
        infra: ["postgis"],
        sahool: "PostGIS جاهز لاستيعاب بيانات التربة. لكن لا تتوفر قاعدة بيانات تربة يمنية مرقمة ومهيكلة حالياً.",
        missing: "قاعدة بيانات التربة اليمنية (شراكة مع الجهات الحكومية) + خوارزمية Interpolation للمناطق غير المُحللة.",
        dev: "3-6 أشهر بما يشمل جمع البيانات الميدانية والشراكات الحكومية.",
      },
    ],
  },
  {
    cat: "الري وإدارة المياه",
    icon: Droplets,
    items: [
      {
        id: "irrigation-recommend",
        name: "توصيات ري ذكية (توقيت + كميات)",
        from: "CropX",
        status: "partial",
        effort: "months",
        infra: ["ai", "iot", "fastapi", "nats"],
        sahool: "13 وكيل AI + IoT sensors + FastAPI = البنية متوفرة. نماذج FAO-56 وAquaCrop-OSPy مدروسة للتكامل.",
        missing: "نموذج Soil Water Balance مُعاير لأنواع التربة اليمنية + تكامل AquaCrop أو pyfao56 مع بيانات المستشعرات.",
        dev: "2-3 أشهر لبناء Irrigation Recommendation Engine مُعاير محلياً.",
      },
      {
        id: "et-monitoring",
        name: "مراقبة التبخر النتحي الفعلي (ETa)",
        from: "CropX Evato",
        status: "gap",
        effort: "quarters",
        infra: ["iot", "fastapi"],
        sahool: "لا يوجد مستشعر ET في البنية الحالية. يمكن حساب ET بالمعادلات (Penman-Monteith) من بيانات محطات الطقس كبديل.",
        missing: "إما مستشعر Evato أو بناء ET Calculator يستخدم بيانات الطقس + FAO equations.",
        dev: "1-2 شهر لـ ET Calculation Module من البيانات الموجودة.",
      },
      {
        id: "vri-irrigation",
        name: "ري بمعدل متغير (VRI) للري المركزي",
        from: "CropX + FieldView",
        status: "gap",
        effort: "quarters",
        infra: ["iot", "fastapi", "nats"],
        sahool: "لا يوجد تكامل مع أنظمة الري المركزي. السوق اليمني يعتمد على ري بالتنقيط والغمر.",
        missing: "بروتوكول تحكم بأنظمة ري محلية (مضخات، صمامات) عبر IoT + واجهة أتمتة.",
        dev: "ليست أولوية للسوق اليمني. 4-6 أشهر إذا طُلبت.",
      },
      {
        id: "water-stress",
        name: "كشف الإجهاد المائي الاستباقي",
        from: "CropX + Farmonaut",
        status: "partial",
        effort: "weeks",
        infra: ["ai", "iot", "ndvi"],
        sahool: "NDVI + مستشعرات رطوبة التربة + AI = كل المكونات موجودة. يحتاج تدريب نموذج على عتبات الإجهاد للمحاصيل اليمنية.",
        missing: "Dataset محلي لعتبات الإجهاد المائي لمحاصيل يمنية + نموذج Early Warning.",
        dev: "6-8 أسابيع بمجرد توفر بيانات تدريب.",
      },
      {
        id: "salinity-mgmt",
        name: "إدارة ملوحة التربة والمياه",
        from: "CropX",
        status: "partial",
        effort: "weeks",
        infra: ["iot", "fastapi", "ai"],
        sahool: "shared/salinity/ مُطبّق بالكامل — مراقبة EC، تصنيف الملوحة، حسابات غسيل التربة، توصيات ثنائية اللغة.",
        missing: "ربط بمستشعرات EC حقلية + واجهة مستخدم لعرض بيانات الملوحة.",
        dev: "3-4 أسابيع لبناء UI والربط بالمستشعرات.",
      },
    ],
  },
  {
    cat: "الذكاء الاصطناعي والتوصيات الزراعية",
    icon: Brain,
    items: [
      {
        id: "ai-advisory",
        name: "مستشار زراعي AI مخصص",
        from: "Farmonaut JEEVN",
        status: "advantage",
        effort: null,
        infra: ["ai", "fastapi", "nats"],
        sahool: "SAHOOL يتفوق: 13 وكيل AI متخصص + RAG على قاعدة معرفة زراعية عربية (91 ملف، 50,000+ سطر). NLP يعمل بنظام keyword-based (لا AraBERT فعلي حالياً).",
        missing: "توسيع قاعدة RAG بأبحاث المحاصيل اليمنية + تفعيل AraBERT (المكتبة غير مثبّتة) + ربط الوكلاء بـ IoT.",
        dev: "جاهز جوهرياً — يحتاج توسيع Dataset وتكامل IoT.",
      },
      {
        id: "disease-detection",
        name: "كشف أمراض المحاصيل من الصور + AI",
        from: "غائب في كل المنافسين",
        status: "advantage",
        effort: "months",
        infra: ["ai", "flutter", "fastapi"],
        sahool: "YOLO26 Vision Service مُطبّق بالكامل: 7 مهام كشف، 22 آفة، 34 مرض، GPU support، 26 كود خطأ ثنائي اللغة. Port 8150.",
        missing: "Dataset صور أمراض محاصيل يمنية مُعلّمة + Fine-tuning على أصناف محلية + واجهة Scouting في التطبيق.",
        dev: "الـ backend جاهز. 2-3 أشهر لجمع Dataset يمني وبناء واجهة.",
      },
      {
        id: "yield-forecast",
        name: "توقع الغلة (Yield Forecasting)",
        from: "Farmonaut + FieldView",
        status: "partial",
        effort: "months",
        infra: ["ai", "ndvi", "fastapi"],
        sahool: "NDVI Pipeline + AI agents = قدرة تقنية موجودة. yield-prediction-service موجود (NestJS port 8152).",
        missing: "بيانات غلة تاريخية لمحاصيل يمنية + نموذج ML موسمي مُعاير + ربط بالـ NDVI والطقس.",
        dev: "3-5 أشهر بما يشمل جمع البيانات التاريخية.",
      },
      {
        id: "pest-risk",
        name: "نموذج مخاطر الآفات والأمراض الفطرية",
        from: "CropX",
        status: "partial",
        effort: "months",
        infra: ["ai", "iot", "fastapi"],
        sahool: "shared/pest_scouting/ مُطبّق: 40+ آفة مع وصف مورفولوجي ثنائي اللغة، عتبات اقتصادية، IPM strategies.",
        missing: "Disease Risk Model مُعاير على مناخ اليمن + تكامل بيانات الطقس الفعلية.",
        dev: "2-3 أشهر لبناء نموذج مخاطر مُعاير.",
      },
      {
        id: "nitrogen-leaching",
        name: "كشف تسرب النيتروجين (Leaching Detection)",
        from: "CropX",
        status: "gap",
        effort: "quarters",
        infra: ["iot"],
        sahool: "يحتاج مستشعرات EC متعددة الأعماق. SAHOOL لا تمتلك حالياً مستشعرات EC بعمق متعدد.",
        missing: "مستشعرات EC متعددة الأعماق + نموذج Leaching Detection مُعاير.",
        dev: "4-6 أشهر شاملة تطوير أو استيراد مستشعرات EC مناسبة.",
      },
      {
        id: "fertilizer-calc",
        name: "حاسبة NPK وتوصيات التسميد",
        from: "CropX + FieldView",
        status: "full",
        effort: null,
        infra: ["ai", "fastapi"],
        sahool: "shared/fertilizer_management/ مُطبّق بالكامل: نماذج NPK لـ 8+ محاصيل مع مراحل نمو، حساب الجرعات، تتبع المخزون.",
        missing: "لا شيء مفقود في الـ backend — يحتاج واجهة في التطبيق.",
        dev: "جاهز للإنتاج — يحتاج UI فقط.",
      },
      {
        id: "pest-scouting",
        name: "نظام استكشاف الآفات (40+ آفة)",
        from: "CropX + Farmonaut",
        status: "full",
        effort: null,
        infra: ["ai", "fastapi", "flutter"],
        sahool: "shared/pest_scouting/ يحتوي 40+ آفة مع وصف مورفولوجي مفصّل (عربي/إنجليزي)، دورة حياة، أعراض، عتبات اقتصادية.",
        missing: "لا شيء مفقود في الـ backend — يحتاج واجهة Scouting في التطبيق.",
        dev: "جاهز للإنتاج — يحتاج UI فقط.",
      },
    ],
  },
  {
    cat: "الأسطول والآلات الزراعية",
    icon: Tractor,
    items: [
      {
        id: "fleet-tracking",
        name: "تتبع الأسطول والآلات GPS",
        from: "John Deere + Farmonaut",
        status: "gap",
        effort: "months",
        infra: ["iot", "postgis", "nats", "fastapi"],
        sahool: "Equipment Service موجود لكن يخزّن الموقع كنص عادي (location_name). لا يوجد GPS tracking حقيقي.",
        missing: "GPS Tracker IoT devices + تحويل حقل الموقع لإحداثيات جغرافية + Fleet Dashboard مباشر.",
        dev: "3-4 أشهر لبناء Fleet Module حقيقي مع GPS hardware.",
      },
      {
        id: "machine-data",
        name: "استيراد بيانات الآلات (CLAAS، CNH، Deere)",
        from: "FieldView + CropX + John Deere",
        status: "gap",
        effort: "quarters",
        infra: ["kong", "fastapi"],
        sahool: "Kong API Gateway جاهز لاستقبال بيانات خارجية. لكن لا يوجد تكامل مع بروتوكولات ISOBUS.",
        missing: "ISOBUS/ISOXML Parser + APIs للشركات الكبرى + Machine Data Connector.",
        dev: "ليست أولوية للسوق اليمني. 4-6 أشهر.",
      },
      {
        id: "maintenance",
        name: "إدارة الصيانة الوقائية للآلات",
        from: "John Deere",
        status: "gap",
        effort: "months",
        infra: ["fastapi", "nats", "flutter"],
        sahool: "shared/equipment_maintenance/ يحتوي نماذج بيانات أساسية. لا يوجد Maintenance scheduling module مكتمل.",
        missing: "Maintenance Module: خطط صيانة، تنبيهات، سجل، تكامل مع موردي قطع الغيار.",
        dev: "2-3 أشهر لبناء وحدة صيانة — ميزة تمييزية في السوق اليمني.",
      },
      {
        id: "remote-display",
        name: "التحكم عن بُعد في شاشة الكابينة (Remote View)",
        from: "John Deere + FieldView",
        status: "gap",
        effort: "quarters",
        infra: ["nats", "fastapi"],
        sahool: "NATS JetStream يدعم نقل البيانات اللحظية. لكن Remote Display يحتاج WebRTC.",
        missing: "WebRTC integration + In-Cab Device SDK. غير ضرورية للسوق اليمني.",
        dev: "غير مُوصى بها كأولوية. 6+ أشهر.",
      },
    ],
  },
  {
    cat: "الوصفات والزراعة الدقيقة (Precision Ag)",
    icon: Target,
    items: [
      {
        id: "vra-seeds",
        name: "وصفات البذور بمعدل متغير (VRS/VRA)",
        from: "FieldView",
        status: "partial",
        effort: "quarters",
        infra: ["ai", "postgis", "fastapi"],
        sahool: "AI Agents + PostGIS Zones + بيانات تاريخية = بنية قادرة. يحتاج Dataset محلي كافٍ.",
        missing: "Dataset بيانات غلة تاريخية لعدة مواسم + Prescription Engine مُعاير + تصدير للآلات.",
        dev: "6-9 أشهر — يعتمد على توفر بيانات تاريخية.",
      },
      {
        id: "vra-fertilizer",
        name: "وصفات الأسمدة بمعدل متغير (Fertility Scripts)",
        from: "FieldView + CropX",
        status: "partial",
        effort: "months",
        infra: ["ai", "postgis", "iot"],
        sahool: "shared/vra_maps/vra_generator.py مُطبّق + fertilizer_management + AI = أساس قوي.",
        missing: "معايرة نموذج Nutrient Balance لأنواع التربة اليمنية + تكامل مع موردي الأسمدة المحليين.",
        dev: "3-5 أشهر بمجرد توفر بيانات التربة الأساسية.",
      },
      {
        id: "crop-protection-vra",
        name: "وصفات حماية المحاصيل بمعدل متغير",
        from: "FieldView + CropX",
        status: "partial",
        effort: "months",
        infra: ["ai", "ndvi", "fastapi"],
        sahool: "NDVI يحدد مناطق الإجهاد + AI يمكنه اقتراح التطبيق المناسب.",
        missing: "نموذج Spray Zone Recommendation + خريطة مناطق الإصابة من صور الأقمار + تصدير للمعدات.",
        dev: "3-4 أشهر لبناء أولي مناسب.",
      },
      {
        id: "drone-vra",
        name: "خرائط VRA للطائرات المسيّرة",
        from: "Farmonaut",
        status: "partial",
        effort: "months",
        infra: ["ai", "postgis", "fastapi"],
        sahool: "shared/drone_integration/vra.py مُطبّق بالكامل + flight_planner.py لتخطيط الرحلات + drone-service (port 8126).",
        missing: "تكامل مع أجهزة drone فعلية + اختبار ميداني.",
        dev: "2-3 أشهر للتكامل الميداني.",
      },
    ],
  },
  {
    cat: "الطقس والمناخ",
    icon: Cloud,
    items: [
      {
        id: "field-weather",
        name: "توقعات طقس على مستوى الحقل",
        from: "FieldView + CropX + John Deere",
        status: "partial",
        effort: "weeks",
        infra: ["fastapi", "nats", "flutter"],
        sahool: "يمكن دمج Open-Meteo أو ERA5 API مباشرة. NATS يُوصل البيانات للـ Flutter.",
        missing: "ربط إحداثيات الحقل بـ Weather API + عرض توقعات مخصصة لكل حقل.",
        dev: "2-3 أسابيع للتكامل والعرض.",
      },
      {
        id: "spray-insights",
        name: "توصيات توقيت الرش (Spray Insights)",
        from: "FieldView",
        status: "full",
        effort: null,
        infra: ["ai", "fastapi", "nats"],
        sahool: "spray_window_endpoints.py مُطبّق بالكامل في vegetation-analysis-service: حساب نوافذ الرش المثالية بناءً على الرياح والرطوبة والحرارة.",
        missing: "لا شيء مفقود في الـ backend — يحتاج واجهة في التطبيق.",
        dev: "جاهز — يحتاج UI فقط.",
      },
      {
        id: "gdd",
        name: "Growing Degree Days (GDD) — تراكم الحرارة",
        from: "CropX + FieldView",
        status: "full",
        effort: null,
        infra: ["fastapi", "ai"],
        sahool: "gdd_tracker.py + gdd_endpoints.py مُطبّقان بالكامل: 3 طرق حساب (standard, modified, sine)، 22 محصول مع عتبات حرارية، تتبع مراحل النمو.",
        missing: "لا شيء مفقود في الـ backend — يحتاج فقط ربط UI.",
        dev: "جاهز للإنتاج — UI موجود في /precision-agriculture/gdd.",
      },
      {
        id: "local-weather-stations",
        name: "محطات أرصاد يمنية محلية",
        from: "SAHOOL فقط",
        status: "advantage",
        effort: "months",
        infra: ["iot", "fastapi", "postgis"],
        sahool: "IoT Integration يدعم أجهزة Arduino وRaspberry Pi. يمكن بناء شبكة محطات طقس منخفضة التكلفة.",
        missing: "تصميم نموذج محطة طقس رخيص (< $50) مناسب للبيئة اليمنية + بروتوكول LoRa/NB-IoT.",
        dev: "3-4 أشهر لبناء أول شبكة تجريبية.",
      },
    ],
  },
  {
    cat: "التتبع والتقارير والامتثال",
    icon: ClipboardList,
    items: [
      {
        id: "seasonal-reports",
        name: "تقارير موسمية شاملة",
        from: "FieldView + CropX + John Deere",
        status: "partial",
        effort: "weeks",
        infra: ["fastapi", "nextjs", "flutter"],
        sahool: "FastAPI + Next.js = قدرة تقارير ممتازة.",
        missing: "Report Templates بالعربية + تصدير PDF + قوالب مخصصة للجهات الحكومية والبنوك.",
        dev: "3-5 أسابيع.",
      },
      {
        id: "finance-tracking",
        name: "تتبع مالي وتكاليف الموسم",
        from: "FieldView EU + Combyne",
        status: "partial",
        effort: "weeks",
        infra: ["fastapi", "nextjs", "flutter"],
        sahool: "shared/financial_reports/ مُطبّق: تتبع تكاليف 12 فئة، حساب ROI، نقطة التعادل، تحليل تكلفة/هكتار.",
        missing: "واجهة مستخدم (Dashboard) لعرض البيانات المالية + تكامل مع العملة اليمنية.",
        dev: "3-4 أسابيع لبناء UI فوق الـ backend الموجود.",
      },
      {
        id: "crop-marketing",
        name: "تسويق المحاصيل وأسعار السوق",
        from: "FieldView Combyne",
        status: "partial",
        effort: "months",
        infra: ["fastapi", "nextjs"],
        sahool: "shared/market_prices/ مُطبّق: تتبع أسعار 5 دول + تحليل اتجاهات. لكن بيانات الأسعار ثابتة (لا تغذية حية).",
        missing: "تغذية أسعار حية من أسواق الجملة + ربط بالمشترين + تتبع العقود.",
        dev: "3-4 أشهر لبناء منصة تسويق متكاملة مع بيانات حية.",
      },
      {
        id: "globalgap",
        name: "امتثال GlobalGAP (IFA v6)",
        from: "متطلب تصدير",
        status: "partial",
        effort: "months",
        infra: ["fastapi", "nextjs"],
        sahool: "shared/globalgap/ مُطبّق: قوائم فحص IFA v6، API endpoints، تقييم الامتثال.",
        missing: "واجهة إدارة الامتثال + تصدير تقارير للمُدقّقين.",
        dev: "2-3 أشهر لبناء واجهة كاملة.",
      },
    ],
  },
  {
    cat: "الاتصال والمجتمع الزراعي",
    icon: MessageCircle,
    items: [
      {
        id: "whatsapp-telegram",
        name: "تكامل WhatsApp / Telegram للمزارعين",
        from: "SAHOOL فقط",
        status: "advantage",
        effort: "months",
        infra: ["fastapi", "nats", "ai"],
        sahool: "whatsapp-bot-service (port 8240) مُطبّق مع intent detection + AI Agent يرد بالعربية.",
        missing: "تحسين المحادثات المعقدة + Offline messaging queue.",
        dev: "2-3 أشهر لتحسين التجربة.",
      },
      {
        id: "field-chat",
        name: "دردشة الحقل ومجتمع المزارعين",
        from: "Farmonaut Field Chat",
        status: "partial",
        effort: "weeks",
        infra: ["nats", "flutter", "fastapi"],
        sahool: "chat-service (NestJS port 8115) موجود + NATS JetStream يدعم Real-time Messaging.",
        missing: "Chat Module مرتبط بالحقل + مشاركة الصور والخرائط.",
        dev: "3-4 أسابيع.",
      },
      {
        id: "advisor-sharing",
        name: "مشاركة البيانات مع المستشارين والجهات",
        from: "FieldView + CropX",
        status: "partial",
        effort: "weeks",
        infra: ["kong", "fastapi", "postgis"],
        sahool: "Kong API Gateway + PostgreSQL RLS = صلاحيات مضبوطة.",
        missing: "Sharing Dashboard: تحكم في الصلاحيات لكل طرف + تقارير مشتركة.",
        dev: "2-3 أسابيع.",
      },
    ],
  },
  {
    cat: "ميزات SAHOOL الفريدة",
    icon: Star,
    items: [
      {
        id: "arabic-rtl",
        name: "عربية أصلية + RTL كامل + لهجة يمنية",
        from: "SAHOOL فقط",
        status: "advantage",
        effort: null,
        infra: ["flutter", "nextjs", "ai"],
        sahool: "كل المنافسين يدعمون الإنجليزية فقط. SAHOOL هو المنصة الزراعية العربية الوحيدة بمستوى enterprise.",
        missing: "توسيع قاموس المصطلحات الزراعية اليمنية في نماذج AI + دعم اللهجة في الصوت.",
        dev: "جاهز — يحتاج توسيع مستمر.",
      },
      {
        id: "local-calendar",
        name: "التقويم الزراعي اليمني + المنازل القمرية",
        from: "SAHOOL فقط",
        status: "advantage",
        effort: null,
        infra: ["ai", "fastapi", "flutter"],
        sahool: "astronomical-calendar service (port 8111) مُطبّق بالكامل: التقويم الهجري + المنازل القمرية الـ 28 + توقيتات الزراعة التقليدية اليمنية.",
        missing: "لا شيء مفقود — يحتاج توسيع مستمر لقاعدة المعرفة التقليدية.",
        dev: "جاهز للإنتاج.",
      },
      {
        id: "offline-first",
        name: "Offline-First في مناطق انعدام الاتصال",
        from: "SAHOOL فقط",
        status: "advantage",
        effort: null,
        infra: ["flutter", "nats"],
        sahool: "Flutter مع Drift + SQLCipher (256-bit AES) + outbox pattern + ETag conflict resolution = أقوى حل Offline-First.",
        missing: "تحسين مستمر لـ Sync Logic + تقليل حجم البيانات المُخزّنة.",
        dev: "جاهز للإنتاج.",
      },
      {
        id: "loan-insurance",
        name: "تمويل وتأمين زراعي مدعوم بالأقمار",
        from: "Farmonaut API",
        status: "gap",
        effort: "quarters",
        infra: ["ndvi", "postgis", "fastapi"],
        sahool: "shared/crop_insurance/ يحتوي مخططات بيانات أساسية (enums, data classes) بدون business logic فعلي.",
        missing: "شراكة مع بنوك وشركات تأمين + بناء API تحقق + business logic للتقييم.",
        dev: "6-12 شهر شاملة الجانب القانوني والشراكات.",
      },
      {
        id: "blockchain-trace",
        name: "تتبع المنتج (بن، عسل، تمر يمني)",
        from: "Farmonaut",
        status: "partial",
        effort: "months",
        infra: ["fastapi", "kong"],
        sahool: "shared/traceability/ مُطبّق: QR codes + event logging + سلسلة توريد. لا يوجد blockchain حقيقي — يستخدم قاعدة بيانات تقليدية.",
        missing: "Distributed Ledger إن لزم + واجهة QR للمستهلك + API للمستوردين.",
        dev: "2-3 أشهر لتحسين التجربة وإضافة واجهة المستهلك.",
      },
      {
        id: "cooperative-mgmt",
        name: "إدارة التعاونيات الزراعية",
        from: "SAHOOL فقط",
        status: "advantage",
        effort: "months",
        infra: ["fastapi", "nextjs", "flutter"],
        sahool: "shared/cooperatives/ مُطبّق: تجميع موارد (معدات/عمالة/أراضي)، توزيع إيرادات، حسابات تكلفة مشتركة.",
        missing: "واجهة مستخدم لإدارة التعاونيات + تطبيق خاص لمدير التعاونية.",
        dev: "2-3 أشهر لبناء واجهة كاملة.",
      },
    ],
  },
];

// ═══════════════════════════════════════════════════════════════════
// STATUS & EFFORT CONFIG
// ═══════════════════════════════════════════════════════════════════

const STATUS_CONFIG: Record<
  FeatureStatus,
  { label: string; icon: typeof CheckCircle2; textClass: string; bgClass: string; borderClass: string }
> = {
  full: {
    label: "جاهز للإنتاج",
    icon: CheckCircle2,
    textClass: "text-emerald-600 dark:text-emerald-400",
    bgClass: "bg-emerald-50 dark:bg-emerald-900/20",
    borderClass: "border-emerald-500",
  },
  partial: {
    label: "جزئي - يحتاج تطوير",
    icon: Zap,
    textClass: "text-amber-600 dark:text-amber-400",
    bgClass: "bg-amber-50 dark:bg-amber-900/20",
    borderClass: "border-amber-500",
  },
  gap: {
    label: "فجوة - يحتاج بناء",
    icon: XCircle,
    textClass: "text-red-600 dark:text-red-400",
    bgClass: "bg-red-50 dark:bg-red-900/20",
    borderClass: "border-red-500",
  },
  advantage: {
    label: "ميزة تفوق حصرية",
    icon: Trophy,
    textClass: "text-violet-600 dark:text-violet-400",
    bgClass: "bg-violet-50 dark:bg-violet-900/20",
    borderClass: "border-violet-500",
  },
};

const EFFORT_CONFIG: Record<EffortLevel, { label: string; textClass: string }> = {
  weeks: { label: "أسابيع", textClass: "text-emerald-600 dark:text-emerald-400" },
  months: { label: "أشهر", textClass: "text-amber-600 dark:text-amber-400" },
  quarters: { label: "6+ أشهر", textClass: "text-red-600 dark:text-red-400" },
};

// ═══════════════════════════════════════════════════════════════════
// PRIORITIES
// ═══════════════════════════════════════════════════════════════════

const PRIORITIES = [
  {
    p: "P0",
    label: "فوري",
    items: ["تفعيل Sentinel Hub الحقيقي", "تقارير موسمية PDF بالعربية", "واجهة QR للتتبع", "Financial Dashboard UI"],
    colorClass: "text-red-600 dark:text-red-400",
    bgClass: "bg-red-600",
  },
  {
    p: "P1",
    label: "1-3 أشهر",
    items: ["توصيات الري الذكي (FAO-56)", "واجهة Scouting للأمراض", "خرائط NDVI متعددة الطبقات", "Field Chat بالعربية"],
    colorClass: "text-amber-600 dark:text-amber-400",
    bgClass: "bg-amber-600",
  },
  {
    p: "P2",
    label: "3-6 أشهر",
    items: ["Yield Forecasting", "WhatsApp تحسين", "Fleet GPS Tracking", "واجهة التعاونيات"],
    colorClass: "text-blue-600 dark:text-blue-400",
    bgClass: "bg-blue-600",
  },
  {
    p: "P3",
    label: "6+ أشهر",
    items: ["Crop Marketing Module", "تأمين زراعي (API + شراكات)", "خريطة التربة اليمنية", "VRS البذور"],
    colorClass: "text-violet-600 dark:text-violet-400",
    bgClass: "bg-violet-600",
  },
];

// ═══════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════

export default function GapAnalysisPage() {
  const [filter, setFilter] = useState<"all" | FeatureStatus>("all");
  const [selected, setSelected] = useState<string | null>(null);
  const [expandedCat, setExpandedCat] = useState<string | null>(null);

  const allItems = FEATURES.flatMap((c) => c.items);
  const counts: Record<FeatureStatus, number> = {
    full: allItems.filter((i) => i.status === "full").length,
    partial: allItems.filter((i) => i.status === "partial").length,
    gap: allItems.filter((i) => i.status === "gap").length,
    advantage: allItems.filter((i) => i.status === "advantage").length,
  };

  const filteredFeatures = FEATURES.map((cat) => ({
    ...cat,
    items: filter === "all" ? cat.items : cat.items.filter((i) => i.status === filter),
  })).filter((cat) => cat.items.length > 0);

  const sel = selected ? allItems.find((i) => i.id === selected) ?? null : null;

  const filterTabs: { id: "all" | FeatureStatus; label: string; icon: typeof CheckCircle2 }[] = [
    { id: "all", label: "الكل", icon: Info },
    { id: "full", label: "جاهز", icon: CheckCircle2 },
    { id: "partial", label: "جزئي", icon: Zap },
    { id: "gap", label: "فجوة", icon: XCircle },
    { id: "advantage", label: "تفوق", icon: Trophy },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Header
        title="تحليل الفجوات التنافسية"
        subtitle="ما تدعمه بنيتك الحالية وما تحتاج تطويره وأين تتفوق على الجميع"
      />

      <div className="p-6">
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard
            title="جاهز للإنتاج"
            value={counts.full}
            icon={CheckCircle2}
            iconColor="text-emerald-600"
            className="dark:bg-gray-900 dark:border-gray-800"
          />
          <StatCard
            title="جزئي - يحتاج تطوير"
            value={counts.partial}
            icon={Zap}
            iconColor="text-amber-600"
            className="dark:bg-gray-900 dark:border-gray-800"
          />
          <StatCard
            title="فجوة - يحتاج بناء"
            value={counts.gap}
            icon={XCircle}
            iconColor="text-red-600"
            className="dark:bg-gray-900 dark:border-gray-800"
          />
          <StatCard
            title="ميزة تفوق حصرية"
            value={counts.advantage}
            icon={Trophy}
            iconColor="text-violet-600"
            className="dark:bg-gray-900 dark:border-gray-800"
          />
        </div>

        {/* Filter tabs */}
        <div className="flex gap-1 mb-6 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-1">
          {filterTabs.map((tab) => {
            const isActive = filter === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setFilter(tab.id)}
                className={cn(
                  "flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all",
                  isActive
                    ? "bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300 shadow-sm"
                    : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300",
                )}
              >
                <tab.icon className="w-4 h-4" />
                <span className="hidden sm:inline">{tab.label}</span>
                {tab.id !== "all" && (
                  <span className={cn(
                    "text-xs px-1.5 py-0.5 rounded-full",
                    isActive ? "bg-sahool-100 dark:bg-sahool-800" : "bg-gray-100 dark:bg-gray-800",
                  )}>
                    {counts[tab.id as FeatureStatus]}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Infrastructure strip */}
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-4 mb-6 border-r-4 border-r-emerald-500">
          <h3 className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 tracking-wider mb-3">
            البنية التحتية الحالية لـ SAHOOL
          </h3>
          <div className="flex flex-wrap gap-2">
            {INFRA.map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-2 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-md px-3 py-1.5"
              >
                <item.icon className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                <div>
                  <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-300">{item.label}</span>
                  <span className="text-xs text-emerald-600/60 dark:text-emerald-400/60 mr-1.5">{item.desc}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main content: feature list + detail panel */}
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Feature list */}
          <div className="flex-1 space-y-4">
            {filteredFeatures.map((cat) => (
              <div key={cat.cat}>
                <button
                  type="button"
                  onClick={() => setExpandedCat(expandedCat === cat.cat ? null : cat.cat)}
                  className="w-full flex items-center gap-3 px-4 py-3 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <cat.icon className="w-5 h-5 text-sahool-600 dark:text-sahool-400" />
                  <span className="text-sm font-bold text-gray-900 dark:text-gray-100 flex-1 text-right">{cat.cat}</span>
                  <span className="text-xs text-gray-400 dark:text-gray-500">{cat.items.length} ميزة</span>
                  {(expandedCat === cat.cat || filter !== "all") ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  )}
                </button>

                {(expandedCat === cat.cat || filter !== "all") && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3 pr-2">
                    {cat.items.map((item) => {
                      const sc = STATUS_CONFIG[item.status];
                      const ef = item.effort ? EFFORT_CONFIG[item.effort] : null;
                      const isSelected = selected === item.id;
                      const StatusIcon = sc.icon;
                      return (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => setSelected(isSelected ? null : item.id)}
                          className={cn(
                            "text-right bg-white dark:bg-gray-900 border rounded-lg p-4 transition-all hover:shadow-md",
                            isSelected
                              ? `${sc.bgClass} border-2 ${sc.borderClass}`
                              : "border-gray-200 dark:border-gray-800",
                            `border-r-4 ${sc.borderClass}`,
                          )}
                        >
                          <div className="flex items-start justify-between gap-2 mb-2">
                            <h4 className="text-sm font-bold text-gray-900 dark:text-gray-100 leading-relaxed flex-1">
                              {item.name}
                            </h4>
                            {ef && (
                              <span className={cn("text-xs border rounded-full px-2 py-0.5 whitespace-nowrap", ef.textClass, `border-current`)}>
                                <Clock className="w-3 h-3 inline ml-1" />
                                {ef.label}
                              </span>
                            )}
                          </div>
                          <div className="flex items-center justify-between">
                            <span className={cn("text-xs flex items-center gap-1 px-2 py-1 rounded", sc.bgClass, sc.textClass)}>
                              <StatusIcon className="w-3 h-3" />
                              {sc.label}
                            </span>
                            <span className="text-xs text-gray-400 dark:text-gray-500 truncate max-w-[120px]">
                              {item.from}
                            </span>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}

            {filteredFeatures.length === 0 && (
              <div className="text-center py-16 text-gray-400 dark:text-gray-500 text-sm">
                لا توجد ميزات بهذا التصفية
              </div>
            )}
          </div>

          {/* Detail panel */}
          <div className="w-full lg:w-80 lg:min-w-[320px] shrink-0">
            <div className="sticky top-20 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
              {sel ? (
                <div className="p-5">
                  {/* Status badges */}
                  <div className="flex items-center gap-2 mb-4">
                    <span className={cn("text-xs flex items-center gap-1 px-2.5 py-1 rounded-md border", STATUS_CONFIG[sel.status].bgClass, STATUS_CONFIG[sel.status].textClass, `border-current`)}>
                      {React.createElement(STATUS_CONFIG[sel.status].icon, { className: "w-3.5 h-3.5" })}
                      {STATUS_CONFIG[sel.status].label}
                    </span>
                    {sel.effort && (
                      <span className={cn("text-xs flex items-center gap-1 px-2.5 py-1 rounded-md border border-current", EFFORT_CONFIG[sel.effort].textClass)}>
                        <Clock className="w-3.5 h-3.5" />
                        {EFFORT_CONFIG[sel.effort].label}
                      </span>
                    )}
                  </div>

                  <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-1 leading-relaxed">{sel.name}</h3>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mb-5">مصدر الإلهام: {sel.from}</p>

                  {/* Infrastructure */}
                  <div className="mb-4">
                    <h4 className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 tracking-wider mb-2">
                      البنية الحالية الداعمة
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {sel.infra.map((inf) => {
                        const item = INFRA.find((x) => x.id === inf);
                        return item ? (
                          <span
                            key={inf}
                            className="text-xs bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 px-2 py-0.5 rounded flex items-center gap-1"
                          >
                            <item.icon className="w-3 h-3" />
                            {item.label}
                          </span>
                        ) : null;
                      })}
                    </div>
                  </div>

                  {/* What SAHOOL supports */}
                  <div className="bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-200 dark:border-emerald-800 border-r-4 border-r-emerald-500 rounded-md p-3.5 mb-3">
                    <h4 className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 tracking-wider mb-2">
                      ما تدعمه بنيتك الحالية
                    </h4>
                    <p className="text-xs text-emerald-800 dark:text-emerald-200 leading-relaxed">{sel.sahool}</p>
                  </div>

                  {/* What's missing */}
                  <div className="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 border-r-4 border-r-red-500 rounded-md p-3.5 mb-3">
                    <h4 className="text-xs font-semibold text-red-600 dark:text-red-400 tracking-wider mb-2">
                      ما يحتاج بناء أو تطوير
                    </h4>
                    <p className="text-xs text-red-800 dark:text-red-200 leading-relaxed">{sel.missing}</p>
                  </div>

                  {/* Dev estimate */}
                  {sel.effort && (
                    <div className="bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800 border-r-4 border-r-amber-500 rounded-md p-3.5">
                      <h4 className="text-xs font-semibold text-amber-600 dark:text-amber-400 tracking-wider mb-2">
                        تقدير وقت التطوير
                      </h4>
                      <p className="text-xs text-amber-800 dark:text-amber-200 leading-relaxed">{sel.dev}</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="p-5">
                  <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 tracking-wider mb-4">
                    ملخص الفجوات
                  </h3>

                  {/* Progress bars */}
                  {(["full", "partial", "gap", "advantage"] as FeatureStatus[]).map((status) => {
                    const sc = STATUS_CONFIG[status];
                    const pct = (counts[status] / allItems.length) * 100;
                    return (
                      <div key={status} className="mb-3">
                        <div className="flex justify-between text-xs mb-1">
                          <span className={sc.textClass}>{sc.label}</span>
                          <span className={cn(sc.textClass, "font-bold")}>{counts[status]}/{allItems.length}</span>
                        </div>
                        <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full">
                          <div
                            className={cn("h-full rounded-full transition-all duration-500", sc.borderClass.replace("border-", "bg-"))}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}

                  {/* Priorities */}
                  <div className="mt-6 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 border-t-2 border-t-sahool-500 rounded-md p-4">
                    <h4 className="text-xs font-semibold text-sahool-600 dark:text-sahool-400 mb-3">
                      أولويات التطوير المقترحة
                    </h4>
                    {PRIORITIES.map((pri) => (
                      <div key={pri.p} className="mb-3">
                        <div className="flex items-center gap-2 mb-1.5">
                          <span className={cn("text-xs font-bold text-white px-1.5 py-0.5 rounded", pri.bgClass)}>
                            {pri.p}
                          </span>
                          <span className={cn("text-xs font-medium", pri.colorClass)}>{pri.label}</span>
                        </div>
                        {pri.items.map((it) => (
                          <p key={it} className="text-xs text-gray-500 dark:text-gray-400 pr-4 mb-0.5 leading-relaxed">
                            {it}
                          </p>
                        ))}
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-md p-3 text-xs text-blue-700 dark:text-blue-300 leading-relaxed">
                    اضغط على أي ميزة لرؤية تحليل تفصيلي: ما تدعمه بنيتك، وما يحتاج تطويراً، وتقدير وقت البناء.
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
