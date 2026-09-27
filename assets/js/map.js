/* ==========================================================================
   Mapa do Brasil — potencial de bioetanol por estado.

   Reaproveita calcBalance/calcEconomics/SCENARIOS/formatBRLCompact definidos
   em app.js (mesmo motor de calculo do Simulador — nao ha uma segunda
   formula "so para o mapa").
========================================================================== */

const VIOLET_RAMP = ["#f3f1fb", "#d9d0f0", "#b6a4e2", "#8a6fd0", "#5c3fb0", "#3c2f8a"];

function lerpColor(hexA, hexB, t) {
  const a = hexA.match(/\w\w/g).map((h) => parseInt(h, 16));
  const b = hexB.match(/\w\w/g).map((h) => parseInt(h, 16));
  const c = a.map((v, i) => Math.round(v + (b[i] - v) * t));
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
}

function rampColor(t) {
  const n = VIOLET_RAMP.length - 1;
  const scaled = Math.min(Math.max(t, 0), 1) * n;
  const i = Math.min(Math.floor(scaled), n - 1);
  return lerpColor(VIOLET_RAMP[i], VIOLET_RAMP[i + 1], scaled - i);
}

// --- Potencial de bioetanol por estado, a partir da producao de leite real ---
// Cadeia: leite (real, Embrapa/IBGE 2019) -> soro HIPOTETICO (E02, 85-90% SE
// todo o leite virasse queijo) -> mesmo pipeline do Simulador (calcBalance/
// calcEconomics), no cenario "experimental" (8.5% teor alcoolico, premissa).
function computeStatePotential(milLitros) {
  const milkL = milLitros * 1000;
  const soroMinL = milkL * SORO_FRACTION_MIN;
  const soroMaxL = milkL * SORO_FRACTION_MAX;
  const soroMidL = milkL * (SORO_FRACTION_MIN + SORO_FRACTION_MAX) / 2;

  const results = {};
  for (const [key, sc] of Object.entries(SCENARIOS)) {
    const balance = calcBalance(soroMidL, sc.teorAlcoolico);
    results[key] = balance.etanolPuroL;
  }
  const balanceMin = calcBalance(soroMinL, SCENARIOS.experimental.teorAlcoolico);
  const balanceMax = calcBalance(soroMaxL, SCENARIOS.experimental.teorAlcoolico);

  return {
    milkL, soroMidL,
    etanolPorCenario: results,
    etanolRangeSoro: [balanceMin.etanolPuroL, balanceMax.etanolPuroL],
  };
}

const STATE_INDEX = {};
MILK_PRODUCTION_BY_STATE.forEach((s) => {
  STATE_INDEX[s.code] = { ...s, potential: computeStatePotential(s.milLitros) };
});

const maxLog = Math.log10(Math.max(...MILK_PRODUCTION_BY_STATE.map((s) => s.milLitros)));
const minLog = Math.log10(Math.min(...MILK_PRODUCTION_BY_STATE.map((s) => s.milLitros)));

function formatMilLitros(milLitros) {
  const litros = milLitros * 1000;
  if (litros >= 1_000_000_000) return (litros / 1_000_000_000).toLocaleString("pt-BR", { maximumFractionDigits: 2 }) + " bilhões de L";
  if (litros >= 1_000_000) return (litros / 1_000_000).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + " milhões de L";
  return litros.toLocaleString("pt-BR", { maximumFractionDigits: 0 }) + " L";
}

function formatEtanolL(v) {
  if (v >= 1_000_000) return (v / 1_000_000).toLocaleString("pt-BR", { maximumFractionDigits: 2 }) + " milhões de L";
  if (v >= 1_000) return (v / 1_000).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + " mil L";
  return v.toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + " L";
}

let activeStateCode = null;

