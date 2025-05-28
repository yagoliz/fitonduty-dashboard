from dash import html
import dash_bootstrap_components as dbc

def create_navbar():
    """Create the participant navbar with links to different sections"""
    return dbc.Navbar(
            dbc.Container([
                html.A(
                    dbc.Row([
                        dbc.Col(html.Img(src="/assets/logo.svg", height="30px"), width="auto"),
                        dbc.Col(dbc.NavbarBrand("FitonDuty | Dashboard", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0,),
                dbc.Collapse(
                    dbc.Nav([
                        dbc.NavItem(dbc.Button("Logout", id="logout-button", className="btn-logout")),
                    ],
                    className="ms-auto",
                    navbar=True),
                    id="navbar-collapse",
                    navbar=True,
                    is_open=False,
                ),
            ]),
            color="#0a2342",
            className="mb-4",
            dark=True,
            expand="md",
        )