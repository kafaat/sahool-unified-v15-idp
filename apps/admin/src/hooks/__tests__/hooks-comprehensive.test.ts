/**
 * Hooks Comprehensive Tests (Source Code Analysis)
 * اختبارات شاملة للخطافات (تحليل الكود المصدري)
 *
 * Tests for: useWebSocket, useRealTimeAlerts, useCsrf
 * Uses fs.readFileSync to verify hook structure, exports, and patterns.
 */

import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// ═══════════════════════════════════════════════════════════════════════════
// Helper: Read hook source code
// ═══════════════════════════════════════════════════════════════════════════

const HOOKS_DIR = path.resolve(__dirname, '..');

function readHookSource(filename: string): string {
  const filePath = path.join(HOOKS_DIR, filename);
  return fs.readFileSync(filePath, 'utf-8');
}

// ═══════════════════════════════════════════════════════════════════════════
// useWebSocket Tests | اختبارات خطاف WebSocket
// ═══════════════════════════════════════════════════════════════════════════

describe('useWebSocket hook (source analysis)', () => {
  const source = readHookSource('useWebSocket.ts');

  it('exports useWebSocket as a named export', () => {
    expect(source).toMatch(/export\s+function\s+useWebSocket/);
  });

  it('exports useWebSocketEvent as a named export', () => {
    expect(source).toMatch(/export\s+function\s+useWebSocketEvent/);
  });

  it('exports useRealtimeData as a named export', () => {
    expect(source).toMatch(/export\s+function\s+useRealtimeData/);
  });

  it('exports useConnectionStatus as a named export', () => {
    expect(source).toMatch(/export\s+function\s+useConnectionStatus/);
  });

  it('exports AlertMessage, SensorMessage, IrrigationMessage, DiagnosisMessage types', () => {
    expect(source).toMatch(/export\s+type\s*\{[^}]*AlertMessage/);
    expect(source).toMatch(/export\s+type\s*\{[^}]*SensorMessage/);
    expect(source).toMatch(/export\s+type\s*\{[^}]*IrrigationMessage/);
    expect(source).toMatch(/export\s+type\s*\{[^}]*DiagnosisMessage/);
  });

  it('exports ConnectionStatus type', () => {
    expect(source).toMatch(/export\s+type\s*\{[^}]*ConnectionStatus/);
  });

  it('imports useState from react', () => {
    expect(source).toMatch(/import\s*\{[^}]*useState[^}]*\}\s*from\s*['"]react['"]/);
  });

  it('imports useEffect from react', () => {
    expect(source).toMatch(/import\s*\{[^}]*useEffect[^}]*\}\s*from\s*['"]react['"]/);
  });

  it('imports useCallback from react', () => {
    expect(source).toMatch(/import\s*\{[^}]*useCallback[^}]*\}\s*from\s*['"]react['"]/);
  });

  it('imports useRef from react', () => {
    expect(source).toMatch(/import\s*\{[^}]*useRef[^}]*\}\s*from\s*['"]react['"]/);
  });

  it('imports getWebSocketClient from @/lib/websocket', () => {
    expect(source).toMatch(/import\s*\{[^}]*getWebSocketClient[^}]*\}\s*from\s*['"]@\/lib\/websocket['"]/);
  });

  it('imports ConnectionStatus from @/lib/websocket', () => {
    expect(source).toMatch(/import\s*\{[^}]*ConnectionStatus[^}]*\}\s*from\s*['"]@\/lib\/websocket['"]/);
  });

  it('returns status in UseWebSocketReturn', () => {
    expect(source).toMatch(/status:\s*ConnectionStatus/);
    expect(source).toMatch(/return\s*\{[^}]*status/);
  });

  it('returns isConnected in UseWebSocketReturn', () => {
    expect(source).toMatch(/isConnected:\s*boolean/);
    expect(source).toMatch(/return\s*\{[^}]*isConnected/);
  });

  it('returns connect function in UseWebSocketReturn', () => {
    expect(source).toMatch(/connect:\s*\(\)\s*=>\s*void/);
    expect(source).toMatch(/return\s*\{[^}]*connect/);
  });

  it('returns disconnect function in UseWebSocketReturn', () => {
    expect(source).toMatch(/disconnect:\s*\(\)\s*=>\s*void/);
    expect(source).toMatch(/return\s*\{[^}]*disconnect/);
  });

  it('returns subscribe function in UseWebSocketReturn', () => {
    expect(source).toMatch(/subscribe.*EventType.*handler/);
    expect(source).toMatch(/return\s*\{[^}]*subscribe/);
  });

  it('returns send function in UseWebSocketReturn', () => {
    expect(source).toMatch(/send:\s*\(type:\s*string/);
    expect(source).toMatch(/return\s*\{[^}]*send/);
  });

  it('returns error in UseWebSocketReturn', () => {
    expect(source).toMatch(/error:\s*Error\s*\|\s*null/);
    expect(source).toMatch(/return\s*\{[^}]*error/);
  });

  it('uses useEffect for auto-connect on mount', () => {
    expect(source).toMatch(/useEffect\(\s*\(\)\s*=>\s*\{[\s\S]*?autoConnect[\s\S]*?\}/);
  });

  it('uses useEffect for status listener setup', () => {
    expect(source).toMatch(/onStatusChange/);
  });

  it('uses useEffect for error listener setup', () => {
    expect(source).toMatch(/clientRef\.current\.on\(\s*['"]error['"]/);
  });

  it('defines UseWebSocketOptions interface with autoConnect', () => {
    expect(source).toMatch(/autoConnect\?:\s*boolean/);
  });

  it('defines UseWebSocketOptions interface with autoDisconnect', () => {
    expect(source).toMatch(/autoDisconnect\?:\s*boolean/);
  });

  it('provides Arabic status text translations', () => {
    expect(source).toMatch(/متصل/);
    expect(source).toMatch(/غير متصل/);
    expect(source).toMatch(/جاري الاتصال/);
    expect(source).toMatch(/إعادة الاتصال/);
    expect(source).toMatch(/خطأ في الاتصال/);
  });

  it('provides status color mapping', () => {
    expect(source).toMatch(/getStatusColor/);
    expect(source).toMatch(/['"]green['"]/);
    expect(source).toMatch(/['"]yellow['"]/);
    expect(source).toMatch(/['"]red['"]/);
    expect(source).toMatch(/['"]gray['"]/);
  });

  it('has "use client" directive', () => {
    expect(source.trimStart()).toMatch(/^['"]use client['"]/);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// useRealTimeAlerts Tests | اختبارات خطاف التنبيهات في الوقت الفعلي
// ═══════════════════════════════════════════════════════════════════════════

describe('useRealTimeAlerts hook (source analysis)', () => {
  const source = readHookSource('useRealTimeAlerts.ts');

  it('exports useRealTimeAlerts as a named export', () => {
    expect(source).toMatch(/export\s+function\s+useRealTimeAlerts/);
  });

  it('exports useCriticalAlerts as a named export', () => {
    expect(source).toMatch(/export\s+function\s+useCriticalAlerts/);
  });

  it('exports useAlertStats as a named export', () => {
    expect(source).toMatch(/export\s+function\s+useAlertStats/);
  });

  it('exports Alert interface', () => {
    expect(source).toMatch(/export\s+interface\s+Alert/);
  });

  it('imports useState from react', () => {
    expect(source).toMatch(/import\s*\{[^}]*useState[^}]*\}\s*from\s*['"]react['"]/);
  });

  it('imports useEffect from react', () => {
    expect(source).toMatch(/import\s*\{[^}]*useEffect[^}]*\}\s*from\s*['"]react['"]/);
  });

  it('imports useCallback from react', () => {
    expect(source).toMatch(/import\s*\{[^}]*useCallback[^}]*\}\s*from\s*['"]react['"]/);
  });

  it('imports useWebSocketEvent from useWebSocket', () => {
    expect(source).toMatch(/import\s*\{[^}]*useWebSocketEvent[^}]*\}\s*from\s*['"]\.\/useWebSocket['"]/);
  });

  it('imports AlertMessage type from useWebSocket', () => {
    expect(source).toMatch(/import\s+type\s*\{[^}]*AlertMessage[^}]*\}\s*from\s*['"]\.\/useWebSocket['"]/);
  });

  it('imports logger from lib/logger', () => {
    expect(source).toMatch(/import\s*\{[^}]*logger[^}]*\}\s*from\s*['"]\.\.\/lib\/logger['"]/);
  });

  it('returns alerts array', () => {
    expect(source).toMatch(/alerts:\s*Alert\[\]/);
    expect(source).toMatch(/return\s*\{[^}]*alerts/);
  });

  it('returns unreadAlerts array', () => {
    expect(source).toMatch(/unreadAlerts/);
    expect(source).toMatch(/return\s*\{[^}]*unreadAlerts/);
  });

  it('returns unreadCount number', () => {
    expect(source).toMatch(/unreadCount/);
    expect(source).toMatch(/return\s*\{[^}]*unreadCount/);
  });

  it('returns criticalAlerts array', () => {
    expect(source).toMatch(/criticalAlerts/);
    expect(source).toMatch(/return\s*\{[^}]*criticalAlerts/);
  });

  it('returns markAsRead function', () => {
    expect(source).toMatch(/markAsRead:\s*\(alertId:\s*string\)/);
    expect(source).toMatch(/return\s*\{[^}]*markAsRead/);
  });

  it('returns markAllAsRead function', () => {
    expect(source).toMatch(/markAllAsRead:\s*\(\)\s*=>\s*void/);
    expect(source).toMatch(/return\s*\{[^}]*markAllAsRead/);
  });

  it('returns clearAlerts function', () => {
    expect(source).toMatch(/clearAlerts:\s*\(\)\s*=>\s*void/);
    expect(source).toMatch(/return\s*\{[^}]*clearAlerts/);
  });

  it('returns removeAlert function', () => {
    expect(source).toMatch(/removeAlert:\s*\(alertId:\s*string\)/);
    expect(source).toMatch(/return\s*\{[^}]*removeAlert/);
  });

  it('defines severity levels for filtering', () => {
    expect(source).toMatch(/SEVERITY_LEVELS/);
    expect(source).toMatch(/low:\s*0/);
    expect(source).toMatch(/medium:\s*1/);
    expect(source).toMatch(/high:\s*2/);
    expect(source).toMatch(/critical:\s*3/);
  });

  it('supports maxAlerts option', () => {
    expect(source).toMatch(/maxAlerts\?:\s*number/);
  });

  it('supports minSeverity option', () => {
    expect(source).toMatch(/minSeverity\?:\s*['"]low['"]\s*\|\s*['"]medium['"]\s*\|\s*['"]high['"]\s*\|\s*['"]critical['"]/);
  });

  it('supports enableNotifications option', () => {
    expect(source).toMatch(/enableNotifications\?:\s*boolean/);
  });

  it('supports onNewAlert callback option', () => {
    expect(source).toMatch(/onNewAlert\?:\s*\(alert:\s*Alert\)\s*=>\s*void/);
  });

  it('implements browser notification support', () => {
    expect(source).toMatch(/showBrowserNotification/);
    expect(source).toMatch(/Notification\.permission/);
    expect(source).toMatch(/new Notification/);
  });

  it('implements alert sound playback', () => {
    expect(source).toMatch(/playAlertSound/);
    expect(source).toMatch(/new Audio/);
  });

  it('uses useEffect for notification permission request', () => {
    expect(source).toMatch(/Notification\.requestPermission/);
  });

  it('prevents duplicate alerts by checking existing IDs', () => {
    expect(source).toMatch(/prev\.some\(\s*\(a\)\s*=>\s*a\.id\s*===\s*alert\.id\)/);
  });

  it('Alert interface extends AlertMessage with read and notified fields', () => {
    expect(source).toMatch(/export\s+interface\s+Alert\s+extends\s+AlertMessage/);
    expect(source).toMatch(/read:\s*boolean/);
    expect(source).toMatch(/notified:\s*boolean/);
  });

  it('useCriticalAlerts returns criticalCount and hasCritical', () => {
    expect(source).toMatch(/criticalCount:\s*criticalAlerts\.length/);
    expect(source).toMatch(/hasCritical:\s*criticalAlerts\.length\s*>\s*0/);
  });

  it('useAlertStats computes bySeverity and byType', () => {
    expect(source).toMatch(/bySeverity/);
    expect(source).toMatch(/byType/);
  });

  it('has "use client" directive', () => {
    expect(source.trimStart()).toMatch(/^['"]use client['"]/);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// useCsrf Tests | اختبارات خطاف CSRF
// ═══════════════════════════════════════════════════════════════════════════

describe('useCsrf hook (source analysis)', () => {
  const source = readHookSource('useCsrf.ts');

  it('exports useCsrf as a named export', () => {
    expect(source).toMatch(/export\s+function\s+useCsrf/);
  });

  it('exports useCsrfForm as a named export', () => {
    expect(source).toMatch(/export\s+function\s+useCsrfForm/);
  });

  it('exports useCsrf as default export', () => {
    expect(source).toMatch(/export\s+default\s+useCsrf/);
  });

  it('imports useState from react', () => {
    expect(source).toMatch(/import\s*\{[^}]*useState[^}]*\}\s*from\s*['"]react['"]/);
  });

  it('imports useEffect from react', () => {
    expect(source).toMatch(/import\s*\{[^}]*useEffect[^}]*\}\s*from\s*['"]react['"]/);
  });

  it('imports useCallback from react', () => {
    expect(source).toMatch(/import\s*\{[^}]*useCallback[^}]*\}\s*from\s*['"]react['"]/);
  });

  it('imports useRef from react', () => {
    expect(source).toMatch(/import\s*\{[^}]*useRef[^}]*\}\s*from\s*['"]react['"]/);
  });

  it('imports CSRF_CONFIG from @/lib/csrf', () => {
    expect(source).toMatch(/import\s*\{[^}]*CSRF_CONFIG[^}]*\}\s*from\s*['"]@\/lib\/csrf['"]/);
  });

  it('returns token in state', () => {
    expect(source).toMatch(/token:\s*string\s*\|\s*null/);
  });

  it('returns expiresAt in state', () => {
    expect(source).toMatch(/expiresAt:\s*number\s*\|\s*null/);
  });

  it('returns loading in state', () => {
    expect(source).toMatch(/loading:\s*boolean/);
  });

  it('returns error in state', () => {
    expect(source).toMatch(/error:\s*string\s*\|\s*null/);
  });

  it('returns ready boolean', () => {
    expect(source).toMatch(/ready:\s*boolean/);
    expect(source).toMatch(/ready:\s*!!state\.token\s*&&\s*!state\.loading\s*&&\s*!state\.error/);
  });

  it('returns fetchToken function', () => {
    expect(source).toMatch(/fetchToken:\s*\(\)\s*=>\s*Promise<void>/);
  });

  it('returns refreshToken function', () => {
    expect(source).toMatch(/refreshToken:\s*\(\)\s*=>\s*Promise<void>/);
  });

  it('returns getHeaders function', () => {
    expect(source).toMatch(/getHeaders:\s*\(additionalHeaders\?:\s*HeadersInit\)\s*=>\s*HeadersInit/);
  });

  it('returns addToFormData function', () => {
    expect(source).toMatch(/addToFormData:\s*\(formData:\s*FormData\)\s*=>\s*void/);
  });

  it('returns getHiddenInput function', () => {
    expect(source).toMatch(/getHiddenInput:\s*\(\)\s*=>\s*\{\s*name:\s*string;\s*value:\s*string\s*\}/);
  });

  it('returns needsRefresh function', () => {
    expect(source).toMatch(/needsRefresh:\s*\(\)\s*=>\s*boolean/);
  });

  it('fetches token from /api/csrf-token endpoint', () => {
    expect(source).toMatch(/fetch\(\s*['"]\/api\/csrf-token['"]/);
  });

  it('uses GET method for fetchToken', () => {
    expect(source).toMatch(/method:\s*['"]GET['"]/);
  });

  it('uses POST method for refreshToken', () => {
    expect(source).toMatch(/method:\s*['"]POST['"]/);
  });

  it('uses credentials: include for cookie-based auth', () => {
    expect(source).toMatch(/credentials:\s*['"]include['"]/);
  });

  it('supports autoFetch option', () => {
    expect(source).toMatch(/autoFetch\?:\s*boolean/);
    expect(source).toMatch(/autoFetch\s*=\s*true/);
  });

  it('supports refreshBuffer option with default of 5 minutes', () => {
    expect(source).toMatch(/refreshBuffer\?:\s*number/);
    expect(source).toMatch(/DEFAULT_REFRESH_BUFFER\s*=\s*5\s*\*\s*60\s*\*\s*1000/);
  });

  it('uses useEffect for auto-fetch on mount', () => {
    expect(source).toMatch(/useEffect\(\s*\(\)\s*=>\s*\{[\s\S]*?autoFetch[\s\S]*?\}/);
  });

  it('uses useEffect for auto-refresh scheduling', () => {
    expect(source).toMatch(/timeUntilRefresh/);
    expect(source).toMatch(/refreshTimeoutRef/);
  });

  it('tracks mounted state with isMountedRef', () => {
    expect(source).toMatch(/isMountedRef/);
    expect(source).toMatch(/isMountedRef\.current\s*=\s*true/);
    expect(source).toMatch(/isMountedRef\.current\s*=\s*false/);
  });

  it('clears timeout on cleanup', () => {
    expect(source).toMatch(/clearTimeout\(\s*refreshTimeoutRef\.current\s*\)/);
  });

  it('uses CSRF_CONFIG.HEADER_NAME for headers', () => {
    expect(source).toMatch(/CSRF_CONFIG\.HEADER_NAME/);
  });

  it('uses CSRF_CONFIG.FIELD_NAME for form data', () => {
    expect(source).toMatch(/CSRF_CONFIG\.FIELD_NAME/);
  });

  it('handles Headers, Array, and object additionalHeaders in getHeaders', () => {
    expect(source).toMatch(/additionalHeaders\s+instanceof\s+Headers/);
    expect(source).toMatch(/Array\.isArray\(\s*additionalHeaders\s*\)/);
    expect(source).toMatch(/Object\.assign\(\s*headers,\s*additionalHeaders\s*\)/);
  });

  it('useCsrfForm returns loading, error, and submitWithCsrf', () => {
    expect(source).toMatch(/interface\s+UseCsrfFormReturn/);
    expect(source).toMatch(/submitWithCsrf/);
    expect(source).toMatch(/event\.preventDefault\(\)/);
  });

  it('has "use client" directive', () => {
    expect(source.trimStart()).toMatch(/^['"]use client['"]/);
  });
});
