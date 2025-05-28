from datetime import datetime, timedelta

from dash import html, dcc, callback, callback_context, Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import current_user

# Import custom components
from layouts.footer import create_footer
from utils.database import get_user_latest_data_date

def create_layout():
    """
    Create the layout for the participant dashboard with 3 distinct sections:
    1. Ranking (whole dataset)
    2. Daily Snapshot (single day picker)
    3. Health Metrics (single day + n days prior)
    
    Returns:
        A dash component with the participant dashboard
    """
    # Get the current participant's information
    display_name = current_user.display_name if current_user.is_authenticated else "Not logged in"
    
    # Get group information
    group = current_user.group if current_user.is_authenticated else None
    
    # Set default dates based on user's actual data
    if current_user.is_authenticated:
        latest_date = get_user_latest_data_date(current_user.id)
        today = latest_date if latest_date else datetime.now().date()
    else:
        today = datetime.now().date()
    
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
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0,),
                dbc.Collapse(
                    dbc.Nav([
                        dbc.NavItem(dbc.Button("Logout", id="logout-button", className="btn-logout")),
                    ],
                    className="ms-auto",
                    navbar=True),
                    id="navbar-collapse",
                    navbar=True,
                    is_open=False,
                ),
            ]),
            color="#0a2342",
            className="mb-4",
            dark=True,
            expand="md",
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
            
            # SECTION 1: RANKING (Whole dataset)
            html.Div([
                html.H4("Your Data Consistency Ranking", className="section-title text-primary"),
                html.P("Your ranking is calculated across your entire data history", className="text-muted mb-3"),
                html.Div(id="participant-ranking-container"),
            ], className="mb-5"),
            
            # SECTION 2: DAILY SNAPSHOT (Single day)
            html.Div([
                html.H4("Daily Health Snapshot", className="section-title text-primary"),
                dbc.Row([
                    dbc.Col([
                        html.H6("Select Date", className="mb-2"),
                        dcc.DatePickerSingle(
                            id="snapshot-date-picker",
                            date=today,
                            display_format="YYYY-MM-DD",
                            className="date-input mb-3",
                        ),
                        html.P("View your health metrics for a specific day", className="text-muted small"),
                        # Add info about data availability
                        html.P(f"Showing data from your most recent available date: {today.strftime('%B %d, %Y')}" if current_user.is_authenticated else "", 
                               className="text-info small", 
                               id="data-availability-info"),
                    ], xs=12, md=4, className="mb-3"),
                    dbc.Col([
                        html.Div(id="daily-snapshot-container"),
                    ], xs=12, md=8),
                ]),
            ], className="mb-5"),
            
            # SECTION 3: HEALTH METRICS TRENDS (Single day + n days prior)
            html.Div([
                html.H4("Health Metrics Trends", className="section-title text-primary"),
                
                # Date controls row
                dbc.Row([
                    dbc.Col([
                        html.H6("Select End Date & Period", className="mb-2"),
                        dcc.DatePickerSingle(
                            id="trends-end-date-picker",
                            date=today,
                            display_format="YYYY-MM-DD",
                            className="date-input mb-3",
                        ),
                        html.Div([
                            dbc.Button("Last 7 Days", id="trends-btn-7-days", color="light", size="sm", className="date-button me-1"),
                            dbc.Button("Last 30 Days", id="trends-btn-30-days", color="light", size="sm", className="date-button me-1"),
                            dbc.Button("Last 90 Days", id="trends-btn-90-days", color="light", size="sm", className="date-button"),
                        ], className="date-button-group mb-3"),
                        html.P("View trends leading up to your selected date", className="text-muted small"),
                        
                        # Store for the calculated start date
                        dcc.Store(id="trends-date-range", data={
                            "end_date": today.isoformat(),
                            "start_date": (today - timedelta(days=6)).isoformat(),
                            "days_back": 7
                        })
                    ], xs=12, md=6, lg=4, className="mb-3"),
                    dbc.Col([
                        html.Div(id="trends-period-info", className="mb-3"),
                    ], xs=12, md=6, lg=8),
                ]),
                
                # Charts row (full width)
                dbc.Row([
                    dbc.Col([
                        html.Div(id="health-metrics-container"),
                    ], xs=12),
                ]),
            ], className="mb-5"),
            
            # SECTION 4: DETAILED ANALYSIS (Uses same date range as health metrics)
            # html.Div([
            #     html.H4("Detailed Analysis", className="section-title text-primary"),
            #     html.P("Advanced charts based on your selected trend period", className="text-muted mb-3"),
            #     html.Div(id="detailed-analysis-container"),
            # ], className="mb-5"),
            
            # Footer
            create_footer()
        ], className="px-3 px-md-4")
    ])


@callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n_clicks, is_open):
    """Toggle the navbar collapse on mobile"""
    if n_clicks:
        return not is_open
    return is_open


@callback(
    [Output("trends-date-range", "data"),
     Output("trends-period-info", "children")],
    [Input("trends-btn-7-days", "n_clicks"),
     Input("trends-btn-30-days", "n_clicks"),
     Input("trends-btn-90-days", "n_clicks"),
     Input("trends-end-date-picker", "date")],
    [State("trends-date-range", "data")],
    # prevent_initial_call=True
)
def update_trends_date_range(n_7, n_30, n_90, end_date, current_data):
    """Update the trends date range based on button clicks or date changes"""
    
    ctx = callback_context
    # if not ctx.triggered:
    #     return current_data, ""
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Convert end_date to date object if it's a string
    if isinstance(end_date, str):
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        end_date_obj = end_date
    
    # Determine days back based on trigger
    if trigger_id == "trends-btn-7-days":
        days_back = 7
    elif trigger_id == "trends-btn-30-days":
        days_back = 30
    elif trigger_id == "trends-btn-90-days":
        days_back = 90
    elif trigger_id == "trends-end-date-picker":
        # Date picker changed, keep current days_back
        days_back = current_data.get("days_back", 7)
    else:
        days_back = current_data.get("days_back", 7)
    
    # Calculate start date
    start_date_obj = end_date_obj - timedelta(days=days_back-1)
    
    # Create info message
    info_message = html.Div([
        html.Strong(f"Viewing: {days_back} days"), 
        html.Br(),
        html.Span(f"From {start_date_obj.strftime('%b %d')} to {end_date_obj.strftime('%b %d, %Y')}", className="text-muted small")
    ])
    
    return {
        "end_date": end_date_obj.isoformat(),
        "start_date": start_date_obj.isoformat(),
        "days_back": days_back
    }, info_message