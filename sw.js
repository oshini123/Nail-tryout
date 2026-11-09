// Offline cache for the app shell and the hand-tracking model.
const CACHE = 'lacquer-v1';
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
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
    if (res.ok && new URL(e.request.url).origin === location.origin) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
    return res;
  }).catch(() => hit)));
});
