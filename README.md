# Produção de bioetanol a partir do soro de leite

**Aproveitamento energético de um resíduo da indústria de laticínios**

| | |
|---|---|
| **Autores** | Cauã Lara Fernando, Giovanni Marques Ferreira, Otávio Zanquini de Souza |
| **Professor orientador** | André Luiz de Paiva Godinho (Colégio IMP) |
| **Coorientadoras** | Fernanda Neves Miranda (Engenharia de Materiais, UFLA); Ana Alice Normandia de Lacerda (Engenharia Química, UFLA) |
| **Instituições** | Colégio IMP, Lavras-MG; Laboratório G-Óleo, Universidade Federal de Lavras (UFLA) |
| **Área do conhecimento** | Química — Ensino Médio (2ª série) |
| **Evento** | III Feira do Conhecimento do Colégio IMP — Arte, Cultura e Ciência, 2026 |
| **Período do projeto** | 01/06/2026 a 25/09/2026 |

> **Vai rodar o site em outro computador?** Siga o [`SETUP.md`](SETUP.md) — passo a passo do zero
> (instalar Git/Python, clonar, rodar), sem precisar já conhecer o projeto.

---

## Resumo

Este projeto de iniciação científica investiga a viabilidade técnica e econômica da produção de
bioetanol a partir do soro de leite, resíduo abundante da indústria de laticínios. Em escala de
bancada, 250 mL de soro cru foram desproteinizados por aquecimento (90–100 °C) e filtração a vácuo,
resultando em 160 mL de filtrado. A lactose presente foi hidrolisada enzimaticamente com lactase em
glicose e galactose, fermentada com *Saccharomyces cerevisiae* (30 °C, 72 h), e o mosto resultante foi
destilado fracionadamente (coleta a 78 °C), produzindo 15 mL de destilado — uma razão **volumétrica**
de 6,0% em relação ao soro original (**não** o teor alcoólico, que não foi medido). Três evidências
convergentes (temperatura de coleta, teste de chama positivo e ausência de coloração na combustão)
confirmam qualitativamente a presença de etanol. A partir desses dados, foi construído um modelo
técnico e econômico em Python (balanço de massa, análise de sensibilidade e Monte Carlo) para projetar
produção e custos em escala. Os resultados indicam que a rota química funciona, mas que, nas condições
de preço testadas — mesmo considerando apenas o custo físico de energia, sem reagentes —, o processo
está muito distante do equilíbrio econômico. A direção mais promissora identificada para viabilidade
futura
é reduzir a diluição do processo (aumentar a concentração final de etanol), não negociar preços de
insumo. Limitações incluem execução experimental única (sem réplicas) e ausência de medição direta do
teor alcoólico do destilado e de preços industriais de insumos.

## Abstract

This undergraduate research project investigates the technical and economic feasibility of producing
bioethanol from cheese whey, an abundant residue often discarded by the dairy industry. At bench
scale, 250 mL of raw whey was deproteinized by heating (90–100 °C) and vacuum filtration, yielding
160 mL of filtrate. The lactose present was enzymatically hydrolyzed with lactase into glucose and
galactose, fermented with *Saccharomyces cerevisiae* (30 °C, 72 h), and the resulting must was
fractionally distilled (collection at 78 °C), producing 15 mL of distillate — a **volumetric** ratio
of 6.0% relative to the original whey (**not** the alcohol content, which was not measured). Three
converging pieces of evidence (collection temperature, a positive flame test, and colorless
combustion) qualitatively confirm the presence of ethanol. From these data, a technical and economic
model was built in Python (mass balance, sensitivity analysis, and Monte Carlo simulation) to project
production and costs across scales and scenarios. Results indicate that the chemical route works, but
under the tested price conditions — even considering only the physical cost of energy, excluding
reagents — the process remains far from economic equilibrium. The most promising direction identified
for future viability is reducing process dilution (increasing final ethanol concentration), rather
than negotiating input prices. Limitations include a single experimental run (no replicates) and the
absence of direct measurement of the distillate's alcohol content and of industrial input prices.

