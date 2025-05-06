from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
from dash.exceptions import PreventUpdate

def create_date_selector():
    """
    Create the date selector component for participant dashboard
    
    Returns:
        A dash component with date selector
    """
    # Create last 7 days date range for default view
    today = datetime.now().date()
    week_ago = today - timedelta(days=6)
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Select Date Range", className="card-title"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("From:"),
                            dcc.DatePickerSingle(
                                id="participant-start-date",
                                date=week_ago,
                                display_format="YYYY-MM-DD",
                                className="mb-2"
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("To:"),
                            dcc.DatePickerSingle(
                                id="participant-end-date",
                                date=today,
                                display_format="YYYY-MM-DD",
                                className="mb-2"
                            ),
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("Last 7 Days", id="btn-last-7-days", color="secondary", size="sm", className="me-1"),
                            dbc.Button("Last 30 Days", id="btn-last-30-days", color="secondary", size="sm", className="me-1"),
                            dbc.Button("This Month", id="btn-this-month", color="secondary", size="sm"),
                        ])
                    ], className="mt-2"),
                ])
            ])
        ], width=12)
    ], className="mb-4")

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
    today = datetime.now().date()
    
    if button_id == "btn-last-7-days":
        start_date = today - timedelta(days=6)
        end_date = today
    elif button_id == "btn-last-30-days":
        start_date = today - timedelta(days=29)
        end_date = today
    elif button_id == "btn-this-month":
        start_date = today.replace(day=1)
        end_date = today
    else:
        return current_start, current_end
    
    return start_date, end_date