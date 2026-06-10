"""
World Cup Manager 2026 — pages/dashboard.py
Dashboard principal: cards de estatísticas, ranking de vitórias (top 10)
e Top 3 seleções — todos via stored procedure sp_ranking_vitorias.
"""

import dash
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd

dash.register_page(__name__, path="/", name="Dashboard")

# ── Mesma constante do ranking.py — manter sincronizadas ─────────────────────
RANKING_PROCEDURE = "sp_ranking_vitorias"


# ── Helpers compartilhados ────────────────────────────────────────────────────

def _safe_fetch(query, params=None):
    """Executa fetch_data com fallback silencioso."""
    try:
        from config.database import fetch_data
        return fetch_data(query, params)
    except Exception as e:
        print(f"[dashboard] DB fetch failed: {e}")
        return pd.DataFrame()


def _count(query, col="total"):
    df = _safe_fetch(query)
    if df.empty or col not in df.columns:
        return 0
    return int(df[col].iloc[0])


def get_ranking_vitorias() -> pd.DataFrame:
    """
    Chama sp_ranking_vitorias e retorna DataFrame normalizado.
    Função idêntica à de pages/ranking.py — usa a mesma procedure
    como fonte única de verdade para Dashboard e tela de Ranking.
    """
    try:
        from config.database import fetch_data
        df = fetch_data(f"CALL {RANKING_PROCEDURE}();")
        if df is None or df.empty:
            return pd.DataFrame(columns=["posicao", "nome_selecao", "vitorias"])

        df.columns = [c.lower() for c in df.columns]

        if "vitorias" not in df.columns:
            for alias in ["wins", "victories", "num_vitorias", "total_vitorias"]:
                if alias in df.columns:
                    df = df.rename(columns={alias: "vitorias"})
                    break
            else:
                df["vitorias"] = 0

        if "nome_selecao" not in df.columns:
            for alias in ["nome", "selecao", "team", "name"]:
                if alias in df.columns:
                    df = df.rename(columns={alias: "nome_selecao"})
                    break

        df["vitorias"] = pd.to_numeric(df["vitorias"], errors="coerce").fillna(0).astype(int)
        df = df.sort_values("vitorias", ascending=False).reset_index(drop=True)

        if "posicao" not in df.columns:
            df["posicao"] = df.index + 1

        return df[["posicao", "nome_selecao", "vitorias"]]

    except Exception as e:
        print(f"[dashboard] Erro ao chamar {RANKING_PROCEDURE}: {e}")
        return pd.DataFrame(columns=["posicao", "nome_selecao", "vitorias"])


# ── Stat card builder ─────────────────────────────────────────────────────────

_CARD_DEFS = [
    ("SELEÇÕES",      "stat-selecoes",  "cadastradas",  "fa-solid fa-flag",             "ic-blue",   "/selecoes"),
    ("JOGADORES",     "stat-jogadores", "cadastrados",  "fa-solid fa-users",            "ic-green",  "/jogadores"),
    ("ESTÁDIOS",      "stat-estadios",  "cadastrados",  "fa-solid fa-map-location-dot", "ic-teal",   "/estadios"),
    ("PARTIDAS",      "stat-partidas",  "realizadas",   "fa-solid fa-futbol",           "ic-red",    "/partidas"),
    ("TOTAL DE GOLS", "stat-gols",      "marcados",     "fa-solid fa-fire",             "ic-purple", "/partidas"),
    ("MÉDIA DE GOLS", "stat-media",     "por partida",  "fa-solid fa-calculator",       "ic-orange", "/partidas"),
]


def _stat_card(label, stat_id, sub, icon_cls, bg_cls, href):
    return dcc.Link(
        html.Div([
            html.Div([
                html.Span(label,   className="card-label"),
                html.Span(id=stat_id, className="card-value"),
                html.Span(sub,     className="card-sub"),
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
    return html.Div([_stat_card(*d) for d in _CARD_DEFS], className="cards-row")


# ── Wins bar chart (top 10) ───────────────────────────────────────────────────

def _wins_chart(df: pd.DataFrame):
    """Exibe top 10 no gráfico do Dashboard."""
    top = df.head(10) if not df.empty else pd.DataFrame(columns=["nome_selecao", "vitorias"])

    if top.empty:
        teams  = []
        wins   = []
    else:
        teams = top["nome_selecao"].tolist()
        wins  = top["vitorias"].tolist()

    max_w  = max(wins) if wins else 1
    colors = ["#10B981" if w == max_w and max_w > 0 else "#E2E8F0" for w in wins]

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
            range=[0, max_w * 1.25],
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


# ── Top-3 podium ──────────────────────────────────────────────────────────────

_PODIUM_STYLES = [
    ("1", "medal-gold",   "border-gold"),
    ("2", "medal-silver", "border-silver"),
    ("3", "medal-bronze", "border-bronze"),
]


def _top3_card(pos_label, medal_cls, border_cls, team_name, wins):
    return html.Div([
        html.Div(pos_label, className=f"medal {medal_cls}"),
        html.Span(team_name,         className="podium-team"),
        html.Span(f"{wins} vitórias", className="podium-wins"),
    ], className=f"podium-card {border_cls}")


def _top3_panel(df: pd.DataFrame):
    """Exibe top 3 na coluna lateral do Dashboard."""
    if df.empty or "nome_selecao" not in df.columns:
        entries = [("—", 0), ("—", 0), ("—", 0)]
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


# ── Page layout ───────────────────────────────────────────────────────────────

def layout():
    # Procedure é chamada uma vez no carregamento do layout
    wins_df = get_ranking_vitorias()

    return html.Div([
        html.Div([
            html.H2("Dashboard",                             className="page-title"),
            html.P("Visão geral dos dados da Copa do Mundo", className="page-sub"),
        ], className="page-header"),

        _stat_cards_row(),

        html.Div([
            html.Div([
                html.H4("RANKING DE VITÓRIAS POR SELEÇÃO", className="section-title"),
                _wins_chart(wins_df),
            ], className="chart-panel card-panel"),

            _top3_panel(wins_df),
        ], className="bottom-row"),

        dcc.Interval(id="dash-refresh", interval=999999, n_intervals=0, max_intervals=1),
    ], className="dashboard-wrap animate-fade-in")


# ── Callback: preencher stat cards ────────────────────────────────────────────

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
    # Ajuste os nomes de tabela/coluna conforme seu schema real
    n_selecoes  = _count("SELECT COUNT(*) AS total FROM selecoes")
    n_jogadores = _count("SELECT COUNT(*) AS total FROM jogadores")
    n_estadios  = _count("SELECT COUNT(*) AS total FROM estadios")
    n_partidas  = _count("SELECT COUNT(*) AS total FROM partidas")

    gols_df = _safe_fetch(
        "SELECT COALESCE(SUM(gols_mandante + gols_visitante), 0) AS total FROM partidas"
        # ↑ Substitua gols_mandante / gols_visitante pelos nomes reais das colunas
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