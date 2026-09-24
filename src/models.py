"""
Modelo tecnico e economico - Producao de bioetanol a partir do soro de leite.

Este modulo concentra toda a logica de calculo do projeto, separada da
visualizacao, para que possa ser reutilizada nos notebooks e, futuramente,
em uma aplicacao Streamlit.

Convencao de nomenclatura dos parametros:
    - Prefixo/sufixo indica a UNIDADE (ex.: `_L` = litros, `_g` = gramas).
    - Todo valor numerico "magico" usado como premissa tem uma constante
      nomeada no topo do arquivo, com comentario indicando se e:
        MEDIDO      -> dado experimental do projeto (data/raw)
        EXTERNO     -> dado de fonte externa (data/external)
        CALCULADO   -> derivado por estequiometria/fisica basica
        PREMISSA    -> hipotese de projeto assumida explicitamente
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Caminhos de dados
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "dados_experimentais.csv"
EXTERNAL_DATA_PATH = DATA_DIR / "external" / "dados_externos.csv"


def load_experimental_data() -> pd.DataFrame:
    """Carrega a tabela de dados experimentais (data/raw)."""
    return pd.read_csv(RAW_DATA_PATH)


def load_external_data() -> pd.DataFrame:
    """Carrega a tabela de dados externos, com fontes (data/external)."""
    return pd.read_csv(EXTERNAL_DATA_PATH)


# ---------------------------------------------------------------------------
# Constantes fisico-quimicas (CALCULADO / dominio publico da quimica)
# ---------------------------------------------------------------------------

# Massas molares (g/mol) - tabela periodica
MOLAR_MASS_LACTOSE = 342.3      # C12H22O11
MOLAR_MASS_ETHANOL = 46.07      # C2H5OH

# Estequiometria: 1 mol de lactose -> 2 mol de hexoses (hidrolise)
#                 1 mol de hexose  -> 2 mol de etanol (fermentacao)
#                 => 1 mol de lactose -> 4 mol de etanol
# Rendimento teorico (Gay-Lussac estendido para lactose):
LACTOSE_TO_ETHANOL_MOL_RATIO = 4.0
THEORETICAL_YIELD_G_ETHANOL_PER_G_LACTOSE = (
    LACTOSE_TO_ETHANOL_MOL_RATIO * MOLAR_MASS_ETHANOL / MOLAR_MASS_LACTOSE
)  # = 0.538 g etanol / g lactose (dado externo E07, calculo proprio)

ETHANOL_DENSITY_G_PER_ML = 0.789  # a 20 C, valor de referencia de tabelas de quimica

# Constantes termicas para o calculo de energia teorica minima (notebook 04)
SPECIFIC_HEAT_WATER_KJ_PER_KG_K = 4.186          # calor especifico da agua
LATENT_HEAT_VAPORIZATION_WATER_KJ_PER_KG = 2257  # a 100 C
LATENT_HEAT_VAPORIZATION_ETHANOL_KJ_PER_KG = 841  # a 78.4 C
KWH_PER_KJ = 1 / 3600

# ---------------------------------------------------------------------------
# Premissas de composicao do soro (EXTERNO - data/external, id E03)
# ---------------------------------------------------------------------------

LACTOSE_CONCENTRATION_WHEY_G_PER_L = 49.0  # EXTERNO E03 (~4.9% m/m, EPAMIG/ILCT)

# ---------------------------------------------------------------------------
# Cadeia de processo observada no experimento (MEDIDO - data/raw)
# ---------------------------------------------------------------------------

# 250 mL soro cru -> 160 mL filtrado (desproteinizacao + filtracao a vacuo)
RECUPERACAO_FILTRACAO = 160 / 250  # 0.64, MEDIDO

# 160 mL mosto fermentado -> 15 mL destilado (destilacao fracionada)
RAZAO_DESTILADO_MOSTO = 15 / 160  # 0.09375, MEDIDO

VOLUME_SORO_EXPERIMENTO_L = 0.250  # MEDIDO


# ---------------------------------------------------------------------------
# Cenarios de teor alcoolico (PREMISSA DE PROJETO)
# ---------------------------------------------------------------------------
# A densidade/teor alcoolico do destilado NAO foi medida no experimento
# (ver data/README.md). Por decisao do responsavel pelo projeto, usamos a
# faixa esperada descrita no relatorio (secao 4.6): 5%-12% v/v antes de
# qualquer retificacao. Isso NAO e um dado medido - e uma premissa.

SCENARIOS: dict[str, dict[str, float]] = {
    "conservador": {
        "recuperacao_filtracao": RECUPERACAO_FILTRACAO,
        "razao_destilado_mosto": RAZAO_DESTILADO_MOSTO,
        "teor_alcoolico": 0.05,   # limite inferior da faixa esperada (relatorio 4.6)
    },
    "experimental": {
        "recuperacao_filtracao": RECUPERACAO_FILTRACAO,
        "razao_destilado_mosto": RAZAO_DESTILADO_MOSTO,
        "teor_alcoolico": 0.085,  # ponto medio da faixa esperada (relatorio 4.6)
    },
    "otimista": {
        "recuperacao_filtracao": RECUPERACAO_FILTRACAO,
        "razao_destilado_mosto": RAZAO_DESTILADO_MOSTO,
        "teor_alcoolico": 0.12,   # limite superior da faixa esperada (relatorio 4.6)
    },
}

# Eficiencia de fermentacao industrial reportada na literatura (EXTERNO E08/E09)
# Usada apenas como TETO TEORICO comparativo (rota biologica diferente: os
# estudos usam Kluyveromyces, que fermenta lactose direto; o projeto usa
# lactase + Saccharomyces cerevisiae). Ver data/README.md, item 3.
LITERATURE_FERMENTATION_EFFICIENCY_RANGE = (0.80, 0.97)


# ---------------------------------------------------------------------------
# Modelo tecnico
# ---------------------------------------------------------------------------

@dataclass
class ProcessBalance:
    """Balanco de volumes/massas de uma corrida do processo."""

    soro_L: float
    filtrado_L: float
    mosto_L: float
    destilado_L: float
    etanol_puro_L: float
    etanol_puro_g: float
    lactose_disponivel_g: float
    etanol_teorico_g: float
    eficiencia_sobre_teorico: float  # etanol_puro_g / etanol_teorico_g


def calculate_lactose_mass(
    soro_volume_L: float,
    lactose_concentration_g_L: float = LACTOSE_CONCENTRATION_WHEY_G_PER_L,
) -> float:
    """Massa de lactose disponivel em um volume de soro (g).

    `lactose_concentration_g_L` e um dado EXTERNO (proxy de literatura),
    pois a concentracao de lactose do soro usado no experimento nao foi
    medida.
    """
    return soro_volume_L * lactose_concentration_g_L


def calculate_theoretical_yield(
    lactose_mass_g: float,
    stoich_yield: float = THEORETICAL_YIELD_G_ETHANOL_PER_G_LACTOSE,
) -> float:
    """Massa teorica maxima de etanol (g) a partir de uma massa de lactose,
    assumindo conversao estequiometrica de 100% (Gay-Lussac estendido).
    """
    return lactose_mass_g * stoich_yield


def calculate_ethanol_production_custom(
    soro_volume_L: float,
    recuperacao_filtracao: float = RECUPERACAO_FILTRACAO,
    razao_destilado_mosto: float = RAZAO_DESTILADO_MOSTO,
    teor_alcoolico: float = SCENARIOS["experimental"]["teor_alcoolico"],
    lactose_concentration_g_L: float = LACTOSE_CONCENTRATION_WHEY_G_PER_L,
) -> ProcessBalance:
    """Versao parametrizada de `calculate_ethanol_production`, que aceita
    qualquer combinacao de parametros (nao apenas os 3 cenarios fixos).
    Usada pelo simulador interativo (app/); `calculate_ethanol_production`
    e os cenarios de notebook continuam usando esta funcao por baixo.

    IMPORTANTE (ressalva de escala): esta e uma extrapolacao LINEAR das
    razoes observadas em bancada (250 mL). Ela preserva o balanco de massa
    por definicao, mas assume implicitamente que a eficiencia de cada etapa
    (filtracao, fermentacao, destilacao) NAO muda com a escala - o que nao
    foi verificado experimentalmente nem confirmado na literatura consultada
    para este processo especifico. Ver notebook 03 para discussao.
    """
    filtrado_L = soro_volume_L * recuperacao_filtracao
    mosto_L = filtrado_L  # nenhuma perda adicional reportada entre filtrado e mosto
    destilado_L = mosto_L * razao_destilado_mosto
    etanol_puro_L = destilado_L * teor_alcoolico
    etanol_puro_g = etanol_puro_L * 1000 * ETHANOL_DENSITY_G_PER_ML

    lactose_disponivel_g = calculate_lactose_mass(soro_volume_L, lactose_concentration_g_L)
    etanol_teorico_g = calculate_theoretical_yield(lactose_disponivel_g)
    eficiencia = etanol_puro_g / etanol_teorico_g if etanol_teorico_g > 0 else float("nan")

    return ProcessBalance(
        soro_L=soro_volume_L,
        filtrado_L=filtrado_L,
        mosto_L=mosto_L,
        destilado_L=destilado_L,
        etanol_puro_L=etanol_puro_L,
        etanol_puro_g=etanol_puro_g,
        lactose_disponivel_g=lactose_disponivel_g,
        etanol_teorico_g=etanol_teorico_g,
        eficiencia_sobre_teorico=eficiencia,
    )


def calculate_ethanol_production(soro_volume_L: float, scenario_name: str) -> ProcessBalance:
    """Projeta a producao de etanol para um volume de soro, usando um dos
    3 cenarios fixos (conservador/experimental/otimista). Ver
    `calculate_ethanol_production_custom` para parametros livres.
    """
    if scenario_name not in SCENARIOS:
        raise ValueError(f"Cenario desconhecido: {scenario_name!r}. Use um de {list(SCENARIOS)}")
    return calculate_ethanol_production_custom(soro_volume_L, **SCENARIOS[scenario_name])


def calculate_yield(balance: ProcessBalance) -> dict[str, float]:
    """Metricas de rendimento a partir de um ProcessBalance."""
    return {
        "mL_etanol_puro_por_L_soro": (balance.etanol_puro_L / balance.soro_L) * 1000,
        "percentual_v_v_sobre_soro": (balance.etanol_puro_L / balance.soro_L) * 100,
        "percentual_do_rendimento_teorico": balance.eficiencia_sobre_teorico * 100,
    }


def run_scenario(soro_volume_L: float, scenario_name: str) -> dict:
    """Executa um cenario completo e devolve balanco + rendimento em um dict
    (formato conveniente para DataFrame / Streamlit).
    """
    balance = calculate_ethanol_production(soro_volume_L, scenario_name)
    yield_metrics = calculate_yield(balance)
    return {"cenario": scenario_name, **balance.__dict__, **yield_metrics}


def scale_production(volumes_L: list[float], scenario_name: str) -> pd.DataFrame:
    """Projeta um cenario para uma lista de volumes de soro (ex.: 100, 1000,
    10000, 100000, 1000000 L) e devolve um DataFrame.
    """
    rows = [run_scenario(v, scenario_name) for v in volumes_L]
    return pd.DataFrame(rows)


def scale_all_scenarios(volumes_L: list[float]) -> pd.DataFrame:
    """Mesmo que `scale_production`, mas para os tres cenarios de uma vez."""
    frames = [scale_production(volumes_L, s) for s in SCENARIOS]
    return pd.concat(frames, ignore_index=True)


def literature_ceiling_ethanol_g(
    soro_volume_L: float,
    fermentation_efficiency: float,
    lactose_concentration_g_L: float = LACTOSE_CONCENTRATION_WHEY_G_PER_L,
) -> float:
    """Teto teorico de producao de etanol (g) baseado em estequiometria +
    eficiencia de fermentacao industrial da LITERATURA (nao e um dos 3
    cenarios oficiais do projeto - serve como linha de referencia/comparacao
    em graficos). Ver LITERATURE_FERMENTATION_EFFICIENCY_RANGE.
    """
    lactose_g = calculate_lactose_mass(soro_volume_L, lactose_concentration_g_L)
    teorico_g = calculate_theoretical_yield(lactose_g)
    return teorico_g * fermentation_efficiency


# ---------------------------------------------------------------------------
# Modelo economico
# ---------------------------------------------------------------------------

@dataclass
class CostParams:
    """Parametros de custo, com a origem de cada um documentada no campo
    `origem`. Valores padrao vem dos dados MEDIDOS/EXTERNOS do projeto,
    escalonados de forma proporcional ao volume de soro processado.

    ATENCAO: os precos de lactase e fermento sao de VAREJO (farmacia/
    comercio local), nao de insumo industrial a granel - nao encontramos
    fonte institucional para preco industrial (ver data/README.md, item 2).
    Isso tende a SUPERESTIMAR o custo de insumos.
    """

    # Doses por litro de soro CRU, calculadas a partir do experimento (MEDIDO)
    lactase_g_por_L_soro: float = 4.0047 / VOLUME_SORO_EXPERIMENTO_L        # 16.02 g/L
    fermento_g_por_L_soro: float = 4.0 / VOLUME_SORO_EXPERIMENTO_L          # 16.0 g/L

    # Precos unitarios de VAREJO (MEDIDO, relatorio secao 3.6 / data E17-E18)
    preco_lactase_BRL_por_g: float = 40.00 / 4.0047     # R$9,99/g
    preco_fermento_BRL_por_g: float = 5.00 / 4.0        # R$1,25/g

    # Tarifa de energia industrial (EXTERNO E16, CEMIG Grupo A4, fora-ponta)
    tarifa_energia_BRL_por_kWh: float = 0.48077

    # Preco de referencia do etanol (EXTERNO E12, CEPEA/Esalq, hidratado)
    preco_etanol_BRL_por_L: float = 2.6412

    # Custo evitado de tratamento de efluente (nao usado por padrao - sem
    # dado de custo de tratamento por m3 encontrado; fica disponivel para
    # o usuario informar caso obtenha esse dado)
    custo_evitado_tratamento_BRL_por_L_soro: float = 0.0


def calculate_thermal_energy_kWh(
    soro_volume_L: float,
    balance: ProcessBalance,
    delta_T_desproteinizacao: float = 70.0,   # 25 C -> 95 C (MEDIDO, faixa 90-100 C)
    delta_T_destilacao: float = 53.0,         # 25 C -> 78 C (MEDIDO)
    usar_calor_latente_etanol: bool = True,
) -> float:
    """Energia termica TEORICA MINIMA (kWh) para aquecer o soro na
    desproteinizacao e para levar o mosto a ebulicao + vaporizar o volume
    de destilado coletado.

    Isto e um CALCULO FISICO (calor especifico + calor latente), nao um
    dado medido de consumo real de energia - nao inclui perdas termicas,
    eficiencia do equipamento (<100%) nem energia eletrica de bombas/
    agitadores/incubadora. O consumo real tende a ser MAIOR que este valor,
    possivelmente por um fator de varias vezes.
    """
    massa_soro_kg = soro_volume_L  # aproximacao: densidade do soro ~ 1 kg/L (93% agua)
    energia_aquecimento_kJ = (
        massa_soro_kg * SPECIFIC_HEAT_WATER_KJ_PER_KG_K * delta_T_desproteinizacao
    )

    massa_mosto_kg = balance.mosto_L
    energia_aquecimento_destilacao_kJ = (
        massa_mosto_kg * SPECIFIC_HEAT_WATER_KJ_PER_KG_K * delta_T_destilacao
    )

    massa_destilado_kg = balance.destilado_L
    calor_latente = (
        LATENT_HEAT_VAPORIZATION_ETHANOL_KJ_PER_KG
        if usar_calor_latente_etanol
        else LATENT_HEAT_VAPORIZATION_WATER_KJ_PER_KG
    )
    energia_vaporizacao_kJ = massa_destilado_kg * calor_latente

    energia_total_kJ = (
        energia_aquecimento_kJ + energia_aquecimento_destilacao_kJ + energia_vaporizacao_kJ
    )
    return energia_total_kJ * KWH_PER_KJ


def calculate_cost_from_balance(
    balance: ProcessBalance,
    cost_params: CostParams | None = None,
    label: str = "custom",
) -> dict[str, float]:
    """Mesmo calculo de `calculate_cost`, mas a partir de um ProcessBalance
    ja pronto (permite usar `calculate_ethanol_production_custom` com
    parametros livres, sem depender dos 3 cenarios fixos). Usada pelo
    simulador interativo.
    """
    cost_params = cost_params or CostParams()
    soro_volume_L = balance.soro_L

    custo_lactase = soro_volume_L * cost_params.lactase_g_por_L_soro * cost_params.preco_lactase_BRL_por_g
    custo_fermento = soro_volume_L * cost_params.fermento_g_por_L_soro * cost_params.preco_fermento_BRL_por_g

    energia_kWh = calculate_thermal_energy_kWh(soro_volume_L, balance)
    custo_energia = energia_kWh * cost_params.tarifa_energia_BRL_por_kWh

    custo_evitado = soro_volume_L * cost_params.custo_evitado_tratamento_BRL_por_L_soro

    custo_total = custo_lactase + custo_fermento + custo_energia - custo_evitado

    etanol_L = balance.etanol_puro_L
    custo_por_L_etanol = custo_total / etanol_L if etanol_L > 0 else float("inf")

    return {
        "cenario": label,
        "soro_L": soro_volume_L,
        "custo_lactase_R$": custo_lactase,
        "custo_fermento_R$": custo_fermento,
        "energia_kWh": energia_kWh,
        "custo_energia_R$": custo_energia,
        "custo_evitado_tratamento_R$": custo_evitado,
        "custo_total_R$": custo_total,
        "etanol_puro_L": etanol_L,
        "custo_por_L_etanol_R$": custo_por_L_etanol,
    }


def calculate_cost(
    soro_volume_L: float,
    scenario_name: str,
    cost_params: CostParams | None = None,
) -> dict[str, float]:
    """Custo total estimado (R$) para processar `soro_volume_L` litros de
    soro sob o cenario tecnico `scenario_name`, decomposto por item.
    """
    balance = calculate_ethanol_production(soro_volume_L, scenario_name)
    return calculate_cost_from_balance(balance, cost_params, label=scenario_name)


def calculate_revenue(
    etanol_puro_L: float,
    preco_etanol_BRL_por_L: float = CostParams().preco_etanol_BRL_por_L,
) -> float:
    """Receita bruta (R$) pela venda do etanol produzido, ao preco de
    referencia informado (EXTERNO E12/E13, CEPEA/Esalq).

    Ressalva: o etanol do processo e uma solucao hidroalcoolica de baixa
    concentracao (5-12% v/v premissa); para ser vendido ao preco de mercado
    de combustivel (~92-96 GL) precisaria de retificacao adicional, cujo
    custo NAO esta incluido neste calculo. Ver notebook 04.
    """
    return etanol_puro_L * preco_etanol_BRL_por_L


def run_economic_scenario(
    soro_volume_L: float,
    scenario_name: str,
    cost_params: CostParams | None = None,
) -> dict[str, float]:
    """Combina calculate_cost + calculate_revenue em um resultado unico."""
    cost_params = cost_params or CostParams()
    costs = calculate_cost(soro_volume_L, scenario_name, cost_params)
    revenue = calculate_revenue(costs["etanol_puro_L"], cost_params.preco_etanol_BRL_por_L)
    costs["receita_R$"] = revenue
    costs["resultado_operacional_R$"] = revenue - costs["custo_total_R$"]
    return costs


# ---------------------------------------------------------------------------
# Analise de sensibilidade
# ---------------------------------------------------------------------------

def sensitivity_analysis(
    soro_volume_L: float,
    scenario_name: str,
    variations: dict[str, list[float]],
    base_cost_params: CostParams | None = None,
) -> pd.DataFrame:
    """Analise de sensibilidade "um parametro por vez" (one-at-a-time /
    tornado). Para cada (parametro, multiplicador) em `variations`, recalcula
    o resultado operacional mantendo os demais parametros no valor base.

    `variations` exemplo:
        {
            "preco_etanol_BRL_por_L": [0.7, 0.85, 1.0, 1.15, 1.3],  # multiplicadores
            "tarifa_energia_BRL_por_kWh": [0.7, 1.0, 1.3],
            "preco_lactase_BRL_por_g": [0.5, 1.0, 2.0],
        }
    """
    base_cost_params = base_cost_params or CostParams()
    base_result = run_economic_scenario(soro_volume_L, scenario_name, base_cost_params)

    rows = []
    for param_name, multipliers in variations.items():
        for mult in multipliers:
            params_dict = base_cost_params.__dict__.copy()
            params_dict[param_name] = params_dict[param_name] * mult
            varied_params = CostParams(**params_dict)
            result = run_economic_scenario(soro_volume_L, scenario_name, varied_params)
            rows.append(
                {
                    "parametro": param_name,
                    "multiplicador": mult,
                    "valor_parametro": params_dict[param_name],
                    "resultado_operacional_R$": result["resultado_operacional_R$"],
                    "custo_total_R$": result["custo_total_R$"],
                    "delta_vs_base_R$": result["resultado_operacional_R$"]
                    - base_result["resultado_operacional_R$"],
                }
            )
    return pd.DataFrame(rows)


def monte_carlo_simulation(
    soro_volume_L: float,
    scenario_name: str,
    n_simulations: int,
    param_distributions: dict[str, tuple[float, float]],
    base_cost_params: CostParams | None = None,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Simulacao de Monte Carlo simples: cada parametro em
    `param_distributions` recebe uma distribuicao uniforme (min, max) e e
    sorteado independentemente a cada simulacao.

    Usar SOMENTE para os parametros cuja incerteza e conhecida e razoavel de
    modelar como uniforme (ex.: preco do etanol variando +-30% conforme
    volatilidade observada no CEPEA). Nao usar para "inventar" incerteza em
    parametros que na verdade sao desconhecidos por falta de dado - nesses
    casos, cenarios discretos (conservador/experimental/otimista) sao mais
    honestos que uma distribuicao de probabilidade sem base.
    """
    import numpy as np

    rng = np.random.default_rng(random_seed)
    base_cost_params = base_cost_params or CostParams()

    rows = []
    for _ in range(n_simulations):
        params_dict = base_cost_params.__dict__.copy()
        for param_name, (low, high) in param_distributions.items():
            params_dict[param_name] = rng.uniform(low, high)
        sim_params = CostParams(**params_dict)
        result = run_economic_scenario(soro_volume_L, scenario_name, sim_params)
        rows.append(result)

    return pd.DataFrame(rows)
