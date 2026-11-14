/* offline copy of the home-screen app: the page opens at once from the saved copy and is refreshed
   in the background, so a new version shows at the next launch; without a saved copy it comes from the network. */
const C = 'manasik-v137';
self.addEventListener('install', e => { e.waitUntil(caches.open(C).then(c => c.add('./index.html')).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || e.request.mode !== 'navigate') return;
  if (new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(caches.open(C).then(c => c.match('./index.html').then(hit => {
    const upd = fetch(e.request).then(res => { if (res.ok && !res.redirected) c.put('./index.html', res.clone()); return res; });
    if (hit) { e.waitUntil(upd.catch(() => {})); return hit; }
    return upd;
  })));
});
