"""
World Cup Manager 2026 — pages/perfil.py
Tela de perfil do usuário: exibe dados, permite edição e exclusão de conta.
Usa dcc.Store (user-store) como fonte de verdade da sessão simulada.
"""

import re
import dash
from dash import html, dcc, callback, Output, Input, State, no_update

dash.register_page(__name__, path="/perfil", name="Perfil")

NATIONALITIES = [
    "Brasil", "Argentina", "França", "Alemanha", "Espanha",
    "Portugal", "Inglaterra", "Uruguai", "Itália", "Holanda", "Outro",
]


# ── Layout principal ──────────────────────────────────────────────────────────

def layout():
    return html.Div([
        dcc.Location(id="perfil-redirect", refresh=True),

        html.Div([
            html.H2("Perfil",                          className="page-title"),
            html.P("Gerencie seus dados de acesso",    className="page-sub"),
        ], className="page-header"),

        # Card do perfil
        html.Div([
            html.Div(id="perfil-avatar",    className="perfil-avatar"),
            html.Div([
                html.Div(id="perfil-nome",  className="perfil-name"),
                html.Div(id="perfil-email", className="perfil-email"),
                html.Div(id="perfil-nac",   className="perfil-nac"),
                html.Div([
                    html.Span("Senha: ", className="perfil-field-label"),
                    html.Span("••••••••", className="perfil-senha"),
                ], className="perfil-senha-row"),
            ], className="perfil-info"),
            html.Div([
                html.Button([
                    html.I(className="fa-solid fa-pen btn-icon"), " Editar perfil",
                ], id="btn-open-edit", className="btn-primary"),
                html.Button([
                    html.I(className="fa-solid fa-trash btn-icon"), " Excluir conta",
                ], id="btn-open-delete", className="btn-danger"),
            ], className="perfil-actions"),
        ], className="perfil-card card-panel"),

        # ── Modal Editar ──────────────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fa-solid fa-user-pen modal-title-icon"),
                        html.Span("EDITAR PERFIL", className="modal-title-text"),
                    ], className="modal-title-row"),
                    html.Button(html.I(className="fa-solid fa-xmark"), id="btn-close-edit",
                                className="modal-close"),
                ], className="modal-header"),

                html.Div([
                    html.Div([
                        html.Label("Nome completo", className="field-label"),
                        dcc.Input(id="edit-nome", type="text",
                                  className="field-input", debounce=False),
                    ], className="field-group"),
                    html.Div([
                        html.Label("E-mail", className="field-label"),
                        dcc.Input(id="edit-email", type="email",
                                  className="field-input", debounce=False),
                    ], className="field-group"),
                    html.Div([
                        html.Label("Nacionalidade", className="field-label"),
                        dcc.Dropdown(
                            id="edit-nac",
                            options=[{"label": n, "value": n} for n in NATIONALITIES],
                            clearable=False,
                            className="field-dropdown",
                        ),
                    ], className="field-group"),
                    html.Div([
                        html.Label("Nova senha (opcional)", className="field-label"),
                        dcc.Input(id="edit-senha", type="password",
                                  placeholder="Deixe em branco para manter",
                                  className="field-input", debounce=False),
                    ], className="field-group"),
                    html.Div([
                        html.Label("Confirmar nova senha", className="field-label"),
                        dcc.Input(id="edit-confirmar", type="password",
                                  placeholder="Repita a nova senha",
                                  className="field-input", debounce=False),
                    ], className="field-group"),
                    html.Div(id="edit-error", className="modal-error"),
                ], className="modal-body modal-body-scroll"),

                html.Div([
                    html.Button("Cancelar", id="btn-cancel-edit",  className="btn-secondary"),
                    html.Button([
                        html.I(className="fa-solid fa-floppy-disk btn-icon"), " Salvar",
                    ], id="btn-save-edit", className="btn-primary"),
                ], className="modal-footer"),
            ], className="modal-box"),
        ], id="modal-edit-perfil", className="modal-overlay modal-hidden"),

        # ── Modal Excluir ─────────────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fa-solid fa-triangle-exclamation confirm-icon"),
                        html.Span("EXCLUIR CONTA", className="modal-title-text"),
                    ], className="modal-title-row"),
                    html.Button(html.I(className="fa-solid fa-xmark"), id="btn-close-delete",
                                className="modal-close"),
                ], className="modal-header"),

                html.P("Deseja realmente excluir sua conta? Esta ação não poderá ser desfeita.",
                       className="confirm-msg"),

                html.Div([
                    html.Button("Cancelar", id="btn-cancel-delete", className="btn-secondary"),
                    html.Button([
                        html.I(className="fa-solid fa-trash btn-icon"), " Excluir conta",
                    ], id="btn-confirm-delete", className="btn-danger"),
                ], className="modal-footer"),
            ], className="modal-box modal-box-sm"),
        ], id="modal-delete-perfil", className="modal-overlay modal-hidden"),

        # Toast
        html.Div(id="perfil-toast", className="toast toast-hidden"),

    ], className="page-wrap animate-fade-in")


