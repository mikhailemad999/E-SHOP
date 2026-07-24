/*
 * E-Shop PWA Service Worker — Safe SPA & Asset fetch handling
 */

const CACHE_NAME = 'eshop-v2';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.svg',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS)).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) return caches.delete(key);
        })
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Skip chrome-extension and dev server HMR requests
  if (url.protocol.startsWith('chrome-extension') || url.pathname.includes('/@vite/')) {
    return;
  }

  // API calls: Network-first
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() =>
        caches.match(event.request).then((res) => res || new Response(JSON.stringify({ error: 'Offline' }), { headers: { 'Content-Type': 'application/json' } }))
      )
    );
    return;
  }

  // SPA navigation: Always serve index.html or fetch
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() =>
        caches.match('/index.html').then((res) => res || new Response('Offline Page', { headers: { 'Content-Type': 'text/html' } }))
      )
    );
    return;
  }

  // Static assets: Network first falling back to cache
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response && response.status === 200 && response.type === 'basic') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone)).catch(() => {});
        }
        return response;
      })
      .catch(() => caches.match(event.request).then((res) => res || new Response('', { status: 404 })))
  );
});
