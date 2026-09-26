"""
Gera knowledge/context.md a partir dos dados do projeto (data/, src/models.py).

Este e o "banco de dados" que a IA usa como contexto. Para adicionar novas
fontes/pesquisas no futuro:
  1. Adicione a linha em data/external/dados_externos.csv (mesmo formato: id,
     categoria, variavel, valor, unidade, fonte, url, data_fonte, regiao,
     periodo_referencia, metodologia, confiabilidade, observacoes_limitacoes)
  2. Rode: python build_context.py
  3. Reinicie o servidor (server.py) para carregar o contexto atualizado.

Nao inventa numeros: tudo que aparece aqui vem de data/raw, data/external ou
e calculado por src/models.py (mesma logica dos notebooks e do site Streamlit).
"""

from __future__ import annotations

import sys
from pathlib import Path

WEBAPP_DIR = Path(__file__).resolve().parent
ROOT_DIR = WEBAPP_DIR.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

import pandas as pd
import models as m  # noqa: E402

OUTPUT_PATH = WEBAPP_DIR / "knowledge" / "context.md"


def df_to_md_table(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False)


def build_experimental_section() -> str:
    df = m.load_experimental_data()
    return (
        "## 1. Dados experimentais medidos (Laboratório G-Óleo, UFLA)\n\n"
        "Cada linha abaixo tem um `tipo`: **Medido** (medido diretamente no experimento), "
        "**Calculado** (derivado por aritmética/estequiometria simples a partir de dados medidos).\n\n"
        f"{df_to_md_table(df)}\n"
    )


def build_external_section() -> str:
    df = m.load_external_data()
    cols = [
        "id", "categoria", "variavel", "valor", "unidade", "fonte",
        "regiao", "confiabilidade", "observacoes_limitacoes",
    ]
    return (
        "## 2. Dados externos (literatura científica e institucional)\n\n"
        "Fontes: EPAMIG/ILCT, CEPEA/Esalq (USP), CTBE/CNPEM, CEMIG, artigos indexados no PMC "
        "(estudos internacionais de fermentação de soro com *Kluyveromyces* spp.). Cada linha "
        "tem URL, ano, região e nível de confiabilidade documentados em "
        "`data/external/dados_externos.csv`.\n\n"
        f"{df_to_md_table(df[cols])}\n"
    )


def build_scenarios_section() -> str:
    volumes_L = [0.250, 100, 1_000, 10_000, 100_000, 1_000_000]
    df = m.scale_all_scenarios(volumes_L)
    cols = [
        "cenario", "soro_L", "filtrado_L", "mosto_L", "destilado_L",
        "etanol_puro_L", "mL_etanol_puro_por_L_soro", "percentual_do_rendimento_teorico",
    ]
    out = df[cols].copy()
    for c in ["soro_L", "filtrado_L", "mosto_L", "destilado_L", "etanol_puro_L"]:
        out[c] = out[c].map(lambda v: f"{v:,.4f}")
    out["mL_etanol_puro_por_L_soro"] = out["mL_etanol_puro_por_L_soro"].map(lambda v: f"{v:.2f}")
    out["percentual_do_rendimento_teorico"] = out["percentual_do_rendimento_teorico"].map(lambda v: f"{v:.1f}%")

    return (
        "## 3. Modelo técnico — projeção de produção por escala (calculado)\n\n"
        "Extrapolação LINEAR das razões medidas no experimento de bancada (250 mL). "
        "Os 3 cenários (conservador/experimental/otimista) diferem apenas no teor "
        "alcoólico assumido do destilado (5%, 8,5% e 12% v/v — premissa de projeto, "
        "NÃO medido; ver seção 6). `0,250 L` é o próprio experimento realizado.\n\n"
        f"{df_to_md_table(out)}\n\n"
        "Rendimento teórico estequiométrico: 0,538 g etanol / g lactose "
        "(lactose + H2O -> 2 hexoses -> 4 etanol + 4 CO2). "
        "Nos 3 cenários, o processo atinge entre 9% e 22% desse teto teórico.\n"
    )


