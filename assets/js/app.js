/* ==========================================================================
   soro.valor — motor de calculo do simulador.

   Cada constante e formula abaixo espelha 1:1 `src/models.py` (o mesmo
   modulo usado pelos notebooks de pesquisa e pelo site Streamlit). Isso foi
   conferido manualmente rodando `scale_all_scenarios` / `run_economic_scenario`
   em Python e comparando os resultados (ver historico da sessao). Se os
   numeros do simulador algum dia divergirem do Python, o Python e a fonte
   da verdade — corrija aqui, nunca o contrario.
========================================================================== */

// --- Constantes fisico-quimicas (CALCULADO / dominio publico da quimica) ---
const MOLAR_MASS_LACTOSE = 342.3;
const MOLAR_MASS_ETHANOL = 46.07;
const LACTOSE_TO_ETHANOL_MOL_RATIO = 4.0;
const STOICH_YIELD_G_ETHANOL_PER_G_LACTOSE =
  (LACTOSE_TO_ETHANOL_MOL_RATIO * MOLAR_MASS_ETHANOL) / MOLAR_MASS_LACTOSE; // 0.538

const ETHANOL_DENSITY_G_PER_ML = 0.789;
const SPECIFIC_HEAT_WATER_KJ_PER_KG_K = 4.186;
const LATENT_HEAT_VAPORIZATION_ETHANOL_KJ_PER_KG = 841;
const KWH_PER_KJ = 1 / 3600;

// --- Premissa de composicao do soro (EXTERNO E03) ---
const LACTOSE_CONCENTRATION_WHEY_G_PER_L = 49.0;

// --- Cadeia de processo observada no experimento (MEDIDO) ---
const RECUPERACAO_FILTRACAO = 160 / 250;      // 0.64
const RAZAO_DESTILADO_MOSTO = 15 / 160;       // 0.09375
const VOLUME_SORO_EXPERIMENTO_L = 0.250;

// --- Cenarios de teor alcoolico (PREMISSA DE PROJETO, relatorio 4.6) ---
const SCENARIOS = {
  conservador:  { teorAlcoolico: 0.05,  cor: "#eb6834", label: "Conservador" },
  experimental: { teorAlcoolico: 0.085, cor: "#2a78d6", label: "Experimental" },
  otimista:     { teorAlcoolico: 0.12,  cor: "#1baf7a", label: "Otimista" },
};

// --- Custos (MEDIDO/EXTERNO — preco de VAREJO, ver Metodologia) ---
const COST = {
  lactaseGPorLSoro: 4.0047 / VOLUME_SORO_EXPERIMENTO_L,     // 16.0188 g/L
  fermentoGPorLSoro: 4.0 / VOLUME_SORO_EXPERIMENTO_L,       // 16.0 g/L
  precoLactaseBRLPorG: 40.00 / 4.0047,                      // R$9,99/g
  precoFermentoBRLPorG: 5.00 / 4.0,                         // R$1,25/g
  tarifaEnergiaBRLPorKWh: 0.48077,                          // CEMIG A4 fora-ponta
  precoEtanolBRLPorL: 2.6412,                               // CEPEA/Esalq
};

function calcBalance(soroL, teorAlcoolico) {
  const filtradoL = soroL * RECUPERACAO_FILTRACAO;
  const mostoL = filtradoL;
  const destiladoL = mostoL * RAZAO_DESTILADO_MOSTO;
  const etanolPuroL = destiladoL * teorAlcoolico;
  const etanolPuroG = etanolPuroL * 1000 * ETHANOL_DENSITY_G_PER_ML;

  const lactoseDisponivelG = soroL * LACTOSE_CONCENTRATION_WHEY_G_PER_L;
  const etanolTeoricoG = lactoseDisponivelG * STOICH_YIELD_G_ETHANOL_PER_G_LACTOSE;
  const eficiencia = etanolTeoricoG > 0 ? etanolPuroG / etanolTeoricoG : NaN;

  return {
    soroL, filtradoL, mostoL, destiladoL, etanolPuroL, etanolPuroG,
    lactoseDisponivelG, etanolTeoricoG, eficiencia,
    etanolTeoricoL: etanolTeoricoG / (1000 * ETHANOL_DENSITY_G_PER_ML),
  };
}

