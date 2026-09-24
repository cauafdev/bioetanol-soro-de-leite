"""
Ponte entre o site (Streamlit) e o modelo de cálculo (src/models.py) já
validado nos notebooks 01-06. Nenhuma fórmula é reimplementada aqui - tudo
chama as mesmas funções usadas na pesquisa, para garantir que o site mostre
exatamente os mesmos números.
"""

from __future__ import annotations

import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .styling import CATEGORICAL, CENARIO_COLOR, INK, SRC_DIR, plotly_layout_defaults

sys.path.insert(0, str(SRC_DIR))
import models as m  # noqa: E402  (src/models.py - núcleo de cálculo do projeto)


@st.cache_data
def load_experimental_df() -> pd.DataFrame:
    # fillna: celulas de observacao vazias no CSV viram NaN, que o grid de
    # tabela do Streamlit exibe como o texto literal "None" - preferimos em branco.
    return m.load_experimental_data().fillna("")


@st.cache_data
def load_external_df() -> pd.DataFrame:
    return m.load_external_data()


@st.cache_data
def scale_all_scenarios_cached(volumes: tuple[float, ...]) -> pd.DataFrame:
    return m.scale_all_scenarios(list(volumes))


@st.cache_data
def economic_scenarios_cached(volumes: tuple[float, ...]) -> pd.DataFrame:
    frames = [
        pd.DataFrame([m.run_economic_scenario(v, s) for v in volumes])
        for s in m.SCENARIOS
    ]
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# Gráficos compartilhados (Plotly, paleta do dataviz skill)
# ---------------------------------------------------------------------------

def fig_producao_vs_volume(volumes: list[float]) -> go.Figure:
    escala = m.scale_all_scenarios(volumes)
    eff_min, eff_max = m.LITERATURE_FERMENTATION_EFFICIENCY_RANGE
    teto_min = [m.literature_ceiling_ethanol_g(v, eff_min) / (1000 * m.ETHANOL_DENSITY_G_PER_ML) for v in volumes]
    teto_max = [m.literature_ceiling_ethanol_g(v, eff_max) / (1000 * m.ETHANOL_DENSITY_G_PER_ML) for v in volumes]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=volumes + volumes[::-1], y=teto_max + teto_min[::-1],
        fill="toself", fillcolor="rgba(137,135,129,0.15)",
        line=dict(color="rgba(0,0,0,0)"), name="Teto teórico (literatura)",
        hoverinfo="skip", showlegend=True,
    ))
    for cenario in m.SCENARIOS:
        sub = escala[escala["cenario"] == cenario].sort_values("soro_L")
        fig.add_trace(go.Scatter(
            x=sub["soro_L"], y=sub["etanol_puro_L"], mode="lines+markers",
            name=f"Cenário {cenario}", line=dict(color=CENARIO_COLOR[cenario], width=2.5),
            marker=dict(size=8, line=dict(color="#fcfcfb", width=2)),
            hovertemplate="Soro: %{x:,.0f} L<br>Etanol puro: %{y:,.3f} L<extra>%{fullData.name}</extra>",
        ))

    layout = plotly_layout_defaults()
    fig.update_layout(
        **layout,
        title="Produção de etanol × volume de soro processado",
        xaxis_title="Volume de soro processado (L, escala log)",
        yaxis_title="Etanol puro produzido (L, escala log)",
        xaxis_type="log", yaxis_type="log",
        height=440,
    )
    return fig


def fig_comparacao_cenarios_bar(volumes: list[float]) -> go.Figure:
    escala = m.scale_all_scenarios(volumes)
    fig = go.Figure()
    for cenario in m.SCENARIOS:
        sub = escala[escala["cenario"] == cenario].sort_values("soro_L")
        fig.add_trace(go.Bar(
            x=[f"{v:,.0f} L" for v in sub["soro_L"]], y=sub["etanol_puro_L"],
            name=f"Cenário {cenario}", marker_color=CENARIO_COLOR[cenario],
            marker_line=dict(color="#fcfcfb", width=1),
            hovertemplate="%{x}<br>Etanol puro: %{y:,.3f} L<extra>%{fullData.name}</extra>",
        ))
    layout = plotly_layout_defaults()
    fig.update_layout(
        **layout,
        barmode="group",
        title="Comparação entre cenários por volume de soro",
        xaxis_title="Volume de soro processado",
        yaxis_title="Etanol puro produzido (L)",
        yaxis_type="log",
        height=440,
    )
    return fig


def fig_rendimento_comparacao() -> go.Figure:
    calibracao = pd.DataFrame([m.run_scenario(0.250, s) for s in m.SCENARIOS])
    labels = [
        "Nosso experimento (conservador, 5%)",
        "Nosso experimento (médio, 8,5%)",
        "Nosso experimento (otimista, 12%)",
        "Literatura industrial (mínimo, 80%)",
        "Literatura industrial (máximo, 97%)",
        "Rendimento teórico (estequiométrico, 100%)",
    ]
    values = [
        calibracao.loc[calibracao["cenario"] == "conservador", "eficiencia_sobre_teorico"].iloc[0] * 100,
        calibracao.loc[calibracao["cenario"] == "experimental", "eficiencia_sobre_teorico"].iloc[0] * 100,
        calibracao.loc[calibracao["cenario"] == "otimista", "eficiencia_sobre_teorico"].iloc[0] * 100,
        80, 97, 100,
    ]
    colors = [CENARIO_COLOR["conservador"], CENARIO_COLOR["experimental"], CENARIO_COLOR["otimista"],
              CATEGORICAL["violet"], CATEGORICAL["violet"], INK["muted"]]

    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h", marker_color=colors,
        text=[f"{v:.1f}%" for v in values], textposition="auto",
        insidetextfont=dict(color="white"), outsidetextfont=dict(color=INK["primary"]),
        hovertemplate="%{y}<br>%{x:.1f}%% do rendimento teórico<extra></extra>",
    ))
    layout = plotly_layout_defaults()
    layout["margin"] = dict(l=10, r=35, t=50, b=70)
    fig.update_layout(
        **layout,
        title="Nosso resultado vs. literatura vs. teto teórico",
        xaxis_title="% do rendimento teórico estequiométrico",
        xaxis_range=[0, 112],
        height=400,
    )
    return fig


