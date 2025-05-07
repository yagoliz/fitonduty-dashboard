from dash import html, dcc
import dash_bootstrap_components as dbc

def create_health_metrics():
    """
    Create the health metrics component for participant dashboard
    
    Returns:
        A dash component with health metrics
    """
    return html.Div([
        html.H5("Health Metrics", className="section-title"),
        dbc.Row([
            # Heart rate card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Heart Rate", className="card-title mb-0")),
                    dbc.CardBody([
                        html.Div(id="heart-rate-summary", className="metrics-summary"),
                        html.Div(dcc.Graph(id="heart-rate-chart", className="chart-container"))
                    ])
                ])
            ], xs=12, lg=4, className="mb-4"),
            
            # Sleep card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Sleep", className="card-title mb-0")),
                    dbc.CardBody([
                        html.Div(id="sleep-summary", className="metrics-summary"),
                        html.Div(dcc.Graph(id="sleep-chart", className="chart-container"))
                    ])
                ])
            ], xs=12, lg=4, className="mb-4"),
            
            # HRV card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Heart Rate Variability", className="card-title mb-0")),
                    dbc.CardBody([
                        html.Div(id="hrv-summary", className="metrics-summary"),
                        html.Div(dcc.Graph(id="hrv-chart", className="chart-container"))
                    ])
                ])
            ], xs=12, lg=4, className="mb-4"),
        ], className="health-metrics-row")
    ])