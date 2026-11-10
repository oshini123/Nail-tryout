// Offline cache. Pages load network-first so a new deploy shows up on the next open.
const CACHE = 'lacquer-v3';
const ASSETS = [
  "./",
  "index.html",
  "manifest.webmanifest",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "mediapipe/hands.js",
  "mediapipe/hands.binarypb",
  "mediapipe/hand_landmark_full.tflite",
  "mediapipe/hands_solution_packed_assets.data",
  "mediapipe/hands_solution_packed_assets_loader.js",
  "mediapipe/hands_solution_simd_wasm_bin.js",
  "mediapipe/hands_solution_simd_wasm_bin.wasm",
  "mediapipe/hands_solution_simd_wasm_bin.data",
  "mediapipe/hands_solution_wasm_bin.js",
  "mediapipe/hands_solution_wasm_bin.wasm"
];
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(res => { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return res; })
      .catch(() => caches.match(req).then(hit => hit || caches.match('index.html'))));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return res;
  })));
});
