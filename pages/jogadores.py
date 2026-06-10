"""
World Cup Manager 2026 — pages/jogadores.py
CRUD completo de jogadores conectado ao MySQL via config/database.py.

Schema real:
  jogadores : id_jogador, nome_jogador, posicao, numero_camisa, data_nascimento, id_selecao
  selecoes  : id_selecao, nome_selecao, continente, tecnico, titulos
"""

import time
import dash
from dash import html, dcc, callback, Output, Input, State, ctx, ALL, no_update, clientside_callback
import pandas as pd

dash.register_page(__name__, path="/jogadores", name="Jogadores")

_POSICOES_VALIDAS = {"Goleiro", "Defensor", "Meio-campista", "Atacante"}


# ═══════════════════════════════════════════════════════════
#  CAMADA DE DADOS
# ═══════════════════════════════════════════════════════════

def _fetch(query, params=None):
    try:
        from config.database import fetch_data
        result = fetch_data(query, params)
        return result if result is not None else pd.DataFrame()
    except Exception as e:
        print(f"[jogadores] DB fetch error: {e}")
        return pd.DataFrame()


def _execute(query, params=None):
    try:
        from config.database import execute_query
        execute_query(query, params)
        return True
    except Exception as e:
        print(f"[jogadores] DB execute error: {e}")
        return False


def _load_jogadores():
    return _fetch("""
        SELECT
            j.id_jogador,
            j.nome_jogador,
            s.nome_selecao,
            s.id_selecao,
            j.posicao,
            j.numero_camisa,
            j.data_nascimento
        FROM jogadores j
        INNER JOIN selecoes s ON j.id_selecao = s.id_selecao
        ORDER BY j.nome_jogador;
    """)


def _load_selecoes():
    df = _fetch("SELECT id_selecao, nome_selecao FROM selecoes ORDER BY nome_selecao;")
    if df.empty:
        return []
    return [
        {"label": row["nome_selecao"], "value": str(row["id_selecao"])}
        for _, row in df.iterrows()
    ]


def _insert_jogador(nome, posicao, camisa, nascimento, id_selecao):
    print(f"[jogadores] INSERT → nome={nome!r}, posicao={posicao!r}, "
          f"camisa={camisa!r}, nascimento={nascimento!r}, id_selecao={id_selecao!r}")
    return _execute("""
        INSERT INTO jogadores
            (nome_jogador, posicao, numero_camisa, data_nascimento, id_selecao)
        VALUES (%s, %s, %s, %s, %s);
    """, (nome, posicao, int(camisa), nascimento, int(id_selecao)))


def _update_jogador(id_jogador, nome, posicao, camisa, nascimento, id_selecao):
    print(f"[jogadores] UPDATE id={id_jogador} → nome={nome!r}, posicao={posicao!r}, "
          f"camisa={camisa!r}, nascimento={nascimento!r}, id_selecao={id_selecao!r}")
    return _execute("""
        UPDATE jogadores
        SET nome_jogador    = %s,
            posicao         = %s,
            numero_camisa   = %s,
            data_nascimento = %s,
            id_selecao      = %s
        WHERE id_jogador = %s;
    """, (nome, posicao, int(camisa), nascimento, int(id_selecao), int(id_jogador)))


def _delete_jogador(id_jogador):
    print(f"[jogadores] DELETE id={id_jogador!r}")
    return _execute(
        "DELETE FROM jogadores WHERE id_jogador = %s;",
        (int(id_jogador),)
    )


def _get_jogador(id_jogador):
    df = _fetch("""
        SELECT j.id_jogador, j.nome_jogador, j.posicao,
               j.numero_camisa, j.data_nascimento, j.id_selecao
        FROM jogadores j
        WHERE j.id_jogador = %s;
    """, (int(id_jogador),))
    return df.iloc[0] if not df.empty else None


# ═══════════════════════════════════════════════════════════
#  VALIDAÇÕES
# ═══════════════════════════════════════════════════════════

