import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.styling import ASSETS_DIR, PHOTOS_DIR, inject_base_css, page_header, stat_tile

st.set_page_config(
    page_title="Bioetanol do Soro de Leite",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_base_css()

with st.sidebar:
    logo_path = PHOTOS_DIR / "logo_colegio.png"
    if logo_path.exists():
        st.image(str(logo_path), width=120)
    st.markdown("**Colégio IMP**  \nIII Feira do Conhecimento — 2026")
    st.markdown("---")
    st.caption(
        "Pesquisa desenvolvida em parceria com o Laboratório G-Óleo, "
        "Universidade Federal de Lavras (UFLA)."
    )

# --- Hero -------------------------------------------------------------
left, right = st.columns([1.15, 1], gap="large")

with left:
    page_header(
        kicker="FEIRA DE CIÊNCIAS · QUÍMICA · ENSINO MÉDIO",
        title="Bioetanol a partir do Soro de Leite",
        subtitle=(
            "Um resíduo da indústria de laticínios, rico em lactose, convertido em "
            "bioetanol por hidrólise enzimática e fermentação alcoólica — e avaliado, "
            "com dados reais e modelagem em Python, quanto ao seu potencial técnico "
            "e econômico em escala industrial."
        ),
    )
    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.page_link("pages/1_🧪_Experimento.py", label="Ver o experimento", icon="🧪")
    with c2:
        st.page_link("pages/2_📊_Resultados.py", label="Ver os resultados", icon="📊")
    with c3:
        st.page_link("pages/3_🧮_Simulador.py", label="Testar o simulador", icon="🧮")

with right:
    hero_photo = PHOTOS_DIR / "fig6_destilado_final.jpg"
    if hero_photo.exists():
        st.image(str(hero_photo), use_container_width=True,
                  caption="Destilado obtido ao final da destilação fracionada do mosto fermentado.")

st.markdown('<hr class="imp-section-divider">', unsafe_allow_html=True)

# --- Stat tiles ---------------------------------------------------------
st.markdown("##### O experimento em números")
s1, s2, s3, s4 = st.columns(4)
with s1:
    stat_tile("Soro de leite processado", "250 mL", help_text="Medido — laticínio local, Lavras-MG")
with s2:
    stat_tile("Destilado obtido", "15 mL", delta="6,0% do volume de soro (rendimento)", delta_color="muted",
               help_text="Medido — 15 mL de destilado a partir de 250 mL de soro (destilação fracionada, "
                          "coleta a 78 °C). Isto é uma razão de VOLUME (destilado/soro), não o teor "
                          "alcoólico do destilado — que não foi medido (ver cartão ao lado).")
with s3:
    stat_tile("Teste de chama", "Positivo", delta="Chama sem coloração visível", delta_color="good",
               help_text="Evidência qualitativa de etanol")
with s4:
    stat_tile("Teor alcoólico do destilado", "Não medido", delta="Densidade não determinada", delta_color="critical",
               help_text="Maior lacuna do experimento — ver página de Metodologia")

st.markdown('<hr class="imp-section-divider">', unsafe_allow_html=True)

# --- Project narrative ---------------------------------------------------
st.markdown("##### Sobre o projeto")
n1, n2, n3 = st.columns(3, gap="large")
with n1:
    st.markdown("**🧪 O problema**")
    st.markdown(
        "O soro de leite corresponde a 80–90% do volume de leite usado na fabricação "
        "de queijo. Descartado *in natura*, tem Demanda Bioquímica de Oxigênio muito "
        "alta e causa sério impacto ambiental — mas é rico em lactose, um açúcar "
        "fermentável."
    )
with n2:
    st.markdown("**⚗️ A rota experimental**")
    st.markdown(
        "Desproteinização térmica → filtração a vácuo → hidrólise da lactose com "
        "lactase → fermentação anaeróbica com *Saccharomyces cerevisiae* → destilação "
        "fracionada. Executada no Laboratório G-Óleo (UFLA), com evidências "
        "convergentes de produção de etanol."
    )
with n3:
    st.markdown("**📐 A pergunta desta fase**")
    st.markdown(
        "Esse resultado de bancada, combinado a dados reais da indústria de "
        "laticínios e da literatura, sustenta um processo tecnicamente e "
        "economicamente viável em escala? A resposta, com todas as ressalvas, "
        "está nas páginas de **Resultados** e no **Simulador**."
    )

st.markdown('<hr class="imp-section-divider">', unsafe_allow_html=True)

st.markdown("##### Equipe")
st.markdown(
    """
    **Estudantes:** Cauã Lara Fernando · Giovanni Marques Ferreira · Otávio Zanquini de Souza
    **Professor responsável:** André Luiz de Paiva Godinho — Professor de Química
    **Coorientadoras:** Fernanda Neves Miranda (Eng. de Materiais, UFLA) · Ana Alice Normandia de Lacerda (Eng. Química, UFLA)
    **Instituição parceira:** Laboratório G-Óleo — Universidade Federal de Lavras (UFLA)
    """
)

st.caption(
    "Este site consolida a pesquisa técnica e econômica documentada nos notebooks "
    "Jupyter do projeto (pasta `notebooks/`). Todo número aqui é rotulado como "
    "medido, calculado, externo (com fonte) ou premissa de projeto — nunca uma "
    "suposição silenciosa. Ver a página **Metodologia e Fontes** para o detalhe completo."
)
