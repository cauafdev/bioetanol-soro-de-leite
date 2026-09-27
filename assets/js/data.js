/* Referências externas — extraídas de data/external/dados_externos.csv.
   Cada objeto espelha uma linha da planilha; nao inventar/editar valores
   aqui sem atualizar o CSV de origem correspondente. */

const REFERENCES = {
  "Laticínios — composição e volume do soro": [
    {
      id: "E01",
      titulo: "Adequabilidade de diferentes tipos de soros de leite para o aproveitamento em produtos lácteos",
      autor: "Paula, J.C.J. et al. — EPAMIG-ILCT (citando Walstra 2006)",
      url: "https://www.epamig.br/ilct/wp-content/uploads/2020/07/ARTIGO-ADEQUABILIDADE-DE-DIFERENTES-TIPOS-DE-SORO.pdf",
      dado: "7–9 L de soro por kg de queijo produzido",
      confiabilidade: "alta",
      nota: "Valor consolidado na literatura de laticínios; não é específico de Lavras/MG."
    },
    {
      id: "E02",
      titulo: "Adequabilidade de diferentes tipos de soros de leite (idem, citando González Sisó 1996; Atra et al. 2005)",
      autor: "Paula, J.C.J. et al. — EPAMIG-ILCT",
      url: "https://www.epamig.br/ilct/wp-content/uploads/2020/07/ARTIGO-ADEQUABILIDADE-DE-DIFERENTES-TIPOS-DE-SORO.pdf",
      dado: "85–90% do volume do leite vira soro no processo de fabricação do queijo",
      confiabilidade: "alta",
      nota: "Corrobora a faixa de 80–90% já citada na introdução do relatório do próprio projeto."
    },
    {
      id: "E03",
      titulo: "Adequabilidade de diferentes tipos de soros de leite — Tabela 2 (adaptado de Mello 1989; Fox 1997; Walstra et al. 2006)",
      autor: "Paula, J.C.J. et al. — EPAMIG-ILCT",
      url: "https://www.epamig.br/ilct/wp-content/uploads/2020/07/ARTIGO-ADEQUABILIDADE-DE-DIFERENTES-TIPOS-DE-SORO.pdf",
      dado: "Concentração de lactose no soro: 4,9% m/m (~49 g/L) — usado no simulador",
      confiabilidade: "alta",
      nota: "Assume densidade ~1 g/mL para converter %m/m em g/L; não é medição do soro usado neste projeto."
    },
    {
      id: "E05",
      titulo: "Adequabilidade de diferentes tipos de soros de leite (citando Pelegrine e Carrasqueira 2008; Giraldo-Zúñiga et al. 2002)",
      autor: "Paula, J.C.J. et al. — EPAMIG-ILCT",
      url: "https://www.epamig.br/ilct/wp-content/uploads/2020/07/ARTIGO-ADEQUABILIDADE-DE-DIFERENTES-TIPOS-DE-SORO.pdf",
      dado: "DBO do soro: 25.000–120.000 mg/L",
      confiabilidade: "alta",
      nota: "Usado apenas como referência do impacto ambiental do descarte — não entra no modelo econômico."
    }
  ],
  "Bioetanol — rendimento de fermentação": [
    {
      id: "E07",
      titulo: "Rendimento teórico estequiométrico (cálculo próprio)",
      autor: "Gay-Lussac estendido: lactose + H₂O → 2 hexoses → 4 etanol + 4 CO₂",
      url: null,
      dado: "0,538 g de etanol por g de lactose",
      confiabilidade: "alta",
      nota: "Resultado CALCULADO a partir de massas molares (lactose 342,3 g/mol; etanol 46,07 g/mol) — não é uma citação de terceiros."
    },
    {
      id: "E08 / E09",
      titulo: "Síntese de múltiplos estudos sobre fermentação de soro/lactose por Kluyveromyces spp.",
      autor: "Vários autores, 2010–2023",
      url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC6920800/",
      dado: "Eficiência de fermentação industrial: 80–97% do rendimento teórico",
      confiabilidade: "media",
      nota: "Rota biológica DIFERENTE da usada no projeto (Kluyveromyces fermenta lactose direto; aqui usa-se lactase + Saccharomyces cerevisiae). Serve como teto técnico comparativo, não validação direta. Acesso apenas a resumos indexados."
    },
    {
      id: "E10",
      titulo: "Estudos de fermentação de soro de queijo por Kluyveromyces spp.",
      autor: "Vários autores, 2018–2019",
      url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC6312371/",
      dado: "Concentração de etanol no mosto: 11,7–24,85 g/L",
      confiabilidade: "media",
      nota: "Concentração no MOSTO (não no destilado); usada apenas como referência comparativa."
    },
    {
      id: "E11",
      titulo: "Bio-ethanol production by fermentation of ricotta cheese whey as an effective alternative non-vegetable source",
      autor: "Sansonetti, S.; Curcio, S.; Calabrò, V.; Iorio, G. — Biomass & Bioenergy, v.33",
      url: "https://doi.org/10.1016/j.biombioe.2009.09.002",
      dado: "Referência mais próxima do processo do projeto (soro desproteinado → etanol)",
      confiabilidade: "baixa",
      nota: "NÃO VERIFICÁVEL — bloqueado por paywall. Apenas o registro bibliográfico foi confirmado; os valores numéricos do artigo não foram usados no modelo."
    },
    {
      id: "E19",
      titulo: "Alcohol production by selected yeast strains in lactase-hydrolyzed acid whey",
      autor: "O'Leary, V.S.; Green, R.; Sullivan, B.C.; Holsinger, V.H. — Biotechnology and Bioengineering, v.19 (USDA ARS)",
      url: "https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/abs/10.1002/bit.260190706",
      dado: "Referência biológica mais próxima da rota do projeto (usa lactase para hidrolisar antes de fermentar)",
      confiabilidade: "media",
      nota: "Aponta um limite biológico adicional: Saccharomyces cerevisiae pode fermentar mal a galactose liberada pela hidrólise (metade do açúcar disponível) — não verificado no experimento deste projeto. Só o resumo foi acessado (paywall)."
    },
    {
      id: "E20",
      titulo: "Research Report 214: Whey to Ethanol",
      autor: "USDA Rural Business and Cooperative Programs",
      url: "https://www.govinfo.gov/content/pkg/GOVPUB-A109-PURL-LPS110273/pdf/GOVPUB-A109-PURL-LPS110273.pdf",
      dado: "Relatório oficial de viabilidade industrial de plantas de etanol de soro de leite",
      confiabilidade: "baixa",
      nota: "NÃO VERIFICÁVEL — PDF escaneado sem camada de texto, não foi possível extrair os números. Identificado como referência para eventual leitura manual; valores não usados."
    }
  ],
  "Economia — preços e tarifas": [
    {
      id: "E12",
      titulo: "Indicador CEPEA/Esalq — Etanol Hidratado Combustível",
      autor: "CEPEA/Esalq — USP",
      url: "https://cepea.org.br/br/indicador/etanol.aspx",
      dado: "R$ 2,6412 / L (semana de 14–18/09/2026, usinas de SP)",
      confiabilidade: "alta",
      nota: "Preço de usina em SP; não inclui frete/tributos para MG. Alta volatilidade semanal (+7,27% na semana consultada)."
    },
    {
      id: "E14 / E15",
      titulo: "Etanol de segunda geração poderá ser economicamente viável a partir de 2025",
      autor: "Agência FAPESP, citando Antonio Bonomi (CTBE/CNPEM)",
      url: "https://agencia.fapesp.br/etanol-de-segunda-geracao-podera-ser-economicamente-viavel-a-partir-de-2025/26272",
      dado: "Custo de produção de etanol 1G (cana): R$ 1,15/L · custo de enzimas no etanol 2G: 20–40% do custo total",
      confiabilidade: "alta",
      nota: "Refere-se a etanol de CANA (1G) e etanol 2G lignocelulósico (bagaço) — processos distintos do deste projeto. Usado apenas como ordem de grandeza."
    },
    {
      id: "E16",
      titulo: "Tarifas Vigentes — Grupo A4, bandeira verde",
      autor: "CEMIG",
      url: "https://www.cemig.com.br/valores-e-tarifas/tarifas-vigentes/",
      dado: "R$ 0,48077/kWh (fora-ponta) — usado no simulador",
      confiabilidade: "alta",
      nota: "Tarifa binomial (não é um único valor por kWh); não inclui tributos (ICMS/PIS/COFINS)."
    },
    {
      id: "E17 / E18",
      titulo: "Preço de lactase e fermento — dado primário do próprio relatório",
      autor: "Compra direta, Lavras-MG, set/2026",
      url: null,
      dado: "Lactase: R$ 40,00 / caixa de 30 cápsulas · Fermento: R$ 2,50 / pacote",
      confiabilidade: "alta",
      nota: "GAP: preço de VAREJO/farmacêutico, não de insumo industrial a granel — tende a superestimar o custo real em escala."
    },
    {
      id: "E21",
      titulo: "Cotações comerciais de lactase grau alimentício a granel",
      autor: "Fornecedores B2B online (enzymes.bio; marketplace indiano)",
      url: "https://enzymes.bio/product/food-grade-lactase-liquid/",
      dado: "US$ 240–420/kg",
      confiabilidade: "baixa",
      nota: "Cotação online, não é preço confirmado por compra real nem fonte institucional. Ainda assim, é uma fração do preço de varejo usado no modelo (equivalente a ~R$ 3.546/kg) — reforça que o custo de insumo do projeto provavelmente está superestimado."
    }
  ]
};
