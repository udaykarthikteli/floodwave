/* =========================================================================
   FloodWave — dashboard.js
   Fetches /api/dashboard-data and renders KPI cards + Plotly charts:
   risk distribution, monthly trend, model performance, SHAP-style
   feature importance, and a recent-predictions table.
   ========================================================================= */

(function () {
  "use strict";

  const plotlyTheme = {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: { color: "#e8f4fb", family: "Inter, sans-serif" },
    margin: { t: 20, r: 20, b: 40, l: 44 },
  };

  async function load() {
    const res = await fetch("/api/dashboard-data");
    const data = await res.json();
    renderKPIs(data);
    renderRiskDistribution(data.risk_distribution);
    renderMonthlyTrend(data.monthly_trend);
    renderModelPerformance(data.model_metadata);
    renderFeatureImportance(data.model_metadata);
    renderTable(data.recent_predictions);
  }

  function renderKPIs(data) {
    const total = Object.values(data.risk_distribution || {}).reduce((a, b) => a + b, 0);
    const high = (data.risk_distribution || {}).High || 0;
    const acc = data.model_metadata && data.model_metadata.all_results
      ? Object.values(data.model_metadata.all_results)[0]
      : null;

    const kpis = [
      { label: "Total Predictions", value: total, sub: "All-time recorded" },
      { label: "High-Risk Alerts", value: high, sub: "Requiring urgent action" },
      { label: "Best Model", value: (data.model_metadata && data.model_metadata.best_model) || "—", sub: "Auto-selected" },
      { label: "Model Accuracy", value: acc ? `${(acc.accuracy * 100).toFixed(1)}%` : "—", sub: "Held-out test set" },
    ];
    const wrap = document.getElementById("kpiGrid");
    if (!wrap) return;
    wrap.innerHTML = kpis.map(k => `
      <div class="glass-card kpi-card reveal in-view">
        <div class="kpi-label">${k.label}</div>
        <div class="kpi-value">${k.value}</div>
        <div class="kpi-sub">${k.sub}</div>
      </div>
    `).join("");
  }

  function renderRiskDistribution(dist) {
    const el = document.getElementById("riskDistChart");
    if (!el || typeof Plotly === "undefined") return;
    const labels = Object.keys(dist || {});
    const values = Object.values(dist || {});
    const colors = labels.map(l => ({ Low: "#34d399", Medium: "#fbbf24", High: "#f87171" }[l] || "#48CAE4"));

    Plotly.newPlot(el, [{
      type: "pie", labels, values, hole: 0.55,
      marker: { colors, line: { color: "#022544", width: 2 } },
      textfont: { color: "#fff" },
    }], { ...plotlyTheme, showlegend: true, legend: { orientation: "h" } }, { displayModeBar: false, responsive: true });
  }

  function renderMonthlyTrend(trend) {
    const el = document.getElementById("monthlyTrendChart");
    if (!el || typeof Plotly === "undefined") return;
    const months = Object.keys(trend || {});
    const series = ["Low", "Medium", "High"];
    const colors = { Low: "#34d399", Medium: "#fbbf24", High: "#f87171" };

    const traces = series.map(s => ({
      x: months,
      y: months.map(m => (trend[m] && trend[m][s]) || 0),
      name: s,
      type: "bar",
      marker: { color: colors[s] },
    }));

    Plotly.newPlot(el, traces, {
      ...plotlyTheme, barmode: "stack",
      xaxis: { gridcolor: "rgba(255,255,255,0.08)" },
      yaxis: { gridcolor: "rgba(255,255,255,0.08)" },
      legend: { orientation: "h" },
    }, { displayModeBar: false, responsive: true });
  }

  function renderModelPerformance(meta) {
    const el = document.getElementById("modelPerfChart");
    if (!el || typeof Plotly === "undefined" || !meta || !meta.all_results) return;

    const models = Object.keys(meta.all_results);
    const metricNames = ["accuracy", "precision", "recall", "f1"];
    const traces = metricNames.map(metric => ({
      x: models,
      y: models.map(m => (meta.all_results[m][metric] || 0) * 100),
      name: metric.toUpperCase(),
      type: "bar",
    }));

    Plotly.newPlot(el, traces, {
      ...plotlyTheme, barmode: "group",
      xaxis: { gridcolor: "rgba(255,255,255,0.08)" },
      yaxis: { gridcolor: "rgba(255,255,255,0.08)", title: "%" },
      legend: { orientation: "h" },
    }, { displayModeBar: false, responsive: true });
  }

  function renderFeatureImportance(meta) {
    const el = document.getElementById("featureImportanceChart");
    if (!el || typeof Plotly === "undefined" || !meta || !meta.feature_importance) return;

    const entries = Object.entries(meta.feature_importance).slice(0, 8).reverse();
    Plotly.newPlot(el, [{
      x: entries.map(e => e[1]),
      y: entries.map(e => e[0]),
      type: "bar",
      orientation: "h",
      marker: { color: "#48CAE4" },
    }], {
      ...plotlyTheme,
      xaxis: { gridcolor: "rgba(255,255,255,0.08)" },
      yaxis: { automargin: true },
    }, { displayModeBar: false, responsive: true });
  }

  function renderTable(rows) {
    const tbody = document.getElementById("predictionsTableBody");
    if (!tbody) return;
    if (!rows || !rows.length) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;opacity:0.6;padding:24px;">No predictions yet — run one from the Prediction page.</td></tr>`;
      return;
    }
    tbody.innerHTML = rows.map(r => `
      <tr>
        <td>${(r.city || "—")}${r.country ? ", " + r.country : ""}</td>
        <td>${r.rainfall_mm != null ? r.rainfall_mm + " mm" : "—"}</td>
        <td><span class="tag ${r.predicted_risk}">${r.predicted_risk}</span></td>
        <td>${r.confidence != null ? r.confidence + "%" : "—"}</td>
        <td>${new Date(r.created_at).toLocaleDateString()}</td>
      </tr>
    `).join("");
  }

  load();
})();
