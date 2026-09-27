# Referências (ABNT NBR 6023)

Bibliografia completa das fontes externas usadas no projeto, no padrão ABNT NBR 6023. O identificador
entre colchetes (`[E01]` etc.) é o mesmo usado em `data/external/dados_externos.csv`, na aba
"Referências" do site e em `src/models.py` — use-o para rastrear qual referência sustenta qual número.
Fontes que aparecem várias vezes (ex. E01–E06, mesmo artigo) estão consolidadas em uma única entrada
bibliográfica, citada mais de uma vez no texto.

Dados classificados como **Medido** ou **Calculado** (produzidos pelo próprio projeto) não têm entrada
aqui — só entram fontes **Externas**. Ver `data/README.md` para a legenda completa de proveniência.

## Laticínios — composição e volume do soro

**[E01, E02, E03, E04, E05]** PAULA, J. C. J. et al. **Adequabilidade de diferentes tipos de soros de
leite para o aproveitamento em produtos lácteos**. Juiz de Fora: EPAMIG/ILCT, 2017. Disponível em:
<https://www.epamig.br/ilct/wp-content/uploads/2020/07/ARTIGO-ADEQUABILIDADE-DE-DIFERENTES-TIPOS-DE-SORO.pdf>.
Acesso em: 2026.

**[E06]** MILKPOINT; EPAMIG/ILCT. **Soro do queijo: resíduo ou matéria-prima?** [S. l.], [19--?].
Disponível em: <https://www.milkpoint.com.br/colunas/ilctepamig/soro-do-queijo-residuo-ou-materiaprima-233910/>.
Acesso em: 2026.

## Bioetanol — rendimento de fermentação

**[E07]** Cálculo estequiométrico próprio do projeto (Gay-Lussac estendido: lactose + H₂O → 2 hexoses
→ 4 etanol + 4 CO₂), a partir de massas molares tabeladas (lactose 342,3 g/mol; etanol 46,07 g/mol).
Não é uma citação de terceiros — ver `src/models.py`, constantes `MOLAR_MASS_LACTOSE` e
`MOLAR_MASS_ETHANOL`.

**[E08, E09]** Síntese de múltiplos estudos de fermentação de soro/lactose por *Kluyveromyces* spp.,
2010–2023. Disponível em: <https://pmc.ncbi.nlm.nih.gov/articles/PMC6920800/> e
<https://pmc.ncbi.nlm.nih.gov/articles/PMC6312371/>. Acesso em: 2026. Nota: rota biológica diferente
da usada neste projeto (*Kluyveromyces* fermenta lactose diretamente; aqui usa-se lactase +
*Saccharomyces cerevisiae*) — serve como teto técnico comparativo, não validação direta.

**[E10]** Estudos de fermentação de soro de queijo por *Kluyveromyces* spp., 2018–2019. Disponível
em: <https://pmc.ncbi.nlm.nih.gov/articles/PMC6312371/>. Acesso em: 2026.

**[E11]** SANSONETTI, S.; CURCIO, S.; CALABRÒ, V.; IORIO, G. Bio-ethanol production by fermentation of
ricotta cheese whey as an effective alternative non-vegetable source. **Biomass & Bioenergy**, v. 33,
n. 12, p. 1687-1692, 2009. DOI: 10.1016/j.biombioe.2009.09.002. Nota: texto completo bloqueado por
paywall — apenas o registro bibliográfico foi confirmado; valores numéricos não usados no modelo.

**[E19]** O'LEARY, V. S.; GREEN, R.; SULLIVAN, B. C.; HOLSINGER, V. H. Alcohol production by selected
yeast strains in lactase-hydrolyzed acid whey. **Biotechnology and Bioengineering**, v. 19, p.
1019-1035, 1977. Disponível em:
<https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/abs/10.1002/bit.260190706>. Acesso em:
2026. Nota: apenas o resumo foi acessado (paywall); valor de rendimento citado não confirmado no
texto completo.

**[E20]** ESTADOS UNIDOS. United States Department of Agriculture (USDA), Rural Business and
Cooperative Programs. **Research Report 214: Whey to Ethanol**. [19--?]. Disponível em:
<https://www.govinfo.gov/content/pkg/GOVPUB-A109-PURL-LPS110273/pdf/GOVPUB-A109-PURL-LPS110273.pdf>.
Acesso em: 2026. Nota: PDF escaneado sem camada de texto; identificado como referência para leitura
manual futura, valores não usados no modelo.

## Economia — preços e tarifas

**[E12, E13]** CEPEA/ESALQ — Centro de Estudos Avançados em Economia Aplicada, Universidade de São
Paulo. **Indicador do Etanol**. Piracicaba, 2026. Disponível em:
<https://cepea.org.br/br/indicador/etanol.aspx>. Acesso em: 18 set. 2026. Nota: preço de usina em São
Paulo, semana de 14–18/09/2026; não inclui frete/tributos para outras regiões.

**[E14, E15]** AGÊNCIA FAPESP. **Etanol de segunda geração poderá ser economicamente viável a partir
de 2025**. São Paulo, 28 set. 2017. Disponível em:
<https://agencia.fapesp.br/etanol-de-segunda-geracao-podera-ser-economicamente-viavel-a-partir-de-2025/26272>.
Acesso em: 2026. Nota: refere-se a etanol de cana (1G) e etanol 2G lignocelulósico — processos
distintos do deste projeto; usado apenas como ordem de grandeza.

**[E16]** CEMIG — Companhia Energética de Minas Gerais. **Tarifas vigentes**. Belo Horizonte, 2026.
Disponível em: <https://www.cemig.com.br/valores-e-tarifas/tarifas-vigentes/>. Acesso em: 24 set.
2026.

**[E17, E18]** Dado primário do próprio relatório do projeto (compra direta em farmácia e comércio
local, Lavras-MG, set. 2026) — ver `docs/relatorio-original.docx`, seção 3.6.

**[E21]** ENZYMES.BIO; fornecedores B2B diversos (marketplace indiano). **Cotações comerciais de
lactase grau alimentício a granel**. [S. l.], 2026. Disponível em:
<https://enzymes.bio/product/food-grade-lactase-liquid/>. Acesso em: set. 2026. Nota: cotação online
de fornecedor B2B, não é preço confirmado por compra real nem fonte institucional/acadêmica —
confiabilidade baixa/média.
