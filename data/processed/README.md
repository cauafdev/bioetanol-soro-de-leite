# Dados processados

Esta pasta existe para seguir o padrão de pesquisa reprodutível (`raw/` → `processed/`), mas hoje
está vazia por uma razão específica: **nenhum resultado deste projeto é cacheado em disco**.

Todo número derivado (balanço de massa, cenários técnicos, análise de sensibilidade, simulação de
Monte Carlo) é calculado **em tempo real** a partir de `data/raw/` e `data/external/` pelas funções
de `../../src/models.py`, tanto quando os notebooks em `../../notebooks/` são executados quanto
quando o site (`../../index.html`) roda os mesmos cálculos em JavaScript no navegador.

Ou seja: não há uma etapa de "processamento em lote que grava um CSV intermediário" — o processamento
acontece a cada execução, direto do dado bruto. Isso é intencional (elimina o risco de um CSV
processado ficar desatualizado em relação ao dado bruto ou ao código), mas significa que, sem rodar
os notebooks, não há aqui uma tabela pronta para inspecionar fora do Python/Jupyter.

Se no futuro for útil ter tabelas processadas prontas para abrir num editor de planilhas (por
exemplo, para a estudante de Química revisar sem precisar rodar Jupyter), os candidatos naturais são:

- `cenarios_tecnicos.csv` — resultado de `scale_all_scenarios()` para os 3 cenários (conservador/
  experimental/otimista) num volume de referência.
- `sensibilidade_tornado.csv` — resultado da análise de sensibilidade (notebook 05).
- `monte_carlo_receita.csv` — as 2.000 simulações de receita geradas por `monte_carlo_simulation()`
  (mesmo notebook, `random_seed=42`).

Essas exportações não foram geradas nesta reorganização para não inventar um artefato de dados sem
confirmar com o responsável pelo projeto qual formato seria mais útil.
