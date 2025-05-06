from dash import html, dcc
import dash_bootstrap_components as dbc

def create_detailed_charts():
    """
    Create the detailed charts component for participant dashboard
    
    Returns:
        A dash component with detailed charts
    """
    return html.Div([
        dbc.Row([
            # Heart rate zones chart
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Heart Rate Zones", className="card-title")),
                    dbc.CardBody([
                        dcc.Graph(id="heart-rate-zones-chart", style={"height": "300px"})
                    ])
                ])
            ], width=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Activity Trends", className="card-title")),
                    dbc.CardBody([
                        dcc.Graph(id="activity-chart", style={"height": "300px"})
                    ])
                ])
            ], width=6, className="mb-4"),
        ]),
    ])