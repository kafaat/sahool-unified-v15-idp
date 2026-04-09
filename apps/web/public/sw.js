/* global self, caches, clients, fetch, Request, Response, URL */
/**
 * SAHOOL Service Worker
 * Provides offline-first functionality for the agricultural platform
 *
 * Features:
 * - Cache-first strategy for static assets
 * - Network-first for API calls with cache fallback
 * - Offline page support
 * - Background sync for offline actions
 */

const CACHE_VERSION = "v1.0.0";
const STATIC_CACHE = `sahool-static-${CACHE_VERSION}`;
const DYNAMIC_CACHE = `sahool-dynamic-${CACHE_VERSION}`;
const API_CACHE = `sahool-api-${CACHE_VERSION}`;

// Static assets to cache on install
const STATIC_ASSETS = [
  "/",
  "/dashboard",
  "/offline",
  "/manifest.json",
  "/favicon.svg",
  "/icon-192.png",
  "/icon-512.png",
];

// API endpoints to cache
const CACHEABLE_API_PATTERNS = [
  /\/api\/v1\/fields/,
  /\/api\/v1\/weather/,
  /\/api\/v1\/kpis/,
  /\/api\/v1\/user\/profile/,
];

// Max age for cached API responses (in milliseconds)
const API_CACHE_MAX_AGE = 5 * 60 * 1000; // 5 minutes

/**
 * Install event - cache static assets
 */
self.addEventListener("install", (event) => {
  console.log("[SW] Installing service worker...");

  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => {
        console.log("[SW] Caching static assets");
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log("[SW] Static assets cached");
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error("[SW] Failed to cache static assets:", error);
      }),
  );
});

/**
 * Activate event - clean up old caches
 */
self.addEventListener("activate", (event) => {
  console.log("[SW] Activating service worker...");

  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              return (
                cacheName.startsWith("sahool-") &&
                cacheName !== STATIC_CACHE &&
                cacheName !== DYNAMIC_CACHE &&
                cacheName !== API_CACHE
              );
            })
            .map((cacheName) => {
              console.log("[SW] Deleting old cache:", cacheName);
              return caches.delete(cacheName);
            }),
        );
      })
      .then(() => {
        console.log("[SW] Service worker activated");
        return self.clients.claim();
      }),
  );
});

/**
 * Check if request is for an API endpoint
 */
function isApiRequest(request) {
  return request.url.includes("/api/");
}

/**
 * Check if API endpoint should be cached
 */
function isCacheableApi(url) {
  return CACHEABLE_API_PATTERNS.some((pattern) => pattern.test(url));
}

/**
 * Check if request is for a static asset
 */
function isStaticAsset(request) {
  const url = new URL(request.url);
  return (
    url.pathname.match(/\.(js|css|png|jpg|jpeg|gif|svg|woff|woff2|ico)$/) ||
    url.pathname.startsWith("/_next/static/")
  );
}

/**
 * Network-first strategy for API calls
 * Falls back to cache if network fails
 */
async function networkFirstWithCache(request, cacheName) {
  try {
    const networkResponse = await fetch(request);

    if (networkResponse.ok && isCacheableApi(request.url)) {
      const cache = await caches.open(cacheName);
      const responseToCache = networkResponse.clone();

      // Add timestamp to cached response
      const headers = new Headers(responseToCache.headers);
      headers.set("sw-cached-at", Date.now().toString());

      const cachedResponse = new Response(await responseToCache.blob(), {
        status: responseToCache.status,
        statusText: responseToCache.statusText,
        headers,
      });

      cache.put(request, cachedResponse);
    }

    return networkResponse;
  } catch (_error) {
    console.log("[SW] Network failed, trying cache:", request.url);

    const cachedResponse = await caches.match(request);

    if (cachedResponse) {
      const cachedAt = cachedResponse.headers.get("sw-cached-at");
      const age = cachedAt ? Date.now() - parseInt(cachedAt, 10) : 0;

      if (age < API_CACHE_MAX_AGE) {
        console.log("[SW] Serving from cache:", request.url);
        return cachedResponse;
      }
    }

    // Return offline indicator for API calls
    return new Response(
      JSON.stringify({
        error: "offline",
        message: "You are currently offline",
        messageAr: "أنت غير متصل بالإنترنت حالياً",
      }),
      {
        status: 503,
        headers: { "Content-Type": "application/json" },
      },
    );
  }
}

/**
 * Cache-first strategy for static assets
 */
async function cacheFirstWithNetwork(request, cacheName) {
  const cachedResponse = await caches.match(request);

  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (_error) {
    console.log("[SW] Failed to fetch:", request.url);
    return new Response("Offline", { status: 503 });
  }
}

/**
 * Stale-while-revalidate for dynamic content
 */
