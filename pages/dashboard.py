"""
pages/dashboard.py
Tela inicial do World Cup Manager 2026 — Dashboard
"""

import dash
from dash import html, dcc
import plotly.graph_objects as go
from config.database import fetch_data

# ── helpers ────────────────────────────────────────────────────────────────────

def _safe_int(df, col="total"):
    """Retorna o valor inteiro de df[col].iloc[0], ou 0 se falhar."""
    try:
        return int(df[col].iloc[0])
    except Exception:
        return 0


def _safe_float(df, col="media"):
    """Retorna o valor float formatado, ou '0.00'."""
    try:
        return f"{float(df[col].iloc[0]):.2f}"
    except Exception:
        return "0.00"


# ── consultas SQL ───────────────────────────────────────────────────────────────

def _get_kpis():
    """Busca os indicadores do dashboard."""
    # Ajuste os nomes das colunas conforme o seu schema real
    selecoes  = _safe_int(fetch_data("SELECT COUNT(*) AS total FROM selecoes"))
    jogadores = _safe_int(fetch_data("SELECT COUNT(*) AS total FROM jogadores"))
    estadios  = _safe_int(fetch_data("SELECT COUNT(*) AS total FROM estadios"))
    partidas  = _safe_int(fetch_data("SELECT COUNT(*) AS total FROM partidas"))

    # Ajuste a coluna de gols conforme o schema (ex: gols_mandante, gols_visitante)
    gols_df = fetch_data(
        "SELECT COALESCE(SUM(gols_mandante + gols_visitante), 0) AS total FROM partidas"
    )
    gols = _safe_int(gols_df)

    media = round(gols / partidas, 2) if partidas else 0.0

    return {
        "selecoes":  selecoes,
        "jogadores": jogadores,
        "estadios":  estadios,
        "partidas":  partidas,
        "gols":      gols,
        "media":     f"{media:.2f}",
    }


def _get_ranking():
    """
    Busca o ranking de vitórias por seleção.
    Ajuste os nomes das colunas (nome_selecao, vitorias) conforme o schema real.
    """
    query = """
        SELECT
            s.nome AS nome_selecao,           -- ajuste se necessário
            COUNT(*) AS vitorias
        FROM partidas p
        JOIN selecoes s
            ON (
                (p.id_selecao_mandante = s.id AND p.gols_mandante > p.gols_visitante)
                OR
                (p.id_selecao_visitante = s.id AND p.gols_visitante > p.gols_mandante)
            )
        GROUP BY s.id, s.nome
        ORDER BY vitorias DESC
        LIMIT 20
    """
    try:
        df = fetch_data(query)
        return df
    except Exception:
        return None


# ── componentes visuais ─────────────────────────────────────────────────────────

def _card_kpi(label, value, sub, icon, color, href):
    """Card de indicador clicável."""
    return dcc.Link(
        html.Div(
            className="kpi-card",
            children=[
                html.Div(className="kpi-left", children=[
                    html.Span(label, className="kpi-label"),
                    html.Span(str(value), className="kpi-value"),
                    html.Span(sub, className="kpi-sub"),
                ]),
                html.Div(
                    className="kpi-icon",
                    style={"background": color},
                    children=html.Span(icon, className="kpi-emoji"),
                ),
            ],
        ),
        href=href,
        style={"textDecoration": "none"},
    )


