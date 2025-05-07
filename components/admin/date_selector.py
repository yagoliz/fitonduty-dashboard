# components/admin/date_selector.py - Updated version
from datetime import datetime, timedelta

from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


def create_admin_date_selector():
    """
    Create a date selector component for admin dashboard
    without card styling
    
    Returns:
        A dash component with date selection controls
    """
    # Create last 7 days date range for default view
    today = datetime(2025, 5, 1).date()
    week_ago = today - timedelta(days=6)
    
    return html.Div([
        html.H5("Select Date Range", className="mb-2"),
        
        # More compact From/To layout
        html.Div([
            dbc.Col([
                html.Label("From:", className="date-range-label"),
                dcc.DatePickerSingle(
                    id="admin-start-date",
                    date=week_ago,
                    display_format="YYYY-MM-DD",
                    className="date-input dash-bootstrap",
                ),
            ], className="date-range-row"),
            
            dbc.Col([
                html.Label("To:", className="date-range-label"),
                dcc.DatePickerSingle(
                    id="admin-end-date",
                    date=today,
                    display_format="YYYY-MM-DD",
                    className="date-input"
                ),
            ], className="date-range-row"),
        ]),
        
        # Quick select buttons
        html.Div([
            dbc.Button("Last 7", id="admin-btn-last-7-days", color="light", size="sm", className="date-button me-1"),
            dbc.Button("Last 30", id="admin-btn-last-30-days", color="light", size="sm", className="date-button me-1"),
            dbc.Button("This Month", id="admin-btn-this-month", color="light", size="sm", className="date-button"),
        ], className="date-button-group"),
        
        # Data store for date range (for callbacks to use)
        dcc.Store(id="admin-date-range", data={
            "start_date": week_ago.isoformat(),
            "end_date": today.isoformat(),
        })
    ], className="date-selector") 

@callback(
    [Output("admin-start-date", "date"),
     Output("admin-end-date", "date"),
     Output("admin-date-range", "data")],
    [Input("admin-btn-last-7-days", "n_clicks"),
     Input("admin-btn-last-30-days", "n_clicks"),
     Input("admin-btn-this-month", "n_clicks"),
     Input("admin-start-date", "date"),
     Input("admin-end-date", "date")],
    [State("admin-date-range", "data")],
    prevent_initial_call=True
)
def update_admin_date_range(n_last_7, n_last_30, n_this_month, start_date, end_date, current_data):
    """Update the date range based on button clicks or direct date changes"""
    ctx = callback_context
    
    if not ctx.triggered:
        return start_date, end_date, current_data
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    current_end_date = datetime.now().date() if end_date is None else end_date
    
    # If end_date is string, convert to date
    if isinstance(current_end_date, str):
        current_end_date = datetime.strptime(current_end_date, "%Y-%m-%d").date()
    
    # For direct date changes from the date pickers
    if trigger_id in ["admin-start-date", "admin-end-date"]:
        if trigger_id == "admin-start-date" and start_date > end_date:
            # If start date is after end date, adjust end date
            end_date = start_date
        elif trigger_id == "admin-end-date" and end_date < start_date:
            # If end date is before start date, adjust start date
            start_date = end_date
            
        return start_date, end_date, {
            "start_date": start_date if isinstance(start_date, str) else start_date.isoformat(),
            "end_date": end_date if isinstance(end_date, str) else end_date.isoformat()
        }
    
    # For button clicks
    today = current_end_date
    
    if trigger_id == "admin-btn-last-7-days":
        start_date = today - timedelta(days=6)
        end_date = today
    elif trigger_id == "admin-btn-last-30-days":
        start_date = today - timedelta(days=29)
        end_date = today
    elif trigger_id == "admin-btn-this-month":
        start_date = today.replace(day=1)
        # Calculate end of month
        if today.month == 12:
            next_month = today.replace(year=today.year+1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month+1, day=1)
        end_date = next_month - timedelta(days=1)
    else:
        # No change
        return start_date, end_date, current_data
    
    return start_date, end_date, {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }