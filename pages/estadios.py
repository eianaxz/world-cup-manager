from dash import html, dcc, callback, Input, Output, State, ctx, no_update, ALL
import dash
from config.database import get_connection

dash.register_page(__name__, path="/estadios", name="Estádios")

# ── helpers ───────────────────────────────────────────────────────────────────

def _fetch_estadios():
    try:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id_estadio, nome_estadio, cidade, pais, capacidade
            FROM estadios
            ORDER BY nome_estadio
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows
    except Exception as e:
        print(f"Erro ao buscar estádios: {e}")
        return []

# ── estilos ───────────────────────────────────────────────────────────────────

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

# ── card ──────────────────────────────────────────────────────────────────────

def _info_row(icon, label, valor):
    return html.P([
        html.I(className=f"fa-solid {icon}",
               style={"color": "#94a3b8", "marginRight": "8px", "fontSize": "10px"}),
        html.Span(f"{label}: ", style={"color": "#94a3b8", "fontSize": "11px"}),
        html.Span(valor, style={"color": "#1e293b", "fontWeight": "600", "fontSize": "11px"}),
    ], style={"marginBottom": "5px", "display": "flex", "alignItems": "center"})

def _card(e: dict) -> html.Div:
    cap_fmt = f"{e.get('capacidade', 0):,}".replace(",", ".")
    return html.Div(
        style={
            "backgroundColor": "#fff",
            "border": "1px solid #e2e8f0",
            "borderRadius": "20px",
            "padding": "20px",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-between",
            "boxShadow": "0 1px 3px rgba(0,0,0,.05)",
            "transition": "border-color .2s, box-shadow .2s",
            "minHeight": "180px",
        },
        className="estadio-card",
        children=[
            # Topo: nome + ícone
            html.Div([
                html.Span(
                    e.get("nome_estadio", "").upper(),
                    style={
                        "fontSize": "12px", "fontWeight": "800",
                        "color": "#1e293b", "letterSpacing": "0.04em",
                        "lineHeight": "1.3", "flex": "1", "marginRight": "12px",
                    }
                ),
                html.Div(
                    html.I(className="fa-solid fa-building",
                           style={"fontSize": "13px", "color": "#3b82f6"}),
                    style={
                        "width": "32px", "height": "32px",
                        "borderRadius": "8px", "backgroundColor": "#eff6ff",
                        "display": "flex", "alignItems": "center",
                        "justifyContent": "center", "flexShrink": "0",
                    }
                ),
            ], style={"display": "flex", "alignItems": "flex-start", "marginBottom": "14px"}),

            # Infos
            html.Div([
                _info_row("fa-map-pin",        "Sede",        e.get("cidade", "")),
                _info_row("fa-earth-americas", "País",        e.get("pais", "")),
                _info_row("fa-users",          "Capacidade",  cap_fmt),
            ], style={"marginBottom": "16px"}),

            # Rodapé: botões
            html.Div([
                html.Div(style={"borderTop": "1px solid #f1f5f9", "marginBottom": "12px"}),
                html.Div([
                    html.Button(
                        html.I(className="fa-solid fa-pen"),
                        id={"type": "btn-edit-estadio", "index": e["id_estadio"]},
                        title="Editar", n_clicks=0,
                        style={
                            "padding": "7px 10px", "cursor": "pointer",
                            "backgroundColor": "#f8fafc", "color": "#475569",
                            "border": "1px solid #e2e8f0", "borderRadius": "8px",
                            "fontSize": "11px", "marginRight": "6px",
                        },
                    ),
                    html.Button(
                        html.I(className="fa-solid fa-trash-can"),
                        id={"type": "btn-delete-estadio", "index": e["id_estadio"]},
                        title="Excluir", n_clicks=0,
                        style={
                            "padding": "7px 10px", "cursor": "pointer",
                            "backgroundColor": "#f8fafc", "color": "#475569",
                            "border": "1px solid #e2e8f0", "borderRadius": "8px",
                            "fontSize": "11px",
                        },
                    ),
                ], style={"display": "flex", "justifyContent": "flex-end"}),
            ]),
        ]
    )

