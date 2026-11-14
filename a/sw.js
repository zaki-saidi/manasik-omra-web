/* offline copy of the home-screen app. Pages: network first (a new version shows at once),
   the saved copy when there is no network or it takes more than 4 s. */
const C = 'manasik-v136';
const FILES = ['./', './index.html'];
self.addEventListener('install', e => { e.waitUntil(caches.open(C).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url); if (u.origin !== location.origin) return;
  if (e.request.mode !== 'navigate' && !/\/(index\.html)?$/.test(u.pathname)) return;
  const saved = () => caches.match(e.request, { ignoreSearch: true }).then(r => r || caches.match('./index.html'));
  const net = fetch(e.request).then(res => { if (res.ok) { const cp = res.clone(); caches.open(C).then(c => c.put('./index.html', cp)); } return res; });
  const slow = new Promise(ok => setTimeout(ok, 4000)).then(saved).then(r => r || net);
  e.respondWith(Promise.race([net.catch(saved), slow]).then(r => r || saved()));
});
