from datetime import datetime

from dash import html, dcc
import dash_bootstrap_components as dbc
from flask_login import current_user
import pandas as pd

# Import components
from components.participant.anomaly_charts import create_anomaly_charts
from components.participant.date_selector import create_date_selector
from components.participant.health_metrics import create_health_metrics
from components.participant.detailed_charts import create_detailed_charts
from layouts.footer import create_footer

def create_layout():
    """
    Create the layout for the participant dashboard
    
    Returns:
        A dash component with the participant dashboard
    """
    # Get the current participant's information
    user_id = current_user.id if current_user.is_authenticated else None
    display_name = current_user.display_name if current_user.is_authenticated else "Not logged in"
    
    # Get group information
    group = current_user.group if current_user.is_authenticated else None
    
    return html.Div([
        # Navigation bar - outside the container for full width
        dbc.Navbar(
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
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(
                    dbc.Nav([
                        dbc.NavItem(dbc.Button("Logout", id="logout-button", className="btn-logout")),
                    ],
                    className="ms-auto",
                    navbar=True),
                    id="navbar-collapse",
                    navbar=True,
                ),
            ]),
            color="#0a2342",
            className="mb-4",
        ),
        
        # Main content container
        dbc.Container([
            # Header section with user info
            dbc.Row([
                dbc.Col([
                    html.H1("Your FitonDuty Dashboard", className="display-5 mb-3"),
                    html.P(f"Welcome {display_name}!", className="lead mb-2"),
                    html.P(f"Group: {group}" if group else "", className="text-muted mb-3"),
                    html.Hr(className="my-3"),
                ])
            ], className="mb-4"),
            
            # Date selector component and health summary
            dbc.Row([
                dbc.Col([
                    html.H5("Dates of Interest", className="section-title"),
                    create_date_selector()
                ], xs=12, md=5, lg=4, className="mb-4"),
                dbc.Col([
                    html.H5("Your Health Summary", className="section-title"),
                    html.Div(id="participant-details-container", className="mb-3"),
                    html.Div(id="participant-ranking-container"),
                ], xs=12, md=7, lg=8, className="mb-4")
            ], className="mb-3"),

            # Anomaly charts component
            create_anomaly_charts(),
            
            # Health metrics section
            create_health_metrics(),
            
            # Detailed charts component
            create_detailed_charts(),
            
            # Footer
            create_footer()
        ], className="px-3 px-md-4")
    ])