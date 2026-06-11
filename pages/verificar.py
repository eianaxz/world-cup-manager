"""
World Cup Manager 2026 — pages/verificar.py  →  rota /verificar
Verificação em duas etapas simulada (código fixo: 123456).
"""

import dash
from dash import html, dcc, callback, Output, Input, State, no_update

dash.register_page(__name__, path="/verificar", name="Verificação")

FAKE_CODE = "123456"


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
        html.P("Segurança simulada para fins acadêmicos.", className="auth-tagline"),
        html.Div(className="auth-circle ac-green"),
        html.Div(className="auth-circle ac-blue"),
        html.Div(className="auth-circle ac-red"),
        html.Div(className="auth-circle ac-orange"),
        html.Div(className="auth-circle ac-purple"),
        html.Div(className="auth-circle ac-yellow"),
    ], className="auth-left")


def layout():
    return html.Div([
        dcc.Location(id="ver-loc", refresh=True),
        _left_panel(),
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fa-solid fa-shield-halved auth-verify-icon"),
                ], className="auth-verify-icon-wrap"),

                html.H2("Verificação de segurança", className="auth-title"),
                html.P([
                    "Verificação em duas etapas simulada para fins acadêmicos.",
                    html.Br(),
                    "Use o código: ", html.Strong("123456"),
                ], className="auth-sub"),

                html.Div([
                    html.Label("Código de verificação", className="field-label"),
                    html.Div([
                        html.I(className="fa-solid fa-key auth-field-icon"),
                        dcc.Input(id="verify-code", type="text",
                                  placeholder="000000", maxLength=6,
                                  className="field-input auth-field-padded auth-code-input",
                                  debounce=False),
                    ], className="auth-field-wrap"),
                ], className="field-group"),

                html.Div(id="verify-error", className="modal-error"),

                html.Button([
                    html.I(className="fa-solid fa-check btn-icon"), " Verificar e entrar",
                ], id="btn-verify", className="btn-primary auth-btn-full"),

                html.Div([
                    dcc.Link("Voltar ao cadastro", href="/cadastro", className="link-add-selecao"),
                ], className="hint-row auth-hint-center", style={"marginTop": "8px"}),

            ], className="auth-form-inner"),
        ], className="auth-right"),
    ], className="auth-wrap")


@callback(
    Output("verify-error", "children"),
    Output("ver-loc",      "pathname"),
    Input("btn-verify",    "n_clicks"),
    State("verify-code",   "value"),
    State("reg-store",     "data"),
    prevent_initial_call=True,
)
def _do_verify(n, code, reg_data):
    if not n:
        return no_update, no_update, no_update
    if not code or code.strip() != FAKE_CODE:
        return "Código incorreto. Use 123456.", no_update, no_update
    # Grava user-store e vai para dashboard
    return "", "/dashboard", (reg_data or {})