def _validar_nome(nome):
    """Retorna (True, None) ou (False, mensagem)."""
    nome = (nome or "").strip()
    if not nome:
        return False, "Informe o nome do jogador."
    if len(nome) < 3:
        return False, "O nome do jogador deve ter pelo menos 3 caracteres."
    return True, None


def _validar_selecao(id_selecao):
    if not id_selecao or str(id_selecao).strip() in ("", "None"):
        return False, "Selecione uma selecao para o jogador."
    return True, None


def _validar_posicao(posicao):
    if not posicao or str(posicao).strip() not in _POSICOES_VALIDAS:
        return False, "Selecione a posicao do jogador."
    return True, None


def _validar_camisa(camisa):
    try:
        v = int(camisa)
        if 1 <= v <= 99:
            return True, None
    except (TypeError, ValueError):
        pass
    return False, "Informe um numero de camisa valido entre 1 e 99."


def _validar_data(raw):
    """
    Aceita '' (campo vazio — data é opcional).
    Se preenchida, valida e converte DD/MM/AAAA → AAAA-MM-DD.
    Retorna (True, 'AAAA-MM-DD' | None) ou (False, mensagem).
    """
    raw = (raw or "").strip()
    if not raw:
        return True, None   # data de nascimento é opcional

    parts = raw.split("/")
    if len(parts) != 3:
        return False, "Informe uma data de nascimento valida no formato DD/MM/AAAA."

    dd, mm, aaaa = parts
    try:
        ts = pd.Timestamp(f"{aaaa}-{mm}-{dd}")
        if pd.isna(ts):
            raise ValueError
        return True, ts.strftime("%Y-%m-%d")
    except Exception:
        return False, "Informe uma data de nascimento valida no formato DD/MM/AAAA."


# ═══════════════════════════════════════════════════════════
#  HELPERS DE INTERFACE
# ═══════════════════════════════════════════════════════════

_BADGE_MAP = {
    "Atacante":      "badge-atacante",
    "Defensor":      "badge-defensor",
    "Meio-campista": "badge-meio",
    "Goleiro":       "badge-goleiro",
}


def _badge(posicao):
    cls = _BADGE_MAP.get(str(posicao).strip(), "badge-default")
    return html.Span(posicao, className=f"pos-badge {cls}")


def _fmt_date(val):
    if val is None or str(val).strip() in ("", "None", "NaT"):
        return ""
    try:
        return pd.Timestamp(val).strftime("%d/%m/%Y")
    except Exception:
        return str(val)


def _table_rows(df):
    if df is None or df.empty:
        return [html.Tr(
            html.Td("Nenhum jogador encontrado.", colSpan=6, className="empty-row")
        )]

    rows = []
    for _, r in df.iterrows():
        jid = str(r["id_jogador"])
        rows.append(html.Tr([
            html.Td(r["nome_jogador"],               className="td-bold"),
            html.Td(r["nome_selecao"],               className="td-medium"),
            html.Td(_badge(r["posicao"])),
            html.Td(str(r["numero_camisa"]),         className="td-mono td-center"),
            html.Td(_fmt_date(r["data_nascimento"]), className="td-mono td-muted"),
            html.Td(
                html.Div([
                    html.Button(
                        html.I(className="fa-solid fa-pen"),
                        id={"type": "btn-edit",   "index": jid},
                        className="action-btn action-edit",
                        title="Editar jogador",
                        n_clicks=0,
                    ),
                    html.Button(
                        html.I(className="fa-solid fa-trash-can"),
                        id={"type": "btn-delete", "index": jid},
                        className="action-btn action-delete",
                        title="Excluir jogador",
                        n_clicks=0,
                    ),
                ], className="actions-cell"),
                className="td-actions",
            ),
        ], className="table-row"))
    return rows


# ═══════════════════════════════════════════════════════════
#  LAYOUT
# ═══════════════════════════════════════════════════════════

