/* offline cache for the home-screen app; the name changes with each version so the new one replaces the old */
const C = 'manasik-v134d';
const FILES = ['./', './index.html', './manifest.webmanifest'];
self.addEventListener('install', e => { e.waitUntil(caches.open(C).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url); if (u.origin !== location.origin) return;
  if (e.request.mode !== 'navigate' && !/\/(index\.html|manifest\.webmanifest)?$/.test(u.pathname)) return;   /* icons: straight from the network */
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(r => r || fetch(e.request).then(res => {
    if (res.ok) { const cp = res.clone(); caches.open(C).then(c => c.put(e.request, cp)); } return res;
  }).catch(() => caches.match('./index.html'))));
});
