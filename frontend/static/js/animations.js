/* =========================================================================
   FloodWave — animations.js
   Cinematic landing-page hero: an ocean wave rolling toward a city skyline,
   striking one tall tower, which collapses into debris and then rebuilds
   itself with a soft futuristic glow — looping seamlessly. Built on Canvas2D
   so it needs no external assets and stays lightweight.
   ========================================================================= */

(function () {
  "use strict";

  const wrap = document.getElementById("hero-canvas-wrap");
  if (!wrap) return;

  const canvas = document.createElement("canvas");
  wrap.appendChild(canvas);
  const ctx = canvas.getContext("2d");

  let W, H, DPR;
  function resize() {
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = wrap.clientWidth;
    H = wrap.clientHeight;
    canvas.width = W * DPR;
    canvas.height = H * DPR;
    canvas.style.width = W + "px";
    canvas.style.height = H + "px";
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    buildCity();
  }

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---- City skyline model -------------------------------------------------
  let buildings = [];
  let targetIndex = 0;

  function buildCity() {
    buildings = [];
    const count = Math.max(9, Math.floor(W / 90));
    const baseline = H * 0.72;
    let x = -20;
    const seedRnd = mulberry32(42);
    for (let i = 0; i < count; i++) {
      const w = 46 + seedRnd() * 40;
      const h = 60 + seedRnd() * (H * 0.34);
      buildings.push({
        x, w, h, baseline,
        windows: Math.floor(h / 22),
        seed: seedRnd(),
      });
      x += w + 10 + seedRnd() * 10;
    }
    // pick the tallest-ish central building as the "target" tower
    let maxH = -1;
    buildings.forEach((b, i) => {
      const centerBias = 1 - Math.abs((b.x - W / 2) / W);
      const score = b.h * (0.6 + 0.4 * centerBias);
      if (score > maxH) { maxH = score; targetIndex = i; }
    });
  }

  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // ---- Clouds ---------------------------------------------------------
  const clouds = Array.from({ length: 5 }, (_, i) => ({
    y: 30 + i * 26 + Math.random() * 20,
    speed: 6 + Math.random() * 8,
    scale: 0.6 + Math.random() * 0.9,
    seed: Math.random() * 1000,
  }));

  // ---- Debris particles for collapse/rebuild -----------------------------
  let debris = [];

  function spawnDebris(building, phase) {
    const n = 26;
    const arr = [];
    for (let i = 0; i < n; i++) {
      arr.push({
        x: building.x + Math.random() * building.w,
        y: building.baseline - Math.random() * building.h,
        vx: (Math.random() - 0.5) * 30,
        vy: phase === "collapse" ? Math.random() * 20 : -(40 + Math.random() * 60),
        size: 3 + Math.random() * 6,
        life: 1,
        phase,
      });
    }
    return arr;
  }

  // ---- Cycle timing (seconds) -------------------------------------------
  const T_APPROACH = 4.2;
  const T_IMPACT = 1.0;
  const T_COLLAPSE = 2.2;
  const T_PAUSE = 1.0;
  const T_REBUILD = 2.6;
  const T_HOLD = 2.0;
  const CYCLE = T_APPROACH + T_IMPACT + T_COLLAPSE + T_PAUSE + T_REBUILD + T_HOLD;

  let tStart = performance.now();
  let lastDebrisSpawn = -1;

  function phaseAt(t) {
    let acc = 0;
    if (t < (acc += T_APPROACH)) return { name: "approach", p: t / T_APPROACH };
    if (t < (acc += T_IMPACT)) return { name: "impact", p: (t - (acc - T_IMPACT)) / T_IMPACT };
    if (t < (acc += T_COLLAPSE)) return { name: "collapse", p: (t - (acc - T_COLLAPSE)) / T_COLLAPSE };
    if (t < (acc += T_PAUSE)) return { name: "pause", p: (t - (acc - T_PAUSE)) / T_PAUSE };
    if (t < (acc += T_REBUILD)) return { name: "rebuild", p: (t - (acc - T_REBUILD)) / T_REBUILD };
    return { name: "hold", p: (t - (acc)) / T_HOLD };
  }

  function easeInOut(x) { return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; }
  function easeOutBack(x) {
    const c1 = 1.4, c3 = c1 + 1;
    return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
  }

  function draw(now) {
    const t = ((now - tStart) / 1000) % CYCLE;
    const ph = phaseAt(t);

    ctx.clearRect(0, 0, W, H);

    // ---- sky gradient handled by CSS background; canvas stays transparent

    // ---- clouds ----
    ctx.save();
    clouds.forEach(c => {
      const cx = ((now / 1000 * c.speed) + c.seed) % (W + 300) - 150;
      drawCloud(cx, c.y, c.scale);
    });
    ctx.restore();

    const waterline = H * 0.74;

    // ---- reflections (mirrored skyline, faint) ----
    ctx.save();
    ctx.globalAlpha = 0.14;
    ctx.translate(0, waterline * 2);
    ctx.scale(1, -1);
    drawSkyline(ph, t, true);
    ctx.restore();

    // ---- skyline ----
    drawSkyline(ph, t, false);

    // ---- ocean wave ----
    drawWave(now / 1000, ph, waterline);

    // ---- debris ----
    updateAndDrawDebris(ph, t);

    if (!reducedMotion) requestAnimationFrame(draw);
  }

  function drawCloud(cx, cy, scale) {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(scale, scale);
    ctx.fillStyle = "rgba(255,255,255,0.18)";
    ctx.beginPath();
    ctx.ellipse(0, 0, 46, 16, 0, 0, Math.PI * 2);
    ctx.ellipse(28, -6, 30, 14, 0, 0, Math.PI * 2);
    ctx.ellipse(-26, -4, 28, 13, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  function drawSkyline(ph, t, isReflection) {
    buildings.forEach((b, i) => {
      let h = b.h;
      let collapseOffset = 0;
      let opacity = 1;

      if (i === targetIndex) {
        if (ph.name === "collapse") {
          const p = easeInOut(ph.p);
          h = b.h * (1 - p * 0.92);
          collapseOffset = p * 6;
        } else if (ph.name === "pause") {
          h = b.h * 0.08;
        } else if (ph.name === "rebuild") {
          const p = easeOutBack(Math.min(ph.p, 1));
          h = b.h * Math.max(0.08, Math.min(p, 1));
        }
      }

      const x = b.x, w = b.w, baseline = b.baseline;
      ctx.save();
      const grad = ctx.createLinearGradient(0, baseline - h, 0, baseline);
      grad.addColorStop(0, "#0a4d82");
      grad.addColorStop(1, "#022544");
      ctx.fillStyle = isReflection ? "rgba(10,77,130,0.7)" : grad;
      ctx.fillRect(x, baseline - h + collapseOffset, w, h);

      // windows
      if (!isReflection) {
        ctx.fillStyle = "rgba(72,202,228,0.55)";
        const rows = Math.max(1, Math.floor(h / 22));
        const cols = Math.max(1, Math.floor(w / 16));
        for (let r = 0; r < rows; r++) {
          for (let c = 0; c < cols; c++) {
            if ((r + c + Math.floor(b.seed * 10)) % 3 === 0) continue;
            const wx = x + 6 + c * 15;
            const wy = baseline - h + collapseOffset + 10 + r * 20;
            if (wy < baseline - 4) ctx.fillRect(wx, wy, 5, 8);
          }
        }
      }
      ctx.restore();
    });

    // rebuild glow effect on target building
    if (!isReflection && ph.name === "rebuild") {
      const b = buildings[targetIndex];
      if (b) {
        const p = ph.p;
        ctx.save();
        ctx.globalAlpha = 0.5 * (1 - p);
        const glowH = b.h * Math.min(p * 1.3, 1);
        const grad = ctx.createLinearGradient(0, b.baseline - glowH, 0, b.baseline);
        grad.addColorStop(0, "rgba(72,202,228,0.9)");
        grad.addColorStop(1, "rgba(72,202,228,0)");
        ctx.fillStyle = grad;
        ctx.fillRect(b.x - 4, b.baseline - glowH, b.w + 8, glowH);
        ctx.restore();
      }
    }
  }

  function drawWave(tSec, ph, waterline) {
    // wave surge amount: rises during approach + impact, recedes after
    let surge = 0;
    if (ph.name === "approach") surge = easeInOut(ph.p) * 0.7;
    else if (ph.name === "impact") surge = 0.7 + easeInOut(ph.p) * 0.3;
    else if (ph.name === "collapse") surge = 1 - ph.p * 0.5;
    else if (ph.name === "pause") surge = 0.5 - ph.p * 0.3;
    else surge = 0.15;

    const waveTop = waterline - surge * (H * 0.16);

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(0, H);
    ctx.lineTo(0, waveTop);
    const amp = 6 + surge * 10;
    for (let x = 0; x <= W; x += 8) {
      const y = waveTop + Math.sin((x * 0.02) + tSec * 2.4) * amp
                + Math.sin((x * 0.008) - tSec * 1.1) * (amp * 0.6);
      ctx.lineTo(x, y);
    }
    ctx.lineTo(W, H);
    ctx.closePath();
    const g = ctx.createLinearGradient(0, waveTop - 20, 0, H);
    g.addColorStop(0, "rgba(72,202,228,0.85)");
    g.addColorStop(0.4, "rgba(0,180,216,0.85)");
    g.addColorStop(1, "rgba(0,59,115,0.95)");
    ctx.fillStyle = g;
    ctx.fill();

    // foam line
    ctx.beginPath();
    for (let x = 0; x <= W; x += 8) {
      const y = waveTop + Math.sin((x * 0.02) + tSec * 2.4) * amp
                + Math.sin((x * 0.008) - tSec * 1.1) * (amp * 0.6);
      if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = "rgba(255,255,255,0.55)";
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();
  }

  function updateAndDrawDebris(ph, t) {
    const b = buildings[targetIndex];
    if (!b) return;

    if (ph.name === "collapse" && lastDebrisSpawn !== "collapse-" + Math.floor(t * 3)) {
      if (Math.random() < 0.6) debris.push(...spawnDebris(b, "collapse").slice(0, 4));
      lastDebrisSpawn = "collapse-" + Math.floor(t * 3);
    }
    if (ph.name === "rebuild" && lastDebrisSpawn !== "rebuild-" + Math.floor(t * 3)) {
      if (Math.random() < 0.6) debris.push(...spawnDebris(b, "rebuild").slice(0, 4));
      lastDebrisSpawn = "rebuild-" + Math.floor(t * 3);
    }

    ctx.save();
    debris = debris.filter(d => d.life > 0);
    debris.forEach(d => {
      d.x += d.vx * 0.016;
      d.y += d.vy * 0.016;
      d.vy += (d.phase === "collapse" ? 60 : -20) * 0.016;
      d.life -= 0.012;
      ctx.globalAlpha = Math.max(d.life, 0);
      ctx.fillStyle = d.phase === "collapse" ? "#7fb8d9" : "#48CAE4";
      ctx.beginPath();
      ctx.arc(d.x, d.y, d.size, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.restore();
  }

  window.addEventListener("resize", resize);
  resize();

  if (reducedMotion) {
    draw(performance.now());
  } else {
    requestAnimationFrame(draw);
  }

  // Ambient floating particles overlay (DOM-based, decorative)
  if (window.FloodWaveParticles) {
    window.FloodWaveParticles(wrap, 14);
  }
})();
