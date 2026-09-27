# Metodologia

Este documento descreve, por extenso, a metodologia experimental e estatística do projeto
**"Produção de bioetanol a partir do soro de leite"** (Colégio IMP / Laboratório G-Óleo, UFLA). É o
complemento textual da aba "Metodologia" do site (`index.html`) e dos comentários em
`src/models.py` — nada aqui deveria contradizer o código; se um dia contradisser, o código é a fonte
da verdade e este documento está desatualizado.

## 1. Metodologia experimental

Execução única (sem réplicas), realizada no Laboratório G-Óleo (UFLA), Lavras-MG, entre 15/09/2026 e
18/09/2026 (fermentação) dentro do período do projeto (01/06/2026–25/09/2026). Etapas, com os
parâmetros efetivamente medidos (ver `data/raw/dados_experimentais.csv` para a tabela completa):

| Etapa | Condições | Entrada → Saída |
|---|---|---|
| 1. Desproteinização | 90–100 °C, 15–30 min, filtração a vácuo (Büchner) | 250 mL soro cru → 160 mL filtrado |
| 2. Hidrólise enzimática | Lactase, 37–40 °C, 4,0047 g de enzima | Lactose → glicose + galactose |
| 3. Fermentação | *Saccharomyces cerevisiae* (4 g), 30 °C, 72 h (15–18/09/2026) | 160 mL mosto fermentado |
| 4. Destilação fracionada | Coleta a 78 °C | 15 mL destilado |

**Evidências de identificação do destilado como etanol** (todas qualitativas ou indiretas — a
densidade/teor alcoólico nunca foram medidos diretamente, ver seção 3):
1. Temperatura de coleta ≈78 °C — coerente com o ponto de ebulição do etanol.
2. Teste de chama positivo, combustão sem coloração visível.
3. Rota química coerente com a literatura de hidrólise enzimática de lactose seguida de fermentação
   alcoólica (ver `docs/referencias-ABNT.md`, referências E07–E10, E19).

**Amostra:** n = 1 (uma corrida experimental, sem réplicas nem ensaio controle sem lactase). Esta é
uma limitação central do projeto — nenhuma afirmação sobre reprodutibilidade ou variância do processo
experimental pode ser feita a partir destes dados. O próximo item da lista de próximos passos do
projeto é justamente repetir o experimento com réplicas.

## 2. Metodologia de modelagem técnica e econômica

Toda a lógica de cálculo está em `src/models.py`, com cada constante rotulada por proveniência
(Medido / Calculado / Externo / Premissa de projeto — ver `data/README.md` para a legenda completa).
Não há ajuste de curva nem regressão estatística nesta parte: é um modelo determinístico de balanço
de massa e energia, escalado linearmente a partir das razões observadas em bancada
(`calculate_ethanol_production_custom`, `calculate_cost_from_balance`).

**Ressalva de escala, explícita no código:** a extrapolação linear preserva o balanço de massa por
definição, mas assume implicitamente que a eficiência de cada etapa (filtração, fermentação,
destilação) não muda com a escala — isso não foi verificado experimentalmente nem confirmado na
literatura consultada para esta rota específica (lactase + *S. cerevisiae*).

Três cenários técnicos fixos (teor alcoólico do destilado, nunca medido — premissa de projeto baseada
na faixa esperada pelo próprio relatório, seção 4.6):

| Cenário | Teor alcoólico assumido |
|---|---|
| Conservador | 5% v/v |
| Experimental | 8,5% v/v (ponto médio) |
| Otimista | 12% v/v |

## 3. Metodologia estatística

Duas análises com componente estatístico, ambas em `notebooks/05_sensitivity_analysis.ipynb`, usando
o volume de referência `VOLUME_REF_L = 10.000 L` de soro e o cenário técnico "experimental":

### 3.1 Análise de sensibilidade (one-at-a-time / tornado)

