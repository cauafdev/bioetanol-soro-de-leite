# SoroIA — site da feira

Site com IA de chat especialista no projeto de bioetanol a partir do soro de
leite. Roda **100% localmente no seu notebook, offline, sem chave de API, sem
cartão de crédito e sem conta em lugar nenhum** — o modelo de IA (via Ollama)
roda direto no seu computador. Não precisa de internet para o chat funcionar
(só precisa se quiser, por exemplo, abrir o site de outro dispositivo na
mesma rede).

## Antes da feira (fazer uma vez)

1. **Instalar o Ollama** (o programa que roda o modelo de IA local):
   - Baixe em https://ollama.com/download (ou já foi instalado nesta máquina).
   - Abra o Ollama uma vez para confirmar que instalou certo (ele fica rodando
     em segundo plano, com um ícone na bandeja do Windows).

2. **Baixar o modelo de IA** (só precisa fazer isso uma vez — é um download
   de ~2GB, então faça isso com uma internet boa, hoje à noite, não na hora
   da feira):

   ```bash
   ollama pull llama3.2:3b
   ```

   Testamos também o `llama3.1:8b` (mais "inteligente"), mas nesse notebook
   (GTX 1650, 4GB de VRAM) ele processa a base de conhecimento parcialmente
   na CPU e uma resposta pode levar 3+ minutos. O `llama3.2:3b` cabe melhor
   na GPU e responde bem mais rápido — por isso é o padrão.

3. **Instalar as dependências do site** (na raiz do projeto, `Projeto 10 produção bioetanol/`):

   ```bash
   python -m pip install -r webapp/requirements.txt
   ```

## No dia da feira

1. Confirme que o Ollama está rodando (ícone na bandeja do Windows — se não
   estiver, abra o aplicativo Ollama).
2. Abra um terminal na pasta `webapp/` e rode:

   ```bash
   python server.py
   ```

3. Abra o navegador em **http://localhost:8000** e deixe em tela cheia (F11).
4. Pronto — os visitantes podem conversar com a SoroIA, sem precisar de
   internet nenhuma. Ela responde tanto perguntas simples ("quanto de etanol
   foi produzido?") quanto complexas ("é viável economicamente?", "compare com
   outras pesquisas", "gere um gráfico dos cenários"), sempre com base nos
   dados reais do projeto.

Se o Ollama não estiver aberto, o chat mostra um aviso claro pedindo para
abrir o aplicativo — o resto do site continua funcionando normalmente.

**Sobre a velocidade:** ao iniciar, `server.py` manda uma pergunta de
"aquecimento" que já deixa a base de conhecimento pré-processada (pode levar
~1 minuto, aparece "Aquecendo o modelo..." no terminal — espere aparecer
"Modelo pronto." antes de abrir o navegador). Depois disso, perguntas
consecutivas respondem bem mais rápido, porque o Ollama reaproveita esse
pré-processamento enquanto o modelo continuar "quente" na memória. A primeira
pergunta depois de um intervalo longo sem uso (>30 min) volta a demorar mais.
Respostas mais longas (textos de viabilidade, comparações) demoram mais que
perguntas curtas — é o processamento local, sem GPU/servidor dedicado.

## Se as respostas ficarem muito lentas

Se mesmo assim o notebook "engasgar" na feira, dá pra reduzir ainda mais:

1. Diminua o limite de tokens da resposta — crie `webapp/.env` (copie de
   `.env.example`) e coloque `OLLAMA_NUM_PREDICT=400` (respostas mais curtas).
2. Se quiser tentar o modelo maior (`llama3.1:8b`, mais "inteligente" mas
   mais lento neste notebook), baixe com `ollama pull llama3.1:8b` e coloque
   `OLLAMA_MODEL=llama3.1:8b` no `.env` — não recomendado no dia da feira
   com muitos visitantes, mas ok para testar com calma antes.

## Atualizando a base de conhecimento (banco de dados da IA)

A IA responde com base em `webapp/knowledge/context.md`, gerado automaticamente
a partir de `data/raw/`, `data/external/` e `src/models.py`. Para adicionar uma
nova fonte de pesquisa (ex.: um artigo novo, um dado de outra universidade):

1. Adicione uma linha em `data/external/dados_externos.csv` (mesmo formato das
   linhas existentes — inclua fonte, URL, data e confiabilidade).
2. Rode de novo:

   ```bash
   cd webapp
   python build_context.py
   ```

3. Reinicie `python server.py` para carregar o contexto atualizado.

Isso é o "sistema de crescimento do banco de dados": nenhum dado é inventado —
tudo vem de `data/` ou é calculado por `src/models.py`, igual aos notebooks da
pesquisa e ao site Streamlit (`app/`).

## Arquitetura (resumo técnico)

- `server.py` — servidor Flask local. Serve o site estático (`static/`) e o
  endpoint `/api/chat`, que repassa a conversa para o Ollama (rodando em
  `http://localhost:11434`, modelo `llama3.2:3b` por padrão), injetando
  `knowledge/context.md` como mensagem de sistema. Faz um "aquecimento" ao
  iniciar para acelerar a primeira pergunta.
- `static/` — frontend puro (HTML/CSS/JS, sem framework nem build step).
  Usa `marked.js` para renderizar markdown e `Chart.js` para gráficos que a
  IA pode gerar (`static/vendor/` — bibliotecas baixadas localmente, não
  dependem de CDN durante a feira).
- `build_context.py` — gera a base de conhecimento a partir dos dados do
  projeto. Reexecutável a qualquer momento.
- Nenhum dado da pesquisa muda: o site é uma camada de apresentação sobre o
  mesmo `data/` e `src/models.py` usados pelos notebooks e pelo site Streamlit.
