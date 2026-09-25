/* =========================================================================
   FloodWave — main.js
   Shared behaviors: navbar scroll state, mobile menu, flood-ripple button
   interaction, toast notifications, scroll-reveal, floating particles.
   ========================================================================= */

(function () {
  "use strict";

  // ---- Navbar scroll state -------------------------------------------
  const navbar = document.getElementById("navbar");
  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("navLinks");

  function onScroll() {
    if (!navbar) return;
    if (window.scrollY > 40) navbar.classList.add("scrolled");
    else navbar.classList.remove("scrolled");
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => navLinks.classList.toggle("open"));
    navLinks.querySelectorAll("a").forEach(a =>
      a.addEventListener("click", () => navLinks.classList.remove("open"))
    );
  }

  // ---- Flood ripple button interaction ---------------------------------
  // Any element with class "btn" gets a rising-water fill overlay when
  // clicked, lasting ~1s, per the FloodWave interaction spec.
  function attachFloodEffect(btn) {
    if (btn.querySelector(".flood-fill")) {
      // already has the fill element (server-rendered)
    } else {
      const fill = document.createElement("span");
      fill.className = "flood-fill";
      btn.prepend(fill);
      if (!btn.querySelector(".btn-label")) {
        const label = document.createElement("span");
        label.className = "btn-label";
        while (btn.childNodes.length > 1) {
          label.appendChild(btn.childNodes[1]);
        }
        btn.appendChild(label);
      }
    }

    btn.addEventListener("click", function (e) {
      btn.classList.add("flood-active");
      window.setTimeout(() => btn.classList.remove("flood-active"), 950);
    });
  }
  document.querySelectorAll(".btn").forEach(attachFloodEffect);

  // ---- Toast ------------------------------------------------------------
  window.FloodWaveToast = function (message, duration) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("show");
    window.clearTimeout(toast._timer);
    toast._timer = window.setTimeout(() => toast.classList.remove("show"), duration || 3200);
  };

  // ---- Scroll reveal ------------------------------------------------------
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealEls.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    revealEls.forEach(el => io.observe(el));
  } else {
    revealEls.forEach(el => el.classList.add("in-view"));
  }

  // ---- Floating water particles (subtle ambient decoration) -------------
  window.FloodWaveParticles = function (container, count) {
    if (!container) return;
    const n = count || 18;
    for (let i = 0; i < n; i++) {
      const p = document.createElement("div");
      p.className = "particle";
      const size = 2 + Math.random() * 4;
      p.style.width = size + "px";
      p.style.height = size + "px";
      p.style.left = Math.random() * 100 + "%";
      p.style.top = Math.random() * 100 + "%";
      p.style.opacity = (0.15 + Math.random() * 0.35).toFixed(2);
      const duration = 6 + Math.random() * 10;
      p.style.animation = `floaty ${duration}s ease-in-out infinite`;
      p.style.animationDelay = (-Math.random() * duration) + "s";
      container.appendChild(p);
    }
  };

  // Auto-hide flash-style alerts after a few seconds
  document.querySelectorAll("[data-autohide]").forEach(el => {
    window.setTimeout(() => { el.style.display = "none"; }, 5000);
  });
})();