def _ranking_chart(df):
    """Gráfico de barras horizontal com Plotly."""
    if df is None or df.empty:
        # Dados de exemplo enquanto não há partidas
        nomes   = ["Brasil", "Argentina", "França", "Alemanha", "Itália",
                   "Espanha", "Inglaterra", "Holanda", "Uruguai", "Portugal"]
        vitorias = [0] * 10
    else:
        nomes    = df["nome_selecao"].tolist()[::-1]  # invertido para o eixo Y
        vitorias = df["vitorias"].tolist()[::-1]

    max_v = max(vitorias) if max(vitorias) > 0 else 1

    fig = go.Figure()

    # Barra de fundo (track cinza)
    fig.add_trace(go.Bar(
        y=nomes,
        x=[max_v * 1.05] * len(nomes),
        orientation="h",
        marker=dict(color="rgba(230,232,240,0.6)", line=dict(width=0)),
        showlegend=False,
        hoverinfo="skip",
    ))

    # Barra principal
    bar_colors = [
        "#10B981" if v == max(vitorias) and v > 0 else "#CBD5E1"
        for v in vitorias
    ]

    fig.add_trace(go.Bar(
        y=nomes,
        x=vitorias,
        orientation="h",
        marker=dict(
            color=bar_colors,
            line=dict(width=0),
        ),
        text=[str(v) for v in vitorias],
        textposition="outside",
        textfont=dict(size=13, color="#374151", family="Inter, sans-serif"),
        hovertemplate="%{y}: <b>%{x} vitórias</b><extra></extra>",
        showlegend=False,
    ))

    fig.update_layout(
        barmode="overlay",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=50, t=10, b=10),
        height=max(300, len(nomes) * 40),
        xaxis=dict(
            showgrid=False, showticklabels=False,
            zeroline=False, range=[0, max_v * 1.2],
        ),
        yaxis=dict(
            showgrid=False, tickfont=dict(size=13, color="#374151"),
        ),
        bargap=0.35,
        font=dict(family="Inter, sans-serif"),
    )

    return fig


def _top3_card(df):
    """Card com os 3 primeiros do ranking."""
    medals = [
        {"bg": "#FEF9C3", "border": "#F59E0B", "text": "#92400E"},  # ouro
        {"bg": "#F1F5F9", "border": "#94A3B8", "text": "#475569"},  # prata
        {"bg": "#FEF3C7", "border": "#D97706", "text": "#92400E"},  # bronze
    ]
    medal_labels = ["1", "2", "3"]

    if df is None or df.empty:
        rows = [
            {"nome": "Brasil",    "vitorias": 0},
            {"nome": "Argentina", "vitorias": 0},
            {"nome": "França",    "vitorias": 0},
        ]
    else:
        rows = df.head(3).to_dict("records")
        # garante ao menos 3 linhas
        while len(rows) < 3:
            rows.append({"nome_selecao": "—", "vitorias": 0})

    items = []
    for i, row in enumerate(rows[:3]):
        m = medals[i]
        nome = row.get("nome_selecao", row.get("nome", "—"))
        vit  = row.get("vitorias", 0)
        items.append(
            html.Div(className="top3-item", children=[
                html.Div(
                    medal_labels[i],
                    className="top3-medal",
                    style={
                        "background": m["bg"],
                        "border": f"2px solid {m['border']}",
                        "color": m["text"],
                    },
                ),
                html.Span(nome, className="top3-name"),
                html.Span(
                    f"{vit} {'vitória' if vit == 1 else 'vitórias'}",
                    className="top3-wins",
                ),
            ])
        )

    return html.Div(className="top3-card", children=[
        html.H3("TOP 3 SELEÇÕES", className="top3-title"),
        html.Div(items),
    ])


def _sidebar():
    """Sidebar lateral esquerda."""
    menu_items = [
        {"label": "Dashboard",        "icon": "📊", "href": "/",          "active": True},
        {"label": "Seleções",         "icon": "🚩", "href": "/selecoes",  "active": False},
        {"label": "Jogadores",        "icon": "👕", "href": "/jogadores", "active": False},
        {"label": "Estádios",         "icon": "🏟️", "href": "/estadios",  "active": False},
        {"label": "Partidas",         "icon": "📅", "href": "/partidas",  "active": False},
        {"label": "Ranking de Vitórias", "icon": "📈", "href": "/ranking","active": False},
    ]

    links = []
    for item in menu_items:
        cls = "sidebar-link active" if item["active"] else "sidebar-link"
        links.append(
            dcc.Link(
                children=[
                    html.Span(item["icon"], className="sidebar-icon"),
                    html.Span(item["label"]),
                ],
                href=item["href"],
                className=cls,
            )
        )

    return html.Div(className="sidebar", children=[
        # Logo
        html.Div(className="sidebar-logo", children=[
            html.Div("⚽", className="sidebar-logo-icon"),
            html.Div(children=[
                html.Span("WORLD CUP", className="logo-top"),
                html.Span("MANAGER",   className="logo-bottom"),
            ]),
        ]),

        # Navegação
        html.Nav(className="sidebar-nav", children=links),

        # Card decorativo inferior
        html.Div(className="sidebar-footer-card", children=[
            html.Div(className="bubble b1"),
            html.Div(className="bubble b2"),
            html.Div(className="bubble b3"),
            html.Div(className="bubble b4"),
            html.Div(className="bubble b5"),
            html.Div(className="footer-label", children=[
                html.Span("ADMINISTRADOR", className="footer-role"),
                html.Div(children=[
                    html.Span("● ", style={"color": "#10B981", "fontSize": "10px"}),
                    html.Span("Online", className="footer-status"),
                ]),
            ]),
        ]),
    ])


