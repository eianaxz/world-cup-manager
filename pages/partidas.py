# =============================================================
#  pages/partidas.py  —  World Cup Manager 2026
#  Retorna APENAS o conteúdo interno da página.
#  Sidebar, topbar e layout global são responsabilidade do app.py.
# =============================================================

import pandas as pd
import dash
from dash import html, dcc, Input, Output, State, callback, ctx, no_update

from config.database import fetch_data, execute_query

# ------------------------------------------------------------------
# Registro da página no Dash Pages
# ------------------------------------------------------------------
dash.register_page(__name__, path="/partidas", name="Partidas")


# ==================================================================
#  LAYOUT — apenas conteúdo interno da página
# ==================================================================

def layout():
    return html.Div(
        [
            # ── Cabeçalho da página ──────────────────────────────────
            html.Div(
                [
                    html.Div(
                        [
                            html.H1("Partidas", className="page-title"),
                            html.P(
                                "Gerencie as partidas da Copa do Mundo",
                                className="page-sub",
                            ),
                        ],
                        className="page-header",
                    ),
                    html.Button(
                        [
                            html.I(className="fa-solid fa-plus btn-icon"),
                            "NOVA PARTIDA",
                        ],
                        id="btn-nova-partida",
                        className="btn-primary",
                        n_clicks=0,
                    ),
                ],
                className="page-header-row",
            ),

            # ── Card de Filtros ──────────────────────────────────────
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Filtrar por Seleção", className="filter-label"),
                            dcc.Dropdown(
                                id="filter-selecao",
                                placeholder="Todas as Seleções",
                                clearable=True,
                                className="filter-dropdown",
                            ),
                        ],
                        className="filter-col",
                    ),
                    html.Div(
                        [
                            html.Label("Filtrar por Estádio", className="filter-label"),
                            dcc.Dropdown(
                                id="filter-estadio",
                                placeholder="Todos os Estádios",
                                clearable=True,
                                className="filter-dropdown",
                            ),
                        ],
                        className="filter-col",
                    ),
                    html.Div(
                        [
                            html.Label("Filtrar por Data", className="filter-label"),
                            dcc.DatePickerSingle(
                                id="filter-data",
                                placeholder="Selecione uma data",
                                display_format="DD/MM/YYYY",
                                clearable=True,
                                style={"width": "100%"},
                            ),
                        ],
                        className="filter-col",
                    ),
                ],
                className="filter-card",
                style={"gridTemplateColumns": "1fr 1fr 1fr"},
            ),

            # ── Tabela de Partidas ───────────────────────────────────
            html.Div(
                html.Table(
                    [
                        html.Thead(
                            html.Tr(
                                [
                                    html.Th("Data",      className="th"),
                                    html.Th("Estádio",   className="th"),
                                    html.Th("Seleção 1", className="th"),
                                    html.Th("Placar",    className="th th-center"),
                                    html.Th("Seleção 2", className="th"),
                                    html.Th("Vencedor",  className="th"),
                                    html.Th("Ações",     className="th th-center"),
                                ],
                                className="thead-row",
                            )
                        ),
                        html.Tbody(id="tabela-partidas"),
                    ],
                    className="data-table",
                ),
                className="table-card",
            ),

            # ── Toast de feedback ────────────────────────────────────
            html.Div(id="toast-partidas", className="toast toast-hidden"),

            # ── Stores ──────────────────────────────────────────────
            dcc.Store(id="store-id-partida",      data=None),
            dcc.Store(id="store-id-excluir",      data=None),
            dcc.Store(id="store-refresh-partidas", data=0),

            # ── Modal: Nova / Editar Partida ─────────────────────────
            html.Div(
                html.Div(
                    [
                        # Cabeçalho
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.I(className="fa-solid fa-calendar-check modal-title-icon"),
                                        html.Span(id="modal-partida-titulo", className="modal-title-text"),
                                    ],
                                    className="modal-title-row",
                                ),
                                html.Button(
                                    html.I(className="fa-solid fa-xmark"),
                                    id="btn-fechar-modal",
                                    className="modal-close",
                                    n_clicks=0,
                                ),
                            ],
                            className="modal-header",
                        ),
                        # Corpo
                        html.Div(
                            [
                                # Data da partida
                                html.Div(
                                    [
                                        html.Label("Data da Partida", className="field-label"),
                                        dcc.Input(
                                            id="input-data-partida",
                                            type="text",
                                            placeholder="DD/MM/AAAA",
                                            maxLength=10,
                                            className="field-input",
                                        ),
                                    ],
                                    className="field-group",
                                ),
                                # Estádio
                                html.Div(
                                    [
                                        html.Label("Estádio", className="field-label"),
                                        dcc.Dropdown(
                                            id="input-estadio",
                                            placeholder="Selecione o estádio",
                                            clearable=False,
                                            className="field-dropdown",
                                        ),
                                        html.Div(
                                            [
                                                html.Span("Não encontrou o estádio?", className="hint-text"),
                                                dcc.Link("Adicionar Estádio", href="/estadios", className="link-add-selecao"),
                                            ],
                                            className="hint-row",
                                        ),
                                    ],
                                    className="field-group",
                                ),
                                # Seleção 1
                                html.Div(
                                    [
                                        html.Label("Seleção 1", className="field-label"),
                                        dcc.Dropdown(
                                            id="input-selecao1",
                                            placeholder="Selecione a seleção 1",
                                            clearable=False,
                                            className="field-dropdown",
                                        ),
                                        html.Div(
                                            [
                                                html.Span("Não encontrou a seleção?", className="hint-text"),
                                                dcc.Link("Adicionar Seleção", href="/selecoes", className="link-add-selecao"),
                                            ],
                                            className="hint-row",
                                        ),
                                    ],
                                    className="field-group",
                                ),
                                # Gols Seleção 1
                                html.Div(
                                    [
                                        html.Label("Gols Seleção 1", className="field-label"),
                                        dcc.Input(
                                            id="input-gols1",
                                            type="number",
                                            min=0,
                                            value=0,
                                            className="field-input",
                                        ),
                                    ],
                                    className="field-group",
                                ),
                                # Seleção 2
                                html.Div(
                                    [
                                        html.Label("Seleção 2", className="field-label"),
                                        dcc.Dropdown(
                                            id="input-selecao2",
                                            placeholder="Selecione a seleção 2",
                                            clearable=False,
                                            className="field-dropdown",
                                        ),
                                        html.Div(
                                            [
                                                html.Span("Não encontrou a seleção?", className="hint-text"),
                                                dcc.Link("Adicionar Seleção", href="/selecoes", className="link-add-selecao"),
                                            ],
                                            className="hint-row",
                                        ),
                                    ],
                                    className="field-group",
                                ),
                                # Gols Seleção 2
                                html.Div(
                                    [
                                        html.Label("Gols Seleção 2", className="field-label"),
                                        dcc.Input(
                                            id="input-gols2",
                                            type="number",
                                            min=0,
                                            value=0,
                                            className="field-input",
                                        ),
                                    ],
                                    className="field-group",
                                ),
                                # Erro de validação
                                html.Div(id="modal-erro", className="modal-error"),
                            ],
                            className="modal-body modal-body-scroll",
                        ),
                        # Rodapé
                        html.Div(
                            [
                                html.Button(
                                    "Cancelar",
                                    id="btn-cancelar-modal",
                                    className="btn-secondary",
                                    n_clicks=0,
                                ),
                                html.Button(
                                    "Salvar",
                                    id="btn-salvar-partida",
                                    className="btn-primary",
                                    n_clicks=0,
                                ),
                            ],
                            className="modal-footer",
                        ),
                    ],
                    className="modal-box",
                ),
                id="modal-partida",
                className="modal-overlay modal-hidden",
            ),

            # ── Modal: Confirmar exclusão ────────────────────────────
            html.Div(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.I(className="fa-solid fa-triangle-exclamation confirm-icon"),
                                        html.Span("CONFIRMAR EXCLUSÃO", className="modal-title-text"),
                                    ],
                                    className="modal-title-row",
                                ),
                                html.Button(
                                    html.I(className="fa-solid fa-xmark"),
                                    id="btn-fechar-confirm",
                                    className="modal-close",
                                    n_clicks=0,
                                ),
                            ],
                            className="modal-header",
                        ),
                        html.P(
                            "Deseja realmente excluir esta partida?",
                            className="confirm-msg",
                        ),
                        html.Div(
                            [
                                html.Button(
                                    "Cancelar",
                                    id="btn-cancelar-confirm",
                                    className="btn-secondary",
                                    n_clicks=0,
                                ),
                                html.Button(
                                    "Excluir",
                                    id="btn-confirmar-excluir",
                                    className="btn-danger",
                                    n_clicks=0,
                                ),
                            ],
                            className="modal-footer",
                        ),
                    ],
                    className="modal-box modal-box-sm",
                ),
                id="modal-confirmar-exclusao",
                className="modal-overlay modal-hidden",
            ),
        ],
        className="page-wrap animate-fade-in",
    )


