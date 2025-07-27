from datetime import datetime, timedelta

from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


def create_admin_date_selector():
    """
    Create a date selector component for admin dashboard
    with single current date and optional custom start date
    
    Returns:
        A dash component with date selection controls
    """
    # Set default current date
    today = datetime.now()
    
    return html.Div([
        html.H5("Select Analysis Period", className="mb-2"),
        
        # Current date selector with navigation arrows
        html.Div([
            html.Label("Current Date:", className="date-range-label"),
            html.Div([
                dbc.Button("◀", id="admin-date-prev", color="light", size="sm", className="me-2"),
                html.Div([
                    dcc.DatePickerSingle(
                        id="admin-current-date",
                        date=today,
                        display_format="YYYY-MM-DD",
                        className="date-input",
                        first_day_of_week=1,),
                ], style={"flex": "1", "maxWidth": "200px", "position": "relative"}),
                dbc.Button("▶", id="admin-date-next", color="light", size="sm", className="ms-2"),
            ], className="d-flex align-items-center", style={"width": "fit-content"}),
        ], className="date-range-row mb-3"),
        
        # Period selection buttons
        html.Div([
            dbc.Button("Last 7", id="admin-btn-last-7-days", color="light", size="sm", className="date-button me-1"),
            dbc.Button("Last 30", id="admin-btn-last-30-days", color="light", size="sm", className="date-button me-1"),
            dbc.Button("Custom", id="admin-btn-custom", color="light", size="sm", className="date-button"),
        ], className="date-button-group mb-3"),
        
        # Custom start date selector (initially hidden)
        html.Div([
            html.Label("Start Date:", className="date-range-label"),
            dcc.DatePickerSingle(
                id="admin-custom-start-date",
                date=today - timedelta(days=6),
                display_format="YYYY-MM-DD",
                className="date-input",
            ),
        ], id="custom-date-container", className="date-range-row", style={"display": "none"}),
        
        # Data store for date range (for callbacks to use)
        dcc.Store(id="admin-date-range", data={
            "start_date": (today - timedelta(days=6)).isoformat(),
            "end_date": today.isoformat(),
            "mode": "last_7"  # Track which mode is active
        })
    ], className="date-selector") 