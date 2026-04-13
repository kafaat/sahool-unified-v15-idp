/* global self, caches */
/**
 * SAHOOL "Kill Switch" Service Worker
 *
 * Purpose: Recover users whose Chrome has a wedged / broken service
 * worker pinned (e.g. a stale /sw.js shell that references bundle
 * hashes no longer on the server).
 *
 * Recovery procedure for affected users:
 *   1. Visit https://<sahool-host>/sw-kill (a tiny page that registers
 *      this script via `navigator.serviceWorker.register('/sw-kill.js')`).
 *   2. This SW takes control, deletes every sahool-* cache, then
 *      `self.registration.unregister()`s itself.
 *   3. Next page load is fully fresh — no controller, no cache.
 *
 * After deploying this file the support team can simply tell users
 * "open /sw-kill once, then refresh" instead of walking them through
 * Chrome DevTools to manually clear site data.
 *
 * This file MUST be kept tiny and side-effect free except for the
 * cache-purge + unregister.
 */

self.addEventListener("install", (event) => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      // 1. Take control of all open clients so we can talk to them.
      await self.clients.claim();

      // 2. Nuke every SAHOOL-owned cache so a stale Next.js HTML shell
      //    can't keep referencing dead bundle hashes.
      if ("caches" in self) {
        const names = await caches.keys();
        await Promise.all(
          names
            .filter((n) => n.startsWith("sahool-"))
            .map((n) => caches.delete(n)),
        );
      }

      // 3. Unregister ourselves so the user has *no* SW after this load.
      await self.registration.unregister();

      // 4. Force every open SAHOOL tab to reload without the controller.
      const allClients = await self.clients.matchAll({
        type: "window",
        includeUncontrolled: true,
      });
      for (const client of allClients) {
        // navigate() is the cleanest reload that bypasses the now-dead SW.
        if ("navigate" in client) {
          try {
            await client.navigate(client.url);
          } catch {
            // some browsers reject navigate() to a different origin; ignore.
          }
        }
      }
    })(),
  );
});

// Pass everything through to the network unconditionally — never serve
// from cache, never cache anything new.
self.addEventListener("fetch", (event) => {
  event.respondWith(fetch(event.request));
});
