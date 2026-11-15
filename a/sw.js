/* offline copy of the home-screen app: the page opens at once from the saved copy and is refreshed
   in the background, so a new version shows at the next launch; without a saved copy it comes from the network. */
const C = 'manasik-v141b';
const B = new URL('./', location).pathname;   /* folder of this worker: /manasik-omra-web/ or /manasik-omra-web/a/ */
self.addEventListener('install', e => { e.waitUntil(caches.open(C).then(c => c.add('./index.html')).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C && k !== C + '-snd').map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url); if (u.origin !== location.origin) return;
  if (u.pathname.includes('/snd/')) {   /* adhan recordings: kept once played */
    e.respondWith(caches.open(C + '-snd').then(c => c.match(e.request).then(hit => hit || fetch(e.request).then(res => { if (res.ok && res.status === 200) c.put(e.request, res.clone()); return res; }))));
    return;
  }
  /* only the app page itself: other pages of the site (privacy policy) load normally */
  if (e.request.mode !== 'navigate' || !(u.pathname === B || u.pathname === B + 'index.html')) return;
  e.respondWith(caches.open(C).then(c => c.match('./index.html').then(hit => {
    const upd = fetch(e.request).then(res => { if (res.ok && !res.redirected) c.put('./index.html', res.clone()); return res; });
    if (hit) { e.waitUntil(upd.catch(() => {})); return hit; }
    return upd;
  })));
});
