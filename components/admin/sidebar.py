# components/admin/sidebar.py
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

from components.admin.date_selector import create_admin_date_selector

def create_admin_sidebar():
    """
    Create the sidebar content for the admin dashboard
    
    Returns:
        List of dash components for the sidebar
    """
    # Create date picker with default to today
    today = datetime(2025, 4, 1).date()
    
    # Sidebar content
    sidebar_content = [
        html.H4("Admin Dashboard", className="text-center"),
        html.Hr(),
        html.Div(id="admin-user-info", className="text-center"),
        html.Hr(),
        
        # Date selection
        create_admin_date_selector(),
        
        html.Hr(),
        
        # Groups and participants selection
        html.H5("Select Data View"),
        dbc.Label("Group"),
        dcc.Dropdown(
            id="group-dropdown",
            options=[],  # Will be populated in callback
            clearable=False,
            className="mb-2"
        ),
        
        html.Div(id="participant-dropdown-container", className="mt-3"),
        
        # Show all participants option
        dbc.Checklist(
            options=[{"label": "Show all participants", "value": 1}],
            value=[],
            id="show-all-checkbox",
            switch=True,
            className="mt-3"
        ),
        
        html.Hr(),
        
        # Data management section
        html.H5("Data Management"),
        dbc.Button(
            "Generate Mock Data", 
            id="generate-mock-data-btn", 
            color="secondary", 
            size="sm",
            className="w-100 mb-2"
        ),
        
        dbc.Collapse(
            dbc.Card(
                dbc.CardBody([
                    dbc.Label("Date Range for Mock Data"),
                    dbc.Row([
                        dbc.Col([
                            dcc.DatePickerSingle(
                                id="mock-data-start-date",
                                date=today - timedelta(days=30),
                                display_format="YYYY-MM-DD",
                                className="mb-2 w-100"
                            ),
                        ], width=6),
                        dbc.Col([
                            dcc.DatePickerSingle(
                                id="mock-data-end-date",
                                date=today,
                                display_format="YYYY-MM-DD",
                                className="mb-2 w-100"
                            ),
                        ], width=6),
                    ]),
                    dbc.Checklist(
                        options=[{"label": "Overwrite existing data", "value": 1}],
                        value=[],
                        id="overwrite-data-checkbox",
                        switch=True,
                        className="mt-2 mb-2"
                    ),
                    dbc.Button(
                        "Generate", 
                        id="confirm-generate-data-btn", 
                        color="primary", 
                        size="sm",
                        className="w-100"
                    ),
                    html.Div(id="generate-data-status", className="mt-2 small")
                ])
            ),
            id="mock-data-collapse",
            is_open=False,
        ),
        
        html.Hr(),
        
        # Logout button
        dbc.Button(
            "Logout", 
            id="logout-button", 
            color="danger", 
            className="w-100 mt-3"
        )
    ]
    
    return sidebar_content