function calcEnergyKWh(balance) {
  const deltaTDesproteinizacao = 70.0; // 25C -> 95C
  const deltaTDestilacao = 53.0;       // 25C -> 78C
  const energiaAquecimentoKJ = balance.soroL * SPECIFIC_HEAT_WATER_KJ_PER_KG_K * deltaTDesproteinizacao;
  const energiaAquecimentoDestilacaoKJ = balance.mostoL * SPECIFIC_HEAT_WATER_KJ_PER_KG_K * deltaTDestilacao;
  const energiaVaporizacaoKJ = balance.destiladoL * LATENT_HEAT_VAPORIZATION_ETHANOL_KJ_PER_KG;
  const energiaTotalKJ = energiaAquecimentoKJ + energiaAquecimentoDestilacaoKJ + energiaVaporizacaoKJ;
  return energiaTotalKJ * KWH_PER_KJ;
}

function calcEconomics(balance) {
  const custoLactase = balance.soroL * COST.lactaseGPorLSoro * COST.precoLactaseBRLPorG;
  const custoFermento = balance.soroL * COST.fermentoGPorLSoro * COST.precoFermentoBRLPorG;
  const energiaKWh = calcEnergyKWh(balance);
  const custoEnergia = energiaKWh * COST.tarifaEnergiaBRLPorKWh;
  const custoTotal = custoLactase + custoFermento + custoEnergia;
  const receita = balance.etanolPuroL * COST.precoEtanolBRLPorL;
  const resultadoOperacional = receita - custoTotal;
  return { custoLactase, custoFermento, energiaKWh, custoEnergia, custoTotal, receita, resultadoOperacional };
}

function runFull(soroL, teorAlcoolico) {
  const balance = calcBalance(soroL, teorAlcoolico);
  const economics = calcEconomics(balance);
  return { ...balance, ...economics };
}

/* ==========================================================================
   Formatacao (pt-BR) — espelha app/utils/styling.py::format_brl_compact
========================================================================== */

function formatBRLCompact(value) {
  const sign = value < 0 ? "-" : "";
  const v = Math.abs(value);
  let s;
  if (v >= 1_000_000) s = (v / 1_000_000).toLocaleString("pt-BR", { maximumFractionDigits: 2 }) + "M";
  else if (v >= 1_000) s = (v / 1_000).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + "K";
  else s = v.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
  return `${sign}R$ ${s}`;
}

function formatBRLFull(value) {
  return value.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 2 });
}

function formatLitros(value, casas = 0) {
  return value.toLocaleString("pt-BR", { maximumFractionDigits: casas }) + " L";
}

function formatVolumeSlider(v) {
  if (v >= 1000) return (v / 1000).toLocaleString("pt-BR", { maximumFractionDigits: v >= 100000 ? 0 : 1 }) + " mil L";
  return Math.round(v).toLocaleString("pt-BR") + " L";
}

/* ==========================================================================
   Estado global do simulador
========================================================================== */

const state = {
  soroL: 1000,
  scenario: "experimental",
  teorAlcoolico: SCENARIOS.experimental.teorAlcoolico,
  view: "producao",
  touched: false, // vira true assim que o usuario mexe em algo no Simulador
};

/* ==========================================================================
   Navegacao entre abas
========================================================================== */

document.querySelectorAll(".nav-item").forEach((btn) => {
  btn.addEventListener("click", () => goToTab(btn.dataset.tab));
});
document.querySelectorAll("[data-goto]").forEach((btn) => {
  btn.addEventListener("click", () => goToTab(btn.dataset.goto));
});

function goToTab(tab) {
  document.querySelectorAll(".nav-item").forEach((b) => b.classList.toggle("is-active", b.dataset.tab === tab));
  document.querySelectorAll(".tab-panel").forEach((p) => p.classList.toggle("is-active", p.id === `tab-${tab}`));
  window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
}

/* ==========================================================================
   Icones SVG (violeta, thin-stroke) — substituem emoji em toda a Visao Geral
========================================================================== */

const ICONS = {
  soro: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2c1.5 3 4.5 5 4.5 9a4.5 4.5 0 1 1-9 0c0-1.6.9-2.7 1.8-3.8.5 1 1.2 1.3 1.7.8-.4-2 .3-3.7 1-6z"/></svg>',
  flask: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2h4"/><path d="M11 2v6.5L5.5 18a2 2 0 0 0 1.7 3h9.6a2 2 0 0 0 1.7-3L13 8.5V2"/><path d="M8 15h8"/></svg>',
  trendUp: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l6-6 4 4 8-8"/><path d="M15 6h6v6"/></svg>',
  scale: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18"/><path d="M5 8h14"/><path d="M5 8l-3 6a3 3 0 0 0 6 0z"/><path d="M19 8l-3 6a3 3 0 0 0 6 0z"/></svg>',
  filter: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16l-6 8v6l-4 2v-8z"/></svg>',
  droplet: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3s6 7 6 11.5A6 6 0 0 1 6 14.5C6 10 12 3 12 3z"/></svg>',
};

/* ==========================================================================
   Contagem animada (ease-out) — usada na tira de processo
========================================================================== */

function animateCount(el, target, formatter, duration = 850) {
  const startTime = performance.now();
  function step(now) {
    const t = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - t, 3);
    el.textContent = formatter(target * eased);
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ==========================================================================
   Tira de processo — Soro cru -> Filtrado -> Destilado -> Bioetanol
========================================================================== */

function renderFlowStrip() {
  const r = runFull(state.soroL, state.teorAlcoolico);
  const steps = [
    { icon: ICONS.soro, label: "Soro cru", value: r.soroL, tag: "Medido" },
    { icon: ICONS.filter, label: "Filtrado / mosto", value: r.mostoL, tag: "Medido" },
    { icon: ICONS.droplet, label: "Destilado", value: r.destiladoL, tag: "Medido" },
    { icon: ICONS.flask, label: "Bioetanol (premissa)", value: r.etanolPuroL, tag: "Premissa" },
  ];
  const strip = document.getElementById("flow-strip");
  strip.innerHTML = steps.map((s, i) => `
    ${i > 0 ? `<div class="flow-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M13 6l6 6-6 6"/></svg></div>` : ""}
    <div class="flow-step">
      <div class="flow-icon">${s.icon}</div>
      <div class="flow-value" data-raw="${s.value}">0 L</div>
      <div class="flow-label">${s.label} <span class="tag tag-${s.tag.toLowerCase() === "medido" ? "medido" : "premissa"}">${s.tag}</span></div>
    </div>
  `).join("");

  strip.querySelectorAll(".flow-value").forEach((el) => {
    const raw = parseFloat(el.dataset.raw);
    const casas = raw < 10 ? 2 : raw < 1000 ? 1 : 0;
    animateCount(el, raw, (v) => formatLitros(v, casas));
  });
}

/* ==========================================================================
   Simulador — sliders, toggles, balanco
========================================================================== */

const sliderVolume = document.getElementById("slider-volume");
const sliderTeor = document.getElementById("slider-teor");
const volumeReadout = document.getElementById("volume-readout");
const teorReadout = document.getElementById("teor-readout");

function volumeFromSlider(sliderVal) {
  return Math.pow(10, parseFloat(sliderVal));
}
function sliderFromVolume(volumeL) {
  return Math.log10(volumeL);
}

sliderVolume.addEventListener("input", () => {
  state.soroL = volumeFromSlider(sliderVolume.value);
  state.touched = true;
  updateAll();
});

sliderTeor.addEventListener("input", () => {
  state.teorAlcoolico = parseFloat(sliderTeor.value) / 100;
  state.touched = true;
  // desmarca botoes de cenario se o valor nao bate com nenhum preset
  const matched = Object.entries(SCENARIOS).find(([, s]) => Math.abs(s.teorAlcoolico - state.teorAlcoolico) < 0.0001);
  document.querySelectorAll(".scenario-btn").forEach((b) => b.classList.toggle("is-active", !!matched && b.dataset.scenario === matched[0]));
  if (matched) state.scenario = matched[0];
  updateAll();
});

document.querySelectorAll(".scenario-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const sc = btn.dataset.scenario;
    state.scenario = sc;
    state.teorAlcoolico = SCENARIOS[sc].teorAlcoolico;
    state.touched = true;
    document.querySelectorAll(".scenario-btn").forEach((b) => b.classList.toggle("is-active", b === btn));
    sliderTeor.value = (state.teorAlcoolico * 100).toFixed(1);
    teorReadout.textContent = `${(state.teorAlcoolico * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}% v/v`;
    updateAll();
  });
});

document.querySelectorAll(".view-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    state.view = btn.dataset.view;
    document.querySelectorAll(".view-btn").forEach((b) => b.classList.toggle("is-active", b === btn));
    renderChart();
  });
});

document.getElementById("btn-restore").addEventListener("click", () => {
  state.soroL = 1000;
  state.scenario = "experimental";
  state.teorAlcoolico = SCENARIOS.experimental.teorAlcoolico;
  state.view = "producao";
  state.touched = false;
  sliderVolume.value = sliderFromVolume(1000);
  sliderTeor.value = "8.5";
  document.querySelectorAll(".scenario-btn").forEach((b) => b.classList.toggle("is-active", b.dataset.scenario === "experimental"));
  document.querySelectorAll(".view-btn").forEach((b) => b.classList.toggle("is-active", b.dataset.view === "producao"));
  updateAll();
});

function renderVolumeReadout() {
  volumeReadout.textContent = formatVolumeSlider(state.soroL);
  teorReadout.textContent = `${(state.teorAlcoolico * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}% v/v`;
}

function renderMiniStats() {
  const r = runFull(state.soroL, state.teorAlcoolico);
  const mini = document.getElementById("sim-mini");
  mini.innerHTML = `
    <div><div class="mini-stat-label">Etanol produzido</div><div class="mini-stat-value">${r.etanolPuroL.toLocaleString("pt-BR", { maximumFractionDigits: 2 })} L</div></div>
    <div><div class="mini-stat-label">Eficiência sobre o teórico</div><div class="mini-stat-value">${(r.eficiencia * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}%</div></div>
    <div><div class="mini-stat-label">Custo total (varejo)</div><div class="mini-stat-value">${formatBRLCompact(r.custoTotal)}</div></div>
    <div><div class="mini-stat-label">Resultado operacional</div><div class="mini-stat-value ${r.resultadoOperacional < 0 ? "is-critical" : ""}">${formatBRLCompact(r.resultadoOperacional)}</div></div>
  `;
}

function renderBalanceFlow() {
  const r = runFull(state.soroL, state.teorAlcoolico);
  const nodes = [
    { label: "Soro cru", value: formatLitros(r.soroL, r.soroL < 10 ? 2 : 0) },
    { label: "Filtrado / mosto", value: formatLitros(r.mostoL, r.mostoL < 10 ? 2 : 0) },
    { label: "Destilado", value: formatLitros(r.destiladoL, 2) },
    { label: "Etanol puro (premissa)", value: formatLitros(r.etanolPuroL, 3) },
  ];
  const flow = document.getElementById("balance-flow");
  flow.innerHTML = nodes.map((n, i) => `
    ${i > 0 ? '<div class="balance-arrow">→</div>' : ""}
    <div class="balance-node"><div class="bn-label">${n.label}</div><div class="bn-value">${n.value}</div></div>
  `).join("");
}

/* ==========================================================================
   Grafico — Curva de potencial (Chart.js)
========================================================================== */

let chartInstance = null;

function logRange(min, max, n) {
  const logMin = Math.log10(min);
  const logMax = Math.log10(max);
  const pts = [];
  for (let i = 0; i < n; i++) {
    pts.push(Math.pow(10, logMin + ((logMax - logMin) * i) / (n - 1)));
  }
  return pts;
}

function renderChart() {
  const ctx = document.getElementById("sim-chart-canvas");
  const volumes = logRange(10, 1_000_000, 40);
  const note = document.getElementById("chart-note");

  if (chartInstance) chartInstance.destroy();

  if (state.view === "producao") {
    const datasets = Object.entries(SCENARIOS).map(([key, sc]) => ({
      label: sc.label,
      data: volumes.map((v) => ({ x: v, y: calcBalance(v, sc.teorAlcoolico).etanolPuroL })),
      borderColor: sc.cor,
      backgroundColor: sc.cor,
      borderWidth: key === state.scenario ? 3 : 1.5,
      pointRadius: 0,
      tension: 0.15,
    }));
    datasets.push({
      label: "Limite teórico (estequiométrico)",
      data: volumes.map((v) => ({ x: v, y: calcBalance(v, 1).etanolTeoricoL })),
      borderColor: "#c9c2dc",
      borderDash: [5, 4],
      borderWidth: 1.5,
      pointRadius: 0,
      tension: 0.15,
    });
    datasets.push({
      label: "Ponto atual",
      data: [{ x: state.soroL, y: calcBalance(state.soroL, state.teorAlcoolico).etanolPuroL }],
      type: "scatter",
      showLine: false,
      pointRadius: 6,
      pointBackgroundColor: "#4a3aa7",
      pointBorderColor: "#fff",
      pointBorderWidth: 2,
    });

    chartInstance = new Chart(ctx, {
      type: "line",
      data: { datasets },
      options: chartOptions("Volume de soro (L)", "Bioetanol (L)"),
    });
    note.textContent = "Linha tracejada = teto estequiométrico (100% de conversão). Ponto roxo = seleção atual.";
  } else {
    const custoData = volumes.map((v) => {
      const b = calcBalance(v, state.teorAlcoolico);
      return { x: v, y: calcEconomics(b).custoTotal };
    });
    const receitaData = volumes.map((v) => {
      const b = calcBalance(v, state.teorAlcoolico);
      return { x: v, y: calcEconomics(b).receita };
    });
    const datasets = [
      { label: "Custo total (varejo)", data: custoData, borderColor: "#d03b3b", backgroundColor: "#d03b3b", borderWidth: 2.5, pointRadius: 0, tension: 0.1 },
      { label: "Receita estimada", data: receitaData, borderColor: "#0ca30c", backgroundColor: "#0ca30c", borderWidth: 2.5, pointRadius: 0, tension: 0.1 },
      {
        label: "Ponto atual",
        data: [{ x: state.soroL, y: calcEconomics(calcBalance(state.soroL, state.teorAlcoolico)).custoTotal }],
        type: "scatter", showLine: false, pointRadius: 6,
        pointBackgroundColor: "#4a3aa7", pointBorderColor: "#fff", pointBorderWidth: 2,
      },
    ];
    chartInstance = new Chart(ctx, {
      type: "line",
      data: { datasets },
      options: chartOptions("Volume de soro (L)", "R$", true),
    });
    note.textContent = "Escala log-log — em todo o intervalo simulado, o custo (insumo a preço de varejo) supera a receita.";
  }
}

