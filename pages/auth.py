"""
World Cup Manager 2026 — pages/auth.py  →  rota /login
"""

import re
import dash
from dash import html, dcc, callback, Output, Input, State, no_update

dash.register_page(__name__, path="/login", name="Login")

NATIONALITIES = [
    "Brasil", "Argentina", "França", "Alemanha", "Espanha",
    "Portugal", "Inglaterra", "Uruguai", "Itália", "Holanda", "Outro",
]

# ── Painel esquerdo (compartilhado visualmente) ───────────────────────────────

def _left_panel(tagline="Gerencie seleções, jogadores, estádios e partidas em um painel moderno e integrado."):
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
        html.P(tagline, className="auth-tagline"),
        html.Div(className="auth-circle ac-green"),
        html.Div(className="auth-circle ac-blue"),
        html.Div(className="auth-circle ac-red"),
        html.Div(className="auth-circle ac-orange"),
        html.Div(className="auth-circle ac-purple"),
        html.Div(className="auth-circle ac-yellow"),
    ], className="auth-left")


# ── Layout ────────────────────────────────────────────────────────────────────

def layout():
    return html.Div([
        dcc.Location(id="login-loc", refresh=True),
        _left_panel(),
        html.Div([
            html.Div([
                html.H2("Bem-vindo de volta", className="auth-title"),
                html.P("Acesse seu painel administrativo", className="auth-sub"),

                html.Div([
                    html.Label("E-mail", className="field-label"),
                    html.Div([
                        html.I(className="fa-solid fa-envelope auth-field-icon"),
                        dcc.Input(id="login-email", type="email",
                                  placeholder="seu@email.com",
                                  className="field-input auth-field-padded", debounce=False),
                    ], className="auth-field-wrap"),
                ], className="field-group"),

                html.Div([
                    html.Label("Senha", className="field-label"),
                    html.Div([
                        html.I(className="fa-solid fa-lock auth-field-icon"),
                        dcc.Input(id="login-senha", type="password",
                                  placeholder="••••••••",
                                  className="field-input auth-field-padded", debounce=False),
                    ], className="auth-field-wrap"),
                ], className="field-group"),

                html.Div(id="login-error", className="modal-error"),

                html.Button([
                    html.I(className="fa-solid fa-arrow-right-to-bracket btn-icon"), " Entrar",
                ], id="btn-login", className="btn-primary auth-btn-full"),

                html.Div([
                    html.Span("Ainda não tem conta? ", className="hint-text"),
                    dcc.Link("Criar cadastro", href="/cadastro", className="link-add-selecao"),
                ], className="hint-row auth-hint-center"),

            ], className="auth-form-inner"),
        ], className="auth-right"),
    ], className="auth-wrap")


# ── Callbacks ─────────────────────────────────────────────────────────────────

@callback(
    Output("login-error", "children"),
    Output("login-loc",   "pathname"),
    Input("btn-login",    "n_clicks"),
    State("login-email",  "value"),
    State("login-senha",  "value"),
    prevent_initial_call=True,
)
def _do_login(n, email, senha):
    if not n:
        return no_update, no_update
    if not email or not re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", email or ""):
        return "Informe um e-mail válido.", no_update
    if not senha:
        return "Informe sua senha.", no_update
    return "", "/dashboard"