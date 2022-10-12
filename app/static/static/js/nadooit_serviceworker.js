// Base Service Worker implementation.  To use your own Service Worker, set the PWA_SERVICE_WORKER_PATH variable in settings.py

var staticCacheName = "nadooit-pwa" + new Date().getTime();
var filesToCache = [
    '/offline',
    '/static/static/static/nadooit_website/css/style.css',
    '/static/static/static/appicon/maskable_icon_x48.png',
    '/static/static/static/appicon/maskable_icon_x72.png',
    '/static/static/static/appicon/maskable_icon_x96.png',
    '/static/static/static/appicon/maskable_icon_x128.png',
    '/static/static/static/appicon/maskable_icon_x192.png',
    '/static/static/static/appicon/maskable_icon.png',
    '/static/static/static/splashscreen/nadooit.png',
];

// Cache on install
self.addEventListener("install", event => {
    this.skipWaiting();
    event.waitUntil(
        caches.open(staticCacheName)
            .then(cache => {
                return cache.addAll(filesToCache);
            })
    )
});

// Clear cache on activate
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(cacheName => (cacheName.startsWith("nadooit-pwa")))
                    .filter(cacheName => (cacheName !== staticCacheName))
                    .map(cacheName => caches.delete(cacheName))
            );
        })
    );
});

// Serve from Cache
self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                return response || fetch(event.request);
            })
            .catch(() => {
                return caches.match('offline');
            })
    )
});