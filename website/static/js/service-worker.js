const CACHE_NAME = "pwa-cache-v1";
const URLS_TO_CACHE = [
    "/",
    "/website/site.webmanifest",
    "/website/static/css/theme.css",
    "/website/static/images/apple-touch-icon.png",
    "/website/static/images/favicon-96x96.png",
    "/website/static/images/favicon.ico",
    "/website/static/images/favicon.svg",
    "/website/static/images/hubsync_logo.png",
    "/website/static/images/web-app-manifest-192x192.png",
    "/website/static/images/web-app-manifest-512x512.png",
    "/website/static/js/auto-alert.js",
    "/website/static/js/navbar-manager.js",
    "/website/static/js/password-toggle.js",
    "/website/static/js/service-worker.js",
    "/website/static/js/theme-manager.js"
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
