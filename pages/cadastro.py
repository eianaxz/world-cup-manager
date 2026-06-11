"""
World Cup Manager 2026 — pages/cadastro.py  →  rota /cadastro
"""

import re
import dash
from dash import html, dcc, callback, Output, Input, State, no_update

dash.register_page(__name__, path="/cadastro", name="Cadastro")

NATIONALITIES = [
    "Brasil", "Argentina", "França", "Alemanha", "Espanha",
    "Portugal", "Inglaterra", "Uruguai", "Itália", "Holanda", "Outro",
]

def _left_panel():
    return html.Div([
        html.Div([
            html.Div([
                html.Div([html.I(className="fa-solid fa-futbol auth-ball-icon")], className="auth-logo-inner"),
            ], className="auth-logo-ring"),
            html.Div([
                html.Span("WORLD CUP", className="auth-logo-title"),
                html.Span("MANAGER",   className="auth-logo-sub"),
            ], className="auth-logo-text"),
        ], className="auth-logo-wrap"),
        html.P("Crie sua conta e comece a gerenciar a Copa do Mundo 2026.", className="auth-tagline"),
        html.Div(className="auth-circle ac-green"),
        html.Div(className="auth-circle ac-blue"),
        html.Div(className="auth-circle ac-red"),
        html.Div(className="auth-circle ac-orange"),
        html.Div(className="auth-circle ac-purple"),
        html.Div(className="auth-circle ac-yellow"),
    ], className="auth-left")


def layout():
    return html.Div([
        dcc.Location(id="cad-loc", refresh=True),
        _left_panel(),
        html.Div([
            html.Div([
                html.H2("Criar conta", className="auth-title"),
                html.P("Preencha os dados para se cadastrar", className="auth-sub"),

                html.Div([
                    html.Label("Nome completo", className="field-label"),
                    html.Div([
                        html.I(className="fa-solid fa-user auth-field-icon"),
                        dcc.Input(id="reg-nome", type="text", placeholder="Seu nome completo",
                                  className="field-input auth-field-padded", debounce=False),
                    ], className="auth-field-wrap"),
                ], className="field-group"),

                html.Div([
                    html.Label("E-mail", className="field-label"),
                    html.Div([
                        html.I(className="fa-solid fa-envelope auth-field-icon"),
                        dcc.Input(id="reg-email", type="email", placeholder="seu@email.com",
                                  className="field-input auth-field-padded", debounce=False),
                    ], className="auth-field-wrap"),
                ], className="field-group"),

                html.Div([
                    html.Label("Senha", className="field-label"),
                    html.Div([
                        html.I(className="fa-solid fa-lock auth-field-icon"),
                        dcc.Input(id="reg-senha", type="password", placeholder="Mínimo 6 caracteres",
                                  className="field-input auth-field-padded", debounce=False),
                    ], className="auth-field-wrap"),
                ], className="field-group"),

                html.Div([
                    html.Label("Confirmar senha", className="field-label"),
                    html.Div([
                        html.I(className="fa-solid fa-lock auth-field-icon"),
                        dcc.Input(id="reg-confirmar", type="password", placeholder="Repita a senha",
                                  className="field-input auth-field-padded", debounce=False),
                    ], className="auth-field-wrap"),
                ], className="field-group"),

                html.Div([
                    html.Label("Nacionalidade", className="field-label"),
                    dcc.Dropdown(
                        id="reg-nacionalidade",
                        options=[{"label": n, "value": n} for n in NATIONALITIES],
                        placeholder="Selecione sua nacionalidade",
                        clearable=False,
                        className="field-dropdown",
                    ),
                ], className="field-group"),

                html.Div(id="reg-error", className="modal-error"),

                html.Button([
                    html.I(className="fa-solid fa-user-plus btn-icon"), " Criar conta",
                ], id="btn-register", className="btn-primary auth-btn-full"),

                html.Div([
                    html.Span("Já tem conta? ", className="hint-text"),
                    dcc.Link("Fazer login", href="/login", className="link-add-selecao"),
                ], className="hint-row auth-hint-center"),

            ], className="auth-form-inner"),
        ], className="auth-right"),
    ], className="auth-wrap")


@callback(
    Output("reg-error",  "children"),
    Output("cad-loc",    "pathname"),
    Output("user-store",  "data"),
    Input("btn-register",      "n_clicks"),
    State("reg-nome",          "value"),
    State("reg-email",         "value"),
    State("reg-senha",         "value"),
    State("reg-confirmar",     "value"),
    State("reg-nacionalidade", "value"),
    prevent_initial_call=True,
)
def _do_register(n, nome, email, senha, confirmar, nacionalidade):
    if not n:
        return no_update, no_update, no_update
    if not nome or not nome.strip():
        return "Informe seu nome completo.", no_update, no_update
    if not email or not re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", email or ""):
        return "Informe um e-mail válido.", no_update, no_update
    if not senha or len(senha) < 6:
        return "A senha deve ter pelo menos 6 caracteres.", no_update, no_update
    if senha != confirmar:
        return "As senhas não coincidem.", no_update, no_update
    if not nacionalidade:
        return "Selecione uma nacionalidade.", no_update, no_update

    initials = "".join(p[0].upper() for p in nome.strip().split() if p)[:2]
    user_data = {
        "nome": nome.strip(),
        "email": email.strip(),
        "senha": senha,
        "nacionalidade": nacionalidade,
        "initials": initials,
    }
    return "", "/dashboard", user_data