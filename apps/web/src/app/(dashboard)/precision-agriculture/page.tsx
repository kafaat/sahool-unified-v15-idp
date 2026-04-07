import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'الزراعة الدقيقة | SAHOOL',
  description: 'Precision agriculture tools — VRA, GDD, spray timing, and fertilizer planning',
};

const features = [
  {
    href: '/precision-agriculture/vra',
    icon: '🗺️',
    titleAr: 'خرائط التطبيق المتغير',
    titleEn: 'Variable Rate Application',
    descAr: 'خرائط VRA لتوزيع المدخلات بدقة',
  },
  {
    href: '/precision-agriculture/gdd',
    icon: '🌡️',
    titleAr: 'وحدات النمو الحرارية',
    titleEn: 'Growing Degree Days',
    descAr: 'تتبع تراكم الحرارة ومراحل النمو',
  },
  {
    href: '/precision-agriculture/spray',
    icon: '💧',
    titleAr: 'توقيت الرش الذكي',
    titleEn: 'Spray Timing',
    descAr: 'تحديد أفضل أوقات الرش بناءً على الطقس',
  },
  {
    href: '/precision-agriculture/fertilizer',
    icon: '🌿',
    titleAr: 'تخطيط التسميد',
    titleEn: 'Fertilizer Planning',
    descAr: 'توصيات التسميد المبنية على تحليل التربة',
  },
];

export default function PrecisionAgriculturePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">الزراعة الدقيقة</h1>
        <p className="text-muted-foreground mt-1">
          أدوات متقدمة لإدارة المزرعة بدقة عالية
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {features.map((f) => (
          <Link
            key={f.href}
            href={f.href}
            className="block p-6 rounded-lg border bg-card hover:bg-accent transition-colors"
          >
            <div className="flex items-start gap-4">
              <span className="text-3xl" role="img" aria-hidden="true">
                {f.icon}
              </span>
              <div>
                <h2 className="font-semibold text-lg">{f.titleAr}</h2>
                <p className="text-sm text-muted-foreground">{f.titleEn}</p>
                <p className="text-sm text-muted-foreground mt-1">{f.descAr}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
