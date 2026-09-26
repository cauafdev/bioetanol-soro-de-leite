"""
Servidor local do site da feira — SoroIA.

Serve o frontend estatico (static/) e um endpoint /api/chat que repassa a
conversa para um modelo rodando localmente via Ollama (100% offline, sem
chave de API, sem custo), injetando a base de conhecimento do projeto
(knowledge/context.md) como instrucao de sistema.

Pre-requisito: o app Ollama precisa estar aberto/rodando (ele fica escutando
em http://localhost:11434) e o modelo abaixo precisa ter sido baixado uma vez
com `ollama pull <modelo>`.

Rodar:
    python server.py
Abre em http://localhost:8000
"""

from __future__ import annotations

import json
import os
import re
import time
import unicodedata
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, Response, request, send_from_directory
from ollama import Client

WEBAPP_DIR = Path(__file__).resolve().parent
STATIC_DIR = WEBAPP_DIR / "static"
CONTEXT_PATH = WEBAPP_DIR / "knowledge" / "context.md"
FAQ_PATH = WEBAPP_DIR / "knowledge" / "faq.json"

load_dotenv(WEBAPP_DIR / ".env")

# Modelo local do Ollama. Pode trocar via .env (OLLAMA_MODEL=...) sem editar
# este arquivo. Trocar aqui exige rodar `ollama pull <modelo-novo>` antes.
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# O Ollama usa por padrao uma janela de contexto pequena (2048-4096 tokens),
# o que corta silenciosamente a base de conhecimento (context.md tem ~13-15 mil
# tokens). Sem isso, o modelo responde como se não tivesse os dados do projeto.
NUM_CTX = int(os.environ.get("OLLAMA_NUM_CTX", "16384"))

# Limite de tokens gerados por resposta. Neste notebook (GTX 1650), a geração
# roda a ~3-4 tokens/s, entao uma resposta sem limite pode levar varios minutos.
NUM_PREDICT = int(os.environ.get("OLLAMA_NUM_PREDICT", "400"))

# Mantem o modelo carregado na memoria entre perguntas (evita recarregar o
# modelo do zero se houver uma pausa longa sem visitantes).
KEEP_ALIVE = os.environ.get("OLLAMA_KEEP_ALIVE", "30m")

PERSONA = """Você é a SoroIA, a inteligência artificial especialista do projeto de \
pesquisa "Bioetanol a partir do soro de leite", apresentado na feira de \
ciências do Colégio IMP (pesquisa conduzida no Laboratório G-Óleo, UFLA, \
Lavras-MG). Você conversa com visitantes da feira: estudantes, professores, \
avaliadores e curiosos, de todas as idades e níveis de conhecimento técnico.

Sua base de conhecimento (abaixo) contém TODOS os dados do experimento, os \
dados de fontes externas (universidades e institutos de pesquisa), o modelo \
técnico e econômico calculado, as limitações conhecidas e a conclusão final \
do projeto. Use SOMENTE essas informações — nunca invente números.

Regras de resposta:
- Responda em português do Brasil, salvo se o visitante escrever em outro idioma.
- Sempre que citar um número, deixe claro sua origem usando os rótulos do \
projeto: **Medido** (no experimento), **Calculado** (derivado por \
matemática/estequiometria), **Externo** (de outra fonte/instituição, cite \
qual) ou **Premissa de projeto** (hipótese assumida, não medida). Nunca \
apresente uma premissa como se fosse um dado medido.
- Para perguntas simples ("quanto de etanol foi produzido?"), responda direto \
e em poucas frases, depois ofereça aprofundar se a pessoa quiser.
- Para perguntas complexas (viabilidade econômica, comparação com outras \
pesquisas, redigir um texto, produção em escala industrial), pode escrever \
uma resposta mais longa e estruturada, sempre fundamentada nos dados da base.
- Ao comparar com "outras universidades" ou "outras pesquisas", use as fontes \
externas da base (EPAMIG/ILCT, CEPEA/Esalq-USP, CTBE/CNPEM, CEMIG, estudos \
internacionais indexados no PMC sobre fermentação de soro com Kluyveromyces \
spp., O'Leary et al. 1977/USDA, relatório USDA de viabilidade industrial) e \
deixe claro quando a rota biológica delas é diferente da usada neste projeto \
(lactase + Saccharomyces cerevisiae, não Kluyveromyces).
- Seja honesto sobre as limitações: o teor alcoólico do destilado nunca foi \
medido (é a maior lacuna do projeto), e o modelo econômico usa preço de \
varejo dos insumos. PROIBIDO afirmar de forma definitiva que o projeto "é \
viável" ou "não é viável" economicamente — mesmo com um "parece que" ou \
"provavelmente" na frase, isso ainda soa como conclusão definitiva, o que os \
dados NÃO sustentam. Em vez disso, diga algo como: "os cenários calculados \
mostram custo de produção estimado em X e receita estimada em Y — o custo \
supera a receita nos cenários avaliados, mas o modelo econômico tem lacunas \
importantes (preço de varejo em vez de industrial, teor alcoólico não \
medido), então não dá para concluir viabilidade ou inviabilidade definitiva \
a partir dele."
- ATENÇÃO, erro crítico a evitar: os 15 mL medidos (dado "volume_destilado_obtido", \
rótulo Medido) são o volume do DESTILADO, não de "etanol puro". NUNCA diga que \
foram produzidos "15 mL de etanol puro" — isso é falso, porque o teor alcoólico \
do destilado nunca foi determinado (densidade não medida). Ao falar da produção \
medida, diga sempre "15 mL de destilado (o teor alcoólico dele não foi medido)". \
Os valores de "etanol_puro_L" que aparecem nas tabelas de cenários são \
CALCULADOS/projetados (a partir do rendimento teórico estequiométrico), não o \
resultado medido diretamente — deixe isso claro sempre que os citar.
- Quando fizer sentido visualizar dados (comparar cenários, mostrar produção \
por escala, custo vs. receita, sensibilidade de preço), gere um gráfico \
emitindo um bloco de código cercado com a linguagem `chart`, contendo APENAS \
um JSON válido neste formato:
  ```chart
  {"type": "bar", "title": "Título do gráfico",
   "labels": ["A", "B", "C"],
   "series": [{"name": "Série 1", "data": [1, 2, 3]}],
   "xLabel": "Eixo X", "yLabel": "Eixo Y",
   "source": "Nota de fonte/proveniência, curta"}
  ```
  `type` pode ser "bar", "line" ou "pie". Use dados reais da base de \
conhecimento (nunca invente valores do gráfico). Só gere gráfico quando \
ele agregar valor real à resposta — não force um gráfico em toda resposta.
- Formate texto com markdown (negrito, listas, títulos ##) quando ajudar a \
legibilidade, mas não exagere em estrutura para respostas curtas.
- Se perguntarem quem te criou ou qual IA você é, diga que é a SoroIA, \
um modelo de IA rodando localmente (via Ollama) para este projeto de feira \
de ciências, treinada especificamente com os dados desta pesquisa.
"""