def layout():
    selecoes_opts = _load_selecoes()

    return html.Div([

        # Toast de feedback
        html.Div(
            id="toast-msg",
            className="toast toast-hidden",
            children=[
                html.I(id="toast-icon", className="fa-solid fa-circle-check toast-icon"),
                html.Span("", id="toast-text"),
            ],
        ),

        # Cabeçalho
        html.Div([
            html.Div([
                html.H2("Jogadores",                         className="page-title"),
                html.P("Gerencie os jogadores das selecoes", className="page-sub"),
            ]),
            html.Button([
                html.I(className="fa-solid fa-user-plus btn-icon"),
                "NOVO JOGADOR",
            ], id="btn-open-add", className="btn-primary", n_clicks=0),
        ], className="page-header-row"),

        # Filtros
        html.Div([
            html.Div([
                html.Label("FILTRAR POR SELECAO", className="filter-label"),
                dcc.Dropdown(
                    id="filter-selecao",
                    options=[{"label": "Todas as Selecoes", "value": ""}] + selecoes_opts,
                    value="",
                    clearable=False,
                    className="filter-dropdown",
                ),
            ], className="filter-col"),
            html.Div([
                html.Label("FILTRAR POR POSICAO", className="filter-label"),
                dcc.Dropdown(
                    id="filter-posicao",
                    options=[
                        {"label": "Todas as Posicoes",  "value": ""},
                        {"label": "Goleiro",            "value": "Goleiro"},
                        {"label": "Defensor",           "value": "Defensor"},
                        {"label": "Meio-campista",      "value": "Meio-campista"},
                        {"label": "Atacante",           "value": "Atacante"},
                    ],
                    value="",
                    clearable=False,
                    className="filter-dropdown",
                ),
            ], className="filter-col"),
        ], className="filter-card"),

        # Tabela
        html.Div([
            html.Table([
                html.Thead(html.Tr([
                    html.Th("NOME",       className="th"),
                    html.Th("SELECAO",    className="th"),
                    html.Th("POSICAO",    className="th"),
                    html.Th("No CAMISA",  className="th th-center"),
                    html.Th("NASCIMENTO", className="th"),
                    html.Th("ACOES",      className="th th-center"),
                ], className="thead-row")),
                html.Tbody(id="jogadores-tbody"),
            ], className="data-table"),
        ], className="table-card"),

        # ── Modal: Adicionar / Editar ────────────────────────
        # position:fixed + flex garante centralização independente do scroll
        html.Div([
            html.Div([
                # Cabeçalho
                html.Div([
                    html.Div([
                        html.I(className="fa-solid fa-shirt modal-title-icon"),
                        html.Span("ADICIONAR ATLETA", id="modal-title-text",
                                  className="modal-title-text"),
                    ], className="modal-title-row"),
                    html.Button(
                        html.I(className="fa-solid fa-xmark"),
                        id="btn-close-modal",
                        className="modal-close",
                        n_clicks=0,
                    ),
                ], className="modal-header"),

                # Corpo com scroll interno caso o conteúdo seja grande
                html.Div([
                    dcc.Store(id="editing-id", data=None),

                    # Nome
                    html.Div([
                        html.Label("NOME COMPLETO", className="field-label"),
                        dcc.Input(
                            id="inp-nome", type="text",
                            placeholder="Ex: Vinicius Jr.",
                            className="field-input",
                            debounce=False,
                            maxLength=120,
                        ),
                    ], className="field-group"),

                    # Selecao + Posicao
                    html.Div([
                        html.Div([
                            html.Label("SELECAO", className="field-label"),
                            dcc.Dropdown(
                                id="inp-selecao",
                                options=selecoes_opts,
                                placeholder="Selecione...",
                                clearable=False,
                                className="field-dropdown",
                            ),
                            # Link adicionar selecao
                            html.Div([
                                html.Span("Nao encontrou a selecao? ",
                                          className="hint-text"),
                                html.A(
                                    "Adicionar selecao",
                                    href="/selecoes",
                                    target="_blank",
                                    className="link-add-selecao",
                                ),
                            ], className="hint-row"),
                        ], className="half-col"),
                        html.Div([
                            html.Label("POSICAO EM CAMPO", className="field-label"),
                            dcc.Dropdown(
                                id="inp-posicao",
                                options=[
                                    {"label": "Goleiro",       "value": "Goleiro"},
                                    {"label": "Defensor",      "value": "Defensor"},
                                    {"label": "Meio-campista", "value": "Meio-campista"},
                                    {"label": "Atacante",      "value": "Atacante"},
                                ],
                                value="Goleiro",
                                clearable=False,
                                className="field-dropdown",
                            ),
                        ], className="half-col"),
                    ], className="two-cols"),

                    # Camisa + Nascimento
                    html.Div([
                        html.Div([
                            html.Label("No DA CAMISA", className="field-label"),
                            dcc.Input(
                                id="inp-camisa", type="number",
                                min=1, max=99,
                                placeholder="7",
                                className="field-input",
                                debounce=False,
                            ),
                        ], className="half-col"),
                        html.Div([
                            html.Label("DATA DE NASCIMENTO", className="field-label"),
                            dcc.Input(
                                id="inp-nascimento", type="text",
                                placeholder="DD/MM/AAAA",
                                className="field-input",
                                debounce=False,
                                maxLength=10,
                            ),
                        ], className="half-col"),
                    ], className="two-cols"),

                    html.P("", id="modal-error", className="modal-error"),

                ], className="modal-body modal-body-scroll"),

                # Rodapé
                html.Div([
                    html.Button("CANCELAR",       id="btn-cancel",
                                className="btn-secondary", n_clicks=0),
                    html.Button("SALVAR JOGADOR", id="btn-save",
                                className="btn-primary",   n_clicks=0),
                ], className="modal-footer"),
            ], className="modal-box"),
        ], id="modal-form", className="modal-overlay modal-hidden"),

        # ── Modal: Confirmação de exclusão ───────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fa-solid fa-triangle-exclamation confirm-icon"),
                    html.Span("Confirmar Exclusao", className="modal-title-text"),
                ], className="modal-title-row modal-header"),

                html.P(
                    "Deseja realmente excluir este jogador? "
                    "Esta acao nao pode ser desfeita.",
                    className="confirm-msg",
                ),

                dcc.Store(id="delete-id", data=None),

                html.Div([
                    html.Button("CANCELAR", id="btn-cancel-delete",
                                className="btn-secondary", n_clicks=0),
                    html.Button("EXCLUIR",  id="btn-confirm-delete",
                                className="btn-danger",    n_clicks=0),
                ], className="modal-footer"),
            ], className="modal-box modal-box-sm"),
        ], id="modal-delete", className="modal-overlay modal-hidden"),

        dcc.Store(id="jog-store", data=None),
        dcc.Interval(id="toast-interval", interval=3000, n_intervals=0, disabled=True),

    ], className="page-wrap animate-fade-in")