## Objetivo e pergunta de pesquisa

**Objetivo geral:** avaliar se é tecnicamente viável produzir bioetanol a partir do soro de leite por
hidrólise enzimática seguida de fermentação alcoólica, e projetar, a partir dos dados do experimento,
se essa rota poderia ser economicamente viável em escala.

**Pergunta de pesquisa:** *É possível produzir etanol combustível a partir do soro de leite descartado
pela indústria de laticínios, e essa produção se sustenta economicamente sob as condições de custo e
preço atuais?*

A pergunta se desdobra em duas partes independentes, respondidas separadamente neste projeto: (1) a
rota química funciona? (resposta experimental, ver Resultados) e (2) ela se sustenta economicamente?
(resposta por modelagem, sujeita às limitações declaradas na Seção 5 e no notebook 06).

## Metodologia experimental

Execução única (sem réplicas), realizada no Laboratório G-Óleo (UFLA), Lavras-MG, entre 15/09/2026 e
18/09/2026 (fermentação), dentro do período do projeto.

| Etapa | Materiais e condições | Entrada → Saída |
|---|---|---|
| 1. Desproteinização | Soro de leite cru (laticínio local, Lavras-MG), pH inicial 6,0 → acidificado a 4,5–4,6 (ponto isoelétrico das proteínas); aquecimento 90–100 °C, 15–30 min; filtração a vácuo (Büchner) | 250 mL → 160 mL filtrado |
| 2. Hidrólise enzimática | Lactase (4,0047 g; ~106.000 U·FCC), 37–40 °C | Lactose → glicose + galactose |
| 3. Fermentação | *Saccharomyces cerevisiae* seca (4 g), 30 °C, 72 h (15–18/09/2026) | 160 mL mosto fermentado |
| 4. Destilação fracionada | Coleta estabilizada a 78 °C | 15 mL destilado |

**Evidências de identificação do destilado como etanol** (qualitativas/indiretas — teor alcoólico e
densidade nunca foram medidos diretamente): temperatura de coleta ≈78 °C (ponto de ebulição do
etanol), teste de chama positivo (combustão sem coloração visível), e coerência da rota com a
literatura de hidrólise enzimática de lactose seguida de fermentação alcoólica.

Metodologia completa (todas as condições, materiais e quantidades) em
[`docs/metodologia.md`](docs/metodologia.md) — seção 1.

## Metodologia estatística

Modelagem determinística de balanço de massa/energia (sem ajuste estatístico) em `src/models.py`,
mais duas análises com componente estatístico em `notebooks/05_sensitivity_analysis.ipynb` (volume de
referência 10.000 L de soro, cenário "experimental"):

- **Análise de sensibilidade** (one-at-a-time / tornado): preço do etanol e tarifa de energia
  variados em ±30%; preço de lactase e fermento variados 0,5×–2×; rendimento testado separadamente a
  −20%. Método determinístico, sem teste de hipótese nem nível de significância — é uma varredura de
  parâmetros, não uma inferência estatística.
- **Simulação de Monte Carlo**: **n = 2.000 simulações**, preço do etanol amostrado de uma
  distribuição **uniforme(R$ 1,80; R$ 3,40)** (faixa da volatilidade observada no CEPEA/Esalq),
  **semente aleatória fixa (seed = 42)** para reprodutibilidade total.

**Software:** Python 3.14.4, pandas 3.0.3, numpy 2.5.0, matplotlib 3.11.0 (versões efetivamente usadas
nesta execução; mínimos declarados em `requirements.txt`).

Metodologia estatística completa, com a justificativa de por que Monte Carlo só é usado para o preço
do etanol (e não para os demais parâmetros incertos), em [`docs/metodologia.md`](docs/metodologia.md)
— seção 3.

