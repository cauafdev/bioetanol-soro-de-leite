import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.styling import inject_base_css, page_header, source_note, stat_tile
from utils.data import (
    fig_comparacao_cenarios_bar,
    fig_custo_composicao,
    fig_custo_receita,
    fig_producao_vs_volume,
    fig_rendimento_comparacao,
    fig_tornado,
    m,
)

st.set_page_config(page_title="Resultados — Bioetanol do Soro de Leite", page_icon="📊", layout="wide")
inject_base_css()

page_header(
    kicker="MODELAGEM TÉCNICA E ECONÔMICA",
    title="O que o modelo mostra",
    subtitle=(
        "A partir do resultado de bancada, três cenários projetam a produção em escala "
        "e seu resultado econômico — com as ressalvas de cada premissa sempre visíveis."
    ),
)

VOLUMES = [100, 1_000, 10_000, 100_000, 1_000_000]

st.markdown('<hr class="imp-section-divider">', unsafe_allow_html=True)

# --- Técnico ---------------------------------------------------------------
st.markdown("### 1. Potencial técnico")

t1, t2, t3 = st.columns(3)
calib = {s: m.run_scenario(0.250, s) for s in m.SCENARIOS}
with t1:
    stat_tile("Cenário conservador", "3,0 mL etanol/L soro", delta="~9% do rendimento teórico", delta_color="muted")
with t2:
    stat_tile("Cenário experimental", "5,1 mL etanol/L soro", delta="~15% do rendimento teórico", delta_color="muted")
with t3:
    stat_tile("Cenário otimista", "7,2 mL etanol/L soro", delta="~22% do rendimento teórico", delta_color="muted")

st.plotly_chart(fig_producao_vs_volume(VOLUMES), use_container_width=True)
source_note(
    "Cenários calibrados no experimento (250 mL → 160 mL → 15 mL); teor alcoólico "
    "(5/8,5/12%) é premissa de projeto (relatório, seção 4.6), não medição. Teto "
    "teórico: estequiometria própria + eficiência de fermentação industrial da "
    "literatura (Kluyveromyces spp. — rota biológica diferente da usada no experimento)."
)

col_a, col_b = st.columns(2, gap="large")
with col_a:
    st.plotly_chart(fig_comparacao_cenarios_bar(VOLUMES), use_container_width=True)
    source_note("Mesma base de dados do gráfico anterior, em formato de barras por volume.")
with col_b:
    st.plotly_chart(fig_rendimento_comparacao(), use_container_width=True)
    source_note(
        "Comparação para 250 mL de soro (escala do experimento). A distância entre "
        "nosso melhor cenário (~22%) e a literatura industrial (80-97%) é esperada "
        "para um processo de bancada não otimizado, execução única, sem controle de "
        "pH na fermentação."
    )

with st.expander("Ressalva sobre escala — por que não é 'simplesmente multiplicar'"):
    st.markdown(
        """
        A extrapolação acima é **matematicamente linear**: mesma composição de soro,
        mesma eficiência de processo → resultado proporcional ao volume. Isso é
        diferente de dizer que a **eficiência** se mantém em escala industrial. Três
        coisas não foram verificadas:

        - **Filtração**: 64% de recuperação foi medido com funil de Büchner de
          bancada — centrífugas industriais têm eficiência diferente (não sabemos se maior ou menor).
        - **Fermentação**: manter anaerobiose e temperatura uniforme é mais simples em
          500 mL do que em milhares de litros — mas fermentadores industriais bem
          controlados podem *superar* a eficiência de bancada.
        - **Destilação**: colunas industriais, com mais estágios de equilíbrio, tendem
          a ser mais eficientes que a montagem usada.

        A extrapolação linear é o cenário mais simples e defensável com os dados que
        temos — não é uma previsão do desempenho industrial real.
        """
    )

st.markdown('<hr class="imp-section-divider">', unsafe_allow_html=True)

# --- Econômico ---------------------------------------------------------------
st.markdown("### 2. Potencial econômico")

