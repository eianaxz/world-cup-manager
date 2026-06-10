"""
World Cup Manager 2026 — app.py
Entry point: multi-page Dash application with sidebar navigation.
"""

import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Font Awesome for professional icons
FA = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"
GOOGLE_FONTS = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"

app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[FA, GOOGLE_FONTS],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "World Cup Manager 2026"
server = app.server  # for gunicorn / production deployment

# ─── Sidebar Navigation Items ────────────────────────────────────────────────
NAV_ITEMS = [
    {"label": "Dashboard",          "href": "/",            "icon": "fa-solid fa-chart-pie",         "id": "nav-dashboard"},
    {"label": "Seleções",           "href": "/selecoes",    "icon": "fa-solid fa-flag",              "id": "nav-selecoes"},
    {"label": "Jogadores",          "href": "/jogadores",   "icon": "fa-solid fa-shirt",             "id": "nav-jogadores"},
    {"label": "Estádios",           "href": "/estadios",    "icon": "fa-solid fa-map-location-dot",  "id": "nav-estadios"},
    {"label": "Partidas",           "href": "/partidas",    "icon": "fa-solid fa-calendar-check",    "id": "nav-partidas"},
    {"label": "Ranking de Vitórias","href": "/ranking",     "icon": "fa-solid fa-ranking-star",      "id": "nav-ranking"},
]

def build_nav_links(current_pathname):
    """Returns sidebar nav buttons with active state based on current pathname."""
    links = []
    for item in NAV_ITEMS:
        is_active = (current_pathname == item["href"]) or \
                    (item["href"] == "/" and current_pathname in ["/", ""])
        links.append(
            dcc.Link(
                html.Div([
                    html.I(className=f"{item['icon']} sidebar-icon"),
                    html.Span(item["label"], className="sidebar-label"),
                ], className=f"sidebar-btn {'sidebar-btn-active' if is_active else ''}"),
                href=item["href"],
                id=item["id"],
                className="sidebar-link",
            )
        )
    return links

# ─── Sidebar Geometric Art (bottom decoration) ───────────────────────────────
sidebar_art = html.Div(
    [
        # Coloured circles overlay
        html.Div(className="geom-circle c-green"),
        html.Div(className="geom-circle c-blue"),
        html.Div(className="geom-circle c-red"),
        html.Div(className="geom-circle c-orange"),
        html.Div(className="geom-circle c-purple"),
        html.Div(className="geom-circle c-yellow"),
        # Label + online badge
        html.Div([
            html.P("Administrador", className="admin-label"),
            html.Div([
                html.Span(className="online-dot"),
                html.Span("Online", className="online-text"),
            ], className="online-row"),
        ], className="admin-info"),
    ],
    className="panini-art",
)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
sidebar = html.Aside(
    [
        # Logo
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fa-solid fa-futbol sidebar-ball-icon"),
                ], className="logo-inner"),
            ], className="logo-ring"),
            html.Div([
                html.Span("WORLD CUP", className="logo-title"),
                html.Span("MANAGER",   className="logo-sub"),
            ], className="logo-text"),
        ], className="logo-wrap"),

        # Navigation — dynamically re-rendered on pathname change
        html.Nav(id="sidebar-nav", className="sidebar-nav"),

        # Bottom art
        sidebar_art,
    ],
    className="sidebar",
)

# ─── Topbar ──────────────────────────────────────────────────────────────────
topbar = html.Header(
    [
        # Search
        html.Div([
            html.I(className="fa-solid fa-magnifying-glass search-icon"),
            dcc.Input(
                placeholder="Buscar seleções, estádios ou jogadores...",
                type="text",
                className="search-input",
                debounce=False,
            ),
        ], className="search-wrap"),

        # Right: notification + profile
        html.Div([
            html.Button(
                html.I(className="fa-regular fa-bell"),
                className="notif-btn",
            ),
            html.Div(className="topbar-divider"),
            html.Div([
                html.Div([
                    html.P("Master Admin",       className="profile-name"),
                    html.Span("root@fifa-replica", className="profile-tag"),
                ], className="profile-info"),
                html.Div("MA", className="avatar"),
            ], className="profile-wrap"),
        ], className="topbar-right"),
    ],
    className="topbar",
)

# ─── Root layout ─────────────────────────────────────────────────────────────
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        sidebar,
        html.Div(
            [topbar, html.Main(dash.page_container, className="page-main")],
            className="content-col",
        ),
    ],
    className="root-wrap",
)

# ─── Callback: highlight active nav link ─────────────────────────────────────
@app.callback(Output("sidebar-nav", "children"), Input("url", "pathname"))
def update_nav(pathname):
    return build_nav_links(pathname or "/")


if __name__ == "__main__":
    app.run(debug=True)