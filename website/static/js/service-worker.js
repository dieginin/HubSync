const CACHE_NAME = "pwa-cache-v1";
const URLS_TO_CACHE = [
    "/",
    "/static/site.webmanifest",
    "/static/css/themes.css",
    "/static/images/apple-touch-icon.png",
    "/static/images/favicon-96x96.png",
    "/static/images/favicon.ico",
    "/static/images/favicon.svg",
    "/static/images/hubsync_logo.png",
    "/static/images/web-app-manifest-192x192.png",
    "/static/images/web-app-manifest-512x512.png",
    "/static/js/auto-alert.js",
    "/static/js/navbar-manager.js",
    "/static/js/password-toggle.js",
    "/static/js/service-worker.js",
    "/static/js/theme-manager.js"
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(URLS_TO_CACHE))
    );
});

self.addEventListener("fetch", (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => response || fetch(event.request))
    );
});
