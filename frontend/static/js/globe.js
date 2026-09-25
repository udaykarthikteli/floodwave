/* =========================================================================
   FloodWave — globe.js
   Interactive rotating 3D Earth (Three.js). Drag to rotate, scroll/pinch to
   zoom, click anywhere on the surface to select a location and resolve its
   latitude / longitude (and, via the backend, country / state / city).

   The Earth texture is generated procedurally on a <canvas> so the globe
   works fully offline with zero external image dependencies.
   ========================================================================= */

(function () {
  "use strict";

  const mount = document.getElementById("globe-canvas-wrap");
  if (!mount || typeof THREE === "undefined") return;

  let scene, camera, renderer, globe, cloudsMesh, raycaster, controls;
  let W = mount.clientWidth, H = mount.clientHeight;

  function init() {
    scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera(45, W / H, 0.1, 1000);
    camera.position.z = 3.1;

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(W, H);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    mount.appendChild(renderer.domElement);

    // Lighting
    scene.add(new THREE.AmbientLight(0x88b8d8, 0.9));
    const sun = new THREE.DirectionalLight(0xffffff, 1.1);
    sun.position.set(5, 3, 5);
    scene.add(sun);

    // Earth — try to load a real equirectangular NASA/Natural-Earth style
    // photographic texture first (actual continents, actual coastlines).
    // If it can't be fetched (offline, blocked CDN, etc.) we transparently
    // fall back to the procedural texture so the globe never breaks.
    const geometry = new THREE.SphereGeometry(1, 64, 64);
    const material = new THREE.MeshPhongMaterial({
      map: new THREE.CanvasTexture(buildEarthTexture()), // placeholder until real texture resolves
      shininess: 10,
      specular: new THREE.Color(0x48cae4),
    });
    globe = new THREE.Mesh(geometry, material);
    scene.add(globe);

    loadRealEarthTexture(material);

    // Atmosphere glow (backside shell)
    const atmoGeo = new THREE.SphereGeometry(1.04, 64, 64);
    const atmoMat = new THREE.MeshBasicMaterial({
      color: 0x48cae4, transparent: true, opacity: 0.14, side: THREE.BackSide,
    });
    scene.add(new THREE.Mesh(atmoGeo, atmoMat));

    // Thin wireframe grid overlay for a "data" feel
    const wireGeo = new THREE.SphereGeometry(1.002, 24, 16);
    const wireMat = new THREE.MeshBasicMaterial({ color: 0x48cae4, wireframe: true, transparent: true, opacity: 0.08 });
    scene.add(new THREE.Mesh(wireGeo, wireMat));

    raycaster = new THREE.Raycaster();

    setupControls();
    window.addEventListener("resize", onResize);
    animate();
  }

  // ---- Real earth texture (with graceful procedural fallback) -----------
  const REAL_EARTH_TEXTURE_URLS = [
    "https://unpkg.com/three-globe@2.31.0/example/img/earth-blue-marble.jpg",
    "https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg",
  ];

  function loadRealEarthTexture(material, urlIndex) {
    urlIndex = urlIndex || 0;
    if (urlIndex >= REAL_EARTH_TEXTURE_URLS.length) {
      console.warn("[FloodWave] Could not load a real Earth texture — using procedural globe instead.");
      return; // keep the procedural CanvasTexture already assigned
    }
    const loader = new THREE.TextureLoader();
    loader.setCrossOrigin("anonymous");
    loader.load(
      REAL_EARTH_TEXTURE_URLS[urlIndex],
      (tex) => {
        tex.wrapS = THREE.RepeatWrapping;
        material.map = tex;
        material.needsUpdate = true;
      },
      undefined,
      () => loadRealEarthTexture(material, urlIndex + 1) // try next URL on failure
    );
  }

  // ---- Procedural earth texture (offline fallback) -----------------------
  function buildEarthTexture() {
    const w = 1024, h = 512;
    const canvas = document.createElement("canvas");
    canvas.width = w; canvas.height = h;
    const c = canvas.getContext("2d");

    // ocean base
    const oceanGrad = c.createLinearGradient(0, 0, 0, h);
    oceanGrad.addColorStop(0, "#003b73");
    oceanGrad.addColorStop(0.5, "#005f99");
    oceanGrad.addColorStop(1, "#003b73");
    c.fillStyle = oceanGrad;
    c.fillRect(0, 0, w, h);

    // pseudo-random continents using layered blobs (seeded for stability)
    const rnd = mulberry32(1337);
    c.fillStyle = "#2f8f5b";
    const blobCount = 46;
    for (let i = 0; i < blobCount; i++) {
      const cx = rnd() * w;
      const cy = h * 0.15 + rnd() * h * 0.7;
      const rx = 30 + rnd() * 90;
      const ry = 18 + rnd() * 50;
      drawBlob(c, cx, cy, rx, ry, rnd);
      // wrap around seam
      drawBlob(c, cx - w, cy, rx, ry, rnd);
      drawBlob(c, cx + w, cy, rx, ry, rnd);
    }

    // subtle terrain shading
    c.fillStyle = "rgba(20,70,40,0.35)";
    for (let i = 0; i < 30; i++) {
      const cx = rnd() * w, cy = h * 0.15 + rnd() * h * 0.7;
      drawBlob(c, cx, cy, 12 + rnd() * 30, 8 + rnd() * 18, rnd);
    }

    // polar ice caps
    const iceTop = c.createLinearGradient(0, 0, 0, h * 0.09);
    iceTop.addColorStop(0, "rgba(255,255,255,0.95)");
    iceTop.addColorStop(1, "rgba(255,255,255,0)");
    c.fillStyle = iceTop;
    c.fillRect(0, 0, w, h * 0.09);
    const iceBottom = c.createLinearGradient(0, h, 0, h * 0.91);
    iceBottom.addColorStop(0, "rgba(255,255,255,0.95)");
    iceBottom.addColorStop(1, "rgba(255,255,255,0)");
    c.fillStyle = iceBottom;
    c.fillRect(0, h * 0.91, w, h * 0.09);

    // cloud wisps
    c.fillStyle = "rgba(255,255,255,0.14)";
    for (let i = 0; i < 40; i++) {
      const cx = rnd() * w, cy = rnd() * h;
      drawBlob(c, cx, cy, 20 + rnd() * 50, 6 + rnd() * 14, rnd);
    }

    return canvas;
  }

  function drawBlob(c, cx, cy, rx, ry, rnd) {
    c.beginPath();
    const points = 10;
    for (let i = 0; i <= points; i++) {
      const angle = (i / points) * Math.PI * 2;
      const jitter = 0.7 + rnd() * 0.6;
      const px = cx + Math.cos(angle) * rx * jitter;
      const py = cy + Math.sin(angle) * ry * jitter;
      if (i === 0) c.moveTo(px, py); else c.lineTo(px, py);
    }
    c.closePath();
    c.fill();
  }

  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // ---- Interaction: drag-rotate, zoom, click-to-select -------------------
  let isDragging = false;
  let lastX = 0, lastY = 0;
  let rotationVelocity = { x: 0, y: 0.0015 };
  let dragDistance = 0;

  function setupControls() {
    const dom = renderer.domElement;
    dom.addEventListener("pointerdown", (e) => {
      isDragging = true;
      dragDistance = 0;
      lastX = e.clientX; lastY = e.clientY;
      dom.setPointerCapture(e.pointerId);
    });
    dom.addEventListener("pointermove", (e) => {
      if (!isDragging) return;
      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      dragDistance += Math.abs(dx) + Math.abs(dy);
      rotationVelocity.y = dx * 0.004;
      rotationVelocity.x = dy * 0.004;
      globe.rotation.y += dx * 0.004;
      globe.rotation.x = THREE.MathUtils.clamp(globe.rotation.x + dy * 0.004, -1.2, 1.2);
      lastX = e.clientX; lastY = e.clientY;
    });
    dom.addEventListener("pointerup", (e) => {
      isDragging = false;
      if (dragDistance < 6) handleClick(e);
    });
    dom.addEventListener("wheel", (e) => {
      e.preventDefault();
      camera.position.z = THREE.MathUtils.clamp(camera.position.z + e.deltaY * 0.0015, 1.6, 5.5);
    }, { passive: false });
  }

  function handleClick(e) {
    const rect = renderer.domElement.getBoundingClientRect();
    const mouse = new THREE.Vector2(
      ((e.clientX - rect.left) / rect.width) * 2 - 1,
      -((e.clientY - rect.top) / rect.height) * 2 + 1
    );
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObject(globe);
    if (intersects.length === 0) return;

    const point = intersects[0].point.clone();
    globe.worldToLocal(point);

    const lat = 90 - (Math.acos(point.y / point.length())) * (180 / Math.PI);
    // Longitude: matches the equirectangular UV mapping Three.js's SphereGeometry
    // uses internally (u=0.5 -> +x axis -> lon 0), verified against reference
    // points at each quarter-turn of the equator. The previous formula had a
    // sign error plus a stray "-90" offset, which put reported coordinates a
    // consistent 90 degrees east of wherever you actually clicked.
    let lon = -Math.atan2(point.z, point.x) * (180 / Math.PI);
    if (lon < -180) lon += 360;
    if (lon > 180) lon -= 360;

    if (typeof window.onGlobeLocationSelected === "function") {
      window.onGlobeLocationSelected(lat, lon);
    }
    spawnMarker(point);
  }

  let marker;
  function spawnMarker(localPoint) {
    if (marker) globe.remove(marker);
    const geo = new THREE.SphereGeometry(0.018, 16, 16);
    const mat = new THREE.MeshBasicMaterial({ color: 0xff5555 });
    marker = new THREE.Mesh(geo, mat);
    marker.position.copy(localPoint).setLength(1.01);
    globe.add(marker);
  }

  function onResize() {
    W = mount.clientWidth; H = mount.clientHeight;
    if (!W || !H) return;
    camera.aspect = W / H;
    camera.updateProjectionMatrix();
    renderer.setSize(W, H);
  }

  function animate() {
    requestAnimationFrame(animate);
    if (!isDragging) {
      globe.rotation.y += 0.0018; // gentle idle spin
    }
    renderer.render(scene, camera);
  }

  init();
})();
