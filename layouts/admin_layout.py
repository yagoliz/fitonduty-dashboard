# layouts/admin_layout.py - Updated version
from dash import html, dcc
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
    # Complete admin layout
    return html.Div([
        # Navigation bar - outside the container for full width
        dbc.Navbar(
            dbc.Container([
                html.A(
                    dbc.Row([
                        dbc.Col(html.Img(src="/assets/logo.svg", height="30px"), width="auto"),
                        dbc.Col(dbc.NavbarBrand("FitonDuty Dashboard Admin", className="ms-2")),
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
                        dbc.NavItem(dbc.Button("Logout", id="logout-button", className="btn-logout ms-3")),
                    ],
                    className="ms-auto",
                    navbar=True),
                    id="navbar-collapse",
                    navbar=True,
                ),
            ]),
            color="primary",
            dark=True,
            className="mb-4",
            style={"border-bottom": "none"}
        ),
        
        # Main container with sidebar toggle button outside of both sidebar and content
        dbc.Container([
            # Sidebar toggle button - fixed position
            html.Div([
                dbc.Button(
                    html.I(className="fas fa-bars"),
                    id="sidebar-toggle",
                    color="light",
                    size="sm",
                    className="sidebar-toggle-btn",
                ),
            ], id="sidebar-toggle-container"),
            
            dbc.Row([
                # Sidebar column - now with collapsible state
                dbc.Col(
                    dbc.Collapse(
                        html.Div(
                            create_admin_sidebar(),
                            className="sidebar-inner p-3",
                        ),
                        id="sidebar-collapse",
                        is_open=True,
                        className="h-100"
                    ),
                    width=12, md=3, lg=3,
                    id="sidebar-column",
                    className="sidebar-column bg-white shadow-sm px-0",
                ),
                
                # Main content area - with spacing from sidebar
                dbc.Col([
                    html.Div([
                        html.H2("FitonDuty Dashboard", className="text-center mb-4"),
                        
                        # Display selected view information
                        html.Div(id="selected-view-info", className="mb-4"),
                        
                        # Data visualization sections
                        html.Div(id="admin-data-visualizations"),
                        
                        # Add a Store component to hold the selected participant ID
                        dcc.Store(id="selected-participant-store")
                    ], className="main-content-inner px-4 py-3")
                ],
                width=12, md=9, lg=9,
                id="main-content-column",
                className="main-content-column pb-3 ps-md-4",
                ),
            ],
            className="g-0 row-with-sidebar"
            ),
            
            # Footer
            create_footer()
        ],
        fluid=True,
        className="px-0 pb-3"
        ),
        
        # Store to track sidebar state
        dcc.Store(id="sidebar-state", data={"is_open": True})
    ])