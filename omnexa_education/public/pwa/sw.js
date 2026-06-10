/* Omnexa Education PWA service worker — offline shell cache */
const CACHE = "omnexa-education-v1";
const ASSETS = [
  "/assets/omnexa_education/pwa/manifest.json",
  "/assets/omnexa_education/css/education-rtl.css",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