col_c, col_d = st.columns(2, gap="large")
with col_c:
    st.plotly_chart(fig_custo_receita(VOLUMES, "experimental"), use_container_width=True)
with col_d:
    st.plotly_chart(fig_custo_composicao(VOLUMES, "experimental"), use_container_width=True)
source_note(
    "Custos de lactase/fermento em preço de VAREJO (relatório do projeto) — proxy "
    "fraco para preço industrial, não encontramos fonte confiável (ver Metodologia). "
    "Energia térmica calculada por física (calor específico + calor latente), não "
    "por preço de mercado de insumo. Preço do etanol: CEPEA/Esalq."
)

st.markdown("#### O achado mais robusto: nem a energia é coberta pela receita")
e1, e2 = st.columns([1, 1.4], gap="large")
with e1:
    cp = m.CostParams()
    custos_base = m.calculate_cost(10_000, "experimental", cp)
    receita_base = m.calculate_revenue(custos_base["etanol_puro_L"], cp.preco_etanol_BRL_por_L)
    razao = custos_base["custo_energia_R$"] / receita_base
    teor_breakeven = m.SCENARIOS["experimental"]["teor_alcoolico"] * razao
    stat_tile("Energia ÷ receita (10.000 L soro)", f"{razao:.1f}×", delta="custo de energia sozinho já supera a receita", delta_color="critical")
    st.write("")
    stat_tile("Teor alcoólico necessário só p/ cobrir energia", f"{teor_breakeven:.0%} v/v", delta="vs. 5-12% esperado pelo projeto", delta_color="critical")
with e2:
    st.markdown(
        """
        Isolar o custo de **energia térmica** (calculado por física — não depende de
        nenhum preço de varejo questionável) contra a receita ao preço real do
        etanol (CEPEA/Esalq) é o teste mais objetivo que este modelo permite.

        O resultado: mesmo **ignorando todos os reagentes**, a energia sozinha já
        custa ~4,8× mais do que a receita gerada. Seria necessário um teor
        alcoólico de **~41% v/v** só para empatar com a energia — bem acima da
        faixa de 5-12% que o próprio projeto espera antes de qualquer retificação.

        **Leitura**: o gargalo não é "só" o preço da enzima — é que o processo,
        como caracterizado no experimento, produz uma solução **muito diluída**.
        Aquecer/destilar um grande volume de líquido (majoritariamente água) para
        recuperar uma quantidade pequena de etanol é o que domina o custo.
        """
    )

st.plotly_chart(fig_tornado(10_000, "experimental"), use_container_width=True)
source_note(
    "Análise 'um parâmetro por vez' (one-at-a-time). Preço do etanol e energia "
    "variam ±30%; preço de lactase/fermento entre 0,5× e 2× o valor de varejo. "
    "Rendimento não incluso no gráfico (não é um CostParams) — ver notebook 05 "
    "para o teste isolado de -20% no teor alcoólico (efeito pequeno, R$ -27)."
)

st.markdown('<hr class="imp-section-divider">', unsafe_allow_html=True)

st.markdown("### 3. Conclusão desta fase")
c1, c2 = st.columns(2, gap="large")
with c1:
    st.success(
        "**O que os dados sustentam**: a rota química funciona (evidências "
        "convergentes de etanol); em escala, a produção cresce linearmente com o "
        "volume de soro, sob as mesmas eficiências observadas em bancada.",
        icon="✅",
    )
with c2:
    st.error(
        "**O que os dados NÃO sustentam**: uma afirmação definitiva de viabilidade "
        "ou inviabilidade econômica industrial — falta o preço real de insumo em "
        "escala e falta saber se a diluição do processo pode ser reduzida.",
        icon="⛔",
    )
st.info(
    "**Direção mais promissora**: não é negociar preço de insumo — é reduzir a "
    "diluição do processo (aumentar a concentração final de etanol). Isso não foi "
    "testado neste projeto.",
    icon="💡",
)
