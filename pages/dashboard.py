"""
World Cup Manager 2026 — pages/dashboard.py
Dashboard principal: cards de estatísticas, ranking de vitórias e Top 3 seleções.
"""

import dash
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd

# Register this page as the root route
dash.register_page(__name__, path="/", name="Dashboard")

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _safe_fetch(query):
    """
    Wraps config.database.fetch_data in a try/except so the page degrades
    gracefully when the DB is unreachable (useful in dev without Railway).
    Adjust column names here if your schema differs.
    """
    try:
        from config.database import fetch_data
        return fetch_data(query)
    except Exception as e:
        print(f"[dashboard] DB fetch failed: {e}")
        return pd.DataFrame()


def _count(query, col="total"):
    """Run a COUNT query and return the integer result, or 0 on failure."""
    df = _safe_fetch(query)
    if df.empty or col not in df.columns:
        return 0
    return int(df[col].iloc[0])


def _wins_df():
    """
    Returns a DataFrame with columns [nome_selecao, vitorias] sorted DESC.
    Adjust column names (id_selecao_mandante, gols_mandante, etc.) to match
    your actual schema.
    """
    query = """
        SELECT
            s.nome AS nome_selecao,
            COUNT(*) AS vitorias
        FROM partidas p
        JOIN selecoes s
          ON (
              (p.id_selecao_mandante  = s.id AND p.gols_mandante  > p.gols_visitante)
           OR (p.id_selecao_visitante = s.id AND p.gols_visitante > p.gols_mandante)
          )
        GROUP BY s.id, s.nome
        ORDER BY vitorias DESC
        LIMIT 10;
    """
    return _safe_fetch(query)


# ─── Stat card builder ───────────────────────────────────────────────────────

_CARD_DEFS = [
    # (label, stat_id, sub,          icon_class,                   bg_class,        href)
    ("SELEÇÕES",      "stat-selecoes",  "cadastradas",  "fa-solid fa-flag",             "ic-blue",    "/selecoes"),
    ("JOGADORES",     "stat-jogadores", "cadastrados",  "fa-solid fa-users",            "ic-green",   "/jogadores"),
    ("ESTÁDIOS",      "stat-estadios",  "cadastrados",  "fa-solid fa-map-location-dot", "ic-teal",    "/estadios"),
    ("PARTIDAS",      "stat-partidas",  "realizadas",   "fa-solid fa-futbol",           "ic-red",     "/partidas"),
    ("TOTAL DE GOLS", "stat-gols",      "marcados",     "fa-solid fa-fire",             "ic-purple",  "/partidas"),
    ("MÉDIA DE GOLS", "stat-media",     "por partida",  "fa-solid fa-calculator",       "ic-orange",  "/partidas"),
]

def _stat_card(label, stat_id, sub, icon_cls, bg_cls, href):
    return dcc.Link(
        html.Div([
            html.Div([
                html.Span(label,                     className="card-label"),
                html.Span(id=stat_id,                className="card-value"),
                html.Span(sub,                       className="card-sub"),
            ], className="card-text"),
            html.Div(
                html.I(className=icon_cls),
                className=f"card-icon {bg_cls}",
            ),
        ], className="stat-card"),
        href=href,
        className="stat-card-link",
    )

def _stat_cards_row():
    return html.Div(
        [_stat_card(*d) for d in _CARD_DEFS],
        className="cards-row",
    )


# ─── Wins bar chart ──────────────────────────────────────────────────────────

def _wins_chart(df: pd.DataFrame):
    if df.empty or "nome_selecao" not in df.columns:
        # Placeholder when DB is offline
        teams = ["Brasil","Argentina","França","Alemanha","Itália",
                 "Espanha","Inglaterra","Holanda","Uruguai","Portugal"]
        wins  = [0] * 10
    else:
        teams = df["nome_selecao"].tolist()
        wins  = df["vitorias"].tolist()

    max_w = max(wins) if wins else 1

    # Colour each bar: winner gets brand green, rest get light slate
    colors = []
    for w in wins:
        colors.append("#10B981" if w == max_w and max_w > 0 else "#E2E8F0")

    fig = go.Figure(go.Bar(
        x=wins,
        y=teams,
        orientation="h",
        marker_color=colors,
        marker_line_width=0,
        text=wins,
        textposition="outside",
        textfont=dict(size=11, color="#1E293B", family="Inter"),
        hovertemplate="%{y}: %{x} vitórias<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=0, r=40, t=0, b=0),
        height=380,
        xaxis=dict(
            showgrid=False, showticklabels=False, showline=False,
            range=[0, max(wins + [1]) * 1.25],
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=11, color="#475569", family="Inter"),
            showgrid=False, showline=False,
        ),
        bargap=0.35,
        font=dict(family="Inter"),
    )

    return dcc.Graph(
        figure=fig,
        config={"displayModeBar": False},
        className="wins-chart",
    )