def _topbar():
    """Barra superior."""
    return html.Div(className="topbar", children=[
        html.Div(className="topbar-search", children=[
            html.Span("🔍", className="search-icon"),
            dcc.Input(
                placeholder="Buscar seleções, estádios ou jogadores...",
                className="search-input",
                type="text",
                debounce=False,
            ),
        ]),
        html.Div(className="topbar-profile", children=[
            html.Div(className="notif-wrapper", children=[
                html.Span("🔔", className="notif-icon"),
                html.Span("", className="notif-dot"),
            ]),
            html.Div(className="profile-info", children=[
                html.Span("Master Admin", className="profile-name"),
                html.Span("ROOT@FIFA-REPLICA", className="profile-role"),
            ]),
            html.Div("MA", className="profile-avatar"),
        ]),
    ])


# ── layout principal ────────────────────────────────────────────────────────────

def layout():
    """Retorna o layout completo da página Dashboard."""

    # KPIs
    try:
        kpis = _get_kpis()
    except Exception:
        kpis = {"selecoes": "—", "jogadores": "—", "estadios": "—",
                "partidas": "—", "gols": "—", "media": "—"}

    # Ranking
    ranking_df = _get_ranking()

    kpi_cards = [
        _card_kpi("SELEÇÕES",      kpis["selecoes"],  "cadastradas",  "🚩", "rgba(59,130,246,0.15)",   "/selecoes"),
        _card_kpi("JOGADORES",     kpis["jogadores"], "cadastrados",  "👥", "rgba(16,185,129,0.15)",   "/jogadores"),
        _card_kpi("ESTÁDIOS",      kpis["estadios"],  "cadastrados",  "🏟️", "rgba(16,185,129,0.15)",   "/estadios"),
        _card_kpi("PARTIDAS",      kpis["partidas"],  "realizadas",   "⚙️", "rgba(239,68,68,0.15)",    "/partidas"),
        _card_kpi("TOTAL DE GOLS", kpis["gols"],      "marcados",     "🔮", "rgba(139,92,246,0.15)",   "/partidas"),
        _card_kpi("MÉDIA DE GOLS", kpis["media"],     "por partida",  "📋", "rgba(249,115,22,0.15)",   "/partidas"),
    ]

    return html.Div(className="app-wrapper", children=[
        _sidebar(),

        html.Div(className="main-area", children=[
            _topbar(),

            html.Div(className="content", children=[
                # Cabeçalho
                html.Div(className="page-header", children=[
                    html.H1("Dashboard", className="page-title"),
                    html.P("Visão geral dos dados da Copa do Mundo",
                           className="page-subtitle"),
                ]),

                # Cards KPI
                html.Div(className="kpi-grid", children=kpi_cards),

                # Ranking + Top 3
                html.Div(className="bottom-grid", children=[
                    # Gráfico
                    html.Div(className="ranking-card", children=[
                        html.H3("RANKING DE VITÓRIAS POR SELEÇÃO",
                                className="section-title"),
                        dcc.Graph(
                            figure=_ranking_chart(ranking_df),
                            config={"displayModeBar": False},
                            style={"width": "100%"},
                        ),
                    ]),

                    # Top 3
                    _top3_card(ranking_df),
                ]),
            ]),
        ]),
    ])