# ═══════════════════════════════════════════════════════════
#  CLIENTSIDE: máscara DD/MM/AAAA no campo de nascimento
# ═══════════════════════════════════════════════════════════
# Aplica a máscara enquanto o usuário digita, sem round-trip ao servidor.
clientside_callback(
    """
    function(value) {
        if (!value) return value;

        // Remove tudo que não for dígito
        var digits = value.replace(/\\D/g, '');

        // Limita a 8 dígitos
        digits = digits.substring(0, 8);

        // Aplica a máscara DD/MM/AAAA
        var result = '';
        if (digits.length <= 2) {
            result = digits;
        } else if (digits.length <= 4) {
            result = digits.substring(0, 2) + '/' + digits.substring(2);
        } else {
            result = digits.substring(0, 2) + '/' +
                     digits.substring(2, 4) + '/' +
                     digits.substring(4);
        }
        return result;
    }
    """,
    Output("inp-nascimento", "value", allow_duplicate=True),
    Input("inp-nascimento",  "value"),
    prevent_initial_call=True,
)


# ═══════════════════════════════════════════════════════════
#  CALLBACKS
# ═══════════════════════════════════════════════════════════

# ── 1. Renderiza tabela ──────────────────────────────────────────────────────
@callback(
    Output("jogadores-tbody", "children"),
    Input("filter-selecao",  "value"),
    Input("filter-posicao",  "value"),
    Input("jog-store",       "data"),
)
def render_table(sel_filter, pos_filter, store):
    df = _load_jogadores()
    if df is not None and not df.empty:
        if sel_filter:
            df = df[df["id_selecao"].astype(str) == str(sel_filter)]
        if pos_filter:
            df = df[df["posicao"] == pos_filter]
    return _table_rows(df)