def build_economics_section() -> str:
    rows = []
    for volume_L in (1_000, 100_000):
        for scenario in m.SCENARIOS:
            r = m.run_economic_scenario(volume_L, scenario)
            rows.append(r)
    df = pd.DataFrame(rows)
    cols = [
        "cenario", "soro_L", "etanol_puro_L", "custo_lactase_R$", "custo_fermento_R$",
        "energia_kWh", "custo_energia_R$", "custo_total_R$", "receita_R$",
        "resultado_operacional_R$",
    ]
    out = df[cols].copy()
    for c in cols:
        if c in ("cenario", "soro_L"):
            continue
        out[c] = out[c].map(lambda v: f"{v:,.2f}")

    return (
        "## 4. Modelo econômico — custo variável e receita (calculado)\n\n"
        "Custo de lactase/fermento a preço de VAREJO (farmácia/comércio local — "
        "superestima custo industrial real, ver seção 6). Tarifa de energia: CEMIG "
        "Grupo A4 fora-ponta. Preço do etanol: CEPEA/Esalq hidratado (set/2026). "
        "Modelo de custo VARIÁVEL apenas — não inclui CAPEX, mão de obra nem retificação.\n\n"
        f"{df_to_md_table(out)}\n\n"
        "**Achado mais robusto (independe do preço de varejo dos insumos):** "
        "isolando apenas o custo de ENERGIA TÉRMICA (calculado por física — calor "
        "específico e calor latente — não por preço de mercado) contra a receita ao "
        "preço real do etanol, o custo de energia sozinho já é aproximadamente 4,8× "
        "maior que a receita no cenário experimental. Seria necessário um teor "
        "alcoólico de aproximadamente 41% v/v só para cobrir a energia do processo — "
        "bem acima da faixa de 5–12% que o próprio projeto espera antes de retificação. "
        "Isso aponta para uma causa estrutural: o processo produz uma solução muito "
        "diluída (o custo de aquecer/destilar escala com o volume total, majoritariamente "
        "água; a receita escala com o teor alcoólico, que é baixo).\n"
    )


def build_limitations_section() -> str:
    return (
        "## 5. Limitações e lacunas de dados conhecidas (não inventar valores)\n\n"
        "1. **Teor alcoólico/densidade do destilado nunca foi medido no experimento.** "
        "Usa-se a faixa que o próprio projeto já esperava (5–12% v/v pré-retificação, "
        "relatório seção 4.6) como premissa de projeto, não como medição. É a lacuna "
        "mais impactante de todo o modelo técnico.\n"
        "2. **Preço industrial de lactase e de levedura não encontrado em fonte "
        "institucional.** Só há preço de varejo/farmácia — tende a SUPERESTIMAR o custo "
        "de insumos em escala industrial. Encontramos cotações comerciais online de "
        "lactase a granel (US$240–420/kg) — não são preço confirmado por compra real "
        "nem fonte institucional (confiabilidade Baixa/Média), mas mesmo assim são uma "
        "fração do preço de varejo usado no modelo, o que reforça que o custo de insumo "
        "do projeto provavelmente está superestimado.\n"
        "3. **Rendimento de fermentação da rota específica do projeto (lactase + "
        "*Saccharomyces cerevisiae*) tem literatura direta limitada.** A maior parte da "
        "literatura usa *Kluyveromyces marxianus/lactis*, que fermenta lactose "
        "diretamente — uma rota biológica diferente. Os valores de eficiência da "
        "literatura (80–97%) servem como TETO TEÓRICO comparativo, não validação direta. "
        "A referência mais próxima encontrada (O'Leary et al. 1977, USDA — usa lactase "
        "para hidrolisar a lactose antes da fermentação, como neste projeto) só foi "
        "acessada em resumo (paywall), mas já aponta um limite biológico adicional: "
        "*Saccharomyces cerevisiae* pode não fermentar bem a galactose liberada pela "
        "hidrólise (metade do açúcar disponível) — algo não verificado no experimento "
        "deste projeto.\n"
        "4. **Sansonetti et al. (2009)** — artigo mais próximo do processo do projeto "
        "(soro desproteinado → etanol) — está bloqueado por paywall; apenas o registro "
        "bibliográfico foi confirmado, os valores numéricos não foram usados.\n"
        "5. **Concentração de lactose no soro usado no experimento não foi medida** — "
        "usa-se a composição média de literatura (~4,9% m/m ≈ 49 g/L) como proxy.\n"
        "6. **Execução única, sem réplicas, sem ensaio controle, sem monitoramento "
        "cinético da fermentação** — limita qualquer afirmação sobre reprodutibilidade.\n"
        "7. **O modelo econômico não inclui CAPEX, custo do soro, mão de obra nem "
        "retificação** — é um modelo de custo variável apenas.\n"
    )


