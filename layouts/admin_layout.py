# layouts/admin_layout.py
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from flask_login import current_user
from datetime import datetime

# Import modular components
from components.admin.sidebar import create_admin_sidebar
from components.admin.group_comparison import create_group_comparison
from components.admin.group_summary import create_group_summary
from components.admin.participant_detail import create_participant_detail
from layouts.footer import create_footer

def create_layout():
    """
    Create the admin dashboard layout
    
    Returns:
        A dash component with the admin dashboard
    """
    # Create sidebar
    sidebar = dbc.Col(
        dbc.Card(dbc.CardBody(create_admin_sidebar())),
        width=3,
    )
    
    # Main content
    main_content = dbc.Col(
        [
            html.H2("Sensor Data Dashboard", className="text-center mb-4"),
            
            # Display selected view information
            html.Div(id="selected-view-info", className="mb-4"),
            
            # Data visualization sections
            html.Div(id="admin-data-visualizations"),
            
            # Add a Store component to hold the selected participant ID
            dcc.Store(id="selected-participant-store")
        ],
        width=9
    )
    
    # Complete admin layout
    return dbc.Container(
        [
            # Navigation bar
            dbc.Navbar(
                dbc.Container([
                    html.A(
                        dbc.Row([
                            dbc.Col(html.Img(src="/assets/logo.svg", height="30px"), width="auto"),
                            dbc.Col(dbc.NavbarBrand("Health Dashboard Admin", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                        ),
                        href="/",
                        style={"textDecoration": "none"},
                    ),
                    dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                    dbc.Collapse(
                        dbc.Nav([
                            dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact")),
                            dbc.NavItem(dbc.NavLink("User Management", href="/users", active="exact")),
                            dbc.NavItem(dbc.NavLink("Settings", href="/settings", active="exact")),
                        ],
                        className="me-auto",
                        navbar=True),
                        id="navbar-collapse",
                        navbar=True,
                    ),
                ]),
                className="mb-4 bg-body-primary",
            ),
            
            # Main content with sidebar
            dbc.Row(
                [
                    sidebar,
                    main_content
                ],
                className="h-100"
            ),
            
            # Footer
            create_footer()
        ],
        fluid=True,
        className="vh-100 py-3"
    )