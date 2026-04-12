/**
 * Consent screen — bilingual (Arabic RTL + English).
 *
 * This is a SERVER-RENDERED HTML page. It must be self-contained (no
 * external JS/CSS) because it runs on the auth-server's origin, not
 * the partner's. CSRF token is embedded in a hidden field and validated
 * on POST.
 *
 * Scope labels are derived client-side from a lookup table so we can
 * show the user what they're consenting to in plain language rather
 * than raw scope strings like "operations:planting:read".
 */

import { escape } from "../utils/html";

export interface ConsentViewModel {
  /** Signed CSRF token to embed in the form */
  csrfToken: string;
  /** Partner display info */
  client: {
    name: string;
    nameAr?: string | null;
    logoUrl?: string | null;
    homepageUrl?: string | null;
    description?: string | null;
  };
  /** Scopes being requested (raw strings) */
  scopes: string[];
  /** Scopes the user has previously approved for this client */
  priorScopes: string[];
  /** OAuth form parameters — echoed back on POST unchanged */
  form: {
    client_id: string;
    redirect_uri: string;
    scope: string;
    state?: string | null;
    nonce?: string | null;
    code_challenge?: string | null;
    code_challenge_method?: string | null;
    response_type: string;
  };
  /** Current user (to show "Not you? Sign out") */
  user: {
    email?: string;
    name?: string;
    nameAr?: string | null;
  };
  /** Preferred language */
  locale: "ar" | "en";
  /** POST target (usually same URL as current) */
  postUrl: string;
  /** Sign-out URL back to user-service */
  signOutUrl?: string;
}

/** Human-readable scope labels — extend as new scopes ship. */
const SCOPE_LABELS: Record<string, { en: string; ar: string; icon: string }> = {
  openid: { en: "Verify your identity", ar: "التحقق من هويتك", icon: "🪪" },
  profile: { en: "Read your name and basic profile", ar: "قراءة اسمك وبياناتك الأساسية", icon: "👤" },
  email: { en: "Read your email address", ar: "قراءة عنوان بريدك الإلكتروني", icon: "✉️" },
  offline_access: { en: "Stay signed in across sessions", ar: "البقاء متصلاً بين الجلسات", icon: "🔁" },
  "fields:read": { en: "View your fields and boundaries", ar: "عرض حقولك وحدودها", icon: "🌾" },
  "fields:write": { en: "Create and modify your fields", ar: "إنشاء وتعديل حقولك", icon: "✏️" },
  "boundaries:read": { en: "View field boundaries", ar: "عرض حدود الحقول", icon: "📐" },
  "boundaries:write": { en: "Create boundaries on your behalf", ar: "إنشاء حدود نيابةً عنك", icon: "📐" },
  "operations:planting:read": { en: "View planting operations", ar: "عرض عمليات الزراعة", icon: "🌱" },
  "operations:planting:write": { en: "Record planting operations", ar: "تسجيل عمليات الزراعة", icon: "🌱" },
  "operations:harvest:read": { en: "View harvest data", ar: "عرض بيانات الحصاد", icon: "🌽" },
  "operations:harvest:write": { en: "Record harvest data", ar: "تسجيل بيانات الحصاد", icon: "🌽" },
  "operations:application:read": { en: "View fertilizer/pesticide applications", ar: "عرض تطبيقات الأسمدة والمبيدات", icon: "🧪" },
  "operations:application:write": { en: "Record fertilizer/pesticide applications", ar: "تسجيل تطبيقات الأسمدة والمبيدات", icon: "🧪" },
  "operations:scouting:read": { en: "View scouting observations", ar: "عرض ملاحظات الاستكشاف", icon: "🔍" },
  "operations:scouting:write": { en: "Record scouting observations + photos", ar: "تسجيل ملاحظات وصور الاستكشاف", icon: "📸" },
  "imagery:ndvi:read": { en: "View NDVI imagery for your fields", ar: "عرض صور NDVI لحقولك", icon: "🛰️" },
  "imagery:ndvi:write": { en: "Upload NDVI imagery", ar: "رفع صور NDVI", icon: "🛰️" },
  "imagery:thermal:read": { en: "View thermal imagery", ar: "عرض الصور الحرارية", icon: "🌡️" },
  "imagery:rgb:read": { en: "View RGB/aerial imagery", ar: "عرض الصور الجوية RGB", icon: "🖼️" },
  "soil:read": { en: "View soil test results", ar: "عرض نتائج فحص التربة", icon: "🧱" },
  "soil:write": { en: "Upload soil test results", ar: "رفع نتائج فحص التربة", icon: "🧱" },
  "weather:read": { en: "Access weather data for your locations", ar: "الوصول إلى بيانات الطقس لمواقعك", icon: "🌤️" },
  "advisory:read": { en: "Read agronomic advisories", ar: "قراءة الاستشارات الزراعية", icon: "💡" },
  "ai:vision:invoke": { en: "Analyze images with SAHOOL AI vision", ar: "تحليل الصور بواسطة الرؤية الحاسوبية", icon: "🤖" },
  "carbon:read": { en: "View carbon footprint data", ar: "عرض بيانات البصمة الكربونية", icon: "♻️" },
  "carbon:mrv:export": { en: "Export carbon MRV reports (Verra/Gold Standard)", ar: "تصدير تقارير كربون MRV", icon: "📤" },
  "exports:read": { en: "Download data exports on your behalf", ar: "تنزيل بيانات مُصدَّرة نيابةً عنك", icon: "📦" },
  partnerapis: { en: "Call SAHOOL partner APIs", ar: "استخدام واجهات شركاء سهول", icon: "🔗" },
  platform: { en: "Access the SAHOOL platform", ar: "الوصول إلى منصة سهول", icon: "🏛️" },
};

