"""
Servidor local do site da feira — soro.valor.

Site 100% estatico: sem IA, sem API, sem internet. Todo o calculo do
simulador roda no navegador (app.js), usando as mesmas formulas de
`src/models.py`. Este servidor so entrega os arquivos (HTML/CSS/JS).

Rodar:
    python server.py
Abre em http://localhost:8000
"""

from pathlib import Path

from flask import Flask, send_from_directory

SITE_DIR = Path(__file__).resolve().parent

app = Flask(__name__, static_folder=None)


@app.get("/")
def index():
    return send_from_directory(SITE_DIR, "index.html")


@app.get("/<path:filename>")
def static_files(filename: str):
    return send_from_directory(SITE_DIR, filename)


if __name__ == "__main__":
    print("soro.valor rodando em http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=False, threaded=True)