## Principais resultados

- **A rota química funciona**: o experimento produziu um destilado inflamável a partir de um resíduo
  agroindustrial, com três evidências convergentes de etanol.
- Em escala, mantendo as mesmas eficiências de processo, a produção de etanol **escala linearmente**
  com o volume de soro — mas isso é uma extrapolação simples, não uma previsão de desempenho
  industrial real (a eficiência de cada etapa não foi verificada em outras escalas).
- Nas condições de preço testadas, o processo está **muito distante do equilíbrio econômico** — e essa
  distância se mantém mesmo isolando apenas o custo de energia (calculado por física, não por preço de
  mercado de insumo) contra a receita ao preço real do etanol: seria necessário um teor alcoólico de
  ~41% v/v só para cobrir a energia, bem acima da faixa de 5–12% esperada pelo projeto.
- A direção mais promissora não é negociar preço de insumo, e sim reduzir a diluição do processo
  (aumentar a concentração final de etanol) — algo que este projeto não testou.
- A conclusão de viabilidade industrial **não pode ser afirmada nem descartada** com os dados atuais.

**Limitações declaradas** (lista completa no notebook 06 e na aba Metodologia do site):

1. Teor alcoólico e densidade do destilado nunca foram medidos — maior fonte de incerteza do modelo.
2. Preço de lactase e fermento é de varejo/farmácia, não de insumo industrial a granel — tende a
   **superestimar** o custo real.
3. A literatura de comparação usa uma rota biológica diferente (*Kluyveromyces* fermentando lactose
   diretamente) da usada neste projeto (lactase + *S. cerevisiae*).
4. Execução única, sem réplicas nem ensaio controle — nenhuma afirmação sobre variância ou
   reprodutibilidade do resultado experimental é sustentada pelos dados atuais.
5. O modelo econômico é de custo variável apenas — não inclui CAPEX, custo do soro, mão de obra nem
   retificação do destilado até a concentração de combustível (~92–96 GL).

## Como reproduzir

Este repositório contém quatro fases do mesmo projeto:

- **Fase 1 — pesquisa** (`notebooks/` + `src/`): a modelagem técnica e econômica completa em Jupyter.
- **Fase 2 — site Streamlit** (`app/`): aplicação visual/interativa para a feira — home, experimento
  (com fotos reais), resultados, simulador ao vivo e metodologia/fontes. Reutiliza `src/models.py`.
- **Fase 3 — chat com IA local** (`webapp/`): chat (Ollama, 100% local/offline) que responde perguntas
  com base numa base de conhecimento gerada a partir de `data/` e `src/models.py`.
- **Fase 4 — site interativo final** (`index.html` + `assets/`, na raiz): visão geral, simulador,
  molécula 3D de etanol, mapa do Brasil e um chatbot embutido (SoroBot). Ver Seção 8/9 abaixo.

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

**Notebooks da pesquisa** (reexecutam todas as estatísticas e regeram todas as figuras a partir de
`data/raw/` e `data/external/` — nenhum número do site é calculado fora deste pipeline):

```bash
jupyter notebook notebooks/
```

Execute em ordem (01 → 06); cada um é independentemente reprodutível.

**Site Streamlit (Fase 2), a partir da raiz do projeto:**

```bash
streamlit run app/Home.py
```

Abre em `http://localhost:8501`.

**Chat com IA local (Fase 3):** ver [`webapp/README.md`](webapp/README.md) (requer Ollama instalado).

### Estrutura

```
index.html, assets/, server.py     - Fase 4: site publicado (ver Seção 8)
data/raw/, data/external/          - dados brutos e externos (ver data/README.md)
data/processed/                    - ver data/processed/README.md (hoje vazia por design)
notebooks/, src/                   - Fase 1: pesquisa (cumprem juntos o papel de "/analysis")
docs/                              - metodologia.md, referencias-ABNT.md, relatorio-original.docx
app/                               - Fase 2: site Streamlit
webapp/                            - Fase 3: chat com IA local
LICENSE, CITATION.cff              - ver Seções 10 e 12
```

