"""Builds dist/ (installable PWA) and artifact/ (Claude preview) from src/app.html."""
import pathlib, shutil, json, sys
from PIL import Image, ImageDraw

root = pathlib.Path(__file__).resolve().parent.parent
mp_src = pathlib.Path(sys.argv[1])
body = (root / "src/app.html").read_text()
MP_FILES = ["hands.js", "hands.binarypb", "hand_landmark_full.tflite", "hands_solution_packed_assets.data",
            "hands_solution_packed_assets_loader.js", "hands_solution_simd_wasm_bin.js", "hands_solution_simd_wasm_bin.wasm",
            "hands_solution_simd_wasm_bin.data", "hands_solution_wasm_bin.js", "hands_solution_wasm_bin.wasm"]

def copy_mp(dest):
    (dest / "mediapipe").mkdir(parents=True, exist_ok=True)
    for f in MP_FILES:
        shutil.copy(mp_src / f, dest / "mediapipe" / f)
    shutil.copy(mp_src / "README.md", dest / "mediapipe" / "LICENSE-NOTE.md")

def icon(size, path, maskable=False):
    im = Image.new("RGB", (size, size), (23, 17, 26))
    d = ImageDraw.Draw(im)
    s = size / 512
    pad = 0 if not maskable else 40 * s
    # almond nail
    cx, top, bot, hw = 256 * s, (96 * s + pad), (430 * s - pad), (118 * s - pad * 0.5)
    d.rounded_rectangle([cx - hw, top + 90 * s, cx + hw, bot], radius=hw, fill=(91, 31, 58))
    d.ellipse([cx - hw, top, cx + hw, top + 260 * s], fill=(91, 31, 58))
    d.ellipse([cx - hw * 0.62, top + 70 * s, cx - hw * 0.22, top + 230 * s], fill=(176, 110, 138))
    im.save(path)

# --- PWA ---
dist = root / "dist"
if dist.exists(): shutil.rmtree(dist)
dist.mkdir()
copy_mp(dist)
(dist / "icons").mkdir()
icon(192, dist / "icons/icon-192.png"); icon(512, dist / "icons/icon-512.png"); icon(512, dist / "icons/maskable-512.png", True)
icon(180, dist / "icons/apple-touch-icon.png")
head = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#17111a">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<style>*{box-sizing:border-box}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>
</head>
<body>
"""
tail = """
<script>
if ('serviceWorker' in navigator && location.protocol === 'https:') {
  window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
</script>
</body>
</html>
"""
# The PWA pads safe areas inside its own components; drop the :root padding to keep the camera full-bleed.
(dist / "index.html").write_text(head.replace(":root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}", "") + body + tail)
(dist / "manifest.webmanifest").write_text(json.dumps({
    "name": "Lacquer Nail Try-On", "short_name": "Lacquer", "start_url": "./", "scope": "./",
    "display": "standalone", "orientation": "portrait", "background_color": "#0e0a0f", "theme_color": "#17111a",
    "description": "Try nail polish shades, finishes and shapes on your own hand in AR.",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ]}, indent=2))
assets = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png"] + ["mediapipe/" + f for f in MP_FILES]
(dist / "sw.js").write_text("""// Offline cache for the app shell and the hand-tracking model.
const CACHE = 'lacquer-v1';
const ASSETS = %s;
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
    if (res.ok && new URL(e.request.url).origin === location.origin) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
    return res;
  }).catch(() => hit)));
});
""" % json.dumps(assets, indent=2))

# --- Artifact preview ---
art = root / "artifact"
if art.exists(): shutil.rmtree(art)
art.mkdir()
(art / "index.html").write_text(body.replace("<script>\n(() => {", "<script>window.LACQUER_PREVIEW = true;</script>\n<script>\n(() => {", 1))
print("built", dist, art)
