# Bioetanol a partir do soro de leite — pesquisa técnica e econômica

Feira de Ciências — Colégio IMP / Laboratório G-Óleo (UFLA), Lavras-MG, 2026.

> **Vai rodar o site em outro computador?** Siga o [`SETUP.md`](SETUP.md) — passo a passo do zero
> (instalar Git/Python, clonar, rodar), sem precisar já conhecer o projeto.

Esta pasta contém quatro fases do mesmo projeto:

- **Fase 1 — pesquisa** (`notebooks/`): a modelagem técnica e econômica completa em Jupyter.
- **Fase 2 — site Streamlit** (`app/`): uma aplicação Streamlit visual e interativa para apresentar o
  projeto na feira — home, experimento (com fotos reais), resultados (gráficos interativos), simulador
  ao vivo e metodologia/fontes. Reutiliza `src/models.py` sem duplicar nenhuma fórmula.
- **Fase 3 — chat com IA local** (`webapp/`): um site com chat de IA (Ollama, 100% local/offline, sem
  custo) que responde perguntas de visitantes com base na base de conhecimento gerada a partir de
  `data/` e `src/models.py`. Ver `webapp/README.md`.
- **Fase 4 — site interativo final** (`index.html` + `assets/`, na raiz do repositório — é o "site
  publicado" deste repositório): visão geral, simulador com gráficos ao vivo, molécula 3D de etanol
  (Three.js, dados reais do PubChem), mapa do Brasil por produção de leite (Embrapa/IBGE) e um chatbot
  embutido (SoroBot/Botpress). 100% estático, sem dependência de servidor Python além de um serviço de
  arquivos simples — ver `server.py`. Publicado via GitHub Pages (link no topo deste README).

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

**Notebooks da pesquisa:**

```bash
jupyter notebook notebooks/
```

Execute os notebooks em ordem (01 → 06). Cada um é independentemente reprodutível: importam apenas
`src/models.py` e os CSVs em `data/`, sem depender de estado deixado por outro notebook.

**Site (Streamlit), rodar a partir da raiz do projeto:**

```bash
streamlit run app/Home.py
```

Abre em `http://localhost:8501`. Para exibir na feira, deixe em tela cheia no navegador (F11).

**Site final da feira (Fase 4), rodar a partir da raiz do repositório:**

```bash
python server.py
```

Abre em `http://localhost:8000`. Nenhum cálculo do site usa IA (simulador, mapa e balanço de massa
rodam em JavaScript puro, espelhando `src/models.py`) — só a aba "SoroBot" carrega um chatbot externo
(Botpress) e precisa de internet; o resto funciona 100% offline.

**Chat com IA local (Fase 3), rodar a partir de `webapp/`:** ver `webapp/README.md` (requer Ollama
instalado).

## Estrutura

```
index.html                        - site publicado (Fase 4) — abre com server.py ou GitHub Pages
server.py                         - servidor local do site (só serve arquivos estáticos)
assets/
  css/style.css                   - tema visual do site (paleta violeta, dataviz skill)
  js/                              - motor de cálculo do site (espelha src/models.py) + simulador +
                                     mapa + molécula 3D + referências
  vendor/                         - bibliotecas vendorizadas (Chart.js, Three.js, mapa SVG do Brasil)
  photos/                         - fotos reais do experimento (extraídas do relatório .docx)
  figures/                        - gráficos estáticos exportados pelos notebooks (PNG)
data/
  raw/dados_experimentais.csv     - dados MEDIDOS no experimento (extraídos do relatório)
  external/dados_externos.csv     - dados de fontes externas, com URL/data/confiabilidade
  processed/                      - tabelas derivadas usadas nos gráficos (ver processed/README.md)
  README.md                       - lacunas de dados conhecidas e decisões tomadas
notebooks/
  01_data_audit.ipynb             - auditoria dos dados experimentais
  02_external_data.ipynb          - dados externos (laticínios, bioetanol, economia)
  03_technical_model.ipynb        - modelo técnico (cenários, escala, comparação com teórico/literatura)
  04_economic_model.ipynb         - modelo econômico (custo, receita)
  05_sensitivity_analysis.ipynb   - análise de sensibilidade + Monte Carlo (preço do etanol)
  06_final_results.ipynb          - consolidação e conclusão final
src/
  models.py                       - toda a lógica de cálculo, reutilizável (notebooks, app/, webapp/ e
                                     fonte da porta em JavaScript usada pelo site)
docs/
  metodologia.md                  - metodologia experimental e estatística por extenso
  referencias-ABNT.md             - bibliografia no padrão ABNT NBR 6023
  relatorio-original.docx         - relatório completo do projeto (fonte de todos os dados brutos)
app/                               - Fase 2: site Streamlit (ver corpo deste README)
  Home.py                         - página inicial do site
  pages/                          - Experimento, Resultados, Simulador, Metodologia e Fontes
  utils/styling.py                - paleta, tipografia e componentes visuais (dataviz skill)
  utils/data.py                   - ponte entre o site e src/models.py + gráficos Plotly
webapp/                           - Fase 3: chat com IA local (Ollama), ver webapp/README.md
LICENSE                           - MIT (código) + CC BY 4.0 (dados/texto/figuras) — ver seção de licença
CITATION.cff                      - como citar este projeto
```

`app/` e `webapp/` são fases anteriores do projeto (mantidas por completude e porque ainda funcionam
de forma independente); a estrutura `/analysis` sugerida por guias genéricos de pesquisa reprodutível
é cumprida aqui por `notebooks/` + `src/` juntos — não foram renomeados para não quebrar os imports
relativos já usados por `app/`, `webapp/` e pelos próprios notebooks.

## Princípio seguido em toda a pesquisa

Todo número usado é rotulado como **Medido**, **Calculado**, **Externo** ou **Premissa de projeto** —
nunca uma suposição silenciosa. `data/README.md` documenta as lacunas conhecidas (a mais importante:
o teor alcoólico do destilado nunca foi medido no experimento; os notebooks usam a faixa que o próprio
relatório do projeto já esperava, 5–12% v/v, como premissa explícita, não como medição).

## Principal achado (resumo — ver notebook 06 para a versão completa)

- A rota química funciona: o experimento produziu um destilado inflamável a partir de um resíduo
  agroindustrial, com evidências convergentes de etanol.
- Nas condições testadas, o processo está **muito distante do equilíbrio econômico** — e essa distância
  se mantém mesmo isolando apenas o custo de energia (calculado por física, não por preço de mercado
  de insumo) contra a receita ao preço real do etanol: seria necessário um teor alcoólico de ~41% v/v
  só para cobrir a energia, bem acima da faixa de 5–12% esperada pelo projeto.
- A direção mais promissora não é negociar preço de insumo, e sim reduzir a diluição do processo
  (aumentar a concentração final de etanol) — algo que este projeto não testou.
- A conclusão de viabilidade industrial não pode ser afirmada nem descartada com os dados atuais;
  as lacunas que mais mudariam essa resposta estão listadas no notebook 06.
