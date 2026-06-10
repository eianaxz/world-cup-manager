"""
World Cup Manager 2026 — pages/ranking.py
Tela de Ranking de Vitórias: consome a stored procedure sp_ranking_vitorias
e exibe cards de destaque, gráfico de barras horizontais e tabela completa.
"""

import dash
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd

dash.register_page(__name__, path="/ranking", name="Ranking de Vitórias")

# ── Constante para o nome da procedure — ajuste se necessário ─────────────────
RANKING_PROCEDURE = "sp_ranking_vitorias"


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_ranking_vitorias() -> pd.DataFrame:
    """
    Chama a stored procedure e retorna um DataFrame com o ranking de vitórias.
    Espera colunas: posicao (opcional), nome_selecao, vitorias.
    Se 'posicao' não vier da procedure, é calculada aqui para exibição.
    Ajuste RANKING_PROCEDURE acima caso o nome real seja diferente.
    """
    try:
        from config.database import fetch_data
        df = fetch_data(f"CALL {RANKING_PROCEDURE}();")
        if df is None or df.empty:
            return pd.DataFrame(columns=["posicao", "nome_selecao", "vitorias"])

        # Normalizar nomes de colunas para minúsculas
        df.columns = [c.lower() for c in df.columns]

        # Garantir coluna 'vitorias'
        if "vitorias" not in df.columns:
            # Tentar aliases comuns
            for alias in ["wins", "victories", "num_vitorias", "total_vitorias"]:
                if alias in df.columns:
                    df = df.rename(columns={alias: "vitorias"})
                    break
            else:
                df["vitorias"] = 0

        # Garantir coluna 'nome_selecao'
        if "nome_selecao" not in df.columns:
            for alias in ["nome", "selecao", "team", "name"]:
                if alias in df.columns:
                    df = df.rename(columns={alias: "nome_selecao"})
                    break

        df["vitorias"] = pd.to_numeric(df["vitorias"], errors="coerce").fillna(0).astype(int)
        df = df.sort_values("vitorias", ascending=False).reset_index(drop=True)

        # Calcular posição se não vier da procedure
        if "posicao" not in df.columns:
            df["posicao"] = df.index + 1

        return df[["posicao", "nome_selecao", "vitorias"]]

    except Exception as e:
        print(f"[ranking] Erro ao chamar {RANKING_PROCEDURE}: {e}")
        return pd.DataFrame(columns=["posicao", "nome_selecao", "vitorias"])


# ── Cards de destaque ─────────────────────────────────────────────────────────

def _highlight_cards(df: pd.DataFrame):
    if df.empty:
        lider_nome    = "—"
        lider_vitorias = 0
        total_selecoes = 0
        max_vitorias   = 0
    else:
        lider_nome     = str(df.iloc[0]["nome_selecao"])
        lider_vitorias = int(df.iloc[0]["vitorias"])
        total_selecoes = len(df)
        max_vitorias   = int(df["vitorias"].max())

    cards = [
        # 1º lugar — destaque dourado
        html.Div([
            html.Div([
                html.Span("1º LUGAR", className="card-label"),
                html.Span(lider_nome,          className="card-value", style={"color": "#B45309", "fontSize": "22px"}),
                html.Span(f"{lider_vitorias} vitórias", className="card-sub"),
            ], className="card-text"),
            html.Div(
                html.I(className="fa-solid fa-trophy"),
                className="card-icon",
                style={"background": "#FEF9C3", "color": "#CA8A04"},
            ),
        ], className="stat-card", style={"borderLeft": "4px solid #FACC15"}),

        # Total de seleções ranqueadas
        html.Div([
            html.Div([
                html.Span("SELEÇÕES RANQUEADAS", className="card-label"),
                html.Span(str(total_selecoes), className="card-value"),
                html.Span("no ranking",        className="card-sub"),
            ], className="card-text"),
            html.Div(
                html.I(className="fa-solid fa-flag"),
                className="card-icon ic-blue",
            ),
        ], className="stat-card"),

        # Maior número de vitórias
        html.Div([
            html.Div([
                html.Span("MÁXIMO DE VITÓRIAS", className="card-label"),
                html.Span(str(max_vitorias),   className="card-value"),
                html.Span("pela líder",        className="card-sub"),
            ], className="card-text"),
            html.Div(
                html.I(className="fa-solid fa-ranking-star"),
                className="card-icon ic-green",
            ),
        ], className="stat-card"),
    ]

    return html.Div(cards, className="cards-row", style={"gridTemplateColumns": "repeat(3, 1fr)"})


# ── Gráfico de barras horizontais ─────────────────────────────────────────────

