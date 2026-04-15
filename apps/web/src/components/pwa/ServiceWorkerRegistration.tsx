'use client';

import { useEffect, useState, useCallback } from 'react';
import { logger } from '@/lib/logger';

interface ServiceWorkerStatus {
  isSupported: boolean;
  isRegistered: boolean;
  isOnline: boolean;
  hasUpdate: boolean;
  registration: ServiceWorkerRegistration | null;
}

/**
 * Hook to manage service worker registration and updates
 */
export function useServiceWorker() {
  const [status, setStatus] = useState<ServiceWorkerStatus>({
    isSupported: false,
    isRegistered: false,
    isOnline: true,
    hasUpdate: false,
    registration: null,
  });

  // Check online status
  useEffect(() => {
    const updateOnlineStatus = () => {
      setStatus((prev) => ({ ...prev, isOnline: navigator.onLine }));
    };

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);

    return () => {
      window.removeEventListener('online', updateOnlineStatus);
      window.removeEventListener('offline', updateOnlineStatus);
    };
  }, []);

  // Register service worker.
  //
  // Chrome-specific note: once a service worker is installed, Chrome will
  // keep serving cached responses for `/` and `/dashboard` (see `sw.js`)
  // until the cache version is bumped OR the user manually clears site
  // data. Firefox is less aggressive. During active development that
  // manifests as "works in other browsers, broken in Chrome" because
  // Chrome is pinning an old bundle hash while Firefox refetches.
  //
  // To avoid that class of bug we only register the SW when:
  //   1. NODE_ENV === 'production', AND
  //   2. `NEXT_PUBLIC_ENABLE_PWA !== 'false'` (kill switch).
  // Development builds actively UNREGISTER any previously installed SW
  // and purge its caches so a broken / stale SW cannot linger across
  // dev sessions.
  useEffect(() => {
    const isProduction = process.env.NODE_ENV === 'production';
    const pwaKillSwitchOff = process.env.NEXT_PUBLIC_ENABLE_PWA === 'false';
    const shouldRegister = isProduction && !pwaKillSwitchOff;

    const unregisterAll = async () => {
      if (!('serviceWorker' in navigator)) return;
      try {
        const registrations = await navigator.serviceWorker.getRegistrations();
        await Promise.all(registrations.map((r) => r.unregister()));
        if ('caches' in window) {
          const names = await caches.keys();
          await Promise.all(
            names.filter((n) => n.startsWith('sahool-')).map((n) => caches.delete(n))
          );
        }
        if (registrations.length > 0) {
          logger.log('[PWA] Unregistered stale service worker(s) and cleared sahool-* caches');
        }
      } catch (error) {
        logger.error('[PWA] Failed to unregister existing service worker:', error);
      }
    };

    const registerSW = async () => {
      if (!('serviceWorker' in navigator)) {
        setStatus((prev) => ({ ...prev, isSupported: false }));
        return;
      }

      setStatus((prev) => ({ ...prev, isSupported: true }));

      if (!shouldRegister) {
        // Kill switch or non-production build: actively purge any SW that a
        // prior visit may have installed. This is the "escape hatch" for
        // Chrome users who already have a stale SW pinned.
        await unregisterAll();
        return;
      }

      try {
        const registration = await navigator.serviceWorker.register('/sw.js', {
          scope: '/',
          // `updateViaCache: 'none'` forces the browser to bypass HTTP cache
          // when checking for a new `/sw.js`, so a deploy is always picked
          // up on the next navigation instead of waiting for the HTTP cache
          // to expire.
          updateViaCache: 'none',
        });

        setStatus((prev) => ({
          ...prev,
          isRegistered: true,
          registration,
        }));

        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;

          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                setStatus((prev) => ({ ...prev, hasUpdate: true }));
              }
            });
          }
        });

        // Check for existing waiting worker
        if (registration.waiting) {
          setStatus((prev) => ({ ...prev, hasUpdate: true }));
        }

        logger.log('[PWA] Service worker registered successfully');
      } catch (error) {
        logger.error('[PWA] Service worker registration failed:', error);
      }
    };

    registerSW();
  }, []);

  // Update service worker
  const updateServiceWorker = useCallback(() => {
    if (status.registration?.waiting) {
      status.registration.waiting.postMessage({ type: 'SKIP_WAITING' });
      window.location.reload();
    }
  }, [status.registration]);

  // Clear cache
  const clearCache = useCallback(async () => {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({ type: 'CLEAR_CACHE' });
    }

    // Also clear caches directly
    if ('caches' in window) {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.filter((name) => name.startsWith('sahool-')).map((name) => caches.delete(name))
      );
    }
  }, []);

  return {
    ...status,
    updateServiceWorker,
    clearCache,
  };
}

