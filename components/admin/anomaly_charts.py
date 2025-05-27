from dash import html, dcc
import dash_bootstrap_components as dbc

def create_anomaly_charts():
    """
    Create the anomaly score visualization component
    
    Returns:
        A dash component for displaying anomaly charts
    """
    return html.Div([
        html.H5("Anomaly Detection", className="section-title"),
        dbc.Row([
            # Daily anomaly timeline
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Daily Anomaly Timeline", className="card-title mb-0")),
                    dbc.CardBody([
                        html.Div(id="anomaly-summary", className="metrics-summary"),
                        html.Div([
                            dcc.Graph(
                                id="anomaly-timeline-chart", 
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
            ], xs=12, md=12, className="mb-4"),
            
            # Weekly heatmap
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Weekly Anomaly Heatmap", className="card-title mb-0")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                id="anomaly-heatmap-chart", 
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
                        ], className="chart-wrapper", style={"height": "400px"})
                    ], style={"height": "450px"})
                ])
            ], xs=12, md=12, className="mb-4"),
        ])
    ], className="anomaly-analysis")