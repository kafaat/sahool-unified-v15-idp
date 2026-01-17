/**
 * SAHOOL CSP Usage Examples
 * أمثلة استخدام CSP
 *
 * This file demonstrates how to use CSP nonces in various scenarios
 * يوضح هذا الملف كيفية استخدام nonces في سيناريوهات مختلفة
 */

import { getNonce, createInlineScript, createInlineStyle } from "./nonce";
// Logger is used dynamically in the inline script example below
import { logger as _logger } from "@/lib/logger";

// ═══════════════════════════════════════════════════════════════════════════
// Example 1: Server Component with Inline Script
// ═══════════════════════════════════════════════════════════════════════════

export async function ExampleWithInlineScript() {
  const nonce = await getNonce();

  const initScript = `
    logger.log('Initializing component...');
    window.SAHOOL_CONFIG = {
      apiUrl: '${process.env.NEXT_PUBLIC_API_URL}',
      version: '16.0.0'
    };
  `;

  return (
    <div>
      <h1>Example Component</h1>
      <script {...createInlineScript(initScript, nonce)} />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 2: Server Component with Inline Styles
// ═══════════════════════════════════════════════════════════════════════════

export async function ExampleWithInlineStyles() {
  const nonce = await getNonce();

  const customStyles = `
    .custom-container {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 2rem;
      border-radius: 8px;
    }
  `;

  return (
    <div className="custom-container">
      <h2>Styled Component</h2>
      <style {...createInlineStyle(customStyles, nonce)} />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 3: Using CSS Custom Properties (Recommended)
// ═══════════════════════════════════════════════════════════════════════════

interface DynamicStyledProps {
  primaryColor: string;
  secondaryColor: string;
}

export function ExampleWithCSSVariables({
  primaryColor,
  secondaryColor,
}: DynamicStyledProps) {
  return (
    <div
      className="dynamic-theme"
      style={
        {
          "--primary-color": primaryColor,
          "--secondary-color": secondaryColor,
        } as React.CSSProperties
      }
    >
      <h2>Dynamic Theme</h2>
      <p>This uses CSS custom properties which are CSP-safe!</p>
    </div>
  );
}

// Add to your CSS file:
// .dynamic-theme {
//   background: var(--primary-color);
//   color: var(--secondary-color);
// }

// ═══════════════════════════════════════════════════════════════════════════
// Example 4: Map Initialization with Nonce
// ═══════════════════════════════════════════════════════════════════════════

export async function ExampleMapComponent() {
  const nonce = await getNonce();

  const mapInitScript = `
    // Initialize Leaflet map
    const map = L.map('map').setView([15.5527, 48.5164], 6);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
  `;

  return (
    <div>
      <div id="map" style={{ height: "400px", width: "100%" }}></div>
      <script {...createInlineScript(mapInitScript, nonce)} />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 5: Analytics/Tracking Scripts
// ═══════════════════════════════════════════════════════════════════════════

export async function ExampleAnalyticsComponent() {
  const nonce = await getNonce();

  // Custom analytics initialization
  const analyticsScript = `
    (function() {
      window.analytics = {
        track: function(event, properties) {
          logger.log('Track:', event, properties);
          // Send to your analytics service
          fetch('/api/analytics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event, properties })
          });
        }
      };
    })();
  `;

  return (
    <>
      <script {...createInlineScript(analyticsScript, nonce)} />
      {/* Rest of your component */}
    </>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 6: Conditional Script Loading
// ═══════════════════════════════════════════════════════════════════════════

interface ConditionalScriptProps {
  enableFeature: boolean;
}

export async function ExampleConditionalScript({
  enableFeature,
}: ConditionalScriptProps) {
  const nonce = await getNonce();

  if (!enableFeature) {
    return null;
  }

  const featureScript = `
    logger.log('Feature enabled');
    // Initialize feature
  `;

  return (
    <div>
      <h3>Feature Component</h3>
      <script {...createInlineScript(featureScript, nonce)} />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 7: Third-party Library Initialization
// ═══════════════════════════════════════════════════════════════════════════

export async function ExampleThirdPartyInit() {
  const nonce = await getNonce();

  // Initialize a third-party library that's already loaded
  const initScript = `
    if (window.Recharts) {
      window.Recharts.configure({
        locale: 'ar',
        dateFormat: 'DD/MM/YYYY'
      });
    }
  `;

  return (
    <>
      <div id="chart-container"></div>
      <script {...createInlineScript(initScript, nonce)} />
    </>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 8: Error Boundary with Custom Logging
// ═══════════════════════════════════════════════════════════════════════════

export async function ExampleErrorLogging() {
  const nonce = await getNonce();

  const errorLoggingScript = `
    window.addEventListener('error', function(event) {
      logger.error('Global error:', event.error);

      // Send to error tracking service
      fetch('/api/log-error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: event.message,
          stack: event.error?.stack,
          url: window.location.href
        })
      });
    });
  `;

  return <script {...createInlineScript(errorLoggingScript, nonce)} />;
}

// ═══════════════════════════════════════════════════════════════════════════
// Best Practices Notes
// ═══════════════════════════════════════════════════════════════════════════

/*
BEST PRACTICES:

1. ✅ DO: Use external script files when possible
2. ✅ DO: Use CSS modules or Tailwind instead of inline styles
3. ✅ DO: Use CSS custom properties for dynamic styling
4. ✅ DO: Use nonce for necessary inline scripts
5. ✅ DO: Keep inline scripts minimal
6. ✅ DO: Use Server Components when you need nonce

7. ❌ DON'T: Use inline event handlers (onclick, onload, etc.)
8. ❌ DON'T: Use javascript: URLs
9. ❌ DON'T: Add 'unsafe-inline' to CSP
10. ❌ DON'T: Use eval() or Function() constructor

MIGRATION FROM UNSAFE CODE:

Before (CSP-unsafe):
<div onClick="handleClick()">Click me</div>

After (CSP-safe):
<div onClick={handleClick}>Click me</div>

Before (CSP-unsafe):
<a href="javascript:void(0)">Link</a>

After (CSP-safe):
<button onClick={handleClick}>Link</button>

Before (CSP-unsafe):
<div style={{ color: 'red' }}>Text</div>

After (CSP-safe):
<div className="text-red-600">Text</div>  // Tailwind
// OR
<div className="custom-text">Text</div>  // CSS Module
*/