def _grid(estadios: list) -> list:
    if not estadios:
        return [html.Div(
            "Nenhum estádio cadastrado.",
            style={"color": "#94a3b8", "fontSize": "12px",
                   "padding": "48px", "textAlign": "center",
                   "gridColumn": "1 / -1"},
        )]
    return [_card(e) for e in estadios]

# ── modal cadastro / edição ───────────────────────────────────────────────────

def _modal():
    return html.Div(
        id="modal-estadio-overlay",
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
                    "borderRadius": "20px", "width": "100%", "maxWidth": "460px",
                    "overflow": "hidden",
                    "boxShadow": "0 20px 40px -10px rgba(0,0,0,.12)",
                },
                children=[
                    # Header
                    html.Div(
                        html.Div([
                            html.I(className="fa-solid fa-map-location-dot",
                                   style={"color": "#2563eb", "marginRight": "8px", "fontSize": "12px"}),
                            html.Span(id="modal-estadio-titulo", children="Novo Estádio",
                                      style={"fontSize": "12px", "fontWeight": "800",
                                             "textTransform": "uppercase", "color": "#1e293b"}),
                        ], style={"display": "flex", "alignItems": "center"}),
                        style={"backgroundColor": "#f8fafc",
                               "borderBottom": "1px solid #e2e8f0", "padding": "18px 24px"},
                    ),
                    # Body
                    html.Div([
                        dcc.Store(id="edit-estadio-id", data=None),

                        # Nome
                        html.Div([
                            html.Label("Nome da Arena", style=_LABEL_STYLE),
                            dcc.Input(id="input-nome-estadio", type="text",
                                      placeholder="Ex: Estádio Lusail...",
                                      maxLength=80, style=_INPUT_STYLE),  # corrigido: varchar(80)
                        ], style={"marginBottom": "16px"}),

                        # Cidade + País
                        html.Div([
                            html.Div([
                                html.Label("Cidade", style=_LABEL_STYLE),
                                dcc.Input(id="input-cidade-estadio", type="text",
                                          placeholder="Ex: Nova York",
                                          maxLength=80, style=_INPUT_STYLE),  # corrigido: varchar(80)
                            ], style={"flex": "1", "marginRight": "12px"}),
                            html.Div([
                                html.Label("País", style=_LABEL_STYLE),
                                dcc.Input(id="input-pais-estadio", type="text",
                                          placeholder="Ex: EUA",
                                          maxLength=50, style=_INPUT_STYLE),
                            ], style={"flex": "1"}),
                        ], style={"display": "flex", "marginBottom": "16px"}),

                        # Capacidade
                        html.Div([
                            html.Label("Capacidade Total", style=_LABEL_STYLE),
                            dcc.Input(id="input-capacidade-estadio", type="number",
                                      min=1000, placeholder="80000", style=_INPUT_STYLE),
                        ], style={"marginBottom": "8px"}),

                        html.Div(id="modal-estadio-erro",
                                 style={"color": "#ef4444", "fontSize": "11px", "marginTop": "4px"}),
                    ], style={"padding": "24px"}),

                    # Footer
                    html.Div([
                        html.Button("Cancelar", id="btn-cancelar-estadio", n_clicks=0,
                                    style={
                                        "padding": "8px 16px", "borderRadius": "8px",
                                        "border": "none", "backgroundColor": "#f1f5f9",
                                        "color": "#475569", "fontSize": "11px",
                                        "fontWeight": "700", "textTransform": "uppercase",
                                        "cursor": "pointer", "marginRight": "8px",
                                    }),
                        html.Button("Salvar Estádio", id="btn-salvar-estadio", n_clicks=0,
                                    style={
                                        "padding": "8px 18px", "borderRadius": "8px",
                                        "border": "none", "backgroundColor": "#2563eb",
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

def _modal_delete():
    return html.Div(
        id="modal-delete-estadio-overlay",
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
                        dcc.Store(id="delete-estadio-id", data=None),
                        html.P("Tem certeza que deseja excluir este estádio? Esta ação não pode ser desfeita.",
                               style={"fontSize": "12px", "color": "#475569", "margin": 0}),
                    ], style={"padding": "24px"}),
                    html.Div([
                        html.Button("Cancelar", id="btn-cancelar-delete-estadio", n_clicks=0,
                                    style={
                                        "padding": "8px 16px", "borderRadius": "8px",
                                        "border": "none", "backgroundColor": "#f1f5f9",
                                        "color": "#475569", "fontSize": "11px",
                                        "fontWeight": "700", "textTransform": "uppercase",
                                        "cursor": "pointer", "marginRight": "8px",
                                    }),
                        html.Button("Excluir", id="btn-confirmar-delete-estadio", n_clicks=0,
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

# ── layout ────────────────────────────────────────────────────────────────────

def layout():
    estadios = _fetch_estadios()
    return html.Div([
        dcc.Store(id="store-estadios", data=estadios),

        # Cabeçalho
        html.Div([
            html.Div([
                html.H2("Estádios Sede", style={
                    "fontSize": "24px", "fontWeight": "800",
                    "color": "#0f172a", "margin": 0,
                }),
                html.P("Gerencie os estádios da competição", style={
                    "fontSize": "11px", "color": "#94a3b8",
                    "marginTop": "4px", "marginBottom": 0,
                }),
            ]),
            html.Button([
                html.I(className="fa-solid fa-plus",
                       style={"fontSize": "9px", "marginRight": "6px"}),
                "Novo Estádio",
            ],
                id="btn-novo-estadio", n_clicks=0,
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

        # Grid
        html.Div(
            id="grid-estadios",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(3, 1fr)",
                "gap": "20px",
            },
            children=_grid(estadios),
        ),

        _modal(),
        _modal_delete(),

        html.Div(id="toast-estadio-container", style={
            "position": "fixed", "top": "24px", "right": "24px", "zIndex": "9999",
        }),
    ], style={"padding": "32px"})


# ── callbacks ─────────────────────────────────────────────────────────────────

@callback(
    Output("modal-estadio-overlay", "style", allow_duplicate=True),
    Output("modal-estadio-titulo", "children", allow_duplicate=True),
    Output("input-nome-estadio", "value", allow_duplicate=True),
    Output("input-cidade-estadio", "value", allow_duplicate=True),
    Output("input-pais-estadio", "value", allow_duplicate=True),
    Output("input-capacidade-estadio", "value", allow_duplicate=True),
    Output("edit-estadio-id", "data", allow_duplicate=True),
    Input("btn-novo-estadio", "n_clicks"),
    prevent_initial_call=True,
)
def abrir_modal_novo(n):
    if not n:
        return [no_update] * 7
    return {"display": "block"}, "Novo Estádio", "", "", "", None, None


@callback(
    Output("modal-estadio-overlay", "style", allow_duplicate=True),
    Output("modal-estadio-titulo", "children", allow_duplicate=True),
    Output("input-nome-estadio", "value", allow_duplicate=True),
    Output("input-cidade-estadio", "value", allow_duplicate=True),
    Output("input-pais-estadio", "value", allow_duplicate=True),
    Output("input-capacidade-estadio", "value", allow_duplicate=True),
    Output("edit-estadio-id", "data", allow_duplicate=True),
    Input({"type": "btn-edit-estadio", "index": ALL}, "n_clicks"),
    State("store-estadios", "data"),
    prevent_initial_call=True,
)
def abrir_modal_edicao(n_clicks, estadios):
    if not any(n_clicks):
        return [no_update] * 7
    triggered = ctx.triggered_id
    if not triggered:
        return [no_update] * 7
    eid = triggered["index"]
    e = next((x for x in estadios if x["id_estadio"] == eid), None)
    if not e:
        return [no_update] * 7
    return (
        {"display": "block"}, "Editar Estádio",
        e["nome_estadio"], e["cidade"], e["pais"], e["capacidade"], eid,
    )


@callback(
    Output("modal-estadio-overlay", "style", allow_duplicate=True),
    Input("btn-cancelar-estadio", "n_clicks"),
    prevent_initial_call=True,
)
def fechar_modal(_):
    return {"display": "none"}


@callback(
    Output("modal-estadio-overlay", "style", allow_duplicate=True),
    Output("modal-estadio-erro", "children"),
    Output("store-estadios", "data", allow_duplicate=True),
    Output("grid-estadios", "children", allow_duplicate=True),
    Output("toast-estadio-container", "children", allow_duplicate=True),
    Input("btn-salvar-estadio", "n_clicks"),
    State("edit-estadio-id", "data"),
    State("input-nome-estadio", "value"),
    State("input-cidade-estadio", "value"),
    State("input-pais-estadio", "value"),
    State("input-capacidade-estadio", "value"),
    prevent_initial_call=True,
)
def salvar_estadio(n, eid, nome, cidade, pais, capacidade):
    if not n:
        return [no_update] * 5
    if not nome or not cidade or not pais or not capacidade:
        return no_update, "Preencha todos os campos obrigatórios.", no_update, no_update, no_update
    try:
        conn = get_connection()
        cur  = conn.cursor()
        if eid is None:
            cur.execute(
                "INSERT INTO estadios (nome_estadio, cidade, pais, capacidade) VALUES (%s,%s,%s,%s)",
                (nome.strip(), cidade.strip(), pais.strip(), int(capacidade)),
            )
            msg = f"Estádio '{nome}' cadastrado com sucesso!"
        else:
            cur.execute(
                "UPDATE estadios SET nome_estadio=%s, cidade=%s, pais=%s, capacidade=%s WHERE id_estadio=%s",
                (nome.strip(), cidade.strip(), pais.strip(), int(capacidade), eid),
            )
            msg = f"Estádio '{nome}' atualizado!"
        conn.commit()
        cur.close(); conn.close()
    except Exception as ex:
        return no_update, f"Erro ao salvar: {ex}", no_update, no_update, no_update
    novos = _fetch_estadios()
    return {"display": "none"}, "", novos, _grid(novos), _toast(msg, "fa-check-double", "#059669", "#f0fdf4", "#bbf7d0")


@callback(
    Output("modal-delete-estadio-overlay", "style", allow_duplicate=True),
    Output("delete-estadio-id", "data"),
    Input({"type": "btn-delete-estadio", "index": ALL}, "n_clicks"),
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
    Output("modal-delete-estadio-overlay", "style", allow_duplicate=True),
    Input("btn-cancelar-delete-estadio", "n_clicks"),
    prevent_initial_call=True,
)
def fechar_modal_delete(_):
    return {"display": "none"}


@callback(
    Output("modal-delete-estadio-overlay", "style", allow_duplicate=True),
    Output("store-estadios", "data", allow_duplicate=True),
    Output("grid-estadios", "children", allow_duplicate=True),
    Output("toast-estadio-container", "children", allow_duplicate=True),
    Input("btn-confirmar-delete-estadio", "n_clicks"),
    State("delete-estadio-id", "data"),
    prevent_initial_call=True,
)
def confirmar_delete(n, eid):
    if not n or not eid:
        return [no_update] * 4
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("DELETE FROM estadios WHERE id_estadio = %s", (eid,))
        conn.commit()
        cur.close(); conn.close()
    except Exception as ex:
        return {"display": "none"}, no_update, no_update, _toast(f"Erro: {ex}", "fa-triangle-exclamation", "#ef4444", "#fef2f2", "#fecaca")
    novos = _fetch_estadios()
    return {"display": "none"}, novos, _grid(novos), _toast("Estádio excluído.", "fa-trash-can", "#ef4444", "#fef2f2", "#fecaca")


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