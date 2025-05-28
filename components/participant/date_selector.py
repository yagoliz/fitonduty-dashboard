from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

def create_date_selector():
    """
    Create a more compact date selector component for participant dashboard
    
    Returns:
        A dash component with date selector
    """
    # Create last 7 days date range for default view
    today = datetime(2025, 5, 1).date()
    week_ago = today - timedelta(days=6)
    
    return html.Div([
        html.H6("Select Date Range", className="mb-2"),
        
        # More compact From/To layout
        html.Div([
            dbc.Col([
                html.Label("From:", className="date-range-label"),
                dcc.DatePickerSingle(
                    id="participant-start-date",
                    date=week_ago,
                    display_format="YYYY-MM-DD",
                    className="date-input dash-bootstrap",
                ),
            ], className="date-range-row"),
            
            dbc.Col([
                html.Label("To:", className="date-range-label"),
                dcc.DatePickerSingle(
                    id="participant-end-date",
                    date=today,
                    display_format="YYYY-MM-DD",
                    className="date-input"
                ),
            ], className="date-range-row"),
        ]),
        
        # Quick select buttons
        html.Div([
            dbc.Button("Last 7", id="btn-last-7-days", color="light", size="sm", className="date-button me-1"),
            dbc.Button("Last 30", id="btn-last-30-days", color="light", size="sm", className="date-button me-1"),
            dbc.Button("This Month", id="btn-this-month", color="light", size="sm", className="date-button"),
        ], className="date-button-group")
    ], className="date-selector-container border-0")

@callback(
    [Output("participant-start-date", "date"),
     Output("participant-end-date", "date")],
    [Input("btn-last-7-days", "n_clicks"),
     Input("btn-last-30-days", "n_clicks"),
     Input("btn-this-month", "n_clicks")],
    [State("participant-start-date", "date"),
     State("participant-end-date", "date")],
    prevent_initial_call=True
)
def update_date_range(n_last_7, n_last_30, n_this_month, current_start, current_end):
    """Update the date range based on button clicks"""
    ctx = callback_context
    
    if not ctx.triggered:
        return current_start, current_end
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Get the end date. If not set, use today
    if current_end is None:
        current_end = datetime.now().date()

    # If end_date is string, convert to date
    if isinstance(current_end, str):
        current_end = datetime.strptime(current_end, "%Y-%m-%d").date()

    # Get the start date. If not set, use 7 days before today
    if current_start is None:
        current_start = current_end - timedelta(days=6)

    today = current_end
    
    if button_id == "btn-last-7-days":
        start_date = today - timedelta(days=6)
        end_date = today
    elif button_id == "btn-last-30-days":
        start_date = today - timedelta(days=29)
        end_date = today
    elif button_id == "btn-this-month":
        start_date = today.replace(day=1)
        end_date = today.replace(day=1) + timedelta(days=31)
    else:
        return current_start, current_end
    
    return start_date, end_date