def fig_custo_receita(volumes: list[float], cenario: str = "experimental") -> go.Figure:
    econ = economic_scenarios_cached(tuple(volumes))
    sub = econ[econ["cenario"] == cenario].sort_values("soro_L")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sub["soro_L"], y=sub["custo_total_R$"], mode="lines+markers", name="Custo total",
        line=dict(color=CATEGORICAL["red"], width=2.5),
        marker=dict(size=8, line=dict(color="#fcfcfb", width=2)),
        hovertemplate="Soro: %{x:,.0f} L<br>Custo: R$ %{y:,.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=sub["soro_L"], y=sub["receita_R$"], mode="lines+markers", name="Receita",
        line=dict(color=CATEGORICAL["aqua"], width=2.5, dash="dot"),
        marker=dict(size=8, line=dict(color="#fcfcfb", width=2)),
        hovertemplate="Soro: %{x:,.0f} L<br>Receita: R$ %{y:,.2f}<extra></extra>",
    ))
    layout = plotly_layout_defaults()
    fig.update_layout(
        **layout,
        title=f"Custo total vs. receita — cenário {cenario}",
        xaxis_title="Volume de soro processado (L, escala log)",
        yaxis_title="R$ (escala log)",
        xaxis_type="log", yaxis_type="log",
        height=440,
    )
    return fig


def fig_custo_composicao(volumes: list[float], cenario: str = "experimental") -> go.Figure:
    econ = economic_scenarios_cached(tuple(volumes))
    sub = econ[econ["cenario"] == cenario].sort_values("soro_L")

    fig = go.Figure()
    itens = [
        ("custo_lactase_R$", "Lactase (varejo)", CATEGORICAL["red"]),
        ("custo_fermento_R$", "Fermento (varejo)", CATEGORICAL["orange"]),
        ("custo_energia_R$", "Energia térmica (calculada)", CATEGORICAL["aqua"]),
    ]
    for col, label, color in itens:
        fig.add_trace(go.Scatter(
            x=sub["soro_L"], y=sub[col], mode="lines", stackgroup="custo",
            name=label, line=dict(width=0.5, color=color), fillcolor=color,
            hovertemplate="Soro: %{x:,.0f} L<br>" + label + ": R$ %{y:,.2f}<extra></extra>",
        ))
    layout = plotly_layout_defaults()
    fig.update_layout(
        **layout,
        title=f"Composição do custo total — cenário {cenario}",
        xaxis_title="Volume de soro processado (L, escala log)",
        yaxis_title="Custo (R$, escala log)",
        xaxis_type="log", yaxis_type="log",
        height=420,
    )
    return fig


def fig_tornado(volume_ref: float, cenario: str = "experimental") -> go.Figure:
    variations = {
        "preco_etanol_BRL_por_L": [0.70, 1.00, 1.30],
        "tarifa_energia_BRL_por_kWh": [0.70, 1.00, 1.30],
        "preco_lactase_BRL_por_g": [0.50, 1.00, 2.00],
        "preco_fermento_BRL_por_g": [0.50, 1.00, 2.00],
    }
    sens = m.sensitivity_analysis(volume_ref, cenario, variations)

    nomes = {
        "preco_etanol_BRL_por_L": "Preço do etanol (±30%)",
        "tarifa_energia_BRL_por_kWh": "Tarifa de energia (±30%)",
        "preco_lactase_BRL_por_g": "Preço da lactase (0,5×-2×)",
        "preco_fermento_BRL_por_g": "Preço do fermento (0,5×-2×)",
    }

    rows = []
    for param in sens["parametro"].unique():
        sub = sens[sens["parametro"] == param]
        rows.append({"parametro": nomes[param], "min": sub["resultado_operacional_R$"].min(),
                      "max": sub["resultado_operacional_R$"].max()})
    tornado = pd.DataFrame(rows)
    tornado["amplitude"] = tornado["max"] - tornado["min"]
    tornado = tornado.sort_values("amplitude")

    base = m.run_economic_scenario(volume_ref, cenario)["resultado_operacional_R$"]

    fig = go.Figure(go.Bar(
        x=tornado["max"] - tornado["min"], y=tornado["parametro"], base=tornado["min"],
        orientation="h", marker_color=CATEGORICAL["blue"],
        hovertemplate="%{y}<br>R$ %{base:,.0f} a R$ %{x:,.0f}<extra></extra>",
    ))
    fig.add_vline(x=base, line_dash="dash", line_color=INK["primary"], annotation_text="Base")
    layout = plotly_layout_defaults()
    fig.update_layout(
        **layout,
        title="Sensibilidade do resultado operacional (gráfico tornado)",
        xaxis_title=f"Resultado operacional (R$) para {volume_ref:,.0f} L de soro",
        height=380,
        showlegend=False,
    )
    return fig