# ==================================================================
#  CALLBACKS
# ==================================================================

# ------------------------------------------------------------------
# 1. Popular dropdowns de filtros e do modal ao carregar / refrescar
# ------------------------------------------------------------------
@callback(
    Output("filter-selecao",  "options"),
    Output("filter-estadio",  "options"),
    Output("input-estadio",   "options"),
    Output("input-selecao1",  "options"),
    Output("input-selecao2",  "options"),
    Input("store-refresh-partidas", "data"),
)
def popular_dropdowns(_):
    df_sel = fetch_data(
        "SELECT id_selecao AS value, nome_selecao AS label "
        "FROM selecoes ORDER BY nome_selecao"
    )
    df_est = fetch_data(
        "SELECT id_estadio AS value, nome_estadio AS label "
        "FROM estadios ORDER BY nome_estadio"
    )
    opts_sel = df_sel.to_dict("records") if not df_sel.empty else []
    opts_est = df_est.to_dict("records") if not df_est.empty else []
    return opts_sel, opts_est, opts_est, opts_sel, opts_sel


# ------------------------------------------------------------------
# 2. Renderizar tabela com filtros aplicados
# ------------------------------------------------------------------
@callback(
    Output("tabela-partidas", "children"),
    Input("store-refresh-partidas", "data"),
    Input("filter-selecao",        "value"),
    Input("filter-estadio",        "value"),
    Input("filter-data",           "date"),
)
def renderizar_tabela(_, id_selecao, id_estadio, data_filtro):
    query = """
        SELECT
            p.id_partida,
            p.data_partida,
            e.nome_estadio,
            s1.nome_selecao  AS selecao_1,
            s2.nome_selecao  AS selecao_2,
            p.id_selecao_1,
            p.id_selecao_2,
            p.id_estadio,
            p.quantidade_gols_selecao_1,
            p.quantidade_gols_selecao_2,
            sv.nome_selecao  AS vencedor
        FROM partidas p
        INNER JOIN estadios  e  ON p.id_estadio   = e.id_estadio
        INNER JOIN selecoes  s1 ON p.id_selecao_1 = s1.id_selecao
        INNER JOIN selecoes  s2 ON p.id_selecao_2 = s2.id_selecao
        LEFT  JOIN selecoes  sv ON p.vencedor      = sv.id_selecao
        ORDER BY p.data_partida DESC
    """
    df = fetch_data(query)

    if df.empty:
        return [html.Tr(html.Td("Nenhuma partida cadastrada.", colSpan=7, className="empty-row"))]

    # Aplicar filtros
    if id_selecao:
        df = df[(df["id_selecao_1"] == id_selecao) | (df["id_selecao_2"] == id_selecao)]
    if id_estadio:
        df = df[df["id_estadio"] == id_estadio]
    if data_filtro:
        df["data_partida"] = df["data_partida"].astype(str)
        df = df[df["data_partida"] == data_filtro]

    if df.empty:
        return [html.Tr(html.Td("Nenhuma partida encontrada para os filtros selecionados.", colSpan=7, className="empty-row"))]

    linhas = []
    for _, row in df.iterrows():
        # Formatar data
        try:
            dt = row["data_partida"]
            if hasattr(dt, "strftime"):
                data_fmt = dt.strftime("%d/%m/%Y")
            else:
                from datetime import datetime
                data_fmt = datetime.strptime(str(dt), "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            data_fmt = str(row["data_partida"])

        placar = f"{row['quantidade_gols_selecao_1']} x {row['quantidade_gols_selecao_2']}"

        # ----------------------------------------------------------
        # Tratar vencedor: NULL, None, NaN, vazio → "Empate"
        # ----------------------------------------------------------
        vencedor_raw = row["vencedor"]
        try:
            is_empty = not vencedor_raw or pd.isna(vencedor_raw)
        except (TypeError, ValueError):
            is_empty = not vencedor_raw

        if is_empty:
            vencedor_texto = "Empate"
            badge_style = {
                "background": "#F1F5F9",
                "color":      "#475569",
                "padding":    "4px 10px",
                "borderRadius": "99px",
                "fontWeight": "700",
                "fontSize":   "10px",
                "border":     "1px solid #CBD5E1",
            }
        else:
            vencedor_texto = str(vencedor_raw)
            badge_style = {
                "background": "#ECFDF5",
                "color":      "#059669",
                "padding":    "4px 10px",
                "borderRadius": "99px",
                "fontWeight": "700",
                "fontSize":   "10px",
                "border":     "1px solid #A7F3D0",
            }

        linhas.append(
            html.Tr(
                [
                    html.Td(data_fmt,           className="td-medium td-muted"),
                    html.Td(row["nome_estadio"], className="td-medium"),
                    html.Td(row["selecao_1"],    className="td-bold"),
                    html.Td(
                        html.Span(
                            placar,
                            style={
                                "background":   "#2563EB",
                                "color":        "white",
                                "padding":      "4px 12px",
                                "borderRadius": "99px",
                                "fontWeight":   "800",
                                "fontSize":     "12px",
                            },
                        ),
                        className="td-mono",
                    ),
                    html.Td(row["selecao_2"],    className="td-bold"),
                    html.Td(html.Span(vencedor_texto, style=badge_style)),
                    html.Td(
                        html.Div(
                            [
                                html.Button(
                                    html.I(className="fa-solid fa-pen"),
                                    id={"type": "btn-editar",  "index": int(row["id_partida"])},
                                    className="action-btn action-edit",
                                    n_clicks=0,
                                ),
                                html.Button(
                                    html.I(className="fa-solid fa-trash-can"),
                                    id={"type": "btn-excluir", "index": int(row["id_partida"])},
                                    className="action-btn action-delete",
                                    n_clicks=0,
                                ),
                            ],
                            className="actions-cell",
                        ),
                        className="td-actions",
                    ),
                ],
                className="table-row",
            )
        )

    return linhas


# ------------------------------------------------------------------
# 3. Abrir modal de nova partida
# ------------------------------------------------------------------
@callback(
    Output("modal-partida",        "className",  allow_duplicate=True),
    Output("modal-partida-titulo", "children",   allow_duplicate=True),
    Output("store-id-partida",     "data",       allow_duplicate=True),
    Output("input-data-partida",   "value",      allow_duplicate=True),
    Output("input-estadio",        "value",      allow_duplicate=True),
    Output("input-selecao1",       "value",      allow_duplicate=True),
    Output("input-gols1",          "value",      allow_duplicate=True),
    Output("input-selecao2",       "value",      allow_duplicate=True),
    Output("input-gols2",          "value",      allow_duplicate=True),
    Output("modal-erro",           "children",   allow_duplicate=True),
    Input("btn-nova-partida", "n_clicks"),
    prevent_initial_call=True,
)
def abrir_modal_novo(n):
    if not n:
        return [no_update] * 10
    return (
        "modal-overlay modal-visible",
        "NOVA PARTIDA",
        None, "", None, None, 0, None, 0, "",
    )


# ------------------------------------------------------------------
# 4. Abrir modal preenchido para edição
# ------------------------------------------------------------------
@callback(
    Output("modal-partida",        "className",  allow_duplicate=True),
    Output("modal-partida-titulo", "children",   allow_duplicate=True),
    Output("store-id-partida",     "data",       allow_duplicate=True),
    Output("input-data-partida",   "value",      allow_duplicate=True),
    Output("input-estadio",        "value",      allow_duplicate=True),
    Output("input-selecao1",       "value",      allow_duplicate=True),
    Output("input-gols1",          "value",      allow_duplicate=True),
    Output("input-selecao2",       "value",      allow_duplicate=True),
    Output("input-gols2",          "value",      allow_duplicate=True),
    Output("modal-erro",           "children",   allow_duplicate=True),
    Input({"type": "btn-editar", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def abrir_modal_editar(n_clicks_list):
    triggered = ctx.triggered_id
    if not triggered or not any(n_clicks_list):
        return [no_update] * 10

    id_partida = triggered["index"]
    df = fetch_data(
        """
        SELECT id_partida, data_partida, id_estadio,
               id_selecao_1, id_selecao_2,
               quantidade_gols_selecao_1, quantidade_gols_selecao_2
        FROM partidas
        WHERE id_partida = %s
        """,
        params=(id_partida,),
    )
    if df.empty:
        return [no_update] * 10

    row = df.iloc[0]
    try:
        dt = row["data_partida"]
        if hasattr(dt, "strftime"):
            data_fmt = dt.strftime("%d/%m/%Y")
        else:
            from datetime import datetime
            data_fmt = datetime.strptime(str(dt), "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        data_fmt = str(row["data_partida"])

    return (
        "modal-overlay modal-visible",
        "EDITAR PARTIDA",
        int(id_partida),
        data_fmt,
        int(row["id_estadio"]),
        int(row["id_selecao_1"]),
        int(row["quantidade_gols_selecao_1"]),
        int(row["id_selecao_2"]),
        int(row["quantidade_gols_selecao_2"]),
        "",
    )


# ------------------------------------------------------------------
# 5. Fechar modal de criação/edição
# ------------------------------------------------------------------
@callback(
    Output("modal-partida", "className", allow_duplicate=True),
    Input("btn-fechar-modal",   "n_clicks"),
    Input("btn-cancelar-modal", "n_clicks"),
    prevent_initial_call=True,
)
def fechar_modal(_n1, _n2):
    return "modal-overlay modal-hidden"


# ------------------------------------------------------------------
# 6. Salvar partida (INSERT ou UPDATE)
# ------------------------------------------------------------------
@callback(
    Output("modal-partida",           "className",  allow_duplicate=True),
    Output("store-refresh-partidas",  "data",       allow_duplicate=True),
    Output("toast-partidas",          "children",   allow_duplicate=True),
    Output("toast-partidas",          "className",  allow_duplicate=True),
    Output("modal-erro",              "children",   allow_duplicate=True),
    Input("btn-salvar-partida", "n_clicks"),
    State("store-id-partida",   "data"),
    State("input-data-partida", "value"),
    State("input-estadio",      "value"),
    State("input-selecao1",     "value"),
    State("input-gols1",        "value"),
    State("input-selecao2",     "value"),
    State("input-gols2",        "value"),
    State("store-refresh-partidas", "data"),
    prevent_initial_call=True,
)
def salvar_partida(n, id_partida, data_str, id_estadio,
                   id_sel1, gols1, id_sel2, gols2, refresh):
    if not n:
        return [no_update] * 5

    # Validações
    if not data_str or not data_str.strip():
        return no_update, no_update, no_update, no_update, "A data é obrigatória."
    if not id_estadio:
        return no_update, no_update, no_update, no_update, "Selecione um estádio."
    if not id_sel1:
        return no_update, no_update, no_update, no_update, "Selecione a Seleção 1."
    if not id_sel2:
        return no_update, no_update, no_update, no_update, "Selecione a Seleção 2."
    if int(id_sel1) == int(id_sel2):
        return no_update, no_update, no_update, no_update, "As seleções devem ser diferentes."
    if gols1 is None or int(gols1) < 0:
        return no_update, no_update, no_update, no_update, "Gols da Seleção 1 não podem ser negativos."
    if gols2 is None or int(gols2) < 0:
        return no_update, no_update, no_update, no_update, "Gols da Seleção 2 não podem ser negativos."

    # Converter data DD/MM/AAAA → AAAA-MM-DD
    try:
        from datetime import datetime
        data_db = datetime.strptime(data_str.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return no_update, no_update, no_update, no_update, "Data inválida. Use o formato DD/MM/AAAA."

    try:
        if id_partida:
            # UPDATE — não envia vencedor; trigger do banco atualiza automaticamente
            execute_query(
                """
                UPDATE partidas
                SET data_partida              = %s,
                    id_estadio                = %s,
                    id_selecao_1              = %s,
                    id_selecao_2              = %s,
                    quantidade_gols_selecao_1 = %s,
                    quantidade_gols_selecao_2 = %s
                WHERE id_partida = %s
                """,
                params=(data_db, id_estadio, id_sel1, id_sel2, gols1, gols2, id_partida),
            )
            msg = "Partida atualizada com sucesso."
        else:
            # INSERT — não envia vencedor; trigger do banco preenche automaticamente
            execute_query(
                """
                INSERT INTO partidas
                    (data_partida, id_estadio, id_selecao_1, id_selecao_2,
                     quantidade_gols_selecao_1, quantidade_gols_selecao_2)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                params=(data_db, id_estadio, id_sel1, id_sel2, gols1, gols2),
            )
            msg = "Partida cadastrada com sucesso."

        toast_content = [html.I(className="fa-solid fa-check toast-icon toast-icon-success"), msg]
        return (
            "modal-overlay modal-hidden",
            (refresh or 0) + 1,
            toast_content,
            "toast toast-visible toast-success",
            "",
        )
    except Exception as e:
        toast_content = [
            html.I(className="fa-solid fa-triangle-exclamation toast-icon toast-icon-error"),
            "Erro ao salvar partida.",
        ]
        return (
            no_update, no_update,
            toast_content, "toast toast-visible toast-error",
            f"Erro: {str(e)}",
        )


# ------------------------------------------------------------------
# 7. Abrir modal de confirmação de exclusão
# ------------------------------------------------------------------
@callback(
    Output("modal-confirmar-exclusao", "className", allow_duplicate=True),
    Output("store-id-excluir",         "data",      allow_duplicate=True),
    Input({"type": "btn-excluir", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def abrir_confirm_exclusao(n_clicks_list):
    triggered = ctx.triggered_id
    if not triggered or not any(n_clicks_list):
        return no_update, no_update
    return "modal-overlay modal-visible", triggered["index"]


# ------------------------------------------------------------------
# 8. Fechar modal de confirmação
# ------------------------------------------------------------------
@callback(
    Output("modal-confirmar-exclusao", "className", allow_duplicate=True),
    Input("btn-fechar-confirm",   "n_clicks"),
    Input("btn-cancelar-confirm", "n_clicks"),
    prevent_initial_call=True,
)
def fechar_confirm(_n1, _n2):
    return "modal-overlay modal-hidden"


# ------------------------------------------------------------------
# 9. Confirmar exclusão
# ------------------------------------------------------------------
@callback(
    Output("modal-confirmar-exclusao", "className", allow_duplicate=True),
    Output("store-refresh-partidas",   "data",      allow_duplicate=True),
    Output("toast-partidas",           "children",  allow_duplicate=True),
    Output("toast-partidas",           "className", allow_duplicate=True),
    Input("btn-confirmar-excluir",  "n_clicks"),
    State("store-id-excluir",       "data"),
    State("store-refresh-partidas", "data"),
    prevent_initial_call=True,
)
def confirmar_exclusao(n, id_excluir, refresh):
    if not n or not id_excluir:
        return [no_update] * 4
    try:
        execute_query(
            "DELETE FROM partidas WHERE id_partida = %s",
            params=(id_excluir,),
        )
        toast_content = [
            html.I(className="fa-solid fa-check toast-icon toast-icon-success"),
            "Partida removida com sucesso.",
        ]
        return "modal-overlay modal-hidden", (refresh or 0) + 1, toast_content, "toast toast-visible toast-success"
    except Exception:
        toast_content = [
            html.I(className="fa-solid fa-triangle-exclamation toast-icon toast-icon-error"),
            "Erro ao remover partida.",
        ]
        return "modal-overlay modal-hidden", no_update, toast_content, "toast toast-visible toast-error"


# ------------------------------------------------------------------
# 10. Máscara automática de data (DD/MM/AAAA)
# ------------------------------------------------------------------
@callback(
    Output("input-data-partida", "value", allow_duplicate=True),
    Input("input-data-partida",  "value"),
    prevent_initial_call=True,
)
def mascara_data(value):
    if not value:
        return value
    digits = "".join(c for c in value if c.isdigit())[:8]
    result = ""
    for i, ch in enumerate(digits):
        if i in (2, 4):
            result += "/"
        result += ch
    return result