async function staleWhileRevalidate(request, cacheName) {
  const cachedResponse = await caches.match(request);

  const fetchPromise = fetch(request)
    .then((networkResponse) => {
      if (networkResponse.ok) {
        // Clone synchronously before the response body is consumed
        const responseClone = networkResponse.clone();
        caches.open(cacheName).then((c) => c.put(request, responseClone));
      }
      return networkResponse;
    })
    .catch(() => cachedResponse);

  return cachedResponse || fetchPromise;
}

/**
 * Fetch event handler
 */
self.addEventListener("fetch", (event) => {
  const { request } = event;

  // Skip non-GET requests
  if (request.method !== "GET") {
    return;
  }

  // Skip chrome-extension and other non-http(s) requests
  if (!request.url.startsWith("http")) {
    return;
  }

  // Handle API requests
  if (isApiRequest(request)) {
    event.respondWith(networkFirstWithCache(request, API_CACHE));
    return;
  }

  // Handle static assets
  if (isStaticAsset(request)) {
    event.respondWith(cacheFirstWithNetwork(request, STATIC_CACHE));
    return;
  }

  // Handle navigation requests (HTML pages)
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(DYNAMIC_CACHE).then((c) => c.put(request, responseClone));
          }
          return response;
        })
        .catch(async () => {
          const cachedPage = await caches.match(request);
          if (cachedPage) {
            return cachedPage;
          }

          // Return offline page
          const offlinePage = await caches.match("/offline");
          if (offlinePage) {
            return offlinePage;
          }

          // Fallback offline HTML
          return new Response(
            `
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
              <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>غير متصل | SAHOOL</title>
                <style>
                  body {
                    font-family: 'Tajawal', sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    background: #f9fafb;
                  }
                  .container {
                    text-align: center;
                    padding: 2rem;
                  }
                  h1 { color: #111827; margin-bottom: 0.5rem; }
                  p { color: #6b7280; margin-bottom: 1.5rem; }
                  button {
                    background: #16a34a;
                    color: white;
                    border: none;
                    padding: 0.75rem 1.5rem;
                    border-radius: 0.5rem;
                    cursor: pointer;
                    font-size: 1rem;
                  }
                  button:hover { background: #15803d; }
                </style>
              </head>
              <body>
                <div class="container">
                  <h1>أنت غير متصل بالإنترنت</h1>
                  <p>يرجى التحقق من اتصالك بالإنترنت والمحاولة مرة أخرى</p>
                  <button onclick="location.reload()">إعادة المحاولة</button>
                </div>
              </body>
            </html>
          `,
            {
              status: 503,
              headers: { "Content-Type": "text/html; charset=utf-8" },
            },
          );
        }),
    );
    return;
  }

  // Default: stale-while-revalidate
  event.respondWith(staleWhileRevalidate(request, DYNAMIC_CACHE));
});

/**
 * Message event handler for communication with the app
 */
self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }

  if (event.data && event.data.type === "CLEAR_CACHE") {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name.startsWith("sahool-"))
            .map((name) => caches.delete(name)),
        );
      }),
    );
  }
});

/**
 * Background sync for offline actions
 */
self.addEventListener("sync", (event) => {
  console.log("[SW] Background sync:", event.tag);

  if (event.tag === "sync-field-data") {
    event.waitUntil(syncFieldData());
  }

  if (event.tag === "sync-offline-actions") {
    event.waitUntil(syncOfflineActions());
  }
});

/**
 * Sync field data when back online
 */
async function syncFieldData() {
  console.log("[SW] Syncing field data...");
  // Implementation would read from IndexedDB and sync to server
}

/**
 * Sync offline actions when back online
 */
async function syncOfflineActions() {
  console.log("[SW] Syncing offline actions...");
  // Implementation would read queued actions from IndexedDB and execute
}

/**
 * Push notification handler
 */
self.addEventListener("push", (event) => {
  if (!event.data) return;

  const data = event.data.json();

  const options = {
    body: data.body || data.messageAr || "New notification",
    icon: "/icon-192.png",
    badge: "/icon-192.png",
    vibrate: [100, 50, 100],
    data: {
      url: data.url || "/dashboard",
    },
    actions: data.actions || [
      { action: "view", title: "عرض | View" },
      { action: "dismiss", title: "إغلاق | Dismiss" },
    ],
  };

  event.waitUntil(
    self.registration.showNotification(data.title || "SAHOOL", options),
  );
});

/**
 * Notification click handler
 */
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  if (event.action === "dismiss") {
    return;
  }

  const url = event.notification.data?.url || "/dashboard";

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
      // Check if there's already an open window
      for (const client of clientList) {
        if (client.url === url && "focus" in client) {
          return client.focus();
        }
      }

      // Open new window if none found
      if (clients.openWindow) {
        return clients.openWindow(url);
      }
    }),
  );
});

console.log("[SW] Service worker loaded");
