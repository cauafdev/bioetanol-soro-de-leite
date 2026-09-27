/* ==========================================================================
   Producao de leite por estado — dado EXTERNO real (nao inventado).

   Fonte: Embrapa Gado de Leite — "Anuario Leite: Analise Brasil" —
   TABELA 1 "Producao de leite nos estados", dados de 2019, apurados pelo
   IBGE (Pesquisa da Pecuaria Municipal / Pesquisa Trimestral do Leite).
   https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1134836/1/Distribuicao-producao-leite.pdf

   E' o ano mais recente para o qual encontramos a tabela COMPLETA com os 27
   estados (noticias de 2023 trazem apenas os 3 maiores estados isolados,
   sem a tabela completa) — por isso usamos 2019 aqui, com a data marcada
   explicitamente na UI. A producao nacional total nao mudou muito desde
   entao (34,8 bilhoes de L em 2019 vs. 35,4 bilhoes em 2023), entao a
   distribuicao geografica relativa deve seguir proxima da atual.

   valor_mil_litros = producao de LEITE (nao de soro) no ano, em milhares
   de litros, exatamente como publicado pela fonte.
========================================================================== */

const MILK_PRODUCTION_BY_STATE = [
  { code: "mg", nome: "Minas Gerais",        milLitros: 9447549 },
  { code: "pr", nome: "Paraná",              milLitros: 4339194 },
  { code: "rs", nome: "Rio Grande do Sul",   milLitros: 4270799 },
  { code: "go", nome: "Goiás",               milLitros: 3180505 },
  { code: "sc", nome: "Santa Catarina",      milLitros: 3040186 },
  { code: "sp", nome: "São Paulo",           milLitros: 1651808 },
  { code: "ro", nome: "Rondônia",            milLitros: 1128596 },
  { code: "ba", nome: "Bahia",               milLitros: 1068451 },
  { code: "pe", nome: "Pernambuco",          milLitros: 1064748 },
  { code: "ce", nome: "Ceará",               milLitros: 797368 },
  { code: "mt", nome: "Mato Grosso",         milLitros: 657526 },
  { code: "pa", nome: "Pará",                milLitros: 605199 },
  { code: "al", nome: "Alagoas",             milLitros: 603808 },
  { code: "rj", nome: "Rio de Janeiro",      milLitros: 431966 },
  { code: "es", nome: "Espírito Santo",      milLitros: 415563 },
  { code: "to", nome: "Tocantins",           milLitros: 399348 },
  { code: "se", nome: "Sergipe",             milLitros: 347645 },
  { code: "ma", nome: "Maranhão",            milLitros: 342270 },
  { code: "rn", nome: "Rio Grande do Norte", milLitros: 323854 },
  { code: "ms", nome: "Mato Grosso do Sul",  milLitros: 282755 },
  { code: "pb", nome: "Paraíba",             milLitros: 241010 },
  { code: "pi", nome: "Piauí",               milLitros: 70789 },
  { code: "am", nome: "Amazonas",            milLitros: 43846 },
  { code: "ac", nome: "Acre",                milLitros: 42741 },
  { code: "df", nome: "Distrito Federal",    milLitros: 29350 },
  { code: "rr", nome: "Roraima",             milLitros: 13470 },
  { code: "ap", nome: "Amapá",               milLitros: 4671 },
];

// EXTERNO E02 (EPAMIG/ILCT, citando Gonzalez Siso 1996 / Atra et al. 2005):
// 85-90% do volume de leite usado no queijo vira soro.
const SORO_FRACTION_MIN = 0.85;
const SORO_FRACTION_MAX = 0.90;
