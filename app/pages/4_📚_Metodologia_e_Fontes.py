import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.styling import inject_base_css, page_header, source_note
from utils.data import load_external_df, load_experimental_df

st.set_page_config(page_title="Metodologia e Fontes — Bioetanol do Soro de Leite", page_icon="📚", layout="wide")
inject_base_css()

page_header(
    kicker="RASTREABILIDADE DOS DADOS",
    title="Metodologia e fontes",
    subtitle=(
        "Todo número usado nesta pesquisa é rotulado como medido, calculado, externo "
        "(com fonte) ou premissa de projeto. Esta página reúne a rastreabilidade completa."
    ),
)

st.markdown('<hr class="imp-section-divider">', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Dados experimentais", "Dados externos", "Limitações", "Referências bibliográficas"])

with tab1:
    st.markdown("#### Todos os dados medidos/calculados no experimento")
    df = load_experimental_df()
    st.dataframe(df, use_container_width=True, height=560, hide_index=True)
    source_note(
        "Extraído linha a linha de PROJETO_BIOETANOL_SORO_DE_LEITE_relatorio.docx "
        "(notebooks/01_data_audit.ipynb). FALTANTE = variável que o processo "
        "científico exigiria mas não foi determinada nesta execução."
    )

with tab2:
    st.markdown("#### Todos os dados externos, com fonte e nível de confiabilidade")
    ext = load_external_df()
    categorias = st.multiselect(
        "Filtrar por categoria", options=sorted(ext["categoria"].unique()),
        default=list(ext["categoria"].unique()),
    )
    ext_show = ext[ext["categoria"].isin(categorias)]
    st.dataframe(
        ext_show[["id", "categoria", "variavel", "valor", "unidade", "fonte", "data_fonte", "confiabilidade"]],
        use_container_width=True, height=460, hide_index=True,
    )
    st.markdown("**Detalhe completo de um dado específico:**")
    escolhido = st.selectbox("Selecionar dado (ID)", options=ext_show["id"].tolist())
    if escolhido:
        row = ext[ext["id"] == escolhido].iloc[0]
        d1, d2 = st.columns(2)
        with d1:
            st.markdown(f"**Variável:** {row['variavel']}")
            st.markdown(f"**Valor:** {row['valor']} {row['unidade']}")
            st.markdown(f"**Fonte:** {row['fonte']}")
            if str(row["url"]).startswith("http"):
                st.markdown(f"**URL:** {row['url']}")
            st.markdown(f"**Data da fonte:** {row['data_fonte']}")
        with d2:
            st.markdown(f"**Região:** {row['regiao']}")
            st.markdown(f"**Período de referência:** {row['periodo_referencia']}")
            st.markdown(f"**Metodologia:** {row['metodologia']}")
            st.markdown(f"**Confiabilidade:** {row['confiabilidade']}")
        st.info(f"**Observações e limitações:** {row['observacoes_limitacoes']}")
    source_note("Fonte completa em data/external/dados_externos.csv (notebooks/02_external_data.ipynb).")

with tab3:
    st.markdown("#### Limitações consolidadas")
    st.markdown(
        """
        1. **Densidade/teor alcoólico do destilado nunca foi medido** — a lacuna mais impactante de todo o modelo técnico. Resolvida com uma premissa de projeto (5-12% v/v), não uma medição.
        2. **Concentração de lactose do soro específico usado no experimento nunca foi medida** — usamos um proxy de literatura (~49 g/L, EPAMIG/ILCT).
        3. **Não há dado confiável de preço industrial de enzima/levedura** — usamos preço de varejo/farmácia, provavelmente uma superestimativa.
        4. **O modelo econômico não inclui CAPEX, custo do soro, mão de obra nem retificação** — é um modelo de custo variável apenas.
        5. **A rota biológica do experimento (lactase + *Saccharomyces cerevisiae*) tem menos precedente direto na literatura** do que a rota alternativa com *Kluyveromyces* (que fermenta lactose diretamente) — as comparações de eficiência são indicativas, não equivalentes.
        6. **Execução única, sem réplicas, sem ensaio controle, sem monitoramento cinético da fermentação** — limita qualquer afirmação sobre reprodutibilidade.
        7. O artigo mais diretamente comparável (Sansonetti et al. 2009, etanol de soro de ricota) não pôde ser acessado — citado como referência, não usado numericamente.
        """
    )
    st.markdown("#### O que isso significa para a conclusão")
    st.warning(
        "Este projeto **não** sustenta uma afirmação definitiva de viabilidade ou "
        "inviabilidade econômica industrial. As lacunas acima — sobretudo o teor "
        "alcoólico não medido e o preço industrial de insumo desconhecido — são "
        "as que mais mudariam a precisão desta análise, em ordem de impacto.",
        icon="⚠️",
    )

with tab4:
    st.markdown("#### Referências bibliográficas do relatório original")
    refs = [
        "ATKINS, Peter; JONES, Loretta. Princípios de Química: questionando a vida moderna e o meio ambiente. 7. ed. Porto Alegre: Bookman, 2018.",
        "BORZANI, Walter et al. Biotecnologia Industrial: Processos Fermentativos e Enzimáticos (Vol. 3). São Paulo: Blucher, 2020.",
        "BRAATHEN, Per Christian. A Química numa abordagem cotidiana. São Paulo: Editora CTS, 2021.",
        "BROWN, Theodore L. et al. Química: a ciência central. 14. ed. São Paulo: Pearson Education do Brasil, 2020.",
        "FELTRE, Ricardo. Química: Química Orgânica (Vol. 3). 7. ed. São Paulo: Moderna, 2015.",
        "MAGALHÃES, M. M.; ALMEIDA, R. S. Produção de biocombustíveis a partir de resíduos agroindustriais: uma abordagem para feiras de ciências. Química Nova na Escola, São Paulo, v. 46, n. 1, p. 34-41, 2024.",
        "PERES, L. S. et al. Reaproveitamento do soro de leite para produção de etanol de segunda geração. Revista Brasileira de Engenharia Química, Campinas, v. 41, n. 2, p. 112-120, 2023.",
        "REIS, Martha. Química: Ensino Médio (Vol. 3). 3. ed. São Paulo: Ática, 2021.",
        "SCHMIDELL, Willibaldo et al. Biotecnologia Industrial: Engenharia Bioquímica (Vol. 2). São Paulo: Blucher, 2021.",
        "SILVA, A. C.; SOUZA, J. G. Experimentos de Química Verde no Ensino Médio: a produção de bioálcool a partir de carboidratos complexos. Encontro Nacional de Ensino de Química (ENEQ), Anais... Belém: SBQ, 2025.",
    ]
    for r in refs:
        st.markdown(f"- {r}")

    st.markdown("#### Fontes externas consultadas nesta fase (pesquisa técnica/econômica)")
    ext = load_external_df()
    fontes_unicas = ext[["fonte", "url"]].drop_duplicates()
    for _, row in fontes_unicas.iterrows():
        if str(row["url"]).startswith("http"):
            st.markdown(f"- {row['fonte']} — [{row['url']}]({row['url']})")
        else:
            st.markdown(f"- {row['fonte']}")
