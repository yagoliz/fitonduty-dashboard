from dash import html, dcc
import dash_bootstrap_components as dbc

def create_health_metrics():
    """
    Create the health metrics component for participant dashboard
    
    Returns:
        A dash component with health metrics
    """
    return html.Div([
        dbc.Row([
            # Heart rate card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Heart Rate", className="card-title")),
                    dbc.CardBody([
                        html.Div(id="heart-rate-summary"),
                        dcc.Graph(id="heart-rate-chart", style={"height": "200px"})
                    ])
                ])
            ], width=12, lg=4, className="mb-4"),
            
            # Sleep card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Sleep", className="card-title")),
                    dbc.CardBody([
                        html.Div(id="sleep-summary"),
                        dcc.Graph(id="sleep-chart", style={"height": "200px"})
                    ])
                ])
            ], width=12, lg=4, className="mb-4"),
            
            # HRV card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Heart Rate Variability", className="card-title")),
                    dbc.CardBody([
                        html.Div(id="hrv-summary"),
                        dcc.Graph(id="hrv-chart", style={"height": "200px"})
                    ])
                ])
            ], width=12, lg=4, className="mb-4"),
        ])
    ])