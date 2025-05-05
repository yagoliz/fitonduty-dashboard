import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

def create_day_selector(id_prefix="participant"):
    """
    Create a day selector component with date picker and navigation buttons
    
    Args:
        id_prefix: Prefix for component IDs to avoid conflicts when using multiple selectors
        
    Returns:
        A dash component with date picker and navigation buttons
    """
    # Get today and yesterday's date for default values
    default_date = datetime(2025, 3, 25).date()
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H5("Select Date", className="mb-2"),
                dbc.Row([
                    dbc.Col([
                        # Add d-flex and align-items-center to vertically center the button
                        html.Div([
                            dbc.Button("◀", id=f"{id_prefix}-prev-day", 
                                      color="primary", 
                                      className="w-100 h-100")
                        ], className="d-flex align-items-center h-100")
                    ], width=2, className="px-1"),
                    dbc.Col([
                        # Customize date picker styling
                        html.Div([
                            dcc.DatePickerSingle(
                                id=f"{id_prefix}-date-picker",
                                date=default_date,
                                display_format='YYYY-MM-DD',
                                clearable=False,
                                className="w-100"
                            )
                        ], style={'height': '38px'})  # Match button height
                    ], width=8, className="px-1"),
                    dbc.Col([
                        # Add d-flex and align-items-center to vertically center the button
                        html.Div([
                            dbc.Button("▶", id=f"{id_prefix}-next-day", 
                                      color="primary", 
                                      className="w-100 h-100")
                        ], className="d-flex align-items-center h-100")
                    ], width=2, className="px-1")
                ], className="align-items-center")  # Align items in row vertically
            ], width=12, md=6)
        ], className="mb-4")
    ])

@callback(
    Output("participant-date-picker", "date"),
    [Input("participant-prev-day", "n_clicks"),
     Input("participant-next-day", "n_clicks")],
    [State("participant-date-picker", "date")]
)
def update_date(prev_clicks, next_clicks, current_date):
    """
    Update the date when navigation buttons are clicked
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    # Convert string date to datetime object
    if isinstance(current_date, str):
        current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "participant-prev-day":
        return current_date - timedelta(days=1)
    elif button_id == "participant-next-day":
        next_date = current_date + timedelta(days=1)
        # Don't allow future dates
        if next_date <= datetime.now().date():
            return next_date
    
    return current_date