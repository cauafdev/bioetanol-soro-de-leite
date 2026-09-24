import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.styling import CATEGORICAL, INK, STATUS, format_brl_compact, inject_base_css, page_header, plotly_layout_defaults, source_note, stat_tile
from utils.data import m

st.set_page_config(page_title="Simulador — Bioetanol do Soro de Leite", page_icon="🧮", layout="wide")
inject_base_css()

page_header(
    kicker="SIMULADOR INDUSTRIAL E ECONÔMICO",
    title="Teste seus próprios cenários",
    subtitle=(
        "Ajuste volume, teor alcoólico e premissas de preço para ver o resultado técnico "
        "e econômico recalculado ao vivo — usando exatamente as mesmas funções dos notebooks "
        "de pesquisa (src/models.py)."
    ),
)

st.markdown('<hr class="imp-section-divider">', unsafe_allow_html=True)

col_ctrl, col_out = st.columns([1, 1.6], gap="large")

with col_ctrl:
    st.markdown("#### Parâmetros")

    soro_L = st.select_slider(
        "Volume de soro a processar",
        options=[10, 100, 1_000, 10_000, 100_000, 1_000_000],
        value=10_000,
        format_func=lambda v: f"{v:,} L",
    )

    cenario_base = st.radio(
        "Teor alcoólico do destilado",
        options=["Conservador (5%)", "Experimental (8,5%)", "Otimista (12%)", "Personalizado"],
        index=1,
        help="Nunca medido no experimento — ver página Experimento. Os 3 primeiros valores vêm "
             "da faixa que o próprio relatório do projeto já esperava (seção 4.6).",
    )
    teor_map = {"Conservador (5%)": 0.05, "Experimental (8,5%)": 0.085, "Otimista (12%)": 0.12}
    if cenario_base == "Personalizado":
        teor_alcoolico = st.slider("Teor alcoólico (% v/v)", min_value=1, max_value=60, value=9, step=1) / 100
        st.caption("Acima de ~40% v/v o processo passaria a cobrir seu próprio custo de energia (ver achado da análise de sensibilidade).")
    else:
        teor_alcoolico = teor_map[cenario_base]

    with st.expander("Premissas econômicas", expanded=False):
        st.caption("Valores padrão = preço de varejo pago no projeto / CEPEA-Esalq / CEMIG. Ver Metodologia e Fontes.")
        cp_default = m.CostParams()

        mult_lactase = st.select_slider(
            "Preço da lactase (múltiplo do preço de varejo)",
            options=[0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0],
            value=1.0, format_func=lambda v: f"{v:g}×",
        )
        mult_fermento = st.select_slider(
            "Preço do fermento (múltiplo do preço de varejo)",
            options=[0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0],
            value=1.0, format_func=lambda v: f"{v:g}×",
        )
        preco_etanol = st.number_input(
            "Preço de venda do etanol (R$/L)", min_value=0.5, max_value=6.0,
            value=cp_default.preco_etanol_BRL_por_L, step=0.05, format="%.2f",
        )
        mult_energia = st.select_slider(
            "Tarifa de energia (múltiplo da tarifa CEMIG)",
            options=[0.5, 0.7, 1.0, 1.3, 1.5, 2.0], value=1.0, format_func=lambda v: f"{v:g}×",
        )

    cost_params = m.CostParams(
        preco_lactase_BRL_por_g=cp_default.preco_lactase_BRL_por_g * mult_lactase,
        preco_fermento_BRL_por_g=cp_default.preco_fermento_BRL_por_g * mult_fermento,
        tarifa_energia_BRL_por_kWh=cp_default.tarifa_energia_BRL_por_kWh * mult_energia,
        preco_etanol_BRL_por_L=preco_etanol,
    )

# --- Cálculo (reutiliza src/models.py) ------------------------------------
balance = m.calculate_ethanol_production_custom(soro_L, teor_alcoolico=teor_alcoolico)
custos = m.calculate_cost_from_balance(balance, cost_params, label="simulador")
receita = m.calculate_revenue(custos["etanol_puro_L"], cost_params.preco_etanol_BRL_por_L)
resultado = receita - custos["custo_total_R$"]