function scopeLabel(scope: string, locale: "ar" | "en") {
  const entry = SCOPE_LABELS[scope];
  if (!entry) {
    return { text: scope, icon: "•" };
  }
  return { text: entry[locale], icon: entry.icon };
}

/**
 * Renders the consent screen as a full HTML document.
 * Security: inline CSS only, no external resources, no JS required.
 */
export function renderConsent(vm: ConsentViewModel): string {
  const isAr = vm.locale === "ar";
  const dir = isAr ? "rtl" : "ltr";
  const lang = isAr ? "ar" : "en";

  const scopeRows = vm.scopes
    .map((s) => {
      const label = scopeLabel(s, vm.locale);
      const known = vm.priorScopes.includes(s);
      return `
        <li class="scope ${known ? "scope--known" : ""}">
          <span class="scope-icon" aria-hidden="true">${escape(label.icon)}</span>
          <span class="scope-text">${escape(label.text)}</span>
          <code class="scope-raw">${escape(s)}</code>
          ${known ? `<span class="scope-badge">${isAr ? "مُعتَمد سابقاً" : "already approved"}</span>` : ""}
        </li>`;
    })
    .join("");

  const clientName = isAr && vm.client.nameAr ? vm.client.nameAr : vm.client.name;
  const userLabel = isAr && vm.user.nameAr ? vm.user.nameAr : vm.user.name ?? vm.user.email ?? "";

  const t = {
    title: isAr ? "منح الإذن لـ" : "Authorize",
    subtitle: isAr
      ? "يطلب هذا التطبيق الصلاحيات التالية للوصول إلى حسابك في سهول:"
      : "This application is requesting access to the following in your SAHOOL account:",
    allow: isAr ? "السماح" : "Allow",
    deny: isAr ? "رفض" : "Deny",
    signedInAs: isAr ? "مسجَّل الدخول باسم" : "Signed in as",
    notYou: isAr ? "ليس أنت؟" : "Not you?",
    signOut: isAr ? "تسجيل الخروج" : "Sign out",
    securityNote: isAr
      ? "سيعود المتصفح إلى التطبيق مع نتيجة اختيارك. يمكنك إلغاء هذا الإذن في أي وقت من إعدادات حسابك."
      : "Your browser will return to the application with your choice. You can revoke this at any time from your SAHOOL account settings.",
    visitHomepage: isAr ? "زيارة موقع التطبيق" : "Visit developer site",
  };

  const logoHtml = vm.client.logoUrl
    ? `<img class="client-logo" src="${escape(vm.client.logoUrl)}" alt="">`
    : `<div class="client-logo client-logo--fallback" aria-hidden="true">${escape(clientName.charAt(0).toUpperCase())}</div>`;

  const homepageHtml = vm.client.homepageUrl
    ? `<a class="client-homepage" href="${escape(vm.client.homepageUrl)}" rel="noopener noreferrer nofollow" target="_blank">${t.visitHomepage}</a>`
    : "";

  const hiddenFields = [
    ["csrf_token", vm.csrfToken],
    ["client_id", vm.form.client_id],
    ["redirect_uri", vm.form.redirect_uri],
    ["scope", vm.form.scope],
    ["state", vm.form.state ?? ""],
    ["nonce", vm.form.nonce ?? ""],
    ["code_challenge", vm.form.code_challenge ?? ""],
    ["code_challenge_method", vm.form.code_challenge_method ?? ""],
    ["response_type", vm.form.response_type],
  ]
    .filter(([, v]) => v !== "")
    .map(
      ([name, value]) =>
        `<input type="hidden" name="${escape(String(name))}" value="${escape(String(value))}">`,
    )
    .join("");

  return `<!DOCTYPE html>
<html lang="${lang}" dir="${dir}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>${escape(t.title)} ${escape(clientName)}</title>
  <style>
    *{box-sizing:border-box}
    html,body{margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Tahoma,"Noto Sans Arabic",Arial,sans-serif;background:#f4f6fb;color:#1a2332;line-height:1.55}
    .card{max-width:520px;margin:48px auto;padding:32px;background:#fff;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.06),0 4px 12px rgba(0,0,0,.04)}
    .header{display:flex;align-items:center;gap:16px;margin-bottom:24px}
    .client-logo{width:56px;height:56px;border-radius:12px;object-fit:cover;background:#e8eef7;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:700;color:#3a5a9c;flex-shrink:0}
    .client-logo--fallback{background:linear-gradient(135deg,#8fb4ff,#6a8fd8)}
    .client-info{flex:1;min-width:0}
    .client-info h1{margin:0;font-size:20px;font-weight:600;color:#1a2332;word-wrap:break-word}
    .client-info p{margin:4px 0 0;font-size:14px;color:#5a6a80}
    .client-homepage{display:inline-block;margin-top:6px;font-size:13px;color:#3a5a9c;text-decoration:none}
    .client-homepage:hover{text-decoration:underline}
    .subtitle{font-size:15px;color:#3a4a60;margin:16px 0 12px}
    .scopes{list-style:none;padding:0;margin:0 0 24px;border:1px solid #e5ebf3;border-radius:8px;overflow:hidden}
    .scope{display:flex;align-items:center;gap:12px;padding:12px 16px;border-bottom:1px solid #eef2f7}
    .scope:last-child{border-bottom:none}
    .scope--known{background:#f8fafd}
    .scope-icon{font-size:20px;width:28px;text-align:center;flex-shrink:0}
    .scope-text{flex:1;font-size:14px;color:#1a2332}
    .scope-raw{font-size:11px;color:#8a98ad;font-family:ui-monospace,"SF Mono",Menlo,monospace;background:#f2f5f9;padding:2px 6px;border-radius:4px;margin:0 6px}
    .scope-badge{font-size:11px;color:#3a7a3a;background:#e8f5e8;padding:2px 8px;border-radius:100px}
    .actions{display:flex;gap:12px;margin-top:24px}
    button{font:inherit;cursor:pointer;padding:12px 24px;border-radius:8px;border:0;font-weight:600;font-size:15px;flex:1;transition:background .1s}
    button[name="decision"][value="allow"]{background:#2d6cb3;color:#fff}
    button[name="decision"][value="allow"]:hover{background:#1f5aa0}
    button[name="decision"][value="deny"]{background:#f2f5f9;color:#1a2332;border:1px solid #dce4ef}
    button[name="decision"][value="deny"]:hover{background:#e8edf4}
    .footer{margin-top:24px;padding-top:20px;border-top:1px solid #eef2f7;font-size:12px;color:#7a8699;text-align:center}
    .footer p{margin:4px 0}
    .footer a{color:#3a5a9c;text-decoration:none}
    .footer a:hover{text-decoration:underline}
    .user-strip{background:#f8fafd;padding:10px 14px;border-radius:8px;font-size:13px;color:#5a6a80;display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:20px;flex-wrap:wrap}
    @media (max-width:560px){.card{margin:0;border-radius:0;min-height:100vh;padding:24px}}
  </style>
</head>
<body>
  <main class="card" role="main">
    <div class="header">
      ${logoHtml}
      <div class="client-info">
        <h1>${escape(clientName)}</h1>
        ${vm.client.description ? `<p>${escape(vm.client.description)}</p>` : ""}
        ${homepageHtml}
      </div>
    </div>

    <div class="user-strip">
      <span>${escape(t.signedInAs)}: <strong>${escape(userLabel)}</strong></span>
      ${vm.signOutUrl ? `<a href="${escape(vm.signOutUrl)}">${escape(t.notYou)} ${escape(t.signOut)}</a>` : ""}
    </div>

    <p class="subtitle">${escape(t.subtitle)}</p>
    <ul class="scopes">${scopeRows}</ul>

    <form method="post" action="${escape(vm.postUrl)}" autocomplete="off">
      ${hiddenFields}
      <div class="actions">
        <button type="submit" name="decision" value="deny">${escape(t.deny)}</button>
        <button type="submit" name="decision" value="allow">${escape(t.allow)}</button>
      </div>
    </form>

    <div class="footer">
      <p>${escape(t.securityNote)}</p>
      <p><strong>SAHOOL</strong> · partner-auth-service</p>
    </div>
  </main>
</body>
</html>`;
}