# ── 2. Controla toast ────────────────────────────────────────────────────────
@callback(
    Output("toast-msg",      "className"),
    Output("toast-text",     "children"),
    Output("toast-icon",     "className"),
    Output("toast-interval", "disabled"),
    Output("toast-interval", "n_intervals"),
    Input("jog-store",       "data"),
    Input("toast-interval",  "n_intervals"),
)
def handle_toast(store, n_intervals):
    triggered = ctx.triggered_id

    if triggered == "toast-interval" and n_intervals and n_intervals > 0:
        return "toast toast-hidden", "", "fa-solid fa-circle-check toast-icon", True, 0

    if store and isinstance(store, dict):
        msg   = store.get("msg", "Operacao realizada.")
        kind  = store.get("type", "success")
        icon  = (
            "fa-solid fa-circle-check toast-icon toast-icon-success"
            if kind == "success"
            else "fa-solid fa-circle-xmark toast-icon toast-icon-error"
        )
        return f"toast toast-visible toast-{kind}", msg, icon, False, 0

    return "toast toast-hidden", "", "fa-solid fa-circle-check toast-icon", True, 0


# ── 3. Abre modal NOVO ───────────────────────────────────────────────────────
@callback(
    Output("modal-form",       "className",  allow_duplicate=True),
    Output("modal-title-text", "children",   allow_duplicate=True),
    Output("editing-id",       "data",       allow_duplicate=True),
    Output("inp-nome",         "value",      allow_duplicate=True),
    Output("inp-selecao",      "value",      allow_duplicate=True),
    Output("inp-posicao",      "value",      allow_duplicate=True),
    Output("inp-camisa",       "value",      allow_duplicate=True),
    Output("inp-nascimento",   "value",      allow_duplicate=True),
    Output("modal-error",      "children",   allow_duplicate=True),
    Input("btn-open-add", "n_clicks"),
    prevent_initial_call=True,
)
def open_add_modal(n):
    if not n:
        return [no_update] * 9
    return (
        "modal-overlay modal-visible",
        "ADICIONAR ATLETA",
        None, "", None, "Goleiro", None, "", "",
    )


