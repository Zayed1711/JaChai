// JaChai Cache Buster & Instant Sync Service Worker
self.addEventListener("install", (event) => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(keys.map((key) => caches.delete(key)));
    }).then(() => self.clients.claim()).then(() => {
      return self.clients.matchAll({ type: 'window' }).then((clients) => {
        clients.forEach((client) => client.navigate(client.url));
      });
    })
  );
});

self.addEventListener("fetch", (event) => {
  // Always fetch fresh content from network to prevent serving stale pre-cached HTML
  event.respondWith(fetch(event.request));
});
