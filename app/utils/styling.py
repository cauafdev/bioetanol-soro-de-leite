"""
Paleta, tipografia e componentes visuais compartilhados por todas as páginas
do site. Centralizar isso aqui garante que o site inteiro leia como um único
sistema (mesma paleta, mesmos rótulos de proveniência de dado, mesmo cabeçalho).

Paleta: instância de referência validada do skill de dataviz (categórica,
sequencial, diverging e status já testadas para contraste e distinção em
daltonismo). Não foram inventadas cores novas.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

APP_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = APP_DIR.parent
SRC_DIR = ROOT_DIR / "src"
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"
PHOTOS_DIR = ASSETS_DIR / "photos"

# ---------------------------------------------------------------------------
# Paleta (dataviz skill - reference instance)
# ---------------------------------------------------------------------------

CATEGORICAL = {
    "blue": "#2a78d6",
    "orange": "#eb6834",
    "aqua": "#1baf7a",
    "yellow": "#eda100",
    "magenta": "#e87ba4",
    "green": "#008300",
    "violet": "#4a3aa7",
    "red": "#e34948",
}

# Cores de cenario - atribuidas por identidade fixa (nunca ciclicas)
CENARIO_COLOR = {
    "conservador": CATEGORICAL["orange"],
    "experimental": CATEGORICAL["blue"],
    "otimista": CATEGORICAL["aqua"],
}

STATUS = {
    "good": "#0ca30c",
    "warning": "#fab219",
    "serious": "#ec835a",
    "critical": "#d03b3b",
}

INK = {
    "primary": "#0b0b0b",
    "secondary": "#52514e",
    "muted": "#898781",
    "gridline": "#e1e0d9",
    "baseline": "#c3c2b7",
}

SURFACE = {
    "chart": "#fcfcfb",
    "page": "#f9f9f7",
}

SEQUENTIAL_BLUE = ["#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#184f95"]


def format_brl_compact(value: float) -> str:
    """Formata um valor em reais de forma compacta (R$ 1,80M / R$ 134,70),
    em vez do valor cheio (R$ 1.800.648,33) — necessario porque um numero
    grande por extenso quebra de linha no meio dentro de um stat_tile
    estreito. Ver skill de dataviz: "value (Sans semibold, auto-compact:
    1,284 / 12.9K / $4.2M)".
    """
    sign = "-" if value < 0 else ""
    v = abs(value)
    if v >= 1_000_000:
        s = f"{v / 1_000_000:,.2f}M"
    elif v >= 1_000:
        s = f"{v / 1_000:,.1f}K"
    else:
        s = f"{v:,.2f}"
    # troca separadores para o padrao pt-BR (milhar '.', decimal ',')
    s = s.replace(",", "\0").replace(".", ",").replace("\0", ".")
    return f"{sign}R$ {s}"


def inject_base_css() -> None:
    """Injeta CSS compartilhado (tipografia, cabeçalho, cards, badges)."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', system-ui, -apple-system, "Segoe UI", sans-serif;
        }}

        h1, h2, h3 {{
            font-family: 'Source Serif 4', Georgia, serif;
            color: {INK["primary"]};
            letter-spacing: -0.01em;
        }}

        .imp-kicker {{
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 0.78rem;
            letter-spacing: 0.10em;
            text-transform: uppercase;
            color: {CATEGORICAL["blue"]};
            margin-bottom: 0.2rem;
        }}

        .imp-hero-title {{
            font-family: 'Source Serif 4', Georgia, serif;
            font-weight: 700;
            font-size: 2.4rem;
            line-height: 1.15;
            color: {INK["primary"]};
            margin: 0 0 0.5rem 0;
        }}

        .imp-subtitle {{
            color: {INK["secondary"]};
            font-size: 1.05rem;
            line-height: 1.55;
            max-width: 62ch;
        }}

        .imp-card {{
            background: {SURFACE["chart"]};
            border: 1px solid {INK["gridline"]};
            border-radius: 10px;
            padding: 1.1rem 1.3rem;
            height: 100%;
        }}

        .imp-source-note {{
            color: {INK["muted"]};
            font-size: 0.80rem;
            line-height: 1.5;
            border-left: 2px solid {INK["gridline"]};
            padding-left: 0.6rem;
            margin-top: 0.4rem;
        }}

        .imp-section-divider {{
            border: none;
            border-top: 1px solid {INK["gridline"]};
            margin: 2.2rem 0 1.6rem 0;
        }}

        .imp-figcaption {{
            color: {INK["secondary"]};
            font-size: 0.85rem;
            font-style: italic;
            margin-top: 0.35rem;
        }}

        [data-testid="stSidebar"] {{
            background-color: {SURFACE["chart"]};
            border-right: 1px solid {INK["gridline"]};
        }}

        #MainMenu, footer {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(kicker: str, title: str, subtitle: str = "") -> None:
    """Cabeçalho consistente de página (kicker + título serifado + subtítulo).

    Monta o HTML como uma única linha (sem indentação nem linhas em branco
    internas) porque o parser Markdown do Streamlit trata qualquer linha
    puramente em branco dentro de um bloco HTML como o fim do bloco, e a
    linha seguinte, se indentada, vira um bloco de código (regra dos "4
    espaços") em vez de HTML renderizado.
    """
    subtitle_html = f'<p class="imp-subtitle">{subtitle}</p>' if subtitle else ""
    html = (
        f'<div class="imp-kicker">{kicker}</div>'
        f'<div class="imp-hero-title">{title}</div>'
        f'{subtitle_html}'
    )
    st.markdown(html, unsafe_allow_html=True)


