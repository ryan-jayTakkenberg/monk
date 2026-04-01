/// <reference lib="WebWorker" />
import { cleanupOutdatedCaches, precacheAndRoute } from 'workbox-precaching'

declare let self: ServiceWorkerGlobalScope

// Injected by vite-plugin-pwa at build time
precacheAndRoute(self.__WB_MANIFEST)
cleanupOutdatedCaches()

// Network-first strategy for API calls
self.addEventListener('fetch', (event: FetchEvent) => {
  const { request } = event
  const url = new URL(request.url)

  // Let the browser handle non-GET requests and cross-origin requests normally
  if (request.method !== 'GET' || url.origin !== self.location.origin) {
    return
  }

  // Network-first for API routes
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/media/')) {
    event.respondWith(
      fetch(request).catch(() => {
        // API calls that fail offline return a 503 JSON response
        return new Response(
          JSON.stringify({ detail: 'You are offline.' }),
          { status: 503, headers: { 'Content-Type': 'application/json' } }
        )
      })
    )
    return
  }

  // Cache-first for precached assets, network-first with offline fallback for navigation
  event.respondWith(
    fetch(request)
      .then((response) => {
        // Clone and cache successful navigation responses
        if (request.mode === 'navigate' && response.ok) {
          const clone = response.clone()
          caches.open('monk-runtime-v1').then((cache) => cache.put(request, clone))
        }
        return response
      })
      .catch(async () => {
        // Try the cache first
        const cached = await caches.match(request)
        if (cached) return cached

        // For navigation requests, serve the offline fallback page
        if (request.mode === 'navigate') {
          const offlineFallback = await caches.match('/offline.html')
          if (offlineFallback) return offlineFallback
        }

        return new Response('Offline', { status: 503 })
      })
  )
})