# ── Callbacks ─────────────────────────────────────────────────────────────────

# Preencher card com dados do store
@callback(
    Output("perfil-avatar", "children"),
    Output("perfil-nome",   "children"),
    Output("perfil-email",  "children"),
    Output("perfil-nac",    "children"),
    Input("user-store",     "data"),
)
def _fill_perfil(data):
    if not data:
        return "MA", "Master Admin", "root@fifa-replica", "—"
    initials = data.get("initials", "?")
    nome  = data.get("nome",         "—")
    email = data.get("email",        "—")
    nac   = data.get("nacionalidade","—")
    return initials, nome, email, nac


# Abrir/fechar modal de edição
@callback(
    Output("modal-edit-perfil", "className"),
    Output("edit-nome",  "value"),
    Output("edit-email", "value"),
    Output("edit-nac",   "value"),
    Input("btn-open-edit",   "n_clicks"),
    Input("btn-close-edit",  "n_clicks"),
    Input("btn-cancel-edit", "n_clicks"),
    State("user-store",      "data"),
    prevent_initial_call=True,
)
def _toggle_edit(open_n, close_n, cancel_n, data):
    from dash import ctx
    triggered = ctx.triggered_id
    if triggered == "btn-open-edit":
        nome  = (data or {}).get("nome",          "")
        email = (data or {}).get("email",         "")
        nac   = (data or {}).get("nacionalidade", None)
        return "modal-overlay modal-visible", nome, email, nac
    return "modal-overlay modal-hidden", no_update, no_update, no_update


# Salvar edição
@callback(
    Output("edit-error",        "children"),
    Output("user-store",        "data",      allow_duplicate=True),
    Output("modal-edit-perfil", "className", allow_duplicate=True),
    Output("perfil-toast",      "children"),
    Output("perfil-toast",      "className"),
    Input("btn-save-edit",      "n_clicks"),
    State("edit-nome",     "value"),
    State("edit-email",    "value"),
    State("edit-nac",      "value"),
    State("edit-senha",    "value"),
    State("edit-confirmar","value"),
    State("user-store",    "data"),
    prevent_initial_call=True,
)
def _save_edit(n, nome, email, nac, senha, confirmar, data):
    if not n:
        return no_update, no_update, no_update, no_update, no_update
    if not nome or not nome.strip():
        return "Informe seu nome completo.", no_update, no_update, no_update, no_update
    if not email or not re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return "Informe um e-mail válido.", no_update, no_update, no_update, no_update
    if not nac:
        return "Selecione uma nacionalidade.", no_update, no_update, no_update, no_update
    if senha and len(senha) < 6:
        return "A nova senha deve ter pelo menos 6 caracteres.", no_update, no_update, no_update, no_update
    if senha and senha != confirmar:
        return "As senhas não coincidem.", no_update, no_update, no_update, no_update

    initials = "".join(p[0].upper() for p in nome.strip().split() if p)[:2]
    updated = {**(data or {}), "nome": nome.strip(), "email": email.strip(),
               "nacionalidade": nac, "initials": initials}
    if senha:
        updated["senha"] = senha

    toast_content = [html.I(className="fa-solid fa-check toast-icon toast-icon-success"),
                     " Perfil atualizado com sucesso."]
    return ("", updated, "modal-overlay modal-hidden",
            toast_content, "toast toast-success toast-visible")


# Fechar toast automaticamente via clientside (simples: reescrevemos a classe após 3 s)
# Abrir/fechar modal de exclusão
@callback(
    Output("modal-delete-perfil", "className"),
    Input("btn-open-delete",   "n_clicks"),
    Input("btn-close-delete",  "n_clicks"),
    Input("btn-cancel-delete", "n_clicks"),
    prevent_initial_call=True,
)
def _toggle_delete(open_n, close_n, cancel_n):
    from dash import ctx
    if ctx.triggered_id == "btn-open-delete":
        return "modal-overlay modal-visible"
    return "modal-overlay modal-hidden"


# Confirmar exclusão de conta
@callback(
    Output("user-store",           "data",      allow_duplicate=True),
    Output("perfil-redirect",      "pathname"),
    Input("btn-confirm-delete",    "n_clicks"),
    prevent_initial_call=True,
)
def _confirm_delete(n):
    if not n:
        return no_update, no_update
    return None, "/login"