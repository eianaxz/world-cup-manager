from dash import html, dcc, callback, Input, Output, State, ctx, no_update, ALL
import dash_bootstrap_components as dbc
import dash
from config.database import get_connection

dash.register_page(__name__, path="/selecoes", name="Seleções")

# ── constantes ────────────────────────────────────────────────────────────────

CONTINENTE_CORES = {
    "América do Sul":   "#22c55e",
    "Europa":           "#3b82f6",
    "África":           "#f59e0b",
    "Ásia":             "#a855f7",
    "América do Norte": "#f97316",
    "Oceania":          "#06b6d4",
}

# ── helpers ───────────────────────────────────────────────────────────────────

def _dot(continente: str) -> html.Span:
    cor = CONTINENTE_CORES.get(continente, "#94a3b8")
    return html.Span(style={
        "display": "inline-block", "width": "10px", "height": "10px",
        "borderRadius": "50%", "backgroundColor": cor,
        "marginRight": "10px", "flexShrink": "0",
    })

def _fetch_selecoes():
    try:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id_selecao, nome_selecao, continente, tecnico, titulos
            FROM selecoes ORDER BY nome_selecao
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows
    except Exception as e:
        print(f"Erro ao buscar seleções: {e}")
        return []

# ── estilos inline compartilhados ────────────────────────────────────────────

_BTN_EDIT = {
    "padding": "7px 10px", "cursor": "pointer",
    "backgroundColor": "#f8fafc", "color": "#475569",
    "border": "1px solid #e2e8f0", "borderRadius": "8px",
    "fontSize": "11px", "marginRight": "4px",
    "transition": "all .15s",
}
_BTN_DEL = {
    "padding": "7px 10px", "cursor": "pointer",
    "backgroundColor": "#f8fafc", "color": "#475569",
    "border": "1px solid #e2e8f0", "borderRadius": "8px",
    "fontSize": "11px",
    "transition": "all .15s",
}
_TH = {
    "fontSize": "10px", "fontWeight": "800",
    "textTransform": "uppercase", "letterSpacing": "0.06em",
    "color": "#64748b", "padding": "13px 16px",
    "backgroundColor": "#f8fafc",
    "borderBottom": "1px solid #e2e8f0",
}
_TD = {"padding": "14px 16px", "fontSize": "12px", "color": "#475569", "fontWeight": "500"}
_TD_NOME = {"padding": "14px 16px 14px 24px", "fontSize": "12px",
            "color": "#1e293b", "fontWeight": "700"}

# ── tabela ────────────────────────────────────────────────────────────────────

def _tbody(selecoes: list) -> list:
    if not selecoes:
        return [html.Tr(html.Td(
            "Nenhuma seleção cadastrada.",
            colSpan=5,
            style={"textAlign": "center", "padding": "48px",
                   "color": "#94a3b8", "fontSize": "12px"},
        ))]

    linhas = []
    for s in selecoes:
        linhas.append(html.Tr(
            style={"borderBottom": "1px solid #f1f5f9", "transition": "background .15s"},
            className="tr-hover",
            children=[
                # Nome
                html.Td(
                    html.Div([_dot(s.get("continente", "")), s.get("nome_selecao", "")],
                             style={"display": "flex", "alignItems": "center"}),
                    style=_TD_NOME,
                ),
                # Continente
                html.Td(s.get("continente", ""), style=_TD),
                # Técnico
                html.Td(s.get("tecnico", ""),    style=_TD),
                # Títulos — badge numérico
                html.Td(
                    html.Span(
                        str(s.get("titulos", 0)),
                        style={
                            "fontFamily": "monospace", "fontWeight": "700",
                            "color": "#1e293b", "fontSize": "12px",
                        }
                    ),
                    style=_TD,
                ),
                # Ações
                html.Td(
                    html.Div([
                        html.Button(
                            html.I(className="fa-solid fa-pen"),
                            id={"type": "btn-edit-selecao", "index": s["id_selecao"]},
                            title="Editar", n_clicks=0,
                            style=_BTN_EDIT,
                        ),
                        html.Button(
                            html.I(className="fa-solid fa-trash-can"),
                            id={"type": "btn-delete-selecao", "index": s["id_selecao"]},
                            title="Excluir", n_clicks=0,
                            style=_BTN_DEL,
                        ),
                    ], style={"display": "flex", "justifyContent": "center"}),
                    style={"padding": "14px 16px", "textAlign": "center"},
                ),
            ],
        ))
    return linhas