def _ranking_chart(df: pd.DataFrame):
    if df.empty:
        teams  = []
        wins   = []
        max_w  = 1
        colors = []
    else:
        teams  = df["nome_selecao"].tolist()
        wins   = df["vitorias"].tolist()
        max_w  = max(wins) if max(wins) > 0 else 1
        colors = [
            "#10B981" if i == 0 else "#3B82F6"
            for i in range(len(wins))
        ]

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
        margin=dict(l=0, r=50, t=0, b=0),
        height=max(320, len(teams) * 36) if teams else 200,
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            showline=False,
            range=[0, max_w * 1.25],
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=12, color="#475569", family="Inter"),
            showgrid=False,
            showline=False,
        ),
        bargap=0.35,
        font=dict(family="Inter"),
    )

    return dcc.Graph(
        figure=fig,
        config={"displayModeBar": False},
        style={"width": "100%"},
    )


# ── Tabela completa ───────────────────────────────────────────────────────────

_MEDAL_STYLES = {
    1: {"background": "#FACC15", "color": "#1C1917", "border": "2px solid #FDE68A"},
    2: {"background": "#CBD5E1", "color": "#334155", "border": "2px solid #E2E8F0"},
    3: {"background": "#F97316", "color": "#FFFFFF", "border": "2px solid #FDBA74"},
}

_BORDER_LEFT = {
    1: "4px solid #FACC15",
    2: "4px solid #CBD5E1",
    3: "4px solid #F97316",
}


def _ranking_table(df: pd.DataFrame):
    if df.empty:
        body = html.Tr(
            html.Td(
                "Ainda não há vitórias registradas.",
                colSpan=3,
                className="empty-row",
            )
        )
        rows = [body]
    else:
        rows = []
        for _, row in df.iterrows():
            pos    = int(row["posicao"])
            nome   = str(row["nome_selecao"])
            vit    = int(row["vitorias"])

            # Badge de posição
            if pos in _MEDAL_STYLES:
                badge = html.Span(
                    f"{pos}º",
                    style={
                        "width": "32px", "height": "32px",
                        "borderRadius": "50%",
                        "display": "inline-flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "fontSize": "11px", "fontWeight": "800",
                        **_MEDAL_STYLES[pos],
                    }
                )
                row_style = {"borderLeft": _BORDER_LEFT[pos]}
            else:
                badge = html.Span(
                    f"{pos}º",
                    style={"fontWeight": "700", "color": "#94A3B8", "fontSize": "12px"},
                )
                row_style = {}

            tr = html.Tr([
                html.Td(badge,  style={"textAlign": "center", "width": "80px",  "padding": "14px 16px"}),
                html.Td(nome,   className="td-bold",  style={"padding": "14px 16px"}),
                html.Td(str(vit), className="td-mono", style={"padding": "14px 16px"}),
            ], className="table-row", style=row_style)

            rows.append(tr)

    return html.Div(
        html.Div([
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Pos.",     className="th th-center"),
                        html.Th("Seleção",  className="th"),
                        html.Th("Vitórias", className="th th-center"),
                    ], className="thead-row")
                ),
                html.Tbody(rows),
            ], className="data-table"),
        ], className="table-card"),
    )


# ── Layout ────────────────────────────────────────────────────────────────────

def layout():
    df = get_ranking_vitorias()

    empty_msg = None
    if df.empty:
        empty_msg = html.Div(
            "Ainda não há vitórias registradas.",
            style={
                "background": "#F8FAFC",
                "border": "1px dashed #CBD5E1",
                "borderRadius": "12px",
                "padding": "32px",
                "textAlign": "center",
                "color": "#94A3B8",
                "fontSize": "13px",
                "fontWeight": "600",
            }
        )

    chart_section = html.Div([
        html.H4("RANKING COMPLETO — BARRAS", className="section-title"),
        _ranking_chart(df) if not df.empty else html.Div(
            "Sem dados para exibir.",
            style={"color": "#94A3B8", "fontSize": "13px", "padding": "20px 0"},
        ),
    ], className="card-panel", style={"marginBottom": "20px"})

    table_section = html.Div([
        html.H4("CLASSIFICAÇÃO DETALHADA", className="section-title"),
        _ranking_table(df),
    ], className="card-panel")

    return html.Div([
        # Cabeçalho
        html.Div([
            html.H2("Ranking de Vitórias",                              className="page-title"),
            html.P("Classificação das seleções por número de vitórias", className="page-sub"),
        ], className="page-header"),

        # Cards de destaque
        _highlight_cards(df),

        # Mensagem de estado vazio (só aparece se df vazio)
        empty_msg or html.Div(),

        # Gráfico
        chart_section,

        # Tabela completa
        table_section,

        # Intervalo para refresh único ao carregar
        dcc.Interval(id="ranking-refresh", interval=999999, n_intervals=0, max_intervals=1),
    ], className="dashboard-wrap animate-fade-in")


# ── Callback de refresh ───────────────────────────────────────────────────────

@callback(
    Output("ranking-refresh", "disabled"),
    Input("ranking-refresh", "n_intervals"),
    prevent_initial_call=True,
)
def _on_load(_):
    """Placeholder para possível lógica de refresh futuro."""
    return True