`app/` e `webapp/` são fases anteriores do projeto, mantidas por completude — não fazem parte do
"site publicado" (Fase 4), mas continuam funcionando de forma independente.

## Como visualizar o site

**Localmente**, a partir da raiz do repositório:

```bash
python server.py
```

Abre em `http://localhost:8000`. Nenhum cálculo do site usa IA — simulador, mapa e balanço de massa
rodam em JavaScript puro (`assets/js/`), espelhando `src/models.py`; só a aba "SoroBot" carrega um
chatbot externo e precisa de internet (ver Seção 9).

**Publicado:** via GitHub Pages, a partir da branch `main` deste repositório (a ativar como parte da
Etapa 5 de organização — ver `github.com/cauafdev/bioetanol-soro-de-leite/settings/pages`). Assim que
ativado, o link será `https://cauafdev.github.io/bioetanol-soro-de-leite/`.

## Assistente de IA

O site publicado (Fase 4) e o site Streamlit (Fase 2) embutem o **SoroBot**, um chatbot construído na
plataforma Botpress. Sua base de conhecimento é gerada a partir dos mesmos dados deste repositório
(`data/`, `docs/metodologia.md`, `docs/referencias-ABNT.md`) — não inclui conhecimento externo não
verificado pelo projeto. Separadamente, a Fase 3 (`webapp/`) roda um chat equivalente 100% local via
Ollama, sem depender de serviço externo.

**Aviso, válido para ambos:** as respostas do SoroBot são geradas por um modelo de linguagem e **podem
conter imprecisões**, mesmo alimentado por dados corretos. Em caso de dúvida sobre qualquer número ou
afirmação, verifique diretamente em `data/`, `docs/metodologia.md` ou na aba Metodologia do site — que
são a fonte da verdade, não o chatbot.

## Como citar

Ver [`CITATION.cff`](CITATION.cff) (formato Citation File Format, validado contra o schema oficial
1.2.0). Exemplo em texto corrido (ABNT):

> FERNANDO, Cauã Lara; FERREIRA, Giovanni Marques; SOUZA, Otávio Zanquini de. **Produção de bioetanol
> a partir do soro de leite: aproveitamento energético de um resíduo da indústria de laticínios**.
> Orientação de André Luiz de Paiva Godinho. Lavras: Colégio IMP, 2026. Disponível em:
> <https://github.com/cauafdev/bioetanol-soro-de-leite>. Acesso em: [data de acesso].

## Referências

Bibliografia completa, no padrão ABNT NBR 6023, em [`docs/referencias-ABNT.md`](docs/referencias-ABNT.md).
Cada referência carrega um identificador (`E01`–`E21`) rastreável até `data/external/dados_externos.csv`
e até a aba "Referências" do site publicado — nenhuma delas foi citada sem checar o que de fato
sustenta (nível de confiabilidade e ressalvas explícitas em cada entrada).

## Licença e contato

- **Código** (notebooks, `src/`, `app/`, `webapp/`, site): MIT — ver [`LICENSE`](LICENSE).
- **Dados, textos e figuras** (`data/`, `docs/`, `assets/figures/`, `assets/photos/`): Creative Commons
  Attribution 4.0 International (CC BY 4.0) — ver detalhes no próprio [`LICENSE`](LICENSE).

**Contato:**

- Colégio IMP — Rua Gustavo Pena, 57, Centro, Lavras-MG, CEP 37200-001 — (35) 3826-1233 /
  (35) 99705-1507 — [colegioimp.com.br](https://colegioimp.com.br)
- Dúvidas técnicas sobre o repositório: abra uma *issue* em
  `github.com/cauafdev/bioetanol-soro-de-leite/issues`.