function renderDetail(code) {
  const s = STATE_INDEX[code];
  const detail = document.getElementById("map-detail");
  if (!s) {
    detail.innerHTML = `<div class="map-detail-placeholder"><div style="font-size:2rem;">🗺️</div><p>Passe o mouse sobre um estado (ou toque, no celular) para ver os números.</p></div>`;
    return;
  }
  const p = s.potential;
  detail.innerHTML = `
    <div class="map-detail-state">${s.nome}</div>
    <div class="map-detail-row">
      <span class="map-detail-label">Produção de leite (2019)</span>
      <span class="map-detail-value">${formatMilLitros(s.milLitros)}</span>
    </div>
    <div class="map-detail-row">
      <span class="map-detail-label">Soro potencial <span class="tag tag-externo">hipotético</span></span>
      <span class="map-detail-value">${formatEtanolL(p.soroMidL)}</span>
    </div>
    <div class="map-detail-divider"></div>
    <div class="map-detail-label" style="margin-bottom:0.5rem;">Potencial de bioetanol/ano (cenário)</div>
    ${Object.entries(SCENARIOS).map(([key, sc]) => `
      <div class="map-detail-row">
        <span class="map-detail-label"><span class="scenario-dot" style="background:${sc.cor}"></span>${sc.label}</span>
        <span class="map-detail-value">${formatEtanolL(p.etanolPorCenario[key])}</span>
      </div>
    `).join("")}
    <div class="map-detail-note">Premissa: 100% do leite do estado viraria queijo (não é o caso real) e teor alcoólico de 5–12% v/v (nunca medido — ver Metodologia). Use como teto comparativo, não como dado de descarte.</div>
  `;
}

function setActiveState(code) {
  activeStateCode = code;
  document.querySelectorAll("#map-svg-container [id^='state-']").forEach((el) => {
    el.classList.toggle("is-hovered", el.id === `state-${code}`);
  });
  document.querySelectorAll(".map-rank-row").forEach((row) => {
    row.classList.toggle("is-hovered", row.dataset.code === code);
  });
  renderDetail(code);
}

function renderRankingTable() {
  const sorted = [...MILK_PRODUCTION_BY_STATE].sort((a, b) => b.milLitros - a.milLitros).slice(0, 10);
  const table = document.getElementById("map-ranking-table");
  table.innerHTML = `
    <thead><tr><th>#</th><th>Estado</th><th>Produção de leite (2019)</th><th>Bioetanol potencial (cenário experimental)</th></tr></thead>
    <tbody>
      ${sorted.map((s, i) => `
        <tr class="map-rank-row" data-code="${s.code}">
          <td>${i + 1}</td>
          <td>${s.nome}</td>
          <td>${formatMilLitros(s.milLitros)}</td>
          <td>${formatEtanolL(STATE_INDEX[s.code].potential.etanolPorCenario.experimental)}</td>
        </tr>
      `).join("")}
    </tbody>
  `;
  table.querySelectorAll(".map-rank-row").forEach((row) => {
    row.addEventListener("mouseenter", () => setActiveState(row.dataset.code));
    row.addEventListener("mouseleave", () => setActiveState(null));
  });
}

async function loadMap() {
  const container = document.getElementById("map-svg-container");
  try {
    const resp = await fetch("vendor/brazil_states.svg");
    const svgText = await resp.text();
    container.innerHTML = svgText;
    const svg = container.querySelector("svg");
    svg.removeAttribute("width");
    svg.removeAttribute("height");
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");

    Object.entries(STATE_INDEX).forEach(([code, s]) => {
      const el = container.querySelector(`#state-${code}`);
      if (!el) return;
      const t = (Math.log10(s.milLitros) - minLog) / (maxLog - minLog);
      el.style.fill = rampColor(t);
      el.style.stroke = "#ffffff";
      el.style.strokeWidth = "300";
      el.style.cursor = "pointer";
      el.style.transition = "filter 0.15s, opacity 0.15s";
      el.addEventListener("mouseenter", () => setActiveState(code));
      el.addEventListener("mouseleave", () => setActiveState(null));
      el.addEventListener("click", () => setActiveState(code));
    });
  } catch (err) {
    container.innerHTML = `<p style="color:#d03b3b;">Não foi possível carregar o mapa (${err}).</p>`;
  }
}

const rampCss = VIOLET_RAMP.map((c, i) => `${c} ${(i / (VIOLET_RAMP.length - 1)) * 100}%`).join(", ");
document.querySelector(".map-legend-ramp").style.background = `linear-gradient(90deg, ${rampCss})`;

renderRankingTable();
loadMap();