# ─── Top-3 podium ────────────────────────────────────────────────────────────

_PODIUM_STYLES = [
    ("1", "medal-gold",   "border-gold"),
    ("2", "medal-silver", "border-silver"),
    ("3", "medal-bronze", "border-bronze"),
]

def _top3_card(pos_label, medal_cls, border_cls, team_name, wins):
    return html.Div([
        html.Div(pos_label, className=f"medal {medal_cls}"),
        html.Span(team_name, className="podium-team"),
        html.Span(f"{wins} vitórias", className="podium-wins"),
    ], className=f"podium-card {border_cls}")

def _top3_panel(df: pd.DataFrame):
    if df.empty or "nome_selecao" not in df.columns:
        entries = [("Brasil", 0), ("Argentina", 0), ("França", 0)]
    else:
        entries = list(zip(df["nome_selecao"].head(3), df["vitorias"].head(3)))
        while len(entries) < 3:
            entries.append(("—", 0))

    cards = [
        _top3_card(sty[0], sty[1], sty[2], entries[i][0], entries[i][1])
        for i, sty in enumerate(_PODIUM_STYLES)
    ]
    return html.Div([
        html.H4("TOP 3 SELEÇÕES", className="section-title"),
        html.Div(cards, className="podium-list"),
    ], className="top3-panel card-panel")


# ─── Page layout (called once on first load, stats filled via callback) ───────

def layout():
    wins_df = _wins_df()

    return html.Div([
        # Page heading
        html.Div([
            html.H2("Dashboard",                               className="page-title"),
            html.P("Visão geral dos dados da Copa do Mundo",   className="page-sub"),
        ], className="page-header"),

        # Stat cards row
        _stat_cards_row(),

        # Bottom: chart + top-3
        html.Div([
            html.Div([
                html.H4("RANKING DE VITÓRIAS POR SELEÇÃO", className="section-title"),
                _wins_chart(wins_df),
            ], className="chart-panel card-panel"),

            _top3_panel(wins_df),
        ], className="bottom-row"),

        # Hidden interval to refresh stats once on load
        dcc.Interval(id="dash-refresh", interval=999999, n_intervals=0, max_intervals=1),
    ], className="dashboard-wrap animate-fade-in")


# ─── Callback: populate stat card values ─────────────────────────────────────

@callback(
    [
        Output("stat-selecoes",  "children"),
        Output("stat-jogadores", "children"),
        Output("stat-estadios",  "children"),
        Output("stat-partidas",  "children"),
        Output("stat-gols",      "children"),
        Output("stat-media",     "children"),
    ],
    Input("dash-refresh", "n_intervals"),
)
def refresh_stats(_):
    # ── Adjust table/column names below if your schema differs ──────────────
    n_selecoes  = _count("SELECT COUNT(*) AS total FROM selecoes")
    n_jogadores = _count("SELECT COUNT(*) AS total FROM jogadores")
    n_estadios  = _count("SELECT COUNT(*) AS total FROM estadios")
    n_partidas  = _count("SELECT COUNT(*) AS total FROM partidas")

    gols_df = _safe_fetch(
        "SELECT COALESCE(SUM(gols_mandante + gols_visitante), 0) AS total FROM partidas"
        # ↑ Replace gols_mandante / gols_visitante with your actual column names
    )
    total_gols = int(gols_df["total"].iloc[0]) if not gols_df.empty and "total" in gols_df.columns else 0
    media_gols = f"{(total_gols / n_partidas):.2f}" if n_partidas > 0 else "0.00"

    return (
        str(n_selecoes),
        str(n_jogadores),
        str(n_estadios),
        str(n_partidas),
        str(total_gols),
        media_gols,
    )