with col_out:
    st.markdown("#### Resultado técnico")
    r1, r2, r3 = st.columns(3)
    with r1:
        stat_tile("Etanol puro produzido", f"{balance.etanol_puro_L*1000:,.2f} mL" if balance.etanol_puro_L < 1 else f"{balance.etanol_puro_L:,.2f} L")
    with r2:
        stat_tile("Destilado (hidroalcoólico)", f"{balance.destilado_L*1000:,.1f} mL" if balance.destilado_L < 1 else f"{balance.destilado_L:,.1f} L")
    with r3:
        stat_tile("% do rendimento teórico", f"{balance.eficiencia_sobre_teorico*100:,.1f}%",
                   delta_color="good" if balance.eficiencia_sobre_teorico > 0.8 else "muted")

    st.markdown("#### Resultado econômico")
    e1, e2, e3 = st.columns(3)
    with e1:
        stat_tile("Custo total", format_brl_compact(custos["custo_total_R$"]))
    with e2:
        stat_tile("Receita", format_brl_compact(receita))
    with e3:
        cor = "good" if resultado >= 0 else "critical"
        sinal = "lucro" if resultado >= 0 else "prejuízo"
        stat_tile("Resultado operacional", format_brl_compact(resultado), delta=sinal, delta_color=cor)

    # --- Gráfico: composição do custo vs receita ---------------------------
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Custo"], y=[custos["custo_lactase_R$"]], name="Lactase",
        marker_color=CATEGORICAL["red"], offsetgroup="custo",
    ))
    fig.add_trace(go.Bar(
        x=["Custo"], y=[custos["custo_fermento_R$"]], name="Fermento",
        marker_color=CATEGORICAL["orange"], offsetgroup="custo", base=[custos["custo_lactase_R$"]],
    ))
    fig.add_trace(go.Bar(
        x=["Custo"], y=[custos["custo_energia_R$"]], name="Energia",
        marker_color=CATEGORICAL["yellow"], offsetgroup="custo",
        base=[custos["custo_lactase_R$"] + custos["custo_fermento_R$"]],
    ))
    fig.add_trace(go.Bar(
        x=["Receita"], y=[receita], name="Receita (venda do etanol)",
        marker_color=CATEGORICAL["aqua"], offsetgroup="receita",
    ))
    layout = plotly_layout_defaults()
    fig.update_layout(
        **layout, barmode="stack", title="Custo (por item) vs. receita",
        yaxis_title="R$", height=380,
    )
    st.plotly_chart(fig, use_container_width=True)

    razao_energia_receita = custos["custo_energia_R$"] / receita if receita > 0 else float("inf")
    if razao_energia_receita > 1:
        st.error(
            f"Mesmo **ignorando lactase e fermento**, o custo de energia sozinho já é "
            f"**{razao_energia_receita:.1f}× maior** que a receita neste cenário.",
            icon="⚠️",
        )
    else:
        st.success(
            f"Neste cenário, a receita cobre o custo de energia isolado "
            f"({razao_energia_receita:.1%} dele) — mas isso ainda não conta os reagentes.",
            icon="✅",
        )

    source_note(
        "Cálculo ao vivo via src/models.py (mesmas funções dos notebooks 03-05). "
        "Teor alcoólico é premissa (não medição); preços de lactase/fermento partem "
        "do preço de varejo pago no projeto; energia calculada por física; preço do "
        "etanol e tarifa de energia partem de CEPEA/Esalq e CEMIG. Ver Metodologia e Fontes."
    )

st.markdown('<hr class="imp-section-divider">', unsafe_allow_html=True)
st.caption(
    "Este simulador não inclui investimento de capital (equipamentos, construção de planta), "
    "custo do soro como matéria-prima, mão de obra, nem retificação do etanol até pureza de "
    "combustível — ver página Metodologia e Fontes para a lista completa de limitações do modelo."
)
