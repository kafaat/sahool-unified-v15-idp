/**
 * Minimal HTML escape for server-side templating.
 * Covers the standard 5 — &amp; &lt; &gt; &#34; &#39; — which is sufficient
 * for all text-content and attribute-value contexts in our consent screen.
 */

const ENTITIES: Record<string, string> = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&#34;",
  "'": "&#39;",
};

export function escape(input: string | number | null | undefined): string {
  if (input === null || input === undefined) return "";
  return String(input).replace(/[&<>"']/g, (c) => ENTITIES[c]);
}
