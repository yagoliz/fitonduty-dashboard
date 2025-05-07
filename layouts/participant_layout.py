from datetime import datetime

from dash import html, dcc
import dash_bootstrap_components as dbc
from flask_login import current_user
import pandas as pd

# Import components
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
    
    return dbc.Container([
        # Navigation bar
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
                        dbc.NavItem(dbc.Button("Logout", id="logout-button", color="danger", outline=True)),
                    ],
                    className="ms-auto",
                    navbar=True),
                    id="navbar-collapse",
                    navbar=True,
                ),
            ]),
        ),
        
        # Header section with user info
        dbc.Row([
            dbc.Col([
                html.H1("Your FitonDuty Dashboard", className="display-4"),
                html.P(f"Welcome {display_name}!", className="lead"),
                html.Hr(className="my-4"),
                html.P(f"Group: {group}" if group else "", className="lead"),
            ])
        ], className="mb-4"),
        
        # Date selector component
        dbc.Row([
            dbc.Col([
                html.H5("Dates of Interest", className="mb-2"),
                create_date_selector()
            ], width=4),
            dbc.Col([
                html.H5("Your Health Summary"),
                html.Div(id="participant-details-container", className="mb-2"),
            ], width=8)
        ], className="mb-4"),
        
        # Health metrics component
        create_health_metrics(),
        
        # Detailed charts component
        create_detailed_charts(),
        
        # Footer
        create_footer()
    ], fluid=True)