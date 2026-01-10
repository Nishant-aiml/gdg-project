// Minimal service worker - doesn't cache aggressively during development
const CACHE_NAME = 'smart-approval-v2';

self.addEventListener('install', (event) => {
  // Skip waiting to immediately activate
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  // Clear old caches
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = event.request.url;

  // Skip service worker for external APIs to prevent auth errors
  const skipUrls = [
    'googleapis.com',
    'firebase',
    'identitytoolkit',
    'securetoken',
    'accounts.google.com',
    'localhost:8000',
    '127.0.0.1:8000'
  ];

  if (skipUrls.some(skip => url.includes(skip))) {
    // Let these requests pass through without service worker interference
    return;
  }

  // Network-first strategy for everything else
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Return the network response
        return response;
      })
      .catch(async () => {
        // Only fall back to cache if network fails
        const cachedResponse = await caches.match(event.request);
        if (cachedResponse) {
          return cachedResponse;
        }
        // Return a proper error response if nothing is cached
        return new Response('Network error', {
          status: 503,
          statusText: 'Service Unavailable',
          headers: new Headers({ 'Content-Type': 'text/plain' })
        });
      })
  );
});
