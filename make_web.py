# Web version for iPhone home screen (GitHub Pages): offline single file + manifest + icons + service worker.
import re, sys, os
SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/Manasik-Omra.html'
OUT = os.path.dirname(os.path.abspath(__file__))
VER = sys.argv[2] if len(sys.argv) > 2 else 'v134'
s = open(SRC, encoding='utf-8').read()
head = ('<link rel="manifest" href="manifest.webmanifest">\n'
        '<link rel="apple-touch-icon" sizes="180x180" href="https://zaki-saidi.github.io/manasik-omra-web/kaaba-180.png?v=3">\n'
        '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
        '<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">\n'
        '<meta name="mobile-web-app-capable" content="yes">\n'
        # the page already sets apple-mobile-web-app-capable / title / status-bar black-translucent;
        # black behind the status bar and the home bar: the canvas is night, the body still covers the screen
        '<style>html{background:#0f1013}body{min-height:100vh;min-height:100dvh}</style>\n')
assert s.count('<title>مناسك العمرة</title>') == 1
s = s.replace('<title>مناسك العمرة</title>', '<title>مناسك العمرة</title>\n' + head, 1)
reg = "<script>if('serviceWorker' in navigator&&location.protocol==='https:'){addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){});});}</script>\n"
i = s.rindex('</html>'); s = s[:i] + reg + s[i:]
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(s)
sw = """/* offline cache for the home-screen app; the name changes with each version so the new one replaces the old */
const C = 'manasik-%s';
const FILES = ['./', './index.html', './manifest.webmanifest'];
self.addEventListener('install', e => { e.waitUntil(caches.open(C).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url); if (u.origin !== location.origin) return;
  if (e.request.mode !== 'navigate' && !/\\/(index\\.html|manifest\\.webmanifest)?$/.test(u.pathname)) return;   /* icons: straight from the network */
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(r => r || fetch(e.request).then(res => {
    if (res.ok) { const cp = res.clone(); caches.open(C).then(c => c.put(e.request, cp)); } return res;
  }).catch(() => caches.match('./index.html'))));
});
""" % VER
open(os.path.join(OUT, 'sw.js'), 'w', encoding='utf-8').write(sw)
print('ok', len(s))
