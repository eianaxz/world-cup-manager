"""
app.py — World Cup Manager 2026
Ponto de entrada da aplicação Dash.
"""

import dash
from dash import html, dcc, Input, Output

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="World Cup Manager 2026",
    update_title=None,
)

# Necessário para deploy em produção (Railway, etc.)
server = app.server

# Layout raiz: apenas um container de rota
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content"),
])


# ── roteamento ──────────────────────────────────────────────────────────────────

@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    """Renderiza a página de acordo com a URL."""

    # Dashboard
    if pathname in ("/", "/dashboard"):
        from pages.dashboard import layout
        return layout()

    # Seleções
    if pathname == "/selecoes":
        try:
            from pages.selecoes import layout
            return layout()
        except Exception:
            return _placeholder("Seleções")

    # Jogadores
    if pathname == "/jogadores":
        try:
            from pages.jogadores import layout
            return layout()
        except Exception:
            return _placeholder("Jogadores")

    # Estádios
    if pathname == "/estadios":
        try:
            from pages.estadios import layout
            return layout()
        except Exception:
            return _placeholder("Estádios")

    # Partidas
    if pathname == "/partidas":
        try:
            from pages.partidas import layout
            return layout()
        except Exception:
            return _placeholder("Partidas")

    # Ranking de Vitórias
    if pathname == "/ranking":
        try:
            from pages.ranking import layout
            return layout()
        except Exception:
            return _placeholder("Ranking de Vitórias")

    # 404
    return html.Div(
        style={"textAlign": "center", "padding": "80px"},
        children=[
            html.H2("404 — Página não encontrada"),
            dcc.Link("← Voltar ao Dashboard", href="/"),
        ],
    )


def _placeholder(name):
    """Placeholder para páginas ainda não implementadas."""
    return html.Div(
        style={"padding": "60px", "textAlign": "center", "color": "#64748B"},
        children=[
            html.H2(name, style={"color": "#1E293B"}),
            html.P("Esta página está em construção."),
            dcc.Link("← Voltar ao Dashboard", href="/"),
        ],
    )


if __name__ == "__main__":
    app.run(debug=True)