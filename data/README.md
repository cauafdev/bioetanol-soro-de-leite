# Dados do projeto — Bioetanol a partir do soro de leite

## Estrutura

- `raw/dados_experimentais.csv` — todos os dados do experimento realizado no Laboratório G-Óleo (UFLA), extraídos do relatório do projeto. Cada linha tem `tipo` = Medido, Calculado ou FALTANTE.
- `external/dados_externos.csv` — dados de fontes externas (artigos científicos, EPAMIG, CEPEA, CTBE/CNPEM, CEMIG), com URL, data, região, metodologia e nível de confiabilidade de cada um.

## Lacunas críticas conhecidas (não inventar valores para preenchê-las)

1. **Teor alcoólico / densidade do destilado — não medido no experimento.**
   Decisão adotada (a pedido do responsável pelo projeto): usar a faixa **esperada pelo próprio projeto, 5%–12% v/v pré-retificação** (relatório, seção 4.6), tratada como *premissa de projeto*, não como dado medido. Cenários técnicos (conservador/experimental/otimista) devem herdar essa faixa.

2. **Preço industrial de lactase e de levedura — não encontrado em fonte institucional.**
   Só temos preço de varejo/farmácia (dados E17/E18, vindos do próprio relatório). Isso tende a **sobrestimar** o custo de insumos em escala industrial (preço de varejo é normalmente maior que preço a granel). Deve ser tratado como premissa conservadora explícita no modelo econômico, não como preço de mercado industrial real. Encontramos cotações comerciais online de lactase a granel (E21, US$240–420/kg) — não são preço confirmado por compra real nem fonte institucional (confiabilidade Baixa/Média), mas mesmo assim são uma fração do preço de varejo usado no modelo, o que reforça que o custo de insumo do projeto provavelmente está superestimado.

3. **Rendimento de fermentação da rota específica do projeto (lactase + *Saccharomyces cerevisiae*) — literatura direta limitada.**
   A maior parte da literatura sobre etanol de soro de leite usa *Kluyveromyces marxianus/lactis*, que fermenta a lactose diretamente, sem hidrólise prévia — uma rota biológica diferente da adotada neste projeto. Os valores de eficiência de fermentação da literatura (E08–E10) servem como **teto técnico comparativo**, não como validação direta da rota do projeto. Encontramos uma referência mais próxima (E19, O'Leary et al. 1977, USDA) que usa lactase para hidrolisar a lactose antes da fermentação — mas apenas o resumo foi acessado (paywall), e ele aponta um limite biológico adicional: *Saccharomyces cerevisiae* pode não fermentar bem a galactose liberada pela hidrólise (metade do açúcar disponível), o que não foi verificado no experimento deste projeto.

4. **Sansonetti et al. (2009) — "Bio-ethanol production by fermentation of ricotta cheese whey".**
   É a referência mais próxima do processo do projeto (soro desproteinado → etanol), mas o texto completo está bloqueado por paywall/captcha. Apenas o registro bibliográfico foi confirmado (E11); os valores numéricos do artigo **não foram usados** porque não puderam ser verificados.

5. **Concentração de lactose no soro usado no experimento — não medida.**
   Usaremos a composição média de literatura (E03, ~4,9% m/m ≈ 49 g/L) como proxy, deixando explícito que não é uma medição do soro específico usado no laboratório G-Óleo.
