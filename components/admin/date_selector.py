from datetime import datetime, timedelta

from dash import html, dcc, callback, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

def create_admin_date_selector():
    """
    Create an enhanced date selector component for the admin dashboard
    that supports both single date selection and date range options
    
    Returns:
        A dash component with date selection controls
    """
    # Create default date values
    today = datetime(2025, 5, 1).date()
    week_ago = today - timedelta(days=6)
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H5("Date Selection", className="mb-2"),
                
                # Date range buttons
                dbc.ButtonGroup([
                    dbc.Button("Single Date", id="admin-single-date-btn", color="primary", 
                              className="me-1 date-range-btn", n_clicks=1),
                    dbc.Button("Last 7 Days", id="admin-last-7-btn", color="secondary", 
                              className="me-1 date-range-btn"),
                    dbc.Button("Last 30 Days", id="admin-last-30-btn", color="secondary", 
                              className="me-1 date-range-btn"),
                    dbc.Button("All Time", id="admin-all-time-btn", color="secondary", 
                              className="date-range-btn")
                ], className="mb-3 d-flex flex-wrap"),
                
                # Date selection content - will switch between single date and date range
                html.Div([
                    # Single date picker (default view)
                    html.Div([
                        dbc.Label("Select Date:"),
                        dcc.DatePickerSingle(
                            id="admin-date-picker",
                            date=today,
                            display_format="YYYY-MM-DD",
                            className="w-100"
                        )
                    ], id="admin-single-date-container"),
                    
                    # Date range pickers (hidden by default)
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("From:"),
                                dcc.DatePickerSingle(
                                    id="admin-start-date",
                                    date=week_ago,
                                    display_format="YYYY-MM-DD",
                                    className="w-100"
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("To:"),
                                dcc.DatePickerSingle(
                                    id="admin-end-date",
                                    date=today,
                                    display_format="YYYY-MM-DD",
                                    className="w-100"
                                )
                            ], width=6)
                        ])
                    ], id="admin-date-range-container", style={"display": "none"})
                ]),
                
                # Store for current date mode
                dcc.Store(id="admin-date-mode", data="single"),
                
                # Store for date range values to use in callbacks
                dcc.Store(id="admin-date-range", data={
                    "start_date": week_ago.isoformat(),
                    "end_date": today.isoformat(),
                    "mode": "single"
                })
            ], width=12)
        ], className="mb-3")
    ])

# Callback to handle date mode selection buttons
@callback(
    [Output("admin-single-date-btn", "color"),
     Output("admin-last-7-btn", "color"),
     Output("admin-last-30-btn", "color"),
     Output("admin-all-time-btn", "color"),
     Output("admin-single-date-container", "style"),
     Output("admin-date-range-container", "style"),
     Output("admin-date-mode", "data"),
     Output("admin-date-range", "data")],
    [Input("admin-single-date-btn", "n_clicks"),
     Input("admin-last-7-btn", "n_clicks"),
     Input("admin-last-30-btn", "n_clicks"),
     Input("admin-all-time-btn", "n_clicks")],
    [State("admin-date-picker", "date"),
     State("admin-start-date", "date"),
     State("admin-end-date", "date"),
     State("admin-date-range", "data")]
)
def update_date_selection_mode(n_single, n_7days, n_30days, n_all_time, 
                            single_date, start_date, end_date, current_range):
    """Update the date selection mode based on which button was clicked"""
    ctx = callback_context
    if not ctx.triggered:
        # Default to single date mode
        return "primary", "secondary", "secondary", "secondary", \
               {"display": "block"}, {"display": "none"}, "single", \
               {"mode": "single", "start_date": None, "end_date": single_date}
               
    # Get which button was clicked
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # We get the date from single_date or end_date
    today = datetime.strptime(single_date, "%Y-%m-%d").date() if single_date else end_date
    
    if button_id == "admin-single-date-btn":
        # Single date mode
        return "primary", "secondary", "secondary", "secondary", \
               {"display": "block"}, {"display": "none"}, "single", \
               {"mode": "single", "start_date": None, "end_date": single_date}
               
    elif button_id == "admin-last-7-btn":
        # Last 7 days mode
        week_ago = (today - timedelta(days=6)).isoformat()
        return "secondary", "primary", "secondary", "secondary", \
               {"display": "none"}, {"display": "block"}, "range", \
               {"mode": "7days", "start_date": week_ago, "end_date": today.isoformat()}
               
    elif button_id == "admin-last-30-btn":
        # Last 30 days mode
        month_ago = (today - timedelta(days=29)).isoformat()
        return "secondary", "secondary", "primary", "secondary", \
               {"display": "none"}, {"display": "block"}, "range", \
               {"mode": "30days", "start_date": month_ago, "end_date": today.isoformat()}
               
    elif button_id == "admin-all-time-btn":
        # All time mode - set start date to 1 year ago by default
        year_ago = (today - timedelta(days=365)).isoformat()
        return "secondary", "secondary", "secondary", "primary", \
               {"display": "none"}, {"display": "block"}, "range", \
               {"mode": "all", "start_date": year_ago, "end_date": today.isoformat()}
               
    # Fallback to single date mode
    return "primary", "secondary", "secondary", "secondary", \
           {"display": "block"}, {"display": "none"}, "single", \
           {"mode": "single", "start_date": None, "end_date": single_date}

# Callback to update date range pickers when mode changes
@callback(
    [Output("admin-start-date", "date"),
     Output("admin-end-date", "date")],
    Input("admin-date-range", "data"),
    prevent_initial_call=True
)
def update_date_range_pickers(date_range):
    """Update the date range picker values when the mode changes"""
    if date_range["mode"] == "single":
        return no_update, no_update
        
    return date_range["start_date"], date_range["end_date"]

# Callback to update date range data when pickers change
@callback(
    Output("admin-date-range", "data", allow_duplicate=True),
    [Input("admin-date-picker", "date"),
     Input("admin-start-date", "date"),
     Input("admin-end-date", "date")],
    State("admin-date-mode", "data"),
    prevent_initial_call=True
)
def update_date_range_from_pickers(single_date, start_date, end_date, mode):
    """Update the date range data when the pickers change"""
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
        
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if trigger_id == "admin-date-picker" and mode == "single":
        return {"mode": "single", "start_date": None, "end_date": single_date}
        
    elif (trigger_id == "admin-start-date" or trigger_id == "admin-end-date") and mode == "range":
        # If the end date is before the start date, change start date to end date
        if trigger_id == "admin-start-date" and end_date and start_date > end_date:
            end_date = start_date
        elif trigger_id == "admin-end-date" and start_date and end_date < start_date:
            start_date = end_date
        return {"mode": "custom", "start_date": start_date, "end_date": end_date}
        
    raise PreventUpdate