import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.styling import PHOTOS_DIR, inject_base_css, page_header, source_note
from utils.data import load_experimental_df

st.set_page_config(page_title="Experimento — Bioetanol do Soro de Leite", page_icon="🧪", layout="wide")
inject_base_css()

page_header(
    kicker="METODOLOGIA EXPERIMENTAL",
    title="Do soro de leite ao destilado",
    subtitle=(
        "Cinco etapas, executadas no Laboratório G-Óleo (UFLA) ao longo de quatro idas, "
        "entre 21 de agosto e 18 de setembro de 2026."
    ),
)

st.markdown('<hr class="imp-section-divider">', unsafe_allow_html=True)

steps = [
    {
        "titulo": "1 · Desproteinização",
        "foto": "fig1_banho_maria.jpg",
        "texto": (
            "O pH do soro cru foi reduzido de 6,0 para a faixa de 4,5–4,6 com HCl — o "
            "ponto isoelétrico das proteínas do soro. Em seguida, aquecimento em "
            "banho-maria a 90–100 °C por 15–30 min desnatura e coagula as proteínas, "
            "visíveis como flocos brancos."
        ),
        "legenda": "Balão de fundo redondo com soro de leite bruto submerso em banho-maria.",
    },
    {
        "titulo": "2 · Filtração a vácuo",
        "foto": "fig2_filtracao_vacuo.jpg",
        "texto": (
            "O precipitado proteico foi separado por filtração a vácuo (funil de "
            "Büchner + kitassato + bomba de vácuo) — um aprimoramento em relação à "
            "filtração por gravidade originalmente planejada. Resultado: 160 mL de "
            "filtrado translúcido a partir de 250 mL de soro cru (64% de recuperação)."
        ),
        "legenda": "Sistema de filtração a vácuo: contraste entre o precipitado opaco e o filtrado translúcido.",
    },
    {
        "titulo": "3 · Hidrólise enzimática",
        "foto": "fig3_pesagem_lactase.jpg",
        "texto": (
            "4,0047 g de lactase (Aspergillus oryzae, ~106.000 U.FCC) foram adicionados "
            "ao filtrado, com temperatura controlada entre 37–40 °C — a faixa de "
            "trabalho da enzima — para romper a lactose em glicose e galactose."
        ),
        "legenda": "Pesagem da enzima lactase em balança analítica (resolução de 0,1 mg).",
    },
    {
        "titulo": "4 · Fermentação anaeróbica",
        "foto": "fig4_mosto_fermentado.jpg",
        "texto": (
            "4 g de fermento biológico seco (Saccharomyces cerevisiae) foram "
            "adicionados ao hidrolisado, sob selo hídrico, em incubadora a 30 °C por "
            "~72 horas. A produção de CO₂ no selo hídrico confirmou a atividade "
            "fermentativa."
        ),
        "legenda": "Mosto fermentado ao final da incubação — aspecto opaco, coloração bege.",
    },
    {
        "titulo": "5 · Destilação fracionada",
        "foto": "fig5_destilacao_fracionada.jpg",
        "texto": (
            "A destilação fracionada (não a simples originalmente planejada) foi "
            "conduzida com coleta a 78 °C — praticamente o ponto de ebulição do "
            "etanol puro (78,4 °C). Dos 160 mL de mosto, obtiveram-se 15 mL de "
            "destilado incolor."
        ),
        "legenda": "Sistema de destilação fracionada montado no Laboratório G-Óleo.",
    },
]

for i, step in enumerate(steps):
    col_txt, col_img = st.columns([1.3, 1], gap="large")
    text_col, img_col = (col_txt, col_img) if i % 2 == 0 else (col_img, col_txt)
    with col_txt:
        st.markdown(f"#### {step['titulo']}")
        st.markdown(step["texto"])
    with col_img:
        foto_path = PHOTOS_DIR / step["foto"]
        if foto_path.exists():
            st.image(str(foto_path), use_container_width=True)
            st.markdown(f'<div class="imp-figcaption">{step["legenda"]}</div>', unsafe_allow_html=True)
    st.write("")