# ── 4. Abre modal EDITAR ─────────────────────────────────────────────────────
@callback(
    Output("modal-form",       "className",  allow_duplicate=True),
    Output("modal-title-text", "children",   allow_duplicate=True),
    Output("editing-id",       "data",       allow_duplicate=True),
    Output("inp-nome",         "value",      allow_duplicate=True),
    Output("inp-selecao",      "value",      allow_duplicate=True),
    Output("inp-posicao",      "value",      allow_duplicate=True),
    Output("inp-camisa",       "value",      allow_duplicate=True),
    Output("inp-nascimento",   "value",      allow_duplicate=True),
    Output("modal-error",      "children",   allow_duplicate=True),
    Input({"type": "btn-edit", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def open_edit_modal(n_list):
    if not any(n for n in n_list if n):
        return [no_update] * 9
    triggered = ctx.triggered_id
    if not triggered:
        return [no_update] * 9

    row = _get_jogador(triggered["index"])
    if row is None:
        return [no_update] * 9

    return (
        "modal-overlay modal-visible",
        "EDITAR ATLETA",
        str(triggered["index"]),
        str(row["nome_jogador"]),
        str(row["id_selecao"]),
        str(row["posicao"]),
        str(row["numero_camisa"]),
        _fmt_date(row["data_nascimento"]),
        "",
    )


# ── 5. Fecha modal de formulário ─────────────────────────────────────────────
@callback(
    Output("modal-form", "className", allow_duplicate=True),
    Input("btn-close-modal", "n_clicks"),
    Input("btn-cancel",      "n_clicks"),
    prevent_initial_call=True,
)
def close_form_modal(n_close, n_cancel):
    return "modal-overlay modal-hidden"


# ── 6. Salva jogador (INSERT ou UPDATE) com validações completas ─────────────
@callback(
    Output("jog-store",   "data",      allow_duplicate=True),
    Output("modal-form",  "className", allow_duplicate=True),
    Output("modal-error", "children",  allow_duplicate=True),
    Input("btn-save", "n_clicks"),
    State("editing-id",     "data"),
    State("inp-nome",       "value"),
    State("inp-selecao",    "value"),
    State("inp-posicao",    "value"),
    State("inp-camisa",     "value"),
    State("inp-nascimento", "value"),
    prevent_initial_call=True,
)
def save_jogador(n, editing_id, nome, id_selecao, posicao, camisa, nascimento):
    if not n:
        return no_update, no_update, no_update

    # ── Validações em sequência — para ao primeiro erro ──────
    ok_nome, err_nome = _validar_nome(nome)
    if not ok_nome:
        return no_update, no_update, err_nome

    ok_sel, err_sel = _validar_selecao(id_selecao)
    if not ok_sel:
        return no_update, no_update, err_sel

    ok_pos, err_pos = _validar_posicao(posicao)
    if not ok_pos:
        return no_update, no_update, err_pos

    ok_cam, err_cam = _validar_camisa(camisa)
    if not ok_cam:
        return no_update, no_update, err_cam

    ok_dt, nascimento_db = _validar_data(nascimento)
    if not ok_dt:
        return no_update, no_update, nascimento_db  # nascimento_db contém a msg de erro

    # Normaliza valores
    nome_clean = nome.strip()

    # ── Persistência ─────────────────────────────────────────
    if editing_id:
        ok  = _update_jogador(editing_id, nome_clean, posicao,
                              int(camisa), nascimento_db, id_selecao)
        msg = "Jogador atualizado com sucesso." if ok else \
              "Nao foi possivel salvar o jogador. Verifique os dados e tente novamente."
    else:
        ok  = _insert_jogador(nome_clean, posicao,
                              int(camisa), nascimento_db, id_selecao)
        msg = "Jogador cadastrado com sucesso." if ok else \
              "Nao foi possivel salvar o jogador. Verifique os dados e tente novamente."

    kind = "success" if ok else "error"

    if not ok:
        return (
            {"ts": time.time(), "msg": msg, "type": kind},
            no_update,
            msg,
        )

    return (
        {"ts": time.time(), "msg": msg, "type": kind},
        "modal-overlay modal-hidden",
        "",
    )


# ── 7. Abre modal de confirmação de exclusão ─────────────────────────────────
@callback(
    Output("modal-delete", "className", allow_duplicate=True),
    Output("delete-id",    "data",      allow_duplicate=True),
    Input({"type": "btn-delete", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def open_delete_modal(n_list):
    if not any(n for n in n_list if n):
        return no_update, no_update
    triggered = ctx.triggered_id
    if not triggered:
        return no_update, no_update
    return "modal-overlay modal-visible", triggered["index"]


# ── 8. Cancela exclusão ──────────────────────────────────────────────────────
@callback(
    Output("modal-delete", "className", allow_duplicate=True),
    Input("btn-cancel-delete", "n_clicks"),
    prevent_initial_call=True,
)
def cancel_delete(_):
    return "modal-overlay modal-hidden"


# ── 9. Confirma e executa exclusão ───────────────────────────────────────────
@callback(
    Output("jog-store",    "data",      allow_duplicate=True),
    Output("modal-delete", "className", allow_duplicate=True),
    Input("btn-confirm-delete", "n_clicks"),
    State("delete-id", "data"),
    prevent_initial_call=True,
)
def confirm_delete(n, id_jogador):
    if not n or not id_jogador:
        return no_update, no_update
    ok   = _delete_jogador(id_jogador)
    msg  = "Jogador excluido com sucesso." if ok else "Erro ao remover jogador."
    kind = "success" if ok else "error"
    return {"ts": time.time(), "msg": msg, "type": kind}, "modal-overlay modal-hidden"