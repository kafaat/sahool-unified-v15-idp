import * as React from "react";

/**
 * Organization Schema for SAHOOL platform
 */
export interface OrganizationSchema {
  name: string;
  nameAr?: string;
  url: string;
  logo?: string;
  description?: string;
  descriptionAr?: string;
  email?: string;
  telephone?: string;
  address?: {
    streetAddress?: string;
    addressLocality?: string;
    addressRegion?: string;
    postalCode?: string;
    addressCountry: string;
  };
  sameAs?: string[];
}

/**
 * Breadcrumb item for navigation schema
 */
export interface BreadcrumbItem {
  name: string;
  nameAr?: string;
  url: string;
}

/**
 * Software Application Schema
 */
export interface SoftwareApplicationSchema {
  name: string;
  nameAr?: string;
  description?: string;
  descriptionAr?: string;
  applicationCategory: string;
  operatingSystem?: string;
  offers?: {
    price: string;
    priceCurrency: string;
  };
}

/**
 * FAQ Item Schema
 */
export interface FAQItem {
  question: string;
  questionAr?: string;
  answer: string;
  answerAr?: string;
}

/**
 * Article Schema for blog/documentation
 */
export interface ArticleSchema {
  headline: string;
  headlineAr?: string;
  description?: string;
  descriptionAr?: string;
  image?: string;
  author?: {
    name: string;
    url?: string;
  };
  datePublished?: string;
  dateModified?: string;
}

/**
 * Product Schema for agricultural products/services
 */
export interface ProductSchema {
  name: string;
  nameAr?: string;
  description?: string;
  descriptionAr?: string;
  image?: string;
  brand?: string;
  offers?: {
    price: string;
    priceCurrency: string;
    availability?: "InStock" | "OutOfStock" | "PreOrder";
  };
}

/**
 * Base component for rendering JSON-LD structured data
 */
function JsonLdScript({ data }: { data: Record<string, unknown> }) {
  // JSON.stringify produces valid JSON with double quotes around keys/values.
  // We only need to escape characters that could allow breaking out of the
  // <script> tag context (< and >) and the ampersand for completeness.
  // We must NOT escape the structural double quotes from JSON.stringify,
  // so we apply targeted replacements instead of sanitizeJsonLd on the full output.
  const jsonStr = JSON.stringify(data)
    .replace(/</g, '\\u003c')
    .replace(/>/g, '\\u003e')
    .replace(/&/g, '\\u0026');

  return (
    <script
      type="application/ld+json"
      // nosemgrep: typescript.react.security.audit.react-dangerouslysetinnerhtml (JSON.stringify output with comprehensive script escape)
      dangerouslySetInnerHTML={{ __html: jsonStr }} // nosemgrep
    />
  );
}

/**
 * Organization JSON-LD for SAHOOL platform
 */
export function OrganizationJsonLd({
  organization,
}: {
  organization: OrganizationSchema;
}) {
  const data = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: organization.name,
    alternateName: organization.nameAr,
    url: organization.url,
    logo: organization.logo,
    description: organization.description,
    email: organization.email,
    telephone: organization.telephone,
    address: organization.address
      ? {
          "@type": "PostalAddress",
          ...organization.address,
        }
      : undefined,
    sameAs: organization.sameAs,
  };

  return <JsonLdScript data={data} />;
}

/**
 * Breadcrumb JSON-LD for navigation
 */
export function BreadcrumbJsonLd({ items }: { items: BreadcrumbItem[] }) {
  const data = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };

  return <JsonLdScript data={data} />;
}

/**
 * Software Application JSON-LD for SAHOOL platform
 */
export function SoftwareApplicationJsonLd({
  app,
}: {
  app: SoftwareApplicationSchema;
}) {
  const data = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: app.name,
    alternateName: app.nameAr,
    description: app.description,
    applicationCategory: app.applicationCategory,
    operatingSystem: app.operatingSystem,
    offers: app.offers
      ? {
          "@type": "Offer",
          price: app.offers.price,
          priceCurrency: app.offers.priceCurrency,
        }
      : undefined,
  };

  return <JsonLdScript data={data} />;
}

/**
 * FAQ JSON-LD for help/support pages
 */
export function FAQJsonLd({ items }: { items: FAQItem[] }) {
  const data = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  };

  return <JsonLdScript data={data} />;
}

/**
 * Article JSON-LD for documentation/blog
 */
