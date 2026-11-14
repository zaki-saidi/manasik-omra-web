# Web version for iPhone home screen (GitHub Pages): offline single file, built-in icon, service worker; no manifest (iOS shows a letter instead of the icon when one is present).
import re, sys, os
SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/Manasik-Omra.html'
OUT = os.path.dirname(os.path.abspath(__file__))
VER = sys.argv[2] if len(sys.argv) > 2 else 'v134'
s = open(SRC, encoding='utf-8').read()
head = (  # no web manifest: with one, iOS ignores apple-touch-icon and shows a letter instead of the logo
        '<link rel="apple-touch-icon" sizes="180x180" href="data:image/png;base64,' + __import__('base64').b64encode(open(os.path.join(OUT, 'apple-touch-icon.png'), 'rb').read()).decode() + '">\n'
        '<link rel="icon" type="image/png" sizes="192x192" href="/manasik-omra-web/icon-192.png">\n'
        '<meta name="mobile-web-app-capable" content="yes">\n'
        # the page already sets apple-mobile-web-app-capable / title / status-bar black-translucent;
        # black behind the status bar and the home bar: the canvas is night, the body still covers the screen
        '<style>html{background:#0f1013}body{min-height:100vh;min-height:100dvh}</style>\n')
assert s.count('<title>مناسك العمرة</title>') == 1
s = s.replace('<title>مناسك العمرة</title>', '<title>مناسك العمرة</title>\n' + head, 1)
reg = "<script>if('serviceWorker' in navigator&&location.protocol==='https:'){addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){});});}</script>\n"
i = s.rindex('</html>'); s = s[:i] + reg + s[i:]
for d in ('', 'a'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)
    open(os.path.join(OUT, d, 'index.html'), 'w', encoding='utf-8').write(s)
sw = """/* offline copy of the home-screen app. Pages: network first (a new version shows at once),
   the saved copy when there is no network or it takes more than 4 s. */
const C = 'manasik-%s';
const FILES = ['./', './index.html'];
self.addEventListener('install', e => { e.waitUntil(caches.open(C).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url); if (u.origin !== location.origin) return;
  if (e.request.mode !== 'navigate' && !/\\/(index\\.html)?$/.test(u.pathname)) return;
  const saved = () => caches.match(e.request, { ignoreSearch: true }).then(r => r || caches.match('./index.html'));
  const net = fetch(e.request).then(res => { if (res.ok) { const cp = res.clone(); caches.open(C).then(c => c.put('./index.html', cp)); } return res; });
  const slow = new Promise(ok => setTimeout(ok, 4000)).then(saved).then(r => r || net);
  e.respondWith(Promise.race([net.catch(saved), slow]).then(r => r || saved()));
});
""" % VER
for d in ('', 'a'):
    open(os.path.join(OUT, d, 'sw.js'), 'w', encoding='utf-8').write(sw)
print('ok', len(s))
