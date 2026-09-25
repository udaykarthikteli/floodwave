/* =========================================================================
   FloodWave — prediction.js
   Wires the 3D globe, environmental input form, and the /api/predict +
   /api/weather + /api/reverse-geocode endpoints together.
   ========================================================================= */

(function () {
  "use strict";

  const els = {
    lat: document.getElementById("f-lat"),
    lon: document.getElementById("f-lon"),
    country: document.getElementById("f-country"),
    state: document.getElementById("f-state"),
    city: document.getElementById("f-city"),
    chip: document.getElementById("locationChip"),
    form: document.getElementById("predictForm"),
    submitBtn: document.getElementById("predictBtn"),
    resultPanel: document.getElementById("result-panel"),
    loadingOverlay: document.getElementById("formLoading"),
  };

  // ---- Globe selection callback -----------------------------------------
  window.onGlobeLocationSelected = async function (lat, lon) {
    if (els.lat) els.lat.value = lat.toFixed(4);
    if (els.lon) els.lon.value = lon.toFixed(4);
    if (els.chip) {
      els.chip.innerHTML = `<span>Lat ${lat.toFixed(2)}</span><span>Lon ${lon.toFixed(2)}</span><span>Resolving location…</span>`;
    }

    fetchWeather(lat, lon);

    try {
      const data = await reverseGeocode(lat, lon);
      if (els.country) els.country.value = data.country || "";
      if (els.state) els.state.value = data.state || "";
      if (els.city) els.city.value = data.city || "";

      const label = [data.city, data.state, data.country].filter(Boolean).join(", ");
      if (els.chip) {
        els.chip.innerHTML = `<span>Lat ${lat.toFixed(2)}</span><span>Lon ${lon.toFixed(2)}</span><span>${label || "Ocean / unresolved — enter manually"}</span>`;
      }
      if (!label && window.FloodWaveToast) {
        window.FloodWaveToast("No address found for this point (likely open ocean) — you can type it in manually.");
      }
    } catch (err) {
      console.error("[FloodWave] reverse-geocode request failed:", err);
      if (els.chip) {
        els.chip.innerHTML = `<span>Lat ${lat.toFixed(2)}</span><span>Lon ${lon.toFixed(2)}</span><span>Couldn't reach geocoding service — enter manually</span>`;
      }
      window.FloodWaveToast && window.FloodWaveToast("Location lookup failed — check your internet connection, then enter city/country manually.");
    }
  };

  // ---- Reverse geocoding ---------------------------------------------------
  // Called directly from the browser (not the Flask backend) because free
  // reverse-geocoding providers like this one require client-side requests —
  // server-side calls from a datacenter IP (e.g. a Render deployment) get
  // rate-limited or blocked, which is why country/state/city could end up
  // blank in production even though they worked locally.
  async function reverseGeocode(lat, lon) {
    try {
      const res = await fetch(
        `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`
      );
      if (!res.ok) throw new Error(`BigDataCloud responded ${res.status}`);
      const d = await res.json();
      return {
        country: d.countryName || "",
        state: d.principalSubdivision || "",
        city: d.city || d.locality || "",
      };
    } catch (err) {
      console.warn("[FloodWave] client-side geocode failed, falling back to server route:", err);
      const res = await fetch(`/api/reverse-geocode?lat=${lat}&lon=${lon}`);
      return await res.json();
    }
  }

  async function fetchWeather(lat, lon) {
    try {
      const res = await fetch(`/api/weather?lat=${lat}&lon=${lon}`);
      const data = await res.json();
      setIfEmpty("f-rainfall", data.rainfall_mm);
      setIfEmpty("f-temperature", data.temperature_c);
      setIfEmpty("f-humidity", data.humidity_pct);
      setIfEmpty("f-wind", data.wind_speed_kmh);
      if (window.FloodWaveToast) {
        window.FloodWaveToast(`Environmental data auto-filled (${data.source})`);
      }
    } catch (err) {
      console.error("[FloodWave] weather request failed:", err);
      window.FloodWaveToast && window.FloodWaveToast("Couldn't fetch weather data — you can enter values manually.");
    }
  }

  function setIfEmpty(id, value) {
    const el = document.getElementById(id);
    if (el && value !== undefined && value !== null) el.value = value;
  }

  // ---- Prediction submit --------------------------------------------------
  if (els.form) {
    els.form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const payload = {
        latitude: parseFloat(els.lat.value) || null,
        longitude: parseFloat(els.lon.value) || null,
        city: els.city.value,
        country: els.country.value,
        rainfall_mm: parseFloat(getVal("f-rainfall")),
        temperature_c: parseFloat(getVal("f-temperature")),
        humidity_pct: parseFloat(getVal("f-humidity")),
        river_level_m: parseFloat(getVal("f-river")),
        elevation_m: parseFloat(getVal("f-elevation")),
        soil_moisture: parseFloat(getVal("f-soil")),
        drainage_capacity_pct: parseFloat(getVal("f-drainage")),
        population_density: parseFloat(getVal("f-population")),
        impervious_pct: parseFloat(getVal("f-impervious")),
        wind_speed_kmh: parseFloat(getVal("f-wind")),
        land_use_type: getVal("f-landuse"),
        previous_flood_history: getVal("f-history") === "yes" ? 1 : 0,
      };

      setLoading(true);
      try {
        const res = await fetch("/api/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (res.ok) {
          renderResult(data);
        } else {
          window.FloodWaveToast && window.FloodWaveToast(data.error || "Prediction failed");
        }
      } catch (err) {
        window.FloodWaveToast && window.FloodWaveToast("Network error — please try again");
      } finally {
        setLoading(false);
      }
    });
  }

  function getVal(id) {
    const el = document.getElementById(id);
    return el ? el.value : "";
  }

  function setLoading(active) {
    if (els.loadingOverlay) els.loadingOverlay.classList.toggle("active", active);
    if (els.submitBtn) els.submitBtn.disabled = active;
  }

  function riskColor(label) {
    return { Low: "#34d399", Safe: "#34d399", Medium: "#fbbf24", Moderate: "#fbbf24", High: "#f87171", Severe: "#f87171" }[label] || "#48CAE4";
  }

  function renderResult(data) {
    if (!els.resultPanel) return;
    els.resultPanel.style.display = "block";

    const gaugePct = Math.round(data.confidence);
    const circumference = 2 * Math.PI * 34;
    const dashOffset = circumference * (1 - gaugePct / 100);

    const breakdownRows = Object.entries(data.probability_breakdown || {})
      .map(([k, v]) => `
        <div class="factor-bar">
          <div class="fb-label"><span>${k}</span><span>${v}%</span></div>
          <div class="fb-track"><div class="fb-fill" style="width:${v}%;background:${riskColor(k)}"></div></div>
        </div>`).join("");

    const factorsRows = (data.contributing_factors || [])
      .map(f => {
        const pct = Math.min(100, Math.abs(f.impact) * 400 + 15);
        return `
        <div class="factor-bar">
          <div class="fb-label"><span>${f.factor}</span><span>${f.impact}</span></div>
          <div class="fb-track"><div class="fb-fill" style="width:${pct}%"></div></div>
        </div>`;
      }).join("");

    const actionsRows = (data.recommended_actions || [])
      .map(a => `<li>${a}</li>`).join("");

    els.resultPanel.innerHTML = `
      <div class="result-header">
        <div>
          <h3 style="margin-bottom:4px;">Prediction Result</h3>
          <span style="font-size:0.8rem;opacity:0.7;">Model: ${data.model_used} · Explainability: ${data.explainability_method}</span>
        </div>
        <span class="risk-badge ${data.overall_risk}">${data.overall_risk} · ${data.flood_probability} Flood Probability</span>
      </div>
      <div class="result-grid">
        <div class="glass-card result-card">
          <h4>Confidence</h4>
          <div class="gauge-wrap">
            <svg viewBox="0 0 80 80">
              <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="8"/>
              <circle cx="40" cy="40" r="34" fill="none" stroke="${riskColor(data.flood_probability)}" stroke-width="8"
                stroke-dasharray="${circumference}" stroke-dashoffset="${dashOffset}" stroke-linecap="round"
                transform="rotate(-90 40 40)"/>
            </svg>
            <div class="gauge-value">${gaugePct}%</div>
          </div>
          <div style="margin-top:18px;">${breakdownRows}</div>
        </div>
        <div class="glass-card result-card">
          <h4>Contributing Factors</h4>
          ${factorsRows || '<p style="opacity:0.7;font-size:0.85rem;">No factor data available.</p>'}
        </div>
        <div class="glass-card result-card">
          <h4>Recommended Actions</h4>
          <ul class="action-list">${actionsRows}</ul>
        </div>
      </div>
    `;

    els.resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  }
})();
