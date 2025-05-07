from dash import html, dcc
import dash_bootstrap_components as dbc

def create_detailed_charts():
    """
    Create the detailed charts component for participant dashboard
    
    Returns:
        A dash component with detailed charts
    """
    return html.Div([
        html.H5("Detailed Analysis", className="section-title"),
        dbc.Row([
            # Heart rate zones chart
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Heart Rate Zones", className="card-title mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id="heart-rate-zones-chart", className="chart-container")
                    ])
                ])
            ], xs=12, md=6, className="mb-4"),
            
            # Activity trends chart
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Activity Trends", className="card-title mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id="activity-chart", className="chart-container")
                    ])
                ])
            ], xs=12, md=6, className="mb-4"),
        ], className="detailed-analysis-row")
    ], className="detailed-analysis")