def build_system_message() -> dict:
    context = CONTEXT_PATH.read_text(encoding="utf-8")
    return {"role": "system", "content": PERSONA + "\n\n" + context}


def _normalize(text: str) -> str:
    """minusculas, sem acento, sem pontuacao — para comparar com tolerancia."""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9\s]", " ", text)


FAQ_ENTRIES = json.loads(FAQ_PATH.read_text(encoding="utf-8"))
for _entry in FAQ_ENTRIES:
    _entry["_norm_keywords"] = [_normalize(k) for k in _entry["keywords"]]


def match_faq(question: str) -> str | None:
    """Casa a pergunta com uma FAQ pronta (resposta instantanea, sem chamar o
    Ollama). So retorna se achar uma frase-chave inteira contida na pergunta —
    evita falso positivo por palavra solta. Em caso de mais de um casar,
    escolhe a frase-chave mais longa (mais especifica).
    """
    normalized = _normalize(question)
    best_answer = None
    best_len = 0
    for entry in FAQ_ENTRIES:
        for kw in entry["_norm_keywords"]:
            if kw in normalized and len(kw) > best_len:
                best_answer = entry["answer"]
                best_len = len(kw)
    return best_answer


app = Flask(__name__, static_folder=None)
client = Client(host=OLLAMA_HOST)


@app.get("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.get("/<path:filename>")
def static_files(filename: str):
    return send_from_directory(STATIC_DIR, filename)


@app.post("/api/chat")
def chat():
    body = request.get_json(force=True)
    messages = body.get("messages", [])
    if not messages or not isinstance(messages, list):
        return {"error": "messages ausente ou inválido"}, 400

    last_user_msg = messages[-1].get("content", "") if messages else ""
    faq_answer = match_faq(last_user_msg)
    if faq_answer:
        def generate_faq():
            for word in faq_answer.split(" "):
                yield f"data: {json.dumps({'delta': word + ' '})}\n\n"
                time.sleep(0.015)
            yield f"data: {json.dumps({'done': True})}\n\n"

        return Response(generate_faq(), mimetype="text/event-stream")

    full_messages = [build_system_message()] + messages

    def generate():
        try:
            stream = client.chat(
                model=MODEL,
                messages=full_messages,
                stream=True,
                keep_alive=KEEP_ALIVE,
                options={"num_ctx": NUM_CTX, "num_predict": NUM_PREDICT},
            )
            for chunk in stream:
                delta = chunk.get("message", {}).get("content", "")
                if delta:
                    yield f"data: {json.dumps({'delta': delta})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as exc:  # noqa: BLE001
            raw = str(exc)
            if any(
                hint in raw
                for hint in ("10061", "actively refused", "Connection refused", "ConnectError")
            ):
                message = (
                    "Não consegui conectar ao Ollama. Verifique se o aplicativo "
                    "Ollama está aberto (ícone na bandeja do Windows) e tente de novo."
                )
            elif "not found" in raw.lower() or "404" in raw:
                message = (
                    f"O modelo '{MODEL}' não foi encontrado no Ollama. Rode "
                    f"`ollama pull {MODEL}` no terminal e tente de novo."
                )
            else:
                message = raw
            yield f"data: {json.dumps({'error': message})}\n\n"

    return Response(generate(), mimetype="text/event-stream")


def warm_up() -> None:
    """Envia uma pergunta trivial ao Ollama para pre-processar e cachear a base
    de conhecimento (persona + context.md) antes do primeiro visitante chegar.
    Sem isso, a primeira pergunta do dia demora ~1 min a mais que as seguintes.
    """
    try:
        print("Aquecendo o modelo (pode levar 1-2 minutos)...")
        client.chat(
            model=MODEL,
            messages=[build_system_message(), {"role": "user", "content": "oi"}],
            stream=False,
            keep_alive=KEEP_ALIVE,
            options={"num_ctx": NUM_CTX, "num_predict": 1},
        )
        print("Modelo pronto.")
    except Exception as exc:  # noqa: BLE001
        print(f"Aviso: não foi possível pré-aquecer o modelo agora ({exc}). "
              f"A primeira pergunta pode demorar um pouco mais.")


if __name__ == "__main__":
    print(f"SoroIA rodando em http://localhost:8000  (modelo Ollama: {MODEL})")
    warm_up()
    app.run(host="0.0.0.0", port=8000, debug=False, threaded=True)
