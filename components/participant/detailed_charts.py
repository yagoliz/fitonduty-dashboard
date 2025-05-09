from dash import html, dcc
import dash_bootstrap_components as dbc

def create_detailed_charts():
    """
    Create the detailed charts component for participant dashboard
    with improved responsive layout
    
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
                        html.Div([
                            dcc.Graph(
                                id="heart-rate-zones-chart", 
                                className="chart-container",
                                config={
                                    'displayModeBar': False,
                                    'responsive': True
                                },
                                style={
                                    'width': '100%',
                                    'height': '100%'
                                }
                            )
                        ], className="chart-wrapper")
                    ])
                ])
            ], xs=12, md=6, className="mb-4"),
            
            # Activity trends chart
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Activity Trends", className="card-title mb-0")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                id="activity-chart", 
                                className="chart-container",
                                config={
                                    'displayModeBar': False,
                                    'responsive': True
                                },
                                style={
                                    'width': '100%',
                                    'height': '100%'
                                }
                            )
                        ], className="chart-wrapper")
                    ])
                ])
            ], xs=12, md=6, className="mb-4"),
        ], className="detailed-analysis-row")
    ], className="detailed-analysis")