st.markdown("#### Comprovação: teste de chama")
c1, c2 = st.columns([1, 1.3], gap="large")
with c1:
    foto_path = PHOTOS_DIR / "fig6_destilado_final.jpg"
    if foto_path.exists():
        st.image(str(foto_path), use_container_width=True)
        st.markdown('<div class="imp-figcaption">Destilado incolor recolhido em proveta graduada.</div>', unsafe_allow_html=True)
with c2:
    st.markdown(
        """
        Três evidências independentes sustentam a identificação do destilado como uma solução de etanol:

        1. **Térmica** — coleta estabilizada em 78 °C, coincidente com o ponto de ebulição do etanol puro (78,4 °C).
        2. **Combustão** — o líquido incolor entrou em combustão; água (a outra hipótese óbvia para um líquido incolor) não queima.
        3. **Aspecto da chama** — sem coloração visível, comportamento característico do etanol (combustão completa, sem fuligem incandescente).
        """
    )

st.markdown('<hr class="imp-section-divider">', unsafe_allow_html=True)

# --- Balanço + tabela de dados -------------------------------------------
st.markdown("#### Balanço de volumes")
bcol1, bcol2 = st.columns([1, 1.4], gap="large")
with bcol1:
    st.metric("Soro de leite cru", "250 mL", "100% do volume inicial", delta_color="off")
    st.metric("Filtrado (pós-desproteinização)", "160 mL", "64,0% do volume inicial", delta_color="off")
    st.metric("Mosto submetido à destilação", "160 mL", "64,0% do volume inicial", delta_color="off")
    st.metric("Destilado obtido", "15 mL", "6,0% do volume inicial", delta_color="off")

with bcol2:
    st.markdown("**Todos os dados experimentais** (classificados por tipo)")
    df = load_experimental_df()
    tipo_filter = st.multiselect(
        "Filtrar por tipo de dado", options=sorted(df["tipo"].unique()),
        default=list(df["tipo"].unique()),
    )
    df_show = df[df["tipo"].isin(tipo_filter)][["variavel", "valor", "unidade", "tipo"]]
    st.dataframe(df_show, use_container_width=True, height=320, hide_index=True)
    source_note(
        "Fonte: relatório do projeto (docs/relatorio-original.docx), "
        "extraído linha a linha em notebooks/01_data_audit.ipynb. FALTANTE = variável "
        "que o processo científico exigiria mas não foi determinada nesta execução."
    )

st.markdown('<hr class="imp-section-divider">', unsafe_allow_html=True)

st.markdown("#### ⚠️ A lacuna mais importante do experimento")
st.warning(
    "A **densidade e o teor alcoólico do destilado nunca foram medidos**. Sabemos que há "
    "álcool inflamável (evidências qualitativas acima), mas não em que concentração. "
    "Toda a modelagem técnica e econômica a partir daqui precisa assumir uma faixa de "
    "teor alcoólico — tratada explicitamente como **premissa de projeto** (5–12% v/v, "
    "a faixa que o próprio relatório já esperava antes da execução), nunca como medição.",
    icon="⚠️",
)

st.markdown("#### Custos do experimento (preço de varejo)")
cost_data = [
    ["Soro de leite fresco", "250 mL", "Laticínio local", "Não contabilizado"],
    ["Lactase em cápsulas", "4,0047 g usados (caixa de 30, 376 mg cada)", "Farmácia", "R$ 40,00"],
    ["Fermento biológico seco", "4 g usados", "Comércio local", "R$ 5,00"],
    ["Vidrarias e equipamentos", "—", "Cedidos pela UFLA", "Cedido"],
]
st.table(
    {
        "Item": [r[0] for r in cost_data],
        "Quantidade": [r[1] for r in cost_data],
        "Origem": [r[2] for r in cost_data],
        "Custo": [r[3] for r in cost_data],
    }
)
source_note(
    "Estes são preços de VAREJO/farmácia, usados como ponto de partida do modelo econômico "
    "(página Simulador) — não representam preço industrial a granel. Ver página Metodologia e Fontes."
)
