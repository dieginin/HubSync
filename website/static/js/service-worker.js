const CACHE_NAME = "hubsync-cache-v4";
const OFFLINE_PAGE = "/static/offline.html";
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
    "/static/js/theme-manager.js",
    OFFLINE_PAGE
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Caching offline page and resources');
                // Cache the offline page first
                return cache.add(OFFLINE_PAGE)
                    .then(() => {
                        // Then cache other resources, but don't fail if some fail
                        return Promise.allSettled(
                            URLS_TO_CACHE.filter(url => url !== OFFLINE_PAGE)
                                .map(url => cache.add(url).catch(err => console.warn('Failed to cache:', url, err)))
                        );
                    });
            })
    );
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener("fetch", (event) => {
    // Only handle GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Only handle navigation requests (HTML pages)
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request)
                .catch(() => {
                    // If request fails, serve offline page
                    console.log('Serving offline page for navigation:', event.request.url);
                    return caches.match(OFFLINE_PAGE)
                        .then(response => {
                            if (response) {
                                return response;
                            }
                            // Fallback if offline page not in cache
                            return new Response(
                                `<!DOCTYPE html>
                                <html><head><title>Offline</title></head>
                                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                                    <h1>No Internet Connection</h1>
                                    <p>Please check your connection and try again.</p>
                                    <button onclick="window.location.reload()">Retry</button>
                                </body></html>`,
                                { headers: { 'Content-Type': 'text/html' } }
                            );
                        });
                })
        );
        return;
    }

    // For other resources, use cache first
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                if (response) {
                    return response;
                }

                // If not in cache, try fetch
                return fetch(event.request)
                    .then((response) => {
                        // If it's a static resource, add it to cache
                        if (response.status === 200 &&
                            (event.request.url.includes('/static/') ||
                                event.request.url.includes('.css') ||
                                event.request.url.includes('.js') ||
                                event.request.url.includes('.png') ||
                                event.request.url.includes('.jpg') ||
                                event.request.url.includes('.svg'))) {

                            const responseToCache = response.clone();
                            caches.open(CACHE_NAME)
                                .then((cache) => {
                                    cache.put(event.request, responseToCache);
                                });
                        }

                        return response;
                    })
                    .catch(() => {
                        // If it's an image and not available, return a placeholder image
                        if (event.request.destination === 'image') {
                            return new Response(
                                '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="#ddd"/><text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#999">No image</text></svg>',
                                { headers: { 'Content-Type': 'image/svg+xml' } }
                            );
                        }

                        // For other resources, simply fail
                        return new Response('Resource not available offline', {
                            status: 404,
                            statusText: 'Not Found'
                        });
                    });
            })
    );
});