def build_conclusion_section() -> str:
    return (
        "## 6. Conclusão final do projeto (notebook 06)\n\n"
        "**O que os dados sustentam:**\n"
        "- A rota química (desproteinização → hidrólise enzimática → fermentação → "
        "destilação fracionada) FUNCIONA: produz um destilado inflamável a partir de "
        "um resíduo agroindustrial, com três evidências convergentes de que se trata "
        "de etanol (temperatura de coleta ≈78°C, combustão positiva, chama sem "
        "coloração visível).\n"
        "- Em escala, mantendo as mesmas eficiências de processo, a produção de "
        "etanol escala linearmente com o volume de soro — mas isso é uma extrapolação "
        "simples, não uma previsão de desempenho industrial real.\n"
        "- Nas condições de preço testadas, o processo está MUITO DISTANTE do "
        "equilíbrio econômico, e essa distância se mantém mesmo sob a incerteza mais "
        "favorável de preço de insumo, porque o próprio custo de energia (calculado, "
        "não estimado de mercado) já supera a receita.\n\n"
        "**O que os dados NÃO sustentam:**\n"
        "- Uma afirmação definitiva de viabilidade ou inviabilidade econômica "
        "industrial — falta o preço real de insumo em escala e falta saber se a "
        "concentração de etanol pode ser aumentada com otimização de processo.\n"
        "- Uma comparação direta e rigorosa com a literatura de fermentação de soro "
        "de leite — a rota biológica usada é diferente da mais estudada.\n"
        "- Qualquer estimativa de retorno sobre investimento — não há dado de CAPEX.\n\n"
        "**Próximos passos que mais mudariam a qualidade da análise, em ordem de impacto:**\n"
        "1. Medir a densidade/teor alcoólico do destilado (maior incerteza do modelo técnico).\n"
        "2. Buscar preço industrial real de lactase e levedura a granel.\n"
        "3. Testar formas de aumentar a concentração final de etanol (menos diluição) — "
        "a alavanca mais promissora indicada pela análise de sensibilidade, mais "
        "do que negociar preço de insumo.\n"
        "4. Repetir o experimento com réplicas e um ensaio controle sem lactase.\n"
    )


def build_provenance_section() -> str:
    rows = [
        ("Recuperação na filtração (64%)", "Medido", "Experimento"),
        ("Razão destilado/mosto (9,4%)", "Medido", "Experimento"),
        ("Teor alcoólico do destilado (5-12%)", "Premissa de projeto", "Relatório seção 4.6 (não medido)"),
        ("Concentração de lactose no soro (~49 g/L)", "Externo (proxy)", "EPAMIG/ILCT (não é medição do soro usado)"),
        ("Rendimento teórico estequiométrico (0,538 g/g)", "Calculado", "Estequiometria própria"),
        ("Eficiência industrial de fermentação (80-97%)", "Externo (literatura)", "Kluyveromyces spp. — rota biológica diferente"),
        ("Preço do etanol (R$ 2,64/L)", "Externo", "CEPEA/Esalq, set/2026"),
        ("Tarifa de energia industrial", "Externo", "CEMIG Grupo A4"),
        ("Energia térmica do processo", "Calculado", "Física (calor específico + calor latente)"),
        ("Preço de lactase e fermento", "Medido (mas VAREJO)", "Relatório — proxy fraco para preço industrial"),
    ]
    df = pd.DataFrame(rows, columns=["parametro", "tipo", "origem"])
    return (
        "## 7. Proveniência dos parâmetros centrais do modelo\n\n"
        f"{df_to_md_table(df)}\n"
    )


def main() -> None:
    sections = [
        "# Base de conhecimento — Bioetanol a partir do soro de leite\n\n"
        "Feira de Ciências — Colégio IMP / Laboratório G-Óleo (UFLA), Lavras-MG, 2026.\n\n"
        "Este documento é gerado automaticamente por `build_context.py` a partir de "
        "`data/raw/`, `data/external/` e `src/models.py`. Não editar diretamente — "
        "editar as fontes e rodar o script de novo.\n",
        build_experimental_section(),
        build_external_section(),
        build_scenarios_section(),
        build_economics_section(),
        build_limitations_section(),
        build_conclusion_section(),
        build_provenance_section(),
    ]
    OUTPUT_PATH.write_text("\n".join(sections), encoding="utf-8")
    print(f"Escrito: {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
