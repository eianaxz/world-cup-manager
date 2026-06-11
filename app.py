import dash
from dash import Dash, html, dcc, Input, Output, State, no_update

FONT_AWESOME = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
GOOGLE_FONT = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[FONT_AWESOME, GOOGLE_FONT],
)
server = app.server

AUTH_ROUTES = {"/login", "/cadastro", "/verificar"}

MENU_ITEMS = [
    ("Dashboard", "fa-solid fa-chart-pie", "/dashboard"),
    ("Seleções", "fa-solid fa-flag", "/selecoes"),
    ("Jogadores", "fa-solid fa-shirt", "/jogadores"),
    ("Estádios", "fa-solid fa-map-location-dot", "/estadios"),
    ("Partidas", "fa-solid fa-calendar-check", "/partidas"),
    ("Ranking de Vitórias", "fa-solid fa-ranking-star", "/ranking"),
    ("Perfil", "fa-solid fa-circle-user", "/perfil"),
]


def _sidebar(pathname: str):
    pathname = pathname or "/dashboard"
    links = []
    for label, icon, href in MENU_ITEMS:
        active = pathname == href or (href == "/dashboard" and pathname == "/")
        links.append(
            dcc.Link(
                html.Div([
                    html.I(className=f"{icon} sidebar-icon"),
                    html.Span(label, className="sidebar-label"),
                ], className="sidebar-btn sidebar-btn-active" if active else "sidebar-btn"),
                href=href,
                className="sidebar-link",
            )
        )

    return html.Aside([
        html.Div([
            html.Div([
                html.Div([
                    html.Div([html.I(className="fa-solid fa-futbol sidebar-ball-icon")], className="logo-inner"),
                ], className="logo-ring"),
                html.Div([
                    html.Span("WORLD CUP", className="logo-title"),
                    html.Span("MANAGER", className="logo-sub"),
                ], className="logo-text"),
            ], className="logo-wrap"),
            html.Nav(links, className="sidebar-nav"),
        ]),
        html.Div([
            html.Div(className="geom-circle c-green"),
            html.Div(className="geom-circle c-blue"),
            html.Div(className="geom-circle c-red"),
            html.Div(className="geom-circle c-orange"),
            html.Div(className="geom-circle c-purple"),
            html.Div(className="geom-circle c-yellow"),
            html.Div([
                html.Div("ADMINISTRADOR", className="admin-label"),
                html.Div([
                    html.Span(className="online-dot"),
                    html.Span("Online", className="online-text"),
                ], className="online-row"),
            ], className="admin-info"),
        ], className="panini-art"),
    ], className="sidebar")


def _topbar():
    return html.Header([
        html.Div([
            html.I(className="fa-solid fa-magnifying-glass search-icon"),
            dcc.Input(
                placeholder="Buscar seleções, estádios ou jogadores...",
                className="search-input",
                type="text",
            ),
        ], className="search-wrap"),
        html.Div([
            html.Button([
                html.I(className="fa-regular fa-bell"),
                html.Span("", id="notif-badge", className="notif-badge notif-badge-hidden"),
            ], id="btn-notif", className="notif-btn-clean"),
            html.Div(className="topbar-divider"),
            dcc.Link([
                html.Div([
                    html.Div(id="topbar-name", className="profile-name"),
                    html.Div(id="topbar-email", className="profile-tag"),
                ], className="profile-info"),
                html.Div(id="topbar-avatar", className="avatar"),
            ], href="/perfil", className="profile-link"),
        ], className="topbar-right"),
    ], className="topbar")


def _main_shell(pathname):
    return html.Div([
        _sidebar(pathname),
        html.Div([
            _topbar(),
            html.Main(dash.page_container, className="page-main"),
        ], className="content-col"),
    ], className="root-wrap")


def _auth_shell():
    return html.Div(
        html.Main(dash.page_container, className="auth-page-main"),
        className="auth-shell",
    )


app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="user-store", storage_type="local"),
    dcc.Store(id="alerts-store", storage_type="local", data=[]),
    dcc.Location(id="perfil-redirect", refresh=True),
    html.Div(id="app-shell"),
    

])

app.validation_layout = html.Div([
    app.layout,
    dash.page_container,
])


@app.callback(
    Output("app-shell", "children"),
    Output("url", "pathname"),
    Input("url", "pathname"),
    State("user-store", "data"),
)
def render_shell(pathname, user_data):
    pathname = pathname or "/login"

    if pathname == "/":
        return no_update, "/login"

    if pathname in AUTH_ROUTES:
        return _auth_shell(), no_update

    if not user_data:
        return no_update, "/login"

    return _main_shell(pathname), no_update


@app.callback(
    Output("topbar-name", "children"),
    Output("topbar-email", "children"),
    Output("topbar-avatar", "children"),
    Input("user-store", "data"),
)
def update_topbar(user_data):
    if not user_data:
        return "Master Admin", "root@fifa-replica", "MA"
    nome = user_data.get("nome") or "Master Admin"
    email = user_data.get("email") or "root@fifa-replica"
    initials = user_data.get("initials") or "MA"
    return nome, email, initials




if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=True)