/**
 * Component to display offline status indicator
 */
export function OfflineIndicator() {
  const { isOnline, isSupported } = useServiceWorker();
  const [dismissed, setDismissed] = useState(false);

  if (!isSupported || isOnline || dismissed) {
    return null;
  }

  return (
    <div
      className="fixed bottom-4 start-4 end-4 sm:start-auto sm:end-4 sm:max-w-sm z-50 bg-yellow-50 border border-yellow-200 rounded-lg p-4 shadow-lg"
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <svg
            className="w-5 h-5 text-yellow-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        <div className="flex-1">
          <p className="font-semibold text-yellow-800">
            أنت غير متصل بالإنترنت
            <span className="sr-only"> - You are offline</span>
          </p>
          <p className="text-sm text-yellow-700 mt-1">
            يمكنك متابعة العمل. سيتم مزامنة البيانات عند الاتصال.
            <span className="sr-only">
              {' '}
              - You can continue working. Data will sync when connected.
            </span>
          </p>
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="flex-shrink-0 text-yellow-600 hover:text-yellow-800"
          aria-label="إغلاق - Dismiss"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}

/**
 * Component to prompt for service worker update
 */
export function UpdatePrompt() {
  const { hasUpdate, updateServiceWorker } = useServiceWorker();
  const [dismissed, setDismissed] = useState(false);

  if (!hasUpdate || dismissed) {
    return null;
  }

  return (
    <div
      className="fixed bottom-4 start-4 end-4 sm:start-auto sm:end-4 sm:max-w-sm z-50 bg-blue-50 border border-blue-200 rounded-lg p-4 shadow-lg"
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <svg
            className="w-5 h-5 text-blue-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
        </div>
        <div className="flex-1">
          <p className="font-semibold text-blue-800">
            تحديث جديد متاح
            <span className="sr-only"> - New update available</span>
          </p>
          <p className="text-sm text-blue-700 mt-1">يتوفر إصدار جديد من التطبيق. انقر للتحديث.</p>
          <div className="mt-3 flex gap-2">
            <button
              onClick={updateServiceWorker}
              className="px-3 py-1.5 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              تحديث الآن
            </button>
            <button
              onClick={() => setDismissed(true)}
              className="px-3 py-1.5 text-blue-600 text-sm font-medium hover:text-blue-800"
            >
              لاحقاً
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Component to display install PWA prompt
 */
export function InstallPrompt() {
  const [showPrompt, setShowPrompt] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setShowPrompt(true);
    };

    window.addEventListener('beforeinstallprompt', handler);

    return () => {
      window.removeEventListener('beforeinstallprompt', handler);
    };
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {
      logger.log('[PWA] App installed');
    }

    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  if (!showPrompt) {
    return null;
  }

  return (
    <div
      className="fixed bottom-4 start-4 end-4 sm:start-auto sm:end-4 sm:max-w-sm z-50 bg-green-50 border border-green-200 rounded-lg p-4 shadow-lg"
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <svg
            className="w-5 h-5 text-green-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
        </div>
        <div className="flex-1">
          <p className="font-semibold text-green-800">
            تثبيت تطبيق سهول
            <span className="sr-only"> - Install SAHOOL App</span>
          </p>
          <p className="text-sm text-green-700 mt-1">
            ثبت التطبيق للوصول السريع والعمل بدون اتصال.
          </p>
          <div className="mt-3 flex gap-2">
            <button
              onClick={handleInstall}
              className="px-3 py-1.5 bg-green-600 text-white rounded-md text-sm font-medium hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            >
              تثبيت
            </button>
            <button
              onClick={() => setShowPrompt(false)}
              className="px-3 py-1.5 text-green-600 text-sm font-medium hover:text-green-800"
            >
              ليس الآن
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Type for beforeinstallprompt event
interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

/**
 * Combined PWA status component
 */
export function PWAStatus() {
  return (
    <>
      <OfflineIndicator />
      <UpdatePrompt />
      <InstallPrompt />
    </>
  );
}

export default PWAStatus;
