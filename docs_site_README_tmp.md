# soro.valor — site final da feira

Site estático (sem IA, sem chave de API) usado na apresentação do projeto **Bioetanol a partir do
soro de leite** — Feira de Ciências, Colégio IMP / Laboratório G-Óleo (UFLA), Lavras-MG.

## Rodar

```bash
cd site
python server.py
```

Abre em `http://localhost:8000`.

## O que tem em cada aba

- **Visão geral** — a molécula 3D de etanol (Three.js, coordenadas atômicas reais do PubChem/NIH),
  os 4 passos do processo e as evidências de que a rota química funcionou.
- **Simulador** — ajuste o volume de soro e o cenário técnico, e veja o balanço de massa e o resultado
  econômico recalculados em tempo real, com gráfico de produção/economia (Chart.js).
- **Resultados** — o que os dados sustentam e o que não sustentam, direto da conclusão da pesquisa.
- **Metodologia** — proveniência de cada parâmetro (Medido / Calculado / Externo / Premissa) e as
  lacunas conhecidas do modelo.
- **Referências** — bibliografia completa das fontes externas usadas.
- **Mapa do Brasil** — produção de leite por estado (Embrapa/IBGE, 2019) e o potencial teórico de
  bioetanol de cada estado, calculado com o mesmo modelo do Simulador.
- **SoroBot (IA)** — chatbot (Botpress) embutido por iframe. É a única parte do site que depende de
  internet; todo o resto funciona 100% offline.

## Por que não usa IA para os números

Todo cálculo (simulador, mapa, balanço de massa) roda no navegador em JavaScript puro
(`app.js`, `map.js`), portando fielmente as mesmas fórmulas de `../src/models.py` — o mesmo módulo
usado pelos notebooks de pesquisa e pelo site Streamlit (`../app/`). Isso foi verificado rodando os
dois lados lado a lado e comparando a saída número a número (ver histórico do projeto). Nenhum dado
é gerado por um modelo de linguagem.

## Estrutura

```
index.html          - marcação das 7 abas
style.css            - tema visual (paleta violeta, já validada no skill de dataviz)
app.js               - motor de cálculo (espelha src/models.py) + simulador + gráficos
data.js              - referências bibliográficas estruturadas
map-data.js          - produção de leite por estado (dado real, Embrapa/IBGE 2019)
map.js               - mapa SVG interativo (coloração por produção, hover com potencial calculado)
molecule-data.js     - coordenadas atômicas reais do etanol (PubChem CID 702)
molecule.js          - visualizador 3D (Three.js) do etanol, arrastável/zoom
server.py            - servidor Flask local, só serve os arquivos estáticos
vendor/              - bibliotecas vendorizadas (Chart.js, Three.js, OrbitControls, mapa SVG do Brasil)
```

## Fontes de dados externas usadas

- Produção de leite por estado: Embrapa Gado de Leite, "Anuário Leite — Análise Brasil" (dados IBGE 2019).
- Mapa do Brasil (SVG): Wikimedia Commons, domínio público (CC0).
- Estrutura 3D do etanol: PubChem/NIH, CID 702.
- Demais fontes (preço do etanol, tarifa de energia, literatura de fermentação): ver aba Referências
  e `../data/external/dados_externos.csv`.
