from datetime import datetime, timedelta

from dash import html, dcc, callback, callback_context, Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import current_user

from components.supervisor.navbar import create_navbar
from components.footer import create_footer
from utils.database import get_supervisor_group_info
from utils.logging_config import get_logger

logger = get_logger(__name__)


def create_layout():
    """
    Create the layout for the supervisor dashboard
    
    Returns:
        A dash component with the supervisor dashboard
    """
    logger.info("Creating supervisor layout")
    
    # Get the current supervisor's information
    display_name = current_user.display_name if current_user.is_authenticated else "Not logged in"
    logger.debug(f"Current user: {display_name} (authenticated: {current_user.is_authenticated})")
    
    # Get supervisor's group information
    group_info = None
    if current_user.is_authenticated:
        logger.debug(f"Getting group info for supervisor user_id={current_user.id}")
        group_info = get_supervisor_group_info(current_user.id)
        if group_info:
            logger.info(f"Supervisor user_id={current_user.id} assigned to group: {group_info['group_name']} (id={group_info['id']})")
        else:
            logger.warning(f"No group assigned to supervisor user_id={current_user.id}")
    
    # Set default dates
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)
    logger.debug(f"Default date range: {seven_days_ago} to {today}")
    
    layout = html.Div([
        # Navigation bar - outside the container for full width
        create_navbar(),
        
        # Main content container
        dbc.Container([
            # Header section with supervisor info
            dbc.Row([
                dbc.Col([
                    html.H1("Supervisor Dashboard", className="display-5 mb-3"),
                    html.P(f"Welcome {display_name}!", className="lead mb-2"),
                    html.Hr(className="my-3"),
                ])
            ], className="mb-4"),
            
            # Group info and date controls on same row
            dbc.Row([
                # Group information
                dbc.Col([
                    html.Div(id="supervisor-group-header"),
                ], xs=12, md=6, className="mb-4"),
                
                # Time period controls
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Select Time Period", className="card-title mb-0")
                        ]),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("End Date:", className="date-range-label"),
                                    dcc.DatePickerSingle(
                                        id="supervisor-end-date-picker",
                                        date=today.isoformat(),
                                        display_format="YYYY-MM-DD",
                                        className="date-input mb-3",
                                    ),
                                ], xs=12),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        dbc.Button("7 Days", id="supervisor-btn-7-days", 
                                                 color="primary", size="sm", className="me-2"),
                                        dbc.Button("30 Days", id="supervisor-btn-30-days", 
                                                 color="outline-primary", size="sm", className="me-2"),
                                        dbc.Button("90 Days", id="supervisor-btn-90-days", 
                                                 color="outline-primary", size="sm"),
                                    ], className="date-button-group"),
                                ], xs=12),
                            ])
                        ])
                    ], className="shadow-sm date-picker-card", style={"overflow": "visible"}),
                ], xs=12, md=6, className="mb-4"),
            ]),

            # Section title
            dbc.Row([
                dbc.Col([
                    html.H5("Supervisor Overview", className="section-title text-primary mb-3"),
                ])
            ], className="mb-4"),
            
            # Main content area
            dbc.Row([
                dbc.Col([
                    html.Div(id="supervisor-content-container"),
                ], xs=12),
            ], className="mb-4"),
            
            # Store for date range
            dcc.Store(id="supervisor-date-range", data={
                "start_date": seven_days_ago.isoformat(),
                "end_date": today.isoformat()
            }),
            
            # Footer
            create_footer()
        ], className="px-3 px-md-4")
    ])
    
    logger.info("Successfully created supervisor layout")
    return layout