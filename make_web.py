# Web version for iPhone home screen (GitHub Pages): offline single file, built-in icon, service worker; no manifest (iOS shows a letter instead of the icon when one is present).
import re, sys, os
SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/Manasik-Omra.html'
OUT = os.path.dirname(os.path.abspath(__file__))
VER = sys.argv[2] if len(sys.argv) > 2 else 'v134'
s = open(SRC, encoding='utf-8').read()
# the adhan recordings (9 MB of the 14) become separate files, loaded only when one is played
import base64
os.makedirs(os.path.join(OUT, 'snd'), exist_ok=True)
def _snd(m):
    open(os.path.join(OUT, 'snd', m.group(1) + '.mp3'), 'wb').write(base64.b64decode(m.group(2)))
    return m.group(1) + ":'/manasik-omra-web/snd/" + m.group(1) + ".mp3'"
i = s.index('var ADHAN_SND={'); j = s.index('};', i)
blk, nsub = re.subn(r"([a-z0-9]+):'data:audio/mpeg;base64,([A-Za-z0-9+/=]+)'", _snd, s[i:j])
assert nsub >= 9, nsub
s = s[:i] + blk + s[j:]
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
sw = """/* offline copy of the home-screen app: the page opens at once from the saved copy and is refreshed
   in the background, so a new version shows at the next launch; without a saved copy it comes from the network. */
const C = 'manasik-%s';
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
""" % VER
for d in ('', 'a'):
    open(os.path.join(OUT, d, 'sw.js'), 'w', encoding='utf-8').write(sw)
print('ok', len(s))
