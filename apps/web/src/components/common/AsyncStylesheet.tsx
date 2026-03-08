'use client';

/**
 * AsyncStylesheet — Client Component for non-blocking CSS loading.
 * Renders a <link> with media="print" and swaps it to media="all" on load,
 * so the stylesheet is fetched in the background without blocking first paint.
 *
 * Must be a Client Component because it uses an event handler (onLoad).
 */
interface AsyncStylesheetProps {
  href: string;
  integrity?: string;
  crossOrigin?: 'anonymous' | 'use-credentials';
}

export function AsyncStylesheet({ href, integrity, crossOrigin }: AsyncStylesheetProps) {
  return (
    <link
      rel="stylesheet"
      href={href}
      integrity={integrity}
      crossOrigin={crossOrigin}
      media="print"
      onLoad={(e) => {
        (e.currentTarget as HTMLLinkElement).media = 'all';
      }}
    />
  );
}
