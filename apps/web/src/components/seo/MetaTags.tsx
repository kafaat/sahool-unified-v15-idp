import type { Metadata } from 'next';

/**
 * Meta tags configuration for pages
 */
export interface MetaTagsProps {
  /** Page title */
  title: string;
  /** Arabic page title */
  titleAr?: string;
  /** Page description */
  description: string;
  /** Arabic description */
  descriptionAr?: string;
  /** Keywords for search engines */
  keywords?: string[];
  /** Canonical URL */
  canonicalUrl?: string;
  /** Open Graph image URL */
  ogImage?: string;
  /** Open Graph type (default: website) */
  ogType?: 'website' | 'article';
  /** Twitter card type */
  twitterCard?: 'summary' | 'summary_large_image';
  /** Robots directive */
  robots?: string;
  /** Alternative language URLs */
  alternates?: {
    ar?: string;
    en?: string;
  };
  /** Published date (for articles) */
  publishedTime?: string;
  /** Modified date (for articles) */
  modifiedTime?: string;
  /** Author name (for articles) */
  author?: string;
}

/**
 * Generate metadata for Next.js pages
 * Uses Next.js 15 Metadata API
 *
 * @example
 * ```tsx
 * // In page.tsx
 * import { generateMetadata } from '@/components/seo/MetaTags';
 *
 * export const metadata = generateMetadata({
 *   title: 'Dashboard',
 *   titleAr: 'لوحة المعلومات',
 *   description: 'View your farm dashboard and analytics',
 *   descriptionAr: 'عرض لوحة معلومات المزرعة والتحليلات',
 * });
 * ```
 */
export function generateMetadata(props: MetaTagsProps): Metadata {
  const {
    title,
    titleAr,
    description,
    descriptionAr,
    keywords,
    canonicalUrl,
    ogImage = '/icon-512.png',
    ogType = 'website',
    twitterCard = 'summary_large_image',
    robots = 'index, follow',
    alternates,
    publishedTime,
    modifiedTime,
    author,
  } = props;

  const fullTitle = titleAr ? `${titleAr} | ${title} - SAHOOL` : `${title} - SAHOOL`;

  const fullDescription = descriptionAr ? `${descriptionAr} - ${description}` : description;

  const metadata: Metadata = {
    title: fullTitle,
    description: fullDescription,
    keywords: keywords?.join(', '),
    robots,
    authors: author ? [{ name: author }] : undefined,
    alternates: {
      canonical: canonicalUrl,
      languages: alternates,
    },
    openGraph: {
      title: fullTitle,
      description: fullDescription,
      type: ogType,
      siteName: 'SAHOOL',
      locale: 'ar_YE',
      alternateLocale: ['en_US'],
      images: ogImage
        ? [
            {
              url: ogImage,
              width: 1200,
              height: 630,
              alt: titleAr || title,
            },
          ]
        : undefined,
      ...(publishedTime && { publishedTime }),
      ...(modifiedTime && { modifiedTime }),
      ...(author && { authors: [author] }),
    },
    twitter: {
      card: twitterCard,
      title: fullTitle,
      description: fullDescription,
      images: ogImage ? [ogImage] : undefined,
      site: '@sahoolplatform',
      creator: author ? `@${author}` : undefined,
    },
  };

  return metadata;
}

/**
 * Client-side meta tags component for dynamic pages
 * Use this when you need to set meta tags from client components
 */
export function MetaTags({
  title,
  titleAr,
  description,
  descriptionAr,
}: Pick<MetaTagsProps, 'title' | 'titleAr' | 'description' | 'descriptionAr'>) {
  const fullTitle = titleAr ? `${titleAr} | ${title} - SAHOOL` : `${title} - SAHOOL`;

  const fullDescription = descriptionAr ? `${descriptionAr} - ${description}` : description;

  // Note: In Next.js 15, prefer using the generateMetadata function in server components
  // This component is for edge cases where dynamic client-side meta is needed
  return (
    <>
      <title>{fullTitle}</title>
      <meta name="description" content={fullDescription} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={fullDescription} />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={fullDescription} />
    </>
  );
}

/**
 * Pre-configured metadata for common SAHOOL pages
 */
export const sahoolPageMetadata = {
  dashboard: generateMetadata({
    title: 'Dashboard',
    titleAr: 'لوحة المعلومات',
    description: 'View your farm dashboard with real-time KPIs, alerts, and field status',
    descriptionAr: 'عرض لوحة معلومات مزرعتك مع مؤشرات الأداء والتنبيهات وحالة الحقول',
    keywords: ['farm dashboard', 'agricultural analytics', 'لوحة معلومات المزرعة'],
  }),

  fields: generateMetadata({
    title: 'Fields',
    titleAr: 'الحقول',
    description: 'Manage and monitor all your agricultural fields',
    descriptionAr: 'إدارة ومراقبة جميع حقولك الزراعية',
    keywords: ['field management', 'crop fields', 'إدارة الحقول'],
  }),

  irrigation: generateMetadata({
    title: 'Irrigation',
    titleAr: 'الري',
    description: 'Smart irrigation management and scheduling',
    descriptionAr: 'إدارة الري الذكي وجدولة المياه',
    keywords: ['irrigation management', 'smart watering', 'إدارة الري'],
  }),

  weather: generateMetadata({
    title: 'Weather',
    titleAr: 'الطقس',
    description: 'Weather forecasts and agricultural advisories',
    descriptionAr: 'توقعات الطقس والاستشارات الزراعية',
    keywords: ['weather forecast', 'agricultural weather', 'توقعات الطقس'],
  }),

  crops: generateMetadata({
    title: 'Crop Health',
    titleAr: 'صحة المحاصيل',
    description: 'Monitor crop health with NDVI analysis and disease detection',
    descriptionAr: 'مراقبة صحة المحاصيل بتحليل NDVI واكتشاف الأمراض',
    keywords: ['crop health', 'NDVI', 'disease detection', 'صحة المحاصيل'],
  }),

  marketplace: generateMetadata({
    title: 'Marketplace',
    titleAr: 'السوق',
    description: 'Agricultural marketplace for buying and selling crops and equipment',
    descriptionAr: 'سوق زراعي لبيع وشراء المحاصيل والمعدات',
    keywords: ['agricultural marketplace', 'farm products', 'السوق الزراعي'],
  }),

  settings: generateMetadata({
    title: 'Settings',
    titleAr: 'الإعدادات',
    description: 'Manage your account settings and preferences',
    descriptionAr: 'إدارة إعدادات حسابك وتفضيلاتك',
    keywords: ['settings', 'account settings', 'الإعدادات'],
  }),

  login: generateMetadata({
    title: 'Login',
    titleAr: 'تسجيل الدخول',
    description: 'Sign in to your SAHOOL account',
    descriptionAr: 'تسجيل الدخول إلى حسابك في سهول',
    robots: 'noindex, nofollow',
  }),

  register: generateMetadata({
    title: 'Register',
    titleAr: 'إنشاء حساب',
    description: 'Create a new SAHOOL account to start managing your farm',
    descriptionAr: 'إنشاء حساب جديد في سهول لبدء إدارة مزرعتك',
  }),
};

export default MetaTags;
