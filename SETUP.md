# Como rodar em um PC novo (do zero)

Guia direto para deixar o **site da feira** (`site/`) rodando em qualquer computador Windows que
nunca teve nada deste projeto instalado. Leva uns 5 minutos.

## 1. Pré-requisitos

Só precisa de duas coisas instaladas: **Git** e **Python**.

- Git: https://git-scm.com/download/win (instalador padrão, next-next-next)
- Python 3.10+: https://www.python.org/downloads/ — **na primeira tela do instalador, marque a
  caixinha "Add python.exe to PATH"** antes de clicar em Install (senão o comando `python` não
  funciona depois).

Para conferir se já estão instalados, abra o PowerShell e rode:

```powershell
git --version
python --version
```

Se aparecer um número de versão nos dois, pode pular para o passo 2.

## 2. Baixar o projeto

```powershell
cd Desktop
git clone https://github.com/cauafdev/bioetanol-soro-de-leite.git
cd bioetanol-soro-de-leite
```

(Se o repositório estiver privado, o Git vai pedir login do GitHub na primeira vez — use a conta
`cauafdev` ou peça para adicionar o novo usuário como colaborador em
`github.com/cauafdev/bioetanol-soro-de-leite/settings/access`.)

## 3. Instalar as dependências do site

```powershell
cd site
python -m pip install -r requirements.txt
```

## 4. Rodar

```powershell
python server.py
```

Deve aparecer:

```
soro.valor rodando em http://localhost:8000
```

Abra o navegador em **http://localhost:8000** e deixe em tela cheia (F11).

## 5. Checklist antes de apresentar

- [ ] A molécula 3D de etanol carrega e gira sozinha na aba "Visão geral" (se não aparecer, aperte
  Ctrl+F5 no navegador para forçar recarregar sem cache).
- [ ] O Simulador responde ao mover os sliders.
- [ ] O Mapa do Brasil mostra os estados coloridos e reage ao passar o mouse.
- [ ] A aba "SoroBot (IA)" **precisa de internet** para carregar (é a única exceção — todo o resto
  do site funciona sem internet nenhuma). Se não tiver internet na hora, essa aba fica em branco,
  mas o resto do site funciona normalmente.

## Se algo der errado

- **`'python' não é reconhecido...`** — o Python foi instalado sem marcar "Add to PATH". Reinstale
  marcando essa opção, ou use `py` no lugar de `python` nos comandos acima.
- **`'pip' não é reconhecido...`** — use `python -m pip install -r requirements.txt` (com `-m`) em
  vez de só `pip install`.
- **Porta 8000 já em uso** — outro programa já está usando essa porta. Feche-o, ou edite a última
  linha de `site/server.py` trocando `port=8000` por outra porta (ex.: `port=8080`) e acesse
  `http://localhost:8080`.
- **Quer usar o chat com IA local também (Fase 3, `webapp/`)** — isso é opcional e dá mais trabalho
  (precisa instalar o Ollama, baixar um modelo de ~2GB). Siga `webapp/README.md` separadamente; não
  é necessário para o site principal (`site/`) funcionar.