Método determinístico (não é uma simulação estatística): cada parâmetro de custo é variado
isoladamente, mantendo os demais no valor base, e o resultado operacional (receita − custo) é
recalculado a cada variação (`src/models.py::sensitivity_analysis`).

- Preço do etanol e tarifa de energia: multiplicadores **0,70 / 1,00 / 1,30** (±30%, faixa escolhida
  para refletir a volatilidade semanal observada no indicador CEPEA/Esalq — referência E12).
- Preço de lactase e de fermento (varejo): multiplicadores **0,50 / 1,00 / 2,00** (faixa mais larga,
  porque não há fonte institucional de preço industrial — ver `data/README.md`, item 2).
- Rendimento (teor alcoólico): testado separadamente como um cenário técnico "experimental −20%"
  (não é um parâmetro de `CostParams`, por isso não entra no laço one-at-a-time).

Não há teste de hipótese nem nível de significância (α) aqui — é uma varredura determinística de
parâmetros, não uma inferência sobre uma distribuição amostral. O produto é o gráfico tornado
(`assets/figures/fig_tornado_sensibilidade.png`), que ordena os parâmetros pela amplitude de impacto
no resultado operacional.

### 3.2 Simulação de Monte Carlo (incerteza do preço do etanol)

- **Função:** `src/models.py::monte_carlo_simulation`.
- **N = 2.000 simulações.**
- **Distribuição:** preço do etanol ~ Uniforme(R$ 1,80; R$ 3,40) — faixa escolhida a partir da
  volatilidade observada no indicador CEPEA/Esalq (referência E12), não uma distribuição normal ou
  ajustada a dados históricos.
- **Semente aleatória (seed):** 42, fixa (`numpy.random.default_rng(random_seed=42)`) — a simulação é
  determinística e reprodutível byte a byte a cada execução do notebook.
- **Por que só este parâmetro:** por decisão explícita registrada no código-fonte
  (`monte_carlo_simulation.__doc__`), Monte Carlo só é usado para incertezas com base empírica
  conhecida (a volatilidade do preço do etanol é observável no CEPEA). Os demais parâmetros incertos
  do modelo (preço industrial de lactase, teor alcoólico real) **não têm distribuição de
  probabilidade conhecida** — modelá-los como aleatórios seria inventar uma precisão que os dados não
  sustentam. Por isso são tratados como cenários discretos (conservador/experimental/otimista), não
  como variáveis aleatórias.
- **Saída:** distribuição da receita simulada (`assets/figures/fig_montecarlo_receita.png`);
  estatística descritiva via `mc["receita_R$"].describe()` no próprio notebook.

**Software e versões usadas para gerar os resultados e figuras** (ver `requirements.txt` para os
mínimos declarados; versões efetivamente usadas nesta execução):

| Pacote | Versão |
|---|---|
| Python | 3.14.4 |
| pandas | 3.0.3 |
| numpy | 2.5.0 |
| matplotlib | 3.11.0 |

## 4. Limitações declaradas (resumo — lista completa no notebook 06 e na aba Metodologia do site)

1. Teor alcoólico e densidade do destilado nunca foram medidos — é a maior fonte de incerteza do
   modelo técnico inteiro.
2. Preço de lactase e fermento é de varejo/farmácia, não de insumo industrial a granel — tende a
   **superestimar** o custo real.
3. A literatura de comparação (E08–E10) usa uma rota biológica diferente (*Kluyveromyces* fermentando
   lactose diretamente) da usada neste projeto (lactase + *S. cerevisiae*); serve como teto técnico
   comparativo, não como validação direta.
4. Execução única, sem réplicas nem ensaio controle — nenhuma afirmação sobre variância ou
   reprodutibilidade do resultado experimental é sustentada pelos dados atuais.
5. O modelo econômico é de custo variável apenas — não inclui CAPEX, custo do soro, mão de obra nem
   retificação do destilado até a concentração de combustível (~92–96 GL).