def source_note(text: str) -> None:
    """Nota de fonte/limitação, no rodapé de uma tabela ou gráfico."""
    st.markdown(f'<div class="imp-source-note">{text}</div>', unsafe_allow_html=True)


def stat_tile(label: str, value: str, delta: str | None = None, delta_color: str = "muted", help_text: str | None = None) -> None:
    """Cartão de estatística (hero number) no padrão do skill de dataviz.

    HTML montado como uma única linha, sem indentação nem linhas em branco
    internas — ver a nota em `page_header` sobre por que isso é necessário
    para o Streamlit não confundir o bloco com um trecho de código.
    """
    color = {"good": STATUS["good"], "critical": STATUS["critical"], "muted": INK["muted"]}.get(delta_color, INK["muted"])
    delta_html = f'<div style="color:{color};font-size:0.85rem;font-weight:600;margin-top:0.15rem;">{delta}</div>' if delta else ""
    help_html = f'<div style="color:{INK["muted"]};font-size:0.78rem;margin-top:0.3rem;">{help_text}</div>' if help_text else ""
    html = (
        '<div class="imp-card">'
        f'<div style="color:{INK["secondary"]};font-size:0.85rem;font-weight:500;">{label}</div>'
        f'<div style="font-family:\'Source Serif 4\',serif;font-weight:700;font-size:1.85rem;color:{INK["primary"]};margin-top:0.1rem;">{value}</div>'
        f'{delta_html}'
        f'{help_html}'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def plotly_layout_defaults() -> dict:
    """Layout base compartilhado por todos os gráficos Plotly do site.

    A legenda horizontal fica ABAIXO da área de plotagem (não acima), de
    propósito: uma legenda acima competia por espaço com o título de cada
    figura (`fig.update_layout(title=...)`, passado por cada chamador) e as
    duas colidiam visualmente. Com a legenda embaixo, título e legenda nunca
    disputam a mesma faixa vertical.
    """
    return dict(
        paper_bgcolor=SURFACE["chart"],
        plot_bgcolor=SURFACE["chart"],
        font=dict(family="Inter, system-ui, sans-serif", color=INK["primary"], size=13),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=50, b=70),
        xaxis=dict(gridcolor=INK["gridline"], zerolinecolor=INK["baseline"], linecolor=INK["baseline"]),
        yaxis=dict(gridcolor=INK["gridline"], zerolinecolor=INK["baseline"], linecolor=INK["baseline"]),
    )