# ── modal cadastro / edição ───────────────────────────────────────────────────

_LABEL_STYLE = {
    "fontSize": "9px", "fontWeight": "700", "textTransform": "uppercase",
    "letterSpacing": "0.07em", "color": "#94a3b8", "marginBottom": "4px",
    "display": "block",
}
_INPUT_STYLE = {
    "width": "100%", "backgroundColor": "#f8fafc", "fontSize": "12px",
    "color": "#1e293b", "padding": "9px 12px", "borderRadius": "8px",
    "border": "1px solid #e2e8f0", "outline": "none",
    "fontFamily": "Inter, sans-serif",
}
_SELECT_STYLE = {**_INPUT_STYLE, "cursor": "pointer"}

def _modal():
    continentes = list(CONTINENTE_CORES.keys())
    return html.Div(
        id="modal-selecao-overlay",
        style={"display": "none"},
        children=html.Div(
            style={
                "position": "fixed", "inset": "0",
                "backgroundColor": "rgba(15,23,42,.45)",
                "backdropFilter": "blur(3px)",
                "zIndex": "1000",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
            },
            children=html.Div(
                style={
                    "backgroundColor": "#fff",
                    "border": "1px solid #e2e8f0",
                    "borderRadius": "20px",
                    "width": "100%", "maxWidth": "440px",
                    "overflow": "hidden",
                    "boxShadow": "0 20px 40px -10px rgba(0,0,0,.12)",
                },
                children=[
                    # Header do modal
                    html.Div(
                        html.Div([
                            html.I(className="fa-solid fa-flag",
                                   style={"color": "#2563eb", "marginRight": "8px", "fontSize": "12px"}),
                            html.Span(id="modal-selecao-titulo", children="Nova Seleção",
                                      style={"fontSize": "12px", "fontWeight": "800",
                                             "textTransform": "uppercase", "letterSpacing": "0.05em",
                                             "color": "#1e293b"}),
                        ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between"}),
                        style={
                            "backgroundColor": "#f8fafc",
                            "borderBottom": "1px solid #e2e8f0",
                            "padding": "18px 24px",
                        }
                    ),
                    # Body
                    html.Div([
                        dcc.Store(id="edit-selecao-id", data=None),

                        # Nome
                        html.Div([
                            html.Label("Nome da Seleção", style=_LABEL_STYLE),
                            dcc.Input(id="input-nome-selecao", type="text",
                                      placeholder="Ex: Brasil, Argentina, Portugal...",
                                      maxLength=100, style=_INPUT_STYLE),
                        ], style={"marginBottom": "16px"}),

                        # Continente + Títulos
                        html.Div([
                            html.Div([
                                html.Label("Continente", style=_LABEL_STYLE),
                                dcc.Dropdown(
                                    id="input-continente-selecao",
                                    options=[{"label": c, "value": c} for c in continentes],
                                    clearable=False,
                                    style={"fontSize": "12px"},
                                ),
                            ], style={"flex": "1", "marginRight": "12px"}),
                            html.Div([
                                html.Label("Títulos Mundiais", style=_LABEL_STYLE),
                                dcc.Input(id="input-titulos-selecao", type="number",
                                          min=0, value=0, style=_INPUT_STYLE),
                            ], style={"width": "120px"}),
                        ], style={"display": "flex", "marginBottom": "16px"}),

                        # Técnico
                        html.Div([
                            html.Label("Técnico Principal", style=_LABEL_STYLE),
                            dcc.Input(id="input-tecnico-selecao", type="text",
                                      placeholder="Ex: Roberto Martínez, Lionel Scaloni...",
                                      maxLength=100, style=_INPUT_STYLE),
                        ], style={"marginBottom": "8px"}),

                        html.Div(id="modal-selecao-erro",
                                 style={"color": "#ef4444", "fontSize": "11px", "marginTop": "4px"}),
                    ], style={"padding": "24px"}),

                    # Footer
                    html.Div([
                        html.Button("Cancelar", id="btn-cancelar-selecao", n_clicks=0,
                                    style={
                                        "padding": "8px 16px", "borderRadius": "8px",
                                        "border": "none", "backgroundColor": "#f1f5f9",
                                        "color": "#475569", "fontSize": "11px",
                                        "fontWeight": "700", "textTransform": "uppercase",
                                        "cursor": "pointer", "marginRight": "8px",
                                    }),
                        html.Button("Salvar Dados", id="btn-salvar-selecao", n_clicks=0,
                                    style={
                                        "padding": "8px 18px", "borderRadius": "8px",
                                        "border": "none", "backgroundColor": "#2563eb",
                                        "color": "#fff", "fontSize": "11px",
                                        "fontWeight": "700", "textTransform": "uppercase",
                                        "cursor": "pointer",
                                    }),
                    ], style={
                        "padding": "16px 24px",
                        "borderTop": "1px solid #f1f5f9",
                        "display": "flex", "justifyContent": "flex-end",
                    }),
                ]
            )
        )
    )

def _modal_confirmar_delete():
    return html.Div(
        id="modal-delete-overlay",
        style={"display": "none"},
        children=html.Div(
            style={
                "position": "fixed", "inset": "0",
                "backgroundColor": "rgba(15,23,42,.45)",
                "backdropFilter": "blur(3px)",
                "zIndex": "1000",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
            },
            children=html.Div(
                style={
                    "backgroundColor": "#fff", "border": "1px solid #e2e8f0",
                    "borderRadius": "20px", "width": "100%", "maxWidth": "360px",
                    "overflow": "hidden",
                    "boxShadow": "0 20px 40px -10px rgba(0,0,0,.12)",
                },
                children=[
                    html.Div(
                        html.Div([
                            html.I(className="fa-solid fa-triangle-exclamation",
                                   style={"color": "#ef4444", "marginRight": "8px"}),
                            html.Span("Confirmar exclusão",
                                      style={"fontSize": "12px", "fontWeight": "800",
                                             "textTransform": "uppercase", "color": "#1e293b"}),
                        ], style={"display": "flex", "alignItems": "center"}),
                        style={"backgroundColor": "#f8fafc",
                               "borderBottom": "1px solid #e2e8f0", "padding": "18px 24px"},
                    ),
                    html.Div([
                        dcc.Store(id="delete-selecao-id", data=None),
                        html.P("Tem certeza que deseja excluir esta seleção? Esta ação não pode ser desfeita.",
                               style={"fontSize": "12px", "color": "#475569", "margin": 0}),
                    ], style={"padding": "24px"}),
                    html.Div([
                        html.Button("Cancelar", id="btn-cancelar-delete-selecao", n_clicks=0,
                                    style={
                                        "padding": "8px 16px", "borderRadius": "8px",
                                        "border": "none", "backgroundColor": "#f1f5f9",
                                        "color": "#475569", "fontSize": "11px",
                                        "fontWeight": "700", "textTransform": "uppercase",
                                        "cursor": "pointer", "marginRight": "8px",
                                    }),
                        html.Button("Excluir", id="btn-confirmar-delete-selecao", n_clicks=0,
                                    style={
                                        "padding": "8px 18px", "borderRadius": "8px",
                                        "border": "none", "backgroundColor": "#ef4444",
                                        "color": "#fff", "fontSize": "11px",
                                        "fontWeight": "700", "textTransform": "uppercase",
                                        "cursor": "pointer",
                                    }),
                    ], style={
                        "padding": "16px 24px", "borderTop": "1px solid #f1f5f9",
                        "display": "flex", "justifyContent": "flex-end",
                    }),
                ]
            )
        )
    )

# ── layout principal ──────────────────────────────────────────────────────────

def layout():
    selecoes = _fetch_selecoes()

    return html.Div([
        dcc.Store(id="store-selecoes", data=selecoes),



        # ── Cabeçalho ──────────────────────────────────────────────
        html.Div([
            html.Div([
                html.H2("Seleções", style={
                    "fontSize": "24px", "fontWeight": "800",
                    "color": "#0f172a", "margin": 0, "lineHeight": "1.2",
                }),
                html.P("Gerencie as seleções participantes", style={
                    "fontSize": "11px", "color": "#94a3b8",
                    "marginTop": "4px", "marginBottom": 0,
                }),
            ]),
            html.Button([
                html.I(className="fa-solid fa-plus",
                       style={"fontSize": "9px", "marginRight": "6px"}),
                "Nova Seleção",
            ],
                id="btn-nova-selecao", n_clicks=0,
                style={
                    "backgroundColor": "#2563eb", "color": "#fff",
                    "border": "none", "borderRadius": "12px",
                    "padding": "10px 22px", "fontWeight": "700",
                    "fontSize": "11px", "letterSpacing": "0.06em",
                    "cursor": "pointer", "textTransform": "uppercase",
                    "boxShadow": "0 4px 12px rgba(37,99,235,.25)",
                    "display": "flex", "alignItems": "center",
                },
            ),
        ], style={
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "center", "marginBottom": "24px",
        }),

        # ── Tabela ─────────────────────────────────────────────────
        html.Div(
            style={
                "backgroundColor": "#fff", "borderRadius": "20px",
                "border": "1px solid #e2e8f0", "overflow": "hidden",
                "boxShadow": "0 1px 3px rgba(0,0,0,.05), 0 1px 2px rgba(0,0,0,.04)",
            },
            children=html.Table(
                style={"width": "100%", "borderCollapse": "collapse"},
                children=[
                    html.Thead(html.Tr([
                        html.Th("Nome",       style={**_TH, "paddingLeft": "24px"}),
                        html.Th("Continente", style=_TH),
                        html.Th("Técnico",    style=_TH),
                        html.Th("Títulos",    style=_TH),
                        html.Th("Ações",      style={**_TH, "textAlign": "center"}),
                    ])),
                    html.Tbody(id="tbody-selecoes", children=_tbody(selecoes)),
                ],
            ),
        ),

        # ── Modais ─────────────────────────────────────────────────
        _modal(),
        _modal_confirmar_delete(),

        # ── Toast ──────────────────────────────────────────────────
        html.Div(id="toast-selecao-container", style={
            "position": "fixed", "top": "24px", "right": "24px",
            "zIndex": "9999",
        }),
    ], style={"padding": "32px"})


# ── callbacks ─────────────────────────────────────────────────────────────────

# Abrir modal nova seleção
@callback(
    Output("modal-selecao-overlay", "style", allow_duplicate=True),
    Output("modal-selecao-titulo", "children", allow_duplicate=True),
    Output("input-nome-selecao", "value", allow_duplicate=True),
    Output("input-continente-selecao", "value", allow_duplicate=True),
    Output("input-tecnico-selecao", "value", allow_duplicate=True),
    Output("input-titulos-selecao", "value", allow_duplicate=True),
    Output("edit-selecao-id", "data", allow_duplicate=True),
    Input("btn-nova-selecao", "n_clicks"),
    prevent_initial_call=True,
)
def abrir_modal_novo(n):
    if not n:
        return [no_update] * 7
    return {"display": "block"}, "Nova Seleção", "", None, "", 0, None


# Abrir modal de edição
@callback(
    Output("modal-selecao-overlay", "style", allow_duplicate=True),
    Output("modal-selecao-titulo", "children", allow_duplicate=True),
    Output("input-nome-selecao", "value", allow_duplicate=True),
    Output("input-continente-selecao", "value", allow_duplicate=True),
    Output("input-tecnico-selecao", "value", allow_duplicate=True),
    Output("input-titulos-selecao", "value", allow_duplicate=True),
    Output("edit-selecao-id", "data", allow_duplicate=True),
    Input({"type": "btn-edit-selecao", "index": ALL}, "n_clicks"),
    State("store-selecoes", "data"),
    prevent_initial_call=True,
)
def abrir_modal_edicao(n_clicks, selecoes):
    if not any(n_clicks):
        return [no_update] * 7
    triggered = ctx.triggered_id
    if not triggered:
        return [no_update] * 7
    sid = triggered["index"]
    s = next((x for x in selecoes if x["id_selecao"] == sid), None)
    if not s:
        return [no_update] * 7
    return (
        {"display": "block"}, "Editar Seleção",
        s["nome_selecao"], s["continente"], s["tecnico"], s["titulos"], sid,
    )


# Fechar modal
@callback(
    Output("modal-selecao-overlay", "style", allow_duplicate=True),
    Input("btn-cancelar-selecao", "n_clicks"),
    prevent_initial_call=True,
)
def fechar_modal(_):
    return {"display": "none"}


# Salvar (INSERT / UPDATE)
@callback(
    Output("modal-selecao-overlay", "style", allow_duplicate=True),
    Output("modal-selecao-erro", "children"),
    Output("store-selecoes", "data", allow_duplicate=True),
    Output("tbody-selecoes", "children", allow_duplicate=True),
    Output("toast-selecao-container", "children", allow_duplicate=True),
    Input("btn-salvar-selecao", "n_clicks"),
    State("edit-selecao-id", "data"),
    State("input-nome-selecao", "value"),
    State("input-continente-selecao", "value"),
    State("input-tecnico-selecao", "value"),
    State("input-titulos-selecao", "value"),
    prevent_initial_call=True,
)
def salvar_selecao(n, sid, nome, continente, tecnico, titulos):
    if not n:
        return [no_update] * 5

    if not nome or not continente or not tecnico:
        return no_update, "Preencha todos os campos obrigatórios.", no_update, no_update, no_update

    try:
        conn = get_connection()
        cur  = conn.cursor()
        if sid is None:
            cur.execute(
                "INSERT INTO selecoes (nome_selecao, continente, tecnico, titulos) VALUES (%s,%s,%s,%s)",
                (nome.strip(), continente, tecnico.strip(), int(titulos or 0)),
            )
            msg = f"Seleção '{nome}' cadastrada com sucesso!"
            icon = "fa-check-double"
            cor  = "#059669"
            bg   = "#f0fdf4"
            brd  = "#bbf7d0"
        else:
            cur.execute(
                "UPDATE selecoes SET nome_selecao=%s, continente=%s, tecnico=%s, titulos=%s WHERE id_selecao=%s",
                (nome.strip(), continente, tecnico.strip(), int(titulos or 0), sid),
            )
            msg = f"Seleção '{nome}' atualizada!"
            icon = "fa-check-double"
            cor  = "#059669"
            bg   = "#f0fdf4"
            brd  = "#bbf7d0"
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        return no_update, f"Erro ao salvar: {e}", no_update, no_update, no_update

    novas = _fetch_selecoes()
    toast = _toast(msg, icon, cor, bg, brd)
    return {"display": "none"}, "", novas, _tbody(novas), toast


# Abrir modal delete
@callback(
    Output("modal-delete-overlay", "style", allow_duplicate=True),
    Output("delete-selecao-id", "data"),
    Input({"type": "btn-delete-selecao", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def abrir_modal_delete(n_clicks):
    if not any(n_clicks):
        return no_update, no_update
    triggered = ctx.triggered_id
    if not triggered:
        return no_update, no_update
    return {"display": "block"}, triggered["index"]


@callback(
    Output("modal-delete-overlay", "style", allow_duplicate=True),
    Input("btn-cancelar-delete-selecao", "n_clicks"),
    prevent_initial_call=True,
)
def fechar_modal_delete(_):
    return {"display": "none"}


# Confirmar delete
@callback(
    Output("modal-delete-overlay", "style", allow_duplicate=True),
    Output("store-selecoes", "data", allow_duplicate=True),
    Output("tbody-selecoes", "children", allow_duplicate=True),
    Output("toast-selecao-container", "children", allow_duplicate=True),
    Input("btn-confirmar-delete-selecao", "n_clicks"),
    State("delete-selecao-id", "data"),
    prevent_initial_call=True,
)
def confirmar_delete(n, sid):
    if not n or not sid:
        return [no_update] * 4
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("DELETE FROM selecoes WHERE id_selecao = %s", (sid,))
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        toast = _toast(f"Erro ao excluir: {e}", "fa-triangle-exclamation", "#ef4444", "#fef2f2", "#fecaca")
        return {"display": "none"}, no_update, no_update, toast

    novas = _fetch_selecoes()
    toast = _toast("Seleção excluída com sucesso.", "fa-trash-can", "#ef4444", "#fef2f2", "#fecaca")
    return {"display": "none"}, novas, _tbody(novas), toast


# ── toast helper ──────────────────────────────────────────────────────────────

def _toast(msg, icon, cor, bg, brd):
    return html.Div([
        html.I(className=f"fa-solid {icon}", style={"marginRight": "8px"}),
        msg,
    ], style={
        "backgroundColor": bg, "border": f"1px solid {brd}",
        "color": cor, "borderRadius": "12px",
        "padding": "12px 18px", "fontSize": "12px", "fontWeight": "700",
        "boxShadow": "0 4px 12px rgba(0,0,0,.08)",
        "display": "flex", "alignItems": "center",
        "textTransform": "uppercase", "letterSpacing": "0.04em",
    })