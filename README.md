# Bioetanol a partir do soro de leite — pesquisa técnica e econômica

Feira de Ciências — Colégio IMP / Laboratório G-Óleo (UFLA), Lavras-MG, 2026.

Esta pasta contém duas fases do mesmo projeto:

- **Fase 1 — pesquisa** (`notebooks/`): a modelagem técnica e econômica completa em Jupyter.
- **Fase 2 — site** (`app/`): uma aplicação Streamlit visual e interativa para apresentar o projeto na
  feira — home, experimento (com fotos reais), resultados (gráficos interativos), simulador ao vivo e
  metodologia/fontes. O site **reutiliza `src/models.py` sem duplicar nenhuma fórmula**.

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

## Estrutura

```
data/
  raw/dados_experimentais.csv     - dados MEDIDOS no experimento (extraídos do relatório)
  external/dados_externos.csv     - dados de fontes externas, com URL/data/confiabilidade
  README.md                       - lacunas de dados conhecidas e decisões tomadas
notebooks/
  01_data_audit.ipynb             - auditoria dos dados experimentais
  02_external_data.ipynb          - dados externos (laticínios, bioetanol, economia)
  03_technical_model.ipynb        - modelo técnico (cenários, escala, comparação com teórico/literatura)
  04_economic_model.ipynb         - modelo econômico (custo, receita)
  05_sensitivity_analysis.ipynb   - análise de sensibilidade + Monte Carlo (preço do etanol)
  06_final_results.ipynb          - consolidação e conclusão final
src/
  models.py                       - toda a lógica de cálculo, reutilizável (notebooks E site)
app/
  Home.py                         - página inicial do site
  pages/                          - Experimento, Resultados, Simulador, Metodologia e Fontes
  utils/styling.py                - paleta, tipografia e componentes visuais (dataviz skill)
  utils/data.py                   - ponte entre o site e src/models.py + gráficos Plotly
assets/photos/                    - fotos reais do experimento (extraídas do relatório .docx)
reports/figures/                  - gráficos estáticos exportados pelos notebooks (PNG)
```

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