function chartOptions(xLabel, yLabel, logY = false) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "nearest", intersect: false },
    plugins: {
      legend: {
        position: "bottom",
        labels: { color: "#524c63", font: { size: 11 }, boxWidth: 12, usePointStyle: true, filter: (item) => item.text !== "Ponto atual" },
      },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const v = ctx.parsed.y;
            const formatted = yLabel === "R$" ? formatBRLFull(v) : `${v.toLocaleString("pt-BR", { maximumFractionDigits: 2 })} L`;
            return `${ctx.dataset.label}: ${formatted}`;
          },
        },
      },
    },
    scales: {
      x: {
        type: "logarithmic",
        title: { display: true, text: xLabel, color: "#8b849b", font: { size: 11 } },
        grid: { color: "#e4e0f0" },
        ticks: {
          color: "#8b849b", font: { size: 10 },
          callback: (value) => {
            const log = Math.log10(value);
            if (Math.abs(log - Math.round(log)) > 1e-9) return null;
            return value.toLocaleString("pt-BR");
          },
        },
      },
      y: {
        type: logY ? "logarithmic" : "linear",
        title: { display: true, text: yLabel, color: "#8b849b", font: { size: 11 } },
        grid: { color: "#e4e0f0" },
        ticks: logY
          ? {
              color: "#8b849b", font: { size: 10 },
              callback: (value) => {
                const log = Math.log10(value);
                if (Math.abs(log - Math.round(log)) > 1e-9) return null;
                return formatBRLCompact(value);
              },
            }
          : { color: "#8b849b", font: { size: 10 } },
      },
    },
  };
}

/* ==========================================================================
   Referencias
========================================================================== */

function renderReferences() {
  const container = document.getElementById("references-list");
  const relBadge = { alta: "reliability-alta", media: "reliability-media", baixa: "reliability-baixa" };
  const relLabel = { alta: "Confiabilidade alta", media: "Confiabilidade média", baixa: "Confiabilidade baixa" };

  container.innerHTML = Object.entries(REFERENCES).map(([grupo, itens]) => `
    <div class="ref-group">
      <div class="ref-group-title">${grupo}</div>
      ${itens.map((ref) => `
        <div class="ref-card">
          <div class="ref-head">
            <div class="ref-title">
              <span style="color:#8b849b;font-weight:700;">${ref.id}</span> —
              ${ref.url ? `<a href="${ref.url}" target="_blank" rel="noopener">${ref.titulo}</a>` : ref.titulo}
              <div style="font-weight:400;color:#8b849b;font-size:0.82rem;margin-top:0.2rem;">${ref.autor}</div>
            </div>
            <span class="reliability ${relBadge[ref.confiabilidade]}">${relLabel[ref.confiabilidade]}</span>
          </div>
          <div class="ref-meta"><strong style="color:#17131f;">Dado usado:</strong> ${ref.dado}</div>
          <div class="ref-note">${ref.nota}</div>
        </div>
      `).join("")}
    </div>
  `).join("");
}

/* ==========================================================================
   Loop principal
========================================================================== */

function updateAll() {
  renderVolumeReadout();
  renderFlowStrip();
  renderMiniStats();
  renderBalanceFlow();
  renderChart();
}

sliderVolume.value = sliderFromVolume(state.soroL);
sliderTeor.value = (state.teorAlcoolico * 100).toFixed(1);
renderReferences();
updateAll();