export function ArticleJsonLd({ article }: { article: ArticleSchema }) {
  const data = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: article.headline,
    description: article.description,
    image: article.image,
    author: article.author
      ? {
          "@type": "Person",
          name: article.author.name,
          url: article.author.url,
        }
      : undefined,
    datePublished: article.datePublished,
    dateModified: article.dateModified,
    publisher: {
      "@type": "Organization",
      name: "SAHOOL",
      logo: {
        "@type": "ImageObject",
        url: "https://sahool.com/icon-512.png",
      },
    },
  };

  return <JsonLdScript data={data} />;
}

/**
 * Product JSON-LD for agricultural products
 */
export function ProductJsonLd({ product }: { product: ProductSchema }) {
  const data = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: product.name,
    alternateName: product.nameAr,
    description: product.description,
    image: product.image,
    brand: product.brand
      ? {
          "@type": "Brand",
          name: product.brand,
        }
      : undefined,
    offers: product.offers
      ? {
          "@type": "Offer",
          price: product.offers.price,
          priceCurrency: product.offers.priceCurrency,
          availability: `https://schema.org/${product.offers.availability || "InStock"}`,
        }
      : undefined,
  };

  return <JsonLdScript data={data} />;
}

/**
 * WebSite JSON-LD for the main website
 */
export function WebSiteJsonLd({
  name,
  nameAr,
  url,
  description,
  descriptionAr,
  searchUrl,
}: {
  name: string;
  nameAr?: string;
  url: string;
  description?: string;
  descriptionAr?: string;
  searchUrl?: string;
}) {
  // Combine descriptions for multilingual support
  const fullDescription = descriptionAr && description
    ? `${descriptionAr} - ${description}`
    : description || descriptionAr;

  const data: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name,
    alternateName: nameAr,
    url,
    description: fullDescription,
    inLanguage: ["ar", "en"],
  };

  if (searchUrl) {
    data.potentialAction = {
      "@type": "SearchAction",
      target: {
        "@type": "EntryPoint",
        urlTemplate: searchUrl,
      },
      "query-input": "required name=search_term_string",
    };
  }

  return <JsonLdScript data={data} />;
}

/**
 * LocalBusiness JSON-LD for agricultural businesses
 */
export function LocalBusinessJsonLd({
  name,
  nameAr,
  description,
  image,
  telephone,
  address,
  geo,
  openingHours,
}: {
  name: string;
  nameAr?: string;
  description?: string;
  image?: string;
  telephone?: string;
  address?: {
    streetAddress?: string;
    addressLocality?: string;
    addressRegion?: string;
    postalCode?: string;
    addressCountry: string;
  };
  geo?: {
    latitude: number;
    longitude: number;
  };
  openingHours?: string[];
}) {
  const data = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": "#local-business",
    name,
    alternateName: nameAr,
    description,
    image,
    telephone,
    address: address
      ? {
          "@type": "PostalAddress",
          ...address,
        }
      : undefined,
    geo: geo
      ? {
          "@type": "GeoCoordinates",
          latitude: geo.latitude,
          longitude: geo.longitude,
        }
      : undefined,
    openingHoursSpecification: openingHours,
  };

  return <JsonLdScript data={data} />;
}

/**
 * Default SAHOOL structured data for all pages
 */
export function SAHOOLDefaultJsonLd() {
  return (
    <>
      <WebSiteJsonLd
        name="SAHOOL - Smart Agricultural Platform"
        nameAr="سهول - منصة الزراعة الذكية"
        url="https://sahool.com"
        description="SAHOOL is a comprehensive smart agricultural platform for Yemen and the Middle East, providing real-time advisory, irrigation management, and crop health monitoring."
        descriptionAr="سهول هي منصة زراعية ذكية متكاملة لليمن والشرق الأوسط، توفر استشارات فورية وإدارة الري ومراقبة صحة المحاصيل"
        searchUrl="https://sahool.com/search?q={search_term_string}"
      />
      <OrganizationJsonLd
        organization={{
          name: "SAHOOL",
          nameAr: "سهول",
          url: "https://sahool.com",
          logo: "https://sahool.com/icon-512.png",
          description: "Smart Agricultural Intelligence Platform",
          descriptionAr: "منصة الذكاء الزراعي",
          address: {
            addressCountry: "YE",
          },
          sameAs: [
            "https://twitter.com/sahoolplatform",
            "https://facebook.com/sahoolplatform",
          ],
        }}
      />
      <SoftwareApplicationJsonLd
        app={{
          name: "SAHOOL",
          nameAr: "سهول",
          description: "Agricultural management and advisory platform",
          descriptionAr: "منصة إدارة واستشارات زراعية",
          applicationCategory: "BusinessApplication",
          operatingSystem: "Web, iOS, Android",
          offers: {
            price: "0",
            priceCurrency: "USD",
          },
        }}
      />
    </>
  );
}

export default SAHOOLDefaultJsonLd;
